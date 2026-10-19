"""Bidirectional conservative fill and risk regression cases."""
import pandas as pd
import pytest
from quantlab.futures_execution import ExecutionSettings,simulate,equity_statistics
def one(o,h,l,c):
    return pd.DataFrame({'open':[o],'high':[h],'low':[l],'close':[c]},
                        index=pd.date_range('2026-10-19T13:30:00Z',periods=1,tz='UTC'))

def settings(side='long',**kw):
    return ExecutionSettings(side=side,stop_points=4,target_points=8,
        multiplier=20,**kw)

def test_long_stop():
    r=simulate(one(20000,20001,19995,19997),20000,settings())
    assert r['gross_points']==-4 and r['exit_reason']=='stop'
def test_short_stop():
    r=simulate(one(20000,20005,19999,20003),20000,settings('short'))
    assert r['gross_points']==-4 and r['exit_reason']=='stop'
def test_short_target():
    r=simulate(one(20000,20001,19990,19991),20000,settings('short'))
    assert r['gross_points']==8 and r['exit_reason']=='target'
def test_long_target():
    assert simulate(one(20000,20010,19999,20008),20000,settings())['gross_points']==8
def test_long_gap_stop_no_price_improvement():
    path=pd.concat([one(20000,20001,19999,20000),one(19994,19996,19993,19995)])
    path.index=pd.date_range('2026-10-19T13:30:00Z',periods=2,freq='min',tz='UTC')
    assert simulate(path,20000,settings())['gross_points']==-6
def test_short_gap_stop_no_price_improvement():
    path=pd.concat([one(20000,20001,19999,20000),one(20006,20007,20005,20006)])
    path.index=pd.date_range('2026-10-19T13:30:00Z',periods=2,freq='min',tz='UTC')
    assert simulate(path,20000,settings('short'))['gross_points']==-6
def test_colliding_levels_report_bounds():
    bar=one(20000,20009,19995,20000)
    p=simulate(bar,20000,settings(ambiguity='pessimistic'))
    o=simulate(bar,20000,settings(ambiguity='optimistic'))
    u=simulate(bar,20000,settings(ambiguity='unresolved'))
    assert (p['gross_points'],o['gross_points'])==(-4,8)
    assert u['status']=='AMBIGUOUS' and u['net_usd'] is None
def test_short_collision_bounds():
    bar=one(20000,20005,19991,20000)
    assert simulate(bar,20000,settings('short',ambiguity='pessimistic'))['gross_points']==-4
    assert simulate(bar,20000,settings('short',ambiguity='optimistic'))['gross_points']==8
def test_costs_and_contracts():
    r=simulate(one(20000,20010,19999,20008),20000,
      settings(contracts=2,spread_points=1,slippage_points_per_side=.25,
               commission_usd_per_side_per_contract=3))
    assert r['gross_usd']>0 and r['commission_usd']==12
    assert r['net_usd']==r['gross_usd']-12
def test_position_cap():
    with pytest.raises(ValueError,match='risk limit'):
        simulate(one(20000,20001,19999,20000),20000,settings(contracts=6,max_contracts=5))
def test_starting_mid_must_match_next_open():
    with pytest.raises(ValueError,match='first next-bar open'):
        simulate(one(20001,20002,20000,20001),20000,settings())
def test_drawdown_with_losses():
    trades=[{'status':'FILLED','net_usd':100},{'status':'FILLED','net_usd':-250},
            {'status':'FILLED','net_usd':50}]
    e=equity_statistics(trades)
    assert e['end_usd']==99900 and e['max_drawdown_usd']==250
def test_unresolved_trades_cannot_be_scored():
    with pytest.raises(ValueError,match='incomplete'):
        equity_statistics([{'status':'AMBIGUOUS','net_usd':None}])
