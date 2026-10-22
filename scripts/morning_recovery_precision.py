"""Fixed CI/quarter/excursion extension of existing29-vs40 morning records."""
import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import t

from scripts.morning_recovery_anatomy import ROOT,load_active,frozen_groups,verify as verify_anatomy,dump
from scripts.register_afternoon_candidate_v2 import verify as verify_candidate
from scripts.oos_preparation.adapter import at,sha
from scripts.oos_preparation.year import forbid_scoring
from scripts.afternoon_specificity import mean_influence

OUT=ROOT/'artifacts/morning-recovery-precision'
PROTOCOL=ROOT/'research/morning-recovery-precision-protocol.json'
LOCK=ROOT/'research/morning-recovery-precision-lock.json'
REPS=20000
BLOCK=5
SEED=20261022


def register():
    verify_candidate();verify_anatomy()
    spec=dict(status='FIXED_PRECISION_EXTENSION_NOT_NEW_MODEL',
        sample='Exactly the existing69 Gap-Down days:29 first-quarter-negative,40 positive,zero flat. Reuse fixed morning measurements, no selection or horizon changes.',
        outcome='Existing long-signed gross following_points:09:45 Open to10:29 Close,45 bars; no first-quarter bar or09:44close-to09:45open gap.',
        requested_CIs='Exactly two nominal pointwise95% intervals: mean of29 negative-opening days and mean29 minus mean40. Not simultaneous, not independent holdout evidence. No p-values or significance selection.',
        main_method='Daily influence scores on all454 original scheduled sessions, including zero influence (not zero return) for nonselected days. Bartlett HAC lags1..5, correction D/(D-1) with29 clusters for mean and69 for contrast; t df28 for both. Contrast scores are subtracted on the same calendar, retaining temporal covariance.',
        sensitivity=dict(method='Circular moving-block percentile bootstrap, entire scheduled-day records/masks together; recompute both conditional means and their difference in each replicate; never fill absent events with zero returns.',
            block_sessions=BLOCK,replicates=REPS,seed=SEED,quantiles=[.025,.975],
            limits='Finite small-sample sensitivity under approximate temporal stability; not guaranteed coverage under arbitrary regime changes. Both methods reported, no choice based on narrower/more positive result.'),
        quarters='All calendar quarters2024Q4 through2026Q3. Per group count, mean, median and fraction following return>0. Empty groups remain N=0, no invented mean. No quarter p-values.',
        excursions='Only29 first-quarter-negative Gap-Down days. Long-oriented MFE=max(High09:45..10:29)-Open09:45; MAE=Open09:45-min(Low09:45..10:29). Nonnegative distances, not exit PnL or known intraminute order. No pre09:45 or post10:29 bars included.',
        excursion_output='Mean,min,P10,P25,median,P75,P90,max in points; per-quarter medians for the29-day group. No stops, targets, risk multiples or parameter search.',
        checks='Reproduce existing69 returns; frozen29/40 membership; direct45-bar excursion endpoints; fresh source replay. Preserve all previous locks including v1, v2 and the149/101 morning tables.',
        publication='Local only; no GitHub/Vercel release or future15:00 test authorized.')
    files=['scripts/morning_recovery_precision.py','research/morning-recovery-precision-protocol.json',
        'artifacts/morning-recovery-anatomy/measurements.csv','artifacts/morning-recovery-anatomy/COMPLETED.json',
        'research/morning-recovery-anatomy-report-manifest.json','research/afternoon-candidate-v2-lock.json',
        'artifacts/raw-market/quality.json','research/oos-year-sources.json','scripts/afternoon_specificity.py']
    if PROTOCOL.exists() and json.loads(PROTOCOL.read_text())!=spec:
        raise ValueError('Protocol replacement refused')
    dump(PROTOCOL,spec)
    snap=dict(status='LOCKED_BEFORE_NEW_CI_QUARTER_AND_MFE_MAE_RESULTS',files_sha256={n:sha(ROOT/n) for n in files})
    if LOCK.exists() and json.loads(LOCK.read_text())!=snap:
        raise ValueError('Method replacement refused')
    dump(LOCK,snap)
    return dict(status=snap['status'],locked_files=len(files))


def preflight():
    verify_candidate();verify_anatomy()
    for name,digest in json.loads(LOCK.read_text())['files_sha256'].items():
        if sha(ROOT/name)!=digest:
            raise ValueError('Frozen method or inputs changed: '+name)


def hac_interval(effect,score,event_days,df):
    score=np.asarray(score,float)
    if event_days<2 or df<1:
        raise ValueError('Insufficient day clusters')
    base=float(score@score)
    meat=base
    for lag in range(1,6):
        meat+=2*(1-lag/6)*float(score[lag:]@score[:-lag])
    factor=event_days/(event_days-1)
    se=float(np.sqrt(max(0.,meat)*factor))
    crit=float(t.ppf(.975,df))
    return dict(estimate=float(effect),se_HAC5=se,se_CR1=float(np.sqrt(base*factor)),
        df=int(df),event_days=int(event_days),ci95=[float(effect-crit*se),float(effect+crit*se)])


def bootstrap_means(frame,calendar,reps=REPS,seed=SEED,block=BLOCK):
    index={day:i for i,day in enumerate(calendar)}
    masks=np.zeros((2,len(calendar)),dtype=float)
    values=np.zeros_like(masks)
    for group,name in enumerate(('NEGATIVE','POSITIVE')):
        for r in frame[frame.first_quarter_status.eq(name)].itertuples():
            j=index[r.day];masks[group,j]=1.;values[group,j]=r.following_points
    rng=np.random.default_rng(seed)
    n=len(calendar);blocks=int(np.ceil(n/block));negative=[];differences=[];valid=0
    for start in range(0,reps,1000):
        count=min(1000,reps-start)
        anchors=rng.integers(0,n,size=(count,blocks))
        ix=((anchors[:,:,None]+np.arange(block)[None,None,:])%n).reshape(count,-1)[:,:n]
        denominator=masks[:,ix].sum(axis=2)
        numerator=values[:,ix].sum(axis=2)
        good=(denominator>0).all(axis=0)
        avg=numerator[:,good]/denominator[:,good]
        negative.extend(avg[0].tolist());differences.extend((avg[0]-avg[1]).tolist());valid+=int(good.sum())
    if valid<reps*.99:
        raise ValueError('Too many bootstrap samples without both groups')
    return dict(replicates=reps,valid_replicates=valid,block_sessions=block,seed=seed,
        mean_negative_ci95=np.quantile(negative,[.025,.975]).tolist(),
        difference_ci95=np.quantile(differences,[.025,.975]).tolist())


def excursion(prices,entry):
    if any(len(prices[k])!=45 or not np.isfinite(prices[k]).all() for k in ('high','low')):
        raise ValueError('Require exactly45 valid post09:45 bars')
    mfe=float(np.max(prices['high'])-entry)
    mae=float(entry-np.min(prices['low']))
    if mfe<0 or mae<0:
        raise ValueError('Entry outside post-entry OHLC span')
    return dict(mfe_points=mfe,mae_points=mae)


def extract_excursions(active,negative,ledger):
    groups={d:g for d,g in active.groupby('trade_date')};lookup=ledger.set_index('day');rows=[]
    for day in sorted(negative):
        ix=pd.date_range(at(day,'09:45'),at(day,'10:30'),freq='min',inclusive='left')
        g=groups[day].reindex(ix)
        if not g.index.equals(ix) or g[['open','high','low','close']].isna().any().any():
            raise ValueError('Missing excursion minute')
        entry=float(g.open.iloc[0]);end=float(g.close.iloc[-1])
        assert end-entry==lookup.at[day,'following_points']
        assert g.contract.nunique()==1
        value=excursion({k:g[k].to_numpy(float) for k in ('high','low')},entry)
        rows.append(dict(day=day,quarter=str(pd.Period(day,freq='Q')),**value))
    return pd.DataFrame(rows)


def distribution(v):
    v=np.asarray(v,float)
    return dict(days=len(v),mean=float(v.mean()),min=float(v.min()),max=float(v.max()),
        **{name:float(np.quantile(v,q)) for name,q in [('p10',.1),('p25',.25),('median',.5),('p75',.75),('p90',.9)]})


def analyze(frame,calendar,paths):
    a=frame[frame.first_quarter_status.eq('NEGATIVE')]
    b=frame[frame.first_quarter_status.eq('POSITIVE')]
    assert len(a)==29 and len(b)==40 and len(frame)==69
    ma,sa=mean_influence(a,calendar,'following_points')
    mb,sb=mean_influence(b,calendar,'following_points')
    assert np.isclose(ma,57.456896551724135,rtol=0,atol=1e-12)
    assert np.isclose(mb,5.325,rtol=0,atol=1e-12)
    intervals=[dict(id='MEAN_NEGATIVE29',**hac_interval(ma,sa,29,28)),
        dict(id='NEGATIVE29_MINUS_POSITIVE40',**hac_interval(ma-mb,sa-sb,69,28))]
    boot=bootstrap_means(frame,calendar)
    quarters=[]
    qseries=frame.day.map(lambda d:str(pd.Period(d,freq='Q')))
    for quarter in pd.period_range('2024Q4','2026Q3',freq='Q').astype(str):
        for sign in ('NEGATIVE','POSITIVE'):
            sl=frame[qseries.eq(quarter)&frame.first_quarter_status.eq(sign)]
            x=sl.following_points
            p=paths[paths.day.isin(sl.day)]
            quarters.append(dict(quarter=quarter,group=sign,days=len(sl),
                mean_points=float(x.mean()) if len(sl) else None,
                median_points=float(x.median()) if len(sl) else None,
                positive_fraction=float(x.gt(0).mean()) if len(sl) else None,
                median_mfe_points=float(p.mfe_points.median()) if len(p) else None,
                median_mae_points=float(p.mae_points.median()) if len(p) else None))
    return dict(intervals=intervals,block_bootstrap=boot,quarters=quarters,
        excursions={k:distribution(paths[k]) for k in ('mfe_points','mae_points')},
        group_means=dict(negative29=ma,positive40=mb,difference=ma-mb))


def verify():
    preflight()
    done=json.loads((OUT/'COMPLETED.json').read_text())
    for name,digest in done['files_sha256'].items():
        if sha(ROOT/name)!=digest:
            raise ValueError('Output changed: '+name)
    return done['verification']


def run():
    preflight()
    if (OUT/'COMPLETED.json').exists():
        raise ValueError('Closed precision round; --verify only')
    saved=pd.read_csv(ROOT/'artifacts/morning-recovery-anatomy/measurements.csv',float_precision='round_trip')
    gaps,_=frozen_groups();frame=saved[saved.day.isin(gaps)].copy()
    negative=set(frame[frame.first_quarter_status.eq('NEGATIVE')].day)
    assert len(negative)==29
    calendar=[r['day'] for r in json.loads((ROOT/'artifacts/raw-market/quality.json').read_text())]
    assert len(calendar)==454 and len(set(calendar))==454
    with forbid_scoring():
        active,sources=load_active();paths=extract_excursions(active,negative,frame)
        active2,_=load_active();replay=extract_excursions(active2,negative,frame)
    pd.testing.assert_frame_equal(paths,replay,check_exact=True)
    result=analyze(frame,calendar,paths)
    OUT.mkdir(parents=True,exist_ok=True)
    paths.to_csv(OUT/'excursions.csv',index=False,float_format='%.17g')
    replay.to_csv(OUT/'excursions-replay.csv',index=False,float_format='%.17g')
    assert sha(OUT/'excursions.csv')==sha(OUT/'excursions-replay.csv')
    verification=dict(existing_gap_days=69,negative_days=29,positive_days=40,source_files=sources,
        fresh_excursion_replay_identical=True,existing_following_returns_reproduced=True,
        exact45_post0945_bars=True,new_afternoon_runs=0,new_strategy_runs=0,new_pvalues=0,
        protected_archive_files=verify_candidate()['protected_archive_files'])
    dump(OUT/'summary.json',dict(status='EXPLORATORY_PRECISION_NOT_INDEPENDENT_VALIDATION',
        **result,verification=verification,protocol_sha256=sha(PROTOCOL)))
    names=['excursions.csv','excursions-replay.csv','summary.json']
    dump(OUT/'COMPLETED.json',dict(verification=verification,files_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in names}))
    preflight()
    print(json.dumps(verification,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group(required=True)
    m.add_argument('--register',action='store_true');m.add_argument('--run',action='store_true');m.add_argument('--verify',action='store_true');args=p.parse_args()
    if args.register:
        print(json.dumps(register(),indent=2))
    elif args.verify:
        print(json.dumps(verify(),indent=2))
    else:
        run()
