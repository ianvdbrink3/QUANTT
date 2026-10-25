import json

import numpy as np
import pandas as pd
import pytest

from scripts.two_pillar import core as c
from scripts.two_pillar import __main__ as r


def example():
    times=pd.DatetimeIndex(['2020-01-02T21:00Z','2020-01-02T21:01Z','2020-01-03T14:29Z','2020-01-03T14:30Z'])
    prices={k:np.full(4,v,dtype=float) for k,v in dict(open=1000,high=1001,low=999,close=1000,volume=10).items()}
    return times,prices


def trade(prices=None,atr=100,missing=None,stop=False):
    times,p=example()
    return c.night('2020-01-02','2020-01-03',times,p if prices is None else prices,
                   atr,[] if missing is None else missing,catastrophe=stop)


def test_fixed_cost_normalization_prior_atr_and_entry_denominator():
    _,p=example();p['open'][-1]=1010
    t=trade(p)
    assert t['net_points']==8.775
    assert t['net_R']==pytest.approx(.08775)
    assert t['net_pct']==pytest.approx(.8775)
    assert t['gross_R']==.1


def test_missing_atr_not_imputed():
    with pytest.raises(ValueError,match='ATR unavailable'):
        c.enrich(dict(entry_price=1000,gross_points=1,net_points=-.225),np.nan)


def test_exit_bar_low_and_close_cannot_affect_overnight_mae_or_return():
    _,p=example();p['open'][-1]=1002
    before=trade(p)
    p['low'][-1]=1;p['close'][-1]=1
    after=trade(p)
    assert before==after
    assert after['mae_R']==.01


def test_intraminute_low_not_just_closes_is_used_for_mae():
    _,p=example();p['low'][1]=920
    t=trade(p)
    assert t['mae_R']==.8 and t['net_points']==-1.225


def test_exit_open_is_included_in_mae():
    _,p=example();p['open'][-1]=900
    assert trade(p)['mae_R']==1.


def test_catastrophe_stop_touch_is_filled_and_charged_once():
    _,p=example();p['low'][1]=950
    t=trade(p,stop=True)
    assert t['reason']=='STOP' and t['exit_price']==950
    assert t['net_points']==-51.225 and t['net_R']==-.51225


def test_catastrophe_stop_gap_not_artificially_capped():
    _,p=example();p['open'][1]=900;p['low'][1]=899
    t=trade(p,stop=True)
    assert t['reason']=='STOP_GAP' and t['exit_price']==900
    assert t['net_R']<-.5


def test_stop_at_exit_open_is_processed_without_future_exit_low():
    _,p=example();p['low'][-1]=900
    assert trade(p,stop=True)['reason']=='NEXT_OPEN'
    p['open'][-1]=900
    assert trade(p,stop=True)['reason']=='STOP_GAP'


def test_stop_rounds_toward_entry_and_stays_on_tick():
    t=trade(atr=100.3,stop=True)
    assert t['stop_price']==950 and (1000-t['stop_price'])<=.5*100.3


def test_first_stop_fill_does_not_use_later_extremes():
    _,p=example();p['low'][1]=940
    before=trade(p,stop=True)
    p['open'][2:]=1;p['low'][2:]=.5;p['close'][2:]=.5
    after=trade(p,stop=True)
    for k in ('exit_price','exit_time','net_points','path_points','mae_R'):
        assert before[k]==after[k]


def test_missing_before_stop_is_unknown_not_zero_print():
    times,p=example();p['low'][2]=940
    t=trade(p,missing=[times[1]+pd.Timedelta(minutes=1)],stop=True)
    assert not t['stop_path_identified'] and not t['complete_holding_path']


def test_missing_after_known_stop_does_not_invalidate_first_fill():
    times,p=example();p['low'][1]=940
    t=trade(p,missing=[times[2]-pd.Timedelta(minutes=1)],stop=True)
    assert t['stop_path_identified'] and not t['complete_holding_path']


def test_evening_stop_accounted_next_cash_boundary():
    _,p=example();p['low'][1]=940
    t=trade(p,stop=True)
    assert t['actual_exit_civil_day']=='2020-01-02'
    assert t['exit_day']=='2020-01-03'


def test_net_pf_recomputed_after_normalization_not_reused_from_points():
    a=trade(atr=100);b=trade(atr=200)
    a.update(gross_points=10,net_points=8.775,gross_R=.1,net_R=.08775,gross_pct=1,net_pct=.8775)
    b.update(gross_points=-10,net_points=-11.225,gross_R=-.05,net_R=-.056125,gross_pct=-1,net_pct=-1.1225)
    x=c.description([a,b])
    assert x['R']['profit_factor']>1 and x['points']['profit_factor']<1


def test_portfolio_rejects_overlapping_positions():
    with pytest.raises(ValueError,match='overlap'):
        c.stats([trade(),trade()],['2020-01-02','2020-01-03'])


def test_daily_sharpe_uses_zero_cash_days_not_trade_only():
    _,p=example();p['open'][-1]=1010
    t=trade(p)
    x=c.stats([t],['2020-01-02','2020-01-03','2020-01-06'])
    expected=np.sqrt(252)*np.mean([0,.08775,0])/np.std([0,.08775,0],ddof=1)
    assert x['sharpe_daily_R']==pytest.approx(expected)
    assert x['cash_days']==3


def test_marked_drawdown_uses_path_and_charges_fee_at_entry():
    _,p=example();p['close'][1]=900;p['open'][-1]=1010
    x=c.stats([trade(p)],['2020-01-02','2020-01-03'])
    assert x['max_marked_drawdown_points']==pytest.approx(101.225)
    assert x['max_marked_drawdown_R']==pytest.approx(1.01225)


def test_R_equals_one_does_not_confuse_points_and_R_drawdown():
    _,p=example();p['open'][-1]=1002
    x=c.stats([trade(p,atr=1)],['2020-01-02','2020-01-03'])
    assert x['max_marked_drawdown_R']==x['max_marked_drawdown_points']
    assert x['net_R']==x['net_points']


def test_quarter_attribution_uses_daily_exit_boundary():
    t=trade();t.update(day='2019-12-31',exit_day='2020-01-02',entry_time='2019-12-31T21:00Z',exit_time='2020-01-02T14:30Z')
    x=c.stats([t],['2019-12-31','2020-01-02'])
    assert next(q for q in x['quarterly'] if q['quarter']=='2019Q4')['N']==0
    assert next(q for q in x['quarterly'] if q['quarter']=='2020Q1')['N']==1


def test_sequential_A_and_B_add_without_halfweight_or_fee_netting():
    _,p=example();p['open'][-1]=1010;a=trade(p)
    b=c.enrich(dict(day='2020-01-03',exit_day='2020-01-03',entry_time='2020-01-03T14:45Z',exit_time='2020-01-03T20:55Z',
                    entry_price=1000,exit_price=1020,gross_points=20.,net_points=18.775,path_points=[-1.225,18.775]),100)
    x=c.stats([a,b],['2020-01-02','2020-01-03'])
    assert x['N']==2 and x['net_R']==pytest.approx(.2755)
    assert x['net_points']==pytest.approx(27.55)
    assert x['points']['gross_total']-x['net_points']==pytest.approx(2*1.225)


def test_original_parity_catches_membership_and_cost_changes():
    old=[dict(day='2020-01-02',net_points=1.)]
    with pytest.raises(ValueError,match='membership'):
        r.parity([],old,('net_points',))
    with pytest.raises(ValueError,match='numeric'):
        r.parity([dict(day='2020-01-02',net_points=2.)],old,('net_points',))


def test_completed_audit_counts_and_additivity():
    if not r.RESULT.exists():pytest.skip('Audit not yet computed')
    x=json.loads(r.RESULT.read_text())
    assert sum(z['SMA20_candidate_dates'] for z in x['coverage'].values())==1024
    assert x['portfolio']['COMBINED']['A']['N']==100
    assert x['portfolio']['COMBINED']['B']['N']==149
    for b in r.BLOCKS:
        for field in ('net_R','net_points','N'):
            assert x['portfolio'][b]['A_PLUS_B'][field]==pytest.approx(x['portfolio'][b]['A'][field]+x['portfolio'][b]['B'][field])
    r.verify()
