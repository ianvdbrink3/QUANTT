"""Fixed daily accounting and the registered joint two-month bootstrap."""
import numpy as np
import pandas as pd

from scripts.edge_marathon.stats import holm, quantiles
from scripts.month_turn_audit import curve_drawdown
from scripts.survivor_portfolio import bootstrap, marked_curve

MODELS=('TOM_RTH','COMPRESSED_BREAK5','SWEEP_REV_1200','PORTFOLIO_EQUAL_THIRD')
SEED=20261022311
REPS=10000


def point_path(trades,prices,weights):
    """Same entry/close marking as frozen ATR path, no stops or targets."""
    path=np.zeros(391)
    for trade,weight in zip(trades,weights):
        a,b=trade['entry'],trade['end']
        path[a:]-=1.225*weight
        moves=trade['direction']*(prices['close'][a:b]-trade['entry_price'])*weight
        path[a+1:b+1]+=moves
        path[b+1:]+=moves[-1]
    return path


def intervals(dates,matrix,reps=REPS,seed=SEED):
    """Exact registered bootstrap, plus conservative simultaneous CI bands.

    Same draws for points/R, all four objects and both variants. Nominal
    95% CIs are NOT Holm-adjusted. Bonferroni4 98.75% marginal intervals give
    a separate approximate familywise95% interval set, under bootstrap validity.
    """
    result=bootstrap(dates,matrix,seed=seed,reps=reps)
    months=sorted({d[:7] for d in dates});n=len(months)
    if n<2:raise ValueError('At least two months required')
    sums=np.array([matrix[[d[:7]==m for d in dates]].sum(axis=0) for m in months])
    counts=np.array([sum(d[:7]==m for d in dates) for m in months])
    start=np.random.default_rng(seed).integers(0,n-1,size=(reps,int(np.ceil(n/2))))
    ix=(start[:,:,None]+np.arange(2)).reshape(reps,-1)[:,:n]
    means=sums[ix].sum(axis=1)/counts[ix].sum(axis=1)[:,None]
    for j,row in enumerate(result):
        # Independent formula check against the reused frozen implementation.
        np.testing.assert_array_equal(np.quantile(means[:,j],[.025,.975]),row['mean_R_ci95'])
        row['mean_familywise95_bonf4']=list(map(float,np.quantile(means[:,j],[.05/8,1-.05/8])))
    return result


def describe(daily,trades,marked,unit,weights):
    x=np.asarray(daily,float);active=np.abs(x)>1e-12
    positive=x[x>0];loss=-x[x<0].sum();sd=x.std(ddof=1)
    values=np.array([r['net_points']/(r['atr'] if unit=='ATR' else 1)*w for r,w in zip(trades,weights)])
    cost=sum(1.225/(r['atr'] if unit=='ATR' else 1)*w for r,w in zip(trades,weights))
    np.testing.assert_allclose(values.sum(),x.sum(),rtol=0,atol=1e-9)
    return dict(total=float(x.sum()),mean_per_evaluation_day=float(x.mean()),
        mean_per_active_day=float(x[active].mean()) if active.any() else None,
        median_active_day=float(np.median(x[active])) if active.any() else None,
        profit_factor=float(positive.sum()/loss) if loss>0 else None,
        winrate_active_days=float((x[active]>0).mean()) if active.any() else None,
        active_days=int(active.sum()),component_trades=len(trades),
        daily_close_drawdown=curve_drawdown(x),minute_close_drawdown=curve_drawdown(marked),
        worst_day=float(x.min()),cost_total=float(cost),
        sharpe_daily_annualized=float(np.sqrt(252)*x.mean()/sd) if sd>0 else None,
        active_day_quantiles=quantiles(x[active]),
        component_trade_quantiles=quantiles(values),
        top3_component_share_of_net=float(np.sort(values)[-3:].sum()/x.sum()) if x.sum()>0 else None)


def summarize(dates,trades_by_day,state,technical,variant):
    n=len(dates);points=np.zeros((n,4));atr=np.zeros((n,4))
    point_marks=[];atr_marks=[];daily_rows=[];ledger=[];collections=[[] for _ in MODELS]
    weights=[[] for _ in MODELS]
    for i,day in enumerate(dates):
        trades=trades_by_day.get(day,[]);prices=state[day][0]
        ppaths=[];rpaths=[]
        for j,model in enumerate(MODELS):
            subset=trades if j==3 else [t for t in trades if t['model']==model]
            w=[1/3 if j==3 else 1.]*len(subset)
            points[i,j]=sum(t['net_points']*q for t,q in zip(subset,w))
            atr[i,j]=sum(t['net_points']/t['atr']*q for t,q in zip(subset,w))
            pp=point_path(subset,prices,w)
            rp=marked_curve(subset,prices,w,'NQ_ATR')
            np.testing.assert_allclose([pp[-1],rp[-1]],[points[i,j],atr[i,j]],rtol=0,atol=1e-9)
            ppaths.append(pp);rpaths.append(rp)
            collections[j]+=subset;weights[j]+=w
            daily_rows.append(dict(variant=variant,day=day,model=model,
                technical_context_available=bool(technical[day][model]) if j<3 else True,
                component_trades=len(subset),net_points=points[i,j],net_atr=atr[i,j]))
        point_marks.append(np.asarray(ppaths).T);atr_marks.append(np.asarray(rpaths).T)
        ledger += [dict(variant=variant,**t,net_atr=t['net_points']/t['atr']) for t in trades]
    for matrix in (points,atr):
        np.testing.assert_allclose(matrix[:,3],matrix[:,:3].mean(axis=1),rtol=0,atol=1e-12)
    result={};quarterly=[]
    for j,model in enumerate(MODELS):
        pm=np.concatenate([path+points[:i].sum(axis=0) for i,path in enumerate(point_marks)])[:,j]
        rm=np.concatenate([path+atr[:i].sum(axis=0) for i,path in enumerate(atr_marks)])[:,j]
        pdiff=np.diff(np.r_[0.,pm]);rdiff=np.diff(np.r_[0.,rm])
        result[model]=dict(points=describe(points[:,j],collections[j],pdiff,'POINTS',weights[j]),
            atr=describe(atr[:,j],collections[j],rdiff,'ATR',weights[j]),
            technical_days=sum(technical[d][model] for d in dates) if j<3 else n,
            mfe_points=quantiles([t['mfe_points'] for t in collections[j]]) if j<3 else None,
            mae_points=quantiles([t['mae_points'] for t in collections[j]]) if j<3 else None)
        for quarter in sorted({str(pd.Period(day,freq='Q')) for day in dates}):
            mask=np.array([str(pd.Period(day,freq='Q'))==quarter for day in dates])
            g=[r for r in collections[j] if str(pd.Period(r['day'],freq='Q'))==quarter]
            x=points[mask,j];y=atr[mask,j];loss=-x[x<0].sum();active=np.abs(x)>1e-12
            quarterly.append(dict(variant=variant,quarter=quarter,model=model,evaluation_days=int(mask.sum()),
                component_trades=len(g),net_points=float(x.sum()),net_atr=float(y.sum()),
                winrate_active_days=float((x[active]>0).mean()) if active.any() else None,
                profit_factor=float(x[x>0].sum()/loss) if loss>0 else None))
    return result,points,atr,ledger,daily_rows,quarterly


def decision(metrics,counts,months,projectwide=False):
    enough=months>=24 and all(n>=30 for n in counts)
    if not enough:return 'INCONCLUSIVE_INFORMATION_FLOOR'
    p=metrics['p_holm6_reserved'] if projectwide else metrics['p_holm4']
    return 'STATISTICAL_SUPPORT_ON_REGISTERED_REMAINDER' if metrics['total']>0 and p<.05 else 'NO_STATISTICAL_SUPPORT'


def apply_inference(results,all_intervals):
    # Ordering: PRIMARY points[4], ATR[4], SECONDARY points[4], ATR[4].
    for vi,variant in enumerate(('PRIMARY_STRICT','SECONDARY_AVAILABLE')):
        for ui,unit in enumerate(('points','atr')):
            rows=[results[variant][m][unit] for m in MODELS]
            estimates=all_intervals[vi*8+ui*4:vi*8+ui*4+4]
            for row,estimate in zip(rows,estimates):
                row.update(p_raw=estimate['p_raw'],mean_ci95=estimate['mean_R_ci95'],
                    total_fixed_N_ci95=estimate['total_R_fixed_N_ci95'],sharpe_ci95=estimate['sharpe_ci95'],
                    mean_familywise95_bonf4=estimate['mean_familywise95_bonf4'])
            for row,p in zip(rows,holm([r['p_raw'] for r in rows])):row['p_holm4']=p
            for row,p in zip(rows,holm([r['p_raw'] for r in rows]+[1.,1.])[:4]):row['p_holm6_reserved']=p
