"""Provider-neutral, fail-closed normalized research bars (v1).
Provider adapters map proprietary fields to this schema, never vice versa.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib
import pandas as pd

FIELDS = ('timestamp_utc','instrument_id','contract_id','venue','market_type',
          'source','open','high','low','close','volume')
MARKET_TYPES = {'future','index_cfd','spot','perpetual'}
def validate_bars(bars: pd.DataFrame) -> pd.DataFrame:
    missing = set(FIELDS)-set(bars.columns)
    if missing: raise ValueError(f'Missing canonical fields: {sorted(missing)}')
    frame=bars.copy()
    frame['timestamp_utc']=pd.to_datetime(frame['timestamp_utc'],utc=True,errors='raise')
    if frame['timestamp_utc'].isna().any(): raise ValueError('Null timestamps')
    for name in ('instrument_id','venue','market_type','source'):
        if frame[name].isna().any() or frame[name].astype(str).str.strip().eq('').any():
            raise ValueError(f'Invalid {name}')
    if not set(frame.market_type).issubset(MARKET_TYPES): raise ValueError('Unknown market type')
    futures=frame.market_type.eq('future')
    if (futures & (frame.contract_id.isna() | frame.contract_id.astype(str).str.strip().eq(''))).any():
        raise ValueError('Futures require actual contract IDs')
    for name in ('open','high','low','close','volume'):
        frame[name]=pd.to_numeric(frame[name],errors='raise')
    import numpy as np
    if not np.isfinite(frame[list(('open','high','low','close','volume'))].to_numpy(dtype=float)).all():
        raise ValueError('Non-finite prices or volume')
    if (frame[list(('open','high','low','close'))]<=0).any().any() or (frame.volume<0).any():
        raise ValueError('Negative volume or nonpositive prices')
    if (frame.high<frame[['open','close','low']].max(axis=1)).any() or (frame.low>frame[['open','close','high']].min(axis=1)).any():
        raise ValueError('OHLC violation')
    keys=['source','venue','market_type','instrument_id','contract_id','timestamp_utc']
    if frame.duplicated(keys).any(): raise ValueError('Duplicate unique bar key')
    # Explicit separation of unlike instruments, never make one synthetic series
    return frame.sort_values(keys,kind='stable').reset_index(drop=True)

def dataset_fingerprint(frame: pd.DataFrame) -> str:
    canonical=validate_bars(frame)
    payload=canonical[list(FIELDS)].to_csv(index=False,float_format='%.12g').encode()
    return hashlib.sha256(payload).hexdigest()

def save_curated(frame: pd.DataFrame, destination: str | Path) -> dict:
    clean=validate_bars(frame)
    path=Path(destination)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    clean.to_parquet(temporary,index=False)
    temporary.replace(path)
    return {'path':str(path),'rows':len(clean),
            'content_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'dataset_fingerprint':dataset_fingerprint(clean),
            'market_types':sorted(clean.market_type.unique().tolist())}
