"""python -m scripts.prop_firm register|replay|verify. Append-only prop feasibility."""
import argparse
import csv
import json
import subprocess
import numpy as np
import pandas as pd

from scripts.judas_replacement import __main__ as prior
from scripts.judas_replacement.core import split_baseline
from scripts.ict_study import __main__ as ict
from scripts.ict_study import core as signals
from scripts.oos_preparation.year import load_registered
from scripts.two_pillar import core as metrics
from .core import globex_entry,flat_window_violation,adverse_gross,dollar_panel,account_check

h=prior.h;ROOT=prior.ROOT
OUT=ROOT/'artifacts/prop-firm';LOCK=ROOT/'research/prop-firm-lock.json'
RESULT=ROOT/'research/prop-firm-results.json';PROOF=ROOT/'research/prop-firm-verification.json'
REPORT=ROOT/'docs/PROP_FIRM_FEASIBILITY_REPORT.md'
RULES=ROOT/'research/prop-firm-rules-2026-10-25.json'
PERIODS=('2019_2021','2024_2026','COMBINED')
JUDAS={'J0830':'ICT3_5m_BOTH_OPEN0830_JUDAS_2R','JBULL0930':'ICT3_5m_BULL_LONG_OPEN0930_JUDAS_2R'}
METHOD=dict(date='2026-10-25',status='RETROSPECTIVE_FEASIBILITY_NOT_ACCOUNT_OR_PROFITABILITY_CERTIFICATION',
 selection='Original frozen A102 selective and A735 bull cohorts unchanged; same preknown contract and signalday priorATR. Two existing strict Judas specs only. No new thresholds or exits searched. All1171cashdays retained. Original16 variants rebuilt exactly; add18 variants independently of16exit/PnL.',
 entry18='Choose18NY on civil day immediately preceding the planned next actualcash09:30 exit. Friday signal->Sunday18->Monday09:30; holiday-gap signal->lastGlobex18 before nextcash. This is a deliberate calendar-timing variant known before entry, not Friday18(venueclosed), not a multi-futuresday hold across another16:10flat window. Strongday/SMA signal remains latestcash signal, explicitly stale across closedcashdays. Exact18bar and next09:30open required in SAME held contract; no first-available fill or replacement contract by future coverage.',
 stops='For selective A, rebuild fixed0.50signaldayATR stop relative to actual18entry, rounded towardentry. Broad A remains NOstop. Frozen targets and strict entry trade-through of Judas unchanged; flat15:55 or earlier sourcecalendar restriction. Both windows andDST handled inAmerica/New_York. No18position may cross a weekday16:10-18flat window.',
 performance='NQ comparison keeps1.225point($24.50)RT per trade and originalATR normalization. Portfolio variants S1-J0830,S1-JBULL0930,S2-J0830; also S2-JBULL0930 as requested sizing sensitivity. Full size, no50/50. MarkDD original minuteopen/close method; zerooverlap verified.',
 mnq='Separate fixed1,2,3MNQ scenarios: grossNQpoints*2USD*quantity minus explicitMNQcost*quantity; NEVER divide24.50 by10. Costs3.22,6.50,9.50USD/RT;3.22 is currentTopstep1.22fees+assumed2slippage, MFFU6.50 provisionalnotquote. SyntheticMNQ-equivalent on NQbars, including data beforeMNQlaunch; no MNQfill evidence.',
 risk='Current2026 official EOD profiles, retrospectively applied. Floor starts-D, ratchets only atEOD max(previous,min(lock,EODpeak-D)), neverdown. Intraday unrealized losses checked against unchangedcurrentfloor. Account activated firstcashday EACHera, no priorprofitcarried across2021--2024gap. Combinedmetrics are bookkeeping only, not onecontinuousaccount.',
 uncertainty='Observedminuteopen/close losses and conservative adverseOHLCbound reported separately. ExitOPEN excludeslaterlow/high; STOP exit never includespoststoplow; TARGET adverseextreme may be afterexit and is labeledpotential. Missingovernightminutes/stopidentity limits retained; no forwardfill. Floor touch conservatively treated as trigger. No observedbreach is NOT certified survival.',
 rules='MFFURapidEOD30%eval only50K;100KusesRapidEval50%, not nonexistentRapidEOD100K. Buildernoevalconsistency,50%payout; TopstepTC55% current. DLL is softpause, notaccountbreach. Recordfirsttrigger and stopclaimingunmodifiedpathvalid afterit; no fabricatedliquidation or optimizedriskoverlay. SimFundedRapidEODnewsfilter notverified ->unconfirmed. Seven-calendarday inactivitydiagnostic recorded; no invented extra trades to resettimer.',
 consistency='Prefix bestday/totalnetprofit, notfractionofgrosswinnings orlargesttrade. Nonpositiveprofit=>ratio undefined.30%too-high is extendedtarget, NOTbreach. FirstprofitTarget+consistency+minimumactivedays reported only if beforeMLL/DLL/inactivitygates. No payouts,withdrawals,monthlyfees,accountresets orfundedscaling simulated. Fullperiod ratios not a payoutcycle certificate.',
 publication='Preserve all prior filesbyte-identical, including baselineplaybook. Add versioned playbookV3 with newguide appendix, appendnewdashboardroutes and ruleprofiles. Two fresh rawsource reconstructions; byte-identical numericaloutputs; code/sources/rules fixed before outcomes. No purchases/accounts/orders, publicaggregates only.')


def verify():
    prior.verify();lock=json.loads(LOCK.read_text())
    if lock['method']!=METHOD:raise ValueError('Prop method changed')
    for n,d in lock['files'].items():
        if h.sha(ROOT/n)!=d:raise ValueError('Protected file changed '+n)
    if PROOF.exists():
        for n,d in json.loads(PROOF.read_text())['files'].items():
            if h.sha(ROOT/n)!=d:raise ValueError('Prop output changed '+n)
    return dict(status='BASELINE_ICT_REPLACEMENT_AND_RULES_VERIFIED',protected=len(lock['files']))


def register():
    if LOCK.exists():return verify()
    prior.verify();names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    h.dump(LOCK,dict(method=METHOD,files={n:h.sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}))
    return dict(status='PROP_TIMING_RULES_AND_COST_SCENARIOS_LOCKED')


def load_inputs():
    data,sources=prior.base.tp.pv.inputs();cash={b:h.cash_dates(min(d['dates']),max(d['dates'])) for b,d in data.items()}
    fullold=pd.read_parquet(h.OUT/'contract-bars.parquet');fullrecent,_,_=load_registered(ROOT)
    full={'2019_2021':{c:g.sort_index() for c,g in fullold.groupby('contract')},'2024_2026':{c:g.sort_index() for c,g in fullrecent.groupby('contract')}}
    return data,cash,full,sources


def overnight(old,frame,calendar,phase):
    signalday,nextday=old['day'],old['exit_day'];start=h.at(signalday,'16:00') if phase=='16' else globex_entry(signalday,nextday)
    end=h.at(nextday,'09:30');rows=frame.loc[start:end]
    if start not in rows.index or end not in rows.index:return None,'MISSING_EXACT_ENDPOINT'
    if 'usable' in rows and not rows.usable.all():return None,'INVALID_SOURCE_BAR'
    if rows.contract.nunique()!=1 or not rows.index.is_unique:raise ValueError('Mixedcontract overnight')
    expected=[]
    first=start.tz_convert('America/New_York').strftime('%Y-%m-%d')
    for d in pd.bdate_range(first,nextday).strftime('%Y-%m-%d'):expected.extend(calendar.grid(d))
    expected=pd.DatetimeIndex(expected);expected=expected[(expected>=start)&(expected<end)]
    if start not in expected:raise ValueError('Entry outside reviewed exchange calendar')
    p={k:rows[k].to_numpy(float) for k in signals.FIELDS};missing=expected.difference(rows.index)
    t=metrics.night(signalday,nextday,rows.index,p,old['atr'],missing,catastrophe=old['stop_price'] is not None)
    t=dict(old,**t,direction=1,exit_at_open=t['reason']!='STOP',entry_phase=phase)
    t['adverse_gross_points']=adverse_gross(t,rows.index,p)
    return t,'FILLED'


def rebuild():
    data,cash,full,sources=load_inputs();Js={k:[] for k in JUDAS}
    for b,d in data.items():
        d['groups']=dict(tuple(d['active'].groupby('trade_date')))
        for day in d['dates']:
            p,ctx=ict.day_input(d,day)
            for label,name in JUDAS.items():
                spec=next(s for s in ict.SPECS if s.name==name);order=signals.signal(p,ctx,spec);t,_=signals.execute(p,order,touch=False)
                if not t:continue
                start=h.at(day,'09:30')+pd.Timedelta(minutes=t['entry_bar']);end=h.at(day,'09:30')+pd.Timedelta(minutes=t['exit_bar'])
                t=metrics.enrich(dict(t,day=day,exit_day=day,block=b,entry_time=start.isoformat(),exit_time=end.isoformat()),ctx['atr'])
                ix=pd.date_range(h.at(day,'08:00'),h.at(day,'16:00'),freq='min',inclusive='left')
                t['adverse_gross_points']=adverse_gross(t,ix,p);Js[label].append(t)
    stored=json.loads((ict.OUT/'run1/orders-and-ledgers.json').read_text())['TRADE_THROUGH']
    for label,name in JUDAS.items():prior.assert_ledger(Js[label],stored[name],('entry_price','exit_price','net_points','net_R','net_stop_R'))
    B=json.loads((prior.base.tp.OUT/'run1/B-trades.json').read_text());A={};coverage={}
    for model,filename in [('S1','S1_SELECTIVE'),('S2','S2_BROAD_NO_STOP')]:
        old=split_baseline(json.loads((prior.base.OUT/'run1'/f'{filename}-trades.json').read_text()),B)
        A[model]={phase:[] for phase in ('16','18')};counts={b:dict(intended=0,known18=0,missing18=0,deferred_calendar_entries=0,incomplete18=0,unidentified_stop18=0) for b in cash};unscored=[]
        for t in old:
            b=t['block'];counts[b]['intended']+=1
            assert h.at(h.expiry(t['contract']),'09:30')>h.at(t['exit_day'],'09:30')
            for phase in ('16','18'):
                new,code=overnight(t,full[b][t['contract']],data[b]['calendar'],phase)
                if new is None:
                    assert phase=='18';counts[b]['missing18']+=1;unscored.append(dict(day=t['day'],exit_day=t['exit_day'],block=b,code=code));continue
                A[model][phase].append(new)
                if phase=='18':
                    counts[b]['known18']+=1;counts[b]['incomplete18']+=not new['complete_holding_path'];counts[b]['unidentified_stop18']+=not new['stop_path_identified'] if model=='S1' else 0
                    counts[b]['deferred_calendar_entries']+=pd.Timestamp(new['entry_time']).tz_convert('America/New_York').strftime('%Y-%m-%d')!=t['day']
                    assert not flat_window_violation(new),'18variant crosses propflatwindow'
        prior.assert_ledger(A[model]['16'],old,('entry_price','exit_price','net_points','net_R','mae_R'))
        coverage[model]=dict(by_era=counts,unscored18=unscored,actual16_positions_crossing_flat_window=sum(flat_window_violation(t) for t in A[model]['16']))
    models={}
    for phase in ('16','18'):
        for base in A:
            models[f'A_{base}_{phase}']=A[base][phase]
            for label in Js:models[f'{base}_{label}_{phase}']=A[base][phase]+Js[label]
    for name,rows in models.items():
        if '_18' in name:assert not any(flat_window_violation(t) for t in rows)
    return models,cash,sources,coverage


def report(x):
    lines=['# Prop-firmvenster en MNQ-haalbaarheid','',METHOD['status'],'',
      'Referentie2ec3a07 en alle ICT/Judas-rapporten blijven ongewijzigd. Deze proef past actuele2026regels toe op historischeNQ-bars, met afzonderlijke eigenbroker16:00- en propvenster18:00-uitvoering. Geen gekochte accounts en geen uitvoeringscertificaat.','',
      '## NQ-vergelijking, kosten24,50USD perroundtrip','',
      '| Periode | Model | N | Netto ATR-R | Netto pt | PF ATR | Sharpe | Mark-DD ATR | Mark-DD pt | +kalenderkwartalen |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    f=lambda v:'n.v.t.' if v is None else f'{v:.6f}'
    for b in PERIODS:
        for m,r in x['performance'][b].items():
            lines.append(f"| {b} | {m} | {r['N']} | {r['net_R']:.6f} | {r['net_points']:.3f} | {f(r['trade_PF_R'])} | {f(r['sharpe_daily_R'])} | {r['max_marked_drawdown_R']:.6f} | {r['max_marked_drawdown_points']:.3f} | {r['positive_quarters_R']}/{len(r['quarterly'])} |")
    lines+=['','## Dollarstress1–3MNQ: vaste hoeveelheden, aparteMNQ-kosten','',
      'Gecombineerde boekhouding is geen continue propaccount. De accountvloer wordt per tijdperk opnieuw gestart. RT3,22USD gebruikt de gepubliceerde Topstep1,22USD-fees plus aangenomen2USDslippage;6,50en9,50USD zijn vaste kostenstress, geen bevestigdeMFFUquote.','',
      '| Periode | Model18 | MNQ | RT$/contract | Netto$ | Mark-DD$ | EOD-DD$ | Ergste intradayverlies$ | Grootste winstdag$ |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in x['dollar_stress']:
        lines.append(f"| {r['period']} | {r['model']} | {r['MNQ_quantity']} | {r['assumed_RT_cost_per_contract']:.2f} | {r['net_USD']:.3f} | {r['marked_drawdown_USD']:.3f} | {r['EOD_close_drawdown_USD']:.3f} | {r['worst_session_adverse_USD']:.3f} | {r['largest_profit_day_USD']:.3f} |")
    lines+=['','## Accountcontroles — uitsluitend de twee echte tijdperken','',
      'Alle scenario’s staan in PROP_ACCOUNT_CHECKS.csv. EersteDLL-hit betekent gewijzigde uitvoering nodig; latere ongewijzigde schaduw-PnL is geen werkelijk accountpad. MLL-floor wordt dagelijks geratcheted, maar intraday met openverlies bewaakt. Een ongunstige OHLC-extreem kan bij target-exit na de fill liggen: potentieel versus observeerbaar wordt apart gehouden. Geen universele prop-goedkeuring.','',
      '| Periode | Model | MNQ | RT$ | Profiel | Status | Eerste MLL | DLL | Inactiviteit | Target+consistency vóór risico | Eind30%ratio |','|---|---|---:|---:|---|---|---|---|---|---|---:|']
    for r in x['account_checks']:
        if r['cost'] not in (3.22,6.5):continue
        lines.append(f"| {r['period']} | {r['model']} | {r['quantity']} | {r['cost']} | {r['profile']} | {r['risk_status']} | {r['first_potential_MLL']} | {r['first_DLL_soft_pause']} | {r['inactivity_first_diagnostic']} | {r['evaluation_ready_before_risk_trigger']} | {f(r['best_day_fraction_of_net'])} |")
    lines+=['','## Bronkwaliteit en kalender','', '```json',json.dumps(h.clean(dict(coverage=x['coverage'],paired_same_cohort=x['paired_timing'])),indent=2),'```','',
      'Ontbrekende18:00-prijzen zijn niet stilzwijgend vervangen of alsnulwinst geïmputeerd. Unscoredcohorten staan expliciet hierboven. Een tijdvenster dat past, bewijst geen naleving van nieuws-/inactiviteits-/persoonlijke contractregels.','',
      '## Vaste methode','']+[f'- {k}: {v}' for k,v in METHOD.items()]
    lines+=['','## Officiële bronnen, gecontroleerd25oktober2026','']+[f'- [{k}]({v})' for k,v in x['rules']['sources'].items()]
    return '\n'.join(lines)+'\n'


def one_run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    models,cash,sources,coverage=rebuild();rules=json.loads(RULES.read_text());performance={};dollars=[];accounts=[];private={}
    allcash=sorted(d for ds in cash.values() for d in ds)
    for b in PERIODS:
        dates=allcash if b=='COMBINED' else cash[b];subset={m:[t for t in rows if b=='COMBINED' or t['block']==b] for m,rows in models.items()}
        performance[b]={m:metrics.stats(rows,dates) for m,rows in subset.items()}
        for m,rows in subset.items():
            if not m.endswith('_18') or m.startswith('A_'):continue
            for q in (1,2,3):
                for cost in rules['costs_usd_per_MNQ_roundtrip']:
                    days,stats=dollar_panel(rows,dates,cost,q);dollars.append(dict(stats,period=b,model=m))
                    private[f'{b}_{m}_{q}_{cost}']=days
                    if b!='COMBINED':
                        for profile in rules['profiles']:
                            accounts.append(dict(account_check(days,profile),period=b,model=m,cost=cost,quantity=q))
    frozen=json.loads(prior.RESULT.read_text())['performance']
    for b in PERIODS:
        for m,previous in [('S1_J0830_16','S1_JUDAS'),('S2_J0830_16','S2_JUDAS')]:
            for k in ('N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R','max_marked_drawdown_points'):
                np.testing.assert_allclose(performance[b][m][k],frozen[b][previous][k],atol=1e-8,rtol=0)
    paired={}
    for b in PERIODS:
        dates=allcash if b=='COMBINED' else cash[b];paired[b]={}
        for a in ('S1','S2'):
            k=lambda t:(t['block'],t['day'],t['exit_day'])
            new=[t for t in models['A_'+a+'_18'] if b=='COMBINED' or t['block']==b];known={k(t) for t in new}
            old=[t for t in models['A_'+a+'_16'] if k(t) in known]
            oldstats=metrics.stats(old,dates);newstats=metrics.stats(new,dates)
            paired[b][a]=dict(N=len(new),net_R_16_common=oldstats['net_R'],net_R_18=newstats['net_R'],net_points_16_common=oldstats['net_points'],net_points_18=newstats['net_points'],delta_net_R=newstats['net_R']-oldstats['net_R'],delta_points=newstats['net_points']-oldstats['net_points'])
    result=dict(paired_timing=paired,status=METHOD['status'],method=METHOD,rules=rules,performance=performance,dollar_stress=dollars,account_checks=accounts,coverage=coverage,source_verification=sources)
    h.dump(directory/'summary.json',result);h.dump(directory/'daily-dollar-panels.json',private)
    h.dump(directory/'ledgers.json',{m:[{k:v for k,v in t.items() if k!='path_points'} for t in rows] for m,rows in models.items()})
    (directory/'report.md').write_text(report(result))
    with (directory/'portfolio-performance.csv').open('w',newline='') as f:
        keys=['N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R','max_marked_drawdown_points','positive_quarters_R'];w=csv.DictWriter(f,fieldnames=['period','model']+keys+['calendar_quarters']);w.writeheader()
        for b,rows in performance.items():
            for m,r in rows.items():w.writerow(dict(period=b,model=m,**{k:r[k] for k in keys},calendar_quarters=len(r['quarterly'])))
    for filename,rows in [('mnq-stress.csv',dollars),('account-checks.csv',accounts)]:
        with (directory/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    verify();return result


def replay():
    if PROOF.exists():return verify()
    result=one_run(OUT/'run1');print('Prop run1 complete; independently rebuilding sources',flush=True);one_run(OUT/'run2')
    hashes=lambda d:{p.name:h.sha(p) for p in d.iterdir() if p.is_file()}
    a,b=hashes(OUT/'run1'),hashes(OUT/'run2');assert a==b,'Propreplay differs'
    h.dump(RESULT,result);REPORT.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,REPORT]+[folder/n for folder in (OUT/'run1',OUT/'run2') for n in a]
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_PROP_FIRM_REPLAYS',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(status='COMPLETE',accounts=len(result['account_checks']),MNQ_stress_rows=len(result['dollar_stress']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('register','replay','verify'));print(json.dumps(globals()[parser.parse_args().action](),indent=2))
