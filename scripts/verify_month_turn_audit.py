"""Source-reload parity, full regression suite and local publication preparation."""
import argparse
import json
import re
import subprocess
import sys

from scripts.month_turn_audit import ROOT, OUT, RESULT, PUBLIC, REPORT, dump, verify
from scripts.oos_preparation.adapter import sha


def command(args):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError('Verification failed: '+' '.join(args)+'\n'+result.stdout+'\n'+result.stderr)
    return result.stdout+result.stderr


def files():
    return [RESULT, PUBLIC, REPORT, ROOT/'public/reports/MONTH_TURN_AUDIT.md',
            OUT/'discovery-daily.json', OUT/'continuous_2022_2024_unverified-daily.json']


def snapshot():
    return {str(p.relative_to(ROOT)):sha(p) for p in files()}


def run(build=True):
    before = snapshot()
    replay = command([sys.executable, '-m', 'scripts.month_turn_audit', 'run'])
    after = snapshot()
    if before != after:
        raise ValueError('Second full source reload is not byte-identical')
    print('Second source reload:', len(after), 'byte-identical outputs.', flush=True)
    # Publish only the explanatory document, never research manifests or private ledgers.
    context = ROOT/'docs/MONTH_TURN_UNCERTAINTY_CONTEXT.md'
    public_context = ROOT/'public/reports/MONTH_TURN_UNCERTAINTY_CONTEXT.md'
    public_context.write_text(context.read_text())
    prior = json.loads((ROOT/'research/new-candidates-round01-results.json').read_text())
    old_interval = prior['results']['TURN_OF_MONTH_RTH']['uncertainty']['mean_nominal95']
    if not (abs(old_interval[0]+.11279453256063054) < 1e-9 and abs(old_interval[1]-111.69454982247605) < 1e-9):
        raise ValueError('Earlier uncertainty context does not match preserved report')
    freeze = command([sys.executable, '-m', 'scripts.verify_research_freeze'])
    v2 = command([sys.executable, '-m', 'scripts.register_afternoon_candidate_v2', '--verify'])
    tests = command([sys.executable, '-m', 'pytest', '-q'])
    (OUT/'pytest.txt').write_text(tests)
    matched = re.search(r'(\d+) passed', tests)
    if not matched:
        raise ValueError('Actual test count missing')
    types = command(['npm', 'run', 'typecheck'])
    (OUT/'typecheck.txt').write_text(types)
    if build:
        built = command(['npm', 'run', 'build'])
        (OUT/'build.txt').write_text(built)
    protected = verify()
    result = dict(status='MONTH_TURN_AUDIT_SOURCE_REPLAY_AND_REGRESSION_PASSED',
                  tests_passed=int(matched.group(1)), source_reload_byte_identical_outputs=len(after),
                  output_sha256=after, preserved_files=len(protected['protected_files']),
                  frozen_baseline=json.loads(freeze), candidate_v2_verifier=json.loads(v2),
                  typecheck_passed=True, production_build_passed=build,
                  implementation_sha256=sha(ROOT/'scripts/month_turn_audit.py'),
                  verifier_sha256=sha(__file__), context_sha256=sha(context),
                  replay_log_sha256=sha(OUT/'discovery-daily.json'),
                  dashboard_route='/research/month-turn-audit', independent_confirmation=False,
                  new_holdout=False, purchases=False, external_publication=False,
                  limitation='Same machine and source parser; independently written daily arithmetic matches original ToM ledgers. '
                             'No external researcher, source-vintage or tick-fill certification. Local production BUILD is not Vercel deployment.')
    dump(ROOT/'research/month-turn-audit-verification.json', result)
    public = {k:result[k] for k in ('status', 'tests_passed', 'source_reload_byte_identical_outputs',
                                   'preserved_files', 'typecheck_passed', 'production_build_passed',
                                   'dashboard_route', 'independent_confirmation', 'new_holdout',
                                   'purchases', 'external_publication', 'limitation')}
    dump(ROOT/'public/data/month-turn-audit-verification.json', public)
    print(result['status'], result['tests_passed'], 'tests.', flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-build', action='store_true')
    args = parser.parse_args()
    run(not args.no_build)
