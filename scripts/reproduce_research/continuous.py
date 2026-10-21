"""Point-in-time additive Panama indicator history. Raw fills stay untouched."""
import numpy as np
import pandas as pd
from . import engine
from .next_engine import active_mask


def roll_spreads(full, schedule):
    """Last common completed 15:59 NY bar BEFORE activation; never settlement."""
    records=[]
    for old,new in zip(schedule,schedule[1:]):
        activation=engine.time_at((pd.Timestamp(new.session)-pd.Timedelta(days=1)).strftime('%Y-%m-%d'),'18:00')
        a=full[(full.contract==old.contract)&(full.index<activation)]
        b=full[(full.contract==new.contract)&(full.index<activation)]
        common=a.index.intersection(b.index)
        common=common[common.tz_convert(engine.NY).strftime('%H:%M')=='15:59']
        if not len(common):
            raise ValueError('No common pre-roll RTH close: '+new.contract)
        t=common.max()
        if a.index.has_duplicates or b.index.has_duplicates:
            raise ValueError('Reconcile contract duplicates before adjustment')
        records.append({'old':old.contract,'new':new.contract,'session':new.session,
                        'effective_utc':activation,'close_bar_utc':t,
                        'spread_available_utc':t+pd.Timedelta(minutes=1),
                        'spread_points':float(b.at[t,'close']-a.at[t,'close']),
                        'close_age_calendar_days':(pd.Timestamp(new.session)-pd.Timestamp(a.at[t,'trade_date'])).days})
    return records


def continuous_daily(full, schedule):
    """Forward-neutral coordinate internally, equivalent to as-of back-adjustment.

    base_price = raw_price - known cumulative roll spreads. At each decision,
    translate historical levels to current raw basis by adding current offset.
    Future roll spreads NEVER revise earlier states. ATR is translation-invariant.
    """
    rolls=roll_spreads(full,schedule)
    selected=full.loc[active_mask(full,schedule)].sort_index()
    if selected.index.has_duplicates:
        raise ValueError('Active stream has duplicate timestamps')
    history=[]; rows=[]; previous=None
    for day,g in selected.groupby('trade_date',sort=True):
        offset=sum(r['spread_points'] for r in rolls if r['session']<=day)
        prior=history[-14:]
        a,b=engine.time_at(day,'09:30'),engine.time_at(day,'16:00')
        rth=engine.window(g,a,b)
        complete=engine.complete(rth,a,b)
        hi=float(rth.high.max()-offset) if complete else np.nan
        lo=float(rth.low.min()-offset) if complete else np.nan
        close=float(rth.close.iloc[-1]-offset) if complete else np.nan
        valid_prev=previous is not None and previous['rth_complete']
        tr=max(hi-lo,abs(hi-previous['base_close']),abs(lo-previous['base_close'])) if complete and valid_prev else np.nan
        row={'trade_date':day,'contract':g.contract.iloc[0],'offset_points':offset,
             'atr14_continuous':float(np.mean(prior)) if len(prior)==14 else np.nan,
             'pdh_continuous':previous['base_high']+offset if valid_prev else np.nan,
             'pdl_continuous':previous['base_low']+offset if valid_prev else np.nan,
             'rth_complete':complete,'base_high':hi,'base_low':lo,'base_close':close,
             'continuous_TR':tr,'valid_prior_TR':len(history),
             'indicator_available_utc':engine.time_at((pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d'),'18:00')}
        rows.append(row)
        if np.isfinite(tr): history.append(tr)
        previous=row
    return pd.DataFrame(rows),rolls


def apply_indicators(master,daily):
    """Only multi-day indicators and their ratios change; never OHLCV or VWAP."""
    out=master.copy()
    lookup=daily.set_index('trade_date')
    out['atr14_prior']=out.trade_date.map(lookup.atr14_continuous)
    out['pdh']=out.trade_date.map(lookup.pdh_continuous)
    out['pdl']=out.trade_date.map(lookup.pdl_continuous)
    out['history_quality_flag']=np.where(out.atr14_prior.notna(),'ok','atr_warmup')
    for n in [5,15,30]:
        out[f'orb{n}_range_pct_atr']=100*(out[f'orb{n}_high']-out[f'orb{n}_low'])/out.atr14_prior
    return out
