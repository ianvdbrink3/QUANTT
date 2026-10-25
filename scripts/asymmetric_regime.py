"""One fixed exploratory regime run on consumed development data. Local only.

python -m scripts.asymmetric_regime register|replay|verify
"""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import prepare_historical_contracts as h
from scripts.historical_validation import __main__ as historical
from scripts.causal_map.__main__ import load_inputs

ROOT=h.ROOT
OUT=ROOT/'artifacts/asymmetric-regime'
LOCK=ROOT/'research/asymmetric-regime-lock.json'
RESULT=ROOT/'research/asymmetric-regime-results.json'
REPORT=ROOT/'docs/ASYMMETRIC_REGIME_EXPLORATION.md'
PROOF=ROOT/'research/asymmetric-regime-verification.json'
MODELS=('A_FIXED','A_BREAKEVEN','B_FADE','A_FIXED_PLUS_B','A_BREAKEVEN_PLUS_B')
TICK=.25
FEE=1.225
END=375  #15:45 open, not15:45 close

METHOD=dict(date='2026-10-24',status='EXPLORATORY_CONSUMED_DEVELOPMENT_POOL',
    sample='Exactly previously released733 historical sessions2019Jan14-2021Dec31 plus435 complete recent sessions2024Dec30-2026Sep30; no2022-24 generic source and no first8 historical dates added.',
    regime='At10:00, only completed09:30..09:59 bars plus prior-knownATR14. A: range30>0.60ATR and09:59close strictly outside first15range, direction outward. B: range30<0.40ATR. Boundaries and intermediate regimes idle.',
    A='Enter10:00open, stop0.5ATR, exit15:45open. Separately registered alternative moves stop to entry after completed bar reaches+1.0ATR; activation next bar only, initial stop takes priority in activation bar.',
    B='From10:00 resting OCO sell limit H30 or buy limit L30; first identifiable side only, max1trade/day, stop0.35ATR from fill, target09:30open, unfilled orders canceled/position flat15:45open.',
    limits='Require1tick trade-through to certify resting entry/target fill, no favorable price improvement. An order marketable at minute open is filled conservatively at its limit. If both OCO entries first cross inside the same minute with neither established at open, mark UNKNOWN_FIRST_OCO and leave its P&L unavailable, never choose a future-profitable side.',
    conflicts='Position at bar open: adverse stop before target if both reachable. Intrabar limit-entry bar: stop counts; target only if entry established at open or closing beyond target proves post-entry crossing. Otherwise do not credit unproven target in entry bar.',
    risk='1NQ/filled trade. 1R=initial entry-stop distance, not account-risk budget. Stops rounded toward entry to0.25tick, trigger+ATR rounded away from entry; gap-through stop at adverse bar open can lose more than1R. No artificial loss cap.',
    costs='Fixed$24.50NQ RT=1.225points per filled trade, no additional slippage subtraction or netting credits.',
    reporting='Only pooled performance, N=filled trades, gross/netpoints, net winrate/PF, maximum marked drawdown and every quarter. DD on chronological minute opens/closes and known stop/target fills; not worst-tick DD. A+B is regime switching with1contract, not optimized weights.',
    ambiguity='UNKNOWN_FIRST_OCO days are explicitly unavailable for B and combined models, not zero-return trades. Report their count and exclude from simulated P&L; full-pool performance would remain unidentified if any occur.',
    restrictions='No optimization, pvalue fishing, new independent-validation claim, purchases, Git commit/push or deployment. Preserve all earlier bytes.')


def digest(value):
    return hashlib.sha256(json.dumps(h.clean(value),sort_keys=True).encode()).hexdigest()


def verify():
    lock=json.loads(LOCK.read_text())
    for name,expected in lock['files'].items():
        if h.sha(ROOT/name)!=expected:raise ValueError('Frozen input/code changed: '+name)
    if lock['method']!=METHOD:raise ValueError('Regime method changed')
    if PROOF.exists():
        for name,expected in json.loads(PROOF.read_text())['files'].items():
            if h.sha(ROOT/name)!=expected:raise ValueError('Replay output changed: '+name)
    return historical.verify()


def register():
    if LOCK.exists():return verify()
    historical.verify()
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    files={n:h.sha(ROOT/n) for n in paths if n and (ROOT/n).is_file()}
    files['scripts/asymmetric_regime.py']=h.sha(Path(__file__))
    h.dump(LOCK,dict(method=METHOD,files=files,anchor_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()))
    return dict(status='METHOD_RECORDED_BEFORE_OUTCOMES',protected_files=len(files))


def classify(prefix,atr):
    if any(len(prefix[key])!=30 for key in ('open','high','low','close')):raise ValueError('Exactly30 completed bars required')
    if not np.isfinite(atr) or atr<=0:return dict(regime='MISSING_PRIOR_ATR',direction=0)
    high=float(np.max(prefix['high']));low=float(np.min(prefix['low']));close=float(prefix['close'][29])
    first_high=float(np.max(prefix['high'][:15]));first_low=float(np.min(prefix['low'][:15]))
    ratio=(high-low)/atr
    direction=1 if close>first_high else -1 if close<first_low else 0
    regime='A' if ratio>.60 and direction else 'B' if ratio<.40 else 'IDLE'
    return dict(regime=regime,direction=direction if regime=='A' else 0,high30=high,low30=low,
        range_atr=ratio,opening=float(prefix['open'][0]))


def stop_level(entry,direction,distance):
    ticks=int(np.floor(distance/TICK+1e-9))
    if ticks<1:raise ValueError('No positive tick-sized risk')
    return entry-direction*ticks*TICK


def manage(p,entry_bar,entry,direction,atr,stop_ratio,target=None,breakeven=False,entry_at_open=True):
    stop=stop_level(entry,direction,stop_ratio*atr)
    initial=stop;armed=False
    trigger=entry+direction*np.ceil(atr/TICK-1e-9)*TICK
    for i in range(entry_bar,END):
        op,hi,lo,cl=(float(p[k][i]) for k in ('open','high','low','close'))
        at_open=i>entry_bar or entry_at_open
        gap_stop=at_open and direction*(op-stop)<=0
        touched_stop=(lo<=stop if direction>0 else hi>=stop)
        if gap_stop:return dict(entry=entry_bar,exit=i,entry_price=entry,exit_price=op,direction=direction,reason='STOP_GAP',exit_at_open=True,initial_stop=initial)
        # An already-live target marketable at the opening print precedes
        # any later intrabar reversal. No favorable price improvement.
        target_open=target is not None and at_open and direction*(op-target)>=TICK-1e-9
        if target_open:return dict(entry=entry_bar,exit=i,entry_price=entry,exit_price=target,direction=direction,reason='TARGET_OPEN',exit_at_open=True,initial_stop=initial)
        if touched_stop:return dict(entry=entry_bar,exit=i,entry_price=entry,exit_price=stop,direction=direction,reason='STOP',exit_at_open=False,initial_stop=initial)
        if target is not None:
            touched=(hi>=target+TICK if direction>0 else lo<=target-TICK)
            confirmed=at_open or direction*(cl-target)>=TICK-1e-9
            if touched and confirmed:return dict(entry=entry_bar,exit=i,entry_price=entry,exit_price=target,direction=direction,reason='TARGET',exit_at_open=False,initial_stop=initial)
        if breakeven and not armed and (hi>=trigger if direction>0 else lo<=trigger):
            stop=entry;armed=True  # only subsequent bars use the new stop
    return dict(entry=entry_bar,exit=END,entry_price=entry,exit_price=float(p['open'][END]),direction=direction,
        reason='TIME_1545',exit_at_open=True,initial_stop=initial)


def execute(p,ctx,model):
    atr=ctx['atr'];reg=classify({k:p[k][:30] for k in ('open','high','low','close')},atr)
    if model.startswith('A_'):
        if reg['regime']!='A':return None,reg['regime']
        return manage(p,30,float(p['open'][30]),reg['direction'],atr,.5,breakeven=model=='A_BREAKEVEN'),'FILLED'
    if model!='B_FADE':raise ValueError('Unknown model')
    if reg['regime']!='B':return None,reg['regime']
    high,low,target=reg['high30'],reg['low30'],reg['opening']
    for i in range(30,END):
        op,hi,lo=(float(p[k][i]) for k in ('open','high','low'))
        if op<=low-TICK:direction,entry,at_open=1,low,True
        elif op>=high+TICK:direction,entry,at_open=-1,high,True
        else:
            buy,sell=lo<=low-TICK,hi>=high+TICK
            if buy and sell:return None,'UNKNOWN_FIRST_OCO'
            if not buy and not sell:continue
            direction,entry,at_open=(1,low,False) if buy else (-1,high,False)
        if target==entry:
            return dict(entry=i,exit=i,entry_price=entry,exit_price=entry,direction=direction,
                reason='ZERO_DISTANCE_TARGET',exit_at_open=at_open,initial_stop=stop_level(entry,direction,.35*atr)),'FILLED'
        return manage(p,i,entry,direction,atr,.35,target=target,entry_at_open=at_open),'FILLED'
    return None,'NO_LIMIT_FILL'


def path_for(trade,p):
    curve=np.zeros(780)
    if trade is None:return curve
    a,b=trade['entry'],trade['exit'];entry=trade['entry_price'];d=trade['direction']
    curve[2*a:]=-FEE
    for i in range(a,b):
        curve[2*i]=d*((entry if i==a else p['open'][i])-entry)-FEE
        curve[2*i+1]=d*(p['close'][i]-entry)-FEE
    offset=2*b+(0 if trade['exit_at_open'] else 1)
    if b<END and not trade['exit_at_open']:
        curve[2*b]=(-FEE if b==a else d*(p['open'][b]-entry)-FEE)
    curve[offset:]=d*(trade['exit_price']-entry)-FEE
    return curve


def describe(ledger,curves,dates):
    gross=np.array([t['gross_points'] for t in ledger]);net=gross-FEE
    daily={d:0. for d in dates}
    for t in ledger:daily[t['day']]+=t['net_points']
    equity=0.;peak=0.;drawdown=0.
    for day in dates:
        path=curves.get(day,np.zeros(780))+equity
        running=np.maximum.accumulate(np.r_[peak,path])[1:]
        drawdown=max(drawdown,float((running-path).max()))
        peak=max(peak,float(path.max()));equity=float(path[-1])
    np.testing.assert_allclose(equity,net.sum(),rtol=0,atol=1e-8)
    quarters=[]
    for quarter in sorted({str(pd.Period(d,freq='Q')) for d in dates}):
        x=[t for t in ledger if t['quarter']==quarter]
        quarters.append(dict(quarter=quarter,trades=len(x),gross_points=sum(t['gross_points'] for t in x),net_points=sum(t['net_points'] for t in x)))
    active=[q for q in quarters if q['trades']]
    return dict(N=len(ledger),gross_points=float(gross.sum()),net_points=float(net.sum()),
        winrate=float((net>0).mean()) if len(net) else None,
        profit_factor=float(net[net>0].sum()/-net[net<0].sum()) if (net<0).any() else None,
        max_marked_drawdown=drawdown,positive_traded_quarters=sum(q['net_points']>0 for q in active),
        traded_quarters=len(active),quarterly=quarters)


def pool():
    old_state,masks,_,_,_,_=historical.inputs()
    recent,_,included,*_=load_inputs()
    dates=masks['PRIMARY_STRICT']
    if len(dates)!=733 or len(included)!=435:raise ValueError('Unexpected development pool')
    if set(dates)&set(included):raise ValueError('Overlapping session dates')
    states={d:old_state[d] for d in dates};states.update({d:recent[d] for d in included})
    return states,sorted(states)


def run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    states,dates=pool();regimes={};missing=[];trades={m:[] for m in MODELS};curves={m:{} for m in MODELS};ambiguous=[];no_fill=[]
    for day in dates:
        p,ctx=states[day]
        if not all(len(p[k])==390 and np.isfinite(p[k]).all() for k in ('open','high','low','close')):raise ValueError('Invalid input bars')
        reg=classify({k:p[k][:30] for k in ('open','high','low','close')},ctx['atr']);regimes[day]=reg['regime']
        if reg['regime']=='MISSING_PRIOR_ATR':missing.append(day);continue
        selected={}
        for model in MODELS[:3]:
            trade,status=execute(p,ctx,model)
            if model=='B_FADE' and status=='UNKNOWN_FIRST_OCO':ambiguous.append(day)
            if model=='B_FADE' and status=='NO_LIMIT_FILL':no_fill.append(day)
            if trade is not None:
                trade.update(day=day,quarter=str(pd.Period(day,freq='Q')),model=model,atr=ctx['atr'])
                trade['gross_points']=trade['direction']*(trade['exit_price']-trade['entry_price'])
                trade['net_points']=trade['gross_points']-FEE
                selected[model]=trade;trades[model].append(trade);curves[model][day]=path_for(trade,p)
        for combined,a in [('A_FIXED_PLUS_B','A_FIXED'),('A_BREAKEVEN_PLUS_B','A_BREAKEVEN')]:
            if a in selected and 'B_FADE' in selected:raise AssertionError('Regime overlap')
            trade=selected.get(a,selected.get('B_FADE'))
            if trade:
                trades[combined].append(dict(trade,model=combined));curves[combined][day]=path_for(trade,p)
    summary={m:describe(trades[m],curves[m],dates) for m in MODELS}
    for combined,a in [('A_FIXED_PLUS_B','A_FIXED'),('A_BREAKEVEN_PLUS_B','A_BREAKEVEN')]:
        for field in ('N','gross_points','net_points'):
            np.testing.assert_allclose(summary[combined][field],summary[a][field]+summary['B_FADE'][field],rtol=0,atol=1e-8)
    result=dict(status='EXPLORATORY_DEVELOPMENT_NOT_INDEPENDENT_VALIDATION',method=METHOD,
        pool_sessions=len(dates),atr_ready_sessions=len(dates)-len(missing),missing_ATR_dates=missing,
        regime_counts={key:list(regimes.values()).count(key) for key in ('A','B','IDLE','MISSING_PRIOR_ATR')},
        ambiguous_OCO_dates=ambiguous,unfilled_limit_dates=no_fill,performance=summary,
        full_pool_B_PnL_identifiable=not ambiguous,old_files_unchanged=True,protocol_sha256=h.sha(LOCK))
    h.dump(directory/'summary.json',result)
    h.dump(directory/'regime-labels.json',regimes)
    for m in MODELS:
        h.dump(directory/(m+'-trades.json'),trades[m])
    lines=['# Asymmetrisch regime-model: ontwikkelingsverkenning','',result['status'],'',
        f"Pool: {len(dates)}sessies; {len(dates)-len(missing)}met vooraf bekende ATR. {len(ambiguous)}onbepaalbare eersteOCO-richtingen, {len(no_fill)}dagen zonder limietfill. Geen onafhankelijke bevestiging, geen parameterzoektocht.",'',
        '| Model | N | Bruto pt | Netto pt | Winrate | PF | Max DD pt | Positieve handelskwartalen |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for m,row in summary.items():
        lines.append(f"| {m} | {row['N']} | {row['gross_points']:.3f} | {row['net_points']:.3f} | {row['winrate']:.4%} | {row['profit_factor']:.4f} | {row['max_marked_drawdown']:.3f} | {row['positive_traded_quarters']}/{row['traded_quarters']} |")
    lines+=['','| Kwartaal | A vast | A breakeven | B fade | A vast+B | A breakeven+B |','|---|---:|---:|---:|---:|---:|']
    for i,q in enumerate(summary[MODELS[0]]['quarterly']):
        lines.append('| '+q['quarter']+' | '+' | '.join(f"{summary[m]['quarterly'][i]['net_points']:+.3f}" for m in MODELS)+' |')
    lines+=['','## Vooraf vastgelegde uitvoeringsaannames','']+[f'- {k}: {value}' for k,value in METHOD.items()]
    (directory/'report.md').write_text('\n'.join(lines)+'\n')
    verify()
    return result


def replay():
    if PROOF.exists():return dict(status='EXISTING_RESULTS_VERIFIED',integrity=verify())
    first=run(OUT/'run1');print('First fixed exploration complete; verifying independent replay',flush=True)
    run(OUT/'run2')
    a={p.name:h.sha(p) for p in (OUT/'run1').iterdir() if p.is_file()}
    b={p.name:h.sha(p) for p in (OUT/'run2').iterdir() if p.is_file()}
    if a!=b:raise AssertionError('Regime replay not byte-identical')
    h.dump(RESULT,first);REPORT.parent.mkdir(exist_ok=True);REPORT.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,REPORT]+[folder/name for folder in (OUT/'run1',OUT/'run2') for name in a]
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_EXPLORATORY_REGIME_REPLAY',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(pool_sessions=first['pool_sessions'],ATR_ready=first['atr_ready_sessions'],
        regimes=first['regime_counts'],ambiguous_OCO=len(first['ambiguous_OCO_dates']),
        performance=first['performance'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','replay','verify'])
    print(json.dumps(globals()[p.parse_args().action](),indent=2))
