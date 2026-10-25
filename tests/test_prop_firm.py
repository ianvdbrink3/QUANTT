import json
import numpy as np
import pandas as pd
import pytest
from scripts.prop_firm import core as c


def profile(**updates):
    x=dict(id='TEST',drawdown=2000,lock=0,dll=None,target=3000,consistency=.30,min_days=4,inactivity_days=None,news_gate=False);x.update(updates);return x


def days(values,mins=None):
    dates=pd.bdate_range('2025-01-06',periods=len(values)).strftime('%Y-%m-%d')
    return {day:dict(net=v,minimum=min(0,v) if mins is None else mins[i],observed_minimum=min(0,v) if mins is None else mins[i],N=int(v!=0),active=v!=0) for i,(day,v) in enumerate(zip(dates,values))}


def test_friday_signal_uses_sunday_not_closed_friday_globex():
    t=c.globex_entry('2025-01-03','2025-01-06')
    assert t==c.h.at('2025-01-05','18:00')


def test_cash_holiday_gap_does_not_hold_across_intervening_daily_flat_window():
    assert c.globex_entry('2025-01-17','2025-01-21')==c.h.at('2025-01-20','18:00')


def test_globex_new_york_dst_changes_utc_time():
    assert c.globex_entry('2025-03-07','2025-03-10').hour==22
    assert c.globex_entry('2025-01-03','2025-01-06').hour==23


def test_entry_cannot_precede_completed_signal():
    with pytest.raises(ValueError):c.globex_entry('2025-01-06','2025-01-06')


def test_sixteen_held_position_crosses_flat_window_but_eighteen_does_not():
    t=dict(entry_time=c.h.at('2025-01-06','16:00').isoformat(),exit_time=c.h.at('2025-01-07','09:30').isoformat(),exit_at_open=True)
    assert c.flat_window_violation(t)
    t['entry_time']=c.h.at('2025-01-06','18:00').isoformat()
    assert not c.flat_window_violation(t)


def test_sixteen_stop_before_cutoff_is_not_a_flat_window_violation():
    t=dict(entry_time=c.h.at('2025-01-06','16:00').isoformat(),exit_time=c.h.at('2025-01-06','16:05').isoformat(),exit_at_open=False)
    assert not c.flat_window_violation(t)
    t['exit_time']=c.h.at('2025-01-06','16:10').isoformat()
    assert c.flat_window_violation(t)


def test_eod_floor_does_not_ratchet_on_unrealized_profit():
    x=c.account_check(days([500,-300],[0,-1700]),profile())
    assert x['first_potential_MLL'] is None  # floor-1500 vs secondday minimum500-1700=-1200
    assert x['ending_floor']==-1500


def test_unrealized_loss_can_breach_even_with_positive_day_close():
    x=c.account_check(days([500,100],[0,-2100]),profile())
    assert x['first_observed_MLL']=='2025-01-07'


def test_floor_locks_at_starting_balance_not_trails_forever():
    x=c.account_check(days([4000,-2500]),profile())
    assert x['ending_floor']==0 and x['first_potential_MLL'] is None


def test_mffu_floor_locks_at_plus100_and_never_moves_down():
    x=c.account_check(days([2500,-100]),profile(lock=100))
    assert x['ending_floor']==100


def test_consistency_uses_total_net_not_gross_winning_sum():
    x=c.account_check(days([1000,-500,1000,1000]),profile())
    assert x['best_day_fraction_of_net']==pytest.approx(.4)
    assert not x['consistency30_at_end'] and x['first_target_and_consistency'] is None


def test_thirty_percent_is_not_a_breach_and_extra_profit_can_resolve_it():
    x=c.account_check(days([1500,1000,1000,1500]),profile())
    assert x['first_potential_MLL'] is None and x['consistency30_at_end']
    assert x['evaluation_ready_before_risk_trigger']


def test_negative_total_has_no_fake_consistency_percentage():
    x=c.account_check(days([100,-500]),profile())
    assert x['best_day_fraction_of_net'] is None and not x['consistency30_at_end']


def test_daily_loss_is_soft_pause_not_fabricated_account_loss():
    x=c.account_check(days([-1100,2500]),profile(dll=1000))
    assert x['risk_status']=='DLL_SOFT_PAUSE_REQUIRES_CHANGED_EXECUTION'
    assert not x['evaluation_ready_before_risk_trigger'] and x['first_DLL_soft_pause']=='2025-01-06'


def test_potential_ohlc_loss_distinguished_from_observed_loss():
    ds=days([100]);next(iter(ds.values()))['minimum']=-2100
    x=c.account_check(ds,profile())
    assert x['first_potential_MLL'] and x['first_observed_MLL'] is None
    assert x['risk_status']=='POTENTIAL_MLL_BREACH_OHLC_BOUND'


def test_inactivity_measured_from_account_activation_without_invented_trades():
    ds=days([0]*8)
    x=c.account_check(ds,profile(inactivity_days=7))
    assert x['inactivity_first_diagnostic']=='2025-01-13'


def test_news_restricted_profile_never_certifies_without_calendar():
    x=c.account_check(days([1000]*4),profile(news_gate=True))
    assert x['risk_status']=='NEWS_CALENDAR_NOT_VERIFIED' and not x['evaluation_ready_before_risk_trigger']


def test_mnq_cost_is_not_nq_fee_divided_by_ten():
    t=dict(exit_day='2025-01-06',entry_time=c.h.at('2025-01-06','18:00').isoformat(),gross_points=10,path_points=[-1.225,8.775],adverse_gross_points=-2)
    ds,r=c.dollar_panel([t],['2025-01-06'],6.5,3)
    assert r['net_USD']==40.5  # (10*2-6.5)*3
    assert ds['2025-01-06']['minimum']==-31.5


def test_complete_replay_preserves_baseline_and_18_flat_rule():
    from scripts.prop_firm import __main__ as run
    run.verify();x=json.loads(run.RESULT.read_text())
    assert json.loads(run.PROOF.read_text())['status']=='BYTE_IDENTICAL_PROP_FIRM_REPLAYS'
    assert len(x['account_checks'])==936 and len(x['dollar_stress'])==108
    for row in x['account_checks']:assert row['full_compliance_certified'] is False
    for b in run.PERIODS:
        assert x['performance'][b]['S1_J0830_16']['net_R']==pytest.approx(json.loads(run.prior.RESULT.read_text())['performance'][b]['S1_JUDAS']['net_R'])
    assert x['rules']['profiles'][4]['consistency']==.30
