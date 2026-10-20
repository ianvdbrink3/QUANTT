"""Fail-closed, raw-only replay of the frozen published NQ research release."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import argparse
import collections
import hashlib
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timezone

REPO=Path(__file__).resolve().parents[2]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def preflight(raw_dir, manifest, public_dir):
    problems=[]
    for item in manifest['sources']:
        name=item['filename']
        if Path(name).name!=name:
            raise ValueError('Manifest contains unsafe filename')
        p=raw_dir/name
        if not p.is_file():
            problems.append(f'MISSING: {name}')
        elif sha(p)!=item['sha256']:
            problems.append(f'SHA256 MISMATCH: {name}')
    published={}
    for name,expected in manifest['reference_files'].items():
        p=public_dir/name
        if not p.is_file() or sha(p)!=expected:
            problems.append(f'PUBLISHED REPORT MISMATCH: {name}')
        else:
            published[name]=json.loads(p.read_text())
    if problems:
        raise ValueError('\n'.join(problems))
    nq=published['nq-overnight.json']
    if [x['sha256'] for x in manifest['sources']]!=nq['source_csv_hashes']:
        raise ValueError('Manifest source hashes do not match published NQ report')
    if len(manifest['sources'])!=11:
        raise ValueError('Exactly the frozen eight H25 and three M25 exports are required')
    return published


def compare(expected, actual, path='$'):
    """Compare full payload shapes/strings/integers; allow only tiny float noise."""
    if isinstance(expected,bool) or expected is None:
        if actual is not expected:
            raise ValueError(f'{path}: {actual!r} != {expected!r}')
    elif isinstance(expected,int):
        if type(actual) is not int or actual!=expected:
            raise ValueError(f'{path}: integer mismatch {actual!r} != {expected!r}')
    elif isinstance(expected,float):
        if not isinstance(actual,(float,int)) or not math.isfinite(actual) or not math.isclose(expected,actual,rel_tol=0,abs_tol=1e-9):
            raise ValueError(f'{path}: float mismatch {actual!r} != {expected!r}')
    elif isinstance(expected,dict):
        if not isinstance(actual,dict) or set(expected)!=set(actual):
            raise ValueError(f'{path}: keys differ: {set(expected)^set(actual)}')
        for key in expected:
            compare(expected[key],actual[key],path+'.'+key)
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(expected)!=len(actual):
            raise ValueError(f'{path}: list length mismatch')
        for i,(a,b) in enumerate(zip(expected,actual)):
            compare(a,b,f'{path}[{i}]')
    elif expected!=actual:
        raise ValueError(f'{path}: value mismatch {actual!r} != {expected!r}')


def semantic_payload(name, value):
    value=json.loads(json.dumps(value))
    if name=='nq-overnight.json':
        value.pop('generated_at',None)
        value.pop('dataset_sha256',None)  # Parquet bytes, separately reported; source hashes never excluded.
    elif name=='research09.json':
        for source in value['sources']:
            source.pop('staged_sha256',None)  # Logical dataset fingerprint remains REQUIRED.
    return value


def verify_targets(manifest, quality, experiments, trades):
    expected=manifest['expected']
    orb=next(x for x in experiments if x['name']=='B_ORB15' and x['quality_view']=='all')
    actual={'bars':quality['bars'],'eligible_days':orb['metrics']['eligible_days'],
            'orb15_trades':orb['metrics']['trades'],'orb15_net_points':orb['metrics']['net_points']}
    for key in ['bars','eligible_days','orb15_trades']:
        if actual[key]!=expected[key]:
            raise ValueError(f'TARGET MISMATCH {key}: {actual[key]} != {expected[key]}')
    if not math.isclose(actual['orb15_net_points'],expected['orb15_net_points'],rel_tol=0,abs_tol=1e-9):
        raise ValueError('ORB15 precise points mismatch')
    decimal_points=sum((Decimal(str(row['gross_points']))-Decimal('1.225')
                        for row in trades if row['strategy']=='B_ORB15'),Decimal(0))
    if sum(row['strategy']=='B_ORB15' for row in trades)!=expected['orb15_trades']:
        raise ValueError('ORB15 underlying trade-list count mismatch')
    if decimal_points!=Decimal('919.425'):
        raise ValueError(f'Decimal PnL reconciliation failed: {decimal_points}')
    actual['orb15_display_points']=str(decimal_points.quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
    if actual['orb15_display_points']!=expected['orb15_display_points']:
        raise ValueError('Rounded display points mismatch')
    actual['orb15_trade_ledger_sha256']=trade_ledger_sha256(trades)
    if actual['orb15_trade_ledger_sha256']!=expected['orb15_trade_ledger_sha256']:
        raise ValueError('ORB15 individual trade-ledger fingerprint mismatch')
    return actual


def trade_ledger_sha256(trades):
    rows=[row for row in trades if row['strategy']=='B_ORB15']
    rows=sorted(rows,key=lambda row:(row.get('entry_utc',''),row.get('trade_date','')))
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main(argv=None):
    if not __debug__:
        raise RuntimeError('Do not run with Python -O: pipeline assertions must remain enabled')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir',type=Path,default=REPO/'data/raw')
    parser.add_argument('--hashes-only',action='store_true',help='Preflight only, not a Level 2 reproduction')
    parser.add_argument('--publish',action='store_true',help='After successful verification, replace the two public aggregate JSON reports')
    args=parser.parse_args(argv)
    manifest=json.loads((REPO/'research/reproduction-manifest.json').read_text())
    print('1/5 Source SHA256 and frozen published report verification',flush=True)
    published=preflight(args.raw_dir,manifest,REPO/'public/data')
    if args.hashes_only:
        print('PREFLIGHT PASS: 11 raw source files match the published hashes (NO recomputation performed)')
        return 0
    # Each invocation starts empty; no cached master, features or trades are read.
    artifact_dir=REPO/'artifacts'
    artifact_dir.mkdir(exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='reproduction-',dir=artifact_dir))
    (work/'public/data').mkdir(parents=True)
    result={'status':'FAILED','work_dir':str(work.relative_to(REPO)),
            'started_at':datetime.now(timezone.utc).isoformat(),'sources_verified':11}
    try:
        from . import engine, publish, audit_outputs
        engine.ROOT=work;engine.OUT=work/'dashboard';engine.DATA=work/'data/overnight_nq'
        engine.source.DOWNLOADS=args.raw_dir.resolve();engine.SOURCE_HASHES.clear()
        print('2/5 Recompute raw bars -> contract sessions -> features -> paths -> trades',flush=True)
        engine.main()
        print('3/5 Independent PnL, baseline, rollover and saved-output reconciliations',flush=True)
        audit_outputs.main()
        publish.ROOT=work;publish.APP=work
        print('4/5 Re-run 0.9 staging/import gate and render both JSON bundles',flush=True)
        publish.main()
        import pandas as pd
        quality=json.loads((work/'dashboard/quality.json').read_text())
        experiments=json.loads((work/'dashboard/experiments.json').read_text())
        trades=pd.read_csv(work/'dashboard/strategy_trades.csv').to_dict('records')
        result['targets']=verify_targets(manifest,quality,experiments,trades)
        result['published_payload_checks']={}
        for name,reference in published.items():
            actual_path=work/'public/data'/name
            actual=json.loads(actual_path.read_text())
            compare(semantic_payload(name,reference),semantic_payload(name,actual))
            result['published_payload_checks'][name]={'semantic_match':True,
                'original_sha256':sha(REPO/'public/data'/name),'recomputed_sha256':sha(actual_path),
                'excluded_serialization_metadata':['generated_at','dataset_sha256'] if name=='nq-overnight.json' else ['sources[].staged_sha256']}
        # Verify original bytes again at end, not only at preflight.
        preflight(args.raw_dir,manifest,REPO/'public/data')
        if args.publish:
            for name in published:
                target=REPO/'public/data'/name
                actual=json.loads((work/'public/data'/name).read_text())
                if name=='nq-overnight.json':
                    actual['generated_at']=published[name]['generated_at']  # Frozen release timestamp, not wall-clock run time.
                encoded=json.dumps(actual,indent=2,allow_nan=False)+'\n'
                # Never silently move the frozen reference hash or publish a non-identical release.
                if hashlib.sha256(encoded.encode()).hexdigest()!=manifest['reference_files'][name]:
                    raise ValueError(f'{name}: byte metadata differs; verified artifact retained privately; no public reference changed')
            for name in published:
                actual=json.loads((work/'public/data'/name).read_text())
                if name=='nq-overnight.json':
                    actual['generated_at']=published[name]['generated_at']
                (REPO/'public/data'/name).write_text(json.dumps(actual,indent=2,allow_nan=False)+'\n')
        result.update(status='PASS',level='2: raw-input rerun of frozen implementation; not independent code or vendor certification',
                      finished_at=datetime.now(timezone.utc).isoformat(),published=args.publish)
        print('5/5 PASS: 106678 bars | 42 eligible days | ORB15 37 trades | +919.425 points (+919.43 half-up)',flush=True)
        return 0
    except Exception as exc:
        result['error']=str(exc)
        raise
    finally:
        (work/'verification-report.json').write_text(json.dumps(result,indent=2)+'\n')
        print(f'Verification report: {work.relative_to(REPO)}/verification-report.json',flush=True)


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'RESEARCH VERIFICATION FAILED: {exc}',file=sys.stderr)
        raise SystemExit(1)
