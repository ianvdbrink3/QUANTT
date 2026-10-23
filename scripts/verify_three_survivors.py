"""Source reload parity and frozen archive checks; no new holdout execution."""
import json
import re
import subprocess
import sys
from scripts.survivor_portfolio import ROOT,RESULT,verify,dump,MODELS
from scripts.oos_preparation.adapter import sha


def command(args):
    x=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if x.returncode:raise RuntimeError('Check failed: '+' '.join(args)+'\n'+x.stdout+'\n'+x.stderr)
    return x.stdout+x.stderr


def outputs():
    paths=[RESULT,ROOT/'public/data/three-survivors.json',ROOT/'docs/THREE_SURVIVORS_ATR_PORTFOLIO.md',ROOT/'public/reports/THREE_SURVIVORS_ATR_PORTFOLIO.md']
    paths+=sorted((ROOT/'artifacts/three-survivors').glob('*-daily.json'))
    paths+=sorted((ROOT/'artifacts/three-survivors').glob('*-trades.json'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def run():
    before=outputs();command([sys.executable,'-m','scripts.survivor_portfolio','run'])
    if outputs()!=before:raise ValueError('Second source replay not byte-identical')
    lock=verify()
    command([sys.executable,'-m','scripts.verify_research_freeze'])
    command([sys.executable,'-m','scripts.register_afternoon_candidate_v2','--verify'])
    command([sys.executable,'-c','from scripts.month_turn_audit import verify; verify()'])
    tests=command([sys.executable,'-m','pytest','-q'])
    count=int(re.search(r'(\d+) passed',tests)[1])
    out=ROOT/'artifacts/three-survivors'
    (out/'tests.txt').write_text(tests)
    types=command(['npm','run','typecheck']);(out/'typecheck.txt').write_text(types)
    build=command(['npm','run','build']);(out/'build.txt').write_text(build)
    document=ROOT/'docs/THREE_SURVIVORS_PREREGISTRATION_2019_2021.md'
    public_document=ROOT/'public/reports/THREE_SURVIVORS_PREREGISTRATION_2019_2021.md'
    public_document.write_text(document.read_text())
    prereg=dict(status='REGISTERED_NOT_RELEASED',specification_sha256=sha(document),
        models=list(MODELS)+['PORTFOLIO_EQUAL_THIRD'],full_descriptive_window=['2019-01-02','2021-12-31'],
        previously_inspected_dates=['2019-01-02','2019-01-03','2019-01-04','2019-01-07','2019-01-08','2019-01-09','2019-01-10','2019-01-11'],
        new_outcome_test_window=['2019-01-14','2021-12-31'],warmup_start='2018-11-19',
        source_code_sha256={p:sha(ROOT/p) for p in ('scripts/edge_marathon/core.py','scripts/edge_marathon/features.py','scripts/survivor_portfolio.py')},
        tests='4two-sided co-primary dailymean netATR tests,Holm4; jointHolm6 if oldv2twohorizons share this remainder.',
        information_floor=dict(usable_months=24,ATR_ready_trades_each_signal=30),
        fixed_end='2021-12-31',interim_outcomes=False,release=False,
        blockers=['full numeric data quality','CME holiday/halt/expiry reconciliation','new calendar adapter parity','locked causal volume rolls','complete source manifest','explicit outcome release'])
    dump(ROOT/'research/three-survivors-preregistration-2019-2021.json',prereg)
    dump(ROOT/'public/data/three-survivors-preregistration.json',prereg)
    result=dict(status='SOURCE_REPLAY_FROZEN_REGRESSION_AND_BUILD_PASSED',tests_passed=count,
        byte_identical_outputs=len(before),output_sha256=before,prior_files_unchanged=len(lock['protected_files']),
        protocol_sha256=sha(ROOT/'research/three-survivors-protocol.json'),
        future_specification_sha256=sha(document),future_holdout_executed=False,
        new_historical_numeric_OHLCV_read=False,external_publication=False,
        provisional_MNQ_cost_USD=6.5,actual_broker_cost_known=False,typecheck=True,build=True,
        dashboard_route='/research/three-survivors')
    dump(ROOT/'research/three-survivors-verification.json',result)
    dump(ROOT/'public/data/three-survivors-verification.json',{k:v for k,v in result.items() if k!='output_sha256'})
    verify();print(json.dumps(result,indent=2));return result


if __name__=='__main__':run()
