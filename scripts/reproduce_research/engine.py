"""Reproducible local NQ contract-aware exploratory batch. No live execution."""
from __future__ import annotations
from pathlib import Path
import sys
import json
import hashlib
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
from . import barchart as source

OUT = ROOT / 'dashboard'
DATA = ROOT / 'data/overnight_nq'
NY = 'America/New_York'
COST = 1.225  # 2 * 2 ticks * .25 points + $4.50 / $20
SEED = 20261020
SNAPS = ['09:30', '09:45', '10:00', '10:30']
SOURCE_HASHES = []
CONFIG = {
    'roll_trade_date': '2025-03-19', 'roll_timestamp_utc': '2025-03-18T22:00:00Z',
    'tick_points': .25, 'point_value_usd': 20, 'slippage_ticks_per_side': 2,
    'commission_rt_usd': 4.50, 'cost_rt_points': COST, 'cost_rt_usd': COST*20,
    'atr': 'SMA of last 14 valid completed RTH true ranges, same contract only; no warmup substitution',
    'vwap': 'Session 18:00 NY anchored volume-weighted HLC3 proxy; population weighted SD of HLC3, not trade-level VWAP',
    'vcr': 'last 30 contiguous 1m log-return population SD / median same-clock SD from prior 20 observations, minimum 10',
    'rvol': 'cumulative session volume / median same-clock cumulative volume of prior 20 complete prefixes, minimum 10',
    'orb_volume': 'completed breakout bar volume / median same NY minute volume from prior 20 sessions, minimum 10',
    'ATR_history': 'Invalid RTH or its immediately following TR omitted, last 14 valid TR observations required',
    'signal_timing': 'Signals use completed minute bars; entry next exact-minute open. All positions flat by noon.',
    'A': 'London sweep high or low 08:30-10:15, strict close back inside range, then directional VWAP close cross on same/later completed bar before 10:15; first signal per day',
    'B': 'ORB5 and ORB15 separately: first close beyond completed range 09:35/09:45-11:00, volume >1.5x prior same-clock median and close on same VWAP side',
    'C': 'First close with |VWAP z|>2 during 10:30-11:30, fade toward VWAP frozen at signal, only if target lies in profit direction at next open',
    'risk': 'A/B SL 0.25 prior ATR and TP 0.50 prior ATR; C SL 0.25 ATR and frozen VWAP TP. Distances floored/ceiled conservatively to tick grid. Fixed, not optimized.',
    'fills': 'One trade per strategy/day, independent strategies not combined portfolio. Gap SL fills worse open; gap TP capped target. Same bar SL+TP -> SL. Costs charged on every exit.',
    'D': 'Overnight 18:00-09:30 high-low / prior ATR: narrow <0.5, broad >1.2, middle otherwise; conditioning four entry times and four horizons',
    'split': 'Chronological trading-date halves shared across all analyses, not split by trade counts',
    'inference': '5-trading-day circular moving-block bootstrap on daily PnL including zero-trade eligible dates; 2000 replicates; Holm across four strategy screens per quality view; exploratory, no independent holdout',
}


def clean(v):
    if isinstance(v, dict):
        return {str(k): clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (float, np.floating)):
        return float(v) if np.isfinite(v) else None
    if isinstance(v, (pd.Timestamp, datetime)):
        return v.isoformat()
    return v


def js(name, obj):
    (OUT/name).write_text(json.dumps(clean(obj), allow_nan=False, indent=2)+'\n')


def hashfile(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def time_at(day, hm):
    return pd.Timestamp(f'{day} {hm}', tz=NY).tz_convert('UTC')


def window(g, start, end):
    return g.loc[(g.index >= start) & (g.index < end)]


def complete(w, start, end):
    return w.index.equals(pd.date_range(start, end, freq='min', inclusive='left'))


def load_contract(contract, suffixes):
    parts = []
    for s in suffixes:
        p = source.DOWNLOADS / f'{contract.lower()}_intraday-1min_historical-data-10-19-2026{s}.csv'
        g, meta = source.load(p)
        SOURCE_HASHES.append(meta)
        parts.append(g)
    g = pd.concat(parts)
    dup = g.loc[g.index.duplicated(False)]
    assert not dup.groupby(level=0)[source.FIELDS].nunique().gt(1).any().any()
    g = g.loc[~g.index.duplicated()].sort_index()
    g['contract'] = contract
    g['trade_date'] = source.trade_dates(g.index).strftime('%Y-%m-%d')
    return g


def expected_grid(day):
    start = time_at(day, '00:00') - pd.DateOffset(hours=6)
    # Construct previous-calendar-day 18:00 explicitly, including NY DST.
    prev = (pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    start = time_at(prev, '18:00')
    end = time_at(day, '17:00')
    grid = pd.date_range(start, end, freq='min', inclusive='left')
    if day == '2025-01-01':
        return grid[:0]
    if day == '2025-01-09':
        grid = grid[grid < time_at(day, '09:30')]
    if day in ['2025-01-20', '2025-02-17']:
        grid = grid[grid < time_at(day, '13:00')]
    return grid


def build_features(full):
    enriched, dailies, snapshots, gaps = [], [], [], []
    for contract, allg in full.groupby('contract'):
        history = []
        clock_vol = {}
        snap_history = {h: [] for h in SNAPS}
        for day, raw in allg.groupby('trade_date', sort=True):
            g = raw.copy()
            exp = expected_grid(day)
            missing = exp.difference(g.index)
            extra = g.index.difference(exp)
            assert len(extra) == 0, (day, extra)
            r0, r1 = time_at(day,'09:30'), time_at(day,'16:00')
            rth = window(g,r0,r1)
            full_rth = complete(rth,r0,r1)
            special = day in ['2025-01-09','2025-01-20','2025-02-17']
            flag = ('special_session;' if special else '') + ('missing_minutes;' if len(missing) else '')
            flag = flag.rstrip(';') or 'ok'
            for t in missing:
                gaps.append({'contract':contract,'trade_date':day,'timestamp_utc':t,'timestamp_ny':t.tz_convert(NY)})
            prev = history[-1] if history else None
            valid_tr = [x['rth_tr'] for x in history if np.isfinite(x['rth_tr'])]
            atr = float(np.mean(valid_tr[-14:])) if len(valid_tr)>=14 else np.nan
            pdh = prev['rth_high'] if prev and prev['rth_complete'] else np.nan
            pdl = prev['rth_low'] if prev and prev['rth_complete'] else np.nan
            prevclose = prev['rth_close'] if prev and prev['rth_complete'] else np.nan
            ranges = {}
            prevday = (pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            bounds = {'asia':(time_at(prevday,'18:00'),time_at(day,'03:00')),
                      'london':(time_at(day,'03:00'),time_at(day,'08:30')),
                      'premarket':(time_at(day,'08:30'),r0),
                      'overnight':(time_at(prevday,'18:00'),r0)}
            for label,(a,b) in bounds.items():
                w = window(g,a,b)
                good = complete(w,a,b)
                ranges[label+'_high'] = float(w.high.max()) if good else np.nan
                ranges[label+'_low'] = float(w.low.min()) if good else np.nan
                ranges[label+'_complete'] = good
                # Attach only once the complete window has finished, never before.
                for side in ['high','low']:
                    g[label+'_'+side] = np.where(g.index>=b,ranges[label+'_'+side],np.nan)
            midnight = time_at(day,'00:00')
            mo = float(g.at[midnight,'open']) if midnight in g.index else np.nan
            g['midnight_open'] = np.where(g.index>=midnight,mo,np.nan)
            for n in [5,15,30]:
                end = r0+pd.Timedelta(minutes=n)
                w = window(g,r0,end)
                good = complete(w,r0,end)
                for side in ['high','low']:
                    value = float(getattr(w,side).max() if side=='high' else getattr(w,side).min()) if good else np.nan
                    ranges[f'orb{n}_{side}'] = value
                    g[f'orb{n}_{side}'] = np.where(g.index>=end,value,np.nan)
                width = ranges[f'orb{n}_high']-ranges[f'orb{n}_low']
                ranges[f'orb{n}_range_points'] = width
                ranges[f'orb{n}_range_pct_atr'] = 100*width/atr if atr>0 else np.nan
                g[f'orb{n}_range_pct_atr'] = np.where(g.index>=end,ranges[f'orb{n}_range_pct_atr'],np.nan)
            g['pdh'], g['pdl'], g['atr14_prior'] = pdh, pdl, atr
            g['data_quality_flag'] = flag
            g['history_quality_flag'] = 'ok' if np.isfinite(atr) else 'atr_warmup'
            typical = (g.high+g.low+g.close)/3
            cv = g.volume.cumsum()
            vw = (typical*g.volume).cumsum()/cv
            var = ((typical.pow(2)*g.volume).cumsum()/cv-vw.pow(2)).clip(lower=0)
            # These columns become available at timestamp + 1 minute.
            g['vwap_close'] = vw
            g['vwap_sd_close'] = np.sqrt(var)
            g['vwap_z_close'] = (g.close-vw)/g.vwap_sd_close.replace(0,np.nan)
            g['feature_available_at_utc'] = g.index+pd.Timedelta(minutes=1)
            contiguous = g.index.to_series().diff().eq(pd.Timedelta(minutes=1))
            g['return_1m'] = np.log(g.close/g.close.shift()).where(contiguous)
            g['volatility_30m_close'] = g.return_1m.rolling(30,min_periods=30).std(ddof=0)
            vol_reference = []
            for t in g.index:
                hm = t.tz_convert(NY).strftime('%H:%M')
                prior = clock_vol.get(hm,[])
                vol_reference.append(float(np.median(prior[-20:])) if len(prior)>=10 else np.nan)
            g['prior_same_minute_median_volume'] = vol_reference
            for hm in SNAPS:
                at = time_at(day,hm)
                pre = window(g,time_at(prevday,'18:00'),at)
                prefix_good = complete(pre,time_at(prevday,'18:00'),at)
                prevminute = at-pd.Timedelta(minutes=1)
                last = g.loc[prevminute] if prevminute in g.index else None
                past = snap_history[hm]
                vols = [x['cumulative_volume'] for x in past if x['prefix_complete']]
                sigmas = [x['sigma30'] for x in past if np.isfinite(x['sigma30'])]
                medvol = float(np.median(vols[-20:])) if len(vols)>=10 else np.nan
                medsigma = float(np.median(sigmas[-20:])) if len(sigmas)>=10 else np.nan
                sigma = float(last.volatility_30m_close) if last is not None else np.nan
                row = {'contract':contract,'trade_date':day,'asof_ny':hm,'asof_utc':at,
                       'data_quality_flag':flag,'atr14_prior':atr,'atr_history_count':min(14,len(valid_tr)),
                       'prefix_complete':prefix_good,'cumulative_volume':int(pre.volume.sum()),
                       'vwap':float(last.vwap_close) if last is not None and prefix_good else np.nan,
                       'vwap_z':float(last.vwap_z_close) if last is not None and prefix_good else np.nan,
                       'sigma30':sigma, 'vcr':sigma/medsigma if medsigma>0 else np.nan,
                       'relative_volume':float(pre.volume.sum())/medvol if prefix_good and medvol>0 else np.nan,
                       'overnight_range_atr':(ranges['overnight_high']-ranges['overnight_low'])/atr if atr>0 else np.nan,
                       'baseline_history_n_volume':min(20,len(vols)), 'baseline_history_n_vcr':min(20,len(sigmas))}
                snapshots.append(row)
                snap_history[hm].append(row)
            # Update reference histories only AFTER all features for this day.
            for t, volume in g.volume.items():
                clock_vol.setdefault(t.tz_convert(NY).strftime('%H:%M'),[]).append(float(volume))
            tr = max(float(rth.high.max()-rth.low.min()),abs(float(rth.high.max())-prevclose),abs(float(rth.low.min())-prevclose)) if full_rth and np.isfinite(prevclose) else np.nan
            daily = {'contract':contract,'trade_date':day,'data_quality_flag':flag,
                     'missing_minutes':len(missing),'expected_minutes':len(exp),'observed_minutes':len(g),
                     'rth_complete':full_rth,'rth_high':float(rth.high.max()) if full_rth else np.nan,
                     'rth_low':float(rth.low.min()) if full_rth else np.nan,
                     'rth_close':float(rth.close.iloc[-1]) if full_rth else np.nan,
                     'rth_tr':tr,'atr14_prior':atr,'atr_history_count':min(14,len(valid_tr)),
                     'pdh':pdh,'pdl':pdl,'midnight_open':mo,
                     'overnight_range_atr':(ranges['overnight_high']-ranges['overnight_low'])/atr if atr>0 else np.nan,
                     **ranges}
            history.append(daily)
            dailies.append(daily)
            enriched.append(g)
    return pd.concat(enriched).sort_index(),pd.DataFrame(dailies),pd.DataFrame(snapshots),pd.DataFrame(gaps)


def selected(df):
    return ((df.contract.eq('NQH25') & df.trade_date.le('2025-03-18')) |
            (df.contract.eq('NQM25') & df.trade_date.ge('2025-03-19')))


def baseline(master):
    rows = []
    for day,g in master.groupby('trade_date'):
        for hm in SNAPS:
            start = time_at(day,hm)
            if start not in g.index:
                continue
            for horizon in ['15m','30m','60m','noon']:
                end = time_at(day,'12:00') if horizon=='noon' else start+pd.Timedelta(minutes=int(horizon[:-1]))
                w = window(g,start,end)
                if not complete(w,start,end):
                    continue
                price = float(w.open.iloc[0])
                for side in [1,-1]:
                    gross = side*(float(w.close.iloc[-1])-price)
                    mfe = max(0,float(w.high.max())-price) if side==1 else max(0,price-float(w.low.min()))
                    mae = max(0,price-float(w.low.min())) if side==1 else max(0,float(w.high.max())-price)
                    rows.append({'trade_date':day,'contract':g.contract.iloc[0], 'entry_ny':hm,'entry_utc':start,
                                 'horizon':horizon,'direction':side,'entry_price':price,
                                 'gross_points':gross,'gross_bps':gross/price*10000,'net_points':gross-COST,
                                 'mfe_points':mfe,'mae_points':mae,'mfe_bps':mfe/price*10000,'mae_bps':mae/price*10000,
                                 'data_quality_flag':g.data_quality_flag.iloc[0]})
    return pd.DataFrame(rows)


def simulate(g, signal, direction, stopdist, targetdist=None, target=None):
    entry = signal+pd.Timedelta(minutes=1)
    end = time_at(g.trade_date.iloc[0],'12:00')
    w = window(g,entry,end)
    if not complete(w,entry,end) or len(w)==0:
        return None
    px = float(w.open.iloc[0])
    stopdist = max(.25,np.floor(stopdist/.25)*.25)
    stop = px-direction*stopdist
    if target is None:
        target = px+direction*max(.25,np.ceil(targetdist/.25)*.25)
    else:
        target = (np.floor(target/.25) if direction==1 else np.ceil(target/.25))*.25
        if direction*(target-px)<=0:
            return None
    exitprice = float(w.close.iloc[-1]); exittime=w.index[-1]; reason='noon'; ambiguous=False
    for t,r in w.iterrows():
        sl = r.low<=stop if direction==1 else r.high>=stop
        tp = r.high>=target if direction==1 else r.low<=target
        if sl or tp:
            ambiguous = bool(sl and tp)
            if sl:
                exitprice = min(stop,float(r.open)) if direction==1 else max(stop,float(r.open))
                reason='stop_both' if ambiguous else 'stop'
            else:
                exitprice=target; reason='target'
            exittime=t
            break
    gross = direction*(exitprice-px)
    # Exit minute extremes may occur after exit; report these only as bounds.
    path = w.loc[:exittime]
    return {'trade_date':g.trade_date.iloc[0],'contract':g.contract.iloc[0], 'signal_utc':signal,
            'entry_utc':entry,'exit_bar_utc':exittime,'entry_price':px,'exit_price':exitprice,
            'direction':direction,'stop':stop,'target':target,'exit_reason':reason,'both_hit_bar':ambiguous,
            'gross_points':gross,'net_points':gross-COST,'net_usd':(gross-COST)*20,
            'mfe_bar_bound_points':max(0,float(path.high.max())-px) if direction==1 else max(0,px-float(path.low.min())),
            'mae_bar_bound_points':max(0,px-float(path.low.min())) if direction==1 else max(0,float(path.high.max())-px),
            'data_quality_flag':g.data_quality_flag.iloc[0]}


def hypotheses(master):
    rows=[]; eligibility=[]
    for day,g in master.groupby('trade_date'):
        atr=float(g.atr14_prior.iloc[0])
        for strategy in ['A_London_sweep','B_ORB5','B_ORB15','C_VWAP_extreme']:
            a = time_at(day,'08:30') if strategy.startswith('A') else time_at(day,'09:30') if strategy.startswith('B') else time_at(day,'10:30')
            end=time_at(day,'12:00')
            eligible=np.isfinite(atr) and atr>0 and complete(window(g,a,end),a,end)
            # VWAP source prefix must also be complete, independently of clean-day filter.
            prevday=(pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            eligible=eligible and complete(window(g,time_at(prevday,'18:00'),end),time_at(prevday,'18:00'),end)
            if strategy.startswith('B'):
                n=5 if strategy=='B_ORB5' else 15
                refs=window(g,time_at(day,'09:30'),time_at(day,'11:00')).prior_same_minute_median_volume
                eligible=eligible and len(refs)>0 and refs.notna().all()
            eligibility.append({'strategy':strategy,'trade_date':day,'eligible':bool(eligible),'data_quality_flag':g.data_quality_flag.iloc[0]})
            if not eligible:
                continue
            candidate=None
            if strategy.startswith('A'):
                london=window(g,time_at(day,'03:00'),time_at(day,'08:30'))
                if not complete(london,time_at(day,'03:00'),time_at(day,'08:30')):
                    continue
                hi,lo=float(london.high.max()),float(london.low.min())
                swept_high=swept_low=inside_after_high=inside_after_low=False
                for t,r in window(g,a,time_at(day,'10:15')).iterrows():
                    prior=g.loc[t-pd.Timedelta(minutes=1)]
                    swept_high=swept_high or r.high>hi
                    swept_low=swept_low or r.low<lo
                    inside=lo<r.close<hi
                    inside_after_high=inside_after_high or (swept_high and inside)
                    inside_after_low=inside_after_low or (swept_low and inside)
                    crossdown=prior.close>=prior.vwap_close and r.close<r.vwap_close
                    crossup=prior.close<=prior.vwap_close and r.close>r.vwap_close
                    # If both directions qualify in one bar, omit ambiguous signal.
                    short=inside_after_high and inside and crossdown
                    long=inside_after_low and inside and crossup
                    if bool(short)^bool(long):
                        candidate=simulate(g,t,1 if long else -1,.25*atr,.5*atr)
                        if candidate:
                            break
            elif strategy.startswith('B'):
                endorb=time_at(day,'09:30')+pd.Timedelta(minutes=n)
                orb=window(g,time_at(day,'09:30'),endorb)
                hi,lo=float(orb.high.max()),float(orb.low.min())
                for t,r in window(g,endorb,time_at(day,'11:00')).iterrows():
                    side=1 if r.close>hi else -1 if r.close<lo else 0
                    if side and r.volume>1.5*r.prior_same_minute_median_volume and side*(r.close-r.vwap_close)>0:
                        candidate=simulate(g,t,side,.25*atr,.5*atr)
                        if candidate:
                            break
            else:
                for t,r in window(g,a,time_at(day,'11:30')).iterrows():
                    if abs(r.vwap_z_close)>2:
                        candidate=simulate(g,t,-int(np.sign(r.vwap_z_close)),.25*atr,target=float(r.vwap_close))
                        if candidate:
                            break
            if candidate:
                rows.append({'strategy':strategy,**candidate})
    cols=['strategy','trade_date','contract','signal_utc','entry_utc','exit_bar_utc','entry_price','exit_price','direction','stop','target','exit_reason','both_hit_bar','gross_points','net_points','net_usd','mfe_bar_bound_points','mae_bar_bound_points','data_quality_flag']
    return pd.DataFrame(rows,columns=cols),pd.DataFrame(eligibility)


def bootstrap(x):
    x=np.asarray(x,dtype=float)
    if len(x)<20:
        return {'ci_low':None,'ci_high':None,'p_value':None}
    rng=np.random.default_rng(SEED)
    starts=rng.integers(0,len(x),size=(2000,int(np.ceil(len(x)/5))))
    ix=((starts[:,:,None]+np.arange(5))%len(x)).reshape(2000,-1)[:,:len(x)]
    means=x[ix].mean(axis=1)
    centered=means-x.mean()
    return {'ci_low':float(np.quantile(means,.025)), 'ci_high':float(np.quantile(means,.975)),
            'p_value':float((1+(abs(centered)>=abs(x.mean())).sum())/2001)}


def holm(ps):
    p=np.array([v if v is not None else 1 for v in ps]); order=np.argsort(p)
    adjusted=np.maximum.accumulate(p[order]*(len(p)-np.arange(len(p))))
    out=np.ones(len(p)); out[order]=np.minimum(1,adjusted)
    return out


def metrics(t, eligible_dates):
    x=t.net_points.to_numpy(dtype=float)
    wins=x[x>0].sum(); losses=-x[x<0].sum()
    eq=np.r_[0,np.cumsum(x)]
    daily=t.groupby('trade_date').net_points.sum().reindex(eligible_dates,fill_value=0)
    return {'trades':len(t),'days':int(t.trade_date.nunique()),'eligible_days':len(eligible_dates),
            'net_points':float(x.sum()),'net_usd':float(x.sum()*20),
            'mean_net_points':float(x.mean()) if len(x) else None,
            'mean_net_bps':float((t.net_points/t.entry_price*10000).mean()) if len(x) else None,
            'win_rate':float((x>0).mean()) if len(x) else None,
            'profit_factor':float(wins/losses) if losses>0 else None,
            'profit_factor_no_losses':bool(len(x)>0 and losses==0),
            'max_drawdown_points':float((np.maximum.accumulate(eq)-eq).max()),
            'median_net_points':float(np.median(x)) if len(x) else None,
            'bootstrap_unit':'eligible-day net points including no-trade zero days',**bootstrap(daily)}


def summarize_baselines(b):
    output=[]
    for keys,t in b.groupby(['quality_view','half','entry_ny','horizon','direction'],dropna=False):
        q,h,hm,hor,side=keys
        output.append({'quality_view':q,'half':h,'entry_ny':hm,'horizon':hor,'direction':side,
                       'n':len(t),'mean_gross_points':t.gross_points.mean(),'mean_net_points':t.net_points.mean(),
                       'win_rate_net':t.net_points.gt(0).mean(),
                       **{f'{name}_{k}':t[col].quantile(v) for name,col in [('return_points','gross_points'),('mfe_points','mfe_points'),('mae_points','mae_points')]
                          for k,v in [('p05',.05),('p25',.25),('p50',.5),('p75',.75),('p95',.95)]}})
    return pd.DataFrame(output)


def verify(master, daily, snapshots, trades):
    assert master.index.is_unique and master.index.is_monotonic_increasing
    assert master.contract.eq('NQH25').equals(master.trade_date.le('2025-03-18'))
    for _,g in master.groupby(['contract','trade_date']):
        assert pd.isna(g.return_1m.iloc[0])
        assert np.isclose(g.vwap_close.iloc[0],(g.high.iloc[0]+g.low.iloc[0]+g.close.iloc[0])/3)
        day=g.trade_date.iloc[0]
        assert g.loc[g.index<time_at(day,'09:35'),'orb5_high'].isna().all()
        assert g.loc[g.index<time_at(day,'08:30'),'london_high'].isna().all()
    assert time_at('2025-03-07','09:30').hour==14
    assert time_at('2025-03-10','09:30').hour==13
    assert np.isclose(COST*20,24.5)
    if len(trades):
        assert ((trades.entry_utc-trades.signal_utc)==pd.Timedelta(minutes=1)).all()
        assert np.allclose(trades.gross_points-trades.net_points,COST)
        assert trades.loc[trades.both_hit_bar,'exit_reason'].eq('stop_both').all()
        for strategy,hm in [('B_ORB5','09:35'),('B_ORB15','09:45')]:
            for _,r in trades.loc[trades.strategy.eq(strategy)].iterrows():
                assert r.signal_utc>=time_at(r.trade_date,hm)
    # Synthetic worst-case/gap tests on the actual fill engine.
    ix=pd.date_range(time_at('2025-02-04','11:58'),periods=2,freq='min')
    fake=pd.DataFrame({'open':[100,100],'high':[103,100],'low':[97,100],'close':[100,100],
                       'trade_date':'2025-02-04','contract':'NQH25','data_quality_flag':'ok'},index=ix)
    test=simulate(fake,ix[0]-pd.Timedelta(minutes=1),1,2,2)
    assert test['exit_price']==98 and test['exit_reason']=='stop_both'
    fake.loc[ix[0],['open','high','low','close']]=[97,98,96,97]
    fake.loc[ix[1],['open','high','low','close']]=[94,95,93,94]
    gaptest=simulate(fake,ix[0]-pd.Timedelta(minutes=1),1,2,20)
    assert gaptest['exit_price']==94 and gaptest['exit_reason']=='stop'
    # Verify that truncating the future cannot change session features already calculated.
    return {'unique_sorted_index':True,'roll_selection':True,'no_cross_contract_or_day_returns':True,
            'vwap_resets':True,'anchor_availability_masks':True,'dst_checks':True,
            'cost_reconciliation':True,'next_bar_entries':True,'orb5_vs_orb15_distinct_windows':True,
            'synthetic_worst_case_fill':True,'synthetic_gap_stop_fill':True}


def main():
    OUT.mkdir(exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    print('Loading immutable raw exports...',flush=True)
    h=load_contract('NQH25',['','-2','-3','-4','-5','-6','-7','-8'])
    m=load_contract('NQM25',['','-2','-3'])
    print('Computing features per contract and trading day...',flush=True)
    full,daily,snap,gaps=build_features(pd.concat([h,m]))
    master=full.loc[selected(full)].sort_index()
    daily=daily.loc[selected(daily)].sort_values('trade_date').reset_index(drop=True)
    snap=snap.loc[selected(snap)].sort_values(['trade_date','asof_ny'])
    gaps=gaps.loc[selected(gaps)]
    dates=sorted(master.trade_date.unique()); midpoint=len(dates)//2
    halfmap={d:'first' if i<midpoint else 'second' for i,d in enumerate(dates)}
    daily['half']=daily.trade_date.map(halfmap)
    snap['half']=snap.trade_date.map(halfmap)
    print('Baseline paths and fixed hypotheses...',flush=True)
    base=baseline(master); trades,eligible=hypotheses(master)
    base['half']=base.trade_date.map(halfmap); trades['half']=trades.trade_date.map(halfmap)
    regimes=daily[['trade_date','overnight_range_atr']].copy()
    regimes['regime']=np.select([regimes.overnight_range_atr.lt(.5),regimes.overnight_range_atr.gt(1.2),regimes.overnight_range_atr.notna()],['narrow','broad','middle'],default='unavailable')
    base=base.merge(regimes,on='trade_date',validate='many_to_one')
    results=[]; curves=[]; eligibility_summary=[]; baseline_views=[]
    for quality_view in ['all','clean']:
        b=base if quality_view=='all' else base.loc[base.data_quality_flag.eq('ok')]
        baseline_views.append(b.assign(quality_view=quality_view))
        for strategy in eligible.strategy.unique():
            e=eligible.loc[eligible.strategy.eq(strategy)&eligible.eligible]
            t=trades.loc[trades.strategy.eq(strategy)]
            if quality_view=='clean':
                e=e.loc[e.data_quality_flag.eq('ok')]; t=t.loc[t.data_quality_flag.eq('ok')]
            ed=sorted(e.trade_date.unique())
            met=metrics(t,ed)
            splits={part:metrics(t.loc[t.half.eq(part)],[d for d in ed if halfmap[d]==part]) for part in ['first','second']}
            stable=all(splits[p]['trades']>=10 and splits[p]['mean_net_points']>0 for p in splits)
            label=f'{strategy}_{quality_view}'
            r={'id':label,'name':strategy,'question':CONFIG[strategy[0]],'status':'EXPLORATORY_INSUFFICIENT_INDEPENDENT_VALIDATION',
               'quality_view':quality_view,'direction':'signal_defined','entry':'next completed-signal bar open','timezone':NY,
               'horizon_minutes':150,'metrics':met,'splits':splits,'yearly':{'2025':met},
               'cost_scenarios':{'base':{'round_trip_points':COST,**met},'double_slippage':{'round_trip_points':2.225,**metrics(t.assign(net_points=t.gross_points-2.225),ed)}},
               'limitations':'Exploratory fixed specification; no tick/orderbook fills; overlapping strategies not a combined portfolio; terminal-bar MFE/MAE are bounds.',
               'baseline':'Unconditional same-clock forward paths exported separately; no claim of excess alpha',
               'data_version':hashlib.sha256(''.join(x['sha256'] for x in SOURCE_HASHES).encode()).hexdigest(),
               'config_version':hashlib.sha256(json.dumps(CONFIG,sort_keys=True).encode()).hexdigest(),
               'run_id':label+'-20261020','positive_both_halves_min10_trades':stable,
               'equity':[{'date':d,'net_points':float(v)} for d,v in t.groupby('trade_date').net_points.sum().reindex(ed,fill_value=0).cumsum().items()]}
            results.append(r)
            for row in r['equity']:
                curves.append({'strategy':strategy,'quality_view':quality_view,**row,'net_usd':row['net_points']*20})
            eligibility_summary.append({'strategy':strategy,'quality_view':quality_view,'eligible_days':len(ed),'trades':len(t),'all_selected_days':len(dates)})
        subset=[r for r in results if r['quality_view']==quality_view]
        for r,q in zip(subset,holm([r['metrics']['p_value'] for r in subset])):
            r['q_value']=float(q);r['significant_fdr_005']=False
            r['holm_adjusted_p']=float(q)
            r['significant_holm_005']=q<.05 and r['metrics']['p_value'] is not None
            r['validated_edge']=False
    bv=pd.concat(baseline_views)
    bsummary=summarize_baselines(pd.concat([bv,bv.assign(half='all')]))
    cond=[]
    conditioned=pd.concat([bv,bv.assign(half='all')])
    for keys,t in conditioned.loc[conditioned.regime.ne('unavailable')].groupby(['quality_view','half','regime','entry_ny','horizon','direction']):
        q,half,reg,hm,hor,direction=keys
        n=len(t); wins=int(t.net_points.gt(0).sum())
        z=1.96; p=wins/n; den=1+z*z/n
        center=(p+z*z/(2*n))/den; margin=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
        cond.append({'quality_view':q,'half':half,'regime':reg,'entry_ny':hm,'horizon':hor,'direction':direction,'n':n,
                     'positive_gross_probability':t.gross_points.gt(0).mean(),'positive_net_probability':p,
                     'wilson_low':center-margin,'wilson_high':center+margin,'mean_net_points':t.net_points.mean(),
                     'median_mfe_points':t.mfe_points.median(),'median_mae_points':t.mae_points.median(),
                     'note':'Descriptive overlapping paths; Wilson independence assumption approximate, no multiple-comparison significance claim'})
    checks=verify(master,daily,snap,trades)
    # A prefix rerun proves actual future invariance, rather than only documenting timing.
    cutoff='2025-02-14'; short=full.loc[full.contract.eq('NQH25') & full.trade_date.le(cutoff),source.FIELDS+['contract','trade_date']]
    prefix,_,ps,_=build_features(short)
    original=full.loc[full.contract.eq('NQH25') & full.trade_date.le(cutoff)]
    pd.testing.assert_frame_equal(prefix,original,check_freq=False)
    pd.testing.assert_frame_equal(ps.reset_index(drop=True),snap.loc[snap.contract.eq('NQH25') & snap.trade_date.le(cutoff)].drop(columns='half').reset_index(drop=True),check_dtype=False)
    checks['future_truncation_invariance']=True
    print('Writing CSV/Parquet and dashboard exports...',flush=True)
    master.index.name='timestamp_utc'
    master.to_parquet(DATA/'NQ_point_in_time_1min.parquet',compression='zstd')
    master.to_csv(DATA/'NQ_point_in_time_1min.csv',date_format='%Y-%m-%dT%H:%M:%SZ')
    daily.to_csv(OUT/'daily_features.csv',index=False)
    snap.to_csv(OUT/'snapshots.csv',index=False)
    gaps.to_csv(OUT/'missing_minutes.csv',index=False)
    base.to_csv(OUT/'baseline_paths.csv',index=False)
    bsummary.to_csv(OUT/'baseline_distributions.csv',index=False)
    trades.to_csv(OUT/'strategy_trades.csv',index=False)
    eligible.to_csv(OUT/'strategy_eligibility.csv',index=False)
    pd.DataFrame(eligibility_summary).to_csv(OUT/'eligibility_summary.csv',index=False)
    pd.DataFrame(curves).to_csv(OUT/'equity_curves.csv',index=False)
    pd.DataFrame(cond).to_csv(OUT/'conditional_distributions.csv',index=False)
    pd.DataFrame([{'strategy':r['name'],'quality_view':r['quality_view'],**r['metrics'],'holm_adjusted_p':r['holm_adjusted_p']} for r in results]).to_csv(OUT/'strategy_metrics.csv',index=False)
    quality={'bars':len(master),'trade_dates':len(dates),'first':master.index.min(),'last':master.index.max(),
             'split_first':[dates[0],dates[midpoint-1]],'split_second':[dates[midpoint],dates[-1]],
             'clean_days':int(daily.data_quality_flag.eq('ok').sum()),'flagged_days':int(daily.data_quality_flag.ne('ok').sum()),
             'missing_minutes':len(gaps),'atr_ready_days':int(daily.atr14_prior.notna().sum()),
             'quality_by_day':daily[['contract','trade_date','data_quality_flag','missing_minutes','atr_history_count']].to_dict('records'),
             'roll_policy':CONFIG['roll_trade_date'],'roll_assumption':'March18 final reported volume assumed available before 17:00 Chicago; historical release timestamp unavailable, hence information-timing assumption, not vendor-vintage certified.',
             'original_audits':'reports/nqh25-quarter and reports/nqm25-quarter; not independently certified against CME ticks',
             'calendar':'Scoped Jan1/Jan9/MLK/Presidents exception masks, not full certified calendar; last observed day April17. No April18 completeness claim.',
             'source_hashes':SOURCE_HASHES}
    js('quality.json',quality);js('experiments.json',results);js('methodology.json',CONFIG)
    js('analytics.json',{'baseline_distributions':bsummary.to_dict('records'),'conditional_distributions':cond,
                         'snapshots':snap.to_dict('records'),'quality':quality})
    js('verification.json',checks)
    # Verify saved data, not only file existence.
    saved=pd.read_parquet(DATA/'NQ_point_in_time_1min.parquet')
    pd.testing.assert_frame_equal(saved,master)
    csv=pd.read_csv(DATA/'NQ_point_in_time_1min.csv',parse_dates=['timestamp_utc'])
    assert len(csv)==len(master) and csv.timestamp_utc.is_unique
    assert pd.DatetimeIndex(csv.timestamp_utc).equals(master.index)
    assert np.allclose(csv[source.FIELDS].to_numpy(),master[source.FIELDS].to_numpy(),rtol=0,atol=1e-8)
    for p in OUT.glob('*.json'):
        json.loads(p.read_text())
    checks['parquet_exact_roundtrip']=True;checks['csv_ohlcv_roundtrip']=True;checks['strict_json_parsing']=True
    assert all(hashfile(Path(meta['path']))==meta['sha256'] for meta in SOURCE_HASHES)
    checks['raw_source_hashes_unchanged']=True
    js('verification.json',checks)
    report(quality,results,daily,cond,checks,bsummary)
    manifests=[]
    for p in sorted(list(OUT.glob('*'))+list(DATA.glob('*'))):
        if p.is_file() and p.name!='manifest.json':
            manifests.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashfile(p)})
    js('manifest.json',{'schema_version':1,'generated_at':datetime.now(timezone.utc),'exports':manifests,
                        'dashboard_integration':'Local sidecar JSON/CSV/Markdown exports. Existing CFD dashboard and live deployment NOT overwritten.',
                        'dataset_version':hashfile(DATA/'NQ_point_in_time_1min.parquet'),'code_version':hashfile(Path(__file__))})
    print(json.dumps(clean({'quality':{k:v for k,v in quality.items() if k not in ['source_hashes','quality_by_day']},'results':[{'id':r['id'],'trades':r['metrics']['trades'],'net_usd':r['metrics']['net_usd'],'holm_p':r['holm_adjusted_p']} for r in results],'checks':checks}),indent=2),flush=True)


def report(q,results,daily,conditional,checks,bsummary=None):
    lines=['# OVERNIGHT RESEARCH REPORT — 2026-10-20','',
           '## Besluit','',
           'De volledige lokale batch is uitgevoerd. Dit is een exploratieve eerste screening, geen bevestigde trading edge. De reeks is contractbewust maar niet foutloos; bekende gaten en bijzondere sessies blijven zichtbaar. Er is geen parameteroptimalisatie of onafhankelijke out-of-sample bevestiging uitgevoerd.','',
           f"Master: **{q['bars']:,} minuten**, **{q['trade_dates']} handelsdagen**, {q['first']} tot {q['last']}. Schone dagen: {q['clean_days']}; gemarkeerd: {q['flagged_days']}; ontbrekende rooster-minuten: {q['missing_minutes']}. ATR beschikbaar op {q['atr_ready_days']} dagen. Geen prijzen of volumes geïmputeerd.",'',
           f"Eerste helft: {q['split_first']}; tweede helft: {q['split_second']}. De splits zijn vooraf kalenderchronologisch bepaald voor alle hypothesen. De tweede helft wordt in deze batch bekeken en is hierna geen ongeopende holdout meer.",'',
           '## Rollover en causaliteit','',
           'NQH25 t/m handelsdatum 18 maart; NQM25 vanaf 19 maart (sessieopening 18 maart 22:00 UTC). Alle features zijn EERST binnen afzonderlijke contracten/handelsdagen berekend. Prijzen zijn niet back-adjusted. Intraday returns en VWAP resetten dagelijks. ATR en PDH/PDL gebruiken uitsluitend de historie van hetzelfde contract; geen H25-levels op M25. De extra M25-overlaphistorie is alleen gebruikt voor echte eerdere M25-waarnemingen.','',
           q['roll_assumption'],'',
           '## Featuredefinities en beschikbaarheid','',
           'Alle kloktijden zijn America/New_York. Asia [18:00 vorige dag,03:00), London [03:00,08:30), premarket [08:30,09:30), RTH [09:30,16:00), overnight [18:00,09:30). Midnight Open is de open van de 00:00-bar. Intervallen zijn links inclusief, rechts exclusief. Volledige high/low-ankers verschijnen pas na sluiting van hun venster. Ontbrekende vensterminuten maken het anker leeg.','',
           'ORB5/15/30 zijn beschikbaar vanaf 09:35/09:45/10:00. ATR is een SMA van 14 eerdere geldige RTH true ranges (geen Wilder smoothing). TR bevat de gap naar de vorige complete RTH-close van hetzelfde contract. Bij onvolledige RTH worden die TR en eventueel de volgende TR niet gebruikt. Historie wordt niet uit andere contracten geleend.','',
           'De minuutmaster bevat bar-close features die pas op `feature_available_at_utc` bekend zijn. De snapshot-tabel op 09:30/09:45/10:00/10:30 gebruikt alleen bars vóór het snapshotmoment. De dagtabel bevat ook eindvenster-/einddaggegevens en mag niet ongefilterd als input op 09:30 worden gebruikt. `data_quality_flag` is een ex-post auditfilter, geen bewezen live beschikbare indicator.','',
           'VWAP en SD zijn HLC3-minuutproxies, geen exacte transactie-VWAP. Z=(laatste bekende close−VWAP)/gewogen population SD(HLC3). VCR is 30-minuten gerealiseerde log-returnvolatiliteit gedeeld door de mediaan op dezelfde kloktijd in eerdere maximaal 20 observaties (minimaal 10). Relatief volume gebruikt overeenkomstig het cumulatieve sessievolume met complete prefixes. Opwarmwaarden blijven leeg.','',
           'NY 09:30 is vóór de Amerikaanse DST-overgang 14:30 UTC en vanaf 10 maart 13:30 UTC. London is hier de door de gebruiker gevraagde vaste NY-klokrange, geen lokale Londense beursopening.','',
           '## Hypothesen en vaste uitvoeringsregels','']
    for key in ['A','B','C','D','risk','fills','orb_volume','inference']:
        lines.append(f'- **{key}**: {CONFIG[key]}')
    lines += ['',
              'Kosten per round trip: 2 ticks slippage per kant × 0,25 punt × $20 × 2 + $4,50 commissie = **$24,50 / 1,225 punt**. Eén NQ-contract, geen financiering/margeberekening. Kosten worden van de bruto fill-PnL afgetrokken; niet nogmaals in prijzen verwerkt. Er is geen extra spread aangenomen naast de opgegeven slippage. Werkelijke uitvoerbaarheid is niet vastgesteld.',
              'SL/TP-controle begint in de entrybar. Stop en target in dezelfde bar betekent stop eerst; een gap voorbij stop krijgt de slechtere open. Target-touch is een fillsimulatie zonder queuebewijs. Terminal-bar-extremen kunnen na de exit liggen; strategy MFE/MAE is daarom alleen als bar-bound gelabeld. Baseline MFE/MAE op vaste horizons heeft dat exitvolgordeprobleem niet.','',
              '## Resultaten na kosten','',
              '| Hypothese | Filter | Trades | Winrate | PF | Netto $ | Gem. punten | 1e helft gem. | 2e helft gem. | Holm p |',
              '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    def fmt(v,n=2):
        return 'n.v.t.' if v is None or not np.isfinite(v) else f'{v:.{n}f}'
    for r in results:
        m=r['metrics']; a=r['splits']['first'];b=r['splits']['second']
        lines.append(f"| {r['name']} | {r['quality_view']} | {m['trades']} | {fmt(m['win_rate']*100 if m['win_rate'] is not None else None)}% | {fmt(m['profit_factor'])} | {fmt(m['net_usd'])} | {fmt(m['mean_net_points'])} | {fmt(a['mean_net_points'])} (n={a['trades']}) | {fmt(b['mean_net_points'])} (n={b['trades']}) | {fmt(r['holm_adjusted_p'],3)} |")
    positives=[r['id'] for r in results if r['positive_both_halves_min10_trades']]
    lines += ['',f"Positief in beide helften met minimaal 10 trades per helft: {', '.join(positives) or 'geen'}. Dit criterium alleen bewijst geen edge.",'',
              'Bootstrapintervallen zijn gemiddelden per geschikte handelsdag inclusief dagen zonder trade, niet per trade. De vier hypothesen worden per kwaliteitsview met Holm gecorrigeerd. De twee kwaliteitsviews zijn sensitiviteitsanalyses, geen onafhankelijke replicaties. Korte reeksen, seriële afhankelijkheid, de rollover en veranderende marktcondities beperken de bewijskracht. Onvoldoende waarnemingen krijgen geen p-waarde. Nul verliestrades levert PF=null met aparte markering, niet een verzonnen eindig getal.','',
              '## Baselines, MFE/MAE en regimes','',
              'Baseline-paden beginnen om 09:30, 09:45, 10:00 en 10:30; entry is de open op dat moment, exit de laatste close vóór 15/30/60 minuten of 12:00. Long én short worden geëxporteerd. Alleen volledig aanwezige forward windows tellen mee. MFE/MAE is niet-negatief, vóór kosten, met punten en basispunten. De ongeconditioneerde verdelingen zijn geen willekeurig-entry-controle voor de eventgedreven strategieën en bewijzen geen excess alpha.','',
              'Conditionele kansen voor narrow <0,5 ATR, broad >1,2 ATR en middle worden per helft, entrytijd, horizon en richting geëxporteerd. Wilson-intervallen zijn beschrijvend en nemen onafhankelijkheid aan; de vele overlappende paden zijn NIET zoveel onafhankelijke tests. Geen significance claim voor de regime-grid.','',
              '## Kwaliteit, uitsluitingen en beperkingen','',
              'Het all-filter bewaart gemarkeerde dagen, maar forceert geen trades wanneer essentiële indicatorvensters of forward paths ontbreken. Het clean-filter sluit alle ex-post gemarkeerde dagen volledig uit. Feature-warmup wordt apart behandeld. Daarom kan het aantal geschikte dagen veel lager liggen dan het totaal. Zie strategy_eligibility.csv en eligibility_summary.csv.','',
              q['calendar'],'',
              'Bekende kalenderuitzonderingen: Nieuwjaar gesloten, nationale rouwdag 9 januari vanaf 09:30 NY, MLK/Presidents vanaf 13:00 NY. Bron-audits documenteren de beperkte kalenderverificatie. Vóór/na gaten wordt niet doorgevuld. Raw CSV bevat geen contractkolom of expliciete tijdzone; identiteit/tijdinterpretatie volgen exportcontext en eerdere overlapcontroles.','',
              'Data- en kostenaannames zijn niet gelijk aan historische publicatievintages of werkelijke brokerfills. Geen causaliteitsclaim, advies om echt te handelen of bewijs van reproduceerbare winst. Licentierechten voor platformgebruik/herdistributie zijn niet bevestigd; alles blijft lokaal.','',
              '## Bestanden en dashboard','',
              '- `data/overnight_nq/NQ_point_in_time_1min.parquet` en `.csv`: master met features.',
              '- `dashboard/daily_features.csv`, `snapshots.csv`: dagankers en point-in-time snapshots.',
              '- `dashboard/baseline_paths.csv`, `baseline_distributions.csv`: forward returns en MFE/MAE-verdelingen.',
              '- `dashboard/strategy_trades.csv`, `strategy_metrics.csv`, `equity_curves.csv`: alle fills en prestaties.',
              '- `dashboard/conditional_distributions.csv`: regimekansen en onzekerheid.',
              '- `dashboard/quality.json`, `missing_minutes.csv`: kwaliteitsvlaggen en gaten.',
              '- `dashboard/experiments.json`: adapter met bestaande Experiment-velden; `analytics.json` is een aanvullende research-bundle, niet het oude CFD Analytics-schema.',
              '- `dashboard/methodology.json`, `verification.json`, `manifest.json`: definities, controles en SHA256-provenance.',
              '',
              'De bestanden zijn lokaal beschikbaar in het gevraagde JSON/CSV/Markdown-formaat. De bestaande CFD-dashboardinterface en live deployment zijn niet overschreven; de nieuwe NQ-run is een afzonderlijke sidecar-export, niet automatisch al zichtbaar in die oude interface. Geen GitHub push, commit of deployment.','',
              '## Verificatie','',f"Geslaagd: {', '.join(k for k,v in checks.items() if v)}.",
              'Parquet exact opnieuw ingelezen; CSV gecontroleerd op rijenaantal, unieke tijdstempels en OHLCV. JSON strikt geparseerd. Een volledige herberekening met afgekapt toekomstpad controleert dat eerdere H25-features/snapshots gelijk blijven. Bronbestanden zijn onveranderd.','',
              '## Bronnen','',
              '- Lokale Barchart-exports, bestandsnamen en hashes in quality.json.',
              '- [CME NQ specificaties](https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html): $20 per indexpunt en tick 0,25. De slippage en commissie zijn door de gebruiker opgegeven scenario-aannames.','']
    if bsummary is not None:
        lines += ['## Baselineoverzicht 09:30 NY (long, alle dagen)','',
                  '| Horizon | n | Gem. bruto punten | Gem. netto punten | Netto winrate | Mediaan MFE | Mediaan MAE |',
                  '|---|---:|---:|---:|---:|---:|---:|']
        sub=bsummary.loc[bsummary.quality_view.eq('all') & bsummary.half.eq('all') & bsummary.entry_ny.eq('09:30') & bsummary.direction.eq(1)]
        for _,r in sub.iterrows():
            lines.append(f"| {r.horizon} | {int(r.n)} | {fmt(r.mean_gross_points)} | {fmt(r.mean_net_points)} | {fmt(r.win_rate_net*100)}% | {fmt(r.mfe_points_p50)} | {fmt(r.mae_points_p50)} |")
        lines += ['', '## Overnight-regimes: 09:30–10:30 NY (long, alle dagen)','',
                  '| Helft | Regime | n | P(netto winst) | Gem. netto punten |',
                  '|---|---|---:|---:|---:|']
        for r in conditional:
            if r['quality_view']=='all' and r['entry_ny']=='09:30' and r['horizon']=='60m' and r['direction']==1:
                lines.append(f"| {r['half']} | {r['regime']} | {r['n']} | {fmt(r['positive_net_probability']*100)}% | {fmt(r['mean_net_points'])} |")
        lines += ['', 'Kleine regimegroepen en overlappende horizons maken deze percentages onzeker. De CSV bevat ook de andere kloktijden, horizons, richtingen, kwaliteitsfilter en Wilson-intervallen. Geen selectief gekozen gunstigste combinatie als edge gepresenteerd.','']
    text='\n'.join(lines)
    (ROOT/'OVERNIGHT_RESEARCH_REPORT_2026-10-20.md').write_text(text)
    (OUT/'OVERNIGHT_RESEARCH_REPORT_2026-10-20.md').write_text(text)


if __name__=='__main__':
    main()
