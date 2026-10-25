"""python -m scripts.two_pillar register|replay|verify. Append-only local audit."""
import argparse
import csv
import json
import subprocess

import numpy as np
import pandas as pd

from scripts.price_volume import __main__ as pv
from scripts.price_volume import core as frozen
from scripts.two_pillar import core as c

h=pv.h
ROOT=h.ROOT
OUT=ROOT/'artifacts/two-pillar'
LOCK=ROOT/'research/two-pillar-lock.json'
RESULT=ROOT/'research/two-pillar-results.json'
PROOF=ROOT/'research/two-pillar-verification.json'
REPORT=ROOT/'docs/TWO_PILLAR_BENCHMARK_RISK_PORTFOLIO.md'
BLOCKS=('COMBINED','2019_2021','2024_2026')
PORTFOLIOS=('A','B','A_PLUS_B','A_STOP','A_STOP_PLUS_B')
METHOD=dict(date='2026-10-25',status='DESCRIPTIVE_CONSUMED_DEVELOPMENT_AUDIT',
    preservation='Preserve all previous files and price_volume outputs. Exactly original A100 and B149, recomputed from source with unchanged selectors. No other models, parameter fitting, reversed shorts, best-of choice, live approval, Git push or deployment.',
    common='1024 entry-session dates with PREOPEN SMA20 available (629old,395recent) inside fixed1151priorATR pool. These are candidate dates, not1024 guaranteed executable nights. Same next-actual-cash-session, same-contract, endpoint and usable-bar requirements as original A. No missing-price filling or crossing2021--2024.',
    comparators='ALL on common dates; BULL on these same dates with completed current RTHclose>current terminal SMA20 (known at16:00, exactly the base condition of original A). A_MATCHED is original A intersect common executable nights; also retain original A100 separately if masks differ. Report membership difference rather than forcing100 into1024. BULL is not yesterday preopen bull: it is entry-time close>SMA20, matching original A.',
    scaling='ATR14 known before entry-session09:30, never next-day ATR. netR=(exit-entry-1.225)/entry_session_priorATR; netpct=100*(exit-entry-1.225)/entry_price. Percentage sums descriptive arithmetic sums, not compounded capital returns. Costs applied once per execution, including stopped trades.',
    MAE='Gross price excursion from actual16:00entry to minimum observed minute low before next09:30, also including exit09:30OPEN; never its low/close. Express positive adverse magnitude / priorATR. Incomplete holding paths give observed lower bounds; report all100 and complete-path subset separately.',
    stop='ONE fixed catastrophe-stop from16:00entry through next actual cash09:30open:entry-0.50priorATR rounded TOWARDentry to0.25tick. A stop touch fills level; gap through stop fills worse actual minuteopen, may lose>0.50R. Earliest observed trigger only, no target, no restart; same total1.225pt friction. Maintenance/weekends have no invented print. Endpointbar only open can trigger. No extra stop-slippage grid.',
    missing_stop='Same100 observed-path simulations reported conditionally; missing scheduled minutes before simulated exit mean actual first-stop outcome cannot be certified. Also paired original/stop results on fully observed original holding paths, not a fitted exclusion. Missing minutes after an already identified stop cannot change that fill. No unknown bars are assumed safe.',
    portfolio='Primary A(original no stop)+B(original P/+1ATR), each full1/ATR unit per sequential position, no halfweight or fitted allocation. Raw points shown separately for1NQ/trade, not implied back-conversion of normalized sizing. Additional fixed A_STOP and A_STOP+B are labeled sensitivity, not chosen in hindsight.',
    chronology='Assert chronological entry>=previous exit per model and combination. All positions flat before next daily16:00boundary. Daily scores realized by that boundary:overnight result assigned next actual cash session even if a stop occurred in prior civil evening; B to its exit session. Use every cash session incl flat/early-close days from first eligible date to last, not trade-only or only1151clean-entry dates. No zero days during2022--2024 gap.',
    metrics='PF in R on net individual executions (also rawpoint/%PF for benchmark); report daily aggregated PF separately in JSON. Sharpe=sqrt252*mean full-cash-day netR/SD(ddof1), no account-risk-free/return-on-capital interpretation. MaxDD chronological observed minuteopens/closes plus known fills, fees atentry, in R and rawpoints. Quarterly netR and netpoints by daily16:00accounting session; report positive R quarters/quarters with trades.',
    validation='Two periods and quarterly sequence are fixed-rule chronological stability, NOT new out-of-sample or honest walk-forward validation:both periods and survivor selection already consumed. No new significance tests or independent promotion.',
    reproduce='Two source reconstructions, original A/B numeric and membership parity, normalization/fee identities, nonoverlap assertions, protected-file checks and byte-identical outputs.')


def verify():
    pv.verify()
    lock=json.loads(LOCK.read_text())
    if lock['method']!=METHOD:raise ValueError('Audit method changed')
    for name,digest in lock['files'].items():
        if h.sha(ROOT/name)!=digest:raise ValueError('Protected bytes changed: '+name)
    if PROOF.exists():
        for name,digest in json.loads(PROOF.read_text())['files'].items():
            if h.sha(ROOT/name)!=digest:raise ValueError('Audit output changed: '+name)
    return dict(status='EARLIER_RESEARCH_AND_AUDIT_BYTES_VERIFIED',protected=len(lock['files']))


def register():
    if LOCK.exists():return verify()
    pv.verify()
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    files={n:h.sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}
    h.dump(LOCK,dict(method=METHOD,files=files,anchor_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()))
    return dict(status='BENCHMARK_STOP_AND_PORTFOLIO_METHOD_RECORDED_BEFORE_NEW_OUTCOMES',protected=len(files))


def path_inputs(data, day, nextday):
    groups=data['groups'];g=groups.get(day);ng=groups.get(nextday)
    if g is None or ng is None:return None,'MISSING_NEXT_SESSION'
    if len(set(g.contract))!=1 or len(set(ng.contract))!=1 or g.contract.iloc[0]!=ng.contract.iloc[0]:
        return None,'CONTRACT_SWITCH'
    start,end=h.at(day,'16:00'),h.at(nextday,'09:30')
    rows=data['active'].loc[start:end]
    if start not in rows.index or end not in rows.index:return None,'MISSING_ENDPOINT'
    if 'usable' in rows and not rows.usable.all():return None,'INVALID_HOLDING_BAR'
    expected=[]
    for d in pd.bdate_range(day,nextday).strftime('%Y-%m-%d'):
        expected.extend(data['calendar'].grid(d))
    expected=pd.DatetimeIndex(expected);expected=expected[(expected>=start)&(expected<end)]
    return (rows.index,{k:rows[k].to_numpy(float) for k in frozen.FIELDS},expected.difference(rows.index)),'FILLED'


def parity(actual, original, fields):
    if {t['day'] for t in actual}!={t['day'] for t in original}:raise ValueError('Original trade membership changed')
    reference={t['day']:t for t in original}
    for t in actual:
        for field in fields:
            if not np.isclose(t[field],reference[t['day']][field],rtol=0,atol=1e-8):
                raise ValueError('Original numeric parity failed '+t['day']+' '+field)


def clean_ledger(rows):
    return [{k:v for k,v in t.items() if k!='path_points'} for t in rows]


def make_report(result):
    lines=['# Twee pijlers: schaal, benchmark, overnight-risico en portefeuille','',result['status'],'',
           'Vaste regels op reeds bekeken ontwikkelingsdata; geen nieuwe onafhankelijke toets. A=16:00->volgende09:30 na sterke trenddag; B=P/+1ATR. Kosten1.225punt pertrade.','',
           '## Benchmark op gemeenschappelijke SMA20-populatie','',
           '| Blok | Groep | N | Netto pt/trade | Netto R/trade | Netto %/trade | PF pt | PF R | PF % |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda v,d=3:'n/a' if v is None else f'{v:.{d}f}'
    for block in BLOCKS:
        for name,x in result['benchmarks'][block].items():
            lines.append('| '+block+' | '+name+' | '+str(x['N'])+' | '+
                         ' | '.join(fmt(x[u][key],5 if u in ('R','pct') else 3) for u,key in
                                    [('points','mean_net'),('R','mean_net'),('pct','mean_net'),('points','profit_factor'),('R','profit_factor'),('pct','profit_factor')])+' |')
    lines+=['','## MAE in vooraf bekende ATR-eenheden','',
            '| Blok | Pad | N | P10 | P25 | P50 | P75 | P90 | P95 | Max |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for b in BLOCKS:
        for name,x in result['MAE'][b].items():
            lines.append('| '+b+' | '+name+' | '+str(x['N'])+' | '+' | '.join(fmt(x[k],4) for k in ('P10','P25','P50','P75','P90','P95','maximum'))+' |')
    lines+=['','## Portefeuille (R per vooraf bekende ATR, raw points apart)','',
            '| Blok | Model | N | Netto R | Netto pt | PF R | Sharpe dagelijks R | DD R | DD pt | +R kwartalen |',
            '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for b in BLOCKS:
        for name,x in result['portfolio'][b].items():
            lines.append(f"| {b} | {name} | {x['N']} | {x['net_R']:.5f} | {x['net_points']:.3f} | {fmt(x['trade_PF_R'])} | {fmt(x['sharpe_daily_R'])} | {x['max_marked_drawdown_R']:.5f} | {x['max_marked_drawdown_points']:.3f} | {x['positive_quarters_R']}/{x['traded_quarters']} |")
    lines+=['','## Stop: gepaarde controle uitsluitend volledige holdingpaden','',
            '| Blok | Variant | N | Netto R | Netto pt | PF R | DD R | DD pt |',
            '|---|---|---:|---:|---:|---:|---:|---:|']
    for b in BLOCKS:
        for name,x in result['complete_stop_pairs'][b].items():
            lines.append(f"| {b} | {name} | {x['N']} | {x['net_R']:.5f} | {x['net_points']:.3f} | {fmt(x['trade_PF_R'])} | {x['max_marked_drawdown_R']:.5f} | {x['max_marked_drawdown_points']:.3f} |")
    lines+=['','## Beschikbaarheid en stopidentificatie','', '```json',json.dumps(result['coverage'],indent=2),'```','',
            '## Vooraf vastgelegde methode','']+[f'- {k}: {v}' for k,v in METHOD.items()]
    lines+=['','## Kwartaalstabiliteit op uitstap-/cash-boundary-datum','',
            '| Blok | Model | Kwartaal | N | Netto R | Netto pt |','|---|---|---|---:|---:|---:|']
    for b in BLOCKS:
        for m,x in result['portfolio'][b].items():
            lines += [f"| {b} | {m} | {q['quarter']} | {q['N']} | {q['net_R']:.5f} | {q['net_points']:.3f} |" for q in x['quarterly']]
    return '\n'.join(lines)+'\n'


def one_run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    datasets,sources=pv.inputs()
    original_A=json.loads((pv.OUT/'run1/G3_1600_OPEN-trades.json').read_text())
    original_B=json.loads((pv.OUT/'run1/G1_ATR-trades.json').read_text())
    old_A={t['day']:t for t in original_A}
    A=[];B=[];stopped=[];bench={k:[] for k in ('A_ORIGINAL','A_MATCHED','BULL','ALL')}
    cash_by_block={};coverage={};cohorts={}
    for block,data in datasets.items():
        data['active']=data['active'].sort_index()
        if not data['active'].index.is_unique:raise ValueError('Duplicate active timestamps')
        data['groups']=dict(tuple(data['active'].groupby('trade_date')))
        dates=data['dates'];common={d for d in dates if data['features'][d]['bull'] is not None}
        expected=629 if block=='2019_2021' else 395
        if len(common)!=expected:raise ValueError('SMA20 common population changed')
        nextcash=dict(zip(data['cash'][:-1],data['cash'][1:]))
        cash=h.cash_dates(min(dates),max(dates));cash_by_block[block]=cash
        counts=dict(entry_pool=len(dates),SMA20_candidate_dates=len(common),cash_days=len(cash),
                    selected_not_in_common=[],benchmark_rejections={},stop_reasons={},original_A_parity=False,original_B_parity=False)
        executable=[]
        for day in dates:
            p,base=data['state'][day];ctx=dict(base,**data['features'][day])
            # Replay only the two frozen models, no new selectors or fitting.
            ev=frozen.select_g1(p,ctx,ctx['prior_volumes'])
            bt,code=frozen.execute(p,ctx,'G1_ATR',ev)
            if bt:
                start=h.at(day,'09:30')+pd.Timedelta(minutes=bt['entry_bar'])
                end=h.at(day,'09:30')+pd.Timedelta(minutes=bt['exit_bar'])
                B.append(c.enrich(dict(bt,day=day,exit_day=day,entry_time=start.isoformat(),exit_time=end.isoformat(),
                                      block=block,path_points=frozen.marks(bt,p)),ctx['atr']))
            is_A=frozen.strong_day(p,ctx)
            if day not in common and not is_A:continue
            nextday=nextcash.get(day)
            if nextday is None:
                code='NO_NEXT_CASH_SESSION';path=None
            else:
                path,code=path_inputs(data,day,nextday)
            if path is None:
                if day in common:counts['benchmark_rejections'][code]=counts['benchmark_rejections'].get(code,0)+1
                continue
            times,prices,missing=path
            trade=dict(c.night(day,nextday,times,prices,ctx['atr'],missing),block=block)
            if day in common:
                executable.append(day);bench['ALL'].append(trade)
                if p['close'][-1]>ctx['sma_today']:bench['BULL'].append(trade)
            if is_A:
                A.append(trade);bench['A_ORIGINAL'].append(trade)
                if day in common:bench['A_MATCHED'].append(trade)
                else:counts['selected_not_in_common'].append(day)
                st=dict(c.night(day,nextday,times,prices,ctx['atr'],missing,catastrophe=True),block=block)
                stopped.append(st);counts['stop_reasons'][st['reason']]=counts['stop_reasons'].get(st['reason'],0)+1
        aa=[t for t in A if t['block']==block];bb=[t for t in B if t['block']==block];ss=[t for t in stopped if t['block']==block]
        parity(aa,[t for t in original_A if t['block']==block],('entry_price','exit_price','gross_points','net_points'))
        parity(bb,[t for t in original_B if t['block']==block],('entry_bar','exit_bar','entry_price','exit_price','gross_points','net_points'))
        counts.update(original_A_parity=True,original_B_parity=True,executable_common_nights=len(executable),
                      selected_A=len(aa),selected_complete_paths=sum(t['complete_holding_path'] for t in aa),
                      original_missing_minutes=sum(t['missing_holding_minutes'] for t in aa),
                      stopped_path_unidentified=sum(not t['stop_path_identified'] for t in ss))
        coverage[block]=counts
        cohorts[block]=dict(SMA20_candidates=sorted(common),executable_common=executable)
    if len(A)!=100 or len(B)!=149:raise ValueError('Frozen model counts changed')
    allcash=sorted(set(d for ds in cash_by_block.values() for d in ds))
    raw_portfolios=dict(A=A,B=B,A_PLUS_B=A+B,A_STOP=stopped,A_STOP_PLUS_B=stopped+B)
    result=dict(status='DESCRIPTIVE_SCALE_BENCHMARK_RISK_PORTFOLIO_NOT_NEW_VALIDATION',
                method=METHOD,coverage=coverage,source_verification=sources,benchmarks={},MAE={},portfolio={},complete_stop_pairs={},comparisons={})
    for block in BLOCKS:
        select=lambda rows:[t for t in rows if block=='COMBINED' or t['block']==block]
        cash=allcash if block=='COMBINED' else cash_by_block[block]
        groups={k:select(v) for k,v in bench.items()}
        if not {t['day'] for t in groups['A_MATCHED']} <= {t['day'] for t in groups['BULL']} <= {t['day'] for t in groups['ALL']}:
            raise AssertionError('Benchmark nesting failed')
        result['benchmarks'][block]={k:c.description(v) for k,v in groups.items()}
        base=select(A);complete=[t for t in base if t['complete_holding_path']]
        result['MAE'][block]=dict(observed_all=c.mae_distribution(base),complete=c.mae_distribution(complete))
        result['portfolio'][block]={k:c.stats(select(v),cash) for k,v in raw_portfolios.items()}
        keys={t['day'] for t in complete}
        result['complete_stop_pairs'][block]=dict(A=c.stats(complete,cash),A_STOP=c.stats([t for t in select(stopped) if t['day'] in keys],cash))
        selected=result['benchmarks'][block]['A_MATCHED']
        result['comparisons'][block]={}
        for name in ('BULL','ALL'):
            ref=result['benchmarks'][block][name]
            result['comparisons'][block][name]={u:dict(mean_net_difference=selected[u]['mean_net']-ref[u]['mean_net'],
                    PF_difference=selected[u]['profit_factor']-ref[u]['profit_factor']) for u in ('points','R','pct')}
    result['method_sha256']=h.sha(LOCK)
    h.dump(directory/'summary.json',result);h.dump(directory/'cohorts.json',cohorts)
    for name,rows in dict(A=A,B=B,A_STOP=stopped,**{'BENCH_'+k:v for k,v in bench.items()}).items():
        h.dump(directory/(name+'-trades.json'),clean_ledger(rows))
    with (directory/'A-normalized-trades.csv').open('w',newline='') as stream:
        fields=['block','day','exit_day','entry_price','exit_price','atr','gross_points','net_points','gross_R','net_R','gross_pct','net_pct','mae_R','complete_holding_path','missing_holding_minutes']
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(clean_ledger(A))
    (directory/'report.md').write_text(make_report(result));verify()
    return result


def replay():
    if PROOF.exists():return verify()
    result=one_run(OUT/'run1');print('Benchmark, stop and sequential portfolio complete; replaying sources',flush=True)
    one_run(OUT/'run2')
    hashes=lambda folder:{p.name:h.sha(p) for p in folder.iterdir() if p.is_file()}
    a,b=hashes(OUT/'run1'),hashes(OUT/'run2')
    if a!=b:raise AssertionError('Two source replays differ')
    h.dump(RESULT,result);REPORT.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,REPORT]+[folder/name for folder in (OUT/'run1',OUT/'run2') for name in a]
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_BENCHMARK_STOP_PORTFOLIO_REPLAYS',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(status='COMPLETE',A=100,B=149,bench_candidate_dates=1024)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('register','replay','verify'))
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
