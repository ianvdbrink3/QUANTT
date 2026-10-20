"""Consolidate user-supplied NQH25 exports; retain NQM25 separately for rollover diagnostics."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DOWNLOADS = Path(__file__).resolve().parents[2] / 'data/raw'
TZ = 'America/Chicago'
FIELDS = ['open', 'high', 'low', 'close', 'volume']
RENAME = dict(Open='open', High='high', Low='low', Latest='close', Volume='volume')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    raw = pd.read_csv(path)
    assert list(raw.columns) == ['Time', 'Open', 'High', 'Low', 'Latest', 'Change', '%Change', 'Volume']
    t = pd.to_datetime(raw.Time, format='%Y-%m-%d %H:%M', errors='coerce')
    footer = raw.loc[t.isna()]
    assert len(footer) == 1 and footer.Time.iloc[0].startswith('Downloaded from Barchart.com as of ')
    assert footer.drop(columns='Time').isna().all().all()
    bars = raw.loc[t.notna()].rename(columns=RENAME)[FIELDS].apply(pd.to_numeric)
    bars.index = pd.DatetimeIndex(t[t.notna()]).tz_localize(TZ, ambiguous='raise', nonexistent='raise').tz_convert('UTC')
    assert bars.index.is_unique and bars.index.is_monotonic_increasing
    assert np.isfinite(bars.to_numpy()).all()
    assert (bars.high >= bars[FIELDS[:4]].max(axis=1)).all()
    assert (bars.low <= bars[FIELDS[:4]].min(axis=1)).all()
    assert np.isclose(bars[FIELDS[:4]].to_numpy() * 4, np.rint(bars[FIELDS[:4]].to_numpy() * 4), rtol=0, atol=1e-8).all()
    assert ((bars.volume > 0) & (bars.volume == bars.volume.round())).all()
    bars.volume = bars.volume.astype('int64')
    return bars, {'path': str(path), 'sha256': digest(path), 'rows': len(bars),
                  'first_utc': bars.index.min().isoformat(), 'last_utc': bars.index.max().isoformat(),
                  'ohlcv_hash': hashlib.sha256(bars.to_csv().encode()).hexdigest(), 'footer': footer.Time.iloc[0]}


def trade_dates(index):
    return (index.tz_convert(TZ).tz_localize(None) + pd.Timedelta(hours=7)).normalize()
