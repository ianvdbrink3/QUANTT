import json
import numpy as np
import pandas as pd
from quantlab.research import hypothesis_trades, metrics, block_inference, benjamini_hochberg, append_registry


def fixture():
    index=pd.date_range('2025-03-19T12:30Z',periods=120,freq='min')
    x=np.arange(120)*.1+20000
    return pd.DataFrame({'open':x,'high':x+1,'low':x-1,'close':x+.05,'volume':1},index=index)

SPEC={'timezone':'America/New_York','entry':'09:30','horizon_minutes':60,'direction':'long'}

def test_causal_entry_and_complete_exit():
    t=hypothesis_trades(fixture(),SPEC)
    assert len(t)==1
    assert t.entry.iloc[0]=='2025-03-19T13:30:00+00:00'
    assert np.isclose(t.gross_points.iloc[0],5.95)


def test_missing_exit_cannot_move_trade_to_next_available_bar():
    f=fixture().drop(pd.Timestamp('2025-03-19T14:29Z'))
    assert hypothesis_trades(f,SPEC).empty


def test_gap_inside_trade_rejected():
    f=fixture().drop(pd.Timestamp('2025-03-19T14:00Z'))
    assert hypothesis_trades(f,SPEC).empty


def test_prior_direction_does_not_use_future():
    f=fixture()
    spec={**SPEC,'direction':'reverse_prior_hour'}
    before=hypothesis_trades(f,spec)
    f.loc[f.index>=pd.Timestamp('2025-03-19T13:30Z'),'close']+=1000
    after=hypothesis_trades(f,spec)
    assert before.direction.iloc[0]==after.direction.iloc[0]==-1


def test_round_trip_costs_and_initial_drawdown():
    t=pd.DataFrame({'gross_points':[1,-2,3],'entry_price':[20000]*3,'date':['a','b','c']})
    m=metrics(t,2)
    assert m['net_points']==-4
    assert m['max_drawdown_points']==5
    assert m['win_rate']==1/3


def test_fdr_accounts_for_all_planned_tests():
    assert np.allclose(benjamini_hochberg([.01,.04,.2]),[.03,.06,.2])


def test_bootstrap_reproducible_and_insufficient_sample():
    assert block_inference([1]*10)['p_value'] is None
    assert block_inference(np.arange(30))==block_inference(np.arange(30))


def test_registry_idempotent(tmp_path):
    path=tmp_path/'registry.jsonl'
    result=[{'run_id':'abc','id':'H1','metrics':{},'equity':[]}]
    append_registry(path,result,'2025-01-01')
    append_registry(path,result,'2025-01-02')
    assert len(path.read_text().splitlines())==1
    assert 'equity' not in json.loads(path.read_text())
