"""Prelocked finite scan, then one separately released historical replication."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.afternoon_inference_round import sha,dump,verify_lock
from scripts.causal_map.__main__ import clean
from .core import catalog,select,fill
from .features import enrich
from .stats import metrics,inference,holm,quantiles
from .data import inventory,verify_source_register,historical_samples

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/edge-marathon'
PROTOCOL=ROOT/'research/edge-marathon-protocol.json'
LOCK=ROOT/'research/edge-marathon-lock.json'
RESULT=ROOT/'research/edge-marathon-results.json'


def safe_dump(path,obj):dump(path,clean(obj))


def prepare():
    verify_lock()
    if LOCK.exists():verify();return
    OUT.mkdir(parents=True,exist_ok=True)
    register=inventory();safe_dump(OUT/'source-register.json',register)
    names=[PROTOCOL,OUT/'source-register.json']+sorted((ROOT/'scripts/edge_marathon').glob('*.py'))
    names += [ROOT/'research/oos-year-sources.json',ROOT/'research/oos-year-rollovers.json',ROOT/'research/oos-year-calendar.json',
              ROOT/'research/afternoon-candidate-v2.json',ROOT/'research/afternoon-method-round2-protocol.json',
              ROOT/'artifacts/raw-market/quality.json']
    value=dict(status='LOCKED_BEFORE_MARATHON_OUTCOMES',created_utc=datetime.now(timezone.utc).isoformat(),
        input_hashes={str(p.relative_to(ROOT)):sha(p) for p in names},
        models=catalog(),user_release='All5phases including fragment outcome access, no purchases/downloads/externalpublication',
        protected_prior_files=len(json.loads((ROOT/'research/afternoon-method-round-lock.json').read_text())['preserved_before_round']))
    with LOCK.open('x') as f:f.write(json.dumps(value,indent=2)+'\n')
    print('LOCKED',len(catalog()),'outcomes;',register['scanned_paths'],'paths;',register['unique_contents'],'contents',flush=True)


def verify():
    verify_lock()
    lock=json.loads(LOCK.read_text())
    for name,digest in lock['input_hashes'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Marathon implementation/protocol changed: '+name)
    return lock


def collect(state,included,name):
    rows=[];excluded=[];prefix_checks=0;mutation_checks=0
    for day in included:
        prices,original=state[day];ctx=dict(original)
        if name=='DISCOVERY' and day<'2025-01-01':ctx['tom']=False
        events=select(prices,ctx)
        # Required causal truncation + mutation tests on every source/day.
        for boundary in [1,5,30,60,120,150,240,300,330,345,385]:
            prefix={k:v[:boundary] for k,v in prices.items()}
            expected=[e for e in events if e['decision']<=boundary]
            actual=select(prefix,ctx)
            if expected!=actual:raise ValueError(f'Future truncation dependency {name} {day} {boundary}')
            prefix_checks+=1
            mutated={k:v.copy() for k,v in prices.items()}
            for k in ('open','high','low','close'):
                mutated[k][boundary:]+=100000.
            actual=[e for e in select(mutated,ctx) if e['decision']<=boundary]
            if expected!=actual:raise ValueError(f'Future mutation dependency {name} {day} {boundary}')
            mutation_checks+=1
        for event in events:
            try:
                row=fill(event,prices,ctx)
            except ValueError as exc:
                excluded.append(dict(day=day,model=event['model'],reason=str(exc)));continue
            row.update(day=day,source_sample=name,tom_position=ctx.get('tom_position'))
            rows.append(row)
    return rows,dict(prefix_truncation_checks=prefix_checks,future_mutation_checks=mutation_checks,
        technical_exclusions=excluded)


def benchmark(trades,state,included):
    if not trades:return dict(unconditional_same_clock_mean=None,mean_premium=None,matched_blind_long_mean=None)
    cache={};base=[];matched=[]
    for r in trades:
        key=(r['entry'],r['end'])
        if key not in cache:
            gross=[]
            for day in included:
                prices,ctx=state[day]
                event=dict(model='BENCHMARK',decision=max(key[0],0),entry=key[0],end=key[1],direction=1)
                try:g=fill(event,prices,ctx)['gross_points']
                except ValueError:continue
                gross.append(g)
            cache[key]=float(np.mean(gross)) if gross else np.nan
        base.append(r['direction']*cache[key]-1.225)
        matched.append(r['direction']*r['gross_points']-1.225)
    average=float(np.mean(base))
    return dict(unconditional_same_clock_mean=average,mean_premium=float(np.mean([r['net_points'] for r in trades])-average),
        matched_blind_long_mean=float(np.mean(matched)),
        limitation='Descriptive same-clock directional benchmark on all complete sample days, not an independent causal control or new p-test')


def scored(rows,calendar,state,included):
    result={}
    for j,name in enumerate(catalog()):
        trades=[r for r in rows if r['model']==name]
        m=metrics(trades,calendar);stat=inference(trades,calendar,seed=20261022061+j)
        result[name]=dict(metrics=m,inference=stat,benchmark=benchmark(trades,state,included))
    sf=holm([result[n]['inference']['signflip_p'] for n in catalog()])
    group=holm([result[n]['inference']['conservative_p'] for n in catalog()])
    for name,p,q in zip(catalog(),sf,group):
        r=result[name];r['inference'].update(signflip_holm25=p,conservative_holm25=q)
        m=r['metrics'];ci=r['inference']['bootstrap95']
        good=bool(m['net_points']>0 and (m.get('profit_factor') or 0)>1.3 and (m.get('positive_quarter_fraction') or 0)>=.7
            and m['quarters']>=4 and ci is not None and ci[0]>0 and p<.05)
        risk=bool(m['net_points']>0 and (m.get('drawdown') or 0)<=.5*m['net_points']
            and (m.get('top3_share_of_net') or 1)<=.5 and m.get('net_without_top3',0)>0
            and m.get('leave_one_quarter_out_mean') and m['leave_one_quarter_out_mean'][0]>0
            and m.get('slippage') and m['slippage'][-1]['net_points']>0)
        r.update(discovery_statistical_screen=good,operational_risk_screen=risk,
            serious_discovery_candidate=good and risk,
            status='EXPLORATORY_SCREEN_SUPPORTED_NOT_VALIDATED' if good and risk else 'NOT_ALL_PREREGISTERED_SCREENS_PASSED')
    return result


def path_anatomy(state,rows):
    days=[r['day'] for r in rows if r['model']=='TOM_RTH'];out=[]
    for day in days:
        p,c=state[day];opening=p['open'][0]
        row=dict(day=day,position=c['tom_position'],rth_points=float(p['close'][389]-opening),
            overnight_points=float(c['on_close']-c['overnight_open']) if c['overnight_complete'] else None,
            opening_gap=float(opening-c['on_close']) if c['overnight_complete'] else None,
            morning=float(p['close'][89]-opening),midday=float(p['close'][269]-p['open'][90]),
            afternoon=float(p['close'][389]-p['open'][270]),
            bridge1100=float(p['open'][90]-p['close'][89]),bridge1400=float(p['open'][270]-p['close'][269]))
        if abs(row['rth_points']-sum(row[k] for k in ['morning','midday','afternoon','bridge1100','bridge1400']))>1e-8:
            raise ValueError('Path components do not reconcile')
        out.append(row)
    aggregate={}
    for label,group in [('ALL',out)]+[(x,[r for r in out if r['position']==x]) for x in ['T-1','T+1','T+2','T+3']]:
        aggregate[label]={}
        for field in ['overnight_points','opening_gap','morning','midday','afternoon','bridge1100','bridge1400','rth_points']:
            values=[r[field] for r in group if r[field] is not None]
            aggregate[label][field]=dict(days=len(values),mean=float(np.mean(values)) if values else None,distribution=quantiles(values))
    worst=sorted(out,key=lambda r:r['rth_points'])[:5]
    return out,dict(groups=aggregate,worst5_days=worst)


def cap_control(state,included,rows):
    comparable=[d for d in included if state[d][1].get('tom') and np.isfinite(state[d][1].get('atr_p90',np.nan)) and d>='2025-01-01']
    baseline=[r for r in rows if r['model']=='TOM_RTH' and r['day'] in comparable]
    cap=[r for r in rows if r['model']=='TOM_ATR_CAP']
    return dict(comparable_known_history_days=len(comparable),matched_baseline=metrics(baseline,included),cap=metrics(cap,included),
        missing60history_tom_dates=[d for d in included if state[d][1].get('tom') and d>='2025-01-01' and not np.isfinite(state[d][1].get('atr_p90',np.nan))])


def frozen_v2_hac(rows,days):
    from scripts.afternoon_specificity import mean_influence,uncertainty
    output=[]
    for h in [2,15]:
        r=[x for x in rows if x['model']==f'AFTERNOON_V2_{h}']
        if len(r)<2:output.append(dict(horizon=h,n=len(r),p_raw=1.,status='DATA_INSUFFICIENT'));continue
        frame=pd.DataFrame([dict(day=x['day'],points=x['net_points']) for x in r])
        mean,scores=mean_influence(frame,days,'points')
        u=uncertainty(mean,scores,len(r),len(r)-1)
        output.append(dict(horizon=h,n=len(r),status='FROZEN_HAC5_FRAGMENT_ONLY',**u))
    for r,p in zip(output,holm([x['p_raw'] for x in output])):r['p_holm2']=p
    return output


def discovery():
    verify();verify_source_register()
    from scripts.causal_map.__main__ import load_inputs
    state,days,included,source,active,cal,rolls=load_inputs()
    state=enrich(state,days,active,rolls)
    rows,checks=collect(state,included,'DISCOVERY')
    calendar=list(pd.bdate_range('2024-12-30','2026-09-30').strftime('%Y-%m-%d'))
    result=scored(rows,calendar,state,included)
    paths,anatomy=path_anatomy(state,rows)
    if result['TOM_RTH']['metrics']['trades']!=81:raise ValueError('Baseline81ToM days changed')
    if abs(result['TOM_RTH']['metrics']['net_points']-4364.025)>1e-7:raise ValueError('ToM baseline parity failed')
    for h in [2,15]:
        if result[f'AFTERNOON_V2_{h}']['metrics']['trades']!=162:raise ValueError('Frozen162cohort parity failed')
    by_variant=[n for n in ['TOM_TREND_1000','TOM_OVERNIGHT_1030','TOM_ATR_CAP']
        if result[n]['metrics']['net_points']>0 and (result[n]['metrics'].get('profit_factor') or 0)>1.3]
    best=sorted(by_variant,key=lambda n:(-result[n]['metrics']['profit_factor'],-result[n]['metrics']['mean_net'],n))[0] if by_variant else None
    selected=['AFTERNOON_V2_2','AFTERNOON_V2_15','TOM_RTH']+([best] if best else [])
    for n,r in result.items():
        if not n.startswith('TOM_') and r['metrics']['net_points']>0 and (r['metrics'].get('profit_factor') or 0)>1.3:selected.append(n)
    selected=sorted(set(selected))
    pd.DataFrame(rows).to_csv(OUT/'discovery-trades.csv',index=False,float_format='%.10f')
    pd.DataFrame(paths).to_csv(OUT/'tom-paths.csv',index=False,float_format='%.10f')
    value=dict(status='BOUNDED_DISCOVERY_COMPLETE_NOT_VALIDATION',models=result,checks=checks,complete_days=len(included),
        family_size=25,calendar_positions=len(calendar),source_files=source['source_files'],anatomy=anatomy,
        cap_comparable_control=cap_control(state,included,rows),historical_selection=selected,best_tom_variant=best,
        frozen_v2_replay=frozen_v2_hac(rows,days),all_rows=len(rows),protocol_sha256=sha(PROTOCOL))
    safe_dump(OUT/'discovery.json',value)
    release=dict(status='HISTORICAL_SELECTION_LOCKED_BEFORE_NEW_FRAGMENT_OUTCOMES',
        selected=selected,best_tom_variant=best,discovery_sha256=sha(OUT/'discovery.json'),
        protocol_sha256=sha(PROTOCOL),source_register_sha256=sha(OUT/'source-register.json'))
    release_path=OUT/'historical-release.json'
    if release_path.exists() and json.loads(release_path.read_text())!=release:raise ValueError('Historical selection changed')
    safe_dump(release_path,release)
    print('Discovery complete; historical selection locked:',selected,flush=True)
    return value


def history():
    verify();release=json.loads((OUT/'historical-release.json').read_text())
    if sha(OUT/'discovery.json')!=release['discovery_sha256']:raise ValueError('Discovery changed after selection')
    selected=set(release['selected']);samples,classification=historical_samples();results={}
    for sample in samples:
        name=sample['name'];state=sample['state'];included=sample['included'];days=sample['days']
        if state is None or not included:
            results[name]=dict(exposure=sample['exposure'],source_certified=False,quality=sample['quality'],status='NO_ELIGIBLE_SESSIONS');continue
        # Selectors are computed, but no outcome is evaluated for models that
        # did not pass the prespecified historical-release selection.
        subset={d:state[d] for d in state}
        # collect() tests selector causality on all days; fill selected only.
        rows=[];checks=0
        for day in included:
            prices,ctx=subset[day];events=[e for e in select(prices,ctx) if e['model'] in selected]
            for boundary in [5,30,60,240,300,330,385]:
                actual=[e for e in select({k:v[:boundary] for k,v in prices.items()},ctx) if e['model'] in selected]
                if actual!=[e for e in events if e['decision']<=boundary]:raise ValueError('Historical future dependency')
                checks+=1
            for event in events:
                try:r=fill(event,prices,ctx)
                except ValueError:continue
                r.update(day=day,source_sample=name,tom_position=ctx.get('tom_position'));rows.append(r)
        calendar=list(pd.bdate_range(days[0],days[-1]).strftime('%Y-%m-%d'))
        scores=scored(rows,calendar,subset,included)
        pd.DataFrame(rows).to_csv(OUT/(name.lower()+'-trades.csv'),index=False,float_format='%.10f')
        results[name]=dict(status='SEPARATE_FRAGMENT_OR_UNVERIFIED_SOURCE_REPLICATION_NOT_VALIDATED',
            exposure=sample['exposure'],source_certified=False,complete_days=len(included),period=[days[0],days[-1]],
            quality=sample['quality'],models=scores,selected_model_ids=sorted(selected),prefix_checks=checks,
            frozen_v2_original_inference=frozen_v2_hac(rows,days))
        print('Historical source finished:',name,'complete days',len(included),'selected trades',len(rows),flush=True)
    # Looking across several source samples incurs another family. Do not
    # select the most flattering sample-specific Holm25 result as validation.
    pairs=[(sample,n) for sample,r in results.items() if 'models' in r for n in catalog()]
    adjusted=holm([results[s]['models'][n]['inference']['signflip_p'] for s,n in pairs])
    for (s,n),p in zip(pairs,adjusted):results[s]['models'][n]['inference']['signflip_holm_all_historical_sources']=p
    value=dict(status='HISTORICAL_FRAGMENT_SCAN_COMPLETE_NO_CERTIFIED_INDEPENDENT_PROMOTION',
        samples=results,source_classification=classification,selection=release,historical_family_size=len(pairs),
        warning='Overlapping dates across source vendors are NOT independent replications and are never pooled. Static revised continuous-vintage data cannot certify historical publication-time causality. Eight January2019days do not complete the locked2019-2021test.')
    safe_dump(OUT/'historical.json',value)
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','verify','discovery','history']);args=p.parse_args()
    {'prepare':prepare,'verify':verify,'discovery':discovery,'history':history}[args.action]()
