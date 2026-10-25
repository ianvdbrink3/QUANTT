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
from scripts.regime_consolidation.inference import joint,REPS,SEED,FAMILY

h=tp.h
c=tp.c
frozen=tp.frozen
ROOT=tp.ROOT
OUT=ROOT/'artifacts/regime-consolidation'
LOCK=ROOT/'research/regime-consolidation-lock.json'
RESULT=ROOT/'research/regime-consolidation-results.json'
PROOF=ROOT/'research/regime-consolidation-verification.json'
REPORT=ROOT/'docs/REGIME_CONSOLIDATION_STATISTICS.md'
BLOCKS=('2019_2021','2024_2026','COMBINED')
SAMPLES=('OBSERVED_PATH','COMPLETE_DAY_SENSITIVITY')
METHOD=dict(date='2026-10-25',status='EXPLORATORY_POST_SELECTION_CONSOLIDATION_NOT_INDEPENDENT_VALIDATION',
    universe='Same1151 eligible entry sessions, same preopen-SMA20 common629+395 candidate sessions yielding original723 bull nights. Preserve original100 selective A and149 B, including original2021Jun4 A outside common preopen population. Same contract/endpoint/usablebar constraints, no cross2021--2024 trade.',
    models=dict(S1_SELECTIVE='Original A100 with fixed0.50priorATR catastrophe-stop plus unchanged B149(P/+1ATR).',
                S2_BROAD_NO_STOP='Original bull723:current RTHclose>terminalSMA20 at16:00, no overnight stop, plus B149.',
                S2_BROAD_STOP='Same bull723 with fixed0.50priorATR catastrophe-stop, plus B149.',
                S3_BASE_1X='One bull overnight position with fixed stop, including strong trenddays at SAME1x size. No added A leg and no B leg. This is also the bull-stop pillar in question2; counted once.',
                S3_NONHOT_1X='One bull overnight position with fixed stop ONLY if current completed RTHrange/priorATR<=0.85 (exclude strict>0.85 regardless close location). No B leg, no short and no increased sizing.'),
    execution='Frozen two_pillar.core.night and price_volume G1_ATR select/execute/marks, unchanged. Entry16:00open to next cash09:30open, stop active fromentry, tick-rounded towardentry, adverse gap open fills. No new stop-distance, clock, target or volume search. All variants one full ATR-normalized position at a time. Rawpoints1NQ/trade; 1.225pt($24.50)RT per executed leg without netting.',
    accounting='Same749/422 full cash calendars, flat days included. Overnight PnL assigned next cash16:00boundary; B to current cash day. Assert non-overlap chronologically; minuteopen/close+knownfill DD with fees atentry. PF per execution in netR, dailyPF in JSON; Sharpe sqrt252 dailymeanR/SD, not accountROI; +quarters from netR cash-boundary attribution.',
    inference=dict(seed=SEED,replications=REPS,block_months=2,objects=list(MODELS),
                   method='Joint moving blocks of two consecutive calendar months within each era, same draws across all5objects. Reuse earlier noncircular block-index scheme and trim to original monthcount; sampled daycount handles unequal/partial months. No block crosses era gap. Combined mean uses fixed original749:422 cash-day era weights.',
                   target='Mean netR per full cash session including zero-position days. Nominal95% BASIC bootstrap CI:observedmean minus97.5/2.5percentiles of centered bootstrap mean errors. Approximate two-sided equal-tail centered-null bootstrap p, plus-one correction. Expected-total-R CI=meanCI times fixed original cash-day count, not uncertainty about already realized PnL.',
                   multiple='15 PRIMARY tests=5uniquevariants x3periods, Holm15 p-values. Also basic Bonferroni15 simultaneous95% interval set (99.6667%marginal). Duplicate bull-stop label is not a new test. Corrections apply only this round; cannot undo earlier strategy selection or all historical mining.',
                   assumptions='Approximate dependent bootstrap; only36historical/21recent months and potential nonstationarity. Noncircular endpoints underrepresented, explicitly reported. No selected blocklength, no alternative method chosen after seeing pvalues. Raw and adjusted p both reported.',
                   sensitivity='Complete-day sensitivity reuses identical bootstrap seeds/method as diagnostic. Its nominalCIs are separately identified; not a second confirmatory family or rescue decision. No sensitivity p-values used for promotion.'),
    missing='Observed-path stop outcomes conditional on no hidden earlier trigger in missing minutes. Report each pillar incomplete/unknown count. Strict COMMON complete-day sensitivity drops entire cash-boundary day (including B that day) whenever any qualifying bull or originalA night has a missing scheduled minute anywhere in original holdingwindow. Filter by data coverage only, not stop exit or PnL. Excluded days/trades saved privately; no bar filling.',
    verdict='Report whether nominalCI>0 forS1,S2both,andbull-stop in EACHera andcombined; also Holm15 and simultaneousCI criteria separately. No formal independent approval, no assertion that stop removes gap/unobserved tail risk.',
    publication='Append-only local report, JSON, aggregateCSVs and private ledgers. No push/deploy requested. Hash-preserve prior outputs including uncommitted work; two fresh rawsource replays, A/B/bull parity and byte-identical outputs.')


def verify():
    tp.verify()
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
    tp.verify()
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    files={n:h.sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}
    h.dump(LOCK,dict(method=METHOD,files=files,anchor_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()))
    return dict(status='FIVE_VARIANTS_AND_INFERENCE_LOCKED_BEFORE_OUTCOMES',protected=len(files))


def rebuild():
    data,sources=tp.pv.inputs()
    original=lambda name:json.loads((tp.OUT/'run1'/name).read_text())
    astop=[];B=[];bull=[];bullstop=[];cash={};coverage={}
    for block,d in data.items():
        d['active']=d['active'].sort_index()
        if not d['active'].index.is_unique:raise ValueError('Duplicate active minute')
        d['groups']=dict(tuple(d['active'].groupby('trade_date')))
        cash[block]=h.cash_dates(min(d['dates']),max(d['dates']))
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
            if not is_A and not is_bull:continue
            nextday=nextcash.get(day)
            if nextday is None:continue
            path,code=tp.path_inputs(d,day,nextday)
            if path is None:continue
            times,prices,missing=path
            tag=dict(block=block,range_atr=float((max(p['high'])-min(p['low']))/ctx['atr']),strong_day=is_A)
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
        coverage[block]=counts
    tp.parity(astop,original('A_STOP-trades.json'),('entry_price','exit_price','net_points','net_R'))
    tp.parity(B,original('B-trades.json'),('entry_bar','exit_bar','entry_price','exit_price','net_points','net_R'))
    tp.parity(bull,original('BENCH_BULL-trades.json'),('entry_price','exit_price','net_points','net_R'))
    if (len(astop),len(B),len(bull))!=(100,149,723):raise ValueError('Frozen source counts changed')
    return assemble(astop,B,bull,bullstop),cash,coverage,sources,astop,bullstop


def report(result):
    lines=['# Consolidatie: vijf vaste regimevarianten en onzekerheid','',result['status'],'',
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
    lines += ['', '## Dekking','', '```json',json.dumps(result['coverage'],indent=2),'```','',
              '## Vooraf vastgelegde methode','']+[f'- {k}: {v}' for k,v in METHOD.items()]
    lines += ['', '## Kwartaalstabiliteit','', '| Sample | Periode | Model | Kwartaal | N | Netto R | Netto pt |','|---|---|---|---|---:|---:|---:|']
    for sample in SAMPLES:
        for b in BLOCKS:
            for m in MODELS:
                lines += [f"| {sample} | {b} | {m} | {q['quarter']} | {q['N']} | {q['net_R']:.5f} | {q['net_points']:.3f} |" for q in result['samples'][sample][b][m]['quarterly']]
    return '\n'.join(lines)+'\n'


def one_run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    models,cash,coverage,sources,astop,bullstop=rebuild()
    bad={t['exit_day'] for t in astop+bullstop if not t['complete_holding_path']}
    result=dict(status='POST_SELECTION_CONSOLIDATION_NOT_INDEPENDENT_CONFIRMATION',method=METHOD,
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
    # S1 must reproduce the already reported stopped-A+B, not become a new fit.
    previous=json.loads(tp.RESULT.read_text())
    for b in BLOCKS:
        for field in ('N','net_R','net_points','max_marked_drawdown_R','max_marked_drawdown_points','sharpe_daily_R'):
            np.testing.assert_allclose(result['samples']['OBSERVED_PATH'][b]['S1_SELECTIVE'][field],previous['portfolio'][b]['A_STOP_PLUS_B'][field],rtol=0,atol=1e-8)
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
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_CONSOLIDATION_REPLAYS',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(status='COMPLETE',unique_variants=5,primary_tests=FAMILY,bootstrap_reps=REPS,criteria=result['criteria'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('register','replay','verify'))
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
