"""Continuous same-clock volume reference and descriptive minute-path bounds.

No strategy constants change. No tick-order certainty is inferred from OHLC bars.
"""
import numpy as np
import pandas as pd
from . import engine


def active_volume_history(master):
    if not master.index.is_unique or not master.index.is_monotonic_increasing:
        raise ValueError('Unique chronological active bars required')
    if master.groupby('trade_date').contract.nunique().gt(1).any():
        raise ValueError('One active contract per session required')
    result=master.copy(); history={}
    for _,g in result.groupby('trade_date',sort=True):
        clocks=g.index.tz_convert(engine.NY).strftime('%H:%M')
        references=[float(np.median(history[hm][-20:])) if len(history.get(hm,[]))>=10 else np.nan for hm in clocks]
        result.loc[g.index,'prior_same_minute_median_volume']=references
        # Never include current-session or inactive-contract volume in its reference.
        for hm,value in zip(clocks,g.volume):history.setdefault(hm,[]).append(float(value))
    return result


def quantiles(values):
    x=np.asarray(values,dtype=float)
    x=x[np.isfinite(x)]
    return {'n':len(x),**{name:float(np.quantile(x,p)) if len(x) else None
                         for name,p in [('p05',.05),('p25',.25),('median',.5),('p75',.75),('p95',.95)]}}


def trade_paths(master,trades):
    rows=[]
    for r in trades.itertuples():
        entry,exitbar=pd.Timestamp(r.entry_utc),pd.Timestamp(r.exit_bar_utc)
        g=master[(master.trade_date==r.trade_date)&(master.contract==r.contract)]
        path=g.loc[(g.index>=entry)&(g.index<=exitbar)]
        expected=pd.date_range(entry,exitbar,freq='min')
        if not path.index.equals(expected):raise ValueError('Incomplete trade path')
        risk=abs(r.entry_price-r.stop)
        if risk<=0 or r.direction*(r.entry_price-r.stop)<=0:
            raise ValueError('Initial stop must be on loss side')
        favorable=(path.high-r.entry_price) if r.direction==1 else (r.entry_price-path.low)
        adverse=(r.entry_price-path.low) if r.direction==1 else (path.high-r.entry_price)
        prefix=path.iloc[:-1]
        fav_prefix=(prefix.high-r.entry_price) if r.direction==1 else (r.entry_price-prefix.low)
        adv_prefix=(r.entry_price-prefix.low) if r.direction==1 else (prefix.high-r.entry_price)
        gross=r.direction*(r.exit_price-r.entry_price)
        # Completed earlier bars and the execution endpoint are known within the
        # modeled position. Exit-bar extremes may have occurred AFTER the fill.
        mfe_lower=max(0.,float(fav_prefix.max()) if len(prefix) else 0.,gross)
        mae_lower=max(0.,float(adv_prefix.max()) if len(prefix) else 0.,-gross)
        mfe_upper=max(mfe_lower,float(favorable.max()),0.)
        mae_upper=max(mae_lower,float(adverse.max()),0.)
        # A modeled position cannot continue beyond its profit barrier, or its
        # stop except for the actual modeled adverse gap fill. This tightens
        # bounds without inventing high/low order within the exit minute.
        target_gain=r.direction*(r.target-r.entry_price)
        if target_gain<=0:raise ValueError('Target must be on profit side')
        mfe_upper=max(mfe_lower,min(mfe_upper,target_gain))
        mae_upper=max(mae_lower,min(mae_upper,max(risk,-gross)))
        if r.exit_reason=='noon':
            # Session exit is at the final minute close: its entire bar occurred
            # while the model position was open, unlike an intrabar SL/TP fill.
            mfe_lower=mfe_upper;mae_lower=mae_upper
        # First occurrence in a tie; integer k labels minute [k,k+1), not exact time.
        # Zero excursion is attained at entry itself: retain those trades at t=0.
        mfe_time=(favorable.idxmax()-entry).total_seconds()/60 if favorable.max()>0 else 0.
        mae_time=(adverse.idxmax()-entry).total_seconds()/60 if adverse.max()>0 else 0.
        reason='stop' if r.exit_reason in ['stop','stop_both'] else 'target' if r.exit_reason=='target' else 'time_session' if r.exit_reason=='noon' else None
        if reason is None:raise ValueError('Unknown exit reason')
        rows.append({'strategy':r.strategy,'trade_date':r.trade_date,'contract':r.contract,
                     'entry_utc':entry,'exit_bar_utc':exitbar,'initial_R_points':risk,
                     'net_points':r.net_points,'net_R':r.net_points/risk,'exit_group':reason,
                     'exit_reason':r.exit_reason,'both_hit_bar':r.both_hit_bar,
                     'MFE_R_lower':mfe_lower/risk,'MFE_R_bar_upper':mfe_upper/risk,
                     'MAE_R_lower':mae_lower/risk,'MAE_R_bar_upper':mae_upper/risk,
                     'MFE_first_bar_minute':mfe_time,'MAE_first_bar_minute':mae_time,
                     'MFE_first_extreme_in_exit_bar':bool(favorable.max()>0 and favorable.idxmax()==exitbar),
                     'MAE_first_extreme_in_exit_bar':bool(adverse.max()>0 and adverse.idxmax()==exitbar),
                     'completed_preexit_bars':len(prefix),
                     'MFE_completed_prefix_minute':(fav_prefix.idxmax()-entry).total_seconds()/60 if len(prefix) and fav_prefix.max()>0 else np.nan,
                     'MAE_completed_prefix_minute':(adv_prefix.idxmax()-entry).total_seconds()/60 if len(prefix) and adv_prefix.max()>0 else np.nan,
                     'exit_bar_minute':(exitbar-entry).total_seconds()/60})
    return pd.DataFrame(rows)


def summarize_paths(paths):
    result={}
    for strategy,g in paths.groupby('strategy'):
        thresholds=[]
        sign=np.where(g.net_points>0,'positive',np.where(g.net_points<0,'negative','flat'))
        for level in [.5,1.,1.5]:
            certain=g.MFE_R_lower.ge(level); possible=g.MFE_R_bar_upper.ge(level)
            by_sign={s:{'certain':int((certain&(sign==s)).sum()),'possible_including_certain':int((possible&(sign==s)).sum())} for s in ['negative','positive','flat']}
            # Bounds on conditional sign shares over all feasible hit assignments.
            conditional={}
            for s in by_sign:
                lower=by_sign[s]['certain'];upper=by_sign[s]['possible_including_certain']
                upper_other=sum(v['possible_including_certain'] for k,v in by_sign.items() if k!=s)
                lower_other=sum(v['certain'] for k,v in by_sign.items() if k!=s)
                conditional[s]={'lower':lower/(lower+upper_other) if lower+upper_other else 1. if upper else None,
                                'upper':upper/(upper+lower_other) if upper+lower_other else 0. if upper_other else None}
            thresholds.append({'R':level,'all_trades':len(g),'certain_hits':int(certain.sum()),
                               'possible_hits_including_certain':int(possible.sum()),
                               'hit_fraction_lower':float(certain.mean()),'hit_fraction_upper':float(possible.mean()),
                               'by_final_net_sign':by_sign,'conditional_sign_fraction_bounds':conditional})
        exits=[]
        for reason in ['target','stop','time_session']:
            e=g[g.exit_group.eq(reason)]
            exits.append({'reason':reason,'trades':len(e),'share':len(e)/len(g),
                          'net_points':float(e.net_points.sum()),'net_usd':float(20*e.net_points.sum()),
                          'positive':int(e.net_points.gt(0).sum()),'negative':int(e.net_points.lt(0).sum()),
                          'flat':int(e.net_points.eq(0).sum()),'net_R':quantiles(e.net_R)})
        result[strategy]={'trades':len(g),'thresholds':thresholds,
                          'MFE_R_lower':quantiles(g.MFE_R_lower),'MFE_R_bar_upper':quantiles(g.MFE_R_bar_upper),
                          'MAE_R_lower':quantiles(g.MAE_R_lower),'MAE_R_bar_upper':quantiles(g.MAE_R_bar_upper),
                          'MFE_first_bar_minutes':quantiles(g.MFE_first_bar_minute),
                          'MAE_first_bar_minutes':quantiles(g.MAE_first_bar_minute),
                          'MFE_completed_prefix_minutes':quantiles(g.MFE_completed_prefix_minute),
                          'MAE_completed_prefix_minutes':quantiles(g.MAE_completed_prefix_minute),
                          'MFE_extreme_in_exit_bar':int(g.MFE_first_extreme_in_exit_bar.sum()),
                          'MAE_extreme_in_exit_bar':int(g.MAE_first_extreme_in_exit_bar.sum()),
                          'stop_both_trades':int(g.both_hit_bar.sum()),'exits':exits}
    return result
