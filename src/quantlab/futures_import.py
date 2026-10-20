"""Explicitly user-provided contract-native CSV adapter for NQ/ES research staging.

Authenticity remains UNVERIFIED: structural validation does not establish CME
licensing, timestamp semantics of the vendor, or contract calendar correctness.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from quantlab.futures_csv import validate_contract_csv
from quantlab.research_contract import save_curated

def stage_futures_csv(file: str | Path, output: str | Path, *,
                      instrument: str, source: str) -> dict:
    path=Path(file)
    label = str(source or '').strip().lower()
    if not label or any(token in label for token in ('synthetic','fixture','cfd','dukascopy')):
        raise ValueError('Provide a non-CFD named source; synthetic fixtures not authorized')
    structural=validate_contract_csv(path,instrument=instrument)
    # The strict, source-native CSV validator runs BEFORE metadata is assigned.
    data=pd.read_csv(path,dtype={'contract_id':'string'})
    if data.empty: raise ValueError('Empty input')
    # Explicitly require UTC suffix or +00:00; pandas normalizes only AFTER validator.
    data['timestamp_utc']=pd.to_datetime(data.timestamp_utc,utc=True)
    data['contract_id']=data.contract_id.str.strip().str.upper()
    data['instrument_id']=instrument
    data['venue']='CME_UNVERIFIED'
    data['market_type']='future'
    data['source']=source
    report=save_curated(data,output)
    report.update({'source_type':'USER_SUPPLIED_CONTRACT_FUTURES',
                   'source_name':source,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                   'structural_validation':structural,
                   'exchange_calendar_verified':False,
                   'contract_provenance_verified':False,
                   'trading_edge_validation_allowed':False,
                   'reason':'Vendor license, exchange origin, contract calendar and roll policy still require independent review'})
    return report

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description='Stage 1m futures bars; authenticity UNVERIFIED')
    parser.add_argument('--input',required=True)
    parser.add_argument('--instrument',required=True,choices=['NQ','ES','MNQ','MES'])
    parser.add_argument('--source',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    dest=Path(args.out)
    if dest.suffix.lower()!='.parquet': raise ValueError('Output must be Parquet')
    result=stage_futures_csv(args.input,dest,instrument=args.instrument,source=args.source)
    quality=dest.with_suffix('.quality.json')
    quality.write_text(json.dumps(result,sort_keys=True,indent=2,default=str)+'\n')
    print('STAGED, NOT CERTIFIED: '+str(quality))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
