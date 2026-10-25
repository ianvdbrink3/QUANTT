import json

import numpy as np
import pytest

from scripts import asymmetric_regime as r


def bars():
    return {k:np.full(390,x,dtype=float) for k,x in dict(open=100,high=100.25,low=99.75,close=100).items()}


def test_regime_uses_exactly_thirty_completed_bars():
    p=bars()
    with pytest.raises(ValueError):r.classify(p,10)
    q={k:v[:30] for k,v in p.items()}
    assert r.classify(q,10)['regime']=='B'
    assert r.classify(q,np.nan)['regime']=='MISSING_PRIOR_ATR'


@pytest.mark.parametrize('width,expected',[(39.75,'B'),(40.,'IDLE'),(60.,'IDLE'),(60.25,'A')])
def test_strict_regime_boundaries(width,expected):
    p=bars();p['high'][20]=100+width;p['low'][:30]=100;p['close'][29]=101
    assert r.classify({k:v[:30] for k,v in p.items()},100)['regime']==expected


def test_expansion_without_confirmed_breakout_is_idle():
    p=bars();p['high'][20]=200
    assert r.classify({k:v[:30] for k,v in p.items()},100)['regime']=='IDLE'


def test_future_poison_does_not_change_ten_oclock_regime():
    p=bars();before=r.classify({k:v[:30] for k,v in p.items()},10)
    for v in p.values():v[30:]=999999
    assert r.classify({k:v[:30] for k,v in p.items()},10)==before


def test_entry_is_ten_oclock_open_not_confirming_close():
    p=bars();p['high'][20]=108;p['close'][29]=107;p['open'][30]=106
    p['low'][30:]=105;p['high'][30:]=108;p['close'][30:]=106
    t,status=r.execute(p,dict(atr=10),'A_FIXED')
    assert status=='FILLED' and t['entry']==30 and t['entry_price']==106


def test_initial_stop_wins_activation_bar_conflict():
    p=bars();p['high'][30]=111;p['low'][30]=94
    t=r.manage(p,30,100,1,10,.5,breakeven=True)
    assert t['exit']==30 and t['exit_price']==95 and t['reason']=='STOP'


def test_breakeven_only_activates_next_bar():
    p=bars();p['high'][30]=110;p['low'][30]=99
    p['open'][31]=101;p['high'][31]=102;p['low'][31]=99
    t=r.manage(p,30,100,1,10,.5,breakeven=True)
    assert t['exit']==31 and t['exit_price']==100


def test_gap_loss_is_not_capped_at_one_r():
    p=bars();p['open'][31]=94;p['low'][31]=93
    t=r.manage(p,30,100,1,10,.5)
    assert t['exit']==31 and t['exit_price']==94 and t['reason']=='STOP_GAP'


def test_stop_rounds_toward_entry_and_stays_on_tick():
    assert r.stop_level(100,1,3.38)==96.75
    assert r.stop_level(100,-1,3.38)==103.25
    with pytest.raises(ValueError):r.stop_level(100,1,.1)


def test_time_exit_is_fifteen_fortyfive_open():
    p=bars();p['open'][375]=103;p['close'][374]=101;p['close'][375]=200
    t=r.manage(p,30,100,1,10,.5)
    assert t['exit']==375 and t['exit_price']==103 and t['exit_at_open']


def test_limit_exact_touch_does_not_prove_a_fill():
    t,status=r.execute(bars(),dict(atr=10),'B_FADE')
    assert t is None and status=='NO_LIMIT_FILL'


def test_first_oco_side_not_chosen_from_future_pnl():
    p=bars();p['high'][30]=100.5;p['low'][30]=99.5
    for v in p.values():v[31:]=999999
    t,status=r.execute(p,dict(atr=10),'B_FADE')
    assert t is None and status=='UNKNOWN_FIRST_OCO'


def test_entry_bar_stop_has_priority_over_ambiguous_target():
    p=bars();p['low'][30]=96;p['high'][30]=100.25
    t,status=r.execute(p,dict(atr=10),'B_FADE')
    assert status=='FILLED' and t['direction']==1
    assert t['exit']==30 and t['exit_price']==96.25 and t['reason']=='STOP'


def test_entry_bar_target_is_not_credited_without_ordering_evidence():
    p=bars();p['low'][30]=99.5;p['high'][30]=100.25;p['close'][30]=99.75
    # Long99.75 is established inside bar30. Target100 touched, but could
    # have preceded entry; the closing print does not establish a crossing.
    p['open'][31]=99.75;p['high'][31]=100.5;p['low'][31]=99.75
    t,status=r.execute(p,dict(atr=10),'B_FADE')
    assert status=='FILLED' and t['exit']==31 and t['reason']=='TARGET'


def test_close_through_target_proves_entry_then_target():
    p=bars();p['low'][30]=99.5;p['high'][30]=100.25;p['close'][30]=100.25
    t,status=r.execute(p,dict(atr=10),'B_FADE')
    assert status=='FILLED' and t['exit']==30 and t['exit_price']==100


def test_existing_target_marketable_at_open_precedes_later_stop():
    p=bars();p['open'][31]=102;p['high'][31]=103;p['low'][31]=90
    t=r.manage(p,30,100,1,10,.5,target=101)
    assert t['reason']=='TARGET_OPEN' and t['exit_price']==101


def test_marked_path_and_aggregate_net_cost_reconcile():
    p=bars();p['low'][31]=94
    t=r.manage(p,30,100,1,10,.5)
    t.update(day='2021-01-04',quarter='2021Q1',gross_points=-5,net_points=-6.225)
    curve=r.path_for(t,p)
    assert curve[60]==-1.225 and curve[-1]==-6.225
    s=r.describe([t],{'2021-01-04':curve},['2021-01-04'])
    assert s['gross_points']==-5 and s['net_points']==-6.225
    assert s['max_marked_drawdown']==6.225


def test_completed_pool_count_and_regime_accounting():
    if not r.RESULT.exists():pytest.skip('Exploration not computed')
    x=json.loads(r.RESULT.read_text())
    assert x['pool_sessions']==1168
    assert sum(x['regime_counts'].values())==1168
    assert x['atr_ready_sessions']+len(x['missing_ATR_dates'])==1168
    assert not x['full_pool_B_PnL_identifiable'] or not x['ambiguous_OCO_dates']
    for m,row in x['performance'].items():
        assert row['gross_points']-1.225*row['N']==pytest.approx(row['net_points'])
    r.verify()
