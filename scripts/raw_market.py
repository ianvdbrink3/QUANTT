"""Strategy-free descriptive OHLCV research. No strategy simulator invocation."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.oos_preparation.adapter import Calendar,at,sha
from scripts.oos_preparation.year import load_registered,dump,forbid_scoring
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation
from scripts.archive_experiments import verify_archive

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'research/raw-market-protocol.json'
TYPES=['RECORD_HIGH','RECORD_LOW','PDH_TOUCH','PDL_TOUCH']
HORIZONS=['15m','60m','rth_close']


def distribution(x):
    x=np.asarray(x,float);x=x[np.isfinite(x)]
    if not len(x):return dict(n=0,mean=None,median=None,p05=None,p25=None,p75=None,p95=None,positive_fraction=None)
    q=np.quantile(x,[.05,.25,.5,.75,.95])
    return dict(n=len(x),mean=float(x.mean()),median=float(q[2]),p05=float(q[0]),
                p25=float(q[1]),p75=float(q[3]),p95=float(q[4]),positive_fraction=float((x>0).mean()))


def block_weights(n,reps=4000,block=5,seed=20261022):
    rng=np.random.default_rng(seed)
    starts=rng.integers(n,size=(reps,int(np.ceil(n/block))))
    ix=((starts[:,:,None]+np.arange(block))%n).reshape(reps,-1)[:,:n]
    weights=np.zeros((reps,n),dtype=np.int32)
    np.add.at(weights,(np.arange(reps)[:,None],ix),1)
    return weights


def inference(theta,replicates):
    b=np.asarray(replicates,float);b=b[np.isfinite(b)]
    if theta is None or not np.isfinite(theta) or len(b)<100:
        return dict(ci_low=None,ci_high=None,p_value=None,valid_bootstrap_replicates=len(b))
    return dict(ci_low=float(np.quantile(b,.025)),ci_high=float(np.quantile(b,.975)),
        p_value=float((1+(np.abs(b-theta)>=abs(theta)).sum())/(len(b)+1)),valid_bootstrap_replicates=len(b))


def summarize(x,day_ids,weights):
    x=np.asarray(x,float);di=np.asarray(day_ids,int);good=np.isfinite(x);x=x[good];di=di[good]
    result=distribution(x);result['days']=len(np.unique(di));n=weights.shape[1]
    if result['days']<20:
        return dict(result,mean_ci_low=None,mean_ci_high=None,median_ci_low=None,median_ci_high=None,p_value=None)
    sums=np.bincount(di,weights=x,minlength=n);counts=np.bincount(di,minlength=n)
    den=weights@counts;num=weights@sums
    boot=np.divide(num,den,out=np.full(len(weights),np.nan),where=den>0)
    inf=inference(result['mean'],boot)
    result.update(mean_ci_low=inf['ci_low'],mean_ci_high=inf['ci_high'],p_value=inf['p_value'],
                  valid_bootstrap_replicates=inf['valid_bootstrap_replicates'])
    order=np.argsort(x);sx=x[order];sd=di[order];medians=[]
    for start in range(0,len(weights),64):
        cw=np.cumsum(weights[start:start+64,sd],axis=1);total=cw[:,-1]
        low=(total-1)//2;high=total//2
        i=(cw>low[:,None]).argmax(axis=1);j=(cw>high[:,None]).argmax(axis=1)
        medians.extend(np.where(total>0,(sx[i]+sx[j])/2,np.nan))
    m=np.asarray(medians);m=m[np.isfinite(m)]
    result.update(median_ci_low=float(np.quantile(m,.025)),median_ci_high=float(np.quantile(m,.975)))
    return result


def correlation(x,y,day_ids,weights):
    x,y,di=np.asarray(x,float),np.asarray(y,float),np.asarray(day_ids,int)
    good=np.isfinite(x)&np.isfinite(y);x,y,di=x[good],y[good],di[good]
    n=weights.shape[1]
    sufficient=np.stack([np.bincount(di,weights=z,minlength=n) for z in
                         [np.ones(len(x)),x,y,x*x,y*y,x*y]],axis=1)
    def coeff(s):
        nn,sx,sy,sxx,syy,sxy=np.asarray(s).T
        cov=nn*sxy-sx*sy;den=np.sqrt(np.maximum(0,nn*sxx-sx*sx)*np.maximum(0,nn*syy-sy*sy))
        return np.clip(np.divide(cov,den,out=np.full_like(cov,np.nan,dtype=float),where=den>0),-1,1)
    theta=float(coeff(sufficient.sum(axis=0))) if len(x) else np.nan
    nd=len(np.unique(di));inf=inference(theta,coeff(weights@sufficient)) if nd>=20 else inference(None,[])
    return dict(pairs=len(x),days=nd,coefficient=theta if np.isfinite(theta) else None,**inf)


def holm(values):
    p=np.asarray([v if v is not None else 1. for v in values]);order=np.argsort(p)
    a=np.maximum.accumulate(p[order]*(len(p)-np.arange(len(p))));out=np.ones(len(p));out[order]=np.minimum(1,a)
    return out.tolist()


def expected_rth(calendar,day):
    ix=calendar.grid(day)
    return ix[(ix>=at(day,'09:30'))&(ix<at(day,'16:00'))]


def event_rows(day,g,pdh=None,pdl=None):
    """Events are known at a COMPLETED bar; outcomes never start at touch price."""
    rows=[];high=g.high.to_numpy();low=g.low.to_numpy();close=g.close.to_numpy();n=len(g)
    previous_hi=np.maximum.accumulate(high);previous_lo=np.minimum.accumulate(low)
    events=[('RECORD_HIGH',i) for i in range(1,n) if high[i]>previous_hi[i-1]]
    events += [('RECORD_LOW',i) for i in range(1,n) if low[i]<previous_lo[i-1]]
    for label,level in [('PDH_TOUCH',pdh),('PDL_TOUCH',pdl)]:
        if level is None or not np.isfinite(level):continue
        hits=np.flatnonzero((low<=level)&(high>=level))
        if len(hits):events.append((label,int(hits[0])))
    for label,i in events:
        for horizon in HORIZONS:
            j=n-1 if horizon=='rth_close' else i+int(horizon[:-1])
            if j>=n or j<=i:continue
            if (g.index[j]-g.index[i])!=pd.Timedelta(minutes=j-i):raise ValueError('Noncontiguous event horizon')
            rows.append(dict(day=day,event=label,horizon=horizon,bar_utc=g.index[i].isoformat(),
                event_known_utc=(g.index[i]+pd.Timedelta(minutes=1)).isoformat(),minutes_to_endpoint=j-i,
                return_bps=float(10000*np.log(close[j]/close[i])),return_points=float(close[j]-close[i])))
    counts={t:sum(label==t for label,_ in events) for t in TYPES}
    return rows,counts


def measure(full,schedule,calendar,start,end):
    active=select_active(full,schedule)
    days=[d for d in pd.bdate_range(start,end).strftime('%Y-%m-%d') if len(calendar.grid(d))]
    lookup={(c,d):g for (c,d),g in full.groupby(['contract','trade_date'],sort=False)}
    selected={d:g for d,g in active.groupby('trade_date')};slots=[];events=[];quality=[];daily=[];pairs={h:[] for h in [5,15,30,60]}
    for k,day in enumerate(days):
        raw=selected.get(day,full.iloc[:0]);contract=raw.contract.iloc[0] if len(raw) else None
        rth=raw.loc[(raw.index>=at(day,'09:30'))&(raw.index<at(day,'16:00'))]
        exp=expected_rth(calendar,day);boundary=at(day,'09:30')-pd.Timedelta(minutes=1)
        reasons=[]
        if len(exp)!=390:reasons.append('early_close_or_no_full_RTH')
        if not rth.index.equals(exp):reasons.append('missing_or_unexpected_RTH_minutes')
        if boundary not in raw.index:reasons.append('missing_09_29_boundary_close')
        q=dict(day=day,contract=contract,included=not reasons,reasons=reasons,observed_RTH=len(rth),expected_RTH=len(exp))
        quality.append(q)
        if reasons:continue
        close=rth.close.to_numpy();base=float(raw.at[boundary,'close']);r=np.log(close/np.r_[base,close[:-1]])
        for b in range(13):
            sl=rth.iloc[b*30:(b+1)*30];p0=base if b==0 else close[b*30-1];p1=close[(b+1)*30-1]
            slots.append(dict(day=day,slot=b,clock=sl.index[0].tz_convert('America/New_York').strftime('%H:%M'),
                return_bps=float(10000*np.log(p1/p0)),return_points=float(p1-p0),
                range_bps=float(10000*np.log(sl.high.max()/sl.low.min())),range_points=float(sl.high.max()-sl.low.min()),
                realized_rv_bps=float(10000*np.sqrt(np.sum(r[b*30:(b+1)*30]**2))),
                volume_share=float(sl.volume.sum()/rth.volume.sum())))
        for h in pairs:
            endpoints=close[np.arange(h-1,390,h)];returns=10000*np.log(endpoints/np.r_[base,endpoints[:-1]])
            pairs[h].extend((day,float(a),float(b)) for a,b in zip(returns[:-1],returns[1:]))
        prev=days[k-1] if k else None;pg=lookup.get((contract,prev)) if prev else None
        prior=None
        if pg is not None:
            pr=pg.loc[pg.index.isin(expected_rth(calendar,prev))]
            if len(pr)>0 and pr.index.equals(expected_rth(calendar,prev)):prior=pr
        q['prior_same_contract_RTH_complete']=prior is not None
        q['previous_scheduled_day']=prev
        q['prior_same_contract_close_utc']=prior.index[-1].isoformat() if prior is not None else None
        overnight=10000*np.log(float(rth.open.iloc[0])/float(prior.close.iloc[-1])) if prior is not None else np.nan
        cc=10000*np.log(close[-1]/float(prior.close.iloc[-1])) if prior is not None else np.nan
        daily.append(dict(day=day,previous_scheduled_day=prev,close_close_bps=float(cc),overnight_bps=float(overnight),
                          rth_open_close_bps=float(10000*np.log(close[-1]/float(rth.open.iloc[0])))))
        ev,counts=event_rows(day,rth,float(prior.high.max()) if prior is not None else None,
                            float(prior.low.min()) if prior is not None else None)
        events.extend(ev);q['event_counts_before_horizon_censoring']=counts
    return days,pd.DataFrame(slots),pd.DataFrame(events),pd.DataFrame(daily),pairs,quality


def calculate(days,slots,events,daily,pairs,protocol):
    ids={d:i for i,d in enumerate(days)};p=protocol['uncertainty']
    weights=block_weights(len(days),p['replicates'],p['block_sessions'],p['seed'])
    tests=[];half=[]
    for slot,g in slots.groupby('slot',sort=True):
        row=dict(slot=int(slot),clock=g.clock.iloc[0])
        for metric in ['return_bps','return_points','range_bps','range_points','realized_rv_bps','volume_share']:
            row[metric]=summarize(g[metric],g.day.map(ids),weights)
            if metric!='return_bps':row[metric].pop('p_value',None)
        tests.append(('half_hour:'+row['clock'],row['return_bps']));half.append(row)
    corrs=[]
    for h,values in pairs.items():
        a=pd.DataFrame(values,columns=['day','x','y']);c=correlation(a.x,a.y,a.day.map(ids),weights)
        row=dict(name=f'intraday_{h}m_lag1',**c);corrs.append(row);tests.append((row['name'],row))
    dd=daily.set_index('day');dc=[]
    for row in daily.itertuples():
        if row.previous_scheduled_day in dd.index:
            prev=dd.loc[row.previous_scheduled_day]
            dc.append((row.day,float(prev.close_close_bps),float(row.close_close_bps)))
    a=pd.DataFrame(dc,columns=['day','x','y'])
    row=dict(name='daily_RTH_close_close_lag1',**correlation(a.x,a.y,a.day.map(ids),weights))
    corrs.append(row);tests.append((row['name'],row))
    row=dict(name='overnight_vs_same_day_RTH',**correlation(daily.overnight_bps,daily.rth_open_close_bps,daily.day.map(ids),weights))
    corrs.append(row);tests.append((row['name'],row))
    conditional=[]
    for label in TYPES:
        for horizon in HORIZONS:
            g=events[events.event.eq(label)&events.horizon.eq(horizon)]
            r=summarize(g.return_bps,g.day.map(ids),weights)
            byday=g.groupby('day').return_bps.mean()
            db=summarize(byday.to_numpy(),[ids[d] for d in byday.index],weights)
            points=distribution(g.return_points);minutes=distribution(g.minutes_to_endpoint)
            row=dict(event=label,horizon=horizon,event_weighted_bps=r,equal_event_day_mean_bps=db,
                     points=points,minutes_to_endpoint=minutes)
            conditional.append(row)
            tests.extend([(label+':'+horizon+':event_weighted',r),(label+':'+horizon+':day_balanced',db)])
    if len(tests)!=43:raise ValueError('Predefined 43-test family changed')
    corrected=holm([r.get('p_value') for _,r in tests]);test_rows=[]
    for (name,row),adj in zip(tests,corrected):
        row['p_holm_global43']=adj;test_rows.append(dict(test=name,p_value=row.get('p_value'),p_holm_global43=adj))
    return dict(half_hours=half,correlations=corrs,events=conditional,tests=test_rows)


def run():
    print('1/4 Verify archive, frozen source identities and fixed definitions',flush=True)
    archive=verify_archive();protocol=json.loads(PROTOCOL.read_text())
    with forbid_scoring():
        full,manifest,reconciliation=load_registered()
        calendar=Calendar(json.loads((ROOT/'research/oos-year-calendar.json').read_text()))
        old=json.loads((ROOT/'research/holdout-protocol.json').read_text())
        year=json.loads((ROOT/'research/oos-year-rollovers.json').read_text())
        schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
        schedule += [Activation(r['to'],r['effective_session']) for r in old['rollovers']+year['rollovers']]
        print('2/4 Raw session windows and observed extrema only; scoring blocked',flush=True)
        days,slots,events,daily,pairs,quality=measure(full,schedule,calendar,*protocol['period'])
        print('3/4 Whole-day block uncertainty and predefined Holm43 correction',flush=True)
        results=calculate(days,slots,events,daily,pairs,protocol)
    out=ROOT/'artifacts/raw-market';out.mkdir(parents=True,exist_ok=True)
    for name,df in [('half-hours',slots),('events',events),('daily',daily)]:df.to_csv(out/(name+'.csv'),index=False)
    dump(out/'quality.json',quality)
    summary=dict(status='EXPLORATORY_RAW_MARKET_ONLY',period=protocol['period'],protocol=protocol,
        protocol_sha256=sha(PROTOCOL),source_register_sha256=sha(ROOT/'research/oos-year-sources.json'),
        source_files=len(manifest['sources'])+len(manifest['warmup_sources']),reconciliation=reconciliation,
        scheduled_sessions=len(days),complete_RTH_and_boundary_days=sum(q['included'] for q in quality),
        excluded_days=[q for q in quality if not q['included']],
        prior_same_contract_days=sum(q.get('prior_same_contract_RTH_complete',False) for q in quality),
        raw_event_observations=len(events),hypothesis_tests=43,archive=archive,
        private_files_sha256={x.name:sha(x) for x in sorted(out.iterdir()) if x.name in ['half-hours.csv','events.csv','daily.csv','quality.json']},
        strategy_signals_computed=False,entries_stops_targets_used=False,**results)
    dump(out/'summary.json',summary);dump(ROOT/'public/data/research-raw-market.json',summary)
    dump(ROOT/'research/raw-market-verification.json',dict(protocol_sha256=sha(PROTOCOL),
        result_sha256=sha(out/'summary.json'),private_files_sha256=summary['private_files_sha256'],
        strategy_functions_runtime_blocked=True))
    print('4/4 Aggregates written; no model, filter, stop or target designed',flush=True)


if __name__=='__main__':run()
