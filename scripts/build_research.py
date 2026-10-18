#!/usr/bin/env python3
"""Build quality, research, and small immutable web data shards from real partitions."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pandas as pd
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from quantlab.data import aggregate, contiguous_returns, sha256
from quantlab.research import describe, evaluate, append_registry
ROOT = Path(__file__).resolve().parents[1]

def sanitize(value):
    if isinstance(value, dict):
        return {k:sanitize(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):
        return [sanitize(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float,np.floating)):
        return round(float(value), 8) if np.isfinite(value) else None
    return value

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(sanitize(value), separators=(',',':'), allow_nan=False))
    temp.replace(path)

def dst_checks(frame):
    rows = []
    for day in ['2025-03-07','2025-03-10','2025-03-28','2025-03-31']:
        ny_open = pd.Timestamp(day+' 09:30', tz='America/New_York').tz_convert('UTC')
        london_open = pd.Timestamp(day+' 08:00', tz='Europe/London').tz_convert('UTC')
        rows.append({'date': day, 'ny_open_utc': ny_open.isoformat(), 'london_open_utc': london_open.isoformat(),
                     'observed_ny_open': ny_open in frame.index, 'observed_london_open': london_open in frame.index})
    return rows

def build(start, end):
    files = sorted(p for p in (ROOT/'data/curated/partitions/USATECHIDXUSD').glob('*.parquet') if start <= p.stem < end)
    if not files:
        raise SystemExit('No real source partitions available; run ingest first.')
    allbars = pd.concat([pd.read_parquet(p) for p in files]).sort_index()
    if not allbars.index.is_unique:
        raise SystemExit('Duplicate timestamps across partitions')
    frame = allbars.loc[allbars.is_market_open].copy()
    if frame.empty:
        raise SystemExit('No validated market bars; refusing to publish fabricated research.')
    curated = ROOT/'data/curated/USATECHIDXUSD-1m.parquet'
    allbars.to_parquet(curated, compression='zstd')
    version = sha256(curated)
    generated = datetime.now(timezone.utc).isoformat()
    latest = {}
    manifest = ROOT/'data/download_manifest.jsonl'
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            row = json.loads(line)
            if row['symbol'] == 'USATECHIDXUSD' and start <= row['date'] < end:
                latest[row['date']] = row
    days = pd.date_range(start, pd.Timestamp(end)-pd.Timedelta(days=1), freq='D', tz='UTC')
    observed = set(frame.index.strftime('%Y-%m-%d'))
    weekdays = {d.strftime('%Y-%m-%d') for d in days if d.weekday() < 5}
    missing = sorted(weekdays-observed)
    coverage = []
    for month, ds in pd.Series(days, index=days).groupby(days.strftime('%Y-%m')):
        dates = [d.strftime('%Y-%m-%d') for d in ds]
        week = [d for d in dates if pd.Timestamp(d).weekday() < 5]
        subset = allbars.loc[allbars.index.strftime('%Y-%m') == month]
        coverage.append({'month': month, 'requested_days': len(dates), 'weekday_days': len(week),
                         'observed_weekdays': len(set(week)&observed), 'observed_days': len(set(dates)&observed),
                         'weekday_coverage_pct': 100*len(set(week)&observed)/len(week) if week else 0,
                         'bars': int(subset.is_market_open.sum()), 'flat_bars': int(subset.is_flat_closed.sum()),
                         'download_failures': sum(latest.get(d,{}).get('status') in ('failed','source_blocked') for d in dates),
                         'unattempted_days': sum(d not in latest for d in dates)})
    years = []
    for year in sorted({int(d[:4]) for d in [start,end]} | set(allbars.index.year)):
        subset = allbars.loc[allbars.index.year==year]
        active = subset.loc[subset.is_market_open]
        expected = [d for d in weekdays if d.startswith(str(year))]
        years.append({'year':year,'bars':len(active),'total_bars':len(subset),
                      'flat_bars':int(subset.is_flat_closed.sum()),'price_anomalies':int(subset.is_price_anomaly.sum()),
                      'first':active.index.min().isoformat() if len(active) else None,
                      'last':active.index.max().isoformat() if len(active) else None,
                      'observed_days':int(active.index.normalize().nunique()),'weekday_days':len(expected),
                      'missing_weekdays':len(set(expected)-observed)})
    failed = [d for d,r in latest.items() if r['status'] in ('failed','source_blocked')]
    unattempted = [d.strftime('%Y-%m-%d') for d in days if d.strftime('%Y-%m-%d') not in latest]
    unavailable = sorted(d for d,r in latest.items() if r['status']=='unavailable')
    missing_partitions = sorted(d for d,r in latest.items() if r['status'] in ('ok','empty') and d not in {p.stem for p in files})
    quality = {'symbol':'USATECHIDXUSD','instrument_type':'Dukascopy index CFD, BID quotes; not CME NQ futures',
        'source':'https://datafeed.dukascopy.com/datafeed','generated_at':generated,'data_version':version,
        'requested_start':start,'requested_end_exclusive':end,'actual_first':frame.index.min().isoformat(),
        'actual_last':frame.index.max().isoformat(),'total_bars':len(allbars),'validated_bars':len(frame),
        'flat_bars_filtered':int(allbars.is_flat_closed.sum()), 'price_anomalies':int(allbars.is_price_anomaly.sum()),
        'min_price':float(frame.low.min()),'max_price':float(frame.high.max()),'price_divisor':1000,
        'duplicate_bars':int(allbars.index.duplicated().sum()),'observed_days':int(frame.index.normalize().nunique()),
        'unavailable_days': unavailable, 'missing_partitions': missing_partitions, 'missing_weekdays':missing, 'failed_days':sorted(failed),'unattempted_days':unattempted,
        'coverage':coverage,'years':years,'dst_checks':dst_checks(frame),
        'ingestion_status':'complete_downloads' if not failed and not unattempted and not unavailable and not missing_partitions else 'incomplete',
        'calendar_note':'Coverage is a weekday diagnostic, not official trading-calendar completeness. Missing weekdays can include holidays. CFD sessions are vendor-specific; no CME-calendar substitution.',
        'flat_rule':'volume == 0 AND open == high == low == close; marked is_market_open=False and excluded from research',
        'volume_note':'Vendor quote activity, not exchange-traded futures contracts',
        'manifest':{'days':len(latest),'statuses':dict(Counter(r['status'] for r in latest.values())),
                    'downloaded_bytes':sum(r.get('bytes',0) for r in latest.values()),
                    'total_attempts':sum(r['attempts'] for r in latest.values())}}
    write_json(ROOT/'data/curated/data_quality_report.json', quality)
    write_json(ROOT/'public/data/quality.json', quality)
    config_paths = [ROOT/f'configs/{f}.yaml' for f in ['instruments','sessions','costs']] + [ROOT/'experiments/hypotheses.yaml']
    code_paths = sorted((ROOT/'src/quantlab').glob('*.py')) + sorted((ROOT/'scripts').glob('*.py'))
    code_version = hashlib.sha256(b''.join(p.read_bytes() for p in code_paths)).hexdigest()
    config_version = hashlib.sha256(b''.join(p.read_bytes() for p in config_paths) + code_version.encode()).hexdigest()
    sessions = yaml.safe_load((ROOT/'configs/sessions.yaml').read_text())
    hypothesis = yaml.safe_load((ROOT/'experiments/hypotheses.yaml').read_text())
    costs = yaml.safe_load((ROOT/'configs/costs.yaml').read_text())
    research = describe(frame, sessions)
    results = sanitize(evaluate(frame, hypothesis, costs, version, config_version))
    for result in results:
        result['code_version'] = code_version
    append_registry(ROOT/'experiments/registry.jsonl', results, generated)
    write_json(ROOT/'experiments/outputs/research.json', research)
    write_json(ROOT/'public/data/analytics.json', research)
    write_json(ROOT/'public/data/experiments.json', results)
    exports = []
    for tf,rule,minutes in [('15m','15min',15),('1h','1h',60),('1d','1D',1440)]:
        bars = aggregate(frame, rule)
        bars['drawdown_pct'] = (bars.close/bars.close.cummax()-1)*100
        returns = contiguous_returns(bars,minutes) if tf!='1d' else np.log(bars.close/bars.close.shift())
        if tf!='1d':
            complete = bars.minute_count.eq(minutes)
            returns = returns.where(complete & complete.shift(fill_value=False))
        bars['rolling_volatility_bps'] = returns.rolling(20,min_periods=20).std()*10000
        for year,part in bars.groupby(bars.index.year):
            rows=[]
            for timestamp,row in part.iterrows():
                rows.append([int(timestamp.timestamp()),*[round(row[c],5) for c in ['open','high','low','close','volume']],
                             int(row.minute_count),round(row.drawdown_pct,5),
                             float(row.rolling_volatility_bps) if pd.notna(row.rolling_volatility_bps) else None])
            name=f'market-{tf}-{year}.json'
            write_json(ROOT/'public/data'/name, rows)
            exports.append({'file':name,'timeframe':tf,'year':int(year),'rows':len(rows),
                            'sha256':sha256(ROOT/'public/data'/name),'bytes':(ROOT/'public/data'/name).stat().st_size})
    write_json(ROOT/'public/data/index.json',{'schema_version':1,'generated_at':generated,'data_version':version,
        'columns':['time','open','high','low','close','volume','minute_count','drawdown_pct','rolling_volatility_bps'],
        'exports':exports,'costs':costs,'research_scope':'Fixed descriptive screens, no validated trading edge'})
    print(json.dumps({'validated_bars':len(frame),'actual_first':quality['actual_first'],'actual_last':quality['actual_last'],
                      'status':quality['ingestion_status'],'missing_weekdays':len(missing),'exports':len(exports)}))
    return quality

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',default='2024-01-01')
    p.add_argument('--end',default=datetime.now(timezone.utc).date().isoformat())
    a=p.parse_args()
    if a.start>=a.end:
        p.error('start must precede end')
    build(a.start,a.end)
