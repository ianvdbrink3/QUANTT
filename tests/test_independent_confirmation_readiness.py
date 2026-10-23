import pandas as pd
import pytest

from scripts.afternoon_inference_round import partition
from scripts.independent_confirmation_readiness import count_information


def calendar(n):
    return pd.bdate_range('2027-01-01', periods=n).strftime('%Y-%m-%d').tolist()


def test_guard_days_never_become_scored_events():
    days = calendar(260)
    result = count_information(days, days)
    assert result['scored_weekday_positions'] == 120
    assert result['scored_selected_days'] == 120
    assert result['selected_in_guard_or_tail'] == 140
    assert result['information_gate_satisfied']


def test_one_horizon_pair_does_not_double_count_a_day():
    days = calendar(260)
    with pytest.raises(ValueError, match='Unique selected'):
        count_information(days, [days[0], days[0]])


def test_120_total_still_fails_when_one_block_has_fewer_than8():
    days = calendar(520)
    groups, _, _ = partition(520)
    selected = [days[int(i)] for i in groups[0][:7]]
    selected += [days[int(i)] for g in groups[1:] for i in g[:17]]
    result = count_information(days, selected)
    assert result['scored_selected_days'] == 126
    assert result['minimum_total_satisfied']
    assert not result['minimum_each_satisfied']
    assert not result['information_gate_satisfied']


def test8_per_block_does_not_override_total120_gate():
    days = calendar(520)
    groups, _, _ = partition(520)
    result = count_information(days, [days[int(i)] for g in groups for i in g[:8]])
    assert result['scored_selected_days'] == 64
    assert result['minimum_each_satisfied']
    assert not result['information_gate_satisfied']


def test_tail_positions_stay_unscored():
    days = calendar(783)
    result = count_information(days, days)
    assert result['scored_selected_days'] == 640
    assert result['selected_in_guard_or_tail'] == 143


def test_closed_or_missing_days_are_not_replaced():
    days = calendar(520)
    groups, _, _ = partition(520)
    selected = [days[int(i)] for g in groups for i in g[:15]]
    assert count_information(days, selected)['scored_selected_days'] == 120
    selected.remove(days[int(groups[0][0])])
    result = count_information(days, selected)
    assert result['scored_selected_days'] == 119
    assert not result['information_gate_satisfied']


def test_calendar_order_and_outside_dates_rejected():
    days = calendar(260)
    with pytest.raises(ValueError, match='chronological'):
        count_information(days[::-1], [])
    with pytest.raises(ValueError, match='belong'):
        count_information(days, ['2030-01-02'])
