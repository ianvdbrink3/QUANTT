import json

import numpy as np
import pytest

from scripts.afternoon_gonogo_audit import (ROOT, block_variance, digest,
    estimate, matrix_hac, null_panel, quote_net, reject, summarize_events)
from scripts.afternoon_feasibility import hac_batch, holm_positive


def test_matrix_kernel_and_independent_batch_estimator_agree():
    rng = np.random.default_rng(2026)
    mask = rng.random(99) < .4
    values = rng.normal(size=(99, 2))*mask[:, None]
    mean, se, covariance = matrix_hac(values, mask)
    other_mean, other_se, _ = estimate(values[None], mask[None])
    assert mean == pytest.approx(other_mean[0])
    assert se == pytest.approx(other_se[0], abs=1e-12)
    assert covariance == pytest.approx(covariance.T)


def test_separate_estimator_matches_existing_on_sparse_panels():
    rng = np.random.default_rng(42)
    mask = rng.random((15, 130)) < .36
    values = rng.normal(size=(15, 130, 2))*mask[:, :, None]
    a = estimate(values, mask)
    b = hac_batch(values, mask)
    for x, y in zip(a, b):
        assert x == pytest.approx(y, abs=1e-12)


def test_direct_holm_agrees_with_ranked_adjustments():
    p = np.random.default_rng(13).uniform(0, .1, (1000, 2))
    assert np.array_equal(reject(p), holm_positive(p, np.ones_like(p)))
    assert reject(np.array([[.01, .8], [.04, .01], [.025, .9]])).tolist() == [[True, False], [True, True], [False, False]]


def test_missing_test_remains_in_family_without_blocking_other():
    assert reject(np.array([[np.nan, .01]])).tolist() == [[False, True]]
    with pytest.raises(ValueError):
        reject(np.array([[.001]]))


def test_quote_pnl_does_not_charge_spread_or_flat_allowance_twice():
    # Static one-tick market: buy ask 20000.25, sell bid 20000.00.
    assert quote_net(20000.25, 20000.) == pytest.approx(-.475)
    assert quote_net(20000.25, 20000., commission_usd=0) == pytest.approx(-.25)
    assert quote_net(20000.25, 20000., remaining_adverse_points=.5) == pytest.approx(-.975)


def test_additional_execution_cost_must_be_nonnegative():
    with pytest.raises(ValueError):
        quote_net(100, 101, -.25)


def test_empirical_panel_preserves_selected_mask_and_pairing():
    mask = np.arange(60) % 2 == 0
    values = np.column_stack([np.arange(60), np.arange(60)*2])*mask[:, None]
    args = (np.random.default_rng(42), 'EMPIRICAL_BLOCK20', 20, 90, mask, values, [1, 1], .5)
    panel, included = null_panel(*args)
    assert np.array_equal(panel[:, :, 1], panel[:, :, 0]*2)
    assert np.all(panel[~included] == 0)


def test_wilson_interval_not_zero_width_at_boundary():
    result = summarize_events(np.ones(100, dtype=bool), 100)
    assert result['rate'] == 1
    assert result['mc_ci95'][0] < 1


def test_block_variance_formula_on_constant_zero_input():
    with np.errstate(invalid='ignore'):
        result = block_variance(np.zeros((60, 2)))
    assert result['model_long_run_coefficient'] == [0, 0]


def test_frozen_audit_outputs_and_no_release():
    r = json.loads((ROOT/'research/afternoon-gonogo-audit-results.json').read_text())
    assert len(r['null_models']) == 21
    assert len(r['partial_null_models']) == 42
    assert not r['v2_changed'] and not r['observed_discovery_mean_tested']
    assert r['protocol']['release'] is False
    for path, expected in r['hashes'].items():
        assert digest(ROOT/path) == expected
    assert r['costs']['frozen_points'] == r['costs']['assumed_execution_points'] + r['costs']['commission_points']
