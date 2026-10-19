"""Source-neutral, fail-closed end-to-end research runner.

Synthetic fixtures verify wiring only: outputs are never market-edge evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import yaml
from quantlab.futures_research import evaluate_forward
from quantlab.research_validation import (
    Instrument, validate_minute_index, opening_range, coverage_report,
    block_bootstrap_mean, cost_sensitivity, test_manifest as build_manifest,
)
from quantlab.sandbox_execution import FillConfig, simulate_long
from quantlab.research_contract import dataset_fingerprint, validate_bars

def canonical_json(value: Any) -> str:
    return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':'),default=str)

def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()

def fixture_frame(seed: int, bars: int) -> pd.DataFrame:
    if bars<130 or bars>100000: raise ValueError('Fixture bars must be between 130 and 100000')
    import numpy as np
    rng=np.random.default_rng(seed)
    idx=pd.date_range('2026-10-19T13:00:00Z',periods=bars,freq='min',tz='UTC')
    jumps=rng.choice([-0.25,0,0.25],size=bars)
    close=20000+np.cumsum(jumps)
    opening=np.r_[20000,close[:-1]]
    high=np.maximum(opening,close)+.25
    low=np.minimum(opening,close)-.25
    return pd.DataFrame({'contract_id':'NQZ26','open':opening,
          'high':high,'low':low,'close':close,'volume':rng.integers(1,100,size=bars)},
          index=idx)

def from_csv(path: Path, source: str, instrument: str) -> pd.DataFrame:
    if source!='synthetic_fixture':
        raise ValueError('Observed datasets require a separately verified source adapter')
    # Explicit fixtures only; never silently treat arbitrary vendor CSV as exchange-native
    frame=pd.read_csv(path)
    required={'timestamp_utc','contract_id','open','high','low','close','volume'}
    if not required.issubset(frame): raise ValueError('Missing synthetic fixture columns')
    idx=pd.to_datetime(frame.pop('timestamp_utc'),utc=True)
    frame.index=pd.DatetimeIndex(idx,name='timestamp_utc')
    return frame

def quality_gate(frame: pd.DataFrame) -> dict:
    validate_minute_index(frame)
    fields=('open','high','low','close','volume')
    if any(f not in frame for f in fields) or 'contract_id' not in frame:
        raise ValueError('Missing required market columns')
    if frame.empty or frame[list(fields)].isna().any().any():
        raise ValueError('Empty data or null OHLCV')
    import numpy as np
    if not np.isfinite(frame[list(fields)].to_numpy(dtype=float)).all():
        raise ValueError('Non-finite OHLCV')
    if (frame.volume<0).any() or (frame[list(fields[:4])]<=0).any().any():
        raise ValueError('Invalid volume or price')
    if (frame.high<frame[['open','close','low']].max(axis=1)).any() or (frame.low>frame[['open','close','high']].min(axis=1)).any():
        raise ValueError('OHLC ordering invalid')
    if frame.contract_id.isna().any() or frame.contract_id.astype(str).eq('').any():
        raise ValueError('Missing contract identity')
    observed_gaps=coverage_report(frame)
    if sum(v['gap_count'] for v in observed_gaps['contracts'].values()):
        raise ValueError('Research fixture has unreconciled missing minute bars')
    return {'status':'PASS','rows':len(frame),'contract_ids':sorted(frame.contract_id.unique().tolist()),
            'observed_gaps':observed_gaps,'exchange_calendar_verified':False,
            'real_market_data':False}

def run_research(config: dict) -> dict:
    if config.get('schema_version')!=1: raise ValueError('Unsupported experiment schema')
    data=config.get('dataset',{})
    if data.get('source_kind')!='synthetic_fixture':
        raise ValueError('Observed futures and CFD data cannot use the synthetic-only runner')
    symbol=config.get('instrument','NQ')
    ins=Instrument(symbol,.25,{'NQ':20,'MNQ':2,'ES':50,'MES':5}[symbol]).validate()
    seed=int(config.get('seed',17))
    bars=int(data.get('bars',500))
    frame=fixture_frame(seed,bars)
    quality=quality_gate(frame)
    canonical=frame.copy().reset_index(names='timestamp_utc')
    canonical['instrument_id']=symbol
    canonical['venue']='SIMULATED'
    canonical['market_type']='future'
    canonical['source']='SYNTHETIC_FIXTURE_ONLY'
    canonical=validate_bars(canonical)
    data_hash=dataset_fingerprint(canonical)
    ranges=opening_range(frame,minutes=int(config.get('opening_range_minutes',15)))
    # Signal defined in config, using only the just-closed bar. The event
    # timestamp is known at event bar close and entry at next-minute open.
    feature=str(config.get('feature','close'))
    if feature not in {'close','open'}: raise ValueError('Unsupported causal signal feature')
    threshold=float(config.get('threshold',20000))
    side=str(config.get('side','above'))
    if side not in {'above','below'}: raise ValueError('Invalid comparator')
    condition=frame[feature].gt(threshold) if side=='above' else frame[feature].lt(threshold)
    event_times=frame.index[condition]
    # Fixed independent spacing is a design choice to avoid labeling every
    # consecutive minute as an independent observation.
    spacing=int(config.get('event_spacing_minutes',60))
    horizon=int(config.get('horizon_minutes',15))
    if not 1<=horizon<=120 or spacing<horizon or spacing<1:
        raise ValueError('Horizon/spacing invalid')
    selected=[]
    for stamp in event_times:
        if not selected or stamp-selected[-1]>=pd.Timedelta(minutes=spacing):
            selected.append(stamp)
    forward=evaluate_forward(frame,pd.DatetimeIndex(selected),horizons=(horizon,))
    complete=forward[forward.complete] if not forward.empty else pd.DataFrame()
    returns=complete.forward_points.astype(float).tolist() if len(complete) else []
    settings=FillConfig(stop_points=float(config.get('stop_points',4)),
                        target_points=float(config.get('target_points',8)),
                        roundtrip_cost_points=float(config.get('cost_points',2)),
                        multiplier=ins.multiplier, ambiguity='pessimistic')
    trades=[]
    for stamp in complete.signal_utc:
        start=stamp+pd.Timedelta(minutes=1)
        path=frame.loc[start:start+pd.Timedelta(minutes=horizon-1)]
        trades.append(simulate_long(path,float(path.open.iloc[0]),settings))
    uncertainty=None
    if len(returns)>=20:
        uncertainty=block_bootstrap_mean(returns,seed=seed,samples=500)
    code_ref=str(config.get('code_ref','UNSET'))
    manifest=build_manifest(data_hash=data_hash,code_ref=code_ref,
             instrument=ins,parameters=config,synthetic=True)
    result={'schema_version':1,'provenance':'SYNTHETIC_FIXTURE_ONLY',
            'research_question':str(config.get('research_question','Synthetic wiring regression')),
            'hypothesis':str(config.get('hypothesis','Demonstrate complete pipeline wiring')),
            'quality':quality,'manifest':manifest,
            'features':{'opening_ranges':len(ranges),'signal_feature':feature},
            'events':{'detected':int(condition.sum()),'spaced':len(selected),
                      'complete_horizons':len(complete),'horizon_minutes':horizon},
            'outcomes':{'mean_forward_points':float(sum(returns)/len(returns)) if returns else None,
                        'cost_sensitivity':cost_sensitivity(returns,costs=(0,2,4)) if returns else {},
                        'mean_simulated_net_points':float(sum(t['net_points'] for t in trades)/len(trades)) if trades else None},
            'uncertainty':uncertainty,
            'limitations':['All price and volume observations are generated, not exchange data',
                           'No independent market validation or license attestation',
                           'Flat costs and OHLC-bar execution bounds are illustrations',
                           'Synthetic observations cannot substantiate trading expectancy'],
            'validation_status':'STATISTICALLY INCONCLUSIVE',
            'edge_validated':False}
    result['run_id']=fingerprint(result)
    return result

def report_markdown(result:dict) -> str:
    q=result['quality'];ev=result['events'];out=result['outcomes']
    return ('# QUANT synthetic research verification\n\n'
      f"**Status:** {result['validation_status']} (NO REAL MARKET EDGE)\n\n"
      f"**Hypothesis:** {result['hypothesis']}\n\n"
      f"**Research question:** {result['research_question']}\n\n"
      f"**Run fingerprint:** `{result['run_id']}`\n\n"
      f"**Data:** {result['provenance']} · {q['rows']} minute bars; {q['status']} structural checks.\n\n"
      f"**Events:** {ev['spaced']} spaced, {ev['complete_horizons']} complete horizons.\n\n"
      f"**Descriptive mean forward points:** {out['mean_forward_points']} (synthetic only).\n\n"
      f"**Illustrative net points:** {out['mean_simulated_net_points']} (not realized performance).\n\n"
      f"**Uncertainty:** {result['uncertainty'] or 'WITHHELD: insufficient independent synthetic events'}.\n\n"
      '## Limitations\n'+''.join('- '+x+'\n' for x in result['limitations']))

def write_bundle(result:dict, directory:Path) -> None:
    directory.mkdir(parents=True,exist_ok=True)
    for name,content in [('result.json',json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'),
                         ('report.md',report_markdown(result))]:
        target=directory/name
        tmp=directory/(name+'.tmp')
        tmp.write_text(content,encoding='utf-8')
        os.replace(tmp,target)
    # Idempotent registry by stable content hash; errors in the ledger cause
    # a hard failure rather than silent reset.
    registry=directory/'registry.jsonl'
    entries=[]
    if registry.exists():
        for line in registry.read_text(encoding='utf-8').splitlines():
            item=json.loads(line)
            if 'run_id' not in item: raise ValueError('Corrupt registry entry')
            entries.append(item)
    if not any(item['run_id']==result['run_id'] for item in entries):
        with registry.open('a',encoding='utf-8') as handle:
            handle.write(canonical_json({'run_id':result['run_id'],
              'status':result['validation_status'],'provenance':result['provenance'],
              'dataset_hash':result['manifest']['dataset_hash']})+'\n')
            handle.flush();os.fsync(handle.fileno())

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description='QUANT synthetic research CLI — NO REAL MARKET EDGE')
    parser.add_argument('--config',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    config_path=Path(args.config)
    config=yaml.safe_load(config_path.read_text(encoding='utf-8'))
    if not isinstance(config,dict): raise ValueError('Config must be a mapping')
    try:
        result=run_research(config)
    except Exception as exc:
        failure={'schema_version':1,'status':'FAILED','error_type':type(exc).__name__,
                 'error':str(exc),'config_fingerprint':fingerprint(config),
                 'edge_validated':False}
        out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
        with (out/'failures.jsonl').open('a',encoding='utf-8') as f:
            f.write(canonical_json(failure)+'\n')
        raise
    write_bundle(result,Path(args.out))
    print(f"QUANT SYNTHETIC research: {result['validation_status']} | {result['run_id']}")
    return 0

if __name__=='__main__':
    sys.exit(main())
