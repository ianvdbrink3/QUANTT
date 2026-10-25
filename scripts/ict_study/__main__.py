"""python -m scripts.ict_study register|replay|verify. No benchmark changes."""
import argparse
import csv
import json
import subprocess
from dataclasses import asdict,replace

import numpy as np
import pandas as pd

from scripts.same_contract import __main__ as benchmark
from scripts.price_volume import __main__ as pv
from scripts.two_pillar import core as metrics
from scripts.regime_consolidation.inference import sample_means,holm
from .core import catalog,signal,execute,retarget,window,FIELDS,aggregate

h=benchmark.h;ROOT=h.ROOT
OUT=ROOT/'artifacts/ict-study'
LOCK=ROOT/'research/ict-study-lock.json'
RESULT=ROOT/'research/ict-study-results.json'
PROOF=ROOT/'research/ict-study-verification.json'
REPORT=ROOT/'docs/ICT_CAUSAL_DEVELOPMENT_STUDY.md'
PERIODS=('2019_2021','2024_2026','COMBINED')
REPS=20000;SEED=2026102511
SPECS=catalog();NAMES=[s.name for s in SPECS]
METHOD=dict(date='2026-10-25',status='EXPLORATORY_CONSUMED_DEVELOPMENT_POOL_NOT_INDEPENDENT_VALIDATION',
    benchmark_commit='2ec3a07adcf2f1bc0301c267a4f410ce44b69905',
    universe='Same1171 cash sessions for accounting (749old+422recent), same1151 ATR-ready complete source entry sessions (733+418). Holidays/short/missing sessions remain flat, not newly repaired. No cross-era history. Prerequisite coverage per model reported. SMA20 prior strict consecutive cash closes; bull yesterday>SMA20, bear yesterday<SMA20 (ties neither).',
    displacement='User accepted mirrored bearish Judas counterpart and delegated displacement choice. Fixed before outcomes: gap>=0.03priorATR AND signed middle-candle body>=0.03priorATR. No threshold optimization. 0.10priorATR minimum stop widened structurally, never excluded for smaller initial distance.',
    fractal='The supplied definition is FIVE bars, strict2left+2right; known after center+2 closes. Equal highs/lows not pivots. Latest already confirmed opposite swing before crossing bar; no current-bar redefinition.',
    bars='Signals use aligned1m or5m bars from08:00NY; incomplete source blocks invalidate structure and pending sweep chain. New RTH day resets all state. All execution and DD remain on raw1m. No forming-bar entries.',
    levels='ICT1 two explicit pre-RTH level families: ON18:00(previouscivil)-09:30, PRE08:30-09:30. London is contained within ON, not a third post-hoc03:00 subgroup. Require every expected minute for a level; use available scheduled source data with no price filling. ICT2 AM priorhour09:00-10:00, PM13:00-14:00; snapshot known at window start. ICT3 anchors09:30open and08:30open separately.',
    chain='First strict sweep per level-side/window. Both-side sweeps in one signal-timeframe bar skipped as ambiguous; no claimed intrabar sequence. Sweep bar must complete before FVG middle-bar starts. Store extreme through completed confirmation, freeze at order. No reentry, one first candidate order/model/window even if unfilled or invalid target.',
    ICT1='09:30-11:30 entry window; low sweep->long/high sweep->short, confirmed opposite swing close-cross in middle or third FVG bar, strictly after sweep. Three exits2R,3R,oppositeON fixed at order. Gap+MSS known only after final thirdbar closes.',
    ICT2='Separate AM10:00-11:00 and PM14:00-15:00. FADE is first directional FVG after priorhour sweep, back toward prior range. CONTINUE reverses direction (high sweep->long). At confirmation continuation additionally requires an untouched PDH/ONH (long) or PDL/ONL(short), strictly beyond current completed RTHextreme. Closest qualifying draw stored; targets remain fixed2R/3R. No discretionary news filter or extra unrequested fractal-MSS requirement for this first-FVG model.',
    ICT3='First shakeout at least0.15priorATR from selected anchor09:30/08:30 during09:30-10:15. Bull-long requires priorbull, bearish mirroredshort requires priorbear. First matching FVG with thirdbar close strictly back above09:30open(long)/below(short), entry before10:30. Fixed exits2R,3R,TIME15:55open. BOTH includes both regime-aligned directions; BULL_LONG retains only original bullish rule.',
    entries='First limit at bullish Low[t] or bearish High[t], active from next1m boundary only; cancel unfilled at window end. Primary touch fill at quoted level, no favorable improvement. Separate paired one-tick trade-through fill sensitivity, not another parameter search. Entry-bar stop wins. Entry-bar target only if entry known atopen or closing price proves a later target cross. Later-open target before later intrabarstop; unresolved intrabarSL/TP stopfirst. Gapped stop fills adverse actualopen and can exceed1stopR. Targets touch; no exactqueue/fillcertificate.',
    risk='ICT1/3 stop1tick beyond observed sweep-extreme; ICT2 stop1tick beyond t-2low(long)/high(short). Widen to at least0.10priorATR and round outward0.25tick. $24.50RT=1.225pt per filled trade. No BE/trailing, all flat15:55open. StopR=netpoints/initial_stopdistance, ATR_R=netpoints/priorATR14. PF/Sharpe/DD in BOTH units; common ATR_R is benchmark scale. StopR is not ATR_R or accountROI.',
    comparisons='Frozen B149 and S1/S2 reused without modification and audited from committed ledgers. Standalone comparison uses full cash calendar incl zeros, ATR_R, points, tradePF and minute-markDD. Also daily correlation, overlap count, and descriptive equal0.5baseline+0.5ICT separate-sleeve panels (costs linearly scaled, no integerMNQ or ordernetting). Compare DAILY close DD/Sharpe to same endpoint baseline; overlapping sleeves allowed and explicitly counted. No future conflict exclusions or frozen benchmark trade substitutions.',
    inference='20000 moving2-calendar-month blocks with fixedseeds2026102511/+1, no era crossing, joint same draws across all80 objects. Basic nominal95CI and centered two-sided p on mean ATR_R/fullcashday. Also paired incremental mean versus fixed B. Global Holm480=80variants x3periods x2contrasts(zero,B). Touch family primary; trade-through is fixed execution sensitivity, reported without rescue p-values. No choice on significance; exploratory consumed-data p cannot certify independently profitable model.',
    outputs='All80specs x3periods for primary and pairedfillsensitivity, per-quarter aggregates, direction splits and causal chain/qualitycounts. Private event/trade/path/dailypanels stay Gitignored. Full rawsource reconstruction twice; byte-identical outputs; hash-check ALL pre-existing tracked files including current public benchmark and playbook.',
    origins=['https://www.youtube.com/watch?v=nQfHZ2DEJ8c','https://www.youtube.com/watch?v=Bkt8B3kLATQ'],
    interpretation='Explicit mechanical operationalization inspired by ICT and user definitions; not certification of authentic discretionary ICT, dealer intent, stop pools or profitable institutional causation.')


def verify():
    benchmark.verify();lock=json.loads(LOCK.read_text())
    if lock['method']!=METHOD or lock['catalog']!=[asdict(s) for s in SPECS]:raise ValueError('ICT method changed')
    for name,digest in lock['files'].items():
        if h.sha(ROOT/name)!=digest:raise ValueError('Frozen bytes changed: '+name)
    if PROOF.exists():
        for name,digest in json.loads(PROOF.read_text())['files'].items():
            if h.sha(ROOT/name)!=digest:raise ValueError('ICT output changed: '+name)
    return dict(status='BENCHMARK_AND_ICT_METHOD_VERIFIED',protected=len(lock['files']))


def register():
    if LOCK.exists():return verify()
    benchmark.verify()
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    files={n:h.sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}
    h.dump(LOCK,dict(method=METHOD,catalog=[asdict(s) for s in SPECS],files=files,anchor_commit=METHOD['benchmark_commit']))
    return dict(status='EIGHTY_VARIANTS_LOCKED_BEFORE_OUTCOMES',protected=len(files))


def levels(g,day,a,b):
    ix=pd.date_range(h.at(day,a),h.at(day,b),freq='min',inclusive='left')
    r=g.reindex(ix)
    if not len(ix) or not np.isfinite(r[list(FIELDS)].to_numpy(float)).all():return None
    if 'usable' in r and not r.usable.fillna(False).all():return None
    return float(r.low.min()),float(r.high.max())


def day_input(data,day):
    g=data['groups'][day];rth,base=data['state'][day];ctx=dict(base,**data['features'][day])
    ix=pd.date_range(h.at(day,'08:00'),h.at(day,'16:00'),freq='min',inclusive='left')
    q=g.reindex(ix);p={k:q[k].to_numpy(float,copy=True) for k in FIELDS}
    if 'usable' in q:
        bad=~q.usable.fillna(False).to_numpy(bool)
        for v in p.values():v[bad]=np.nan
    open0830=h.at(day,'08:30')
    ctx.update(ON=(ctx.get('ONL',np.nan),ctx.get('ONH',np.nan)),PRE=levels(g,day,'08:30','09:30'),
               AM=levels(g,day,'09:00','10:00'),PM=levels(g,day,'13:00','14:00'),
               OPEN0930=float(rth['open'][0]),OPEN0830=float(g.at[open0830,'open']) if open0830 in g.index else np.nan,
               bear=bool(ctx['prior_daily_close']<ctx['sma_prior']) if np.isfinite(ctx['sma_prior']) else None)
    return p,ctx


def prepare_orders(data):
    allorders={};allprices={};coverage={};checks=0
    keys={tuple(asdict(s).values())[:-1]:replace(s,target='2R') for s in SPECS}
    for block,d in data.items():
        d['groups']=dict(tuple(d['active'].groupby('trade_date')))
        counts=dict(ATR_ready=len(d['dates']),preopen_SMA20=0,ON=0,PRE=0,AM=0,PM=0,OPEN0830=0,orders={})
        for day in d['dates']:
            p,ctx=day_input(d,day);allprices[(block,day)]=(p,ctx)
            counts['preopen_SMA20']+=ctx['bull'] is not None
            for level in ('ON','PRE','AM','PM'):
                counts[level]+=ctx[level] is not None and bool(np.isfinite(ctx[level]).all())
            counts['OPEN0830']+=np.isfinite(ctx['OPEN0830'])
            cached_bars={tf:aggregate(p,tf) for tf in (1,5)}
            for key,spec in keys.items():
                order=signal(p,ctx,spec,cached_bars[spec.timeframe])
                # Future cut-off: reconstruct signal with no bars after its
                # actual confirmation (or whole window if no signal).
                cutoff=order['boundary'] if order else window(spec)[1]
                prefix={k:v[:90+cutoff].copy() for k,v in p.items()}
                assert signal(prefix,ctx,spec)==order,('future cutoff',block,day,spec.name)
                checks+=1
                if order:
                    earlier={k:v[:90+cutoff-1].copy() for k,v in p.items()}
                    assert signal(earlier,ctx,spec) is None,('premature signal',day,spec.name)
                    checks+=1
                allorders[(block,day,key)]=order
                counts['orders'][spec.name]=counts['orders'].get(spec.name,0)+(order is not None)
        coverage[block]=counts
    return allorders,allprices,coverage,checks


def rebuild():
    data,sources=pv.inputs();orders,prices,coverage,checks=prepare_orders(data)
    cash={b:h.cash_dates(min(d['dates']),max(d['dates'])) for b,d in data.items()}
    models={fill:{s.name:[] for s in SPECS} for fill in ('TOUCH','TRADE_THROUGH')};statuses={fill:{} for fill in models}
    for spec in SPECS:
        key=tuple(asdict(spec).values())[:-1]
        for block,d in data.items():
            for day in d['dates']:
                p,ctx=prices[(block,day)];order=retarget(orders[(block,day,key)],ctx,spec)
                for fill in models:
                    trade,code=execute(p,order,touch=fill=='TOUCH')
                    statuses[fill].setdefault(spec.name,{}).setdefault(block,{})
                    counts=statuses[fill][spec.name][block];counts[code]=counts.get(code,0)+1
                    if trade:
                        start=h.at(day,'09:30')+pd.Timedelta(minutes=trade['entry_bar']);end=h.at(day,'09:30')+pd.Timedelta(minutes=trade['exit_bar'])
                        models[fill][spec.name].append(metrics.enrich(dict(trade,day=day,exit_day=day,block=block,
                            entry_time=start.isoformat(),exit_time=end.isoformat(),model=spec.name),ctx['atr']))
    return models,cash,coverage,checks,sources,statuses


def inference(panels,bpanels):
    draws=[];means=[];counts=[];bdraws=[];bmeans=[];out={};meta={}
    for i,(block,dates,matrix) in enumerate(panels):
        draw,m=sample_means(dates,matrix,SEED+i,REPS);bmu=bpanels[block].mean()
        bdraw,_=sample_means(dates,bpanels[block][:,None],SEED+i,REPS)
        draws.append(draw);means.append(matrix.mean(axis=0));counts.append(len(dates));bdraws.append(bdraw);bmeans.append(bmu);meta[block]=m
    weights=np.asarray(counts)/sum(counts)
    draws.append(draws[0]*weights[0]+draws[1]*weights[1]);means.append(means[0]*weights[0]+means[1]*weights[1]);counts.append(sum(counts))
    bdraws.append(bdraws[0]*weights[0]+bdraws[1]*weights[1]);bmeans.append(bmeans[0]*weights[0]+bmeans[1]*weights[1])
    refs=[];pvalues=[]
    for b,draw,mu,n,bd,bmu in zip(PERIODS,draws,means,counts,bdraws,bmeans):
        out[b]={}
        for j,name in enumerate(NAMES):
            row={}
            for contrast in ('ZERO','MINUS_B'):
                observed=mu[j]-(bmu if contrast=='MINUS_B' else 0)
                values=draw[:,j]-(bd[:,0] if contrast=='MINUS_B' else 0)
                error=values-observed;lo,hi=np.quantile(error,[.025,.975]);ci=[float(observed-hi),float(observed-lo)]
                p=float(min(1,2*min((1+sum(error>=observed))/(REPS+1),(1+sum(error<=observed))/(REPS+1))))
                row[contrast]=dict(mean_ATR_R_per_cash_day=float(observed),mean_ci95=ci,total_ci95=[v*n for v in ci],p_raw_two_sided=p)
                refs.append((b,name,contrast));pvalues.append(p)
            out[b][name]=row
    adjusted=holm(pvalues)
    assert len(adjusted)==480
    for (b,name,contrast),p in zip(refs,adjusted):out[b][name][contrast]['p_holm480']=float(p)
    return out,dict(replications=REPS,seed=[SEED,SEED+1],family_tests=480,eras=meta)


def daily(rows,dates):
    result={d:0. for d in dates}
    for t in rows:result[t['exit_day']]+=t['net_R']
    return np.asarray(list(result.values()))


def daily_stats(values):
    x=np.asarray(values,float);equity=np.r_[0,np.cumsum(x)];sd=x.std(ddof=1)
    return dict(net_ATR_R=float(x.sum()),daily_sharpe=float(np.sqrt(252)*x.mean()/sd) if sd>0 else None,
                daily_close_drawdown_ATR_R=float(max(np.maximum.accumulate(equity)-equity)),daily_PF_ATR_R=metrics.pf(x))


def combine_stats(rows,dates):
    atr=metrics.stats(rows,dates)
    stop=metrics.stats([dict(t,atr=t['initial_risk'],net_R=t['net_stop_R']) for t in rows],dates)
    return dict(N=atr['N'],net_ATR_R=atr['net_R'],net_stop_R=stop['net_R'],net_points=atr['net_points'],
                gross_points=atr['points']['gross_total'],winrate=atr['points']['winrate'],PF_ATR_R=atr['trade_PF_R'],PF_stop_R=stop['trade_PF_R'],
                sharpe_ATR_R=atr['sharpe_daily_R'],sharpe_stop_R=stop['sharpe_daily_R'],
                max_marked_drawdown_ATR_R=atr['max_marked_drawdown_R'],max_marked_drawdown_stop_R=stop['max_marked_drawdown_R'],
                max_marked_drawdown_points=atr['max_marked_drawdown_points'],positive_quarters_ATR_R=atr['positive_quarters_R'],positive_quarters_stop_R=stop['positive_quarters_R'],
                traded_quarters=atr['traded_quarters'],cash_days=len(dates),quarterly=atr['quarterly'],
                direction={label:metrics.description([t for t in rows if t['direction']==side]) for label,side in (('LONG',1),('SHORT',-1))})


def report(result):
    lines=['# Causale ICT-verkenning — volledige ontwikkelingspool','',METHOD['status'],'',
      'Alle80 vooraf vastgelegde mechanische varianten; geen onafhankelijke validatie. StopR en ATR-R zijn verschillende noemers. De1.171 cashsessies bevatten1.151 ATR-ready instapsessies; overige dagen blijven nul in dagelijkse statistieken.','',
      'S1/S2 en alle bestanden van commit2ec3a07 blijven byte-identiek. De term ICT beschrijft de formele prijsactie-keten, geen bewijs van institutionele causaliteit.','',
      '## Volledige tabel — gevraagde touch-fillaanname','',
      '| Periode | Variant | N | Netto ATR-R | Netto stopR | Bruto pt | Netto pt | Win% | PF ATR | PF stop | Sharpe ATR | Sharpe stop | DD ATR | DD stop | DD pt | +kw ATR |',
      '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda v:'n/a' if v is None else f'{v:.3f}'
    def tables(fill):
        rows=[]
        for b in PERIODS:
            for name in NAMES:
                x=result['samples'][fill][b][name]
                rows.append('| '+b+' | '+name+' | '+str(x['N'])+' | '+' | '.join(fmt(x[k]) for k in ('net_ATR_R','net_stop_R','gross_points','net_points'))+' | '+fmt(None if x['winrate'] is None else x['winrate']*100)+' | '+' | '.join(fmt(x[k]) for k in ('PF_ATR_R','PF_stop_R','sharpe_ATR_R','sharpe_stop_R','max_marked_drawdown_ATR_R','max_marked_drawdown_stop_R','max_marked_drawdown_points'))+f" | {x['positive_quarters_ATR_R']}/{x['traded_quarters']} |")
        return rows
    lines+=tables('TOUCH')
    lines+=['','## Uitvoeringsgevoeligheid — limiet vereist één tick trade-through','','| Periode | Variant | N | Netto ATR-R | Netto stopR | Bruto pt | Netto pt | Win% | PF ATR | PF stop | Sharpe ATR | Sharpe stop | DD ATR | DD stop | DD pt | +kw ATR |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']+tables('TRADE_THROUGH')
    lines+=['','## Bevroren benchmarks','', '| Periode | Model | N | Netto ATR-R | Netto pt | PF ATR-R | Sharpe ATR-R | DD ATR-R |','|---|---|---:|---:|---:|---:|---:|---:|']
    for b in PERIODS:
        for name,x in result['benchmarks'][b].items():
            lines.append(f"| {b} | {name} | {x['N']} | {x['net_R']:.6f} | {x['net_points']:.3f} | {fmt(x['trade_PF_R'])} | {fmt(x['sharpe_daily_R'])} | {x['max_marked_drawdown_R']:.6f} |")
    lines+=['','## Onzekerheid en vergelijking met B','', '| Periode | Variant | 95%CI totaal ATR-R | p nul | Holm480 nul | 95%CI verschil met B | p verschil | Holm480 verschil |','|---|---|---|---:|---:|---|---:|---:|']
    for b in PERIODS:
        for name in NAMES:
            a=result['inference'][b][name]['ZERO'];c=result['inference'][b][name]['MINUS_B']
            ci=lambda r:'['+'; '.join(fmt(v) for v in r['total_ci95'])+']'
            lines.append(f"| {b} | {name} | {ci(a)} | {a['p_raw_two_sided']:.6f} | {a['p_holm480']:.6f} | {ci(c)} | {c['p_raw_two_sided']:.6f} | {c['p_holm480']:.6f} |")
    lines+=['','## Derde pijler — uitsluitend beschrijvende gelijke sleeves','',
      'Geen optimale weging of vervanging van B. 50% bevroren S1/S2 +50% ICT op ATR-R-schaal, inclusief evenredige frictie. Gelijktijdige posities toegestaan in gescheiden sleeves; dit is geen gehele-MNQ-simulatie. DD hieronder is uitsluitend cashdag-slot-DD, niet de minute-mark-DD hierboven.','',
      '| Periode | Variant | Basis | Dagcorrelatie | Overlaptrades | Basis Sharpe | 50/50 Sharpe | Basis dag-DD | 50/50 dag-DD | 50/50 netto ATR-R |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for b in PERIODS:
        for name in NAMES:
            for base,x in result['portfolio'][b][name].items():
                lines.append('| '+b+' | '+name+' | '+base+' | '+' | '.join(fmt(x[k]) for k in ('daily_correlation','overlap_trades','baseline_daily_sharpe','daily_sharpe','baseline_daily_close_drawdown_ATR_R','daily_close_drawdown_ATR_R','net_ATR_R'))+' |')
    lines+=['','## Kwartalen — primaire touchfill','', '| Periode | Variant | Kwartaal | N | Netto ATR-R | Netto pt |','|---|---|---|---:|---:|---:|']
    for b in PERIODS:
        for name in NAMES:
            for q in result['samples']['TOUCH'][b][name]['quarterly']:
                lines.append(f"| {b} | {name} | {q['quarter']} | {q['N']} | {q['net_R']:.6f} | {q['net_points']:.3f} |")
    lines+=['','## Dekking en informatie-afkniptests','', '```json',json.dumps(h.clean(result['coverage']),indent=2),'```','',f"Brondata-afknipcontroles: {result['future_cutoff_checks']}",'', '## Vaste methode en beperkingen','']
    lines += [f'- {k}: {v}' for k,v in METHOD.items()]
    lines += ['', 'Oorspronkelijke ICT-bronnen: [2022 Mentorship Episode3](https://www.youtube.com/watch?v=nQfHZ2DEJ8c), [FVG/MSS college](https://www.youtube.com/watch?v=Bkt8B3kLATQ). De concrete thresholds, uitvoeringsregels en selectie hierboven zijn onze expliciete operationalisering; de bronnen bewijzen de performance niet.','']
    return '\n'.join(lines)


def one_run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    models,cash,coverage,checks,sources,statuses=rebuild()
    allcash=sorted(d for days in cash.values() for d in days);result=dict(status=METHOD['status'],method=METHOD,catalog=[asdict(s) for s in SPECS],coverage=coverage,future_cutoff_checks=checks,source_verification=sources,samples={},benchmarks={},portfolio={})
    baseline={name:json.loads((benchmark.OUT/'run1'/(model+'-trades.json')).read_text()) for name,model in (('S1','S1_SELECTIVE'),('S2','S2_BROAD_NO_STOP'))}
    B=json.loads((benchmark.tp.OUT/'run1/B-trades.json').read_text())
    # Reuse verified frozen benchmark statistics; no benchmark signal or
    # execution is recalculated under new ICT rules.
    oldstats=json.loads(benchmark.RESULT.read_text())['samples']['OBSERVED_PATH']
    bresult=json.loads(benchmark.tp.RESULT.read_text())['portfolio']
    bpanels={};panels=[]
    for fill,rows in models.items():
        result['samples'][fill]={}
        for block in PERIODS:
            dates=allcash if block=='COMBINED' else cash[block]
            subset=lambda v:[t for t in v if block=='COMBINED' or t['block']==block]
            result['samples'][fill][block]={name:combine_stats(subset(rows[name]),dates) for name in NAMES}
            if fill=='TOUCH':
                matrix=np.column_stack([daily(subset(rows[name]),dates) for name in NAMES])
                if block!='COMBINED':panels.append((block,dates,matrix));bpanels[block]=daily(subset(B),dates)
                result['benchmarks'][block]=dict(B=bresult[block]['B'],S1=oldstats[block]['S1_SELECTIVE'],S2=oldstats[block]['S2_BROAD_NO_STOP'])
                result['portfolio'][block]={}
                for name in NAMES:
                    own=subset(rows[name]);values=daily(own,dates);result['portfolio'][block][name]={}
                    for base,ledger in baseline.items():
                        bs=subset(ledger);bv=daily(bs,dates);combined=daily_stats(.5*bv+.5*values);orig=daily_stats(bv)
                        corr=float(np.corrcoef(bv,values)[0,1]) if bv.std()>0 and values.std()>0 else None
                        starts=np.array([pd.Timestamp(t['entry_time']).value for t in bs]);ends=np.array([pd.Timestamp(t['exit_time']).value for t in bs])
                        overlap=sum(bool(np.any((starts<pd.Timestamp(t['exit_time']).value)&(ends>pd.Timestamp(t['entry_time']).value))) for t in own)
                        result['portfolio'][block][name][base]=dict(combined,daily_correlation=corr,overlap_trades=overlap,
                            baseline_daily_sharpe=orig['daily_sharpe'],baseline_daily_close_drawdown_ATR_R=orig['daily_close_drawdown_ATR_R'])
    result['inference'],result['bootstrap']=inference(panels,bpanels)
    h.dump(directory/'summary.json',result);h.dump(directory/'status-counts.json',statuses)
    h.dump(directory/'orders-and-ledgers.json',{fill:{name:benchmark.tp.clean_ledger(v) for name,v in rows.items()} for fill,rows in models.items()})
    for fill,rows in models.items():
        h.dump(directory/(fill+'-daily-panels.json'),{block:dict(dates=days,models=NAMES,net_ATR_R=np.column_stack([daily([t for t in rows[name] if t['block']==block],days) for name in NAMES]).tolist()) for block,days in cash.items()})
    (directory/'report.md').write_text(report(result))
    scalars=['N','net_ATR_R','net_stop_R','gross_points','net_points','winrate','PF_ATR_R','PF_stop_R','sharpe_ATR_R','sharpe_stop_R','max_marked_drawdown_ATR_R','max_marked_drawdown_stop_R','max_marked_drawdown_points','positive_quarters_ATR_R','positive_quarters_stop_R','traded_quarters','cash_days']
    with (directory/'performance.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['fill','period','model']+scalars);writer.writeheader()
        for fill in models:
            for b in PERIODS:
                for name in NAMES:writer.writerow(dict(fill=fill,period=b,model=name,**{k:result['samples'][fill][b][name][k] for k in scalars}))
    verify();return result


def replay():
    if PROOF.exists():return verify()
    x=one_run(OUT/'run1');print('ICT run1 complete; independently rebuilding raw sources',flush=True)
    one_run(OUT/'run2')
    hashes=lambda d:{p.name:h.sha(p) for p in d.iterdir() if p.is_file()}
    a,b=hashes(OUT/'run1'),hashes(OUT/'run2');assert a==b,'Independent ICT replay differs'
    h.dump(RESULT,x);REPORT.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,REPORT]+[folder/name for folder in (OUT/'run1',OUT/'run2') for name in a]
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_ICT_SOURCE_REPLAYS',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(status='COMPLETE',variants=len(SPECS),inference_tests=480,future_cutoff_checks=x['future_cutoff_checks'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('register','replay','verify'))
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
