"""Synthetic pre-outcome checks and read-only completed-output checks."""
import json

import numpy as np
import pytest

from scripts.historical_validation import __main__ as r
from scripts.historical_validation import analysis as a
from scripts.edge_marathon.core import select,fill


def prices():
    return {k:np.full(390,v,dtype=float) for k,v in dict(open=100,high=102,low=98,close=101,volume=10).items()}


def flags():return dict(TOM_RTH=True,COMPRESSED_BREAK5=True,SWEEP_REV_1200=True)


def test_strict_mask_only_drops_predeclared_dates_no_price_access():
    rows=[dict(day='2019-01-14',TOM_RTH=True),dict(day='2019-01-15',TOM_RTH=False),
        dict(day='2019-01-16',TOM_RTH=True),dict(day='2019-01-11',TOM_RTH=True)]
    masks=r.masks(rows,{'2019-01-16'})
    assert masks['PRIMARY_STRICT']==['2019-01-14']
    assert masks['SECONDARY_AVAILABLE']==['2019-01-14','2019-01-16']
    assert '2019-01-15' not in masks['SECONDARY_AVAILABLE']


def test_accepted_inclusion_never_forces_a_half_day():
    masks=r.masks([dict(day='2019-07-03',TOM_RTH=False)],{'2019-07-03'})
    assert masks==dict(PRIMARY_STRICT=[],SECONDARY_AVAILABLE=[])


def test_fixed_specification_and_exact_cost():
    assert a.SEED==20261022311 and a.REPS==10000
    t=fill(dict(model='TOM_RTH',decision=0,entry=0,end=390,direction=1),prices(),dict(atr=200))
    assert t['gross_points']==1 and t['net_points']==pytest.approx(-.225)
    assert t['net_points']/t['atr']==pytest.approx(-.225/200)


@pytest.mark.parametrize('bad',['open','high','low','close','volume'])
def test_missing_required_bar_is_rejected_not_filled(bad):
    p=prices();p[bad][25]=np.nan
    with pytest.raises(ValueError,match='Invalid full RTH'):
        r.generate('2021-01-04',p,dict(atr=200),flags())


def test_no_ATR_eligibility_is_not_a_trade():
    f=flags();f['TOM_RTH']=False
    with pytest.raises(ValueError,match='No full-RTH'):
        r.generate('2021-01-04',prices(),dict(atr=np.nan),f)


def test_only_registered_models_are_filled():
    trades=r.generate('2021-01-04',prices(),dict(atr=200),flags())
    assert {t['model'] for t in trades}=={'TOM_RTH'}


def test_compression_strict_threshold_and_next_open():
    p=prices();p['close'][:5]=103
    p['open'][5]=104
    ctx=dict(atr=100,PDH=102,PDL=98)
    events=[e for e in select(p,ctx) if e['model']=='COMPRESSED_BREAK5']
    assert len(events)==1 and events[0]['decision']==5 and events[0]['entry']==5
    assert fill(events[0],p,ctx)['entry_price']==104
    assert not [e for e in select(p,dict(atr=100,PDH=130,PDL=65)) if e['model']=='COMPRESSED_BREAK5']


def test_sweep_keeps_exact_noon_exit_not_session_close():
    p=prices();p['low'][0]=94
    ctx=dict(atr=100,ONL=95,ONH=105)
    event=next(e for e in select(p,ctx) if e['model']=='SWEEP_REV_1200')
    assert event['entry']==30 and event['end']==150


def test_future_poison_cannot_change_sweep_or_confirmed_compression():
    p=prices();p['low'][0]=94
    ctx=dict(atr=100,ONL=95,ONH=105,PDH=100.5,PDL=98)
    original=[e for e in select(p,ctx) if e['model'] in a.MODELS[:3] and e['decision']<=30]
    poison={k:v.copy() for k,v in p.items()}
    for x in poison.values():x[30:]=999999
    changed=[e for e in select(poison,ctx) if e['model'] in a.MODELS[:3] and e['decision']<=30]
    assert original==changed


def test_portfolio_thirds_do_not_reallocate_idle_sleeves_or_net_costs():
    p=prices();event=dict(model='TOM_RTH',decision=0,entry=0,end=390,direction=1)
    t=dict(fill(event,p,dict(atr=100)),day='2021-01-04')
    out,points,atr,ledger,daily,quarters=a.summarize(['2021-01-04'],{'2021-01-04':[t]},
        {'2021-01-04':(p,{})},{'2021-01-04':flags()},'PRIMARY_STRICT')
    assert points[0,3]==pytest.approx(points[0,0]/3)
    assert atr[0,3]==pytest.approx(points[0,3]/100)
    assert out[a.MODELS[3]]['points']['cost_total']==pytest.approx(1.225/3)


def test_marked_equity_endpoint_and_upfront_cost():
    p=prices();t=dict(entry=30,end=150,direction=-1,entry_price=100,atr=200)
    path=a.point_path([t],p,[1/3])
    assert path[29]==0
    assert path[30]==pytest.approx(-1.225/3)
    assert path[-1]==pytest.approx((-1-1.225)/3)
    assert np.all(path[150:]==path[-1])


def test_bootstrap_joint_identity_seed_and_simultaneous_ci():
    dates=[f'2020-{m:02}-02' for m in range(1,13)]
    x=np.column_stack([np.arange(12),-np.arange(12)*.5,np.zeros(12)])
    matrix=np.column_stack([x,x.mean(axis=1)])
    result=a.intervals(dates,matrix,reps=200)
    assert result==a.intervals(dates,matrix,reps=200)
    for row in result:
        lo,hi=row['mean_R_ci95'];lower,upper=row['mean_familywise95_bonf4']
        assert lower<=lo<=hi<=upper


@pytest.mark.parametrize('count,months,total,p,expected',[
    (29,36,5,.001,'INCONCLUSIVE_INFORMATION_FLOOR'),
    (30,23,5,.001,'INCONCLUSIVE_INFORMATION_FLOOR'),
    (30,24,5,.049,'STATISTICAL_SUPPORT_ON_REGISTERED_REMAINDER'),
    (30,36,5,.05,'NO_STATISTICAL_SUPPORT'),
    (30,36,-5,.001,'NO_STATISTICAL_SUPPORT'),
])
def test_predefined_decision_floor_and_sign(count,months,total,p,expected):
    assert a.decision(dict(total=total,p_holm4=p),[count],months)==expected


def test_holm6_reservation_does_not_run_afternoon_or_rescue_primary():
    results={v:{m:{unit:dict(total=1.) for unit in ('points','atr')} for m in a.MODELS} for v in r.VARIANTS}
    estimates=[dict(p_raw=.01,mean_R_ci95=[0,1],total_R_fixed_N_ci95=[0,2],sharpe_ci95=[0,1],mean_familywise95_bonf4=[-.1,1.1]) for _ in range(16)]
    a.apply_inference(results,estimates)
    for m in a.MODELS:
        row=results['PRIMARY_STRICT'][m]['atr']
        assert row['p_holm4']==.04 and row['p_holm6_reserved']==.06


def test_prerelease_contains_fixed_counts_and_no_outcomes():
    if not r.RELEASE.exists():pytest.skip('Release not yet registered')
    x=json.loads(r.RELEASE.read_text())
    assert x['released'] and not x['parameter_search'] and not x['afternoon_hypotheses_executed']
    assert x['planned_evaluation_days']==dict(PRIMARY_STRICT=733,SECONDARY_AVAILABLE=733)
    assert len(x['provisional_dates'])==9
    assert x['inference']['seed']==20261022311
    assert len(x['previously_inspected_dates_excluded'])==8


def test_completed_replay_keeps_old_bytes_and_trade_counts_consistent():
    if not r.VERIFY.exists():pytest.skip('Released paired run not built')
    r.verify();value=json.loads(r.RESULT.read_text())
    assert value['signals_computed'] and value['holdout_executed']
    assert value['source_verification']['source_files']==105
    assert not value['afternoon_tests_executed'] and value['previous_8_january_days_excluded']
    for model,d in value['sensitivity_difference'].items():assert all(v==0 for v in d.values())
    for variant in r.VARIANTS:
        rows=value['variants'][variant]
        assert rows[a.MODELS[-1]]['points']['total']==pytest.approx(sum(rows[m]['points']['total'] for m in a.MODELS[:3])/3)
        for m in a.MODELS:
            assert sum(q['net_points'] for q in value['quarterly'] if q['variant']==variant and q['model']==m)==pytest.approx(rows[m]['points']['total'])
    assert r.RESULT.read_bytes()==r.PUBLIC.read_bytes()


def test_new_public_results_never_contain_private_trade_or_daily_arrays():
    if not r.PUBLIC.exists():pytest.skip('New results not published locally')
    text=r.PUBLIC.read_text()
    for forbidden in ('entry_price','exit_price','"dates"','"prices"','/Users/','"open":','"high":','"low":'):
        assert forbidden not in text
    assert r.h.ignored(r.OUT/'run1/trades.csv')
