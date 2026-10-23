"""Sequential context enrichment. No current/future-day percentile fitting."""
import numpy as np
import pandas as pd
from scripts.oos_preparation.adapter import at


def cash_dates(start,end):
    # Full closed cash days, not CME early-close trading days. Short cash days
    # still count in month position. Sources registered in protocol.
    closed=set('2022-12-26 2023-01-02 2023-01-16 2023-02-20 2023-04-07 2023-05-29 2023-06-19 2023-07-04 2023-09-04 2023-11-23 2023-12-25 2024-01-01 2024-01-15 2024-02-19 2024-03-29 2024-05-27 2024-06-19 2024-07-04 2024-09-02 2024-11-28 2024-12-25 2025-01-01 2025-01-09 2025-01-20 2025-02-17 2025-04-18 2025-05-26 2025-06-19 2025-07-04 2025-09-01 2025-11-27 2025-12-25 2026-01-01 2026-01-19 2026-02-16 2026-04-03 2026-05-25 2026-06-19 2026-07-03 2026-09-07 2026-11-26 2026-12-25 2018-11-22 2018-12-05 2018-12-25 2019-01-01 2019-01-21 2019-02-18 2019-04-19 2019-05-27 2019-07-04 2019-09-02 2019-11-28 2019-12-25'.split())
    return [d for d in pd.bdate_range(start,end).strftime('%Y-%m-%d') if d not in closed]


def calendar_context(day):
    stamp=pd.Timestamp(day);first=stamp.replace(day=1);end=first+pd.offsets.MonthEnd(0)
    dates=cash_dates(first.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'))
    if day not in dates:return dict(tom=False,tom_position=None)
    index=dates.index(day)
    position='T-1' if index==len(dates)-1 else f'T+{index+1}' if index<3 else None
    return dict(tom=position is not None,tom_position=position)


def enrich(state,scheduled,active,rolls):
    lookup={d:g for d,g in active.groupby('trade_date')}
    offsets={d:sum(r['spread_points'] for r in rolls if r['session']<=d) for d in scheduled}
    hist=[];onvol=[];result={}
    for day in scheduled:
        prices,base=state[day];ctx=dict(base);ctx.update(calendar_context(day))
        ctx['friday']=pd.Timestamp(day).weekday()==4
        trailing=hist[-60:]
        ctx['atr_p90']=float(np.quantile(trailing,.9)) if len(trailing)==60 else np.nan
        if len(trailing)==60 and np.isfinite(ctx['atr']):
            a,b=np.quantile(trailing,[.25,.75])
            ctx['atr_regime']='LOW' if ctx['atr']<a else 'HIGH' if ctx['atr']>b else 'MID'
        else:ctx['atr_regime']=None
        # Week direction uses the first CASH session's open, not an arbitrary
        # first complete date chosen after inspecting the week.
        monday=pd.Timestamp(day)-pd.Timedelta(days=pd.Timestamp(day).weekday())
        week=cash_dates(monday.strftime('%Y-%m-%d'),day)
        first=week[0] if week else None
        ctx['week_open']=np.nan
        if first in state and first<=day:
            start=float(state[first][0]['open'][0])
            if np.isfinite(start):ctx['week_open']=start-offsets.get(first,0)+offsets[day]
        prev=(pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        ix=pd.date_range(at(prev,'18:00'),at(day,'09:30'),freq='min',inclusive='left')
        g=lookup.get(day,active.iloc[:0]);overnight=g.loc[g.index.isin(ix)]
        complete=overnight.index.equals(ix)
        ctx.update(overnight_complete=complete,overnight_open=np.nan,overnight_high=np.nan,
                   overnight_low=np.nan,overnight_volume=None,overnight_rvol=None,
                   overnight_direction=0,inventory_condition=False)
        vol=None
        if complete:
            op=float(overnight.open.iloc[0]);cl=float(overnight.close.iloc[-1]);hi=float(overnight.high.max());lo=float(overnight.low.min())
            vol=int(overnight.volume.sum());prior=onvol[-20:]
            rvol=vol/np.mean(prior) if len(prior)==20 and all(x is not None for x in prior) and np.mean(prior)>0 else None
            efficiency=abs(cl-op)/(hi-lo) if hi>lo else 0.
            direction=int(np.sign(cl-op))
            ctx.update(overnight_open=op,overnight_high=hi,overnight_low=lo,overnight_volume=vol,
                overnight_rvol=float(rvol) if rvol is not None else None,overnight_direction=direction,
                inventory_condition=bool(direction and efficiency>=.7 and rvol is not None and rvol>=1.5 and np.isfinite(ctx['atr']) and hi-lo<=.8*ctx['atr']))
        result[day]=(prices,ctx)
        if np.isfinite(ctx['atr']):hist.append(ctx['atr'])
        onvol.append(vol)
    return result
