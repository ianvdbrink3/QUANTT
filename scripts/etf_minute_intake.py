"""Validate and stage only actual Safari downloads; never read browser secrets."""
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.etf_empirical_intake import ROOT,RAW,sha

PLAN=ROOT/'research/etf-minute-download-plan-2026-10-29.json'
REGISTER=ROOT/'research/etf-minute-intake-2026-10-29.json'
FIELDS=['open','high','low','close','volume']


def plan():
    rows=[]
    for symbol in ('QQQ','TQQQ'):
        for start,end in (('2019-01-14','2022-12-31'),('2025-01-27','2026-09-30')):
            begin=pd.Timestamp(start);last=pd.Timestamp(end)
            while begin<=last:
                finish=min(begin+pd.Timedelta(days=27),last)
                rows.append(dict(sequence=len(rows)+1,symbol=symbol,start=begin.strftime('%Y-%m-%d'),
                    end=finish.strftime('%Y-%m-%d'),start_UI=begin.strftime('%m/%d/%Y'),end_UI=finish.strftime('%m/%d/%Y'),
                    interval_minutes=1,extended_hours=True,dividend_adjust=False))
                begin=finish+pd.Timedelta(days=1)
    value=dict(status='FIXED_CALENDAR_BLOCKS_NO_OUTCOME_SELECTION',max_bars_per_full_block=19200,
        vendor_limit=20000,timing='Equity exchange time America/New_York, unlike Chicago futures files',rows=rows)
    if PLAN.exists():
        if json.loads(PLAN.read_text())!=value:raise ValueError('Download plan changed')
    else:PLAN.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    return value


def read(path):
    raw=pd.read_csv(path)
    expected=['Time','Open','High','Low','Latest','Change','%Change','Volume']
    if list(raw.columns)!=expected:raise ValueError('Unexpected Barchart ETF schema')
    times=pd.to_datetime(raw.Time,format='%Y-%m-%d %H:%M',errors='coerce')
    footer=raw[times.isna()]
    if len(footer)!=1 or not str(footer.Time.iloc[0]).startswith('Downloaded from Barchart.com'):
        raise ValueError('Unexpected non-bar rows')
    frame=raw.loc[times.notna(),['Open','High','Low','Latest','Volume']].copy()
    frame.columns=FIELDS;frame=frame.apply(pd.to_numeric)
    frame.index=pd.DatetimeIndex(times[times.notna()]).tz_localize('America/New_York',ambiguous='raise',nonexistent='raise').tz_convert('UTC')
    if not len(frame) or not frame.index.is_unique or not frame.index.is_monotonic_increasing:raise ValueError('Unordered/duplicate/empty source')
    if len(frame)>=20000:raise ValueError('Potential 20k truncation')
    if not np.isfinite(frame.to_numpy()).all():raise ValueError('Nonfinite bar')
    if not (frame[FIELDS[:4]]>0).all().all() or not (frame.volume>=0).all():raise ValueError('Invalid OHLCV')
    if not ((frame.high>=frame[FIELDS[:4]].max(axis=1))&(frame.low<=frame[FIELDS[:4]].min(axis=1))).all():raise ValueError('Invalid OHLC')
    return frame


def run():
    schedule=plan();rows=[];seen=set();out=RAW/'barchart';out.mkdir(parents=True,exist_ok=True)
    for symbol in ('QQQ','TQQQ'):
        for src in sorted(Path('/Users/ianvandenbrink/Downloads').glob(f'{symbol.lower()}_intraday-1min_historical-data-10-29-2026*.csv')):
            frame=read(src);local=frame.index.tz_convert('America/New_York');first=local[0].strftime('%Y-%m-%d');last=local[-1].strftime('%Y-%m-%d')
            matching=[r for r in schedule['rows'] if r['symbol']==symbol and r['start']<=first<=last<=r['end']]
            if len(matching)!=1:raise ValueError(('Download outside unique planned block',src.name,first,last))
            target=out/src.name
            if target.exists():
                if sha(src)!=sha(target):raise ValueError('Refusing to overwrite different raw bytes')
            else:shutil.copy2(src,target)
            key=(symbol,matching[0]['sequence']);seen.add(key)
            rows.append(dict(symbol=symbol,sequence=matching[0]['sequence'],path=str(target.relative_to(ROOT)),sha256=sha(target),
                bars=len(frame),first=local[0].isoformat(),last=local[-1].isoformat(),days=len(set(local.strftime('%Y-%m-%d'))),
                split_adjusted=True,dividend_adjusted=False,timestamp_zone='America/New_York',
                zero_volume_bars=int((frame.volume==0).sum()),zero_volume_fill_policy='UNTRADED_BAR_NOT_AN_EXECUTABLE_FILL'))
    pending=[r for r in schedule['rows'] if (r['symbol'],r['sequence']) not in seen]
    value=dict(status='FILES_STAGED_NOT_FULL_ENDPOINT_APPROVAL',files=rows,downloaded_blocks=len(seen),
        planned_blocks=len(schedule['rows']),remaining_blocks=len(pending),next_blocks=pending[:5])
    REGISTER.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:value[k] for k in ('downloaded_blocks','planned_blocks','remaining_blocks','next_blocks')},indent=2))
    return value


if __name__=='__main__':run()
