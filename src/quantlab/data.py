"""Strict daily Dukascopy BID M1 decoder. Never fill closed/missing minutes."""
from __future__ import annotations
import hashlib
import lzma
from pathlib import Path
import numpy as np
import pandas as pd

FIELDS = np.dtype([('seconds', '>u4'), ('open', '>u4'), ('close', '>u4'),
                   ('low', '>u4'), ('high', '>u4'), ('volume', '>f4')])
PRICE_COLUMNS = ['open', 'high', 'low', 'close']

def decode_bi5(payload: bytes, day: str, divisor: float = 1000) -> pd.DataFrame:
    if divisor <= 0 or not np.isfinite(divisor):
        raise ValueError('Invalid price divisor')
    raw = lzma.decompress(payload) if payload else b''
    if len(raw) % FIELDS.itemsize:
        raise ValueError('Truncated candle record')
    a = np.frombuffer(raw, dtype=FIELDS)
    seconds = a['seconds'].astype('int64')
    if len(seconds) and ((seconds >= 86400).any() or (seconds % 60 != 0).any()
                         or (np.diff(seconds) <= 0).any()):
        raise ValueError('Invalid, duplicate, or unordered minute offsets')
    frame = pd.DataFrame({c: a[c].astype('float64') / divisor for c in PRICE_COLUMNS})
    frame['volume'] = a['volume'].astype('float64')
    frame.index = pd.DatetimeIndex(pd.Timestamp(day, tz='UTC') + pd.to_timedelta(seconds, unit='s'), name='timestamp')
    return frame

def clean_bars(frame: pd.DataFrame, minimum: float = 5000, maximum: float = 100000):
    f = frame.copy()
    finite = np.isfinite(f[PRICE_COLUMNS + ['volume']]).all(axis=1)
    price_ok = f[PRICE_COLUMNS].ge(minimum).all(axis=1) & f[PRICE_COLUMNS].le(maximum).all(axis=1)
    ohlc_ok = f.high.ge(f[['open', 'close', 'low']].max(axis=1)) & f.low.le(f[['open', 'close', 'high']].min(axis=1))
    valid = finite & price_ok & ohlc_ok & f.volume.ge(0)
    flat = f.volume.eq(0) & f[PRICE_COLUMNS].eq(f.open, axis=0).all(axis=1)
    duplicates = f.index.duplicated(keep='first')
    f['is_market_open'] = valid & ~flat & ~duplicates
    f['is_flat_closed'] = flat
    f['is_price_anomaly'] = ~valid
    return f, {'total_bars': len(f), 'flat_bars_filtered': int((flat & valid).sum()),
               'price_anomalies': int((~valid).sum()), 'duplicate_bars': int(duplicates.sum()),
               'validated_bars': int(f.is_market_open.sum())}

def contiguous_returns(frame: pd.DataFrame, minutes: int = 1) -> pd.Series:
    r = np.log(frame.close / frame.close.shift())
    return r.where(frame.index.to_series().diff().eq(pd.Timedelta(minutes=minutes)))

def aggregate(frame: pd.DataFrame, rule: str) -> pd.DataFrame:
    f = frame.loc[frame.is_market_open] if 'is_market_open' in frame else frame
    groups = f.resample(rule, origin='start_day', label='left', closed='left')
    out = groups.agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
    out['minute_count'] = groups.size()
    return out.dropna(subset=['open'])

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
