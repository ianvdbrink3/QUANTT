#!/usr/bin/env python3
"""One-command March gate, full-history ingest, and reproducible export."""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import sys
import pandas as pd
from dukascopy_ingest import run
from build_research import ROOT, build, dst_checks, write_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start',type=date.fromisoformat,default=date(2024,1,1))
    parser.add_argument('--end',type=date.fromisoformat,default=datetime.now(timezone.utc).date())
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--transport',choices=['curl','requests'],default='curl')
    parser.add_argument('--attempts',type=int,default=5)
    parser.add_argument('--timeout',type=int,default=45)
    args=parser.parse_args()
    if args.start>=args.end or not 1<=args.workers<=16 or args.attempts<1 or args.timeout<1:
        parser.error('Require start < end and workers 1..16')
    errors=run(date(2025,3,1),date(2025,4,1),workers=args.workers,transport=args.transport,attempts=args.attempts,timeout=args.timeout)
    directory=ROOT/'data/curated/partitions/USATECHIDXUSD'
    march_files=sorted(directory.glob('2025-03-*.parquet'))
    if march_files:
        march=pd.concat([pd.read_parquet(p) for p in march_files]).sort_index()
        active=march.loc[march.is_market_open]
        checks=dst_checks(active)
        validation={'partition_days':len(march_files),'source_errors':errors,
            'dst_observations':checks,'saturday_active_bars':int((active.index.dayofweek==5).sum()),
            'price_anomalies':int(march.is_price_anomaly.sum()),
            'passed':not errors and len(march_files)==31 and all(c['observed_ny_open'] and c['observed_london_open'] for c in checks) and not march.is_price_anomaly.any()}
    else:
        validation={'passed':False,'source_errors':errors,'reason':'No March partitions'}
    write_json(ROOT/'data/curated/march_validation.json',validation)
    if not validation['passed']:
        print('March validation is incomplete; full-history stage remains gated.',flush=True)
        if list(directory.glob('*.parquet')):
            build(args.start.isoformat(),args.end.isoformat())
        return 1
    errors=run(args.start,args.end,workers=args.workers,transport=args.transport,attempts=args.attempts,timeout=args.timeout)
    report=build(args.start.isoformat(),args.end.isoformat())
    return int(bool(errors) or report['ingestion_status']!='complete_downloads')

if __name__=='__main__':
    sys.exit(main())
