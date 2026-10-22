"""Fixed three-quarter-hour exploratory comparison, not a trading strategy.

Run --register before reading new window outcomes. Existing archive, causal
map, source register and source bytes remain untouched. No optimize flag.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t

from scripts.causal_map.__main__ import load_inputs, clean
from scripts.causal_map.core import holm
from scripts.oos_preparation.year import forbid_scoring
from scripts.oos_preparation.adapter import sha
from scripts.archive_experiments import verify_archive

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'research/afternoon-specificity-protocol.json'
LOCK=ROOT/'research/afternoon-specificity-lock.json'
OUT=ROOT/'artifacts/afternoon-specificity'
WINDOWS={'14:30':300,'14:45':315,'15:00':330}
GROUPS=('ALL','UP','DOWN')


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(clean(obj),indent=2,allow_nan=False)+'\n')


def register():
    verify_archive()
    spec=dict(status='FIXED_EXPLORATORY_SPECIFICITY_COMPARISON_NOT_NEW_HOLDOUT',
        anchor_commit='8f727f671a4f78a5473aebf853aae89ed663d7c2',
        windows=WINDOWS,horizon_minutes=15,universe='Identical435 complete RTH days from frozen quality mask',
        context='UP/DOWN relative to09:30open using LAST COMPLETED minute close. RTH high-low over completed bars only, divided by frozen prior ATR14. MID=[0.5,1.2), preserving original upper-exclusive rule. Zero direction and missing ATR excluded only from context rows, never from ALL435.',
        direction='ALL and UP use rising-price orientation; DOWN uses falling-price orientation. A DOWN context premium compares with blind SHORT of the same quarter, not blind long.',
        friction_points=1.225,friction_scope='Constant arithmetic deduction per observation, no entries/stops/targets/fill simulator. Costs cancel in context-minus-same-direction-benchmark differences.',
        contrasts='Exactly10:15:00 minus14:30 and minus14:45 for ALL/UP/DOWN raw oriented means (6); and UP/DOWN context premiums over each own same-clock unconditional directional benchmark (4). No extra clocks, horizons, thresholds or subgroups.',
        inference='Primary: two-sided mean LOG-bp contrasts, joint day influence scores with exact overlap covariance. Bartlett daily-score HAC lags1..5, calendar454 rows including0 influence on absent rows, finite correction D/(D-1) for union eventdays, conservative tdf=min compared group daycounts-1. One Holm10 family. Nominal95% intervals; points CI separately computed. CR1 standard error recorded only as sensitivity, no second p-family.',
        paired_cohorts='Context is re-evaluated separately at each clock; cohorts may change. This compares operational conditional means, not a matched-identical-cohort causal treatment effect. Temporal dependence and changing cohort composition are limitations, not parameters to optimize.',
        checks='Every day:selector prefix at each of3 boundaries agrees with full-day selector; mutation of all later bars leaves context unchanged.15:00 subgroup membership and all435 benchmark anchors/outcomes reproduce previous known results. Fresh source reload replay must be identical.',
        known_1500_findings=dict(all_days=435,all_mean_points=.846551724137931,all_median_points=1.25,
            up_days=167,up_mean_points=7.540419161676646,up_median_points=4.,
            down_days=131,down_oriented_mean_points=3.6660305343511452,down_oriented_median_points=2.5,
            previous_benchmark_nominal_p_logbps=.006507373940679841,
            evidence='Previously examined exploratory result; not an independent preregistration or validation.'),
        limits=['Previously consumed data; correction only covers these10 comparisons, not all historical research.',
            'Non-significant pairwise differences do not establish equivalence, absence or generic momentum.',
            'Point-in-time information use is not institutional or economic causal identification.',
            'No promotion or revival of archived strategies. No external publication authorized in this request.'])
    if PROTOCOL.exists() and json.loads(PROTOCOL.read_text())!=spec:raise ValueError('Protocol changed')
    dump(PROTOCOL,spec)
    paths=['scripts/afternoon_specificity.py','research/afternoon-specificity-protocol.json',
        'scripts/causal_map/__main__.py','scripts/causal_map/core.py','research/causal-map-lock.json',
        'artifacts/causal-map/COMPLETED.json','artifacts/causal-map/events-horizons.csv',
        'artifacts/raw-market/quality.json','research/causal-map-publication.json']
    paths+=list(json.loads((ROOT/'research/causal-map-lock.json').read_text())['files_sha256'])
    snap=dict(status='CODE_METHOD_INPUT_LOCK_BEFORE_NEIGHBOR_OUTCOMES',files_sha256={p:sha(ROOT/p) for p in sorted(set(paths))})
    if LOCK.exists() and json.loads(LOCK.read_text())!=snap:raise ValueError('Method lock changed')
    dump(LOCK,snap)
    return dict(protocol_sha256=sha(PROTOCOL),locked_files=len(snap['files_sha256']))


def check():
    archive=verify_archive()
    for path,digest in json.loads(LOCK.read_text())['files_sha256'].items():
        if sha(ROOT/path)!=digest:raise ValueError('Locked bytes changed: '+path)
    return archive


def context_at(prices,atr,k):
    """Selection reads no bar at/after boundary k."""
    if len(prices['close'])<k:raise ValueError('Insufficient causal prefix')
    if not np.isfinite(atr) or atr<=0:return None
    ratio=(max(prices['high'][:k])-min(prices['low'][:k]))/atr
    if not (.5<=ratio<1.2):return None
    sign=np.sign(prices['close'][k-1]-prices['open'][0])
    return 'UP' if sign>0 else ('DOWN' if sign<0 else None)


def measurements(state,days):
    rows=[];prefix_checks=0;mutation_checks=0
    for day in days:
        prices,ctx=state[day]
        for clock,k in WINDOWS.items():
            group=context_at(prices,ctx['atr'],k)
            prefix={z:v[:k] for z,v in prices.items()}
            if context_at(prefix,ctx['atr'],k)!=group:raise AssertionError('Future prefix dependence')
            prefix_checks+=1
            mutated={z:v.copy() for z,v in prices.items()}
            for z in ('open','high','low','close'):mutated[z][k:]*=2
            if context_at(mutated,ctx['atr'],k)!=group:raise AssertionError('Future mutation dependence')
            mutation_checks+=1
            p0,p1=float(prices['close'][k-1]),float(prices['close'][k+14])
            points=p1-p0;bps=10000*np.log(p1/p0)
            for label in ['ALL']+([group] if group else []):
                direction=-1 if label=='DOWN' else 1
                rows.append(dict(day=day,clock=clock,group=label,direction=direction,anchor=p0,endpoint=p1,
                    raw_up_points=points,raw_up_bps=bps,points=direction*points,bps=direction*bps))
    return pd.DataFrame(rows),prefix_checks,mutation_checks


def mean_influence(frame,calendar,metric):
    mean=float(frame[metric].mean());score=pd.Series(0.,index=calendar)
    score.loc[frame.day]=(frame[metric].to_numpy()-mean)/len(frame)
    return mean,score.to_numpy()


def uncertainty(effect,score,event_days,df):
    correction=event_days/(event_days-1);meat=float(score@score)
    cr1=np.sqrt(meat*correction)
    for lag in range(1,6):meat+=2*(1-lag/6)*float(score[lag:]@score[:-lag])
    se=float(np.sqrt(max(0,meat)*correction));crit=float(t.ppf(.975,df))
    p=float(2*t.sf(abs(effect/se),df)) if se>0 else (1. if effect==0 else 0.)
    return dict(delta=effect,se_HAC5=se,se_CR1=float(cr1),ci95=[effect-crit*se,effect+crit*se],p_raw=p,df=df,event_days=event_days)


def calculate(frame,calendar):
    rows=[];est={};groups={}
    cost=1.225
    for clock in WINDOWS:
        blind=frame[(frame.clock==clock)&frame.group.eq('ALL')]
        for label in GROUPS:
            g=frame[(frame.clock==clock)&frame.group.eq(label)]
            direction=-1 if label=='DOWN' else 1
            rows.append(dict(clock=clock,group=label,days=len(g),mean_gross_points=float(g.points.mean()),
                median_gross_points=float(g.points.median()),mean_cost_only_points=float(g.points.mean()-cost),
                median_cost_only_points=float(g.points.median()-cost),positive_fraction=float(g.points.gt(0).mean()),
                positive_after_cost_fraction=float(g.points.gt(cost).mean()),mean_logbps=float(g.bps.mean()),
                same_direction_blind_mean_points=float(direction*blind.points.mean()),
                premium_points=float(g.points.mean()-direction*blind.points.mean())))
            groups[clock,label]=g
            est[clock,label]={m:mean_influence(g,calendar,m) for m in ('points','bps')}
    contrasts=[]
    for other in ('14:30','14:45'):
        for kind,labels in [('raw_mean',GROUPS),('context_premium',('UP','DOWN'))]:
            for label in labels:
                direction=-1 if label=='DOWN' else 1
                a,b=groups['15:00',label],groups[other,label]
                union=set(a.day)|set(b.day)
                df=min(len(a),len(b))-1
                result=dict(kind=kind,group=label,comparison='15:00 minus '+other,n15=len(a),n_other=len(b),
                    common_days=len(set(a.day)&set(b.day)),union_days=len(union))
                if kind=='context_premium':union=set(groups['15:00','ALL'].day);df=min(df,len(union)-1)
                for metric in ('points','bps'):
                    ma,sa=est['15:00',label][metric];mb,sb=est[other,label][metric]
                    effect=ma-mb;score=sa-sb
                    if kind=='context_premium':
                        m1,s1=est['15:00','ALL'][metric];m0,s0=est[other,'ALL'][metric]
                        effect-=direction*(m1-m0);score-=direction*(s1-s0)
                    result[metric]=uncertainty(float(effect),score,len(union),df)
                # Only log-bp p-values enter the10-cell formal test family.
                result['points'].pop('p_raw')
                contrasts.append(result)
    adj=holm([r['bps']['p_raw'] for r in contrasts])
    for r,p in zip(contrasts,adj):r['p_Holm10']=p
    return rows,contrasts


def verify():
    archive=check();done=json.loads((OUT/'COMPLETED.json').read_text())
    for p,digest in done['files_sha256'].items():
        if sha(ROOT/p)!=digest:raise ValueError('Output changed '+p)
    return dict(status='PASS_FIXED_SPECIFICITY_OUTPUTS',archive=archive,**done['verification'])


def run():
    archive=check()
    if (OUT/'COMPLETED.json').exists():raise ValueError('Completed fixed comparison; --verify only')
    OUT.mkdir(parents=True,exist_ok=True)
    with forbid_scoring():state,calendar,days,source,*_=load_inputs()
    frame,prefix,mutation=measurements(state,days)
    old=pd.read_csv(ROOT/'artifacts/causal-map/events-horizons.csv',float_precision='round_trip')
    for label,n in [('UP',167),('DOWN',131)]:
        previous=old[old.mechanism.eq(f'C_1500_{label}_MID')&old.horizon.astype(str).eq('15')].set_index('day')
        current=frame[frame.clock.eq('15:00')&frame.group.eq(label)].set_index('day')
        if len(current)!=n or set(current.index)!=set(previous.index):raise AssertionError('Original membership changed')
        if not np.array_equal(current.points,previous.loc[current.index,'return_points']):raise AssertionError('Original prices changed')
    known=json.loads(PROTOCOL.read_text())['known_1500_findings']
    blind=frame[frame.clock.eq('15:00')&frame.group.eq('ALL')]
    if len(blind)!=435 or not np.isclose(blind.points.mean(),known['all_mean_points'],atol=1e-12,rtol=0):raise AssertionError('Blind benchmark changed')
    rows,contrasts=calculate(frame,calendar)
    # Second source reload, not a cached dataframe replay.
    with forbid_scoring():second,cal2,days2,_,*_=load_inputs()
    replay,_,_=measurements(second,days2)
    pd.testing.assert_frame_equal(frame,replay,check_exact=True)
    r2,c2=calculate(replay,cal2)
    if json.dumps(clean([rows,contrasts]),sort_keys=True)!=json.dumps(clean([r2,c2]),sort_keys=True):raise AssertionError('Aggregate replay mismatch')
    frame.to_csv(OUT/'measurements.csv',index=False,float_format='%.17g')
    replay.to_csv(OUT/'measurements-replay.csv',index=False,float_format='%.17g')
    if sha(OUT/'measurements.csv')!=sha(OUT/'measurements-replay.csv'):raise AssertionError('Replay bytes differ')
    verification=dict(source_files=source['source_files'],complete_RTH_days=len(days),clock_groups=len(rows),formal_tests=len(contrasts),
        prefix_checks=prefix,future_mutation_checks=mutation,source_reload_replay_identical=True,
        original1500_groups_and_benchmark_reproduced=True,protected_archive_files=archive['protected_files'],new_strategy_runs=0)
    dump(OUT/'summary.json',dict(status='EXPLORATORY_FIXED_CLOCK_SPECIFICITY_NOT_VALIDATION',verification=verification,
        protocol_sha256=sha(PROTOCOL),rows=rows,contrasts=contrasts,protocol=json.loads(PROTOCOL.read_text())))
    paths=[OUT/n for n in ('measurements.csv','measurements-replay.csv','summary.json')]
    dump(OUT/'COMPLETED.json',dict(verification=verification,files_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths}))
    dump(ROOT/'research/afternoon-specificity-verification.json',dict(verification=verification,completed_sha256=sha(OUT/'COMPLETED.json')))
    print(json.dumps(verification,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.register:print(json.dumps(register(),indent=2))
    elif a.verify:print(json.dumps(verify(),indent=2))
    else:run()
