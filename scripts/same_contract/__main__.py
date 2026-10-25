"""python -m scripts.regime_consolidation register|replay|verify.

Local consolidation of five specified variants; previous files are immutable.
"""
import argparse
import csv
import json
import subprocess

import numpy as np
import pandas as pd

from scripts.two_pillar import __main__ as tp
from scripts.regime_consolidation.core import MODELS,assemble,panel
from scripts.regime_consolidation import __main__ as archive
from scripts.same_contract.core import choose,path
from scripts.oos_preparation.year import load_registered
from scripts.regime_consolidation.inference import joint,REPS,SEED,FAMILY

h=tp.h
c=tp.c
frozen=tp.frozen
ROOT=tp.ROOT
OUT=ROOT/'artifacts/same-contract'
LOCK=ROOT/'research/same-contract-lock.json'
RESULT=ROOT/'research/same-contract-results.json'
PROOF=ROOT/'research/same-contract-verification.json'
REPORT=ROOT/'docs/SAME_CONTRACT_CAUSAL_EXECUTION.md'
BLOCKS=('2019_2021','2024_2026','COMBINED')
SAMPLES=('OBSERVED_PATH','COMPLETE_DAY_SENSITIVITY')
METHOD=dict(date='2026-10-25',status='CAUSAL_CONTRACT_CORRECTION_ON_CONSUMED_DEVELOPMENT_DATA',
    selection='At09:30 freeze the already effective RTH contract; reconfirm15:55. Only prior-session volume route activations effective before09:30 are allowed. Do not inspect tomorrow route or current finalized futures-session volume. Calendar expiry guard chooses quarterly successor if next cash09:30 is at/after expiry09:30. Guard must be resolved before RTH with matching raw contract features; never patch after entry.',
    holding='16:00open through next actual cash09:30open in SAME contract even if the active indicator route changes at18:00. No rollover transaction/spread PnL, no hindsight switch exclusion, no alternate contract chosen by endpoint availability. Missing same-contract endpoints remain unscored data limitations, not zero PnL.',
    strategies=archive.METHOD['models'],execution=archive.METHOD['execution'],
    accounting=archive.METHOD['accounting'],inference=archive.METHOD['inference'],
    missing=archive.METHOD['missing'],
    preservation='Original consolidated result/report/code and all earlier protected research bytes preserved. B149 unchanged. Previously executable overnight rows must match numerically; only newly admitted same-contract nights can add PnL. No search or independent validation claim.',
    reproduction='Two independent raw CSV source reconstructions with hashes and deterministic byte-identical outputs; inspect future-cutoff contract selection and same-contract endpoints.')


def verify():
    archive.verify()
    lock=json.loads(LOCK.read_text())
    if lock['method']!=METHOD:raise ValueError('Consolidation method changed')
    for name,digest in lock['files'].items():
        if h.sha(ROOT/name)!=digest:raise ValueError('Protected bytes changed: '+name)
    if PROOF.exists():
        for name,digest in json.loads(PROOF.read_text())['files'].items():
            if h.sha(ROOT/name)!=digest:raise ValueError('Output changed: '+name)
    return dict(status='ALL_PRIOR_BYTES_AND_METHOD_VERIFIED',protected=len(lock['files']))


def register():
    if LOCK.exists():return verify()
    archive.verify()
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    files={n:h.sha(ROOT/n) for n in names if n and (ROOT/n).is_file() and (n.startswith('scripts/same_contract/') or n.startswith('tests/test_same_contract'))}
    files.update({str(x.relative_to(ROOT)):h.sha(x) for x in (archive.RESULT,archive.REPORT,archive.PROOF)})
    h.dump(LOCK,dict(method=METHOD,files=files,anchor_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()))
    return dict(status='FIVE_VARIANTS_AND_INFERENCE_LOCKED_BEFORE_OUTCOMES',protected=len(files))


def rebuild():
    data,sources=tp.pv.inputs()
    original=lambda name:json.loads((tp.OUT/'run1'/name).read_text())
    # historical.inputs above rebuilt raw CSVs and compared this full cache exactly.
    full_old=pd.read_parquet(h.OUT/'contract-bars.parquet')
    full_recent,_,_=load_registered(ROOT)
    fulls={'2019_2021':full_old,'2024_2026':full_recent}
    old_rolls=json.loads(h.RESULT.read_text())['rollovers']
    new_rolls=[dict(to='NQM25',effective_session='2025-03-19',decision_session='2025-03-18',effective_utc=h.at('2025-03-18','18:00').isoformat())]
    new_rolls+=json.loads((ROOT/'research/holdout-protocol.json').read_text())['rollovers']
    new_rolls+=json.loads((ROOT/'research/oos-year-rollovers.json').read_text())['rollovers']
    routes={'2019_2021':('NQZ18',old_rolls),'2024_2026':('NQH25',new_rolls)}
    choices=[]
    astop=[];B=[];bull=[];bullstop=[];cash={};coverage={}
    for block,d in data.items():
        d['active']=d['active'].sort_index()
        if not d['active'].index.is_unique:raise ValueError('Duplicate active minute')
        d['groups']=dict(tuple(d['active'].groupby('trade_date')))
        cash[block]=h.cash_dates(min(d['dates']),max(d['dates']))
        contracts={k:g.sort_index() for k,g in fulls[block].groupby('contract')}
        counts_rejected={};guards=0;roll_nights=0
        nextcash=dict(zip(d['cash'][:-1],d['cash'][1:]))
        for day in d['dates']:
            p,base=d['state'][day];ctx=dict(base,**d['features'][day])
            ev=frozen.select_g1(p,ctx,ctx['prior_volumes'])
            t,status=frozen.execute(p,ctx,'G1_ATR',ev)
            if t:
                start=h.at(day,'09:30')+pd.Timedelta(minutes=t['entry_bar'])
                end=h.at(day,'09:30')+pd.Timedelta(minutes=t['exit_bar'])
                B.append(c.enrich(dict(t,day=day,exit_day=day,entry_time=start.isoformat(),exit_time=end.isoformat(),
                                      block=block,path_points=frozen.marks(t,p)),ctx['atr']))
            is_A=frozen.strong_day(p,ctx)
            is_bull=ctx['bull'] is not None and p['close'][-1]>ctx['sma_today']
            nextday=nextcash.get(day)
            if nextday is None:continue
            choice=choose(day,nextday,*routes[block]);guards+=choice['expiry_guard']
            current=str(d['groups'][day].contract.iloc[0])
            if choice['contract']!=current:
                raise ValueError('Preopen expiry reroute requires matching contract RTH/indicator history; never mix '+day)
            choices.append(dict(day=day,nextcash=nextday,block=block,**choice))
            if not is_A and not is_bull:continue
            holding,code=path(contracts[choice['contract']],day,nextday,d['calendar'])
            if holding is None:
                counts_rejected[code]=counts_rejected.get(code,0)+1;continue
            times,prices,missing=holding
            old_path,old_code=tp.path_inputs(d,day,nextday)
            roll_nights+=old_code=='CONTRACT_SWITCH' 
            tag=dict(block=block,range_atr=float((max(p['high'])-min(p['low']))/ctx['atr']),strong_day=is_A,contract=choice['contract'],selection_time=choice['selected_at_utc'],previous_rejection=old_code)
            stop=dict(c.night(day,nextday,times,prices,ctx['atr'],missing,catastrophe=True),**tag)
            if is_A:astop.append(stop)
            if is_bull:
                bull.append(dict(c.night(day,nextday,times,prices,ctx['atr'],missing),**tag));bullstop.append(stop)
        select=lambda rows:[t for t in rows if t['block']==block]
        counts={}
        for label,rows in (('SELECTIVE_STOP',select(astop)),('BULL_STOP',select(bullstop))):
            counts[label]=dict(N=len(rows),incomplete_full_paths=sum(not t['complete_holding_path'] for t in rows),
                               unidentified_stop_paths=sum(not t['stop_path_identified'] for t in rows),
                               observed_stops=sum(t['reason'] in ('STOP','STOP_GAP') for t in rows),
                               gap_stops=sum(t['reason']=='STOP_GAP' for t in rows))
        counts.update(expiry_guard_sessions=guards,new_qualifying_roll_nights=roll_nights,rejections=counts_rejected)
        coverage[block]=counts
    tp.parity(B,original('B-trades.json'),('entry_bar','exit_bar','entry_price','exit_price','net_points','net_R'))
    models=assemble(astop,B,bull,bullstop)
    for model,rows in models.items():
        previous=json.loads((archive.OUT/'run1'/(model+'-trades.json')).read_text())
        keys=lambda t:(t['entry_time'],t['exit_day'])
        known={keys(t):t for t in rows}
        for old in previous:
            now=known[keys(old)]
            for field in ('entry_price','exit_price','net_points','net_R'):
                np.testing.assert_allclose(now[field],old[field],rtol=0,atol=1e-8)
    return models,cash,coverage,sources,astop,bullstop,choices


def report(result):
    lines=['# Causale same-contract correctie: S1, S2 en S3','',result['status'],'',
           'Alle systemen geselecteerd op reeds bekeken data. Geen onafhankelijke bevestiging. NominaleCIs en p-waarden conditioneel op bron- en uitvoeringsaannames.','']
    fmt=lambda v:'n/a' if v is None else f'{v:.4f}'
    for sample in SAMPLES:
        lines += [f'## {sample}','',
                  '| Periode | Model | N | Netto R | Netto pt | PF R | Sharpe | DD R | DD pt | +R kwartalen |',
                  '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for b in BLOCKS:
            for m in MODELS:
                x=result['samples'][sample][b][m]
                lines.append(f"| {b} | {m} | {x['N']} | {x['net_R']:.5f} | {x['net_points']:.3f} | {fmt(x['trade_PF_R'])} | {fmt(x['sharpe_daily_R'])} | {x['max_marked_drawdown_R']:.5f} | {x['max_marked_drawdown_points']:.3f} | {x['positive_quarters_R']}/{x['traded_quarters']} |")
        lines += ['', '| Periode | Model | Gem.R/cashdag | 95%CI gemiddelde | 95%CI verwacht totaalR | p tweezijdig | p Holm15 (primair) | SimultaanCI gemiddelde |',
                  '|---|---|---:|---|---|---:|---:|---|']
        for b in BLOCKS:
            for m in MODELS:
                x=result['samples'][sample][b][m]['inference']
                interval=lambda name:'['+'; '.join(f'{v:.6f}' for v in x[name])+']'
                primary=sample=='OBSERVED_PATH'
                lines.append(f"| {b} | {m} | {x['mean_net_R_per_cash_day']:.6f} | {interval('mean_ci95')} | {interval('expected_total_R_ci95')} | {fmt(x['p_raw_two_sided']) if primary else 'diagnostisch CI'} | {fmt(x['p_holm15']) if primary else 'n/a'} | {interval('mean_familywise95_bonf15')} |")
    lines += ['', '## Ongewijzigd archief versus causale uitvoering','',
              '| Periode | Model | Oud N | Nieuw N | Oud netto pt | Nieuw netto pt | Verschil pt | Verschil R |',
              '|---|---|---:|---:|---:|---:|---:|---:|']
    for row in result['comparison']:
        lines.append(f"| {row['period']} | {row['model']} | {row['old_N']} | {row['new_N']} | {row['old_net_points']:.3f} | {row['new_net_points']:.3f} | {row['delta_points']:.3f} | {row['delta_R']:.6f} |")
    lines += ['', '## Dekking' ,'', '```json',json.dumps(result['coverage'],indent=2),'```','',
              '## Vooraf vastgelegde methode','']+[f'- {k}: {v}' for k,v in METHOD.items()]
    lines += ['', '## Kwartaalstabiliteit','', '| Sample | Periode | Model | Kwartaal | N | Netto R | Netto pt |','|---|---|---|---|---:|---:|---:|']
    for sample in SAMPLES:
        for b in BLOCKS:
            for m in MODELS:
                lines += [f"| {sample} | {b} | {m} | {q['quarter']} | {q['N']} | {q['net_R']:.5f} | {q['net_points']:.3f} |" for q in result['samples'][sample][b][m]['quarterly']]
    return '\n'.join(lines)+'\n'


def one_run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    models,cash,coverage,sources,astop,bullstop,choices=rebuild()
    bad={t['exit_day'] for t in astop+bullstop if not t['complete_holding_path']}
    result=dict(status='CAUSAL_SAME_CONTRACT_CORRECTION_NOT_INDEPENDENT_CONFIRMATION',method=METHOD,
                coverage=coverage,source_verification=sources,samples={},bootstrap={},criteria={},method_sha256=h.sha(LOCK))
    private_panels={}
    for sample in SAMPLES:
        clean=sample=='COMPLETE_DAY_SENSITIVITY'
        rows={m:[t for t in v if not clean or t['exit_day'] not in bad] for m,v in models.items()}
        calendars={b:[d for d in ds if not clean or d not in bad] for b,ds in cash.items()}
        allcash=sorted(set(d for ds in calendars.values() for d in ds))
        matrices=[];stats={}
        for b in BLOCKS:
            ds=allcash if b=='COMBINED' else calendars[b]
            subset={m:[t for t in v if b=='COMBINED' or t['block']==b] for m,v in rows.items()}
            stats[b]={m:c.stats(v,ds) for m,v in subset.items()}
            mat=panel(subset,ds)
            for j,m in enumerate(MODELS):
                np.testing.assert_allclose(mat[:,j].sum(),stats[b][m]['net_R'],rtol=0,atol=1e-8)
            private_panels[sample+'_'+b]=dict(dates=ds,models=list(MODELS),net_R=mat.tolist())
            if b!='COMBINED':matrices.append((b,ds,mat))
        intervals,meta=joint(matrices)
        for b in BLOCKS:
            for j,m in enumerate(MODELS):
                estimate=intervals[b][j]
                estimate['scope']='DIAGNOSTIC_CI_ONLY' if clean else 'PRIMARY15_EXPLORATORY_TESTS'
                if clean:
                    estimate.pop('p_raw_two_sided');estimate.pop('p_holm15')
                stats[b][m]['inference']=estimate
        result['samples'][sample]=stats;result['bootstrap'][sample]=meta
        result['criteria'][sample]={m:dict(
            nominal95_above_zero_all_periods=all(stats[b][m]['inference']['nominal_ci_strictly_positive'] for b in BLOCKS),
            primary_Holm15_below005_all_periods=all(stats[b][m]['inference']['p_holm15']<.05 for b in BLOCKS) if not clean else None,
            simultaneous95_above_zero_all_periods=all(stats[b][m]['inference']['simultaneous_ci_strictly_positive'] for b in BLOCKS)) for m in MODELS}
    previous=json.loads(archive.RESULT.read_text())
    result['comparison']=[]
    for b in BLOCKS:
        for m in MODELS:
            old=previous['samples']['OBSERVED_PATH'][b][m];new=result['samples']['OBSERVED_PATH'][b][m]
            result['comparison'].append(dict(period=b,model=m,old_N=old['N'],new_N=new['N'],old_net_points=old['net_points'],new_net_points=new['net_points'],delta_points=new['net_points']-old['net_points'],delta_R=new['net_R']-old['net_R']))
    result['contract_selection']=dict(status='PREOPEN_ROUTE_SAME_CONTRACT_TO_NEXT_CASH_OPEN',selection_records=len(choices),expiry_guard_sessions=sum(x['expiry_guard'] for x in choices),old_result_sha256=h.sha(archive.RESULT),future_route_not_used=True)
    h.dump(directory/'contract-decisions.json',choices)
    for b in cash:
        result['coverage'][b].update(primary_cash_days=len(cash[b]),strict_excluded_cash_days=sum(d in bad for d in cash[b]))
    h.dump(directory/'summary.json',result);h.dump(directory/'daily-panels.json',private_panels)
    h.dump(directory/'complete-day-exclusions.json',sorted(bad))
    for m,rows in models.items():h.dump(directory/(m+'-trades.json'),tp.clean_ledger(rows))
    (directory/'report.md').write_text(report(result))
    fields=['sample','period','model','N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R','max_marked_drawdown_points','positive_quarters_R','traded_quarters','mean_net_R_per_cash_day','ci95_low','ci95_high','total_ci95_low','total_ci95_high','p_raw_two_sided','p_holm15']
    with (directory/'performance-inference.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for sample in SAMPLES:
            for b in BLOCKS:
                for m in MODELS:
                    x=result['samples'][sample][b][m];i=x['inference']
                    writer.writerow(dict(sample=sample,period=b,model=m,
                        **{k:x[k] for k in fields[3:12]},mean_net_R_per_cash_day=i['mean_net_R_per_cash_day'],
                        ci95_low=i['mean_ci95'][0],ci95_high=i['mean_ci95'][1],total_ci95_low=i['expected_total_R_ci95'][0],total_ci95_high=i['expected_total_R_ci95'][1],
                        p_raw_two_sided=i['p_raw_two_sided'] if sample=='OBSERVED_PATH' else '',p_holm15=i['p_holm15'] if sample=='OBSERVED_PATH' else ''))
    verify();return result


def replay():
    if PROOF.exists():return verify()
    result=one_run(OUT/'run1');print('Five fixed variants and bootstrap complete; independently replaying sources',flush=True)
    one_run(OUT/'run2')
    hashes=lambda d:{p.name:h.sha(p) for p in d.iterdir() if p.is_file()}
    a,b=hashes(OUT/'run1'),hashes(OUT/'run2')
    if a!=b:raise AssertionError('Consolidation replay differs')
    h.dump(RESULT,result);REPORT.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,REPORT]+[folder/name for folder in (OUT/'run1',OUT/'run2') for name in a]
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_SAME_CONTRACT_REPLAYS',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(status='COMPLETE',unique_variants=5,primary_tests=FAMILY,bootstrap_reps=REPS,criteria=result['criteria'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('register','replay','verify'))
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
