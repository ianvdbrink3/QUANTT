"""Second complete source reload and verification, no research-rule changes."""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path
from scripts.edge_marathon.runner import ROOT,OUT,verify,safe_dump,discovery,history
from scripts.afternoon_inference_round import sha


def output_files():
    names=[OUT/'discovery.json',OUT/'historical.json',OUT/'historical-release.json',
        OUT/'historical-zero-loss-release.json',OUT/'historical-before-zero-loss-completion.json',
        OUT/'source-overlap-parity.json',OUT/'inventory-feasibility.json',OUT/'tom-paths.csv',OUT/'non-csv-containers.json',
        ROOT/'research/edge-marathon-results.json',ROOT/'research/edge-marathon-reference-parity.json',
        ROOT/'public/data/edge-marathon.json',ROOT/'public/reports/AUTONOMOUS_EDGE_DISCOVERY_SUMMARY.md',
        ROOT/'docs/AUTONOMOUS_EDGE_DISCOVERY_REPORT.md']
    names+=sorted(OUT.glob('*-trades.csv'))
    return names


def snapshot():return {str(p.relative_to(ROOT)):sha(p) for p in output_files()}


def checked(command):
    result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    if result.returncode:raise RuntimeError('Verification command failed: '+' '.join(command)+'\n'+result.stdout+'\n'+result.stderr)
    return result.stdout+result.stderr


def run(replay=True,build=True):
    started=datetime.now(timezone.utc).isoformat();verify();before=snapshot()
    if replay:
        from scripts.complete_marathon_zero_loss import run as completeness
        from scripts.audit_marathon_source_overlap import run as audit
        from scripts.reference_edge_marathon import run as reference
        from scripts.audit_marathon_containers import run as containers
        from scripts.report_edge_marathon import build as report
        discovery();history();completeness();audit();containers();reference();report()
        after=snapshot()
        if before!=after:
            differences=[p for p in before if before[p]!=after.get(p)]
            safe_dump(OUT/'reproduction-difference.json',dict(changed= differences,before=before,after=after))
            raise ValueError('Second source-reload not byte-identical: '+str(differences))
    else:after=before
    print('Full source-reload byte parity:',len(after),'outputs',flush=True)
    # No byte-updating registration or freeze command: verification only.
    freeze=checked([sys.executable,'-m','scripts.verify_research_freeze'])
    v2=checked([sys.executable,'-m','scripts.register_afternoon_candidate_v2','--verify'])
    window=checked([sys.executable,'-m','scripts.register_historical_replication_window','--verify'])
    tests=checked([sys.executable,'-m','pytest','-q'])
    (OUT/'pytest-output.txt').write_text(tests)
    match=re.search(r'(\d+) passed',tests)
    if not match:raise ValueError('No passed-test count in actual output')
    types=checked(['npm','run','typecheck']);(OUT/'typecheck-output.txt').write_text(types)
    built=checked(['npm','run','build']) if build else 'Not rerun in this command'
    if build:(OUT/'build-output.txt').write_text(built)
    verify()
    result=dict(status='FULL_MARATHON_VERIFICATION_PASSED',started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),
        second_complete_source_reload=replay,byte_identical_outputs=len(after),output_hashes=after,
        tests_passed=int(match.group(1)),test_output_sha256=sha(OUT/'pytest-output.txt'),
        typecheck_passed=True,production_build_passed=build,
        freeze=json.loads(freeze),candidate_v2_original_registration_verifier=json.loads(v2),
        historical_window_original_verifier=window.strip(),
        current_scope=dict(candidate_v2_specification_unmodified=True,user_authorized_new_fragment_calculations=True,
            full_fixed_end_2019_2021_test_completed=False,
            note='Legacy verifier newruns0/outcomesnotreleased strings describe preserved original registration, NOT this newly authorized fragment analysis.'),
        preserved_files=verify()['protected_prior_files'],
        independent_reference= json.loads((ROOT/'research/edge-marathon-reference-parity.json').read_text()),
        execution_limit='Same machine, same raw bytes, independent selector/fill arithmetic plus second source reload. No external independent researcher or tick fills certified.',
        dashboard_route='/research/marathon',external_publication=False,
        replay_code_hash=sha(__file__))
    safe_dump(ROOT/'research/edge-marathon-verification.json',result)
    public={k:result[k] for k in ['status','tests_passed','second_complete_source_reload','byte_identical_outputs',
        'typecheck_passed','production_build_passed','dashboard_route','external_publication','execution_limit']}
    public['reference_events']=sum(x['events'] for x in result['independent_reference']['samples'])
    safe_dump(ROOT/'public/data/edge-marathon-verification.json',public)
    print(result['status'],result['tests_passed'],'tests',len(after),'byte-identical outputs',flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--no-replay',action='store_true');p.add_argument('--no-build',action='store_true');args=p.parse_args()
    run(not args.no_replay,not args.no_build)
