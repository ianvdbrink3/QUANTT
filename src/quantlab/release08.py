"""Release 0.8 — deterministic end-to-end synthetic research bundle.

Fail-closed: only synthetic fixture data.  No statistical evidence of an edge.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import json
import hashlib
import math
import numpy as np
import pandas as pd
import yaml
from quantlab.research_pipeline import run_research, fixture_frame, quality_gate, canonical_json
from quantlab.research_contract import validate_bars, dataset_fingerprint
from quantlab.research_validation import opening_range, vwap_known_at, block_bootstrap_mean, fdr_bh
from quantlab.futures_research import session_context, evaluate_forward
from quantlab.futures_execution import ExecutionSettings, simulate, equity_statistics
from quantlab.validation_governance import purge_overlapping_events, ResearchFamily

HORIZONS=(15,30,60)
SCENARIOS=('London High/Low Sweep','NY 09:30 Opening Range Breakout','VWAP Mean Reversion')

def research_bundle(config:dict)->dict:
    """Compute all visible numbers in Python, rather than invent frontend metrics."""
    baseline=run_research(config)
    if config.get('dataset',{}).get('source_kind')!='synthetic_fixture':
        raise ValueError('The public reference exporter is synthetic-only')
    symbol=config.get('instrument','NQ')
    frame=fixture_frame(int(config.get('seed',17)),int(config['dataset'].get('bars',500))).copy()
    if symbol in {'ES','MES'}:
        # Purely synthetic index-level translation. Never relabel actual CME data.
        for col in ('open','high','low','close'): frame[col]-=14000
        frame['contract_id']=('ESZ26' if symbol=='ES' else 'MESZ26')
    elif symbol=='MNQ': frame['contract_id']='MNQZ26'
    source_quality=quality_gate(frame)
    canonical=frame.reset_index(names='timestamp_utc')
    canonical['instrument_id']=symbol
    canonical['venue']='SIMULATED'
    canonical['market_type']='future'
    canonical['source']='SYNTHETIC_FIXTURE_ONLY'
    source_hash=dataset_fingerprint(validate_bars(canonical))
    run_hash=hashlib.sha256(canonical_json({'instrument':symbol,'config':config,'dataset_hash':source_hash}).encode()).hexdigest()
    context=session_context(frame)
    vwap=vwap_known_at(frame)
    o_range=opening_range(frame,minutes=15)
    local=frame.index.tz_convert('America/New_York')
    day=pd.Index(local.date)
    # Session levels are provided only where prior complete windows exist.
    signals={}
    minute=local.hour*60+local.minute
    london=context.london_high.notna()&context.london_low.notna()
    signals[SCENARIOS[0]]=(london & (frame.high>context.london_high) & (frame.close<context.london_high))
    # 09:30 breakout can only use the completed 09:30–09:45 range.
    breakout=pd.Series(False,index=frame.index)
    for row in o_range.itertuples():
        day_mask=(day==pd.Timestamp(row.ny_calendar_date).date()) & (frame.contract_id==row.contract_id)
        breakout|=pd.Series(day_mask & (frame.index>=row.known_at_utc) & (frame.close>row.range_high),index=frame.index)
    signals[SCENARIOS[1]]=breakout
    signals[SCENARIOS[2]]=vwap.vwap_prior.notna() & (frame.close<vwap.vwap_prior) & (frame.close.shift(1)>=vwap.vwap_prior.shift(1))
    events=[]
    forward_rows=[]
    positions={}
    seed=int(config.get('seed',17))
    min_spacing=int(config.get('event_spacing_minutes',60))
    if min_spacing<60: raise ValueError('The fixed 60-minute forward windows require spacing >=60')
    for name,flag in signals.items():
        selected=[]
        for at in frame.index[flag.fillna(False)]:
            if not selected or at-selected[-1]>=pd.Timedelta(minutes=min_spacing):
                selected.append(at)
        future=evaluate_forward(frame,pd.DatetimeIndex(selected),horizons=HORIZONS)
        for at in selected:
            rows=future[future.signal_utc==at]
            record={'scenario':name,'signal_utc':at.isoformat(),'event_type':'SYNTHETIC',
                    'known_at_utc':(at+pd.Timedelta(minutes=1)).isoformat(),
                    'vwap_prior':float(vwap.loc[at,'vwap_prior']) if pd.notna(vwap.loc[at,'vwap_prior']) else None,
                    'london_high':float(context.loc[at,'london_high']) if pd.notna(context.loc[at,'london_high']) else None,
                    'london_low':float(context.loc[at,'london_low']) if pd.notna(context.loc[at,'london_low']) else None}
            for h in HORIZONS:
                match=rows[rows.horizon_min==h]
                item=match.iloc[0] if len(match) else None
                record[str(h)+'m']=({'forward_points':float(item.forward_points),
                    'mfe_points':float(item.mfe_points),'mae_points':float(item.mae_points)}
                    if item is not None and item.complete else None)
            events.append(record)
    events.sort(key=lambda e:(e['signal_utc'],e['scenario']))
    # Use only complete 60-minute paths for 60-minute strategy execution.
    trade_events=[e for e in events if e['60m'] is not None]
    for mode in ('base_pessimistic','stress_pessimistic','base_optimistic','stress_optimistic'):
        stress=mode.startswith('stress')
        ambiguous='optimistic' if mode.endswith('optimistic') else 'pessimistic'
        fills=[]
        for e in trade_events:
            at=pd.Timestamp(e['signal_utc'])
            start=at+pd.Timedelta(minutes=1)
            path=frame.loc[start:start+pd.Timedelta(minutes=59)]
            direction='short' if 'Sweep' in e['scenario'] or 'Mean Reversion' in e['scenario'] else 'long'
            params=ExecutionSettings(
                side=direction,stop_points=4,target_points=8,
                multiplier={'NQ':20,'MNQ':2,'ES':50,'MES':5}[symbol],
                spread_points=1 if stress else .25,
                slippage_points_per_side=1 if stress else .25,
                commission_usd_per_side_per_contract=3,
                ambiguity=ambiguous)
            trade=simulate(path,float(path.open.iloc[0]),params)
            if trade['status']=='FILLED':
                trade['scenario']=e['scenario']
                fills.append(trade)
        equity=equity_statistics(fills)
        profits=[t['net_usd'] for t in fills]
        gains=sum(max(0,x) for x in profits)
        losses=sum(max(0,-x) for x in profits)
        positions[mode]={'trades':len(fills),'equity_curve_usd':equity['equity_curve_usd'],
            'max_drawdown_usd':equity['max_drawdown_usd'],
            'winrate':sum(x>0 for x in profits)/len(profits) if profits else None,
            'profit_factor':gains/losses if losses>0 else None,
            'total_net_usd':sum(profits),
            'long_count':sum(t['side']=='long' for t in fills),
            'short_count':sum(t['side']=='short' for t in fills),
            'ambiguity_count':sum(t['ambiguity'] for t in fills)}
    # Holdout is NEVER evaluated here. Its results are deliberately sealed.
    interval=pd.DataFrame([{'event_start_utc':e['signal_utc'],
          'event_end_utc':(pd.Timestamp(e['signal_utc'])+pd.Timedelta(minutes=60)).isoformat()}
          for e in events])
    train_end=frame.index[int(len(frame)*.6)]
    valid_end=frame.index[int(len(frame)*.8)]
    first=purge_overlapping_events(interval,train_end,embargo_minutes=60)
    second=purge_overlapping_events(first['evaluation'],valid_end,embargo_minutes=60)
    training=len(first['train'])
    validation=len(second['train'])
    holdout_count=len(second['evaluation'])
    # No fabricated p-values. FDR adjustment requires valid, predeclared tests.
    family=ResearchFamily('release08-sandbox',SCENARIOS,3,seed).validate()
    fwd={}
    for name in SCENARIOS:
        selected=[e for e in events if e['scenario']==name]
        fwd[name]={}
        for h in HORIZONS:
            x=[e[str(h)+'m']['forward_points'] for e in selected if e[str(h)+'m'] is not None]
            fwd[name][str(h)]={'n':len(x),'mean_points':sum(x)/len(x) if x else None,
                'bootstrap_ci':block_bootstrap_mean(x,seed=seed,samples=500) if len(x)>=20 else None,
                'p_value':None,'fdr_adjusted_p':None,
                'status':'NOT TESTED - SYNTHETIC ONLY'}
    return {'schema_version':'0.8','provenance':'SYNTHETIC SANDBOX (DETERMINISTIC)',
        'source_kind':'synthetic_fixture','instrument':symbol,'seed':seed,
        'dataset_id':source_hash,
        'config_hash':hashlib.sha256(canonical_json(config).encode()).hexdigest(),
        'run_id':run_hash,'edge_validated':False,
        'quality':source_quality,'feature_quality':{'vwap_known_at':True,
            'london_complete_segments':int(context.london_high.notna().sum()),
            'opening_ranges':len(o_range)},
        'events':events,'forward':fwd,'execution':positions,
        'governance':{'family_id':family.family_id,'trial_budget':3,
            'trials_registered':3,'train_count':training,'validation_count':validation,
            'holdout_count_sealed':holdout_count,
            'purged_or_embargoed':first['purged_or_embargoed']+second['purged_or_embargoed'],
            'embargo_minutes':60,'holdout_sealed':True,'holdout_scored':False,
            'multiple_testing':'WITHHELD — no real hypothesis p-values',
            'note':'Chronological partitions on synthetic events; not independently certified'},
        'limitations':['Synthetic bars do not model CME futures liquidity',
           'No historical NQ/ES instrument ingestion was performed',
           'A 1-day Dukascopy CFD sample is not CME futures',
           'Synthetic p-values and out-of-sample trading claims are prohibited']}

def export_reference(configs: list[dict],output:Path)->dict:
    runs=[research_bundle(c) for c in configs]
    out={'schema_version':'0.8','classification':'DETERMINISTIC SYNTHETIC REFERENCE',
         'edge_validated':False,'runs':runs,'sources':[
          {'id':'dukascopy_partial_2025_03_19','label':'EMPIRICAL CFD (DUKASCOPY - 1 DAY)',
           'market_type':'index_cfd','date':'2025-03-19','verified_minute_bars':1329,
           'note':'Separate legacy partial observation; no synthetic backtest or CME future status'},
          {'id':'cme_futures_waiting','label':'CME FUTURES READY (AWAITING INGEST)',
           'market_type':'future','observed_bars':0,'provenance_verified':False}]}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,indent=2,allow_nan=False,sort_keys=True)+'\n',encoding='utf-8')
    return out

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--out',default='public/data/research08.json')
    p.add_argument('--bars',type=int,default=1600)
    a=p.parse_args(argv)
    configs=[{'schema_version':1,'dataset':{'source_kind':'synthetic_fixture','bars':a.bars},
       'instrument':s,'seed':41+i,'code_ref':'release08-reference-v1','event_spacing_minutes':60}
       for i,s in enumerate(('NQ','ES'))]
    out=export_reference(configs,Path(a.out))
    print('Synthetic reference exported:',len(out['runs']),'runs')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
