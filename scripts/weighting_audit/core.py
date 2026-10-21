"""Independent numerical implementation; imports no previous research engine."""
import itertools
import numpy as np

SIDES=['RECORD_HIGH','RECORD_LOW']
HORIZONS=['15m','60m','rth_close']
SCHEMES=['event','equal_day','past_count','first_record']


def daily_statistics(high,low,close,horizons=(15,60,'rth_close')):
    """Return day x side x horizon x scheme numerators/denominators.

    Values are signed log-price coordinates in bp. Never orient returns by side.
    Record mask is causal; only the equal_day denominator uses future counts.
    """
    high,low,close=[np.asarray(x,float) for x in [high,low,close]]
    if high.shape!=low.shape or high.shape!=close.shape or close.ndim!=2:
        raise ValueError('Require equal day-by-minute arrays')
    d,t=close.shape
    if not np.isfinite(np.stack([high,low,close])).all():raise ValueError('Nonfinite path')
    if (high<close).any() or (low>close).any() or (high<low).any():raise ValueError('Invalid bar envelope')
    masks=[]
    for prices,op in [(high,np.greater),(low,np.less)]:
        previous=np.maximum.accumulate(prices,axis=1) if op is np.greater else np.minimum.accumulate(prices,axis=1)
        mask=np.zeros((d,t),bool);mask[:,1:]=op(prices[:,1:],previous[:,:-1]);masks.append(mask)
    numerator=np.zeros((d,2,len(horizons),4));denominator=np.zeros_like(numerator)
    for side,record in enumerate(masks):
        rank_full=np.cumsum(record,axis=1)
        past_full=np.divide(record,rank_full,out=np.zeros_like(close),where=rank_full>0)
        first_full=record&(rank_full==1)
        for hi,h in enumerate(horizons):
            end=t-1 if h=='rth_close' else int(h)
            if h=='rth_close':
                mask=record[:,:-1];outcome=close[:,-1,None]-close[:,:-1]
            else:
                if end<=0 or end>=t:raise ValueError('Invalid horizon')
                mask=record[:,:-end];outcome=close[:,end:]-close[:,:-end]
            count=mask.sum(axis=1);total=np.where(mask,outcome,0.).sum(axis=1)
            numerator[:,side,hi,0]=total;denominator[:,side,hi,0]=count
            numerator[:,side,hi,1]=np.divide(total,count,out=np.zeros(d),where=count>0)
            denominator[:,side,hi,1]=count>0
            past=past_full[:,:mask.shape[1]]
            numerator[:,side,hi,2]=(past*outcome).sum(axis=1)
            denominator[:,side,hi,2]=past.sum(axis=1)
            first=first_full[:,:mask.shape[1]]
            numerator[:,side,hi,3]=np.where(first,outcome,0.).sum(axis=1)
            denominator[:,side,hi,3]=count>0
    return numerator,denominator


def estimate(numerator,denominator):
    a=np.asarray(numerator).sum(axis=0);b=np.asarray(denominator).sum(axis=0)
    return np.divide(a,b,out=np.full_like(a,np.nan,dtype=float),where=b>0)


def weighting_decomposition(numerator,denominator):
    rows=[]
    for side in range(2):
        for h in range(numerator.shape[2]):
            counts=denominator[:,side,h,0];good=counts>0
            n=counts[good];means=numerator[good,side,h,1]
            cov=float(np.mean((n-n.mean())*(means-means.mean())))
            event=float(numerator[good,side,h,0].sum()/n.sum());day=float(means.mean())
            scale=float(n.mean());residual=event-day-cov/scale
            rows.append(dict(side=SIDES[side],horizon=HORIZONS[h],days=len(n),events=int(n.sum()),
                event_mean=event,equal_day_mean=day,event_minus_day=event-day,
                population_cov_count_mean=cov,mean_event_count=scale,cov_over_mean_count=cov/scale,
                identity_residual=float(residual),count_min=int(n.min()),count_median=float(np.median(n)),
                count_p95=float(np.quantile(n,.95)),count_max=int(n.max())))
    return rows


def enumerate_symmetric_paths(steps=8):
    """Scalar oracle, deliberately independent of vectorized record extraction."""
    paths=list(itertools.product([-1.,1.],repeat=steps));rows=[]
    for side in [1,-1]:
        for horizon in [1,'rth_close']:
            ns=[];ds=[]
            for increments in paths:
                price=[0.]
                for change in increments:price.append(price[-1]+change)
                hi=[max(price[i],price[i+1]) for i in range(steps)]
                lo=[min(price[i],price[i+1]) for i in range(steps)]
                known=hi[0] if side==1 else lo[0];outcomes=[]
                for i in range(1,steps):
                    value=hi[i] if side==1 else lo[i]
                    record=value>known if side==1 else value<known
                    known=max(known,value) if side==1 else min(known,value)
                    j=steps-1 if horizon=='rth_close' else i+1
                    if record and j<steps and j>i:outcomes.append(price[j+1]-price[i+1])
                count=len(outcomes)
                if count:
                    ns.append([sum(outcomes),sum(outcomes)/count,sum(v/(k+1) for k,v in enumerate(outcomes)),outcomes[0]])
                    ds.append([count,1.,sum(1/(k+1) for k in range(count)),1.])
                else:ns.append([0.]*4);ds.append([0.]*4)
            theta=estimate(np.asarray(ns),np.asarray(ds))
            rows.append(dict(side='RECORD_HIGH' if side==1 else 'RECORD_LOW',horizon=str(horizon),
                equiprobable_paths=len(paths),event_days=int(np.asarray(ds)[:,1].sum()),
                **{s:float(theta[k]) for k,s in enumerate(SCHEMES)}))
    return rows


def circular_weights(n,reps=4000,length=5,seed=20261022):
    rng=np.random.default_rng(seed)
    start=rng.integers(0,n,(reps,(n+length-1)//length))
    ids=((start[:,:,None]+np.arange(length))%n).reshape(reps,-1)[:,:n]
    w=np.zeros((reps,n),np.int32)
    for row in range(reps):w[row]=np.bincount(ids[row],minlength=n)
    return w


def bootstrap(numerator,denominator,weights):
    shape=numerator.shape[1:]
    num=weights@numerator.reshape(len(numerator),-1);den=weights@denominator.reshape(len(denominator),-1)
    values=np.divide(num,den,out=np.full_like(num,np.nan),where=den>0)
    return values.reshape((len(weights),)+shape)


def holm(ps):
    pairs=sorted((1. if p is None else float(p),i) for i,p in enumerate(ps));result=[1.]*len(ps);last=0.
    for rank,(p,i) in enumerate(pairs):last=max(last,p*(len(ps)-rank));result[i]=min(1.,last)
    return result


def zero_test(theta,replicates):
    b=np.asarray(replicates);return float((1+np.count_nonzero(np.abs(b-theta)>=abs(theta)))/(len(b)+1))


def wilson(successes,n,z=1.959963984540054):
    p=successes/n;den=1+z*z/n;center=(p+z*z/(2*n))/den
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(max(0,center-half)),float(min(1,center+half))]


def mc_p(observed,simulated):
    x=np.asarray(simulated);x=x[np.isfinite(x)];n=len(x)
    low=int(np.count_nonzero(x<=observed));high=int(np.count_nonzero(x>=observed));tail=min(low,high)
    p=min(1.,2*(tail+1)/(n+1))
    precision=wilson(tail,n)
    return dict(p_value=float(p),smaller_tail_count=tail,experiments=n,
                mc_precision_95=[min(1.,2*v) for v in precision],
                minimum_two_sided_p=2/(n+1))


def simulated_path(name,rng,shapes,constant_sigma,clock_sigma,day_scales,substeps=8):
    d,t=shapes['close'].shape
    if name=='conditional_bar_reflections':
        sign=rng.integers(0,2,size=(d,t))*2-1
        increment=shapes['close']*sign
        close=np.cumsum(increment,axis=1);previous=np.c_[np.zeros(d),close[:,:-1]]
        high=previous+np.where(sign>0,shapes['high'],-shapes['low'])
        low=previous+np.where(sign>0,shapes['low'],-shapes['high'])
        return high,low,close
    if name not in ['gaussian_iid','gaussian_clock_scale']:raise ValueError('Unknown locked null')
    noise=rng.standard_normal((d,t,substeps))
    if name=='gaussian_iid':noise*=constant_sigma/np.sqrt(substeps)
    else:
        scales=rng.choice(day_scales,size=d)
        noise*=scales[:,None,None]*clock_sigma[None,:,None]/np.sqrt(substeps)
    walk=np.cumsum(noise.reshape(d,-1),axis=1).reshape(d,t,substeps)
    close=walk[:,:,-1];previous=np.c_[np.zeros(d),close[:,:-1]]
    high=np.maximum(walk.max(axis=2),previous);low=np.minimum(walk.min(axis=2),previous)
    return high,low,close
