"""Lock candidate documentation only. Never load new afternoon outcomes."""
import argparse
import json
from pathlib import Path

from scripts.archive_experiments import verify_archive
from scripts.oos_preparation.adapter import sha

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT/'research/afternoon-candidate-v1-lock.json'
FILES = ['research/afternoon-candidate-v1.json', 'docs/AFTERNOON_CANDIDATE_PREREGISTRATION.md',
    'scripts/register_afternoon_candidate.py', 'scripts/afternoon_specificity.py',
    'scripts/causal_map/__main__.py', 'scripts/causal_map/core.py',
    'scripts/oos_preparation/route.py', 'scripts/reproduce_research/next_engine.py']


def verify():
    archive = verify_archive()
    recorded = json.loads(LOCK.read_text())
    for name, digest in recorded['files_sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Candidate lock changed: '+name)
    return dict(status=recorded['status'], locked_files=len(recorded['files_sha256']),
        protected_archive_files=archive['protected_files'], new_afternoon_runs=0)


def register():
    if LOCK.exists():
        return verify()
    spec = json.loads((ROOT/'research/afternoon-candidate-v1.json').read_text())
    assert [o['minutes'] for o in spec['outcomes']] == [15,2]
    assert [o['role'] for o in spec['outcomes']] == ['primary','secondary']
    assert spec['cohort']['range_atr_lower_inclusive'] == .5
    assert spec['cohort']['range_atr_upper_exclusive'] == 1.2
    verify_archive()
    lock = dict(status=spec['status'], registration_date=spec['registration_date'],
        new_afternoon_runs=0, independent_test_released=False,
        files_sha256={name:sha(ROOT/name) for name in FILES})
    LOCK.write_text(json.dumps(lock,indent=2)+'\n')
    return verify()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--verify',action='store_true')
    args = p.parse_args()
    print(json.dumps(verify() if args.verify else register(),indent=2))
