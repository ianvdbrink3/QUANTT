"""One locked synthetic-only method round; never imports a market scoring runner."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import lfilter
from scipy.stats import beta, t

from scripts.afternoon_gonogo_audit import reject

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'research/afternoon-method-round-protocol.json'
LOCK = ROOT/'research/afternoon-method-round-lock.json'
OUT = ROOT/'research/afternoon-method-round-results.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def partition(length, groups=8, guard=20):
    width = (length-(groups-1)*guard)//groups
    if width < 2:
        raise ValueError('Calendar too short')
    blocks = [np.arange(j*(width+guard), j*(width+guard)+width) for j in range(groups)]
    ix = np.concatenate(blocks)
    return blocks, ix, width


def group_test(panel, selected, min_group=8, min_total=120):
    panel, selected = np.asarray(panel), np.asarray(selected, dtype=bool)
    if panel.ndim != 3 or panel.shape[2] != 2 or panel.shape[:2] != selected.shape:
        raise ValueError('Expected batch x calendar x two paired horizons and common mask')
    if not np.isfinite(panel).all() or np.any(panel[~selected] != 0):
        raise ValueError('Unselected values must be influence-score zeros, not returns')
    blocks, indexes, width = partition(panel.shape[1])
    a = np.stack([panel[:, block].mean(axis=1) for block in blocks], axis=1)
    b = np.stack([selected[:, block].mean(axis=1) for block in blocks], axis=1)
    count = selected[:, indexes].sum(axis=1)
    valid = ((b*width).round().min(axis=1) >= min_group) & (count >= min_total)
    moment = a.mean(axis=1)
    se = a.std(axis=1, ddof=1)/np.sqrt(8)
    # Degenerate group variance is not a warrant for infinite significance.
    stat = np.divide(moment, se, out=np.zeros_like(moment), where=se > 0)
    p = 2*t.sf(np.abs(stat), 7)
    p[~valid] = 1
    p[se <= 0] = 1
    mean = np.divide(a.sum(axis=1), b.sum(axis=1)[:, None], out=np.zeros_like(moment), where=b.sum(axis=1)[:, None] > 0)
    return dict(p=p, mean=mean, valid=valid, count=count, group_scores=a,
                group_selection=b, scored_indexes=indexes)


def score_interval(a, b, alpha=.05):
    """Invert t on A-mu*B: bounded Fieller set or explicitly unbounded/empty."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != (8,) or b.shape != (8,):
        raise ValueError('Exactly eight fixed groups required')
    crit2 = float(t.ppf(1-alpha/2, 7)**2)
    ma, mb = a.mean(), b.mean()
    va, vb = a.var(ddof=1)/8, b.var(ddof=1)/8
    cov = float(np.cov(a, b, ddof=1)[0, 1])/8
    aa, bb, cc = mb*mb-crit2*vb, -2*ma*mb+2*crit2*cov, ma*ma-crit2*va
    disc = bb*bb-4*aa*cc
    if aa > 0 and disc >= 0:
        roots = sorted([(-bb-np.sqrt(disc))/(2*aa), (-bb+np.sqrt(disc))/(2*aa)])
        return dict(kind='BOUNDED', interval=[float(x) for x in roots], alpha=alpha)
    if aa > 0 and disc < 0:
        return dict(kind='EMPTY', interval=None, alpha=alpha)
    return dict(kind='UNBOUNDED_OR_DISJOINT', interval=None, alpha=alpha,
                quadratic=[float(aa), float(bb), float(cc)])


def hac_comparator(panel, mask, valid, indexes):
    # Keep original calendar gaps: do NOT compress the scored days together.
    keep = np.zeros(mask.shape[1], bool); keep[indexes] = True
    included = mask & keep
    values = panel*keep[None, :, None]
    n = included.sum(axis=1)
    means = values.sum(axis=1)/np.maximum(n[:, None], 1)
    scores = (values-included[:, :, None]*means[:, None])/np.maximum(n[:, None, None], 1)
    v = (scores*scores).sum(axis=1)
    for lag in range(1, 6):
        v += 2*(1-lag/6)*(scores[:, lag:]*scores[:, :-lag]).sum(axis=1)
    se = np.sqrt(np.maximum(v, 0)*n[:, None]/np.maximum(n[:, None]-1, 1))
    statistic = np.divide(means, se, out=np.zeros_like(means), where=se > 0)
    p = 2*t.sf(abs(statistic), np.maximum(n[:, None]-1, 1))
    p[~valid] = 1; p[se <= 0] = 1
    return p


def generate(rng, model, batch, length, rate, sigma, rho):
    x = rng.normal(size=(batch, length, 2))
    if model == 'T5_IID':
        x = rng.standard_t(5, size=x.shape)*np.sqrt(3/5)
    elif model in ('NEGATIVE_SKEW_IID', 'POSITIVE_SKEW_IID'):
        x = (x+6*(.02-rng.binomial(1, .02, size=x.shape)))/np.sqrt(1+36*.02*.98)
        if model.startswith('POSITIVE'):
            x = -x
    elif model.startswith('MA19'):
        extra = rng.normal(size=(batch, length+19, 2))
        x = lfilter(np.ones(20)/np.sqrt(20), [1], extra, axis=1)[:, 19:]
    elif model.startswith('AR'):
        phi = {'AR06': .6, 'AR09': .9, 'AR095': .95}[model]
        x[:, 1:] *= np.sqrt(1-phi*phi)
        x = lfilter([1], [1, -phi], x, axis=1)
    elif model == 'VOLATILITY_REGIMES':
        scales = np.resize(np.repeat([.5, 2., .8, 1.5], 50), length)
        x *= scales[None, :, None]/np.sqrt(np.mean(scales*scales))
    elif model == 'NONMIXING_COMMON_FACTOR':
        x = (x+2*rng.normal(size=(batch, 1, 2)))/np.sqrt(5)
    if 'PERSISTENT_SELECTION' in model:
        mask = np.empty((batch, length), bool)
        mask[:, 0] = rng.random(batch) < rate
        for day in range(1, length):
            probability = np.where(mask[:, day-1], .8+.2*rate, .2*rate)
            mask[:, day] = rng.random(batch) < probability
    else:
        mask = rng.random((batch, length)) < rate
    x[:, :, 1] = rho*x[:, :, 0]+np.sqrt(1-rho*rho)*x[:, :, 1]
    return x*np.asarray(sigma)*mask[:, :, None], mask


def counter():
    return dict(total=0, evaluable=0, rejected=0, positive=0, rejected_evaluable=0)


def record(state, rejected, positive, valid):
    state['total'] += len(valid)
    state['evaluable'] += int(valid.sum())
    state['rejected'] += int(rejected.sum())
    state['positive'] += int(positive.sum())
    state['rejected_evaluable'] += int((rejected & valid).sum())


def finalize_counter(state, delta):
    result = dict(state)
    for key, denominator, numerator in [('unconditional','total','rejected'), ('evaluable_only','evaluable','rejected_evaluable')]:
        n, k = state[denominator], state[numerator]
        result[key] = dict(rate=k/n if n else None,
                          simultaneous_upper=float(beta.ppf(1-delta, k+1, n-k)) if n and k < n else 1.)
    result['positive_rate'] = state['positive']/state['total']
    return result


def verify_lock():
    lock = json.loads(LOCK.read_text())
    for name, expected in lock['method_inputs'].items():
        if sha(ROOT/name) != expected:
            raise ValueError('Locked method input changed: '+name)
    for name, expected in lock['preserved_before_round'].items():
        if sha(ROOT/name) != expected:
            raise ValueError('Prior research changed: '+name)
    return lock


def prepare():
    names = subprocess.check_output(['git','ls-files','-z'], cwd=ROOT).decode().split('\0')
    tracked = {name: sha(ROOT/name) for name in names if name and (ROOT/name).is_file()}
    # Also protect the previous, intentionally local audit/intake work.
    previous = ['docs/AFTERNOON_GO_NO_GO_AUDIT.md','docs/AFTERNOON_VALIDATION_FEASIBILITY.md',
                'docs/INDEPENDENT_DATA_INVENTORY.md','docs/NQH24_INTAKE_PILOT.md',
                'research/afternoon-feasibility-results.json','research/afternoon-gonogo-audit-results.json',
                'research/nqh24-intake-pilot.json']
    tracked.update({name: sha(ROOT/name) for name in previous})
    inputs = [PROTOCOL, Path(__file__), ROOT/'research/afternoon-feasibility-results.json']
    value = dict(status='PRE_SIMULATION_METHOD_LOCK', method_inputs={str(p.relative_to(ROOT)):sha(p) for p in inputs},
                 preserved_before_round=tracked, new_outcomes_read=False, market_test_released=False)
    if LOCK.exists():
        verify_lock()
        return
    # This lock is created before either Monte Carlo seed is run.
    with LOCK.open('x') as stream:
        stream.write(json.dumps(value, indent=2)+'\n')
    print('Pre-simulation method lock written; no simulation or market file read.')


def run():
    lock = verify_lock()
    protocol = json.loads(PROTOCOL.read_text())
    prior = json.loads((ROOT/'research/afternoon-feasibility-results.json').read_text())
    rate = prior['selection_rate_scheduled']
    sigma = [prior['calibration'][str(h)]['iid_sigma_points'] for h in (2,15)]
    rho = prior['calibration']['paired_outcome_correlation']
    reps = protocol['replications_per_cell_per_seed']
    # joint + two partial nulls, two summaries, both independent Monte Carlo seeds.
    cells = len(protocol['models'])*len(protocol['lengths_weekdays'])*3*2*len(protocol['seeds'])
    delta = .05/cells
    null_rows, power_rows, negative = [], [], []
    for phase, seed in enumerate(protocol['seeds']):
        for m, model in enumerate(protocol['models']+[protocol['negative_control']]):
            for length in protocol['lengths_weekdays']:
                rng = np.random.default_rng(seed+m*100000+length)
                counts = {name: [counter() for _ in range(3)] for name in ('group_score_t','frozen_HAC5')}
                scenarios = [(a, mult) for a in protocol['power_planning']['effects_net_points'] for mult in protocol['power_planning']['sigma_multipliers']]
                do_power = phase == 1 and length == 783 and model in protocol['power_planning']['models']
                powers = [counter() for _ in scenarios]
                nsum = 0
                for off in range(0, reps, 100):
                    panel, mask = generate(rng, model, min(100,reps-off), length, rate, sigma, rho)
                    base = group_test(panel, mask)
                    nsum += int(base['count'].sum())
                    for s, effect in enumerate(([0,0],[4,0],[0,4])):
                        shifted = panel+mask[:,:,None]*np.array(effect)
                        estimate = group_test(shifted, mask)
                        ps = dict(group_score_t=estimate['p'], frozen_HAC5=hac_comparator(shifted, mask, estimate['valid'], estimate['scored_indexes']))
                        for name, p in ps.items():
                            rej = reject(p)
                            true_null = np.array(effect) == 0
                            any_null = (rej & true_null).any(axis=1)
                            positive = (rej & true_null & (estimate['mean'] > 0)).any(axis=1)
                            record(counts[name][s], any_null, positive, estimate['valid'])
                    if do_power:
                        for j, (effect, mult) in enumerate(scenarios):
                            shifted = panel*mult+mask[:,:,None]*np.array(effect)
                            estimate = group_test(shifted, mask)
                            rej = reject(estimate['p'])
                            support = (rej & (estimate['mean'] > 0)).any(axis=1)
                            record(powers[j], support, support, estimate['valid'])
                row = dict(phase=phase+1, model=model, weekdays=length, repetitions=reps,
                           scored_weekdays=len(partition(length)[1]), mean_selected=nsum/reps,
                           methods={name:[finalize_counter(x,delta) for x in states] for name,states in counts.items()})
                (negative if model == protocol['negative_control'] else null_rows).append(row)
                if do_power:
                    for (effect, mult), state in zip(scenarios,powers):
                        power_rows.append(dict(model=model, weekdays=length, sigma_multiplier=mult,
                                               effect_net_points=effect, family_positive=finalize_counter(state, .05)))
                print(f'Synthetic phase {phase+1}: {model}, {length} weekdays', flush=True)
    bounds = [item[summary]['simultaneous_upper'] for row in null_rows
              for item in row['methods']['group_score_t'] for summary in ('unconditional','evaluable_only')]
    passed = max(bounds) <= protocol['calibration_decision']['maximum_simultaneous_upper_bound']
    result = dict(status='CALIBRATION_SCREEN_PASSED_NOT_MARKET_RELEASE' if passed else 'CALIBRATION_FAILED_NO_METHOD_SWITCH',
                  calibration_passed=passed, max_simultaneous_upper=max(bounds), simultaneous_bounds=cells,
                  nominal_alpha=.05, explicit_numerical_tolerance=.06, null_rows=null_rows,
                  negative_control=negative, power_rows=power_rows, raw_market_files_read=0,
                  new_market_outcomes_read=False, candidate_v2_changed=False, independent_test_released=False,
                  historical_window=protocol['window'], inputs=lock['method_inputs'],
                  preserved_files=len(lock['preserved_before_round']),
                  limit='Finite synthetic benchmark only; dependence/normality assumptions and contamination checks remain. No universal finite-sample 5% guarantee or proof of executable profit.')
    dump(OUT,result)
    verify_lock()
    print(json.dumps({k:result[k] for k in ('status','max_simultaneous_upper','preserved_files','raw_market_files_read')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare','run','verify'])
    args = parser.parse_args()
    if args.action == 'prepare': prepare()
    elif args.action == 'run': run()
    else: verify_lock(); print('Method inputs and prior research bytes unchanged.')
