"""Append-only fixed-batch weighting audit, independent of old event/stat code."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .core import (SIDES,HORIZONS,SCHEMES,daily_statistics,estimate,weighting_decomposition,
                  enumerate_symmetric_paths,circular_weights,bootstrap,holm,zero_test,wilson,mc_p,simulated_path)
from scripts.archive_experiments import verify_archive
from scripts.oos_preparation.adapter import sha,Calendar,at
from scripts.oos_preparation.year import load_registered,forbid_scoring
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation

ROOT=Path(__file__).resolve().parents[2]
PROTOCOL=ROOT/'research/weighting-audit-protocol.json'
LOCK=ROOT/'research/weighting-audit-lock.json'
OUT=ROOT/'artifacts/weighting-audit'


def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(np.integer,np.bool_)):return x.item()
    if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
    return x


def dump(path,x):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')


def register():
    verify_archive()
    names=['research/weighting-audit-protocol.json','scripts/weighting_audit/__main__.py',
        'scripts/weighting_audit/core.py','research/raw-market-protocol.json',
        'research/raw-market-verification.json','research/market-review-verification.json',
        'research/oos-year-sources.json','research/oos-year-calendar.json','research/oos-year-rollovers.json',
        'research/holdout-protocol.json','artifacts/raw-market/events.csv','artifacts/raw-market/quality.json',
        'artifacts/raw-market/half-hours.csv','artifacts/raw-market/daily.csv']
    names += list(json.loads((ROOT/'research/market-review-verification.json').read_text())['files_sha256'])
    snapshot=dict(status='FIXED_BEFORE_NEW_ESTIMATOR_AND_SIMULATION_RESULTS',
        anchor_commit='fc888217fba8994eeecfb02273c20ca846b6fa71',
        files_sha256={p:sha(ROOT/p) for p in sorted(set(names))})
    if LOCK.exists():
        if json.loads(LOCK.read_text())!=snapshot:raise ValueError('Locked method/code/input changed')
    else:dump(LOCK,snapshot)
    return snapshot


def preflight():
    verify_archive();lock=json.loads(LOCK.read_text())
    for name,digest in lock['files_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Weighting audit locked bytes changed: '+name)
    return json.loads(PROTOCOL.read_text())


def source_arrays():
    """Independent source extraction; no raw_market.event_rows/measure imports."""
    old=json.loads((ROOT/'public/data/research-raw-market.json').read_text())
    quality=json.loads((ROOT/'artifacts/raw-market/quality.json').read_text())
    complete=[q['day'] for q in quality if q['included']]
    scheduled=[q['day'] for q in quality];indices=[scheduled.index(d) for d in complete]
    full,_,_=load_registered()
    a=json.loads((ROOT/'research/holdout-protocol.json').read_text())
    b=json.loads((ROOT/'research/oos-year-rollovers.json').read_text())
    schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
    schedule += [Activation(r['to'],r['effective_session']) for r in a['rollovers']+b['rollovers']]
    active=select_active(full,schedule);groups={d:g for d,g in active.groupby('trade_date')}
    calendar=Calendar(json.loads((ROOT/'research/oos-year-calendar.json').read_text()))
    prices={k:[] for k in ['open','high','low','close']};bounds=[];timestamps=[]
    for day in complete:
        g=groups[day];ix=pd.date_range(at(day,'09:30'),at(day,'16:00'),freq='min',inclusive='left')
        expected=calendar.grid(day);expected=expected[(expected>=ix[0])&(expected<=ix[-1])]
        raw=g.loc[(g.index>=ix[0])&(g.index<=ix[-1])]
        if not raw.index.equals(ix) or not expected.equals(ix):raise ValueError('RTH sample changed')
        boundary=at(day,'09:29')
        if boundary not in g.index:raise ValueError('Missing original boundary')
        bounds.append(float(g.at[boundary,'close']));timestamps.append(ix)
        for name in prices:prices[name].append(raw[name].to_numpy(float))
    prices={k:np.stack(v) for k,v in prices.items()};previous=np.c_[bounds,prices['close'][:,:-1]]
    shapes={k:10000*np.log(v/previous) for k,v in prices.items()}
    anchor=prices['open'][:,0,None]
    logprices={k:10000*np.log(prices[k]/anchor) for k in ['high','low','close']}
    numerator,denominator=daily_statistics(logprices['high'],logprices['low'],logprices['close'])
    # Independent record extraction versus every original record-event row.
    oldevents=pd.read_csv(ROOT/'artifacts/raw-market/events.csv')
    oldevents=oldevents[oldevents.event.isin(SIDES)].copy();new=[]
    for di,day in enumerate(complete):
        highs=prices['high'][di];lows=prices['low'][di];closes=prices['close'][di]
        known_high,known_low=highs[0],lows[0]
        for minute in range(1,390):
            labels=[]
            if highs[minute]>known_high:labels.append('RECORD_HIGH')
            if lows[minute]<known_low:labels.append('RECORD_LOW')
            known_high=max(known_high,highs[minute]);known_low=min(known_low,lows[minute])
            for label in labels:
                for horizon in HORIZONS:
                    endpoint=389 if horizon=='rth_close' else minute+int(horizon[:-1])
                    if endpoint>=390 or endpoint<=minute:continue
                    new.append(dict(day=day,event=label,horizon=horizon,bar_utc=timestamps[di][minute].isoformat(),
                        return_bps=10000*np.log(closes[endpoint]/closes[minute]),return_points=closes[endpoint]-closes[minute]))
    new=pd.DataFrame(new);keys=['day','event','horizon','bar_utc']
    left=oldevents.sort_values(keys).reset_index(drop=True);right=new.sort_values(keys).reset_index(drop=True)
    if not left[keys].equals(right[keys]):raise ValueError('Independent event identity mismatch')
    if not np.allclose(left.return_bps,right.return_bps,rtol=0,atol=1e-10):raise ValueError('Independent outcome mismatch')
    if not np.array_equal(left.return_points,right.return_points):raise ValueError('Independent point outcomes mismatch')
    theta=estimate(numerator,denominator);max_error=0.
    for r in old['events']:
        if r['event'] not in SIDES:continue
        i,j=SIDES.index(r['event']),HORIZONS.index(r['horizon'])
        for k,key in enumerate(['event_weighted_bps','equal_event_day_mean_bps']):
            error=abs(theta[i,j,k]-r[key]['mean']);max_error=max(max_error,error)
            if error>1e-8:raise ValueError('Published mean disagreement')
        if int(denominator[:,i,j,0].sum())!=r['event_weighted_bps']['n']:raise ValueError('Event count disagreement')
    if len(complete)!=435 or len(scheduled)!=454:raise ValueError('Predefined sample changed')
    independent=dict(status='PASS_INDEPENDENT_RAW_SOURCE_EVENT_REEXTRACTION',source_files=69,
        record_event_horizon_rows=len(new),complete_days=len(complete),scheduled_sessions=len(scheduled),
        max_abs_published_mean_error_bps=max_error,old_outputs_changed=False)
    return numerator,denominator,shapes,indices,independent


def null_summary(x):
    x=np.asarray(x);q=np.quantile(x,[.025,.05,.25,.5,.75,.95,.975])
    return dict(mean=float(x.mean()),sd=float(x.std(ddof=1)),mc_se_mean=float(x.std(ddof=1)/np.sqrt(len(x))),
        p025=float(q[0]),p05=float(q[1]),p25=float(q[2]),median=float(q[3]),p75=float(q[4]),p95=float(q[5]),p975=float(q[6]))


def run():
    protocol=preflight();OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'COMPLETED.json').exists():raise ValueError('Completed batch exists; use --verify, never overwrite or repeat until significant')
    print('1/5 Independent record reconstruction from69 hashed sources; strategies blocked',flush=True)
    with forbid_scoring():
        numerator,denominator,shapes,indices,independent=source_arrays()
    theta=estimate(numerator,denominator);W=circular_weights(454)
    # Preserve original454-calendar row masks; no synthetic zero returns.
    WS=W[:,indices].astype(float)
    boot=bootstrap(numerator,denominator,WS)
    previous=json.loads((ROOT/'public/data/research-raw-market.json').read_text())
    max_ci_error=0.;max_p_error=0.
    for r in previous['events']:
        if r['event'] not in SIDES:continue
        i,j=SIDES.index(r['event']),HORIZONS.index(r['horizon'])
        for k,key in enumerate(['event_weighted_bps','equal_event_day_mean_bps']):
            ci=np.quantile(boot[:,i,j,k],[.025,.975]);old=r[key]
            max_ci_error=max(max_ci_error,float(np.max(np.abs(ci-[old['mean_ci_low'],old['mean_ci_high']]))))
            max_p_error=max(max_p_error,abs(zero_test(theta[i,j,k],boot[:,i,j,k])-old['p_value']))
    if max_ci_error>1e-8 or max_p_error>1/4001+1e-12:raise ValueError('Independent bootstrap differs from prior procedure')
    independent.update(max_abs_previous_ci_error_bps=max_ci_error,max_abs_previous_p_error=max_p_error)
    real=[]
    for i,side in enumerate(SIDES):
        for j,h in enumerate(HORIZONS):
            for k,scheme in enumerate(SCHEMES):
                ci=np.quantile(boot[:,i,j,k],[.025,.975])
                real.append(dict(side=side,horizon=h,scheme=scheme,mean_bps=float(theta[i,j,k]),
                    nominal_95_mean_ci=ci.tolist(),event_days=int(denominator[:,i,j,1].sum()),
                    events=int(denominator[:,i,j,0].sum()),sum_weights=float(denominator[:,i,j,k].sum())))
    decomposition=weighting_decomposition(numerator,denominator)
    for row in decomposition:
        i,j=SIDES.index(row['side']),HORIZONS.index(row['horizon'])
        row['paired_gap_95_ci']=np.quantile(boot[:,i,j,0]-boot[:,i,j,1],[.025,.975]).tolist()
    np.savez_compressed(OUT/'real-statistics.npz',numerator=numerator,denominator=denominator)
    dump(OUT/'independent-reproduction.json',independent)
    print('2/5 Exact256-path scalar counterexample, no stochastic or market input',flush=True)
    exact=enumerate_symmetric_paths()
    variance=shapes['close']**2
    sigma=float(np.sqrt(variance.mean()));clock=np.sqrt(variance.reshape(435,13,30).mean(axis=(0,2))).repeat(30)
    scales=np.sqrt(variance.sum(axis=1)/variance.sum(axis=1).mean())
    calibration=dict(constant_minute_sigma_bps=sigma,halfhour_minute_sigma_bps=clock[::30].tolist(),
        daily_scale_quantiles=np.quantile(scales,[0,.05,.25,.5,.75,.95,1]).tolist(),
        daily_scale_second_moment=float(np.mean(scales**2)),purpose='Variance matching only; no forward-mean fit')
    experiments=protocol['simulation']['experiments_per_generator'];panels=protocol['zero_test_calibration']['panels_per_generator']
    comparisons=[];calibration_rows=[];private_files=['real-statistics.npz','independent-reproduction.json']
    print('3/5 Fixed3x4095 null panels; no interim significance inspection',flush=True)
    for scenario_index,generator in enumerate(protocol['null_generators']):
        name=generator['name'];path=OUT/(name+'.npz')
        if path.exists():
            saved=np.load(path);values=saved['estimates'];counts=saved['event_counts'];pv=saved['calibration_p'];adj=saved['calibration_holm43']
            if values.shape!=(experiments,2,3,4):raise ValueError('Incomplete checkpoint')
            print(name+': reuse completed, hash-checked below',flush=True)
            checkpoint=json.loads((OUT/(name+'.sha.json')).read_text())
            if checkpoint['sha256']!=sha(path) or checkpoint['lock_sha256']!=sha(LOCK):raise ValueError('Checkpoint mismatch')
        else:
            rng=np.random.default_rng(np.random.SeedSequence([protocol['simulation']['seed'],scenario_index]))
            values=np.empty((experiments,2,3,4));counts=np.empty((experiments,2,3))
            pv=np.empty((panels,2,3,2));adj=np.empty_like(pv)
            for rep in range(experiments):
                high,low,close=simulated_path(name,rng,shapes,sigma,clock,scales)
                num,den=daily_statistics(high,low,close);stat=estimate(num,den)
                values[rep]=stat;counts[rep]=den[:,:,:,0].sum(axis=0)
                if rep<panels:
                    # Original procedure tests two schemes only, padded to43.
                    bb=bootstrap(num[:,:,:,:2],den[:,:,:,:2],WS)
                    pp=[zero_test(stat[i,j,k],bb[:,i,j,k]) for i in range(2) for j in range(3) for k in range(2)]
                    pv[rep]=np.array(pp).reshape(2,3,2)
                    adj[rep]=np.array(holm(pp+[1.]*31)[:12]).reshape(2,3,2)
                if (rep+1)%128==0 or rep+1==experiments:print(f'{name}: {rep+1}/{experiments} complete',flush=True)
            np.savez_compressed(path,estimates=values,event_counts=counts,calibration_p=pv,calibration_holm43=adj)
            dump(OUT/(name+'.sha.json'),dict(sha256=sha(path),lock_sha256=sha(LOCK)))
        private_files += [name+'.npz',name+'.sha.json']
        for i,side in enumerate(SIDES):
            for j,h in enumerate(HORIZONS):
                for k,scheme in enumerate(SCHEMES):
                    sample=values[:,i,j,k];ns=null_summary(sample)
                    comparisons.append(dict(generator=name,side=side,horizon=h,scheme=scheme,
                        observed_bps=float(theta[i,j,k]),null=ns,observed_minus_null_median=float(theta[i,j,k]-ns['median']),
                        null_event_count=null_summary(counts[:,i,j]),**mc_p(theta[i,j,k],sample)))
                for k,scheme in enumerate(SCHEMES[:2]):
                    for adjusted,label in [(pv,'nominal'),(adj,'holm43')]:
                        successes=int((adjusted[:,i,j,k]<.05).sum())
                        calibration_rows.append(dict(generator=name,side=side,horizon=h,scheme=scheme,
                            procedure=label,panels=panels,rejections=successes,rate=successes/panels,
                            wilson_95=wilson(successes,panels)))
    print('4/5 Global72 comparison family and deterministic aggregate export',flush=True)
    if len(comparisons)!=72:raise ValueError('Family changed')
    for row,corrected in zip(comparisons,holm([r['p_value'] for r in comparisons])):row['p_holm72']=corrected
    verify_archive();preflight()
    result=dict(status='METHOD_AUDIT_NOT_TRADING_RESEARCH',protocol=protocol,protocol_sha256=sha(PROTOCOL),
        lock_sha256=sha(LOCK),independent_reproduction=independent,real_estimators=real,
        exact_enumeration=exact,weighting_decomposition=decomposition,null_calibration=calibration,
        comparisons=comparisons,zero_test_calibration=calibration_rows,
        total_null_experiments=3*experiments,total_null_days=3*experiments*435,
        private_files_sha256={n:sha(OUT/n) for n in private_files},
        new_strategy_signals=0,entries_stops_targets_used=False,old_archive_files_unchanged=115,
        runtime=dict(python=sys.version.split()[0],numpy=np.__version__,pandas=pd.__version__),
        interpretation='A nonzero ex-post day-weighted mean is not equivalent to predictable future returns. Simulation tail checks are model-dependent and not an independent validation.')
    dump(OUT/'summary.json',result);dump(ROOT/'public/data/research-weighting-audit.json',result)
    dump(OUT/'COMPLETED.json',dict(summary_sha256=sha(OUT/'summary.json'),lock_sha256=sha(LOCK)))
    dump(ROOT/'research/weighting-audit-verification.json',dict(result_sha256=sha(OUT/'summary.json'),
        lock_sha256=sha(LOCK),private_files_sha256=result['private_files_sha256'],old_outputs_unchanged=True))
    print('5/5 Complete; all fixed panels retained, no strategy or selected rescue',flush=True)


def verify_completed():
    preflight();manifest=json.loads((ROOT/'research/weighting-audit-verification.json').read_text())
    for name,digest in manifest['private_files_sha256'].items():
        if sha(OUT/name)!=digest:raise ValueError('Simulation evidence changed: '+name)
    for p in [OUT/'summary.json',ROOT/'public/data/research-weighting-audit.json']:
        if sha(p)!=manifest['result_sha256']:raise ValueError('Aggregate changed')
    return dict(status='PASS_ARCHIVE_METHOD_INPUTS_AND_FIXED_BATCH_HASHES',simulation_experiments=12285,new_strategy_runs=0)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--register',action='store_true');parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.register:register();print('Method, code and inputs locked; no statistics yet.')
    elif args.verify:print(json.dumps(verify_completed(),indent=2))
    else:run()
