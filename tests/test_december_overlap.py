import ast
import json
from pathlib import Path

import pandas as pd
import pytest

from scripts.oos_preparation import adapter, december

ROOT = Path(__file__).resolve().parents[1]


def calendar():
    return adapter.Calendar(json.loads((ROOT/'research/december-overlap-protocol.json').read_text())['calendar'])


def bars(contract, day, volume):
    ix = calendar().grid(day)
    return pd.DataFrame(dict(open=100., high=100., low=100., close=100., volume=volume,
                             contract=contract, trade_date=day), index=ix)


def test_december_calendar_does_not_approve_christmas():
    assert len(calendar().grid('2025-12-15')) == 1380
    with pytest.raises(ValueError, match='CALENDAR_UNVERIFIED'):
        calendar().grid('2025-12-24')


def test_december_first_crossover_not_standard_roll_date():
    f = pd.concat([bars('NQZ25','2025-12-12',3), bars('NQH26','2025-12-12',1),
                   bars('NQZ25','2025-12-15',1), bars('NQH26','2025-12-15',2)])
    r = adapter.determine_roll(f, 'NQZ25', 'NQH26', calendar(), '2025-12-15')
    assert r['decision_session'] == '2025-12-15'
    assert r['effective_session'] == '2025-12-16'
    assert pd.Timestamp(r['spread_available_utc']) < pd.Timestamp(r['effective_utc'])


def test_december_future_volume_cannot_change_roll():
    f = pd.concat([bars('NQZ25','2025-12-15',1), bars('NQH26','2025-12-15',2)])
    r = adapter.determine_roll(f, 'NQZ25', 'NQH26', calendar(), '2025-12-15')
    future = bars('NQZ25','2025-12-16',999999)
    assert adapter.determine_roll(pd.concat([f, future]), 'NQZ25', 'NQH26', calendar(), '2025-12-15') == r


def test_december_audit_has_no_strategy_imports_or_calls():
    tree = ast.parse((ROOT/'scripts/oos_preparation/december.py').read_text())
    allowed = {'argparse', 'json', 'pathlib', 'pandas', 'adapter'}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module in allowed
        if isinstance(node, ast.Call):
            name = getattr(node.func, 'id', getattr(node.func, 'attr', ''))
            assert name not in {'hypotheses', 'simulate', 'build_features', 'trade_paths', 'metrics'}


def test_public_december_provenance_and_no_outcomes():
    d = json.loads((ROOT/'public/data/research-december-overlap.json').read_text())
    assert not d['signals_computed'] and not d['scoring_run']
    assert d['eligible_days'] is None
    assert d['protocol_sha256'] == adapter.sha(ROOT/'research/december-overlap-protocol.json')
    assert d['active_standard_clean_days'] == d['active_sessions'] == 15
    assert d['active_missing_minutes'] == d['conflicting_overlaps'] == 0
    assert not {'daily_volume', 'spread_points', 'old_volume', 'new_volume'} & set(d['roll'])
    assert len(d['sources']) == 4
    assert sum(s['rows'] for s in d['sources']) == 26051


def test_rejected_capped_download_cannot_be_ingested():
    rejected = json.loads((ROOT/'research/december-overlap-protocol.json').read_text())['rejected_download']
    assert all(name != rejected['filename'] and digest != rejected['sha256'] for _, name, digest in december.SOURCES)


def test_verify_reads_staged_raw_and_cannot_hide_tampering_behind_download(tmp_path):
    downloads = tmp_path/'downloads'
    downloads.mkdir()
    original = downloads/'nqh26_test.csv'
    original.write_text('original bytes')
    digest = adapter.sha(original)
    target = december.registered_source(tmp_path, downloads, original.name, digest, stage=True)
    assert december.registered_source(tmp_path, downloads, original.name, digest) == target
    target.write_text('tampered raw')
    with pytest.raises(ValueError, match='staged source hash mismatch'):
        december.registered_source(tmp_path, downloads, original.name, digest)
    assert original.read_text() == 'original bytes'


def test_verify_requires_raw_staging_and_never_implicitly_copies_download(tmp_path):
    original = tmp_path/'nqh26_test.csv'
    original.write_text('original bytes')
    with pytest.raises(FileNotFoundError):
        december.registered_source(tmp_path, tmp_path, original.name, adapter.sha(original))
    assert not (tmp_path/'data/raw/oos'/original.name).exists()
