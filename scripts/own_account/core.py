"""Causal terminal features and observed same-contract percentage paths."""
import numpy as np
import pandas as pd

from scripts.ict_study.core import ceil_tick

YEAR_SECONDS=365.2425*24*3600


def terminal_features(history,current,offset=0.):
    """History excludes today; its closes are normalized by known roll offsets."""
    h=np.asarray(history,float)
    out={}
    for length in (20,200):
        trailing=np.r_[h[-(length-1):],current-offset]
        ready=len(h)>=length-1 and len(trailing)==length and np.isfinite(trailing).all()
        out['SMA'+str(length)]=float(trailing.mean()+offset) if ready else None
    for length in (5,10,20):
        prior=float(h[-length]+offset) if len(h)>=length else np.nan
        out['momentum'+str(length)]=current/prior-1 if np.isfinite(current) and np.isfinite(prior) and prior>0 else None
    return out


def allowed_etf_stop(times):
    local=times.tz_convert('America/New_York')
    return (local.weekday<5)&(local.hour>=4)&(local.hour<20)


def observed_path(times,prices,atr,stop_mode='NONE',reference=None):
    """Only final bar OPEN belongs to exit; later high/low/close never used."""
    if len(times)<2:
        raise ValueError('Two exact endpoints required')
    entry=float(prices['open'][0]) if reference is None else float(reference)
    if not entry>0 or not np.isfinite(entry):
        raise ValueError('Invalid entry')
    last=len(times)-1;end=last;stop=None;reason='NEXT_OPEN';exit_open=True
    if stop_mode!='NONE':
        stop=ceil_tick(entry-.5*atr)
        active=np.ones(len(times),bool) if stop_mode=='GLOBEX050' else np.asarray(allowed_etf_stop(times))
        hits=np.asarray(prices['open'])<=stop
        hits=hits.copy();hits[:-1]|=np.asarray(prices['low'][:-1])<=stop
        ix=np.flatnonzero(hits&active)
        if len(ix):
            end=int(ix[0]);exit_open=bool(prices['open'][end]<=stop)
            reason='STOP_GAP' if exit_open else 'STOP'
    exit_price=(float(prices['open'][end]) if exit_open else float(stop))
    values=[entry];stamps=[times[0].timestamp()]
    for i in range(end):
        values.extend([float(prices['open'][i]),float(prices['close'][i])])
        stamps.extend([times[i].timestamp(),times[i].timestamp()+59.])
    if not exit_open:
        values.append(float(prices['open'][end]));stamps.append(times[end].timestamp())
    values.append(exit_price);stamps.append(times[end].timestamp()+(0 if exit_open else 59.))
    return dict(entry=entry,exit=exit_price,gross_points=exit_price-entry,
        return_fraction=exit_price/entry-1,stop=stop,reason=reason,
        actual_exit_utc=pd.Timestamp(stamps[-1],unit='s',tz='UTC').isoformat(),
        prices=np.asarray(values),elapsed=np.asarray(stamps)-stamps[0],
        holding_seconds=float(stamps[-1]-stamps[0]))


def factors(path,leverage,bp,drag=False):
    elapsed=path['elapsed']/YEAR_SECONDS
    annual=(.06*(leverage-1)+.01) if drag and leverage==3 else 0.
    a=1.+leverage*(path['prices']/path['entry']-1.)-bp/20000.-annual*elapsed
    a=a.copy();a[-1]-=bp/20000.
    a=np.maximum(a,0.)
    if np.any(a<=0):
        first=int(np.flatnonzero(a<=0)[0]);a[first:]=0.
    peak=np.maximum.accumulate(np.r_[1.,a])[1:]
    return dict(final=float(a[-1]),minimum=float(a.min()),maximum=float(max(1.,a.max())),
                local_drawdown=float(np.max(1.-np.divide(a,peak,out=np.zeros_like(a),where=peak>0))))


def underwater(equity,dates):
    peak=float(equity[0]);start=None;maximum=0;calmax=0;count=0
    for i,value in enumerate(equity[1:]):
        if value>=peak-1e-12:
            peak=max(peak,float(value));start=None;count=0
        else:
            if start is None:start=max(0,i-1)
            count+=1;maximum=max(maximum,count)
            calmax=max(calmax,(pd.Timestamp(dates[i])-pd.Timestamp(dates[start])).days)
    fraction=float(np.mean(equity[1:]<np.maximum.accumulate(equity)[1:]-1e-12)) if len(equity)>1 else 0.
    return dict(max_TUW_sessions=maximum,max_TUW_calendar_days=calmax,TUW_fraction=fraction)


def metrics(daily,dates,observed_drawdown=None,years=None):
    a=np.asarray(daily,float);growth=np.cumprod(1.+a);equity=np.r_[1.,growth]
    if years is None:
        years=((pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).total_seconds()+6.5*3600)/YEAR_SECONDS
    total=float(equity[-1]);sd=float(a.std(ddof=1)) if len(a)>1 else 0.
    downside=float(np.sqrt(np.mean(np.minimum(a,0.)**2))) if len(a) else 0.
    peak=np.maximum.accumulate(equity)
    dd=float(np.max(1.-np.divide(equity,peak,out=np.zeros_like(equity),where=peak>0)))
    return dict(total_return_pct=100*(total-1),annualized_growth_pct=100*(total**(1/years)-1) if years>0 else None,
        elapsed_observed_years=float(years),closed_cycle_MDD_pct=100*dd,
        observed_mark_MDD_pct=100*observed_drawdown if observed_drawdown is not None else None,
        Sharpe=float(np.sqrt(252)*a.mean()/sd) if sd>0 else None,
        Sortino=float(np.sqrt(252)*a.mean()/downside) if downside>0 else None,
        **underwater(equity,dates))


def cash_example(trades,contributions,monthly,initial=1000.):
    """Contributions only join trades entered after their actual deposit time."""
    balance=initial;added=0.;j=0
    for trade in sorted(trades,key=lambda t:t['entry_stamp']):
        while j<len(contributions) and contributions[j]<=trade['entry_stamp']:
            balance+=monthly;added+=monthly;j+=1
        balance*=trade['factor']
    balance+=monthly*(len(contributions)-j);added+=monthly*(len(contributions)-j)
    return dict(ending_capital=balance,contributions=initial+added,investment_profit=balance-initial-added)
