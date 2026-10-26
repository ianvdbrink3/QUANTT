from dataclasses import replace
import pandas as pd
import pytest
from scripts.prop_lifecycle.core import RULES, barrier_fill, payout_request, simulate_start, summarize
from scripts.prop_lifecycle.__main__ import record_path


def trade(day,gross,low=0.,opening=None,unknown=False,activation=10,release=20):
    base=pd.Timestamp(day).value//60_000_000_000
    return dict(day=day,entry_ny_day=day,component='J0830',filled=True,gross=gross,
                unknown=unknown,activation=base+activation,release=base+release,
                records=[[base+10,0.,0.]]+([[base+11,opening,low]] if low<0 else []),
                negative_record_lows=[0.]+([-low] if low<0 else []))


def dates(n=15):
    return pd.bdate_range('2026-01-02',periods=n).strftime('%Y-%m-%d').tolist()


def test_no_evaluation_profit_transfer_same_day_funded_or_reused_payout_days():
    ds=dates(12)
    cs={d:[trade(d,900 if i<2 else 100)] for i,d in enumerate(ds)}
    a=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[0],0)
    assert a['milestones']['eval_pass_day']==ds[1]
    assert a['milestones']['funded_start_day']==ds[2]
    assert a['milestones']['payout1_day']==ds[6]
    assert a['milestones']['payout2_day']==ds[11]
    assert a['fees_USD']==198
    assert a['payouts'][0]['gross']==pytest.approx(5*(200-3.22)/2)
    assert a['received_USD']==pytest.approx(.9*sum(p['gross'] for p in a['payouts']))
    assert a['net_cash_through_horizon_USD']==pytest.approx(a['received_USD']-198)
    assert a['remaining_simulated_equity_USD']>0  # not counted as received dollars


def test_pending_limit_reserves_account_without_future_fill_selection():
    ds=dates(1)
    first=trade(ds[0],0,activation=10,release=100)
    first['filled']=False
    second=trade(ds[0],9999,activation=20)
    a=simulate_start(ds,{ds[0]:[first,second]},'S1-Judas-0830',1,RULES[0],0)
    assert a['trades']==0 and a['blocked_orders']==1
    assert a['state']=='CENSORED_EVALUATION'


@pytest.mark.parametrize('q',[1,2])
def test_fee_and_net_scaling_once_per_filled_trade(q):
    ds=dates(1)
    a=simulate_start(ds,{ds[0]:[trade(ds[0],10)]},'S1-Judas-0830',q,RULES[0],0)
    assert a['remaining_simulated_equity_USD']==pytest.approx(q*(20-3.22))


def test_nonpreregistered_quantity_rejected():
    with pytest.raises(ValueError):
        simulate_start(dates(1),{},'S1-Judas-0830',3,RULES[0],0)


def test_first_record_crossing_and_adverse_gap_price():
    t=trade('2026-01-02',0,low=-1100,opening=-1050)
    hit=barrier_fill(t,-1000)
    assert hit['gross']==-1050 and hit['observed_open']
    assert barrier_fill(t,-1200) is None


def test_DLL_pauses_not_fails_and_blocks_later_order():
    ds=dates(1)
    t=trade(ds[0],100,low=-600)
    later=trade(ds[0],9999,activation=30,release=40)
    a=simulate_start(ds,{ds[0]:[t,later]},'S1-Judas-0830',1,RULES[2],0)
    assert a['DLL_pauses']==1 and not a['state'].startswith('FAILED')
    assert a['trades']==1 and a['blocked_orders']==1
    assert -1000.5<=a['remaining_simulated_equity_USD']<=-1000


def test_DLL_gap_can_breach_hard_floor():
    ds=dates(1)
    a=simulate_start(ds,{ds[0]:[trade(ds[0],100,low=-1200,opening=-1100)]},
                     'S1-Judas-0830',1,RULES[2],0)
    assert a['state'].startswith('FAILED_OBSERVED_OPEN_FLOOR')


def test_gap_is_unknown_not_profit_or_failure_unless_earlier_floor_proves_failure():
    ds=dates(1)
    a=simulate_start(ds,{ds[0]:[trade(ds[0],100,unknown=True)]},'S1-Judas-0830',1,RULES[0],0)
    assert a['source_unknown'] and a['net_cash_through_horizon_USD'] is None
    assert summarize([a])['mean_net_cash_per_start_USD'] is None
    b=simulate_start(ds,{ds[0]:[trade(ds[0],100,low=-1100,unknown=True)]},
                     'S1-Judas-0830',1,RULES[0],0)
    assert not b['source_unknown'] and b['state'].startswith('FAILED')


def test_MFFU_eval_inactivity_policy_not_imported_from_legacy_no_timer():
    ds=dates(10)
    a=simulate_start(ds,{},'S1-Judas-0830',1,RULES[2],0)
    assert a['state']=='FAILED_INACTIVITY_EVALUATION'
    assert a['stop_day']=='2026-01-08'
    b=simulate_start(ds,{},'S1-Judas-0830',1,replace(RULES[2],eval_inactivity=None),0)
    assert b['state']=='CENSORED_EVALUATION'
    assert a['fees_USD']==b['fees_USD']==153


def test_Builder_two_cycles_consistency_buffer_and_cash_deduction():
    r=RULES[2]
    assert payout_request(2600,2600,1400,2,0,0,1,'0001-01-04',r)==0
    assert payout_request(2600,2600,1300,2,0,0,1,'0001-01-04',r)==500
    assert payout_request(2500,1000,400,2,0,1,1,'0001-01-04',r)==0
    assert payout_request(3500,900,400,2,0,1,1,'0001-01-04',r)==900


def test_Topstep_consistency_route_not_standard_winning_day_requirement():
    assert payout_request(1000,1000,350,3,0,0,1,'0001-01-04',RULES[1])==500
    assert payout_request(1000,1000,350,3,0,0,1,'0001-01-04',RULES[0])==0


def test_monthly_calendar_rebill_and_tail_is_not_failure():
    ds=['2026-01-02','2026-02-02','2026-03-03']
    a=simulate_start(ds,{},'S1-Judas-0830',1,RULES[0],0)
    assert a['monthly_payments']==3
    assert a['fees_USD']==147 and a['state']=='CENSORED_EVALUATION'
    assert summarize([a])['failures']==0


def test_no_carry_between_started_accounts():
    ds=dates(3)
    cs={d:[trade(d,900)] for d in ds}
    a=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[0],1)
    assert a['milestones']['eval_pass_day']==ds[2] and a['fees_USD']==198
    assert a['received_USD']==0


def test_post_payout_floor_zero_remains_fixed_after_withdrawal():
    ds=dates(8)
    cs={d:[trade(d,900 if i<2 else 100)] for i,d in enumerate(ds)}
    cs[ds[-1]]=[trade(ds[-1],100,low=-260)]
    a=simulate_start(ds,cs,'S1-Judas-0830',1,RULES[0],0)
    assert a['credited_payouts']==1 and a['state'].startswith('FAILED_CONSERVATIVE_OHLC_FLOOR_FUNDED')


def test_source_path_excludes_post_exit_bar_low_and_truncates_first_gap():
    start=pd.Timestamp('2026-01-02 15:00:00+00:00')
    frame=pd.DataFrame(dict(open=[100,99,101],high=[101,102,105],low=[99,98,50],close=[100,101,52]),
                       index=pd.date_range(start,periods=3,freq='min'))
    t=dict(entry_time=str(start),exit_time=str(start+pd.Timedelta(minutes=2)),
           entry=100,gross=1,night=False,component='J0830',day='2026-01-02',adverse_min=-2)
    detail=dict(direction=1,entry_at_open=True,exit_at_open=True)
    result=record_path(t,frame,None,detail)
    assert result['records'][-1][2]==-2 and not result['unknown']
    frame=frame.drop(frame.index[1]);t['adverse_min']=-1
    result=record_path(t,frame,None,detail)
    assert result['unknown'] and result['records'][-1][2]==-1
