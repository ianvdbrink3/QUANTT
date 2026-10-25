import numpy as np
import pandas as pd
from scripts.regime_consolidation.inference import sample_means,holm

PERIODS=('2019_2021','2024_2026','COMBINED')
SEEDS=(2026102511,2026102512)
REPS=20000
FAMILY=9  # six absolute portfolio tests and three UNIQUE paired deltas


def key(t):return t['block'],t['day'],t['entry_time']


def split_baseline(rows,B):
    ids={key(t) for t in B};removed=[t for t in rows if key(t) in ids]
    if len(removed)!=len(B) or {key(t) for t in removed}!=ids:
        raise ValueError('Baseline does not contain exactly frozen B')
    return [t for t in rows if key(t) not in ids]


def daily(rows,dates):
    out={d:0. for d in dates}
    for t in rows:out[t['exit_day']]+=t['net_R']
    return np.asarray(list(out.values()))


def overlap(a,b):
    intersections=[]
    for x in a:
        for y in b:
            lo=max(pd.Timestamp(x['entry_time']),pd.Timestamp(y['entry_time']))
            hi=min(pd.Timestamp(x['exit_time']),pd.Timestamp(y['exit_time']))
            if lo<hi:intersections.append(dict(a_day=x['day'],b_day=y['day'],minutes=(hi-lo).total_seconds()/60))
    return dict(overlap_pairs=len(intersections),overlap_minutes=sum(r['minutes'] for r in intersections))


def describe(mu,samples,n):
    error=np.asarray(samples)-mu;lo,hi=np.quantile(error,[.025,.975])
    p=min(1.,2*min((1+np.count_nonzero(error>=mu))/(len(error)+1),(1+np.count_nonzero(error<=mu))/(len(error)+1)))
    flo,fhi=np.quantile(error,[.05/(2*FAMILY),1-.05/(2*FAMILY)])
    return dict(mean_ATR_R_per_cash_day=float(mu),mean_ci95=[float(mu-hi),float(mu-lo)],
                expected_total_ATR_R_ci95=[float((mu-hi)*n),float((mu-lo)*n)],
                expected_total_ATR_R_familywise95_bonf9=[float((mu-fhi)*n),float((mu-flo)*n)],p_raw_two_sided=float(p))


def inference(panels):
    """Columns S1old,S2old,S1new,S2new. Same joint month-block draws.

    The paired difference must be numerically identical for both replacements;
    do not pretend it is two independent pieces of supporting evidence.
    """
    draws=[];means=[];counts=[];meta={}
    for i,(block,dates,values) in enumerate(panels):
        mat=np.asarray(values,float)
        if mat.shape!=(len(dates),4):raise ValueError('Four exact portfolio panels required')
        np.testing.assert_allclose(mat[:,2]-mat[:,0],mat[:,3]-mat[:,1],atol=1e-12,rtol=0)
        sample,m=sample_means(dates,mat,SEEDS[i],REPS)
        draws.append(sample);means.append(mat.mean(axis=0));counts.append(len(dates));meta[block]=m
    weights=np.asarray(counts)/sum(counts)
    draws.append(draws[0]*weights[0]+draws[1]*weights[1]);means.append(means[0]*weights[0]+means[1]*weights[1]);counts.append(sum(counts))
    results={};refs=[];raw=[]
    for b,mu,draw,n in zip(PERIODS,means,draws,counts):
        rows={name:describe(mu[j],draw[:,j],n) for name,j in (('S1_JUDAS',2),('S2_JUDAS',3))}
        rows['JUDAS_MINUS_B']=describe(mu[2]-mu[0],draw[:,2]-draw[:,0],n)
        np.testing.assert_allclose(draw[:,2]-draw[:,0],draw[:,3]-draw[:,1],atol=1e-12,rtol=0)
        results[b]=rows
        for name,row in rows.items():refs.append((b,name));raw.append(row['p_raw_two_sided'])
    assert len(raw)==9
    for (b,name),p in zip(refs,holm(raw)):results[b][name]['p_holm9']=float(p)
    return results,dict(replications=REPS,seeds=SEEDS,block_months=2,unique_tests=9,eras=meta,
                        paired_differences_identical=True,combined_fixed_era_weights=weights.tolist(),cross_era_blocks=False)
