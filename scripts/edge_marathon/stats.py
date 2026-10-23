"""Fixed inference and full risk description. No new calibration studies."""
import numpy as np
import pandas as pd
from scipy.stats import t
from scripts.afternoon_inference_round import partition


def holm(values):
    values=np.asarray(values,float);order=np.argsort(values,kind='stable');out=np.empty_like(values);prev=0.
    for j,k in enumerate(order):
        prev=max(prev,min(1.,(len(values)-j)*values[k]));out[k]=prev
    return list(map(float,out))


def quantiles(x):
    x=np.asarray(x,float)
    return dict(zip(['p10','p25','median','p75','p90','p95'],map(float,np.quantile(x,[.1,.25,.5,.75,.9,.95])))) if len(x) else None


def inference(trades,calendar,seed=20261022061,reps=10000):
    """Daily clusters; zeros are selection influences, not zero-trade returns.

    MBB5 on full calendar: ratio total outcome / selected-count. Sign flip
    is exact enumeration for<=16 nonzero daily clusters, else Monte Carlo
    99,999 with plus-one correction. Conditional sign symmetry/exchangeability
    is assumed, not established by a small p. Group8 gap20 variance125 is
    also always shown, with unchanged min8/block+120 total information gate.
    """
    lookup={d:i for i,d in enumerate(calendar)}
    sums=np.zeros(len(calendar));counts=np.zeros(len(calendar))
    for r in trades:
        i=lookup[r['day']];sums[i]+=r['net_points'];counts[i]+=1
    total=int(counts.sum());days=int((counts>0).sum())
    result=dict(events=total,unique_days=days,bootstrap95=None,signflip_p=1.,signflip_method='NO_EVENTS',
        conservative_p=1.,conservative_status='DATA_INSUFFICIENT',
        caveat='Sign symmetry is assumed for sign-flip; MBB5 coverage depends on weak dependence. Finite synthetic calibration does not certify arbitrary new model families.')
    if total<2:return result
    rng=np.random.default_rng(seed)
    if len(calendar)>=5:
        blocks=int(np.ceil(len(calendar)/5));means=[]
        for off in range(0,reps,200):
            starts=rng.integers(0,len(calendar)-4,size=(min(200,reps-off),blocks))
            ix=(starts[:,:,None]+np.arange(5)[None,None,:]).reshape(len(starts),-1)[:,:len(calendar)]
            num=sums[ix].sum(axis=1);den=counts[ix].sum(axis=1)
            means.extend((num[den>0]/den[den>0]).tolist())
        if means:result['bootstrap95']=list(map(float,np.quantile(means,[.025,.975])))
    daily=sums[counts>0];observed=abs(daily.sum());n=len(daily)
    tolerance=1e-9
    if n<=16:
        bits=(np.arange(2**n,dtype=np.uint64)[:,None]>>np.arange(n,dtype=np.uint64)[None,:])&1
        perm=(bits.astype(float)*2-1)@daily
        p=float((abs(perm)>=observed-tolerance).mean());method=f'EXACT_ENUMERATION_{2**n}_UNDER_SIGN_SYMMETRY'
    else:
        hits=0;draws=99999
        # Fixed chunks and local seed, not a choice after seeing significance.
        for off in range(0,draws,1000):
            signs=rng.integers(0,2,size=(min(1000,draws-off),n),dtype=np.int8)*2-1
            hits+=int((abs(signs@daily)>=observed-tolerance).sum())
        p=(hits+1)/(draws+1);method='MONTE_CARLO_99999_PLUS_ONE_UNDER_SIGN_SYMMETRY'
    result.update(signflip_p=p,signflip_method=method)
    if len(calendar)>=156:
        groups,indexes,width=partition(len(calendar))
        a=np.array([sums[b].mean() for b in groups]);b=np.array([counts[q].sum() for q in groups])
        result['conservative_group_counts']=list(map(int,b));result['conservative_scored_events']=int(b.sum())
        if b.min()>=8 and b.sum()>=120:
            se=a.std(ddof=1)/np.sqrt(8)*np.sqrt(1.25)
            if se>0:
                result.update(conservative_p=float(2*t.sf(abs(a.mean()/se),7)),conservative_status='EVALUABLE_LIMITED_SCOPE')
    return result


def metrics(trades,calendar):
    n=len(trades)
    if not n:return dict(trades=0,net_points=0.,net_dollars=0.,mean_net=None,profit_factor=None,
                         winrate=None,positive_quarter_fraction=None,quarters=0,drawdown=None)
    x=np.array([r['net_points'] for r in trades]);gross=np.array([r['gross_points'] for r in trades]);eq=np.r_[0,x.cumsum()]
    daily={d:0. for d in calendar}
    for r in trades:daily[r['day']]+=r['net_points']
    dx=np.asarray(list(daily.values()));down=np.sqrt(np.mean(np.minimum(dx,0)**2));sd=dx.std(ddof=1) if len(dx)>1 else 0.
    quarters={}
    for r in trades:
        q=str(pd.Period(r['day'],freq='Q'));quarters.setdefault(q,[]).append(r['net_points'])
    byq={q:dict(trades=len(v),net_points=float(sum(v)),mean_net=float(np.mean(v))) for q,v in quarters.items()}
    bymonth={}
    for r in trades:
        m=r['day'][:7];bymonth.setdefault(m,[]).append(r['net_points'])
    streak=maximum=0
    for v in x:
        streak=streak+1 if v<0 else 0;maximum=max(streak,maximum)
    net=float(x.sum());positive=x[x>0];loss=-x[x<0].sum()
    loo=(net-x)/(n-1) if n>1 else np.array([])
    loq=[(net-sum(v))/(n-len(v)) for v in quarters.values() if len(v)<n]
    sorted_best=np.sort(positive)[-3:];mfe=[r['mfe_points'] for r in trades];mae=[r['mae_points'] for r in trades]
    return dict(trades=n,gross_points=float(gross.sum()),net_points=net,net_dollars=net*20,
        mean_net=float(x.mean()),median_net=float(np.median(x)),winrate=float((x>0).mean()),
        profit_factor=float(positive.sum()/loss) if loss else None,
        drawdown=float((np.maximum.accumulate(eq)-eq).max()),worst_day=float(dx.min()),
        max_consecutive_losses=maximum,daily_sharpe=float(dx.mean()/sd*np.sqrt(252)) if sd else None,
        daily_sortino=float(dx.mean()/down*np.sqrt(252)) if down else None,
        risk_ratio_caveat='One-contract daily point-PnL ratios, no invested-capital return series, no claim of annualized dollar profits',
        top3_share_of_net=float(sorted_best.sum()/net) if net>0 else None,
        net_without_top3=float(net-sorted_best.sum()),
        leave_one_day_out_mean=[float(loo.min()),float(loo.max())] if len(loo) else None,
        leave_one_quarter_out_mean=[float(min(loq)),float(max(loq))] if loq else None,
        quarters=len(quarters),positive_quarter_fraction=sum(sum(v)>0 for v in quarters.values())/len(quarters),
        quarterly=byq,monthly={m:dict(trades=len(v),net_points=float(sum(v))) for m,v in bymonth.items()},
        long_short={str(d):dict(trades=sum(r['direction']==d for r in trades),
            net_points=float(sum(r['net_points'] for r in trades if r['direction']==d))) for d in [-1,1]},
        mfe=quantiles(mfe),mae=quantiles(mae),mae_atr=quantiles([r['mae_points']/r['atr'] for r in trades if r.get('atr') and r['atr']>0]),
        slippage=[dict(extra_ticks_per_leg=t,cost_dollars=24.5+10*t,net_points=float(net-.5*t*n),mean_net=float(x.mean()-.5*t)) for t in [0,1,2]])
