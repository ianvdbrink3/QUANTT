"""Meaningful account execution invariants, independent of ranking outcomes."""
from copy import deepcopy
import numpy as np
import pandas as pd
import pytest
from scripts.prop_challenge import core as c
from scripts.prop_challenge.__main__ import FIRMS
from scripts.prop_challenge.data import path_limits, minute


def dates(n=63):return list(pd.bdate_range('2025-01-06',periods=n).strftime('%Y-%m-%d'))
def combo(**kw):
    d=dict(id='TEST',night='NONE',morning='J0830',late=['ICT1']);d.update(kw);return d
def event(gross=0,adverse=0,obs=0,activation=1,release=2,component='J0830',**kw):
    d=dict(component=component,activation=activation,release=release,risk=50.,night=False,filled=True,
           observed_min=obs,adverse_min=adverse,gross=gross,unknown=False);d.update(kw);return d
def run(events,firm=None,profile=None):
    ds=dates();ev={ds[i]:[dict(t,activation=t['activation']+1440*i,release=t['release']+1440*i) for t in v] for i,v in events.items()}
    return c.simulate(ds,ev,combo(),profile or c.profiles()[0],firm or FIRMS[0])


def test_finite_universe_is_complete_and_not_hidden_winner_selection():
    assert len(c.universe())==319
    assert len({r['id'] for r in c.universe()})==319
    assert sum(c.admissible(m,p) for m in c.universe() for p in c.profiles())==2487


@pytest.mark.parametrize('budget',[200,300,400])
@pytest.mark.parametrize('risk',[5.,25.,100.,300.])
def test_stop_dollar_size_rounds_down_and_cannot_silently_force_one_contract(budget,risk):
    p=c.Profile('TEST','RISK',budget)
    q=int(c.size(p,risk,False,np.array([0.]),np.array([-2000.]),np.array([0.]),.55,50)[0])
    assert q*(risk*2+3.22)<=budget and q<=10


def test_no_stop_night_excluded_from_finite_dollar_risk_sizing():
    assert not c.admissible(combo(night='S2_NO_STOP'),c.Profile('R','RISK',200))
    assert c.admissible(combo(night='S2_NO_STOP'),c.profiles()[0])


def test_cushion_uses_current_realized_profit_and_headroom_only():
    p=c.Profile('C','CUSHION',400)
    q=c.size(p,20,False,np.array([0,800,800,800.]),np.array([-1000,-1000,-1000,-1000.]),np.array([0,0,1400,1700.]),.55,50)
    assert list(q)==[4,10,6,0]


def test_both_fixed_and_risk_quantities_respect_firm_and_pillar_caps():
    assert c.size(c.Profile('X','FIXED',100),1,False,0,-2000,0,.3,30)==30
    assert c.size(c.Profile('X','RISK',400),1,True,0,-2000,0,.3,30)==3


def test_21_42_63_windows_have_different_complete_denominators():
    x=run({})
    assert [len(x[h]) for h in c.HORIZONS]==[43,22,1]
    assert all(r[0]==c.OPEN for r in x[21])


def test_target_is_not_a_pass_when_best_day_dominates_total_profit():
    x=run({0:[event(gross=2000)]})[21][0]
    assert x[0]==c.OPEN and x[3]>3000


def test_topstep_two_day_minimum_and_consistency_can_require_three_days():
    x=run({i:[event(gross=600)] for i in range(3)})[21][0]
    assert x[0]==c.PASS and x[1]==3 and x[2]==3


def test_mffu_requires_four_active_days_and_thirty_percent():
    x=run({i:[event(gross=600)] for i in range(4)},firm=FIRMS[1])[21][0]
    assert x[0]==c.PASS and x[1]==4


def test_unrealized_floor_touch_fails_even_with_profitable_final_exit():
    x=run({0:[event(gross=500,adverse=-1000,obs=-1000)]})[21][0]
    assert x[0]==c.FLOOR_OBSERVED


def test_ohlc_only_possible_breach_is_distinct_from_observed_breach():
    x=run({0:[event(gross=500,adverse=-1000,obs=-100)]})[21][0]
    assert x[0]==c.FLOOR_BOUND


def test_floor_does_not_trail_an_intraday_high_that_was_not_realized():
    x=run({0:[event(gross=50,adverse=-500)],1:[event(gross=50,adverse=-800)]})[21][0]
    assert x[0]==c.OPEN


def test_eod_floor_ratcheting_can_breach_next_day_without_large_total_drawdown():
    x=run({0:[event(gross=500)],1:[event(gross=50,adverse=-1000,obs=-1000)]})[21][0]
    assert x[0]==c.FLOOR_OBSERVED and x[1]==2


def test_unknown_held_minutes_never_turn_into_silent_survival_or_pass():
    x=run({0:[event(gross=5000,unknown=True)]})[21][0]
    assert x[0]==c.UNKNOWN
    summary=c.summarize([x],FIRMS[0])
    assert summary['pass_rate']==0 and summary['pass_upper_source_unknown']==1
    assert summary['cost_per_pass_proxy_USD'] is None


def test_new_rolling_start_has_zero_equity_no_inherited_profits():
    x=run({0:[event(gross=600)],1:[event(gross=600)],2:[event(gross=600)]})[21]
    assert x[0][0]==c.PASS and x[1][0]==c.OPEN


def test_pending_unfilled_order_blocks_later_setup_without_looking_at_fill():
    pending=event(filled=False,release=10)
    late=event(gross=500,activation=3,release=4,component='ICT1')
    x=run({0:[pending,late]})[21][0]
    assert x[2]==0 and x[6]==1


def test_held_judas_position_blocks_afternoon_entry_even_after_1015():
    x=run({0:[event(gross=10,release=1000),event(gross=900,activation=300,release=800,component='ICT1')]})[21][0]
    assert x[2]==1 and x[6]==1


def test_no_size_means_no_order_reservation_and_later_affordable_trade_allowed():
    first=event(risk=200,release=1000)
    second=event(risk=10,gross=5,activation=3,component='ICT1')
    x=run({0:[first,second]},profile=c.Profile('R','RISK',200))[21][0]
    assert x[2]==1 and x[7]==1


def test_zero_profit_fills_count_as_activity_no_invented_keepalive():
    x=run({0:[event(gross=1.61)]},firm=FIRMS[1])[21][0]
    assert x[0]==c.INACTIVE and x[2]==1


def test_pass_terminates_attempt_and_prevents_later_account_losses():
    events={i:[event(gross=600)] for i in range(3)}
    events[3]=[event(gross=-5000,adverse=-5000,obs=-5000)]
    x=run(events)[21][0]
    assert x[0]==c.PASS and x[1]==3 and x[2]==3


def test_full_roundtrip_fee_is_per_contract_not_nq_fee_divided_by_ten():
    x=run({0:[event(gross=10)]},profile=c.profiles()[2])[21][0]
    assert x[3]==pytest.approx((20-3.22)*3)


def test_reset_fee_is_not_double_charged_and_unknown_cost_is_not_certified():
    assert c.economic_cost(1,1,0,0,98,49,149,49)==247
    assert c.economic_cost(1,1,0,0,98,99,149,49)==297
    assert c.economic_cost(1,1,0,1,98,49,149,49) is None


def test_mffu_one_time_fee_has_no_fake_activation_or_monthly_renewal():
    x=run({},firm=dict(FIRMS[1],inactivity=None))[63][0]
    assert x[4]==225 and x[5]==225


def test_monthly_fees_stop_at_pass_and_grow_for_unfinished_accounts():
    assert run({})[63][0][4]==147
    assert run({i:[event(gross=600)] for i in range(3)})[63][0][4]==49


def test_exit_open_excludes_future_exit_bar_low():
    ix=pd.date_range('2025-01-06T14:30Z',periods=2,freq='min')
    t=dict(entry_time=ix[0],exit_time=ix[1],entry_price=100,exit_at_open=True,gross_points=1,direction=1)
    p=dict(open=np.array([100,101]),close=np.array([100,99]),low=np.array([99,-1000]),high=np.array([101,2000]))
    assert path_limits(t,ix,p)==(-0.,-1.,False)


def test_unobserved_price_after_data_gap_cannot_prove_an_earlier_floor_breach():
    ix=pd.date_range('2025-01-06T14:30Z',periods=3,freq='min')
    t=dict(entry_time=ix[0],exit_time=ix[2],entry_price=100,exit_at_open=True,gross_points=-10000,direction=1)
    p=dict(open=np.array([100,100,-9900]),close=np.array([100,100,-9900]),low=np.array([99,99,-10000]),high=np.array([101,101,101]))
    assert path_limits(t,ix,p,[ix[1]])==(0.,-1.,True)


def test_frozen_daily_pnl_prefix_unchanged_by_future_candidates():
    first={i:[event(gross=10)] for i in range(21)}
    a=run(first)[21][0]
    first[40]=[event(gross=90000)]
    assert run(first)[21][0]==a


def test_repeat_same_input_byte_stable_and_inputs_not_mutated():
    first={0:[event(gross=10)]};saved=deepcopy(first)
    assert run(first)==run(first) and first==saved


def scalar_fixed_one(ds,events,start,horizon,firm):
    """Independent deliberately simple one-account oracle for vector engine."""
    balance=0.;floor=-2000.;peak=0.;best=0.;active=0;count=0;busy=-float('inf')
    last=pd.Timestamp(ds[start]);status=c.OPEN;blocked=0
    for offset,day in enumerate(ds[start:start+horizon]):
        if firm['inactivity'] and (pd.Timestamp(day)-last).days>=firm['inactivity']:
            status=c.INACTIVE;break
        opened=False;before=balance
        for t in events.get(day,[]):
            if busy>t['activation']:
                blocked+=1;continue
            busy=t['release']
            if not t['filled']:continue
            opened=True;count+=1;last=pd.Timestamp(day)
            observed=balance+2*t['observed_min']-3.22
            bound=balance+2*t['adverse_min']-3.22
            if bound<=floor+1e-9:
                status=c.FLOOR_OBSERVED if observed<=floor+1e-9 else c.FLOOR_BOUND
                balance=floor;break
            if t['unknown']:
                status=c.UNKNOWN;break
            balance+=2*t['gross']-3.22
        if status!=c.OPEN:break
        active+=opened;best=max(best,balance-before);peak=max(peak,balance)
        floor=max(floor,min(firm['lock'],peak-2000.))
        if balance>=3000-1e-9 and best<=firm['consistency']*balance+1e-9 and active>=firm['min_days']:
            status=c.PASS;break
    return status,offset+1,count,balance,blocked


@pytest.mark.parametrize('firm',FIRMS,ids=['topstep','mffu'])
@pytest.mark.parametrize('seed',[4,17,902])
def test_vectorized_all_starts_match_independent_scalar_account_oracle(firm,seed):
    ds=dates(76);rng=np.random.default_rng(seed);events={}
    for i,day in enumerate(ds):
        if rng.random()<.65:
            g=float(rng.normal(90,430));adverse=min(0.,g-float(rng.uniform(0,500)))
            events[day]=[event(gross=g,adverse=adverse,obs=min(0.,g),activation=i*1440+600,
                release=i*1440+700,unknown=bool(rng.random()<.015),filled=bool(rng.random()>.1))]
            if rng.random()<.4:
                events[day].append(event(gross=float(rng.normal(80,200)),activation=i*1440+650,
                    release=i*1440+690,component='ICT1'))
    result=c.simulate(ds,events,combo(),c.profiles()[0],firm)
    for horizon,rows in result.items():
        assert len(rows)==len(ds)-horizon+1
        for start,row in enumerate(rows):
            expected=scalar_fixed_one(ds,events,start,horizon,firm)
            assert row[0:3]==expected[0:3]
            assert row[3]==pytest.approx(expected[3])
            assert row[6]==expected[4]


def test_silver_bullet_selected_from_published_development_table_by_declared_rule():
    import json
    from scripts.prop_challenge.data import ROOT,SPECS
    x=json.loads((ROOT/'research/ict-study-results.json').read_text())['samples']['TRADE_THROUGH']
    for label,window in [('SB_AM','AM'),('SB_PM','PM')]:
        names=[name for name in x['COMBINED'] if name.startswith('ICT2_') and f'_{window}_' in name
               and all(x[b][name]['net_ATR_R']>0 for b in ('2019_2021','2024_2026'))]
        rank=lambda name:(min(x[b][name]['sharpe_ATR_R'] for b in ('2019_2021','2024_2026')),
                          min(x[b][name]['net_ATR_R'] for b in ('2019_2021','2024_2026')))
        assert SPECS[label]==max(names,key=rank)
