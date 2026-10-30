"""Cash/share accounting on actual split-normalized ETF prices."""
import math

import numpy as np
import pandas as pd

from scripts.own_account.core import metrics,cash_example


def at(day,clock):
    return pd.Timestamp(f'{day} {clock}',tz='America/New_York').tz_convert('UTC')


def contribution_dates(days):
    seen=set();out=[]
    for day in days:
        if day[:7] not in seen:
            if seen:out.append(day)
            seen.add(day[:7])
    return out


def describe_returns(trades):
    values=np.array([t['net_return'] for t in trades],float)
    loss=-float(values[values<0].sum())
    return dict(N=len(values),winrate_pct=100*float(np.mean(values>0)) if len(values) else None,
        trade_PF=float(values[values>0].sum()/loss) if loss else None,
        mean_net_trade_pct=100*float(values.mean()) if len(values) else None)


def holding(frame,feature,days,rule,bp,monthly=0,initial=1000.):
    """Close signal -> next OPEN, never close signal -> same CLOSE.

    Distribution entitlement is based on shares carried from the prior day.
    Economic NAV accrues/reinvests the real distribution at the ex-date open;
    this is a total-return convention, not a payment-date cash claim.
    Deposits after today's open are cash until the next open, never backdated.
    """
    cash=float(initial);shares=0.;previous_nav=float(initial);paid=float(initial)
    entry_nav=None;entries=orders=0;fees=0.;trades=[];returns=[];nav=[];in_position=[]
    deposits=set(contribution_dates(days))
    all_days=list(frame.index);previous={b:a for a,b in zip(all_days,all_days[1:])}
    for i,day in enumerate(days):
        row=frame.loc[day];op=float(row.open);cl=float(row.close);leg=bp/20000.
        cash+=shares*float(row.distribution)
        desired=rule=='BUYHOLD' or bool(feature.at[previous[day],rule])
        if shares and not desired:
            proceeds=shares*op;fee=proceeds*leg;cash+=proceeds-fee;fees+=fee;orders+=1;shares=0.
            trades.append(dict(exit_day=day,net_return=cash/entry_nav-1));entry_nav=None
        if desired and cash>1e-10:
            if not shares:entry_nav=cash;entries+=1
            fee=cash*leg;fees+=fee;orders+=1
            shares+=(cash-fee)/op;cash=0.
        active=shares>0
        if i==len(days)-1 and shares:
            proceeds=shares*cl;fee=proceeds*leg;cash+=proceeds-fee;fees+=fee;orders+=1;shares=0.
            trades.append(dict(exit_day=day,net_return=cash/entry_nav-1));entry_nav=None
        external=float(monthly) if day in deposits else 0.
        end_before_flow=cash+shares*cl
        returns.append(end_before_flow/previous_nav-1)
        cash+=external;paid+=external
        previous_nav=end_before_flow+external;nav.append(previous_nav);in_position.append(active)
    result=dict(**metrics(returns,days),**describe_returns(trades),orders=orders,
        exposure_cash_days=sum(in_position),total_model_costs=fees,
        ending_capital=previous_nav,contributions=paid,investment_profit=previous_nav-paid)
    return dict(summary=result,daily_returns=returns,daily_NAV=nav,trades=trades)


def entitled_distribution(frame,entry,exit_):
    """Entitlement changes at ex-date civil boundary, BEFORE premarket sales."""
    total=0.
    for day,amount in frame.distribution[frame.distribution>0].items():
        boundary=at(day,'00:00')
        if entry<boundary<=exit_:total+=float(amount)
    return total


def minute_path(frame,day,nextday,features,splits,window,stop=False,cash_dates=None):
    """Strict anchors, positive-volume fills; next-open bar future low excluded."""
    begin=at(day,'16:01' if window=='LATENCY' else '16:00')
    end=at(nextday,'09:31' if window=='LATENCY' else '09:30')
    if frame.empty or begin not in frame.index or end not in frame.index:return None,'MISSING_EXACT_ANCHOR'
    rows=frame.loc[begin:end]
    if rows.at[begin,'volume']<=0 or rows.at[end,'volume']<=0:return None,'ZERO_VOLUME_ANCHOR'
    reference=None
    if window=='LAST_MINUTE_CLOSE':
        prior=at(day,'15:59')
        if prior not in frame.index or frame.at[prior,'volume']<=0:return None,'MISSING_1559_TRADE'
        reference=float(frame.at[prior,'close'])
    entry=float(rows.open.iloc[0]) if reference is None else reference
    used=rows[rows.volume>0];ix=used.index;exit_price=float(used.open.iloc[-1]);end_index=len(used)-1
    reason='NEXT_OPEN';stop_price=None;intrabar=False
    if stop:
        atr=features['ATR14']
        if not np.isfinite(atr) or atr<=0:return None,'ETF_ATR_WARMUP'
        future_factor=math.prod(v['ratio'] for v in splits if v['day']>day)
        tick=.01/future_factor;stop_price=math.ceil((entry-.5*atr)/tick-1e-9)*tick
        hit=(used.open.to_numpy()<=stop_price).copy()
        hit[:-1]|=used.low.to_numpy()[:-1]<=stop_price
        where=np.flatnonzero(hit)
        if len(where):
            end_index=int(where[0]);op=float(used.open.iloc[end_index]);intrabar=op>stop_price
            exit_price=min(op,stop_price);reason='STOP' if intrabar else 'STOP_GAP'
    exit_time=ix[end_index]+pd.Timedelta(seconds=59 if intrabar else 0)
    local=ix.tz_convert('America/New_York')
    # Scheduled cash-equity extended-hours minutes are a diagnostic, not a
    # claim that every missing print conceals an executed trade/stop.
    expected=[]
    civil_days=[d for d in cash_dates if day<=d<=nextday] if cash_dates is not None else list(pd.bdate_range(day,nextday).strftime('%Y-%m-%d'))
    for civil in civil_days:
        expected.extend(pd.date_range(at(civil,'04:00'),at(civil,'20:00'),freq='min',inclusive='left'))
    expected=pd.DatetimeIndex(expected);expected=expected[(expected>=begin)&(expected<end)]
    missing=expected.difference(ix)
    return dict(day=day,exit_day=nextday,entry_stamp=begin.timestamp(),entry_time=begin.isoformat(),
        actual_exit_time=exit_time.isoformat(),entry=entry,exit=exit_price,reason=reason,stop_price=stop_price,
        price_return=exit_price/entry-1,missing_minutes=len(missing),
        missing_before_exit=int(sum(t<exit_time for t in missing)),
        stop_data_complete=bool(not len([t for t in missing if t<exit_time]))), 'OK'


def overnight(frame,days,trades,bp,monthly=0,initial=1000.):
    """An economically owned real dividend is included once, not AdjClose twice."""
    rows=[];daily=dict.fromkeys(days,0.)
    for original in trades:
        t=dict(original);start=pd.Timestamp(t['entry_time']);end=pd.Timestamp(t['actual_exit_time'])
        div=entitled_distribution(frame,start,end)
        factor=(t['exit']+div)/t['entry']-bp/10000.
        if factor<=0:raise ValueError('Nonpositive ETF capital factor')
        t.update(distribution=div,factor=factor,net_return=factor-1)
        if t['exit_day'] not in daily:raise ValueError('Exit outside requested calendar')
        daily[t['exit_day']]=factor-1;rows.append(t)
    dates=[at(d,'09:32').timestamp() for d in contribution_dates(days)]
    cash=cash_example(rows,dates,monthly,initial)
    return dict(summary=dict(**metrics(list(daily.values()),days),**describe_returns(rows),
        **cash,orders=2*len(rows),exposure_cash_days=len(rows),
        missing_stop_paths=sum(t['stop_price'] is not None and not t['stop_data_complete'] for t in rows)),
        daily_returns=list(daily.values()),daily_NAV=(initial*np.cumprod(1+np.array(list(daily.values())))).tolist(),trades=rows)


def sleeve_portfolio(core,overlay,days):
    """Initial50/50 buy-and-hold of sleeves, not free daily rebalancing."""
    first=np.cumprod(1+np.array(core['daily_returns']));second=np.cumprod(1+np.array(overlay['daily_returns']))
    nav=(first+second)/2;returns=nav/np.r_[1.,nav[:-1]]-1
    return dict(summary=dict(**metrics(returns,days),N=core['summary']['N']+overlay['summary']['N'],
        orders=core['summary']['orders']+overlay['summary']['orders']),
        daily_returns=returns.tolist(),daily_NAV=(nav*1000).tolist(),trades=[])
