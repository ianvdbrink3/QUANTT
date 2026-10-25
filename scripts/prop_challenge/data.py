"""Rebuild selected frozen kernels and private account-risk paths from source bars."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.prop_firm import __main__ as prior
from scripts.ict_study import __main__ as ict
from scripts.ict_study import core as sig
from scripts.price_volume import core as pv

ROOT = prior.ROOT
SPECS = {
 'J0830':'ICT3_5m_BOTH_OPEN0830_JUDAS_2R',
 'JBULL0930':'ICT3_5m_BULL_LONG_OPEN0930_JUDAS_2R',
 'J1M_TIME':'ICT3_1m_BULL_LONG_OPEN0930_JUDAS_TIME',
 'ICT1':'ICT1_1m_BOTH_ON_REVERSAL_3R',
 # Existing-paper selection: maximum WORST-era Sharpe among positive-in-both
 # strict-fill candidates, then worst-era ATR return, then lexical name.
 'SB_AM':'ICT2_5m_BULL_LONG_AM_CONTINUE_2R',
 'SB_PM':'ICT2_1m_BOTH_PM_CONTINUE_2R',
}
PRIORITY = {'J0830':1,'JBULL0930':1,'J1M_TIME':1,'ICT1':2,
            'SB_AM':3,'PULLBACK':4,'SB_PM':5}


def minute(t): return int(pd.Timestamp(t).value//60_000_000_000)


def path_limits(trade, times, p, missing=()):
    """Bounds only while held; do not turn exit-open future lows into losses.

    A missing scheduled minute yields an unresolvable path from that minute.
    Only known earlier marks may prove a floor breach before the data gap.
    Entry-bar OHLC cannot prove order: adverse bound is explicitly conservative.
    """
    start, end = pd.Timestamp(trade['entry_time']), pd.Timestamp(trade['exit_time'])
    gaps = [pd.Timestamp(t) for t in missing if start <= pd.Timestamp(t) < end]
    cutoff = min(gaps) if gaps else end
    side, entry = trade.get('direction',1), trade['entry_price']
    observed, adverse = [0.], [0.]
    for i, ts in enumerate(times):
        if ts < start or ts > cutoff: continue
        terminal = ts == end and not gaps
        if terminal:
            if trade['exit_at_open']:
                observed.append(trade['gross_points']); adverse.append(trade['gross_points'])
                break
            if ts > start or trade.get('entry_at_open',True):
                observed.append(side*(p['open'][i]-entry))
            observed.append(trade['gross_points'])
            low = side*((p['low'][i] if side==1 else p['high'][i])-entry)
            if trade.get('stop_price') is not None:
                low=max(low,side*(trade['stop_price']-entry))
            # A stop or target fill bounds this bar; no post-exit low/close.
            adverse.extend((low,trade['gross_points']))
            break
        if ts >= cutoff: break
        if ts > start or trade.get('entry_at_open',True):
            observed.append(side*(p['open'][i]-entry))
        observed.append(side*(p['close'][i]-entry))
        adverse.append(side*((p['low'][i] if side==1 else p['high'][i])-entry))
    if not gaps:
        observed.append(trade['gross_points']); adverse.append(trade['gross_points'])
    return float(min(observed)),float(min(adverse)),bool(gaps)


def intraday_candidate(component, day, block, p, ctx, order, trade):
    base=prior.h.at(day,'09:30')
    activation=base+pd.Timedelta(minutes=order['boundary'])
    row=dict(component=component,priority=PRIORITY[component],day=day,block=block,
             activation=minute(activation),night=False,risk=float(order['risk']),filled=bool(trade))
    if trade is None:
        row.update(release=minute(base+pd.Timedelta(minutes=order['expires'])),
                   observed_min=0.,adverse_min=0.,gross=0.,unknown=False)
    else:
        t=dict(trade,entry_time=base+pd.Timedelta(minutes=trade['entry_bar']),
               exit_time=base+pd.Timedelta(minutes=trade['exit_bar']))
        r={k:np.asarray(v[90:]) for k,v in p.items()}
        times=pd.date_range(base,periods=len(r['open']),freq='min')
        missing=times[~np.isfinite(np.column_stack(list(r.values()))).all(axis=1)]
        obs,adv,unknown=path_limits(t,times,r,missing)
        row.update(release=minute(t['exit_time'])+(not trade['exit_at_open']),
                   observed_min=obs,adverse_min=adv,gross=float(trade['gross_points']),unknown=unknown,
                   entry=trade['entry_price'],exit=trade['exit_price'],entry_time=str(t['entry_time']),
                   exit_time=str(t['exit_time']),reason=trade['reason'])
    return row


def night_candidate(label, old, frame, calendar):
    start=prior.globex_entry(old['day'],old['exit_day']);end=prior.h.at(old['exit_day'],'09:30')
    r=frame.loc[start:end]
    if start not in r.index or end not in r.index:
        raise ValueError('Frozen night endpoint missing; no substituted fill')
    if not r.index.is_unique or r.contract.nunique()!=1: raise ValueError('Mixed overnight contract')
    p={k:r[k].to_numpy(float) for k in sig.FIELDS}
    if not np.isfinite(np.column_stack(list(p.values()))).all(): raise ValueError('Invalid source price')
    entry=float(p['open'][0]); stop=None
    if label != 'S2_NO_STOP':
        factor=.75 if label=='S2_STOP075' else .50
        stop=sig.ceil_tick(entry-factor*old['atr'])
    end_ix=len(r)-1;price=float(p['open'][-1]);exit_open=True;reason='NEXT_OPEN'
    if stop is not None:
        for i in range(len(r)):
            if p['open'][i]<=stop:
                end_ix=i;price=float(p['open'][i]);reason='STOP_GAP';break
            if i<len(r)-1 and p['low'][i]<=stop:
                end_ix=i;price=stop;reason='STOP';exit_open=False;break
    finish=r.index[end_ix]
    t=dict(entry_price=entry,entry_time=start,exit_time=finish,exit_at_open=exit_open,
           direction=1,gross_points=price-entry,stop_price=stop)
    first=start.tz_convert('America/New_York').strftime('%Y-%m-%d')
    grid=[]
    for day in pd.bdate_range(first,old['exit_day']).strftime('%Y-%m-%d'):
        grid.extend(calendar.grid(day))
    grid=pd.DatetimeIndex(grid);grid=grid[(grid>=start)&(grid<end)]
    missing=grid.difference(r.index)
    obs,adv,unknown=path_limits(t,r.index,p,missing)
    if label in ('S1_STOP050','S2_NO_STOP'):
        # Exact old reference before applying the new account-level overlays.
        assert abs(old['entry_price']-entry)<1e-8
        assert abs(old['exit_price']-price)<1e-8
    return dict(component=label,priority=0,day=old['exit_day'],block=old['block'],
        activation=minute(start),release=minute(finish)+(not exit_open),risk=None if stop is None else entry-stop,
        night=True,filled=True,observed_min=obs,adverse_min=adv,gross=float(price-entry),unknown=unknown,
        entry=entry,exit=price,entry_time=str(start),exit_time=str(finish),reason=reason,
        contract=old['contract'],missing_before_exit=sum(x<finish for x in missing))


def build():
    prior.verify()
    data,cash,full,sources=prior.load_inputs()
    rows={block:{day:[] for day in days} for block,days in cash.items()}
    counts={k:dict(orders=0,fills=0,late_excluded=0) for k in [*SPECS,'PULLBACK']}
    cutoff_checks=0
    frozen=json.loads((ict.OUT/'run1/orders-and-ledgers.json').read_text())['TRADE_THROUGH']
    for block,d in data.items():
        d['groups']=dict(tuple(d['active'].groupby('trade_date')))
        reproduced={key:[] for key in SPECS}
        for day in d['dates']:
            p,ctx=ict.day_input(d,day)
            for label,name in SPECS.items():
                spec=next(s for s in ict.SPECS if s.name==name)
                order=sig.signal(p,ctx,spec)
                if order is None: continue
                prefix={k:v[:90+order['boundary']].copy() for k,v in p.items()}
                assert sig.signal(prefix,ctx,spec)==order
                cutoff_checks+=1
                trade,_=sig.execute(p,order,touch=False)
                if trade: reproduced[label].append((day,trade))
                # Restrict FIRST existing late order; never search a later one.
                if label in ('ICT1','SB_AM') and order['boundary']<45:
                    counts[label]['late_excluded']+=1;continue
                if not order['valid_target']:continue
                counts[label]['orders']+=1;counts[label]['fills']+=bool(trade)
                rows[block][day].append(intraday_candidate(label,day,block,p,ctx,order,trade))
            rth,base=d['state'][day];c=dict(base,**d['features'][day])
            ev=pv.select_g1(rth,c,c['prior_volumes'])
            if ev is not None:
                prefix={k:v[:ev['boundary']].copy() for k,v in rth.items()}
                assert pv.select_g1(prefix,c,c['prior_volumes'])==ev
                cutoff_checks+=1
                if ev['boundary']<45:
                    counts['PULLBACK']['late_excluded']+=1
                else:
                    trade,_=pv.execute(rth,c,'G1_ATR',ev)
                    if trade:
                        entry=trade['entry_price'];stop=min(ev['low'],pv.floor_tick(entry-.35*c['atr']))
                        trade.update(direction=1,stop_price=stop,initial_risk=entry-stop)
                        order=dict(boundary=ev['boundary'],expires=ev['boundary']+1,risk=entry-stop)
                        rows[block][day].append(intraday_candidate('PULLBACK',day,block,p,c,order,trade))
                        counts['PULLBACK']['orders']+=1;counts['PULLBACK']['fills']+=1
        for label,name in SPECS.items():
            old=[t for t in frozen[name] if t['block']==block]
            actual={day:t for day,t in reproduced[label]}
            assert len(old)==len(actual),(label,block)
            for t in old:
                new=actual[t['day']]
                for k in ('entry_price','exit_price','gross_points','net_points'):
                    assert abs(t[k]-new[k])<1e-8,(label,t['day'],k)
    stored=json.loads((prior.OUT/'run1/ledgers.json').read_text())
    for label,key in [('S1_STOP050','A_S1_18'),('S2_NO_STOP','A_S2_18'),
                      ('S2_STOP050','A_S2_18'),('S2_STOP075','A_S2_18')]:
        for t in stored[key]:
            rows[t['block']][t['exit_day']].append(night_candidate(label,t,full[t['block']][t['contract']],data[t['block']]['calendar']))
    for block,days in rows.items():
        for day,candidates in days.items():
            candidates.sort(key=lambda t:(t['activation'],t['priority'],t['component']))
    return cash,rows,dict(source_verification=sources,signal_counts=counts,
        cutoff_checks=cutoff_checks,kernel_parity='EXACT_FROZEN_STRICT_FILL_PRICE_PARITY',
        night_quality={label:dict(trades=sum(t['component']==label for ds in rows.values() for ts in ds.values() for t in ts),
            incomplete=sum(t['component']==label and t['unknown'] for ds in rows.values() for ts in ds.values() for t in ts))
            for label in ('S1_STOP050','S2_NO_STOP','S2_STOP050','S2_STOP075')})
