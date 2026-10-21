import numpy as np
import pandas as pd
import pytest
from scripts.reproduce_research import engine
from scripts.reproduce_research.volume_path import active_volume_history,trade_paths,summarize_paths


def volume_source():
    frames=[]
    for i,day in enumerate(pd.bdate_range('2025-02-03',periods=25).strftime('%Y-%m-%d')):
        ix=pd.date_range(engine.time_at(day,'09:30'),periods=2,freq='min')
        frames.append(pd.DataFrame({'contract':'OLD' if i<20 else 'NEW','trade_date':day,
                                    'volume':[i+1,100+i],'price':100.},index=ix))
    return pd.concat(frames)


def test_same_clock_20_median_minimum10_survives_roll():
    raw=volume_source();new=active_volume_history(raw)
    assert new.prior_same_minute_median_volume.iloc[18:20].isna().all()
    assert new.prior_same_minute_median_volume.iloc[20]==np.median(np.arange(1,11))
    assert new.prior_same_minute_median_volume.iloc[40]==10.5
    assert new.prior_same_minute_median_volume.iloc[48]==np.median(np.arange(5,25))
    assert new.prior_same_minute_median_volume.iloc[41]==109.5
    pd.testing.assert_frame_equal(new[raw.columns],raw)


def test_volume_reference_does_not_use_current_or_future_sessions():
    raw=volume_source();old=active_volume_history(raw)
    changed=raw.copy();changed.loc[changed.trade_date.ge('2025-03-03'),'volume']*=100
    new=active_volume_history(changed)
    cutoff=raw.trade_date.le('2025-03-03')
    pd.testing.assert_series_equal(old.loc[cutoff,'prior_same_minute_median_volume'],new.loc[cutoff,'prior_same_minute_median_volume'])


def test_dst_uses_ny_clock_not_utc_clock():
    raw=volume_source()
    # Same NY minute across the US DST boundary: reference remains continuous.
    last=raw.iloc[:2].copy();last.index=pd.date_range(engine.time_at('2025-03-10','09:30'),periods=2,freq='min')
    last['trade_date']='2025-03-10';last['contract']='NEW'
    combined=pd.concat([raw,last])
    result=active_volume_history(combined)
    assert result.prior_same_minute_median_volume.iloc[-2]==np.median(np.arange(6,26))


def fixture_path(side=1,reason='stop',net=-2.225):
    ix=pd.date_range(engine.time_at('2025-06-17','10:00'),periods=3,freq='min')
    # Risk 2. Last bar reaches an apparent +2R but might do so after the stop.
    g=pd.DataFrame(dict(contract='NEW',trade_date='2025-06-17',open=[100,100,100],
                         high=[101.,102.,104.],low=[99.5,99,98],close=[100.,101.,98.]),index=ix)
    if side==-1:
        hi=g.high.copy();lo=g.low.copy();g['high']=200-lo;g['low']=200-hi
        g['open']=200-g.open;g['close']=200-g.close
    trade=dict(strategy='TEST',trade_date='2025-06-17',contract='NEW',entry_utc=ix[0],exit_bar_utc=ix[-1],
               entry_price=100.,stop=100-side*2.,target=100+side*4.,exit_price=100-side*2.,direction=side,
               net_points=net,exit_reason=reason,both_hit_bar=False)
    return g,pd.DataFrame([trade])


@pytest.mark.parametrize('side',[1,-1])
def test_R_uses_initial_raw_stop_and_exit_bar_is_not_certain(side):
    g,t=fixture_path(side);paths=trade_paths(g,t);p=paths.iloc[0]
    assert p.initial_R_points==2 and p.MFE_R_lower==1 and p.MFE_R_bar_upper==2
    assert p.MAE_R_lower==1 and p.MAE_R_bar_upper==1
    assert p.MFE_first_bar_minute==2 and p.MFE_completed_prefix_minute==1
    assert p.MAE_first_bar_minute==2 and p.net_R==-2.225/2
    s=summarize_paths(paths)['TEST'];half,one,onehalf=s['thresholds']
    assert half['certain_hits']==one['certain_hits']==1
    assert onehalf['certain_hits']==0 and onehalf['possible_hits_including_certain']==1
    assert onehalf['conditional_sign_fraction_bounds']['negative']=={'lower':1.,'upper':1.}
    assert s['exits'][1]['net_points']==-2.225


def test_session_close_exit_has_no_post_exit_bar_ambiguity():
    g,t=fixture_path(reason='noon')
    t['target']=105.;t['exit_price']=98.5
    g.loc[g.index[-1],'low']=98.25;g.loc[g.index[-1],'close']=98.5
    p=trade_paths(g,t).iloc[0]
    assert p.MFE_R_lower==p.MFE_R_bar_upper==2
    assert p.MAE_R_lower==p.MAE_R_bar_upper==.875
    assert p.exit_group=='time_session'


def test_small_vwap_target_prevents_false_post_exit_threshold_hits():
    g,t=fixture_path(reason='target',net=-.225)
    t['target']=101.;t['exit_price']=101.
    # Earlier complete bars must not have hit that target in this synthetic path.
    g.loc[g.index[:-1],'high']=100.5
    g.loc[g.index[-1],'low']=99.25;g.loc[g.index[-1],'close']=100.75
    p=trade_paths(g,t).iloc[0]
    assert p.MFE_R_lower==p.MFE_R_bar_upper==.5
    h=summarize_paths(trade_paths(g,t))['TEST']['thresholds'][1]
    assert h['possible_hits_including_certain']==0


def test_exit_endpoint_is_included_but_next_bar_is_excluded():
    g,t=fixture_path(reason='target',net=2.775)
    t['exit_price']=104.
    extra=g.iloc[-1:].copy();extra.index+=pd.Timedelta(minutes=1);extra['high']=1000
    p=trade_paths(pd.concat([g,extra]),t).iloc[0]
    assert p.MFE_R_lower==p.MFE_R_bar_upper==2


def test_zero_excursion_time_is_entry_not_missing():
    g,t=fixture_path()
    g['high']=100.
    p=trade_paths(g,t).iloc[0]
    assert p.MFE_first_bar_minute==0
    g,t=fixture_path(reason='target',net=2.775)
    g['low']=100.;t['exit_price']=104.
    p=trade_paths(g,t).iloc[0]
    assert p.MAE_first_bar_minute==0


def test_stop_both_counts_as_stop_and_sign_totals_reconcile():
    g,t=fixture_path(reason='stop_both');t['both_hit_bar']=True
    paths=trade_paths(g,t);s=summarize_paths(paths)['TEST']
    assert s['stop_both_trades']==1
    assert sum(e['trades'] for e in s['exits'])==1
    for h in s['thresholds']:
        assert sum(v['certain'] for v in h['by_final_net_sign'].values())==h['certain_hits']
        assert sum(v['possible_including_certain'] for v in h['by_final_net_sign'].values())==h['possible_hits_including_certain']


def test_missing_minutes_and_wrong_stop_fail():
    g,t=fixture_path()
    with pytest.raises(ValueError,match='Incomplete'):trade_paths(g.drop(g.index[1]),t)
    t['stop']=101.
    with pytest.raises(ValueError,match='loss side'):trade_paths(g,t)


def test_duplicate_or_mixed_contract_sessions_fail():
    raw=volume_source()
    with pytest.raises(ValueError,match='Unique'):active_volume_history(pd.concat([raw,raw.iloc[:1]]))
    broken=raw.copy();broken.iloc[1,broken.columns.get_loc('contract')]='OTHER'
    with pytest.raises(ValueError,match='One active'):active_volume_history(broken)
