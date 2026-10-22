import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public/data'


def load(path):
    return json.loads(path.read_text())


def test_public_reports_are_exact_frozen_copies():
    for name in ('AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md', 'MORNING_RECOVERY_ANATOMY.md', 'MORNING_RECOVERY_PRECISION.md'):
        assert (PUBLIC / name).read_bytes() == (ROOT / 'docs' / name).read_bytes()


def test_only_v2_is_a_formal_candidate():
    registry = load(PUBLIC / 'research-register.json')
    assert registry['active_formal_candidate_ids'] == ['NQ-1430-FIXED-UP-1500-V2']
    formal = [r['id'] for r in registry['entries'] if r.get('formal_candidate')]
    assert formal == registry['active_formal_candidate_ids']
    assert registry['future_independent_test_released'] is False


def test_morning_is_closed_without_validation_claim():
    entries = load(PUBLIC / 'research-register.json')['entries']
    morning = [r for r in entries if r['id'].startswith('NQ-MORNING-')]
    assert len(morning) == 2
    assert all(r['status'] == 'CLOSED_DESCRIPTIVE_NOT_CANDIDATE' and not r['independent_validation'] for r in morning)


def test_public_aggregates_preserve_original_results():
    pairs = [('research-afternoon-candidate-v2.json', 'afternoon-candidate-v2.json'), ('research-morning-anatomy.json', 'morning-recovery-anatomy-results.json'), ('research-morning-precision.json', 'morning-recovery-precision-results.json')]
    for public, private in pairs:
        assert (PUBLIC / public).read_bytes() == (ROOT / 'research' / private).read_bytes()


def test_publication_hashes_and_no_additional_analysis():
    manifest = load(ROOT / 'research/research-round-publication.json')
    assert len(manifest['files_sha256']) == 14
    for path, digest in manifest['files_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    assert manifest['new_afternoon_runs'] == manifest['new_strategy_runs'] == 0
    assert manifest['raw_data_published'] is False


def test_new_public_json_has_no_private_records():
    forbidden = {'bars', 'raw_bars', 'measurements', 'source_rows', 'raw_data', 'open', 'high', 'low', 'close', 'volume', 'ticks'}
    def check(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values():
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)
    for name in ('research-afternoon-candidate-v2.json', 'research-morning-anatomy.json', 'research-morning-precision.json', 'research-round-closure.json'):
        check(load(PUBLIC / name))
