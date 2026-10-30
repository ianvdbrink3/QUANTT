"""Causal daily features; no data access or broker dependency."""
import numpy as np
import pandas as pd


def features(frame):
    required = ['open', 'high', 'low', 'close', 'volume']
    if not frame.index.is_unique or not frame.index.is_monotonic_increasing:
        raise ValueError('UNSORTED_OR_DUPLICATE_DATES')
    if not set(required).issubset(frame):
        raise ValueError('MISSING_OHLCV')
    f = frame[required].astype(float)
    if not np.isfinite(f.to_numpy()).all() or (f[['open','high','low','close']] <= 0).any().any() or (f.volume < 0).any():
        raise ValueError('INVALID_OHLCV')
    if ((f.high < f[['open','close','low']].max(axis=1)) | (f.low > f[['open','close','high']].min(axis=1))).any():
        raise ValueError('INCOHERENT_OHLC')
    p = f.close.shift(1)
    tr = pd.concat([f.high-f.low, (f.high-p).abs(), (f.low-p).abs()], axis=1).max(axis=1)
    out = pd.DataFrame(index=f.index)
    out['SMA20'] = f.close.rolling(20, min_periods=20).mean()
    out['SMA200'] = f.close.rolling(200, min_periods=200).mean()
    out['ATR14_pre'] = tr.shift(1).rolling(14, min_periods=14).mean()
    out['IBS'] = (f.close-f.low)/(f.high-f.low).replace(0, np.nan)
    out['vol_ratio'] = out.ATR14_pre/f.close
    out['vol_p90_pre'] = out.vol_ratio.shift(1).rolling(252, min_periods=252).quantile(.9, interpolation='linear')
    out['HIGH_VOL'] = pd.Series(pd.NA, index=f.index, dtype='boolean')
    ready = out.vol_p90_pre.notna()
    out.loc[ready,'HIGH_VOL'] = out.loc[ready,'vol_ratio'] > out.loc[ready,'vol_p90_pre']
    out['S1'] = ((f.close > out.SMA20) & (out.IBS >= .85) & ((f.high-f.low) > .85*out.ATR14_pre))
    return out
