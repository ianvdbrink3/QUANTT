import json
from pathlib import Path

import pytest

from scripts.verify_research_freeze import verify, ROOT


def test_frozen_bytes_match():
    assert verify()['eligible_days'] == 159


def test_changed_frozen_file_rejected(tmp_path):
    (tmp_path/'research').mkdir()
    (tmp_path/'research/vnext-freeze-manifest.json').write_text(json.dumps({
        'files_sha256': {'engine.py': '0'*64}}))
    (tmp_path/'engine.py').write_text('changed')
    with pytest.raises(ValueError, match='engine.py'):
        verify(tmp_path)


def test_missing_frozen_file_rejected(tmp_path):
    (tmp_path/'research').mkdir()
    (tmp_path/'research/vnext-freeze-manifest.json').write_text(json.dumps({
        'files_sha256': {'missing.py': '0'*64}}))
    with pytest.raises(ValueError, match='missing.py'):
        verify(tmp_path)


def test_future_protocol_has_single_primary_and_no_scoring():
    p = json.loads((ROOT/'research/vnext-future-oos-protocol.json').read_text())
    assert p['primary_strategy'] == 'B_ORB15'
    assert p['status'] == 'LOCKED_RULES_NOT_RUN'
    assert p['cost_rt_usd'] == 24.5
    assert p['pass_rule']['minimum_eligible_days'] == 20
    assert p['inference']['confirmatory_hypotheses'] == 1
    assert p['test_period'] == ['2025-10-01', '2026-09-30']
    public = json.loads((ROOT/'public/data/research-freeze.json').read_text())
    assert public['protocol'] == p
    assert public['historical_tests'] == 207 and public['release_tests'] == 211
    assert public['inventory']['mode'] == 'TIMESTAMPS_ONLY_NO_BACKTEST'
