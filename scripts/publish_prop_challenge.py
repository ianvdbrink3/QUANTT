"""Public aggregates with explicit failure causes and billing sensitivities."""
import csv
import json
from scripts.prop_challenge import __main__ as run
from scripts.prop_challenge.read_outcomes import read

MEASURES=['starts','passed','failed','unknown','unfinished','pass_rate','pass_upper_source_unknown','fail_rate',
 'mean_trades','mean_days_to_pass','mean_days_to_fail','mean_attempt_fee_USD','mean_calendar_billed_fee_USD',
 'cost_per_pass_proxy_USD','cost_per_pass_resolved_paths_USD','cost_reset49_USD','cost_reset99_USD',
 'mean_contracts_per_trade','mean_rejected_overlap','mean_rejected_sizing','nonoverlap_starts','nonoverlap_pass_rate',
 'omitted_right_edge_starts']


def full_rows(result):
    for r in run.ranking(result['results']):
        for era in ('2019_2021','2024_2026','COMBINED'):
            stats=dict(r['combined'] if era=='COMBINED' else r['eras'][era])
            if era=='COMBINED':
                for key in ('mean_attempt_fee_USD','mean_calendar_billed_fee_USD','mean_rejected_overlap','mean_rejected_sizing'):
                    stats[key]=sum(e[key]*e['starts'] for e in r['eras'].values())/stats['starts']
                if r['firm']=='TOPSTEP':
                    stats['cost_reset49_USD']=stats['cost_per_pass_proxy_USD']
                    base=stats['cost_per_pass_proxy_USD']
                    stats['cost_reset99_USD']=None if base is None else base+50*stats['failed']/stats['passed']
            causes=stats.get('outcomes')
            if causes is None:
                causes={name:sum(e['outcomes'][name] for e in r['eras'].values()) for name in run.c.LABELS}
            yield dict(firm=r['firm'],horizon=r['horizon'],combination=r['combination'],sizing=r['sizing'],period=era,
                healthy_both_eras_screen=r['healthy_both_eras_screen'],cost_eligible=r['cost_eligible'],
                **{key:stats.get(key) for key in MEASURES},**{f'outcome_{key}':value for key,value in causes.items()})


def publish():
    run.publish()
    x=json.loads(run.RESULT.read_text());path=run.ROOT/'public/reports/PROP_CHALLENGE_FULL_RANKING.csv'
    rows=full_rows(x);first=next(rows)
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(first),lineterminator='\n');writer.writeheader();writer.writerow(first);writer.writerows(rows)
    target=run.ROOT/'public/reports/PROP_CHALLENGE_REPRODUCTION.md'
    target.write_bytes((run.ROOT/'docs/PROP_CHALLENGE_REPRODUCTION.md').read_bytes())
    # Equal starts across horizons: same earliest N-62 cohorts in EACH era.
    # This is a denominator check, not a new strategy or parameter family.
    common={}
    for header,a in read(run.OUT/'run1/rolling-outcomes.bin.gz'):
        combination,sizing,firm,era,horizon,_=header
        count=x['calendar'][era]['sessions']-62
        states=a['state'][:count]
        common[(combination,sizing,firm,era,horizon)]=dict(starts=count,
            passed=int((states==run.c.PASS).sum()),failed=int(((states>=run.c.FLOOR_OBSERVED)&(states<=run.c.INACTIVE)).sum()),
            unknown=int((states==run.c.UNKNOWN).sum()))
    comparison=run.ROOT/'public/reports/PROP_CHALLENGE_COMMON_STARTS.csv'
    with comparison.open('w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['combination','sizing','firm','era','horizon','same_starts','passed','failed','source_unknown','pass_rate'])
        for key,value in common.items():
            writer.writerow([*key,value['starts'],value['passed'],value['failed'],value['unknown'],value['passed']/value['starts']])
    conclusion={}
    for firm in run.FIRMS:
        rows=[r for r in x['results'] if r['firm']==firm['id'] and r['horizon']==21]
        best=max(rows,key=lambda r:r['combined']['pass_rate'])
        resolved=[r for r in rows if r['cost_eligible']]
        cheap=min(resolved,key=lambda r:r['combined']['cost_per_pass_proxy_USD']) if resolved else None
        conclusion[firm['id']]=dict(two_era_10pct_screen_count=sum(r['healthy_both_eras_screen'] for r in rows),
            best_combined=dict(combination=best['combination'],sizing=best['sizing'],combined=best['combined'],eras=best['eras']),
            lowest_resolved_cost=None if cheap is None else dict(combination=cheap['combination'],sizing=cheap['sizing'],combined=cheap['combined'],eras=cheap['eras']))
    regpath=run.ROOT/'public/data/prop-challenge/register.json';register=json.loads(regpath.read_text())
    register['conclusion']=conclusion;run.dump(regpath,register)
    proof=run.ROOT/'research/prop-challenge-publication.json';p=json.loads(proof.read_text())
    p['files'][str(path.relative_to(run.ROOT))]=run.digest(path)
    p['files'][str(target.relative_to(run.ROOT))]=run.digest(target)
    p['files'][str(regpath.relative_to(run.ROOT))]=run.digest(regpath)
    p['files'][str(comparison.relative_to(run.ROOT))]=run.digest(comparison)
    p['supplementary_export']='Three period rows per cell; outcomes, calendar billing, reset49/99 and nonoverlap diagnostics. Combined sums, not an account spanning the data gap.'
    run.dump(proof,p)
    return dict(status='PUBLIC_AGGREGATES_READY',ranking_rows=len(x['results'])*3,private_data_included=False)


if __name__=='__main__':print(json.dumps(publish(),indent=2))
