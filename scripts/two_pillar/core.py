import numpy as np
import pandas as pd

FEE = 1.225
TICK = .25


def enrich(trade, atr):
    if not np.isfinite(atr) or atr <= 0:
        raise ValueError('Prior ATR unavailable')
    entry=trade['entry_price']
    return dict(trade,atr=float(atr),gross_R=trade['gross_points']/atr,
                net_R=trade['net_points']/atr,
                gross_pct=100*trade['gross_points']/entry,
                net_pct=100*trade['net_points']/entry)


def night(day, nextday, times, prices, atr, missing, catastrophe=False):
    """Last row is exit09:30 OPEN, never its future low/close."""
    if len(times)<2 or any(len(x)!=len(times) for x in prices.values()):
        raise ValueError('Invalid overnight arrays')
    entry=float(prices['open'][0]);last=len(times)-1
    stop=float(np.ceil((entry-.5*atr)/TICK-1e-9)*TICK)
    end=last;reason='NEXT_OPEN';exit_=float(prices['open'][last]);exit_open=True
    if catastrophe:
        hits=prices['open']<=stop
        hits=hits.copy();hits[:-1] |= prices['low'][:-1]<=stop
        ix=np.flatnonzero(hits)
        if len(ix):
            end=int(ix[0]);op=float(prices['open'][end])
            exit_open=op<=stop;exit_=min(op,stop)
            reason='STOP_GAP' if exit_open else 'STOP'
    # The opening print and closing print of completed holding bars, plus
    # known fill. An exit-bar low after the opening exit cannot affect MAE.
    path=[-FEE]
    path.extend((np.column_stack((prices['open'][:end],prices['close'][:end])).ravel()-entry-FEE).tolist())
    if not exit_open:
        path.append(float(prices['open'][end])-entry-FEE)
    path.append(exit_-entry-FEE)
    lowest=min(entry,float(min(prices['low'][:end])) if end else entry,exit_)
    missing_before_exit=[t for t in missing if t<times[end]]
    trade=dict(day=day,exit_day=nextday,
               actual_exit_civil_day=times[end].tz_convert('America/New_York').strftime('%Y-%m-%d'),
               entry_time=times[0].isoformat(),exit_time=times[end].isoformat(),
               entry_price=entry,exit_price=exit_,gross_points=exit_-entry,net_points=exit_-entry-FEE,
               reason=reason,stop_price=stop if catastrophe else None,
               mae_R=(entry-lowest)/atr,mae_points=entry-lowest,
               missing_holding_minutes=len(missing),missing_before_actual_exit=len(missing_before_exit),
               complete_holding_path=not len(missing),stop_path_identified=not len(missing_before_exit),
               path_points=path)
    return enrich(trade,atr)


def pf(values):
    x=np.asarray(values,float)
    losses=-x[x<0].sum()
    return float(x[x>0].sum()/losses) if losses>0 else None


def description(trades):
    result=dict(N=len(trades))
    for unit in ('points','R','pct'):
        gross=np.array([t['gross_'+unit] for t in trades])
        net=np.array([t['net_'+unit] for t in trades])
        result[unit]=dict(gross_total=float(gross.sum()),net_total=float(net.sum()),
                         mean_net=float(net.mean()) if len(net) else None,
                         median_net=float(np.median(net)) if len(net) else None,
                         profit_factor=pf(net),winrate=float(np.mean(net>0)) if len(net) else None)
    return result


def mae_distribution(trades):
    x=np.array([t['mae_R'] for t in trades])
    return dict(N=len(x),incomplete_paths=sum(not t['complete_holding_path'] for t in trades),
                mean=float(np.mean(x)) if len(x) else None,
                **{f'P{q}':float(np.percentile(x,q)) if len(x) else None for q in (10,25,50,75,90,95)},
                maximum=float(max(x)) if len(x) else None)


def stats(trades, cash_days):
    """Each next cash09:30 or same-day15:55 exit is before the cash-day16:00 boundary.

    Daily net P&L includes all cash sessions and flat days; full trade fee is
    included in its holding interval, realized before this daily boundary.
    Minute DD charges the fee at the actual entry. R is a scale, not capital.
    """
    trades=sorted(trades,key=lambda t:pd.Timestamp(t['entry_time']))
    daily={d:0. for d in cash_days}
    daily_pt={d:0. for d in cash_days}
    equity_R=peak_R=dd_R=equity_pt=peak_pt=dd_pt=0.
    previous_end=None
    for t in trades:
        start,end=pd.Timestamp(t['entry_time']),pd.Timestamp(t['exit_time'])
        if previous_end is not None and start<previous_end:
            raise ValueError('Portfolio positions overlap')
        if t['exit_day'] not in daily:
            raise ValueError('Exit date missing from full cash calendar')
        previous_end=end
        pts=np.asarray(t['path_points'],float)
        for unit,scale,equity,peak in (('R',1./t['atr'],equity_R,peak_R),('points',1.,equity_pt,peak_pt)):
            path=pts*scale+equity
            dd=float(max(np.maximum.accumulate(np.r_[peak,path])[1:]-path))
            if unit=='R':
                dd_R=max(dd_R,dd);peak_R=max(peak_R,float(max(path)))
            else:
                dd_pt=max(dd_pt,dd);peak_pt=max(peak_pt,float(max(path)))
        np.testing.assert_allclose(pts[-1],t['net_points'],rtol=0,atol=1e-9)
        equity_R+=t['net_R'];equity_pt+=t['net_points']
        daily[t['exit_day']]+=t['net_R'];daily_pt[t['exit_day']]+=t['net_points']
    x=np.array(list(daily.values()));sd=x.std(ddof=1) if len(x)>1 else 0.
    quarters=[]
    for q in sorted({str(pd.Period(d,freq='Q')) for d in cash_days}):
        dates=[d for d in cash_days if str(pd.Period(d,freq='Q'))==q]
        n=sum(str(pd.Period(t['exit_day'],freq='Q'))==q for t in trades)
        quarters.append(dict(quarter=q,N=n,net_R=sum(daily[d] for d in dates),net_points=sum(daily_pt[d] for d in dates)))
    return dict(**description(trades),net_R=equity_R,net_points=equity_pt,
                trade_PF_R=pf([t['net_R'] for t in trades]),daily_PF_R=pf(x),
                max_marked_drawdown_R=dd_R,max_marked_drawdown_points=dd_pt,
                sharpe_daily_R=float(np.sqrt(252)*x.mean()/sd) if sd>0 else None,
                cash_days=len(cash_days),positive_quarters_R=sum(q['net_R']>0 for q in quarters),
                positive_quarters_points=sum(q['net_points']>0 for q in quarters),
                traded_quarters=sum(q['N']>0 for q in quarters),quarterly=quarters)
