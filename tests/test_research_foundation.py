"""Fail-closed research foundation regression tests with synthetic fixtures."""
import json
import pandas as pd
import pytest
from quantlab.research_contract import validate_bars,dataset_fingerprint,save_curated
from quantlab.synthetic_scenarios import known_path
from quantlab.sandbox_execution import FillConfig,simulate_long
from quantlab.experiment_audit import record_experiment

def canonical():
    return pd.DataFrame([{'timestamp_utc':'2026-10-19T13:30:00Z',
      'instrument_id':'NQ','contract_id':'NQZ26','venue':'CME','market_type':'future',
      'source':'fixture','open':20000,'high':20001,'low':19999,'close':20000.25,'volume':2}])

def test_canonical_stable_fingerprint():
    x=canonical()
    assert dataset_fingerprint(x)==dataset_fingerprint(x.copy())
    assert validate_bars(x).shape[0]==1

def test_cfd_and_future_identity_not_conflated():
    x=canonical()
    c=x.copy()
    c['market_type']='index_cfd'
    c['contract_id']=None
    c['venue']='Dukascopy'
    assert len(validate_bars(pd.concat([x,c],ignore_index=True)))==2

def test_reject_duplicate_bar_key():
    x=canonical()
    with pytest.raises(ValueError,match='Duplicate'):
        validate_bars(pd.concat([x,x],ignore_index=True))

def test_reject_missing_futures_contract():
    x=canonical()
    x['contract_id']=None
    with pytest.raises(ValueError,match='contract'):
        validate_bars(x)

def test_parquet_roundtrip(tmp_path):
    x=canonical()
    result=save_curated(x,tmp_path/'bars.parquet')
    assert result['rows']==1
    assert pd.read_parquet(result['path']).shape[0]==1

def test_ambiguous_fills_are_bounded():
    x=known_path()
    assert simulate_long(x,20000,FillConfig(4,4,1,20,'pessimistic'))['net_points']==-5
    assert simulate_long(x,20000,FillConfig(4,4,1,20,'optimistic'))['net_points']==3
    unknown=simulate_long(x,20000,FillConfig(4,4,1,20,'unresolved'))
    assert unknown['status']=='AMBIGUOUS' and unknown['pnl_usd'] is None

def test_gap_stop_is_not_filled_at_better_stop_price():
    x=known_path('gap_stop')
    assert simulate_long(x,20000,FillConfig(4,4))['gross_points']==-6

def test_experiment_provenance_and_rejection(tmp_path):
    path=tmp_path/'experiments.jsonl'
    kwargs=dict(hypothesis_id='HYP-NQ-001',dataset_hash='testhash',
                code_ref='abc123',parameters={'window':15},
                source_kind='synthetic_fixture',results={'passed_fixture':True})
    a=record_experiment(path,status='SCREENED',**kwargs)
    b=record_experiment(path,status='SCREENED',**kwargs)
    assert a['run_id']==b['run_id']
    assert len(path.read_text().splitlines())==2
    with pytest.raises(ValueError,match='cannot validate'):
        record_experiment(path,status='HOLDOUT_PASSED',**kwargs)
