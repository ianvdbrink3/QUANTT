#!/usr/bin/env python3
"""Verify web shards against curated source and provenance hashes, offline."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from quantlab.data import aggregate
ROOT=Path(__file__).resolve().parents[1]

def verify():
    index=json.loads((ROOT/'public/data/index.json').read_text())
    source=ROOT/'data/curated/USATECHIDXUSD-1m.parquet'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==index['data_version']
    frame=pd.read_parquet(source)
    quality=json.loads((ROOT/'public/data/quality.json').read_text())
    assert frame.is_market_open.sum()==quality['validated_bars']
    assert frame.is_flat_closed.sum()==quality['flat_bars_filtered']
    assert quality==json.loads((ROOT/'data/curated/data_quality_report.json').read_text())
    rules={'15m':'15min','1h':'1h','1d':'1D'}
    for export in index['exports']:
        raw=(ROOT/'public/data'/export['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==export['sha256']
        rows=json.loads(raw)
        assert len(rows)==export['rows']
        expected=aggregate(frame,rules[export['timeframe']])
        expected=expected.loc[expected.index.year==export['year']]
        assert len(expected)==len(rows)
        for row,(timestamp,bar) in zip(rows,expected.iterrows()):
            assert row[0]==int(timestamp.timestamp())
            assert np.allclose(row[1:5],bar[['open','high','low','close']].to_numpy(dtype=float),atol=.00001,rtol=0)
            assert row[6]==bar.minute_count
    print(f"Verified {len(index['exports'])} web shards; {quality['validated_bars']} genuine validated minute bars.")

if __name__=='__main__':
    verify()
