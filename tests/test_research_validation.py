import numpy as np
import pandas as pd
import pytest
from quantlab.research_validation import (Instrument,validate_minute_index,coverage_report,
 to_trade_date,session_window,opening_range,vwap_known_at,fixed_events,matched_baseline,
 chronological_splits,block_bootstrap_mean,fdr_bh,cost_sensitivity,test_manifest as build_manifest)

def bars(n=400,start='2026-10-19T13:00:00Z'):
    idx=pd.date_range(start,periods=n,freq='min',tz='UTC')
    return pd.DataFrame({'contract_id':'NQZ26','open':20000.,'high':20001.,
                         'low':19999.,'close':20000.,'volume':10.},index=idx)
def test_contract_specs():
    assert Instrument('NQ',.25,20).validate().multiplier==20
    with pytest.raises(ValueError): Instrument('NQ',.5,20).validate()
def test_canonical_time():
    validate_minute_index(bars())
    x=bars();x.index=x.index.tz_localize(None)
    with pytest.raises(ValueError): validate_minute_index(x)
def test_gap_detection():
    x=bars(5).drop(pd.Timestamp('2026-10-19T13:02:00Z'))
    assert coverage_report(x)['contracts']['NQZ26']['missing_minutes_between_observations']==1
def test_ny_date_conversion():
    assert str(to_trade_date(bars().index)[0])=='2026-10-19'
def test_session_mask():
    assert session_window(bars(),'09:30','10:00').sum()==30
def test_opening_range_known_after_close():
    result=opening_range(bars(),minutes=15)
    assert len(result)==1
    assert result.iloc[0].known_at_utc==pd.Timestamp('2026-10-19T13:45:00Z')
    assert opening_range(bars().drop(pd.Timestamp('2026-10-19T13:40:00Z')),minutes=15).empty
def test_vwap_is_prior_bar_only():
    x=bars(3)
    result=vwap_known_at(x)
    assert np.isnan(result.vwap_prior.iloc[0])
    assert result.vwap_prior.iloc[1]==20000.
def test_events_only_known_feature():
    x=bars(3);x['signal']=pd.Series([0,2,0],index=x.index)
    assert list(fixed_events(x,'signal',1))==[x.index[1]]
def test_matched_baseline():
    a=pd.DataFrame({'hour_et':[9,10],'volatility_regime':['low','high'],'forward_points':[3,7]})
    b=pd.DataFrame({'hour_et':[9],'volatility_regime':['low'],'forward_points':[1]})
    r=matched_baseline(a,b)
    assert r['matched_events']==1 and r['unmatched_events']==1 and r['mean_excess_points']==2
def test_temporal_split_embargo():
    x=pd.DataFrame({'value':range(100)})
    r=chronological_splits(x,embargo=2)
    assert len(r['train'])==58 and len(r['validation'])==16 and len(r['holdout'])==18
def test_bootstrap_deterministic():
    a=block_bootstrap_mean(range(30),samples=100,seed=5)
    assert a==block_bootstrap_mean(range(30),samples=100,seed=5)
def test_multiple_testing_adjustment():
    assert fdr_bh([.01,.04,.2])==pytest.approx([.03,.06,.2])
def test_cost_scenarios():
    r=cost_sensitivity([5,-1],costs=(0,2))
    assert r['2']['mean_net_points']==0
def test_manifest_is_stable():
    a=build_manifest(data_hash='sha',code_ref='commit',instrument=Instrument('ES',.25,50),parameters={'h':15},synthetic=True)
    assert a==build_manifest(data_hash='sha',code_ref='commit',instrument=Instrument('ES',.25,50),parameters={'h':15},synthetic=True)
    assert not a['edge_validated']
