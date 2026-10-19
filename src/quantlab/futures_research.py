"""Causal NQ/ES intraday session levels from verified contract-native minute bars.

Input must have DatetimeIndex in UTC and columns contract_id, open/high/low/close.
The London research segment is 03:00–08:30 America/New_York as defined in
the QUANT project specification (not local London exchange hours).
"""
from __future__ import annotations
import pandas as pd

NY = 'America/New_York'

def session_context(bars: pd.DataFrame) -> pd.DataFrame:
    required = {'contract_id','open','high','low','close'}
    if not required.issubset(bars.columns):
        raise ValueError(f'Missing columns: {sorted(required-set(bars.columns))}')
    if not isinstance(bars.index,pd.DatetimeIndex) or bars.index.tz is None:
        raise ValueError('DatetimeIndex must be timezone-aware')
    if bars.index.has_duplicates or not bars.index.is_monotonic_increasing:
        raise ValueError('Bars must have unique increasing timestamps')
    if str(bars.index.tz) != 'UTC':
        raise ValueError('Bars must use canonical UTC timestamps')
    local = bars.index.tz_convert(NY)
    result = bars.copy()
    result['ny_trade_date'] = pd.Index(local.date)
    result['london_high'] = float('nan')
    result['london_low'] = float('nan')
    result['known_at_utc'] = bars.index + pd.Timedelta(minutes=1)
    for (_,contract), group in result.groupby(['ny_trade_date','contract_id'],sort=False):
        minutes = group.index.tz_convert(NY).hour*60 + group.index.tz_convert(NY).minute
        inside = (minutes >= 180) & (minutes < 510)
        prior_high = group['high'].where(inside).cummax().shift(1)
        prior_low = group['low'].where(inside).cummin().shift(1)
        # Opening values only become known at the NEXT bar open. At and
        # after 08:30 ET the final London range is available.
        complete_high = group['high'].where(inside).cummax()
        complete_low = group['low'].where(inside).cummin()
        idx = group.index
        result.loc[idx,'london_high'] = complete_high.where(~inside,prior_high).to_numpy()
        result.loc[idx,'london_low'] = complete_low.where(~inside,prior_low).to_numpy()
    return result

def evaluate_forward(bars: pd.DataFrame, event_times: pd.DatetimeIndex,
                     horizons=(15,30,60)) -> pd.DataFrame:
    """Point-in-time forward returns/MFE/MAE at exact calendar-minute horizons.

    Entry uses next bar open after the event close and never crosses contract
    boundaries. Missing minutes invalidate each horizon; same-bar stop/target
    ordering is intentionally not simulated.
    """
    if bars.index.tz is None or str(bars.index.tz) != 'UTC':
        raise ValueError('UTC bars required')
    rows=[]
    for signal_time in event_times:
        if signal_time not in bars.index: continue
        signal=bars.loc[signal_time]
        for horizon in horizons:
            start=signal_time+pd.Timedelta(minutes=1)
            stop=start+pd.Timedelta(minutes=horizon-1)
            path=bars.loc[start:stop]
            valid=(len(path)==horizon and path.index[0]==start
                   and path.index[-1]==stop
                   and (path.index.to_series().diff().dropna()==pd.Timedelta(minutes=1)).all()
                   and path.contract_id.eq(signal.contract_id).all())
            row={'signal_utc':signal_time,'contract_id':signal.contract_id,'horizon_min':horizon,'complete':bool(valid)}
            if valid:
                entry=float(path.open.iloc[0])
                row.update(forward_points=float(path.close.iloc[-1]-entry),
                           mfe_points=float(path.high.max()-entry),
                           mae_points=float(entry-path.low.min()))
            rows.append(row)
    return pd.DataFrame(rows)
