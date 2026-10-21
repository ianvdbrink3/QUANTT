import ast
import json
from pathlib import Path

import pandas as pd
import pytest

from scripts.oos_preparation import adapter
from scripts.oos_preparation.power import normal_power

ROOT = Path(__file__).resolve().parents[1]


def calendar():
    return adapter.Calendar(json.loads((ROOT/'research/oos-calendar-register.json').read_text()))


def fixture(contract, day, volume=1, price=100.):
    ix = calendar().grid(day)
    return pd.DataFrame({'open':price,'high':price,'low':price,'close':price,
                         'volume':volume,'contract':contract,'trade_date':day},index=ix)


def test_dst_and_evening_session_labels():
    a = adapter.at('2025-10-31','09:30')
    b = adapter.at('2025-11-03','09:30')
    assert (a.hour,b.hour) == (13,14)
    ix = pd.DatetimeIndex([adapter.at('2025-09-30','16:59'),adapter.at('2025-09-30','18:00')])
    assert list(adapter.session_dates(ix)) == ['2025-09-30','2025-10-01']


def test_unknown_calendar_fails_closed():
    with pytest.raises(ValueError, match='CALENDAR_UNVERIFIED'):
        calendar().grid('2026-04-03')


def test_thanksgiving_does_not_invent_missing_afternoon():
    c = calendar()
    assert len(c.grid('2025-11-27')) == 1140
    assert len(c.grid('2025-11-28')) == 1155
    assert len(c.grid('2025-11-28',remove_observed_outage=True)) == 510
    f = fixture('NQZ25','2025-11-27')
    row = adapter.audit_contract(f,c,'2025-11-27','2025-11-27')[0]
    assert row['noon_prefix_complete'] and not row['standard_clean']


def test_outage_calendar_does_not_relax_prefix_gate():
    c = calendar()
    f = fixture('NQZ25','2025-11-28')
    keep = c.grid('2025-11-28',remove_observed_outage=True)
    f = f.loc[keep]
    row = adapter.audit_contract(f,c,'2025-11-28','2025-11-28')[0]
    assert row['unresolved_missing'] == 0 and not row['noon_prefix_complete']


def test_identical_overlap_deduplicated_without_price_change():
    f = fixture('NQM25','2025-06-16')
    g = adapter.combine([f,f],'2025-06-16','2025-06-16')
    pd.testing.assert_frame_equal(g,f,check_freq=False)


def test_conflicting_overlap_rejected():
    f = fixture('NQM25','2025-06-16')
    with pytest.raises(ValueError,match='Conflicting'):
        adapter.combine([f,f.assign(close=101.)],'2025-06-16','2025-06-16')


def test_contract_duplicates_are_not_cross_contract_duplicates():
    f = fixture('NQM25','2025-06-16')
    g = fixture('NQU25','2025-06-16')
    assert len(adapter.combine([f,g],'2025-06-16','2025-06-16')) == 2760


def test_stage_is_idempotent_and_refuses_overwrite(tmp_path):
    source,target = tmp_path/'source.csv',tmp_path/'raw/source.csv'
    source.write_text('original')
    first = adapter.stage_immutable(source,target)
    assert adapter.stage_immutable(source,target) == first
    source.write_text('different')
    with pytest.raises(ValueError,match='Refusing'):
        adapter.stage_immutable(source,target)
    assert target.read_text() == 'original'


def test_roll_pit_future_mutation_cannot_revise_decision():
    old = fixture('NQM25','2025-06-16',1,100.)
    new = fixture('NQU25','2025-06-16',2,104.)
    f = pd.concat([old,new])
    r = adapter.determine_roll(f,'NQM25','NQU25',calendar(),'2025-06-16')
    future = fixture('NQU25','2025-06-17',999999,99999.)
    assert adapter.determine_roll(pd.concat([f,future]),'NQM25','NQU25',calendar(),'2025-06-16') == r
    assert r['effective_session'] == '2025-06-17' and r['spread_points'] == 4.
    assert pd.Timestamp(r['spread_available_utc']) <= pd.Timestamp(r['effective_utc'])


def test_equal_volume_has_no_roll_fallback():
    f = pd.concat([fixture('NQM25','2025-06-16'),fixture('NQU25','2025-06-16')])
    with pytest.raises(ValueError,match='DATA_INSUFFICIENT'):
        adapter.determine_roll(f,'NQM25','NQU25',calendar(),'2025-06-16')


def test_source_contract_identity_must_match_filename(tmp_path):
    with pytest.raises(ValueError,match='quarterly contract'):
        adapter.load_csv(tmp_path/'nqh26_fake.csv','NQZ25')


def test_missing_bar_is_reported_never_imputed():
    f = fixture('NQZ25','2025-10-01').iloc[1:]
    row = adapter.audit_contract(f,calendar(),'2025-10-01','2025-10-01')[0]
    assert row['unresolved_missing'] == 1 and not row['noon_prefix_complete']
    assert len(f) == 1379


def test_preparation_has_no_strategy_or_feature_calls():
    forbidden = {'hypotheses','simulate','build_features','trade_paths','metrics'}
    for name in ['adapter.py','prepare.py','power.py']:
        tree = ast.parse((ROOT/'scripts/oos_preparation'/name).read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                function = node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else ''
                assert function not in forbidden
            if isinstance(node,ast.ImportFrom):
                assert not (node.module or '').startswith('scripts.reproduce_research')


def test_analytical_power_is_a_planning_scenario_not_measured_oos():
    assert normal_power(52,0,100) == pytest.approx(.05)
    assert normal_power(240,10,100) > normal_power(52,10,100)


def test_public_preparation_has_no_future_outcome_and_manifest_matches():
    d = json.loads((ROOT/'public/data/research-oos-preparation.json').read_text())
    assert d['status'] == 'DATA_INSUFFICIENT'
    assert d['scoring_run'] is False and d['signals_computed'] is False
    assert d['active_contract_eligible_days'] is None
    assert d['standard_clean_days'] == 51 and d['complete_noon_prefix_days'] == 52
    assert d['source_manifest_sha256'] == adapter.sha(ROOT/'research/oos-source-register.json')
    assert d['calendar_sha256'] == adapter.sha(ROOT/'research/oos-calendar-register.json')
    assert d['frozen_protocol_sha256'] == adapter.sha(ROOT/'research/vnext-future-oos-protocol.json')
    serialized = json.dumps(d)
    assert all(k not in serialized for k in ['entry_price','exit_price','signal_utc','future_net_pnl'])
    assert d['power_planning']['historical_eligible_days'] == 159
