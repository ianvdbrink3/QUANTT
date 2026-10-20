"""Calendar, point-in-time rollover, fill and fail-closed controls."""
import json
from pathlib import Path
import pandas as pd
import pytest
from scripts.reproduce_research import engine, holdout_data as data, holdout

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('day,n',[('2025-04-18',0),('2025-05-26',1140),
    ('2025-06-19',1140),('2025-07-03',1155),('2025-07-04',1140),
    ('2025-09-01',1140),('2025-07-14',1380),('2025-07-12',0)])
def test_expected_calendar_minutes(day,n):
    assert len(data.grid(day))==n


def test_dst_calendar_uses_zone_not_fixed_offset():
    assert data.grid('2025-03-07')[0].hour==23
    assert data.grid('2025-03-10')[0].hour==22


def test_holiday_close_not_reported_as_missing_minutes(monkeypatch):
    day='2025-05-26'
    g=pd.DataFrame({'open':100.,'high':101.,'low':99.,'close':100.,'volume':10,
                    'contract':'NQM25','trade_date':day},index=data.grid(day))
    monkeypatch.setattr(engine,'expected_grid',data.grid)
    bars,daily,_,gaps=engine.build_features(g)
    assert daily.missing_minutes.iloc[0]==0 and len(gaps)==0
    assert daily.expected_minutes.iloc[0]==1140
    assert not bool(daily.rth_complete.iloc[0])  # No synthetic full-RTH warmup.
    assert pd.isna(bars.return_1m.iloc[0])


def synthetic(contract,day,volume):
    ix=data.grid(day)
    return pd.DataFrame({'volume':volume,'contract':contract,'trade_date':day},index=ix)


def test_roll_uses_completed_prior_day_not_current_day():
    parts=[]
    for old,new,days in [('NQM25','NQU25',['2025-06-10','2025-06-11','2025-06-12']),
                         ('NQU25','NQZ25',['2025-09-09','2025-09-10','2025-09-11'])]:
        for i,day in enumerate(days):
            parts += [synthetic(old,day,100),synthetic(new,day,50 if i==0 else 150)]
    rolls=data.rollovers(pd.concat(parts))
    assert [r['decision_session'] for r in rolls]==['2025-06-11','2025-09-10']
    assert [r['effective_session'] for r in rolls]==['2025-06-12','2025-09-11']
    assert rolls[0]['effective_utc']=='2025-06-11T22:00:00+00:00'


def test_contract_selection_never_mixes_roll_day():
    decisions=[{'effective_session':'2025-06-17'},{'effective_session':'2025-09-17'}]
    frame=pd.DataFrame({'contract':['NQM25','NQU25','NQM25','NQU25','NQU25','NQZ25'],
                        'trade_date':['2025-06-16','2025-06-16','2025-06-17','2025-06-17','2025-09-17','2025-09-17']})
    assert list(data.select(frame,decisions))==[True,False,False,True,False,True]


def test_simultaneous_stop_target_is_stop_and_costs_exact():
    ix=pd.date_range(engine.time_at('2025-07-14','11:58'),periods=2,freq='min')
    g=pd.DataFrame({'open':100.,'high':103.,'low':97.,'close':100.,'volume':10,
                    'trade_date':'2025-07-14','contract':'NQU25','data_quality_flag':'ok'},index=ix)
    r=engine.simulate(g,ix[0]-pd.Timedelta(minutes=1),1,1.,2.)
    assert r['exit_reason']=='stop_both'
    assert r['net_points']==-2.225
    assert r['net_usd']==-44.5


def test_promotion_requires_ci_and_p_not_just_profit():
    protocol=json.loads((ROOT/'research/holdout-protocol.json').read_text())
    metrics={'eligible_days':50,'net_points':500.,'profit_factor':1.5,'ci_low':-1.,'p_value':.2}
    assert holdout.verdict(metrics,protocol)[0]=='HOLDOUT_FAILED'
    metrics.update(ci_low=.1,p_value=.01)
    assert holdout.verdict(metrics,protocol)[0]=='HOLDOUT_PASSED'


def test_zero_trade_days_in_bootstrap_and_initial_zero_drawdown():
    t=pd.DataFrame({'trade_date':['2025-07-14'],'net_points':[-2.],
                    'entry_price':[100.],'entry_utc':['2025-07-14T14:00:00Z']})
    dates=[d.strftime('%Y-%m-%d') for d in pd.bdate_range('2025-07-14',periods=25)]
    r=holdout.extra_metrics(t,dates)
    assert r['eligible_days']==25 and r['max_drawdown_points']==2
    assert r['worst_day_points']==-2 and r['best3_share_net_profit_pct'] is None
    assert r['p_value'] is not None


def test_frozen_engine_fingerprint_and_missing_raw_fail_closed(tmp_path):
    p=json.loads((ROOT/'research/holdout-protocol.json').read_text())
    with pytest.raises(FileNotFoundError):
        holdout.preflight(tmp_path,p)
    p['frozen_engine_sha256']='tampered'
    with pytest.raises(ValueError,match='engine changed'):
        holdout.preflight(tmp_path,p)
