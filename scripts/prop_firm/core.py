import numpy as np
import pandas as pd
from scripts import prepare_historical_contracts as h
from scripts.two_pillar.core import pf


def globex_entry(signal_day,nextcash):
    """Last18NY before known nextcash09:30; handles weekends/holiday gaps causally."""
    previous=(pd.Timestamp(nextcash)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    start=h.at(previous,'18:00')
    if start<=h.at(signal_day,'16:00'):raise ValueError('Globex entry cannot precede known signal')
    return start


def flat_window_violation(t):
    start,end=pd.Timestamp(t['entry_time']),pd.Timestamp(t['exit_time'])
    if not t.get('exit_at_open',True):end+=pd.Timedelta(minutes=1)
    first=start.tz_convert('America/New_York').strftime('%Y-%m-%d')
    last=end.tz_convert('America/New_York').strftime('%Y-%m-%d')
    for day in pd.date_range(first,last).strftime('%Y-%m-%d'):
        if pd.Timestamp(day).weekday()>=5:continue
        if start<h.at(day,'18:00') and end>h.at(day,'16:10'):return True
    return False


def adverse_gross(t,times,prices):
    """Conservative OHLC loss bound while held, exclude exit-open future bars.

    Target exit's adverse extreme may be after target: conservative potential
    stress, explicitly not tick-certified. Stop exit uses known stop/open fill,
    never a post-stop low. Missing-minute tail risk is not reconstructed.
    """
    side=t.get('direction',1);entry=t['entry_price'];stop=t.get('stop_price')
    start,end=pd.Timestamp(t['entry_time']),pd.Timestamp(t['exit_time'])
    use=(times>=start)&(times<end)
    vals=(prices['low'][use]-entry) if side==1 else (entry-prices['high'][use])
    floor=min(0.,float(vals.min()) if len(vals) else 0.,t['gross_points'])
    if not t['exit_at_open'] and t['reason'].startswith('TARGET'):
        ix=np.flatnonzero(times==end)
        if len(ix):
            i=ix[0];v=prices['low'][i]-entry if side==1 else entry-prices['high'][i]
            if stop is not None:v=max(v,side*(stop-entry))
            floor=min(floor,float(v))
    return float(floor)


def dollar_panel(rows,dates,cost,quantity):
    """Fixed MNQ quantity, $2/point, explicit RT cost; never NQnet/10."""
    days={d:dict(net=0.,minimum=0.,observed_minimum=0.,N=0,active=False) for d in dates}
    equity=peak=drawdown=0.;trade_pnl=[]
    for t in sorted(rows,key=lambda v:pd.Timestamp(v['entry_time'])):
        d=days[t['exit_day']];scale=2*quantity;fees=cost*quantity
        gross_marks=np.asarray(t['path_points'])+1.225
        marks=gross_marks*scale-fees
        path=equity+marks
        drawdown=max(drawdown,float(np.max(np.maximum.accumulate(np.r_[peak,path])[1:]-path)))
        peak=max(peak,float(path.max()))
        d['observed_minimum']=min(d['observed_minimum'],d['net']+float(marks.min()))
        d['minimum']=min(d['minimum'],d['net']+t['adverse_gross_points']*scale-fees)
        value=t['gross_points']*scale-fees
        equity+=value;trade_pnl.append(value);d['net']+=value;d['N']+=1;d['active']=True
    values=np.array([d['net'] for d in days.values()]);cum=np.r_[0,np.cumsum(values)];sd=values.std(ddof=1)
    worst=float(min(d['minimum'] for d in days.values()))
    return days,dict(N=len(rows),net_USD=float(values.sum()),trade_PF_USD=pf(trade_pnl),
       marked_drawdown_USD=drawdown,EOD_close_drawdown_USD=float(max(np.maximum.accumulate(cum)-cum)),
       worst_session_adverse_USD=worst,largest_profit_day_USD=float(max(0.,values.max())),
       daily_sharpe_USD=float(np.sqrt(252)*values.mean()/sd) if sd>0 else None,
       assumed_RT_cost_per_contract=cost,MNQ_quantity=quantity)


def account_check(days,profile):
    """EOD floor ratchets only at EOD; intraday losses test current floor.

    Unmodified strategy shadow path after firstDLL/MLL is diagnostic only;
    no fabricated liquidation fill and no counterfactual evaluation pass.
    """
    balance=0.;floor=-profile['drawdown'];peak_eod=0.;best=0.;active=0
    observed_breach=potential_breach=dll=first_target=first_ready=None
    last_active=next(iter(days),None);max_gap=0;inactive=None;best30=None
    for day,r in days.items():
        if last_active is not None:
            gap=(pd.Timestamp(day)-pd.Timestamp(last_active)).days
            max_gap=max(max_gap,gap)
            if profile.get('inactivity_days') and gap>=profile['inactivity_days'] and inactive is None:inactive=day
        if balance+r['observed_minimum']<=floor and observed_breach is None:observed_breach=day
        if balance+r['minimum']<=floor and potential_breach is None:potential_breach=day
        if profile['dll'] is not None and r['minimum']<=-profile['dll'] and dll is None:dll=day
        balance+=r['net'];best=max(best,r['net'])
        if r['active']:active+=1;last_active=day
        ratio=best/balance if balance>0 else None
        if ratio is not None and ratio<=.30 and active>=4 and best30 is None:best30=day
        target=profile['target']
        if target is not None and balance>=target and first_target is None:first_target=day
        enough=profile['consistency'] is None or (ratio is not None and ratio<=profile['consistency'])
        if target is not None and balance>=target and enough and active>=profile['min_days'] and first_ready is None:first_ready=day
        peak_eod=max(peak_eod,balance)
        floor=max(floor,min(profile['lock'],peak_eod-profile['drawdown']))
    gates=[v for v in (potential_breach,dll,inactive) if v is not None]
    first_gate=min(gates) if gates else None
    ready_valid=first_ready is not None and (first_gate is None or first_ready<first_gate) and not profile['news_gate']
    status='NO_OBSERVED_LIMIT_TRIGGER_WITHIN_ASSUMPTIONS'
    if potential_breach:status='OBSERVED_MLL_BREACH' if observed_breach else 'POTENTIAL_MLL_BREACH_OHLC_BOUND'
    if dll and (potential_breach is None or dll<potential_breach):status='DLL_SOFT_PAUSE_REQUIRES_CHANGED_EXECUTION'
    if inactive and (first_gate==inactive):status='INACTIVITY_DIAGNOSTIC'
    if profile['news_gate']:status='NEWS_CALENDAR_NOT_VERIFIED'
    return dict(profile=profile['id'],risk_status=status,first_observed_MLL=observed_breach,first_potential_MLL=potential_breach,
        first_DLL_soft_pause=dll,inactivity_first_diagnostic=inactive,longest_calendar_gap=max_gap,
        first_profit_target=first_target,first_target_and_consistency=first_ready,evaluation_ready_before_risk_trigger=ready_valid,
        final_shadow_profit=balance,best_day_USD=best,best_day_fraction_of_net=best/balance if balance>0 else None,
        required_profit_for_30pct=best/.30,consistency30_at_end=balance>0 and best/balance<=.30,
        first_30pct_and_four_active_days=best30,ending_floor=floor,full_compliance_certified=False,
        path_after_first_risk_trigger='COUNTERFACTUAL_SHADOW_NO_EXECUTED_RISK_OVERLAY',news_gate_pending=profile['news_gate'])
