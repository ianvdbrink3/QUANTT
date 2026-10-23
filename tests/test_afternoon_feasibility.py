import json

import numpy as np
import pandas as pd
import pytest

from scripts.afternoon_feasibility import (ROOT, circular_indices, hac_batch,
    holm_positive, power_n, required_n, sha, simulate, wilson)
from scripts.afternoon_specificity import mean_influence, uncertainty
from scripts.independent_data_inventory import classify, extra_dates


def test_parallel_holm_allows_either_horizon_without_rescue_gate():
    p = np.array([[.9, .01], [.01, .04], [.04, .9], [.001, .04]])
    means = np.array([[1, 1], [1, 1], [1, 1], [-1, 1]])
    assert holm_positive(p, means).tolist() == [[False, True], [True, True], [False, False], [False, True]]


def test_hac_vectorized_matches_frozen_estimator_with_calendar_gaps():
    calendar = pd.bdate_range('2024-01-01', periods=30).strftime('%Y-%m-%d').tolist()
    mask = np.arange(30) % 3 != 0
    x = np.zeros((30, 2))
    x[mask, 0] = np.arange(mask.sum()) - 7
    x[mask, 1] = x[mask, 0] * -2
    means, se, n = hac_batch(x[None], mask[None])
    frame = pd.DataFrame(dict(day=np.array(calendar)[mask], points=x[mask, 0]))
    mean, scores = mean_influence(frame, calendar, 'points')
    frozen = uncertainty(mean, scores, int(n[0]), int(n[0]-1))
    assert means[0, 0] == pytest.approx(mean)
    assert se[0, 0] == pytest.approx(frozen['se_HAC5'])


def test_injected_constant_does_not_change_hac_variance():
    rng = np.random.default_rng(42)
    mask = rng.random((4, 80)) > .5
    x = rng.normal(size=(4, 80, 2)) * mask[:, :, None]
    mean, se, _ = hac_batch(x, mask)
    shifted, new_se, _ = hac_batch(x + mask[:, :, None] * [4, 6], mask)
    assert shifted == pytest.approx(mean + [4, 6])
    assert new_se == pytest.approx(se)


def test_required_sample_is_minimum_and_scales_with_noise():
    n = required_n(4, 15)
    assert power_n(n, 4, 15) >= .8 > power_n(n-1, 4, 15)
    assert required_n(4, 30) > n
    assert required_n(2, 15) > n > required_n(6, 15)


def test_circular_blocks_keep_pairing_and_adjacency():
    ix = circular_indices(np.random.default_rng(2), 10, 39, 454)
    assert ix.shape == (10, 39)
    assert np.all((np.diff(ix[:, :20], axis=1) % 454) == 1)
    assert np.all((ix >= 0) & (ix < 454))


def test_synthetic_planning_simulation_is_deterministic():
    rng = np.random.default_rng(42)
    mask = np.arange(100) % 2 == 0
    x = rng.normal(size=(100, 2)) * mask[:, None]
    x[mask] -= x[mask].mean(axis=0)
    protocol = dict(replications=100, effects_net_points=[2], scheduled_sessions=[50], seed=123)
    a = simulate(mask, x, protocol)
    assert a == simulate(mask, x, protocol)
    assert len(a[0]) == 3 and len(a[1]) == 1


def test_inventory_classification_is_not_independence_certification():
    record = dict(rows_with_timestamp=50, sha256='known', rows_before_consumed=10, rows_after_consumed=0)
    assert classify(record, {'known'}).startswith('REGISTERED_DISCOVERY')
    assert classify(record, set()).endswith('UNVERIFIED')
    assert classify(dict(rows_with_timestamp=0), set()) == 'EMPTY_OR_UNREADABLE_NOT_DATA'


def test_timestamp_only_reader_ignores_invalid_ohlcv(tmp_path):
    path = tmp_path / 'nq.csv'
    path.write_text('timestamp,open,volume\n2024-01-02 09:30:00,INVALID,INVALID\n2026-10-01 15:00:00,INVALID,INVALID\n')
    result = extra_dates(path, 'timestamp')
    assert result['rows_before_consumed'] == result['rows_after_consumed'] == 1


def test_frequency_interval_contains_estimate():
    low, high = wilson(162, 454)
    assert low < 162/454 < high


def test_saved_outputs_match_protocol_sources_and_no_new_release():
    result = json.loads((ROOT / 'research/afternoon-feasibility-results.json').read_text())
    assert result['selected_days'] == 162
    assert result['observed_mean_tested'] is False and result['independent_outcomes_read'] is False
    assert result['method']['release'] is False
    assert len(result['joint_Holm2_simulations']) == 63
    for path, digest in result['hashes'].items():
        assert sha(ROOT / path) == digest
    assert all(0 <= x['positive_family_false_support'] <= x['any_sign_family_rejection'] <= 1 for x in result['zero_calibration'])
