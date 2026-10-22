"""Append-only revision and pure Holm decisions, never load afternoon outcomes."""
import argparse
import json

from scripts.register_afternoon_candidate import ROOT,verify as verify_v1
from scripts.oos_preparation.adapter import sha
from scripts.causal_map.core import holm

SPEC = ROOT/'research/afternoon-candidate-v2.json'
LOCK = ROOT/'research/afternoon-candidate-v2-lock.json'
CURRENT = ROOT/'research/afternoon-candidate-current.json'


def parallel_decisions(pvalues, net_means):
    if len(pvalues)!=2 or len(net_means)!=2:
        raise ValueError('Exactly two parallel primary hypotheses required')
    adjusted = holm(pvalues)
    return dict(p_holm2=adjusted,
        positive_support=[q<.05 and mean is not None and mean>0 for q,mean in zip(adjusted,net_means)])


def dump(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def specification():
    v1 = json.loads((ROOT/'research/afternoon-candidate-v1.json').read_text())
    v2 = json.loads(json.dumps(v1))
    v2.update(id='NQ-1430-FIXED-UP-1500-V2',supersedes='NQ-1430-FIXED-UP-1500-V1',
        revision='Two parallel primary horizons, no substantive horizon gate; net-point null includes fixed friction. V1 evidence preserved. No new afternoon outcome calculation.',
        v1_spec_sha256=sha(ROOT/'research/afternoon-candidate-v1.json'))
    for outcome in v2['outcomes']:
        outcome['id']='PARALLEL_PRIMARY_'+str(outcome['minutes'])+'M'
        outcome['role']='parallel_primary'
    v2['statistical_plan']=dict(
        estimand='Mean long-signed net NQ points per eligible day: C_end-O_1500-1.225. Same complete selected-day sample for both horizons.',
        null='Each of exactly two mean net-point outcomes equals zero. Two-sided p-values; positive own mean required for positive support.',
        uncertainty='Frozen afternoon_specificity.mean_influence and uncertainty on NET POINTS: daily influence calendar, Bartlett HAC lags1..5, event-day finite correction, t df=n_selected-1. CR1 SE descriptive sensitivity only.',
        multiplicity='One Holm2 family, FWER alpha0.05: first ranked raw p<0.025; if rejected, second ranked raw p<0.05. Adjusted p1=min(1,2*p1); adjusted p2=max(adjusted p1,p2). Missing test retained as p=1.',
        horizon_decision='Each horizon supported independently when its own Holm2-adjusted p<0.05 AND its own mean net points>0. No positive or significant result required from the other horizon.',
        family_decision='At least one positively supported horizon. Disjunctive parallel-primary success, NOT an intersection rule requiring both outcomes to pass. Report both in all cases.',
        descriptives='Always report gross/net points, nominal intervals, exclusions, both horizons and fixed costs. Gross log-bp descriptive only, no additional p-family. No best-horizon substitution or outcome-based extension.',
        limits='Research support under assumed friction and bar anchors, not execution certification or independent causal-mechanism proof. Two-minute refinement is post-hoc on consumed data; no absence-of-effect claim for later minutes.')
    v2['costs_and_execution'].update(test_friction_usd=24.5,test_friction_points=1.225,
        scope='Fixed friction is inside each registered net-point null. Gross/cost-only tables descriptive. Real bid/ask/latency/fills remain unverified.')
    # Avoid retaining misleading v1 keys that described costs as outside the null.
    v2['costs_and_execution'].pop('fixed_descriptive_friction_usd')
    v2['costs_and_execution'].pop('fixed_descriptive_friction_points')
    return v2


def verify():
    old = verify_v1()
    snap = json.loads(LOCK.read_text())
    for name,digest in snap['files_sha256'].items():
        if sha(ROOT/name)!=digest:
            raise ValueError('V2 lock changed: '+name)
    return dict(status=snap['status'],active_version=2,v1_preserved=True,
        new_afternoon_runs=0,protected_archive_files=old['protected_archive_files'])


def register():
    verify_v1()
    if LOCK.exists():
        return verify()
    if SPEC.exists() or CURRENT.exists():
        raise ValueError('Partial candidate revision exists; inspect before replacing')
    v2 = specification()
    dump(SPEC,v2)
    dump(CURRENT,dict(active_id=v2['id'],specification='research/afternoon-candidate-v2.json',
        sha256=sha(SPEC),prior_specification='research/afternoon-candidate-v1.json',
        independent_test_released=False))
    files=['research/afternoon-candidate-v2.json','research/afternoon-candidate-current.json',
        'docs/AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md','scripts/register_afternoon_candidate_v2.py',
        'research/afternoon-candidate-v1-lock.json','research/afternoon-candidate-v1.json',
        'scripts/afternoon_specificity.py','scripts/causal_map/core.py']
    dump(LOCK,dict(status=v2['status'],independent_test_released=False,new_afternoon_runs=0,
        files_sha256={name:sha(ROOT/name) for name in files}))
    return verify()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');args=p.parse_args()
    print(json.dumps(verify() if args.verify else register(),indent=2))
