import json

import numpy as np
import pytest

from scripts.morning_recovery_anatomy import early_status,measurement,known_groups
from scripts.register_afternoon_candidate import ROOT,verify


def prices():
    p = np.arange(60,dtype=float)+100
    return dict(open=p,close=p+.25)


def test_following_window_excludes_first_quarter_and_boundary_gap():
    p = prices()
    a = measurement(p)
    p['close'][14] = 1.
    b = measurement(p)
    assert a['following_points'] == b['following_points'] == p['close'][59]-p['open'][15]
    assert a['early_points'] != b['early_points']
    assert a['boundary_gap'] != b['boundary_gap']


def test_first_quarter_selection_ignores_all_later_prices():
    p = prices()
    expected = early_status({k:v[:15] for k,v in p.items()})
    for v in p.values():
        v[15:] *= 100
    assert early_status(p) == expected


@pytest.mark.parametrize('last,status',[(99.,'NEGATIVE'),(100.,'FLAT'),(101.,'POSITIVE')])
def test_flat_not_silently_assigned_to_positive(last,status):
    p = prices();p['close'][14] = last
    assert early_status(p) == status


def test_no_shortened_horizon():
    p = prices()
    with pytest.raises(ValueError):
        measurement({k:v[:59] for k,v in p.items()})


def test_onl_after0945_never_selects_causal_group():
    gaps = {'a','b'}
    boundaries = {'a':15,'b':16,'c':60,'d':61,'e':14}
    g = known_groups(gaps,boundaries)
    assert g['BOTH_KNOWN_0945'] == {'a'}
    assert g['GAP_ONLY_KNOWN_0945'] == {'b'}
    assert g['ONL_ONLY_KNOWN_0945'] == {'e'}
    assert 'c' not in set().union(*g.values())
    assert 'd' not in set().union(*g.values())


def test_candidate_frozen_without_releasing_independent_test():
    result = verify()
    spec = json.loads((ROOT/'research/afternoon-candidate-v1.json').read_text())
    assert result['new_afternoon_runs'] == 0
    assert [r['minutes'] for r in spec['outcomes']] == [15,2]
    assert 'Holm' in spec['statistical_plan']['multiplicity']
    assert spec['data_quality']['timestamp_status'] == 'BAR_START_SUPPORTED_INTERNAL_ONLY'
    assert result['status'] == 'CANDIDATE_SPEC_FROZEN_INDEPENDENT_TEST_NOT_RELEASED'
