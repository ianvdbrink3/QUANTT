"""python -m scripts.judas_replacement register|replay|verify. No parameter changes."""
import argparse
import csv
import json
import subprocess

import numpy as np
import pandas as pd

from scripts.ict_study import __main__ as ict
from scripts.ict_study import core as signal_core
from scripts.same_contract import __main__ as base
from scripts.same_contract.core import path as holding_path
from scripts.oos_preparation.year import load_registered
from scripts.two_pillar import core as metrics
from .core import PERIODS,SEEDS,REPS,key,split_baseline,daily,overlap,inference

h=base.h;ROOT=base.ROOT
OUT=ROOT/'artifacts/judas-replacement'
LOCK=ROOT/'research/judas-replacement-lock.json'
RESULT=ROOT/'research/judas-replacement-results.json'
PROOF=ROOT/'research/judas-replacement-verification.json'
REPORT=ROOT/'docs/JUDAS_ONE_FOR_ONE_REPLACEMENT.md'
JUDAS='ICT3_5m_BOTH_OPEN0830_JUDAS_2R'
SPEC=next(s for s in ict.SPECS if s.name==JUDAS)
METHOD=dict(date='2026-10-25',status='EXPLORATORY_POST_SELECTION_REPLACEMENT_NOT_INDEPENDENT_VALIDATION',
 baseline_commit='2ec3a07adcf2f1bc0301c267a4f410ce44b69905',
 rules='Exactly selected ICT3_5m_BOTH_OPEN0830_JUDAS_2R, frozen one-tick trade-through entry, unchanged targets/stop/fee. S1-Judas=all original selective stopped A plus Judas; S2-Judas=all original broad unstopped bull nights plus Judas. Remove exactly original B149. No50/50 allocation or netting; each sequential position full original ATR exposure.',
 strict_scope='Trade-through means one tick beyond the entry limit. Targets retain the frozen ICT touch/causal-order rules; it is not a tick-level or queue certificate. Overnight source/fill limitations remain identical to baseline.',
 winner_check='Recheck ALL80 frozen variants in each era and both fill modes: total netATR-R,tradePF_ATR anddailySharpe must each be strictly greater than B. Never assume the earlier touch-only label alone proves this. Report all actual qualifying variants and both-fill metrics.',
 units='PortfolioR=netpoints/priorATR14. Standalone ICT initialStopR uses initial stopdistance and is separately reported; NEVER sum initialStopR with overnight ATR-R. NQpoints1contract/execution; total1.225point($24.50)friction per executed leg; no MNQ-cost assumption.',
 reconstruction='Twice reconstruct sources, frozen B selectors, exact chosen Judas chain/strict fills, and same-held-contract overnight paths. Match every frozen ledger execution and original S1/S2 full stats incl marked DD. Complete-path/stop-identification limits carried, not changed or silently dropped.',
 chronology='Verify actual interval intersections for A and Judas, not only nominal RTH windows. Assert zero-overlap before summing at full size. All cash days749+422 included, zeros included, overnight assigned next cashdate, Judas samecashday. Report marked minuteopen/close DD plus fills, not unobservable tick-DD.',
 inference='20000 joint moving2calendar-month blocks, same fixed seeds as ICT scan2026102511/+1. Separate36old/21recent months; no era-gap blocks. Basic95%CIs and centered equal-tail two-sided p. Absolute S1-Judas andS2-Judas per3periods=6tests plus UNIQUE paired Judas-minus-B difference per3periods=3tests:Holm9. Also Bonferroni9 simultaneous95%totalR intervals. Delta exactly same for both portfolios and matches prior frozen ICT paired inference. Prior Holm480 and selection caveats remain; new Holm9 does not erase earlier scan.',
 outputs='Append-only new code/report/aggregateCSV/JSON/local dashboard. ALL existing tracked and untracked research and benchmark files hash-preserved. No new strategy/signals/grid/exit optimization and no independent confirmation claim.')


def verify():
    ict.verify();lock=json.loads(LOCK.read_text())
    if lock['method']!=METHOD:raise ValueError('Replacement method changed')
    for name,digest in lock['files'].items():
        if h.sha(ROOT/name)!=digest:raise ValueError('Protected file changed: '+name)
    if PROOF.exists():
        for name,digest in json.loads(PROOF.read_text())['files'].items():
            if h.sha(ROOT/name)!=digest:raise ValueError('Replacement output changed: '+name)
    return dict(status='BASELINE_AND_ICT_SCAN_IMMUTABLE',protected=len(lock['files']))


def register():
    if LOCK.exists():return verify()
    ict.verify()
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    h.dump(LOCK,dict(method=METHOD,files={n:h.sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}))
    return dict(status='EXACT_REPLACEMENT_METHOD_LOCKED')


def winners():
    x=json.loads(ict.RESULT.read_text());names=[];rows=[]
    for name in ict.NAMES:
        passed=all(x['samples'][fill][b][name][k]>x['benchmarks'][b]['B'][j]
          for fill in ('TOUCH','TRADE_THROUGH') for b in PERIODS[:2]
          for k,j in [('net_ATR_R','net_R'),('PF_ATR_R','trade_PF_R'),('sharpe_ATR_R','sharpe_daily_R')])
        if passed:
            names.append(name)
            for fill in ('TOUCH','TRADE_THROUGH'):
                for b in PERIODS:rows.append(dict(model=name,fill=fill,period=b,**x['samples'][fill][b][name]))
    return names,rows


def assert_ledger(actual,original,fields):
    a={key(t):t for t in actual};b={key(t):t for t in original}
    assert set(a)==set(b),'Execution membership changed'
    for k in a:
        for field in fields:np.testing.assert_allclose(a[k][field],b[k][field],atol=1e-9,rtol=0)


def rebuild():
    data,sources=base.tp.pv.inputs();B=[];J=[];cash={}
    for block,d in data.items():
        d['groups']=dict(tuple(d['active'].groupby('trade_date')))
        cash[block]=h.cash_dates(min(d['dates']),max(d['dates']))
        for day in d['dates']:
            p,ctx=ict.day_input(d,day)
            order=signal_core.signal(p,ctx,SPEC);t,_=signal_core.execute(p,order,touch=False)
            if t:
                J.append(metrics.enrich(dict(t,day=day,exit_day=day,block=block,model=JUDAS,
                    entry_time=(h.at(day,'09:30')+pd.Timedelta(minutes=t['entry_bar'])).isoformat(),
                    exit_time=(h.at(day,'09:30')+pd.Timedelta(minutes=t['exit_bar'])).isoformat()),ctx['atr']))
            rp,rc=d['state'][day];bc=dict(rc,**d['features'][day])
            event=base.frozen.select_g1(rp,bc,bc['prior_volumes']);bt,_=base.frozen.execute(rp,bc,'G1_ATR',event)
            if bt:
                B.append(metrics.enrich(dict(bt,day=day,exit_day=day,block=block,
                    entry_time=(h.at(day,'09:30')+pd.Timedelta(minutes=bt['entry_bar'])).isoformat(),
                    exit_time=(h.at(day,'09:30')+pd.Timedelta(minutes=bt['exit_bar'])).isoformat(),path_points=base.frozen.marks(bt,rp)),bc['atr']))
    oldB=json.loads((base.tp.OUT/'run1/B-trades.json').read_text())
    oldJ=json.loads((ict.OUT/'run1/orders-and-ledgers.json').read_text())['TRADE_THROUGH'][JUDAS]
    assert_ledger(B,oldB,('entry_bar','exit_bar','entry_price','exit_price','net_points','net_R'))
    assert_ledger(J,oldJ,('entry_bar','exit_bar','entry_price','exit_price','initial_risk','net_points','net_R','net_stop_R'))
    original={m:json.loads((base.OUT/'run1'/f'{name}-trades.json').read_text()) for m,name in [('S1','S1_SELECTIVE'),('S2','S2_BROAD_NO_STOP')]}
    full_old=pd.read_parquet(h.OUT/'contract-bars.parquet')  # equality to raw reconstruction was checked by pv.inputs
    full_recent,_,_=load_registered(ROOT)
    fulls={'2019_2021':{c:g.sort_index() for c,g in full_old.groupby('contract')},'2024_2026':{c:g.sort_index() for c,g in full_recent.groupby('contract')}}
    overnight={};quality={}
    for model,rows in original.items():
        A=split_baseline(rows,oldB);fresh=[]
        for old in A:
            assert pd.Timestamp(old['selection_time'])<=h.at(old['day'],'09:30')
            assert h.at(h.expiry(old['contract']),'09:30')>h.at(old['exit_day'],'09:30')
            holding,code=holding_path(fulls[old['block']][old['contract']],old['day'],old['exit_day'],data[old['block']]['calendar'])
            assert code=='FILLED';times,prices,missing=holding
            t=metrics.night(old['day'],old['exit_day'],times,prices,old['atr'],missing,catastrophe=model=='S1')
            fresh.append(dict(old,**t))
        assert_ledger(fresh,A,('entry_price','exit_price','net_points','net_R','mae_R','missing_holding_minutes'))
        overnight[model]=fresh
        quality[model]={b:dict(N=len([t for t in fresh if t['block']==b]),incomplete_paths=sum(not t['complete_holding_path'] for t in fresh if t['block']==b),unidentified_stop_paths=sum(not t['stop_path_identified'] for t in fresh if t['block']==b) if model=='S1' else None) for b in PERIODS[:2]}
    models=dict(S1_ORIGINAL=overnight['S1']+B,S2_ORIGINAL=overnight['S2']+B,S1_JUDAS=overnight['S1']+J,S2_JUDAS=overnight['S2']+J)
    audit={model:overlap(A,J) for model,A in overnight.items()}
    assert all(x['overlap_pairs']==0 and x['overlap_minutes']==0 for x in audit.values())
    return models,cash,sources,audit,quality


def report(x):
    lines=['# Judas — directe vervanging van pijler B','',METHOD['status'],'',
      'S1/S2 baseline2ec3a07 en de volledige ICT-scan blijven ongewijzigd. Geen50/50-verdunning: volledige A+Judas, B exact verwijderd. Alle portefeuillematenR gebruiken vooraf bekende ATR14; initiële stopR hieronder alleen voor losse ICT-trades.','',
      '## Zeven varianten — strenge entry trade-through, gecombineerd','',
      '| Variant | N | Netto ATR-R | Netto stopR | Netto pt | Win% | PF ATR | PF stop | Sharpe ATR | Sharpe stop | DD ATR | DD stop | +kalenderkwartalen |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda v:'n.v.t.' if v is None else f'{v:.6f}'
    for r in x['winner_rows']:
        if r['fill']!='TRADE_THROUGH' or r['period']!='COMBINED':continue
        lines.append('| '+r['model']+' | '+str(r['N'])+' | '+' | '.join(fmt(r[k]) for k in ('net_ATR_R','net_stop_R','net_points'))+' | '+fmt(100*r['winrate'])+' | '+' | '.join(fmt(r[k]) for k in ('PF_ATR_R','PF_stop_R','sharpe_ATR_R','sharpe_stop_R','max_marked_drawdown_ATR_R','max_marked_drawdown_stop_R'))+f" | {r['positive_quarters_ATR_R']}/{len(r['quarterly'])} |")
    lines+=['','## Portefeuilles — volledige oude en nieuwe vergelijking','',
      '| Periode | Model | N | Netto ATR-R | Netto pt | Win% | PF ATR-R | Sharpe | Mark-DD ATR-R | Mark-DD pt | +kalenderkwartalen |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for b in PERIODS:
        for model,r in x['performance'][b].items():
            lines.append(f"| {b} | {model} | {r['N']} | {r['net_R']:.6f} | {r['net_points']:.3f} | {100*r['points']['winrate']:.3f} | {fmt(r['trade_PF_R'])} | {fmt(r['sharpe_daily_R'])} | {r['max_marked_drawdown_R']:.6f} | {r['max_marked_drawdown_points']:.3f} | {r['positive_quarters_R']}/{len(r['quarterly'])} |")
    lines+=['','## Onzekerheid — absolute portefeuilles en gepaarde meerwaarde','',
      'Nominaal95%basic moving2-maand-block-bootstrap,20.000trekkingen. Intervallen voor verwacht totaalR zijn het gemiddelde per cashdag ×vast aantal dagen. De gerealiseerde historische som zelf is niet onzeker. De gepaarde delta is voor beide vervangingen exact Judas−B en wordt daarom niet dubbel als bewijs geteld. Holm9 corrigeert deze nieuwe negen unieke contrasten; eerdere selectie uit80varianten blijft van toepassing.','',
      '| Periode | Contrast | Gemiddeld ATR-R/cashdag | 95%CI verwacht totaal ATR-R | p tweezijdig | Holm9 p | Familie95%Bonf9 totaal ATR-R |','|---|---|---:|---|---:|---:|---|']
    band=lambda r,k:'['+'; '.join(f'{z:.6f}' for z in r[k])+']'
    for b in PERIODS:
        for name,r in x['inference'][b].items():
            lines.append(f"| {b} | {name} | {r['mean_ATR_R_per_cash_day']:.8f} | {band(r,'expected_total_ATR_R_ci95')} | {r['p_raw_two_sided']:.6f} | {r['p_holm9']:.6f} | {band(r,'expected_total_ATR_R_familywise95_bonf9')} |")
    lines+=['','## Overlap en datakwaliteit','', '```json',json.dumps(dict(overlap=x['overlap'],quality=x['quality']),indent=2),'```','',
      'Strengefill betreft één tick trade-through bij de FVG-entry; target-touch en conservatieve intrabarvolgorde blijven zoals bevroren in de ICT-studie. Mark-DD gebruikt waargenomen minuutopens/-closes en fills, geen bewezen worst-tick drawdown. Onvolledige overnightpaden en onbekende eerdere stoptriggers worden niet achteraf weggefilterd.','',
      '## Kwartalen — alle kalenderkwartalen inclusief nulposities','', '| Periode | Model | Kwartaal | N | Netto ATR-R | Netto pt |','|---|---|---|---:|---:|---:|']
    for b in PERIODS:
        for model,r in x['performance'][b].items():
            for q in r['quarterly']:lines.append(f"| {b} | {model} | {q['quarter']} | {q['N']} | {q['net_R']:.6f} | {q['net_points']:.3f} |")
    lines+=['','## Vaste methode','']+[f'- {k}: {v}' for k,v in METHOD.items()]
    return '\n'.join(lines)+'\n'


def one_run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    names,wr=winners();assert len(names)==7,'Rechecked count differs; do not force seven'
    models,cash,sources,audit,quality=rebuild();allcash=sorted(d for ds in cash.values() for d in ds)
    stats={};panels=[];old=json.loads(base.RESULT.read_text())['samples']['OBSERVED_PATH']
    columns=('S1_ORIGINAL','S2_ORIGINAL','S1_JUDAS','S2_JUDAS')
    for b in PERIODS:
        ds=allcash if b=='COMBINED' else cash[b]
        subset={m:[t for t in v if b=='COMBINED' or t['block']==b] for m,v in models.items()}
        stats[b]={m:metrics.stats(rows,ds) for m,rows in subset.items()}
        for m,ref in [('S1_ORIGINAL','S1_SELECTIVE'),('S2_ORIGINAL','S2_BROAD_NO_STOP')]:
            for field in ('N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R','max_marked_drawdown_points','positive_quarters_R'):
                np.testing.assert_allclose(stats[b][m][field],old[b][ref][field],rtol=0,atol=1e-8)
        if b!='COMBINED':panels.append((b,ds,np.column_stack([daily(subset[m],ds) for m in columns])))
    inf,meta=inference(panels)
    previous=json.loads(ict.RESULT.read_text())['inference']
    for b in PERIODS:
        ref=previous[b][JUDAS]['MINUS_B'];got=inf[b]['JUDAS_MINUS_B']
        np.testing.assert_allclose(got['expected_total_ATR_R_ci95'],ref['total_ci95'],rtol=0,atol=1e-10)
        np.testing.assert_allclose(got['p_raw_two_sided'],ref['p_raw_two_sided'],rtol=0,atol=1e-10)
        got['prior_ICT_scan_p_holm480']=ref['p_holm480']
    result=dict(status=METHOD['status'],method=METHOD,winner_names=names,winner_rows=wr,performance=stats,
                inference=inf,bootstrap=meta,overlap=audit,quality=quality,source_verification=sources)
    h.dump(directory/'summary.json',result)
    h.dump(directory/'ledgers.json',{m:base.tp.clean_ledger(v) for m,v in models.items()})
    h.dump(directory/'daily-panels.json',{b:dict(dates=ds,columns=columns,net_ATR_R=values.tolist()) for b,ds,values in panels})
    (directory/'report.md').write_text(report(result))
    fields=['N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R','max_marked_drawdown_points','positive_quarters_R','cash_days']
    with (directory/'portfolio-performance.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['period','model']+fields+['calendar_quarters','winrate']);w.writeheader()
        for b in PERIODS:
            for m,r in stats[b].items():w.writerow(dict(period=b,model=m,**{k:r[k] for k in fields},calendar_quarters=len(r['quarterly']),winrate=r['points']['winrate']))
    fields=['N','net_ATR_R','net_stop_R','net_points','winrate','PF_ATR_R','PF_stop_R','sharpe_ATR_R','sharpe_stop_R','max_marked_drawdown_ATR_R','max_marked_drawdown_stop_R','positive_quarters_ATR_R']
    with (directory/'seven-variants.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['model','period','fill']+fields);w.writeheader()
        for r in wr:w.writerow({k:r[k] for k in w.fieldnames})
    with (directory/'inference.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['period','contrast','mean_ATR_R_per_cash_day','total_ci95_low','total_ci95_high','p_raw_two_sided','p_holm9','prior_ICT_scan_p_holm480']);w.writeheader()
        for b in PERIODS:
            for name,r in inf[b].items():w.writerow(dict(period=b,contrast=name,mean_ATR_R_per_cash_day=r['mean_ATR_R_per_cash_day'],total_ci95_low=r['expected_total_ATR_R_ci95'][0],total_ci95_high=r['expected_total_ATR_R_ci95'][1],p_raw_two_sided=r['p_raw_two_sided'],p_holm9=r['p_holm9'],prior_ICT_scan_p_holm480=r.get('prior_ICT_scan_p_holm480','')))
    verify();return result


def replay():
    if PROOF.exists():return verify()
    result=one_run(OUT/'run1');print('Replacement run1 complete; replaying from raw sources',flush=True)
    one_run(OUT/'run2');hashes=lambda d:{p.name:h.sha(p) for p in d.iterdir() if p.is_file()}
    a,b=hashes(OUT/'run1'),hashes(OUT/'run2');assert a==b,'Replacement replay differs'
    h.dump(RESULT,result);REPORT.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,REPORT]+[folder/n for folder in (OUT/'run1',OUT/'run2') for n in a]
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_JUDAS_REPLACEMENT_REPLAYS',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(status='COMPLETE',winners=len(result['winner_names']),overlap=result['overlap'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('register','replay','verify'))
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
