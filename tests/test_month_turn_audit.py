import numpy as np
import pytest

from scripts.month_turn_audit import curve_drawdown, day_record, month_contrast, risk, summary
from scripts.edge_marathon.stats import holm


def prices():
    close = np.linspace(100., 110., 390)
    return dict(open=close.copy(), close=close.copy(), high=close+1, low=close-1)


def row(day='2025-01-02', gross=10., tom=True, atr=20.):
    return dict(day=day, month=day[:7], quarter=day[:4]+'Q'+str((int(day[5:7])-1)//3+1),
                gross_points=gross, net_points=gross-1.225, tom=tom, prior_atr=atr,
                mfe_points=15., mae_points=5.)


def test_original_calendar_not_refined():
    assert day_record('2025-01-02', prices(), {}, 'DISCOVERY')['tom']
    assert day_record('2025-01-06', prices(), {}, 'DISCOVERY')['tom']
    assert not day_record('2025-01-07', prices(), {}, 'DISCOVERY')['tom']


def test_original_partial_december_exception_only_for_discovery():
    assert not day_record('2024-12-31', prices(), {}, 'DISCOVERY')['tom']
    assert day_record('2024-12-31', prices(), {}, 'OTHER')['tom']


def test_missing_atr_never_filters_original_tom_trade():
    r = day_record('2025-01-02', prices(), {}, 'DISCOVERY')
    assert r['tom'] and r['prior_atr'] is None
    assert r['net_points'] == pytest.approx(8.775)


@pytest.mark.parametrize('delay', [0, 1, 5])
def test_delay_changes_entry_only_and_keeps_fixed_exit(delay):
    p = prices()
    r = day_record('2025-01-02', p, {}, 'DISCOVERY', delay=delay)
    assert r['tom'] and r['gross_points'] == p['close'][389]-p['open'][delay]


def test_no_unregistered_delay_or_truncated_session():
    with pytest.raises(ValueError, match='Unregistered'):
        day_record('2025-01-02', prices(), {}, 'DISCOVERY', delay=2)
    with pytest.raises(ValueError, match='390'):
        day_record('2025-01-02', {k:v[:389] for k,v in prices().items()}, {}, 'DISCOVERY')


def test_drawdown_includes_loss_before_first_profit():
    assert curve_drawdown([-10, 5, 10, -20]) == 20
    assert curve_drawdown([-10, -5]) == 15


def test_costs_are_per_roundtrip_not_per_leg_twice():
    r = [row(), row('2025-01-03', gross=-5)]
    base = summary(r); stress = summary(r, 2.225)
    assert base['net_points'] == pytest.approx(2.55)
    assert base['net_points']-stress['net_points'] == 2.
    assert stress['net_dollars'] == pytest.approx(11.)


def observations():
    rows = []
    for m in range(1, 7):
        rows.append(row(f'2025-{m:02}-02', gross=float(m), tom=True))
        rows += [row(f'2025-{m:02}-{d:02}', gross=float(-m), tom=False) for d in range(3, m+4)]
    return rows


def test_bootstrap_computes_pooled_event_means_not_mean_of_month_means():
    rows = observations()
    result = month_contrast(rows, reps=200)
    control = [r['net_points'] for r in rows if not r['tom']]
    assert result['non_tom_mean'] == pytest.approx(np.mean(control))
    assert result['tom_mean'] == pytest.approx(np.mean([r['net_points'] for r in rows if r['tom']]))
    assert result['non_tom_days'] == len(control)


def test_missing_atr_only_excludes_from_diagnostic_common_sample():
    rows = observations(); rows[0]['prior_atr'] = None
    raw = month_contrast(rows, reps=100)
    normalized = month_contrast(rows, normalized=True, reps=100)
    assert raw['tom_days'] == 6
    assert normalized['tom_days'] == 5
    assert rows[0]['tom'] and rows[0]['net_points'] == -.2250000000000001


def test_bootstrap_deterministic_and_has_nonzero_plus_one_p_floor():
    a = month_contrast(observations(), reps=100)
    assert a == month_contrast(observations(), reps=100)
    assert 1/101 <= a['p_raw'] <= 1


def test_four_contrasts_remain_in_one_holm_family():
    assert holm([.01, .02, .2, .9]) == pytest.approx([.04, .06, .4, .9])


def test_minute_marked_equity_exposes_more_risk_than_closed_trade_equity():
    rows = [row(f'2025-01-0{d}', gross=10.) for d in (2, 3, 6)]
    state = {}
    for r in rows:
        p = prices(); p['close'][100] = 50.
        state[r['day']] = (p, {})
    result = risk(rows, state)
    assert summary(rows)['closed_trade_drawdown'] == 0
    assert result['minute_close_equity_drawdown'] > 50
    assert result['top3_share_of_total_net'] == 1


def test_empty_group_is_unavailable_not_fake_flat_trade():
    r = summary([])
    assert r['days'] == 0 and r['mean_net'] is None and r['profit_factor'] is None
