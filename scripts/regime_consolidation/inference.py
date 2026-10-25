"""Joint chronological two-month blocks, basic CIs and centered equal-tail p.

No block crosses the gap between the two source eras. No optimized block size.
"""
import numpy as np

REPS=20000
SEED=2026102507
ALPHA=.05
FAMILY=15


def holm(values):
    p=np.asarray(values,float)
    order=np.argsort(p,kind='stable')
    out=np.empty(len(p))
    out[order]=np.minimum(1.,np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]))
    return out


def sample_means(dates,matrix,seed=SEED,reps=REPS):
    matrix=np.asarray(matrix,float)
    if matrix.ndim!=2 or len(matrix)!=len(dates) or not np.isfinite(matrix).all():
        raise ValueError('Invalid daily panel')
    months=sorted({d[:7] for d in dates});n=len(months)
    if n<2:raise ValueError('Need at least two calendar months')
    sums=np.array([matrix[[d[:7]==m for d in dates]].sum(axis=0) for m in months])
    counts=np.array([sum(d[:7]==m for d in dates) for m in months])
    start=np.random.default_rng(seed).integers(0,n-1,size=(reps,int(np.ceil(n/2))))
    ix=(start[:,:,None]+np.arange(2)).reshape(reps,-1)[:,:n]
    means=sums[ix].sum(axis=1)/counts[ix].sum(axis=1)[:,None]
    return means,dict(days=len(dates),months=months,block_months=2,replications=reps,
                      first_month_inclusion=float((ix==0).sum()/reps),
                      last_month_inclusion=float((ix==n-1).sum()/reps))


def describe(observed,samples,n_days):
    observed=np.asarray(observed,float);samples=np.asarray(samples,float)
    centered=samples-observed
    lo,hi=np.quantile(centered,[ALPHA/2,1-ALPHA/2],axis=0)
    flo,fhi=np.quantile(centered,[ALPHA/(2*FAMILY),1-ALPHA/(2*FAMILY)],axis=0)
    reps=len(samples)
    upper=(1+(centered>=observed).sum(axis=0))/(reps+1)
    lower=(1+(centered<=observed).sum(axis=0))/(reps+1)
    p=np.minimum(1.,2*np.minimum(upper,lower))
    rows=[]
    for j,mu in enumerate(observed):
        ci=[float(mu-hi[j]),float(mu-lo[j])]
        family=[float(mu-fhi[j]),float(mu-flo[j])]
        rows.append(dict(mean_net_R_per_cash_day=float(mu),mean_ci95=ci,
                         expected_total_R_ci95=[v*n_days for v in ci],
                         mean_familywise95_bonf15=family,p_raw_two_sided=float(p[j]),
                         nominal_ci_strictly_positive=ci[0]>0,
                         simultaneous_ci_strictly_positive=family[0]>0))
    return rows


def joint(panels,seeds=(SEED,SEED+1),reps=REPS):
    """Exactly two eras. Combined keeps the original cash-day era weights."""
    if len(panels)!=2:raise ValueError('Two separate chronological eras required')
    results={};draws=[];observed=[];counts=[];metadata={}
    for i,(name,dates,matrix) in enumerate(panels):
        sample,meta=sample_means(dates,matrix,seeds[i],reps)
        mu=np.asarray(matrix).mean(axis=0)
        results[name]=describe(mu,sample,len(dates));draws.append(sample)
        observed.append(mu);counts.append(len(dates));metadata[name]=meta
    weights=np.array(counts)/sum(counts)
    pooled=draws[0]*weights[0]+draws[1]*weights[1]
    mu=observed[0]*weights[0]+observed[1]*weights[1]
    results['COMBINED']=describe(mu,pooled,sum(counts))
    order=[(b,j) for b in (*[p[0] for p in panels],'COMBINED') for j in range(len(results[b]))]
    if len(order)!=FAMILY:raise ValueError('Expected five unique objects by three periods')
    adjusted=holm([results[b][j]['p_raw_two_sided'] for b,j in order])
    for (b,j),p in zip(order,adjusted):
        results[b][j]['p_holm15']=float(p)
    return results,dict(eras=metadata,fixed_era_weights=weights.tolist(),seed=list(seeds),
                        combined_blocks_cross_era_gap=False)
