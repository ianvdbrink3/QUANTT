"""Fixed falsification of the already observed15:00 pattern. No strategy calls."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.afternoon_specificity import WINDOWS,context_at,mean_influence,uncertainty
from scripts.causal_map.__main__ import ROOT,clean,load_inputs
from scripts.causal_map.core import holm
from scripts.oos_preparation.adapter import sha,at
from scripts.oos_preparation.year import forbid_scoring
from scripts.archive_experiments import verify_archive

OUT=ROOT/'artifacts/afternoon-falsification'
PROTOCOL=ROOT/'research/afternoon-falsification-protocol.json'
LOCK=ROOT/'research/afternoon-falsification-lock.json'


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(clean(obj),indent=2,allow_nan=False)+'\n')


def register():
    verify_archive()
    spec=dict(status='FIXED_FALSIFICATION_ON_CONSUMED_DATA_NOT_VALIDATION',
        universe='Exactly435 frozen complete RTH days, same sources, active schedule and prior ATR14 as causal-map and specificity comparison.',
        fixed_cohort='UP/DOWN at boundary14:30, determined only by14:29close relative09:30open and completed RTH range/knownATR14 in[0.5,1.2). Hold membership unchanged across all3 quarters.',
        dynamic_cohort='Same criteria independently at14:30,14:45,15:00. No retrospective15:00-membership selection for earlier quarters.',
        windows=WINDOWS,
        parts=dict(FULL='close minute k-1 to close k+14, same original benchmark anchor',
            FIRST='open minute k to close minute k: actual first completed minute',
            REST='open minute k+1 to close k+14: remaining14 minutes',
            GAPS='FULL=priorclose-to-open gap+FIRST+firstclose-to-nextopen gap+REST in points. Median components need not add.'),
        orientation='UP follows rising price; DOWN follows falling price; also retain raw-up values. No cost/fill/stop/target simulation.',
        status_matrix='UP/DOWN/OTHER on435 days between14:30 and15:00; separate detailed reasons for range outside MID, flat or missing ATR. Only transition counts, no return optimization on movers.',
        tests='Exactly24 two-sided log-bp tests: FIRST/REST means vs0 at15:00 for fixed/dynamic UP/DOWN (8);15:00 FIRST/REST minus each of2 earlier quarters for fixed/dynamic UP/DOWN (16). Joint daily influence scores, known overlap covariance, daily-score HAC(5), same conservative tdf as specificity, one Holm24 family. Points CI separately calculated, no extra p-family. No FULL zero tests or chosen horizons.',
        concentration='All leave-one-day-out and all leave-one-calendar-quarter-out means of original FULL15:00 point return for fixed and dynamic UP cohorts. Report all quarter omissions and min/max day omissions; no deleting outliers from official results or recomputing favorable p-values.',
        integrity='Check raw active timestamps14:59,15:00,15:01 on all435 days: presence, uniqueness,60-second spacing, one contract and vendor trade date, finite/tick-grid/OHLC coherence. Price difference previousclose-to-nextopen is NOT automatically a missing minute. Bar labels and subsecond paths cannot be independently certified with same-source1m bars.',
        decision_order=['If fixed UP FULL15:00 mean<=0: positive average disappears under fixed cohort (selection explanation).',
            'Else if any UP leave-day or leave-quarter mean<=0 in either scheme: sign-fragile (concentration explanation).',
            'Else if grid/integrity fails or no independent second source: interesting observation, independently unconfirmed. Same-source checks can survive but do not certify label alignment.',
            'Else: stronger research hypothesis, not a validated trading edge. No equivalence claim from non-significance.'],
        inference_limits='Exploratory after earlier analyses; Holm24 only covers this round, not whole project. Causal timing is not institutional causal identification. Open prices do not prove executable fills. No fixed minimum economically important effect was agreed; survival means direction survival only.',
        publication='Local report and aggregates only. No new GitHub or Vercel authorization in current task.')
    if PROTOCOL.exists() and json.loads(PROTOCOL.read_text())!=spec:raise ValueError('Protocol replacement refused')
    dump(PROTOCOL,spec)
    names=['scripts/afternoon_falsification.py','research/afternoon-falsification-protocol.json',
        'scripts/afternoon_specificity.py','research/afternoon-specificity-lock.json',
        'research/afternoon-specificity-protocol.json','artifacts/afternoon-specificity/COMPLETED.json']
    names+=list(json.loads((ROOT/'research/afternoon-specificity-lock.json').read_text())['files_sha256'])
    names+=list(json.loads((ROOT/'research/afternoon-specificity-report-manifest.json').read_text())['files_sha256'])
    snap=dict(status='LOCKED_BEFORE_NEW_FIXED_COHORT_AND_COMPONENT_RESULTS',files_sha256={p:sha(ROOT/p) for p in sorted(set(names))})
    if LOCK.exists() and json.loads(LOCK.read_text())!=snap:raise ValueError('Code/input lock replacement refused')
    dump(LOCK,snap)
    return dict(protocol_sha256=sha(PROTOCOL),locked_files=len(snap['files_sha256']))


def check():
    archive=verify_archive()
    for name,digest in json.loads(LOCK.read_text())['files_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Frozen bytes changed: '+name)
    return archive


def status_at(p,atr,k):
    selected=context_at(p,atr,k)
    if selected:return selected
    if not np.isfinite(atr) or atr<=0:return 'ATR_MISSING'
    ratio=(max(p['high'][:k])-min(p['low'][:k]))/atr
    if ratio<.5:return 'RANGE_BELOW_MID'
    if ratio>=1.2:return 'RANGE_ABOVE_MID'
    return 'MID_FLAT'


def measure(state,days):
    rows=[];transitions=[];checks=0
    for day in days:
        p,ctx=state[day];atr=ctx['atr'];fixed=context_at(p,atr,300)
        transitions.append(dict(day=day,at1430=status_at(p,atr,300),at1445=status_at(p,atr,315),at1500=status_at(p,atr,330)))
        for clock,k in WINDOWS.items():
            dynamic=context_at(p,atr,k)
            prefix={z:v[:k] for z,v in p.items()}
            if context_at(prefix,atr,k)!=dynamic:raise AssertionError('Future selection dependence')
            checks+=1
            for scheme,group in [('fixed',fixed),('dynamic',dynamic)]:
                if group not in ('UP','DOWN'):continue
                s=1 if group=='UP' else -1
                c0=float(p['close'][k-1]);o0=float(p['open'][k]);c1=float(p['close'][k]);o1=float(p['open'][k+1]);end=float(p['close'][k+14])
                parts={'FULL':(c0,end),'FIRST':(o0,c1),'REST':(o1,end)}
                for part,(a,b) in parts.items():
                    rows.append(dict(day=day,quarter=str(pd.Period(day,freq='Q')),scheme=scheme,group=group,clock=clock,
                        part=part,points=s*(b-a),bps=s*10000*np.log(b/a),raw_up_points=b-a,
                        gap_before=s*(o0-c0),gap_between=s*(o1-c1)))
                if not np.isclose((o0-c0)+(c1-o0)+(o1-c1)+(end-o1),end-c0,rtol=0,atol=1e-10):raise AssertionError('Parts do not reconcile')
    return pd.DataFrame(rows),pd.DataFrame(transitions),checks


def calculate(frame,calendar):
    tables=[];est={};groups={}
    for scheme in ('fixed','dynamic'):
        for group in ('UP','DOWN'):
            for clock in WINDOWS:
                for part in ('FULL','FIRST','REST'):
                    g=frame[frame.scheme.eq(scheme)&frame.group.eq(group)&frame.clock.eq(clock)&frame.part.eq(part)]
                    groups[scheme,group,clock,part]=g
                    est[scheme,group,clock,part]={m:mean_influence(g,calendar,m) for m in ('points','bps')}
                    tables.append(dict(scheme=scheme,group=group,clock=clock,part=part,days=len(g),
                        mean_points=float(g.points.mean()),median_points=float(g.points.median()),mean_logbps=float(g.bps.mean()),
                        positive_fraction=float(g.points.gt(0).mean()),gap_before_mean=float(g.gap_before.mean()),gap_between_mean=float(g.gap_between.mean())))
    tests=[]
    for scheme in ('fixed','dynamic'):
        for group in ('UP','DOWN'):
            for part in ('FIRST','REST'):
                a=groups[scheme,group,'15:00',part]
                for other in (None,'14:30','14:45'):
                    b=None if other is None else groups[scheme,group,other,part]
                    union=set(a.day) if b is None else set(a.day)|set(b.day)
                    df=len(a)-1 if b is None else min(len(a),len(b))-1
                    r=dict(scheme=scheme,group=group,part=part,comparison='15:00 mean vs0' if other is None else '15:00 minus '+other,
                        n15=len(a),n_other=0 if b is None else len(b))
                    for metric in ('points','bps'):
                        ma,sa=est[scheme,group,'15:00',part][metric]
                        mb,sb=(0.,np.zeros(len(calendar))) if other is None else est[scheme,group,other,part][metric]
                        r[metric]=uncertainty(ma-mb,sa-sb,len(union),df)
                    r['points'].pop('p_raw');tests.append(r)
    adjusted=holm([r['bps']['p_raw'] for r in tests])
    for r,p in zip(tests,adjusted):r['p_Holm24']=p
    return tables,tests


def concentration(frame):
    summaries=[];quarters=[];private_days=[]
    for scheme in ('fixed','dynamic'):
        g=frame[frame.scheme.eq(scheme)&frame.group.eq('UP')&frame.clock.eq('15:00')&frame.part.eq('FULL')].copy()
        n=len(g);total=float(g.points.sum());loo=(total-g.points)/(n-1)
        for j,(_,r) in enumerate(g.iterrows()):
            private_days.append(dict(scheme=scheme,omitted_day=r.day,omitted_return=float(r.points),remaining_mean=float(loo.iloc[j])))
        q=[]
        for name,sl in g.groupby('quarter'):
            q.append(dict(scheme=scheme,omitted_quarter=name,omitted_days=len(sl),omitted_mean=float(sl.points.mean()),
                remaining_days=n-len(sl),remaining_mean=float((total-sl.points.sum())/(n-len(sl)))))
        quarters.extend(q)
        low=int(np.argmin(loo.to_numpy()));high=int(np.argmax(loo.to_numpy()))
        summaries.append(dict(scheme=scheme,days=n,original_mean=float(g.points.mean()),original_median=float(g.points.median()),
            day_out_min_mean=float(loo.iloc[low]),day_out_min_omitted=g.iloc[low].day,
            day_out_min_removed_return=float(g.iloc[low].points),
            day_out_max_mean=float(loo.iloc[high]),day_out_max_omitted=g.iloc[high].day,
            day_out_max_removed_return=float(g.iloc[high].points),
            quarter_out_min=min(q,key=lambda r:r['remaining_mean']),quarter_out_max=max(q,key=lambda r:r['remaining_mean']),
            any_day_sign_flip=bool((loo<=0).any()),any_quarter_sign_flip=any(r['remaining_mean']<=0 for r in q)))
    return summaries,quarters,pd.DataFrame(private_days)


def audit_bars(active,days):
    groups={d:g for d,g in active.groupby('trade_date')};rows=[]
    for day in days:
        g=groups[day];ix=pd.DatetimeIndex([at(day,c) for c in ('14:59','15:00','15:01')]);z=g.loc[g.index.isin(ix)]
        missing=len(ix.difference(z.index));duplicates=int(z.index.duplicated().sum())
        spacing=bool(len(z)==3 and np.all(np.diff(z.index.asi8)==60*1000000000))
        p=z[['open','high','low','close']].to_numpy()
        coherent=bool(np.isfinite(p).all() and (z.high>=z[['open','close','low']].max(axis=1)).all() and (z.low<=z[['open','close','high']].min(axis=1)).all())
        ticks=bool(np.allclose(p*4,np.rint(p*4),rtol=0,atol=1e-8))
        row=dict(day=day,missing=missing,duplicates=duplicates,spacing60seconds=spacing,
            coherent=coherent,tick_grid=ticks,one_contract=z.contract.nunique()==1,one_trade_date=z.trade_date.nunique()==1)
        if not missing and not duplicates:
            row['gap1500']=float(z.at[ix[1],'open']-z.at[ix[0],'close'])
            row['gap1501']=float(z.at[ix[2],'open']-z.at[ix[1],'close'])
        rows.append(row)
    a=pd.DataFrame(rows);gaps=[]
    for key in ('gap1500','gap1501'):
        x=a[key].to_numpy()
        gaps.append(dict(pair=key,nonzero_days=int((x!=0).sum()),mean_points=float(x.mean()),median_points=float(np.median(x)),
            min_points=float(x.min()),max_points=float(x.max()),max_absolute_points=float(np.abs(x).max())))
    failures=a[(a.missing>0)|(a.duplicates>0)|~a.spacing60seconds|~a.coherent|~a.tick_grid|~a.one_contract|~a.one_trade_date]
    return dict(days=len(a),expected_bars=3*len(a),observed_bars=3*len(a)-int(a.missing.sum())+int(a.duplicates.sum()),
        missing=int(a.missing.sum()),duplicates=int(a.duplicates.sum()),flagged_days=len(failures),price_gaps=gaps,
        second_source_verified=False,limitation='Same-source timestamp/OHLC audit only; not proof of true vendor bar-label semantics, subsecond ordering or executable fills.'),a


def transition_summary(frame):
    f=frame.copy()
    for col in ('at1430','at1500'):f[col]=f[col].where(f[col].isin(['UP','DOWN']),'OTHER')
    matrix=[]
    for a in ('UP','DOWN','OTHER'):
        for b in ('UP','DOWN','OTHER'):matrix.append(dict(at1430=a,at1500=b,days=int((f.at1430.eq(a)&f.at1500.eq(b)).sum())))
    detail=frame.groupby(['at1430','at1500']).size().reset_index(name='days').to_dict('records')
    any_change=None
    if 'at1445' in frame:
        mid=frame.at1445.where(frame.at1445.isin(['UP','DOWN']),'OTHER')
        any_change=int(((f.at1430!=mid)|(mid!=f.at1500)).sum())
    return dict(matrix=matrix,detailed=detail,coarse_changed_days=int((f.at1430!=f.at1500).sum()),
        detailed_changed_days=int((frame.at1430!=frame.at1500).sum()),changed_at_any_of_three_clocks=any_change)


def verify():
    check();saved=json.loads((OUT/'COMPLETED.json').read_text())
    for name,digest in saved['files_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Output drift '+name)
    return dict(status='PASS_FIXED_FALSIFICATION_EVIDENCE',**saved['verification'])


def run():
    archive=check()
    if (OUT/'COMPLETED.json').exists():raise ValueError('Completed round exists, use --verify')
    OUT.mkdir(parents=True,exist_ok=True)
    with forbid_scoring():state,calendar,days,source,active,*_=load_inputs()
    frame,transitions,prefix=measure(state,days)
    previous=pd.read_csv(ROOT/'artifacts/afternoon-specificity/measurements.csv',float_precision='round_trip')
    for clock in WINDOWS:
        for group in ('UP','DOWN'):
            new=frame[frame.scheme.eq('dynamic')&frame.group.eq(group)&frame.clock.eq(clock)&frame.part.eq('FULL')].set_index('day')
            old=previous[previous.group.eq(group)&previous.clock.eq(clock)].set_index('day')
            if set(new.index)!=set(old.index) or not np.array_equal(new.points,old.loc[new.index,'points']):raise AssertionError('Previous specificity rows changed')
    tables,tests=calculate(frame,calendar);conc,quarters,loo=concentration(frame);integrity,bar_rows=audit_bars(active,days)
    # True source reload for replay, not cached measurement reformatting.
    with forbid_scoring():s2,c2,d2,_,a2,*_=load_inputs()
    replay,tr2,_=measure(s2,d2);pd.testing.assert_frame_equal(frame,replay,check_exact=True);pd.testing.assert_frame_equal(transitions,tr2,check_exact=True)
    t2,p2=calculate(replay,c2)
    if json.dumps(clean([tables,tests]),sort_keys=True)!=json.dumps(clean([t2,p2]),sort_keys=True):raise AssertionError('Inference replay mismatch')
    frame.to_csv(OUT/'measurements.csv',index=False,float_format='%.17g');replay.to_csv(OUT/'measurements-replay.csv',index=False,float_format='%.17g')
    if sha(OUT/'measurements.csv')!=sha(OUT/'measurements-replay.csv'):raise AssertionError('Replay bytes differ')
    transitions.to_csv(OUT/'transitions.csv',index=False);loo.to_csv(OUT/'leave-days.csv',index=False,float_format='%.17g');bar_rows.to_csv(OUT/'bar-audit.csv',index=False,float_format='%.17g')
    fixed=next(r for r in conc if r['scheme']=='fixed')
    if fixed['original_mean']<=0:decision='DISAPPEARS_WITH_FIXED_COHORT'
    elif any(r['any_day_sign_flip'] or r['any_quarter_sign_flip'] for r in conc):decision='SIGN_FRAGILE_TO_LEAVE_OUT'
    elif integrity['flagged_days'] or not integrity['second_source_verified']:decision='INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED'
    else:decision='STRONGER_RESEARCH_HYPOTHESIS_NOT_VALIDATED_EDGE'
    verification=dict(source_files=source['source_files'],days=len(days),prefix_checks=prefix,fresh_source_replay_identical=True,
        previous_clock_cohorts_and_returns_reproduced=True,formal_tests=len(tests),new_strategy_runs=0,protected_archive_files=archive['protected_files'])
    dump(OUT/'summary.json',dict(status='EXPLORATORY_FIXED_FALSIFICATION_COMPLETE',decision=decision,verification=verification,
        tables=tables,tests=tests,concentration=conc,leave_quarters=quarters,transitions=transition_summary(transitions),integrity=integrity,
        protocol_sha256=sha(PROTOCOL)))
    names=['measurements.csv','measurements-replay.csv','transitions.csv','leave-days.csv','bar-audit.csv','summary.json']
    dump(OUT/'COMPLETED.json',dict(verification=verification,files_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in names}))
    dump(ROOT/'research/afternoon-falsification-verification.json',dict(verification=verification,completed_sha256=sha(OUT/'COMPLETED.json')))
    print(json.dumps(dict(decision=decision,**verification),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.register:print(json.dumps(register(),indent=2))
    elif a.verify:print(json.dumps(verify(),indent=2))
    else:run()
