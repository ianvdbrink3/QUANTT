"""Timestamped OHLCV context, without invented tick counts or future windows."""
import numpy as np
import pandas as pd
from . import engine


def day_context(master):
    history=[]; rows=[]
    for day,g in master.groupby('trade_date',sort=True):
        t=engine.time_at(day,'09:30'); end=engine.time_at(day,'09:45')
        prev=(pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        overnight=engine.window(g,engine.time_at(prev,'18:00'),t)
        good=engine.complete(overnight,engine.time_at(prev,'18:00'),t)
        orb=engine.window(g,t,end); complete=engine.complete(orb,t,end)
        op=float(g.at[t,'open']) if t in g.index else np.nan
        atr=float(g.atr14_prior.iloc[0]); pdh=float(g.pdh.iloc[0]); pdl=float(g.pdl.iloc[0])
        hi,lo=(float(overnight.high.max()),float(overnight.low.min())) if good else (np.nan,np.nan)
        opening_volume=float(orb.volume.sum()) if complete else np.nan
        # Last 14 observed active sessions, not last 14 hand-picked valid sessions.
        prior=history[-14:]
        reference=float(np.mean(prior)) if len(prior)==14 and np.isfinite(prior).all() else np.nan
        location=None if not np.isfinite([op,pdh,pdl]).all() else 'GAP_ABOVE_PDH' if op>pdh else 'GAP_BELOW_PDL' if op<pdl else 'INSIDE_PRIOR_RANGE'
        rows.append({'trade_date':day,'contract':g.contract.iloc[0],
                     'opening_location':location,'opening_context_available_utc':t,
                     'overnight_range_ATR':(hi-lo)/atr if atr>0 else np.nan,
                     'open_in_overnight_pct':100*(op-lo)/(hi-lo) if hi>lo else np.nan,
                     'overnight_regime':None if not (atr>0 and good) else 'COMPRESSED' if (hi-lo)/atr<.5 else 'EXPANDED' if (hi-lo)/atr>1.2 else 'MIDDLE',
                     'opening_volume_15m':opening_volume,'prior14_opening_volume_mean':reference,
                     'opening_RVOL14':opening_volume/reference if reference>0 else np.nan,
                     'opening_volume_available_utc':end,'opening_relative_ticks':np.nan,
                     'opening_volume_per_tick':np.nan,'ticks_status':'UNAVAILABLE_SOURCE_HAS_NO_TICK_COUNTS'})
        history.append(opening_volume)
    return pd.DataFrame(rows)


def trade_context(master,trades,days):
    contexts=days.set_index('trade_date'); rows=[]
    for r in trades.itertuples():
        entry=pd.Timestamp(r.entry_utc); signal=pd.Timestamp(r.signal_utc)
        g=master[master.trade_date.eq(r.trade_date)]
        ctx=contexts.loc[r.trade_date].to_dict()
        opening_at=pd.Timestamp(ctx['opening_context_available_utc'])
        volume_at=pd.Timestamp(ctx['opening_volume_available_utc'])
        if not opening_at<entry:
            for key in ['opening_location','open_in_overnight_pct','overnight_range_ATR','overnight_regime']:
                ctx[key]=None
        if volume_at>entry:
            for key in ['opening_volume_15m','prior14_opening_volume_mean','opening_RVOL14']:
                ctx[key]=None
        # Completed signal bar is known at next-bar entry; its price is NOT entry open.
        price=float(g.at[signal,'close']); atr=float(g.at[signal,'atr14_prior'])
        ctx.update(trade_date=r.trade_date,strategy=r.strategy,entry_utc=entry,
                   context_asof_utc=entry,breakout_reference_price=price,
                   distance_to_PDH_pct_ATR=100*(float(g.at[signal,'pdh'])-price)/atr,
                   distance_to_PDL_pct_ATR=100*(price-float(g.at[signal,'pdl']))/atr,
                   breakout_bar_volume=float(g.at[signal,'volume']),
                   breakout_bar_relative_ticks=None,breakout_bar_volume_per_tick=None,
                   net_points=r.net_points,mfe_bar_bound_points=r.mfe_bar_bound_points,
                   mae_bar_bound_points=r.mae_bar_bound_points)
        rows.append(ctx)
    return pd.DataFrame(rows)
