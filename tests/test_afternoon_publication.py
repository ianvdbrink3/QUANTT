"""Public artifact contracts: no raw data, exact report, honest research status."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public/data'


def test_original_report_published_byte_identically():
    assert (ROOT / 'docs/AFTERNOON_FALSIFICATION_REPORT.md').read_bytes() == (PUBLIC / 'AFTERNOON_FALSIFICATION_REPORT.md').read_bytes()


def test_public_aggregates_preserve_all_results_and_correction():
    public = json.loads((PUBLIC / 'research-afternoon-falsification.json').read_text())
    local = json.loads((ROOT / 'research/afternoon-falsification-results.json').read_text())
    for name in ('tables', 'tests', 'concentration', 'leave_quarters', 'transitions', 'integrity'):
        assert public[name] == local[name]
    assert len(public['tests']) == 24 and len(public['tables']) == 36
    assert public['integrity']['flagged_days'] == 0
    assert public['time_audit_correction']['legacy_flagged_days'] == 435
    assert public['time_audit_correction']['statistical_tables_or_pvalues_changed'] is False


def test_public_register_has_exact_status_report_and_hash():
    register = json.loads((PUBLIC / 'research-register.json').read_text())
    entries = [r for r in register['entries'] if r['id'] == 'NQ-AFTERNOON-FALSIFICATION']
    assert len(entries) == 1
    entry = entries[0]
    assert entry['status'] == 'INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED'
    assert entry['independent_validation'] is False
    assert entry['report_sha256'] == hashlib.sha256((PUBLIC / Path(entry['report']).name).read_bytes()).hexdigest()
    assert entry['dashboard'] == '/research/nq#afternoon-falsification'


def test_public_payload_contains_no_private_arrays_or_source_paths():
    payload = (PUBLIC / 'research-afternoon-falsification.json').read_text()
    def check(value):
        if isinstance(value, dict):
            assert not set(value) & {'open', 'high', 'low', 'close', 'volume', 'measurements', 'measurements_replay', 'source_path', 'raw_bars', 'leave_days'}
            for v in value.values():
                check(v)
        elif isinstance(value, list):
            for v in value:
                check(v)
    check(json.loads(payload))
    assert '/Users/' not in payload and 'data/raw/' not in payload
    assert 'artifacts/' not in payload
    dashboard = (ROOT / 'app/research/nq/page.tsx').read_text()
    assert '<AfternoonFalsification />' in dashboard
    assert 'research-afternoon-falsification.json' in (ROOT / 'app/research/nq/AfternoonFalsification.tsx').read_text()
