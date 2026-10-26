from dataclasses import replace
import math
import pytest
from tests.test_prop_lifecycle import trade,dates
from scripts.prop_uniform.core import Profile,RULES,quantity_for,simulate_start
from scripts.prop_refinement.core import simulate_start as old_start


@pytest.mark.parametrize('budget',[300.,350.,400.])
@pytest.mark.parametrize('stop',[10.,80.,160.,200.,400.])
def test_both_pillars_share_exact_floor_zero_cap_formula(budget,stop):
    profile=Profile(uniform_budget=budget)
    for night in (True,False):
        q=quantity_for(dict(risk=stop,night=night),2,profile)
        assert q==max(0,min(6,math.floor(budget/(2*stop+3.22))))
        assert q*(2*stop+3.22)<=budget


def test_zero_quantity_does_not_reserve_order_pay_fee_or_reset_clock():
    ds=dates(1)
    wide=trade(ds[0],999,activation=1,release=9999);wide.update(risk=1000.,night=False)
    narrow=trade(ds[0],10,activation=5,release=10);narrow.update(risk=40.,night=False)
    a=simulate_start(ds,{ds[0]:[wide,narrow]},'S1-Judas-0830',2,RULES[0],0,
                     profile=Profile(uniform_budget=300.))
    assert a['zero_size_skipped_signals']==1 and a['trades']==1
    assert a['blocked_orders']==0
    assert a['remaining_simulated_equity_USD']==pytest.approx(3*(20-3.22))


def test_no_minimum_one_reintroduced_between_budget_and_125percent():
    assert quantity_for(dict(risk=170.,night=True),2,Profile(uniform_budget=300.))==0


def test_refinement_default_fields_unchanged_when_new_switches_off():
    ds=dates(12);cs={d:[trade(d,900 if i<2 else 100)] for i,d in enumerate(ds)}
    old=old_start(ds,cs,'S1-Judas-0830',1,RULES[0],0)
    actual=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[0],0)
    assert all(actual[k]==v for k,v in old.items())


def test_full_year_keeps_paying_after_two_and_first_two_snapshot_matches():
    ds=dates(22);cs={d:[trade(d,900 if i<2 else 100)] for i,d in enumerate(ds)}
    capped=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[0],0)
    full=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[0],0,profile=Profile(continue_after_two=True))
    assert capped['credited_payouts']==2 and full['credited_payouts']==4
    assert full['received_first_two_USD']==pytest.approx(capped['received_USD'])
    assert full['net_first_two_USD']==pytest.approx(capped['cash_net_accrued_USD'])
    assert full['net_full_window_USD']-full['net_first_two_USD']==pytest.approx(full['net_after_second_USD'])
    assert full['payouts'][2]['day']>full['payouts'][1]['day']


def test_builder_five_sim_payout_limit_not_silently_extended_into_live():
    ds=dates(45)
    cs={d:[trade(d,900 if i<2 else 600)] for i,d in enumerate(ds)}
    p=Profile(continue_after_two=True)
    stage=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[2],0,profile=p)
    assert stage['credited_payouts']==5 and stage['state']=='SIM_LIMIT_REQUIRES_LIVE_RULES'
    assert stage['net_full_window_USD'] is None
    extension=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[2],0,
                  profile=replace(p,ignore_builder_stage_limit=True))
    assert extension['credited_payouts']>5
    assert extension['net_full_window_USD'] is not None


def test_no_trade_cost_or_fictional_account_profit_for_zero_size_only():
    ds=dates(1);t=trade(ds[0],9999);t.update(risk=500.,night=False)
    a=simulate_start(ds,{ds[0]:[t]},'S1-Judas-0830',2,RULES[0],0,
                     profile=Profile(uniform_budget=300.))
    assert a['trades']==0 and a['remaining_simulated_equity_USD']==0
    assert a['cash_net_accrued_USD']==-49
