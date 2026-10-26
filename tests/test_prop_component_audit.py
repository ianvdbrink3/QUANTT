import pytest
from scripts.audit_prop_components import aggregate


def trade(gross, risk, filled=True):
    return dict(component='X', filled=filled, unknown=False, gross=gross, risk=risk,
                day='2026-01-02', entry_time='2026-01-02 15:00:00+00:00', release=29456115)


def test_equal_risk_can_reverse_unscaled_dollar_expectancy():
    # Large-stop winner, small-stop loser: positive dollars need not mean positive R.
    r = aggregate([trade(20, 100), trade(-10, 10), trade(999, 1, False)],
                  ['2026-01-02', '2026-01-05'], 'X', 3.22)
    assert r['trades'] == 2
    assert r['trades_per_21_sessions'] == 21
    assert r['mean_net_USD_1MNQ'] > 0
    assert r['mean_net_initial_stop_R'] < 0
    assert r['profit_factor_USD'] > 1
    assert r['profit_factor_initial_stop_R'] < 1


def test_cost_stress_and_unknown_path_not_silently_ignored():
    ts = [trade(5, 10)]
    a = aggregate(ts, ['2026-01-02'], 'X', 3.22)
    b = aggregate(ts, ['2026-01-02'], 'X', 6.50)
    assert a['mean_net_USD_1MNQ'] - b['mean_net_USD_1MNQ'] == pytest.approx(3.28)
    ts[0]['unknown'] = True
    with pytest.raises(ValueError, match='resolved'):
        aggregate(ts, ['2026-01-02'], 'X', 3.22)
