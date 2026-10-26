from dataclasses import replace
import pandas as pd
import pytest
from scripts.prop_lifecycle.core import simulate_start as frozen
from scripts.prop_refinement.core import (RULES,Profile,simulate_start,quantity_for,keep_alive_due)
from scripts.prop_refinement.__main__ import observed_records
from tests.test_prop_lifecycle import trade, dates


def test_original_fields_remain_exact_with_all_switches_off():
    ds=dates(12)
    cs={d:[trade(d,900 if i<2 else 100)] for i,d in enumerate(ds)}
    old=frozen(ds,cs,'S1-Judas-0830',1,RULES[0],0)
    new=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[0],0)
    assert all(new[k]==v for k,v in old.items())


@pytest.mark.parametrize('budget',[250.,300.])
@pytest.mark.parametrize('stop',[10.,30.,100.,250.])
def test_exact_requested_minimum_one_and_cap_six_formula(budget,stop):
    import math
    p=Profile('HYBRID',True,True,budget)
    t=dict(night=False,risk=stop)
    assert quantity_for(t,2,p)==max(1,min(6,math.floor(budget/(2*stop+3.22))))
    assert quantity_for(dict(night=True,risk=stop),2,p)==2


def test_real_overbudget_is_reported_not_silently_called_hard_budget():
    ds=dates(1);t=trade(ds[0],1);t.update(risk=200,night=False)
    a=simulate_start(ds,{ds[0]:[t]},'S1-Judas-0830',1,RULES[0],0,
                     profile=Profile('HYBRID',True,True,300.))
    assert a['minimum_one_MNQ_budget_overruns']==1 and a['judas_budget_overruns']==1
    assert a['max_initial_judas_risk_USD']==403.22


def test_Builder_actual_trade_fee_is_not_the_sizing_denominator():
    t=dict(night=False,risk=40.)
    assert quantity_for(t,1,Profile('HYBRID',True,True,250.))==3
    ds=dates(1);t.update(trade(ds[0],10))
    a=simulate_start(ds,{ds[0]:[t]},'S1-Judas-0830',1,RULES[2],0,
                     profile=Profile('HYBRID',True,True,250.))
    assert a['remaining_simulated_equity_USD']==pytest.approx(3*(20-6.50))
    assert a['judas_budget_overruns']==1 # 3*(80+6.50)>250


def test_keepalive_resets_timer_costs_cash_and_is_not_a_winning_day():
    ds=dates(30)
    a=simulate_start(ds,{},'S1-Judas-0830',1,RULES[2],0,
                     profile=Profile('KA',True,True))
    assert a['keep_alive_roundtrips']>0
    assert a['state']=='CENSORED_EVALUATION'
    assert a['keep_alive_cost_USD']==pytest.approx(3.22*a['keep_alive_roundtrips'])
    assert a['remaining_simulated_equity_USD']==pytest.approx(-a['keep_alive_cost_USD'])
    assert not a['milestones']['eval_pass_day']


def test_weekend_lead_is_preknown_not_monday_retroactive_repair():
    assert keep_alive_due(5,0,8) # Fri day5, next Mon day8
    assert not keep_alive_due(4,0,5)
    assert keep_alive_due(6,0,7)


def test_no_keepalive_when_pending_order_reserves_noon():
    ds=dates(5);orders={}
    for d in ds:
        base=pd.Timestamp(d+'T12:00',tz='America/New_York').value//60_000_000_000
        pending=trade(d,0,activation=1,release=2);pending.update(filled=False,release=base+60)
        orders[d]=[pending]
    a=simulate_start(ds,orders,'S1-Judas-0830',1,RULES[0],0,
                     profile=Profile('KA',True,True))
    assert a['keep_alive_roundtrips']==0


def test_normal_fill_day_does_not_add_maintenance_trade_or_double_count_day():
    ds=dates(20)
    cs={d:[trade(d,1)] for d in ds}
    a=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[2],0,
                     profile=Profile('KA',True,True))
    assert a['keep_alive_roundtrips']==0 and a['trades']==len(ds)


def test_keepalive_cost_cannot_cross_floor_without_closing_account():
    ds=dates(12)
    rules=replace(RULES[0],drawdown=5)
    a=simulate_start(ds,{},'S1-Judas-0830',1,rules,0,
                     profile=Profile('KA',True,True))
    assert a['state']=='FAILED_KEEPALIVE_COST_FLOOR_EVALUATION'
    assert a['keep_alive_roundtrips']==2


def test_observed_risk_path_walks_later_bars_across_gap_but_never_exit_open_low():
    ts=pd.DatetimeIndex(['2026-01-02T23:00Z','2026-01-02T23:02Z','2026-01-03T14:30Z'])
    frame=pd.DataFrame(dict(open=[100,95,101],low=[99,90,1],contract=['NQH26']*3),index=ts)
    t=dict(entry_time=str(ts[0]),exit_time=str(ts[-1]),entry=100,gross=1,risk=None,
           reason='NEXT_OPEN',unknown=True)
    result=observed_records(t,frame)
    assert result['records'][-1][2]==-10 and not result['unknown']
    assert result['source_gap_retained']
