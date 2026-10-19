"""Reproducible toy scenarios; never represent these as market observations."""
from __future__ import annotations
import pandas as pd

def known_path(kind: str='stop_and_target', entry: float=20000.0) -> pd.DataFrame:
    time=pd.date_range('2026-01-05T14:30:00Z',periods=4,freq='min',tz='UTC')
    paths={
      'stop_and_target':[(entry,entry+5,entry-5,entry)],
      'target':[(entry,entry+6,entry,entry+4)],
      'stop':[(entry,entry+1,entry-5,entry-4)],
      'gap_stop':[(entry-6,entry-5,entry-8,entry-7)],
      'flat':[(entry,entry,entry,entry)]}
    if kind not in paths: raise ValueError('Unknown sandbox scenario')
    data=paths[kind]+[(entry,entry+1,entry-1,entry)]*3
    return pd.DataFrame(data,columns=['open','high','low','close'],index=time)
