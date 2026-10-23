"""One prelocked conservative synthetic follow-up. Never reads market CSVs."""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.stats import beta, t
from scripts import afternoon_inference_round as old
from scripts.afternoon_gonogo_audit import reject

ROOT = old.ROOT
PROTOCOL = ROOT/'research/afternoon-method-round2-protocol.json'
LOCK = ROOT/'research/afternoon-method-round2-lock.json'
OUT = ROOT/'research/afternoon-method-round2-results.json'
FACTOR = 1.25


def adjusted_test(panel, mask):
    result = old.group_test(panel, mask)
    a = result['group_scores']
    se = a.std(axis=1, ddof=1)/np.sqrt(8)*np.sqrt(FACTOR)
    stat = np.divide(a.mean(axis=1), se, out=np.zeros_like(se), where=se > 0)
    result['p'] = 2*t.sf(abs(stat), 7)
    result['p'][~result['valid']] = 1
    result['p'][se <= 0] = 1
    return result


def verify():
    old.verify_lock()
    lock = json.loads(LOCK.read_text())
    for name, digest in lock['inputs'].items():
        if old.sha(ROOT/name) != digest:
            raise ValueError('Round2 input changed: '+name)
    return lock


def prepare():
    old.verify_lock()
    inputs = [PROTOCOL, Path(__file__), old.OUT, old.PROTOCOL,
              ROOT/'research/afternoon-feasibility-results.json',
              ROOT/'research/afternoon-method-round-summary.json']
    value = dict(status='LOCKED_BEFORE_FRESH_SEEDS', inputs={str(p.relative_to(ROOT)):old.sha(p) for p in inputs},
                 candidate_v2_unchanged=True, market_outcomes_released=False)
    if LOCK.exists(): verify(); return
    with LOCK.open('x') as f: f.write(json.dumps(value, indent=2)+'\n')
    print('Round2 protocol and implementation locked before fresh seeds.', flush=True)


def diagnose():
    source = json.loads(old.OUT.read_text())
    rows = []
    for row in source['null_rows']:
        for scenario, item in enumerate(row['methods']['group_score_t']):
            for scope, nkey, kkey in [('unconditional','total','rejected'), ('evaluable_only','evaluable','rejected_evaluable')]:
                if item[scope]['simultaneous_upper'] <= .06: continue
                n, k = item[nkey], item[kkey]
                lower = float(beta.ppf(.05/396, k, n-k+1)) if k else 0.
                rows.append(dict(model=row['model'], weekdays=row['weekdays'], phase=row['phase'],
                    scenario=scenario, scope=scope, n=n, k=k, rate=k/n,
                    simultaneous_lower=lower, simultaneous_upper=item[scope]['simultaneous_upper'],
                    interpretation='EVIDENCE_RATE_ABOVE_NOMINAL_5_PERCENT' if lower > .05 else 'SCREEN_FAILURE_NOT_PROOF_RATE_ABOVE_5_PERCENT'))
    return rows


def run():
    lock = verify(); p = json.loads(PROTOCOL.read_text())
    assert p['variance_multiplier'] == FACTOR
    prior = json.loads((ROOT/'research/afternoon-feasibility-results.json').read_text())
    rate = prior['selection_rate_scheduled']
    sigma = [prior['calibration'][str(h)]['iid_sigma_points'] for h in (2,15)]
    rho = prior['calibration']['paired_outcome_correlation']
    rows, negative, power = [], [], []
    for phase, seed in enumerate(p['seeds']):
        for m, model in enumerate(p['models']+[p['negative_control']]):
            for length in p['lengths']:
                rng = np.random.default_rng(seed+m*100000+length)
                counts = [old.counter() for _ in range(3)]
                scenarios = [(e,s) for e in p['power']['effects'] for s in p['power']['sigma_multipliers']]
                powers = [[old.counter(), old.counter()] for _ in scenarios]
                do_power = phase == 1 and length == 783 and model in p['power']['models']
                for off in range(0,p['replications'],100):
                    panel, mask = old.generate(rng,model,min(100,p['replications']-off),length,rate,sigma,rho)
                    for j,effect in enumerate(([0,0],[4,0],[0,4])):
                        estimate = adjusted_test(panel+mask[:,:,None]*np.array(effect),mask)
                        true = np.array(effect) == 0
                        rejected = reject(estimate['p']) & true
                        old.record(counts[j],rejected.any(axis=1),(rejected & (estimate['mean']>0)).any(axis=1),estimate['valid'])
                    if do_power:
                        for j,(effect,mult) in enumerate(scenarios):
                            values = panel*mult+mask[:,:,None]*np.array(effect)
                            for k,method in enumerate((old.group_test,adjusted_test)):
                                estimate=method(values,mask)
                                support=(reject(estimate['p']) & (estimate['mean']>0) & (np.array(effect)>0)).any(axis=1)
                                old.record(powers[j][k],support,support,estimate['valid'])
                row=dict(phase=phase+1,model=model,weekdays=length,
                         scenarios=[old.finalize_counter(c,.05/396) for c in counts])
                (negative if model==p['negative_control'] else rows).append(row)
                if do_power:
                    for (effect,mult), states in zip(scenarios,powers):
                        power.append(dict(model=model,effect=effect,sigma_multiplier=mult,
                            original=old.finalize_counter(states[0],.05),conservative=old.finalize_counter(states[1],.05)))
                print(f'Round2 seed {phase+1}: {model} / {length}',flush=True)
    bounds=[s[k]['simultaneous_upper'] for row in rows for s in row['scenarios'] for k in ('unconditional','evaluable_only')]
    passed=max(bounds)<=p['screen_max_simultaneous_upper']
    result=dict(status='CALIBRATION_SCREEN_PASSED_LIMITED_SCOPE_NOT_MARKET_VALIDATION' if passed else 'CALIBRATION_FAILED_NO_METHOD_SWITCH',
        max_simultaneous_upper=max(bounds),failed_bounds=sum(b>.06 for b in bounds),tested_bounds=len(bounds),
        synthetic_panels=p['replications']*len(p['seeds'])*(len(p['models'])+1)*len(p['lengths']),
        null_rows=rows,negative_control=negative,power=power,round1_diagnosis=diagnose(),
        inputs=lock['inputs'],raw_market_files_read=0,independent_test_released=False,candidate_v2_changed=False,
        limitation='Fixed 25% variance margin is model-motivated, not a theorem. Common-factor negative control remains outside assumptions. No guarantee under arbitrary dependence, no automatic inference-method adoption.')
    old.dump(OUT,result); verify()
    lines=['# Conservatieve methoderonde 2','',result['status'],'',
        f"{result['synthetic_panels']:,} synthetische panels; {result['failed_bounds']}/{len(bounds)} gelijktijdige bovengrenzen boven 6%; maximum {100*max(bounds):.2f}%.",'',
        'De vaste variantiefactor 1,25 is vóór de nieuwe seeds vastgelegd: SE × sqrt(1,25). Geen wijziging aan cohort, kosten, horizons, kandidaat v2 of het historische testvenster. Alpha blijft 5%; 6% blijft uitsluitend de numerieke screentolerantie. Geen marktuitkomsten gelezen.','',
        '## Diagnose ronde 1','',
        'Een overschreden Monte-Carlo-bovengrens is niet automatisch bewijs van werkelijke alpha-inflatie. Het JSON bevat per falende cel ook een simultane ondergrens: alleen boven 5% heet bewijs van inflatie. De analytische AR(0,95)-variantieverhouding (maximum 1,2029) toont daarnaast concrete restafhankelijkheid; dit is geen geschatte NQ-correlatie.','',
        '## Powerprijs bij 783 weekdagen','',
        '| Model | Netto-effect 2m/15m | SD-factor | Oude power % | Conservatieve power % |',
        '|---|---|---:|---:|---:|']
    for r in power:
        lines.append(f"| {r['model']} | {r['effect']} | {r['sigma_multiplier']} | {100*r['original']['positive_rate']:.2f} | {100*r['conservative']['positive_rate']:.2f} |")
    lines += ['', 'Dit is een beperkte synthetische schermtest, geen universele eindige-steekproefgarantie. De niet-mengende negatieve controle wordt apart zichtbaar gehouden. Ook bij een geslaagde schermtest blijft een expliciet inferentie-addendum nodig vóór een onafhankelijke markttest. De bevroren specificatie wordt niet stil aangepast.']
    (ROOT/'docs/AFTERNOON_METHOD_ROUND2_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(result['status'],result['max_simultaneous_upper'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','run','verify']);args=parser.parse_args()
    {'prepare':prepare,'run':run,'verify':verify}[args.action]()
