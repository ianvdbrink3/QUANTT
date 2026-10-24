"""Explicitly released one-time historical replication and independent replay.

python -m scripts.historical_validation register|replay|verify
No changes to frozen signal, fill, calendar-v2 or preparation code.
"""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import historical_calendar_v2 as v
from scripts import prepare_historical_contracts as h
from scripts.edge_marathon.core import select,fill
from .analysis import MODELS,SEED,REPS,summarize,intervals,apply_inference,decision

ROOT=h.ROOT
RELEASE=ROOT/'research/historical-validation-release.json'
LOCK=ROOT/'research/historical-validation-lock.json'
RESULT=ROOT/'research/historical-validation-results.json'
VERIFY=ROOT/'research/historical-validation-verification.json'
PUBLIC=ROOT/'public/data/historical-validation.json'
REPORT=ROOT/'docs/HISTORICAL_VALIDATION_2019_2021.md'
PUBLIC_REPORT=ROOT/'public/reports/HISTORICAL_VALIDATION_2019_2021.md'
OUT=ROOT/'artifacts/historical-validation'
START,END='2019-01-14','2021-12-31'
VARIANTS=('PRIMARY_STRICT','SECONDARY_AVAILABLE')


def fingerprint(value):
    return hashlib.sha256(json.dumps(h.clean(value),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def masks(rows,provisional):
    available=[r['day'] for r in rows if START<=r['day']<=END and r['TOM_RTH']]
    return dict(PRIMARY_STRICT=[d for d in available if d not in provisional],SECONDARY_AVAILABLE=available)


def make_release():
    quality=json.loads(v.RESULT.read_text())
    technical=json.loads((v.OUT/'technical-days.json').read_text())
    dates=masks(technical,set(quality['remaining_provisional_dates']))
    common=[d for d in h.cash_dates(START,END) if d not in dates['SECONDARY_AVAILABLE']]
    return dict(id='HISTORICAL-THREE-SURVIVORS-RELEASE-20261024',date='2026-10-24',released=True,
        human_authorization='Explicit user release on 24 October 2026: accept documented source limitations; strict and inclusive sensitivity; execute three frozen models plus equal third and publish after completion.',
        accepted_limits=quality['remaining_blockers'],start=START,end=END,
        previously_inspected_dates_excluded=json.loads((ROOT/'research/three-survivors-preregistration-2019-2021.json').read_text())['previously_inspected_dates'],
        models=list(MODELS),provisional_dates=quality['remaining_provisional_dates'],
        rules='Unchanged edge_marathon.core.select/fill. ToM official month positions; compression strict prior range <0.65 ATR, first5m confirm/next open; sweep first30m exactly one side/reversal,10:00open to11:59close. No stops, targets, delay search or additional filters.',
        costs=dict(roundtrip_USD=24.5,NQ_point_value_USD=20.,points=1.225,
            note='Fixed total NQ roundtrip friction, not an extra fee on top. Equal-third sleeves pay proportional full component friction; no netting discount.'),
        normalization='net_points / prior-known ATR14. Equal third of each model, including idle sleeves. No compounding; ATR is not a stop or loss cap.',
        primary='Only strict variant can support a formal conclusion. Exclude provisional dates and normal sessions lacking any full-RTH minute or09:29 anchor; require prior positive ATR. Model-specific PD/overnight availability remains required.',
        secondary='Same fixed rules and same calendar-v2 context history, including available provisional dates ONLY if already technically eligible. Never fill missing prices, force short sessions into full-RTH models, or relax anchors. Descriptive sensitivity, cannot rescue primary failure.',
        history='Exclusion applies to evaluation membership, not deletion of warmup/indicator history. Same corrected calendar and 13 frozen rollovers/spreads for both variants. This sensitivity cannot establish independence from provisional historical context.',
        inference=dict(seed=SEED,reps=REPS,block_months=2,method='Joint moving blocks of consecutive calendar months, exactly frozen survivor bootstrap; daily zero positions retained on every eligible common evaluation day.',
            tests='Four co-primary two-sided mean daily netATR tests, alpha0.05, Holm4. Raw-point tests and secondary variant descriptive; no second chance. Also report reserved projectwide Holm6 with the two unexecuted afternoon tests assigned p=1.',
            intervals='Nominal95% percentile mean/total and Sharpe intervals; separate Bonferroni4 simultaneous95% mean intervals (98.75% marginal), approximate bootstrap coverage.',
            gate='At least24 usable months and30 ATR-ready trades per signal; combination requires all three. Positive total netATR and Holm4 p<0.05 -> STATISTICAL_SUPPORT_ON_REGISTERED_REMAINDER, else NO_STATISTICAL_SUPPORT; below floor INCONCLUSIVE. Never live-trading approval.'),
        daily_universe='Each variant common full-RTH/priorATR calendar. No position is zero, not a fabricated trade. A model without PD or full-night context remains idle, with availability separately counted.',
        metric_units='Standalone PF and winrate on active daily net P&L (at most1trade/day). Portfolio PF/winrate on aggregated active days, not on component legs. Portfolio trade count counts component executions; raw points are theoretical equal-third contract points.',
        planned_evaluation_days={key:len(value) for key,value in dates.items()},
        planned_day_list_sha256={key:fingerprint(value) for key,value in dates.items()},
        planned_technical_days={variant:{m:sum(next(r for r in technical if r['day']==d)[m] for d in ds) for m in MODELS[:3]} for variant,ds in dates.items()},
        excluded_cash_session_dates=common,
        provisional_dates_already_outside_full_RTH_test=[d for d in quality['remaining_provisional_dates'] if d not in dates['SECONDARY_AVAILABLE']],
        interim_outcomes=False,parameter_search=False,afternoon_hypotheses_executed=False,
        publication='After both runs, tests and build: GitHub main and existing Vercel quantt production. No private CSV, context/daily/trade arrays or source images uploaded.')


def verify():
    lock=json.loads(LOCK.read_text())
    v.check_hashes({**lock['protected_files'],**lock['private_inputs'],**lock['method_files']})
    prior=v.verify()
    release=json.loads(RELEASE.read_text())
    if not release['released'] or release['models']!=list(MODELS):raise PermissionError('No matching outcome release')
    if release['inference']['seed']!=SEED or release['inference']['reps']!=REPS:raise ValueError('Inference changed')
    if VERIFY.exists():
        proof=json.loads(VERIFY.read_text())
        for side in ('first','second'):v.check_hashes(proof[side])
        v.check_hashes(proof['published_files'])
    return dict(prior=prior,protected_before_release=len(lock['protected_files']),
        private_inputs=len(lock['private_inputs']),method_files=len(lock['method_files']),released=True)


def register():
    if LOCK.exists():return verify()
    v.verify()
    if RELEASE.exists():raise ValueError('Inspect partial release before replacing it')
    # This registration reads technical availability only; no strategy call.
    h.dump(RELEASE,make_release())
    package=Path(__file__).parent
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    own=lambda n:n.startswith(('scripts/historical_validation/','tests/test_historical_validation','app/research/historical-validation/')) or n.startswith('research/historical-validation-')
    protected={n:h.sha(ROOT/n) for n in names if n and not own(n) and (ROOT/n).is_file()}
    private={str(p.relative_to(ROOT)):h.sha(p) for folder in (h.OUT,v.OUT) for p in folder.glob('*') if p.is_file()}
    methods={str(p.relative_to(ROOT)):h.sha(p) for p in package.glob('*.py')}
    methods[str(RELEASE.relative_to(ROOT))]=h.sha(RELEASE)
    prereg=json.loads((ROOT/'research/three-survivors-preregistration-2019-2021.json').read_text())
    v.check_hashes(prereg['source_code_sha256'])
    h.dump(LOCK,dict(anchor_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        protected_files=protected,private_inputs=private,method_files=methods,
        source_register_sha256=h.sha(h.REGISTER),calendar_v2_lock_sha256=h.sha(v.LOCK),
        status='RELEASE_AND_METHOD_RECORDED_BEFORE_FIRST_NEW_SIGNAL'))
    return verify()


def write_csv(path,rows):
    if not rows:raise ValueError('Empty export is unexpected')
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def inputs():
    manifest=json.loads(h.REGISTER.read_text());parts=[]
    for item in manifest['files']:
        frame,_=h.read_source(item);parts.append(frame)
    full,duplicates=h.reconcile(parts);del parts
    if duplicates['conflicting_keys']:raise ValueError('Conflicting source bars')
    pd.testing.assert_frame_equal(full,pd.read_parquet(h.OUT/'contract-bars.parquet'))
    baseline=json.loads(h.RESULT.read_text());contracts=list(dict.fromkeys(r['contract'] for r in json.loads((ROOT/'research/afternoon-historical-download-plan.json').read_text())['rows']))
    schedule,observed,failure=h.roll_route(full,contracts,h.HistoricalCalendar())
    if failure or observed!=baseline['rollovers']:raise ValueError('Frozen volume route changed')
    active=h.select_active(full,schedule)
    active=active[active.trade_date.between('2018-11-19',END)]
    pd.testing.assert_frame_equal(active,pd.read_parquet(h.OUT/'active-bars.parquet'))
    spreads=h.roll_spreads(full[full.usable],schedule)
    normalized=[{k:(value.isoformat() if isinstance(value,pd.Timestamp) else value) for k,value in row.items()} for row in spreads]
    if normalized!=json.loads((v.OUT/'fixed-spreads.json').read_text()):raise ValueError('Frozen spreads changed')
    calendar=v.CalendarV2()
    days,state,context,technical,changed,groups=v.technical_context(active,spreads,calendar)
    if h.clean(context)!=json.loads((v.OUT/'prior-context.json').read_text()):raise ValueError('Calendar-v2 context parity failed')
    release=json.loads(RELEASE.read_text());dates=masks(technical,set(release['provisional_dates']))
    for variant,value in dates.items():
        if fingerprint(value)!=release['planned_day_list_sha256'][variant]:raise ValueError('Pre-outcome day mask changed')
    source=dict(source_files=len(manifest['files']),reconciliation=duplicates,raw_and_cached_exact=True,
        active_raw_prices_unchanged=True,rollover_count=len(observed),rollover_records_exact=True,
        spread_records_exact=True,calendar_v2_context_exact=True,source_register_sha256=h.sha(h.REGISTER))
    return state,dates,{r['day']:r for r in technical},source,context,active


def generate(day,prices,ctx,technical):
    # Eligibility is locked from complete bars; the selector itself sees only
    # causal confirming prefixes. Future bar poisoning tested synthetically.
    for field in ('open','high','low','close','volume'):
        if len(prices[field])!=390 or not np.isfinite(prices[field]).all():raise ValueError('Invalid full RTH input')
    context=dict(ctx,**h.cash_context(day))
    if not technical['TOM_RTH']:raise ValueError('No full-RTH/priorATR eligibility')
    events=[e for e in select(prices,context) if e['model'] in MODELS[:3] and technical[e['model']]]
    for event in events:
        # ToM is calendar-defined, before current open. The frozen selector
        # needs its first bar only to emit its existing event representation.
        boundary=max(1,event['decision'])
        prefix={k:values[:boundary] for k,values in prices.items()}
        if event not in select(prefix,context):raise AssertionError('Noncausal signal '+day)
        if event['entry']<event['decision']:raise AssertionError('Entry before decision')
    if len({e['model'] for e in events})!=len(events):raise ValueError('More than one event/model/day')
    return [dict(fill(event,prices,context),day=day) for event in events]


def one_run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    state,dates,technical,source,context,active=inputs()
    print('Source replay, frozen rolls, calendar-v2 context and pre-outcome masks verified',flush=True)
    union=sorted(set().union(*map(set,dates.values())));byday={}
    for day in union:
        byday[day]=generate(day,*state[day],technical[day])
        for trade in byday[day]:
            contracts=active[active.trade_date.eq(day)].contract.unique()
            if len(contracts)!=1:raise ValueError('Mixed contracts within an evaluation day')
            trade['contract']=str(contracts[0])
            trade['quarter']=str(pd.Period(day,freq='Q'))
    results={};matrices=[];ledgers=[];daily=[];quarters=[]
    for variant in VARIANTS:
        r,p,a,ledger,rows,q=summarize(dates[variant],byday,state,technical,variant)
        results[variant]=r;matrices.extend([p,a]);ledgers+=ledger;daily+=rows;quarters+=q
    # Registered masks are identical before any outcomes; do not align by
    # post-outcome trade membership. Future extensions must retain joint dates.
    if dates[VARIANTS[0]]!=dates[VARIANTS[1]]:raise ValueError('Different date masks require pre-outcome joint-month bookkeeping')
    estimates=intervals(dates[VARIANTS[0]],np.column_stack(matrices))
    apply_inference(results,estimates)
    months=len({d[:7] for d in dates[VARIANTS[0]]})
    counts=[results[VARIANTS[0]][m]['atr']['component_trades'] for m in MODELS[:3]]
    for model in MODELS:
        row=results[VARIANTS[0]][model]
        cs=counts if model==MODELS[-1] else [row['atr']['component_trades']]
        row['formal_status']=decision(row['atr'],cs,months)
        row['projectwide_reserved_Holm6_status']=decision(row['atr'],cs,months,True)
        results[VARIANTS[1]][model]['formal_status']='DESCRIPTIVE_SENSITIVITY_ONLY'
    differences={model:{'net_points':results[VARIANTS[1]][model]['points']['total']-results[VARIANTS[0]][model]['points']['total'],
        'net_atr':results[VARIANTS[1]][model]['atr']['total']-results[VARIANTS[0]][model]['atr']['total'],
        'component_trades':results[VARIANTS[1]][model]['atr']['component_trades']-results[VARIANTS[0]][model]['atr']['component_trades']} for model in MODELS}
    value=dict(status='REGISTERED_HISTORICAL_REPLICATION_COMPLETED_WITH_ACCEPTED_SOURCE_LIMITS',date='2026-10-24',
        release_sha256=h.sha(RELEASE),method_lock_sha256=h.sha(LOCK),window=[START,END],
        previous_8_january_days_excluded=True,variants=results,quarterly=quarters,
        evaluation_days={k:len(ds) for k,ds in dates.items()},usable_months=months,
        technical_days=json.loads(RELEASE.read_text())['planned_technical_days'],
        sensitivity_difference=differences,source_verification=source,
        inference=json.loads(RELEASE.read_text())['inference'],costs=json.loads(RELEASE.read_text())['costs'],
        accepted_limits=json.loads(RELEASE.read_text())['accepted_limits'],
        interpretation='Historical replication under accepted source limitations, not prospective or independent-vendor/tick certification. No claim of proven future profitability.',
        sensitivity_interpretation='All nine provisional dates already fail full-RTH evaluation or are outside the test window. Both variants keep identical indicator history; zero difference is not proof that provisional history has no indirect effect.',
        metrics=json.loads(RELEASE.read_text())['metric_units'],
        no_optimization=True,signals_computed=True,holdout_executed=True,raw_data_public=False,
        afternoon_tests_executed=False,publication_requested=True)
    h.dump(directory/'summary.json',value)
    h.dump(directory/'prior-context.json',context)
    h.dump(directory/'source-verification.json',source)
    write_csv(directory/'trades.csv',ledgers);write_csv(directory/'daily.csv',daily);write_csv(directory/'quarterly.csv',quarters)
    (directory/'report.md').write_text(report(value))
    verify()
    return value


def report(r):
    names=dict(TOM_RTH='Maandwisseling',COMPRESSED_BREAK5='Compressie-uitbraak',SWEEP_REV_1200='Vroege sweep tot12:00',PORTFOLIO_EQUAL_THIRD='Gelijke1/3-combinatie')
    def f(x,d=3):return 'n.v.t.' if x is None else f'{x:.{d}f}'
    lines=['# Onafhankelijke historische toets: drie bevroren modellen','',r['status'],'',
        '24 oktober 2026. Formele uitkomstvrijgave door de gebruiker met expliciete aanvaarding van de bekende bronbeperkingen. Geen parameters, rollovers, prijzen of eerdere rapporten aangepast. Dit is historische replicatie, geen prospectieve of onafhankelijk-vendor-gecertificeerde proef.','',
        '## Vooraf vastgelegde steekproef en varianten','',
        f"Beslissende periode: {START} t/m {END}. De8 eerder bekeken dagen2–11januari2019 zijn uitgesloten, maar mogen als vooraf bekende opwarming dienen. Er zijn {r['usable_months']} bruikbare kalendermaanden en {r['evaluation_days']['PRIMARY_STRICT']} gemeenschappelijke evaluatiedagen. Niet elke evaluatiedag geeft een signaal.",'',
        'Primair: negen voorlopige datums blind uitgesloten, plus ontbrekende RTH-/09:29-ankerbars en onbruikbare ATR. Secundair: beschikbare data van de negen datums meenemen waar bestaande full-RTH-regels dat toestaan. Geen aanvulling van ontbrekende minuten, geen speciale feestdagtrades. De negen waren al niet eligible of vallen buiten het venster. Daarom zijn de twee vooraf vastgelegde evaluatiemaskers identiek. Dezelfde indicatorhistorie blijft in beide varianten behouden. Een nuleffect in deze gevoeligheidscontrole valideert die historie NIET onafhankelijk.','',
        'Per-model context: maandwisseling733, compressie705, sweep619dagen. Dagen zonder benodigde modelspecifieke context blijven voor die sleeve zonder positie. Het gemeenschappelijke dagelijkse statistiekuniversum blijft733dagen, inclusief nul-posities. Geen ToM-selectie op alleen aanwezige kalenderdagen.','',
        '## Primair: ruwe NQ-punten en dollars','',
        '| Model | Componenttrades | Actieve dagen | Netto pt | Netto $ | PF | Winrate | DD dag pt | DD minuut pt | Sharpe |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for model,row in r['variants']['PRIMARY_STRICT'].items():
        p=row['points'];lines.append(f"| {names[model]} | {p['component_trades']} | {p['active_days']} | {f(p['total'])} | {f(p['total']*20,2)} | {f(p['profit_factor'])} | {f(p['winrate_active_days']*100 if p['winrate_active_days'] is not None else None,2)}% | {f(p['daily_close_drawdown'])} | {f(p['minute_close_drawdown'])} | {f(p['sharpe_daily_annualized'])} |")
    lines += ['',
        'NQwaarde$20/punt. Kosten$24,50RT=1,225punt per volledige componenttrade, reeds in netto verwerkt. Portfolio=precies1/3 per model, niet3contracten en geen herverdeling bij afwezige signalen. Portfoliopunten zijn theoretische gewogen contractpunten. PF/winrate op geaggregeerde actieve dagen; portfolio-tradetelling betreft componentuitvoeringen. Geen MNQ- of werkelijk brokerfill-resultaat geclaimd.','',
        '## Primair: vooraf bekende ATR14-eenheden en geregistreerde toetsen','',
        '| Model | Netto ATR | PF ATR | DD dag ATR | DD minuut ATR | Gem. ATR/dag | 95% CI gem. ATR/dag | Ruwe p | Holm4 p | Gereserveerde Holm6 p | Formeel oordeel |','|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|']
    for model,row in r['variants']['PRIMARY_STRICT'].items():
        a=row['atr'];ci=a['mean_ci95'];lines.append(f"| {names[model]} | {f(a['total'],5)} | {f(a['profit_factor'])} | {f(a['daily_close_drawdown'],5)} | {f(a['minute_close_drawdown'],5)} | {f(a['mean_per_evaluation_day'],6)} | [{f(ci[0],6)}; {f(ci[1],6)}] | {f(a['p_raw'],5)} | {f(a['p_holm4'],5)} | {f(a['p_holm6_reserved'],5)} | {row['formal_status']} |")
    lines += ['',
        '1ATR is een schaalmaat, geen stop of maximale schade. Alle vier primaire toetsen betreffen het dagelijkse nettoATR-gemiddelde; ruwepuntenp-waarden zijn uitsluitend beschrijvend. Exact de geregistreerde gezamenlijke2-maands moving-blockbootstrap,10.000trekkingen,seed20261022311. CI95 is nominaal, niet meervoudig gecorrigeerd. De hierna getoonde Bonferroni4-intervallen geven afzonderlijk een benaderende simultane95%-band. Bootstrap veronderstelt voldoende stabiele afhankelijkheid; dekking is geen garantie.','',
        '| Model | Simultane95%-band gem. ATR/dag (Bonf4) | Nominale95% CI totale ATR bij vaste N | 95% CI Sharpe ATR | Ruwepunten Holm4 p (beschrijvend) |','|---|---|---|---|---:|']
    for model,row in r['variants']['PRIMARY_STRICT'].items():
        a=row['atr'];b=a['mean_familywise95_bonf4'];t=a['total_fixed_N_ci95'];s=a['sharpe_ci95']
        lines.append(f"| {names[model]} | [{f(b[0],6)}; {f(b[1],6)}] | [{f(t[0],5)}; {f(t[1],5)}] | [{f(s[0])}; {f(s[1])}] | {f(row['points']['p_holm4'],5)} |")
    lines += ['',
        'Holm4: de4vooraf geregistreerde co-primaire ATR-toetsen. Voor een projectbrede claim daarnaast Holm6, met de2niet uitgevoerde afternoonhypothesen op p=1; die twee strategieën zijn niet gedraaid. Minimaal24maanden en30ATR-readytrades per signaal. De combinatie vereist voldoende informatie voor alle3. Een secundaire uitkomst kan een falende primaire toets niet redden. STATISTICAL_SUPPORT_ON_REGISTERED_REMAINDER is niet hetzelfde als bewezen toekomstige winstgevendheid of toestemming voor echt geld.','',
        '## Secundaire inclusie en verschil met primair','',
        '| Model | Trades | Netto pt | Netto ATR | PF punten / ATR | Winrate | DD dag pt / ATR | Holm4 ATR p, beschrijvend | Δ pt | Δ ATR |','|---|---:|---:|---:|---|---:|---|---:|---:|---:|']
    for model,row in r['variants']['SECONDARY_AVAILABLE'].items():
        p,a=row['points'],row['atr'];d=r['sensitivity_difference'][model]
        lines.append(f"| {names[model]} | {p['component_trades']} | {f(p['total'])} | {f(a['total'],5)} | {f(p['profit_factor'])} / {f(a['profit_factor'])} | {f(p['winrate_active_days']*100 if p['winrate_active_days'] is not None else None,2)}% | {f(p['daily_close_drawdown'])} / {f(a['daily_close_drawdown'],5)} | {f(a['p_holm4'],5)} | {f(d['net_points'])} | {f(d['net_atr'],5)} |")
    lines += ['', '## Alle kwartalen: vaste eindperiode, geen selectie','',
        '| Kwartaal | Model | Trades | Primair netto pt | Primair netto ATR | Inclusie netto pt | Inclusie netto ATR |','|---|---|---:|---:|---:|---:|---:|']
    lookup={(x['variant'],x['quarter'],x['model']):x for x in r['quarterly']}
    for q in sorted({x['quarter'] for x in r['quarterly']}):
        for model in MODELS:
            a=lookup['PRIMARY_STRICT',q,model];b=lookup['SECONDARY_AVAILABLE',q,model]
            lines.append(f"| {q} | {names[model]} | {a['component_trades']} | {f(a['net_points'])} | {f(a['net_atr'],5)} | {f(b['net_points'])} | {f(b['net_atr'],5)} |")
    lines += ['',
        '## Uitvoerings- en bronbeperkingen','',
        'Exacte volgende minuutopen en laatste minuutclose zijn OHLCV-proxies, geen tick-level uitvoeringsbewijs. Geen stops/targets of intrabar-volgordeclaim. Minuut-DD gebruikt minuutcloses met volledigeRT-frictie bij entry, niet de slechtst mogelijke tickroute. De2019–2021-reeks is niet prospectief en absolute niet-blootstelling aan alle marktinformatie is niet aantoonbaar.','',
        'De gebruiker heeft de resterende bronbeperkingen expliciet geaccepteerd:']+[f'- {limit}' for limit in r['accepted_limits']]+['',
        'EXPLICIT_OUTCOME_RELEASE_REQUIRED in het historische voorbereidingsrapport is met dit aparte vrijgavebesluit afgehandeld; het oude rapport blijft als historische stand ongewijzigd. De andere beperkingen zijn aanvaard, niet technisch opgelost. De Barchart-vraag is nog open. Geen wijziging van rolloverdatum op basis van P&L.','',
        '## Reproductie, publicatie en privacy','',
        'Twee volledige runs vanaf alle105originele gehashteCSV-kopieën, opnieuw ontdubbeld, met opnieuw gereproduceerde volume-route, onveranderde spreads en exact dezelfde kalender-v2-context. Trade-/dagledgers, context en alle uitvoerbytes worden vergeleken voordat publieke bestanden worden geschreven. De reproductie is onafhankelijk uitgevoerd met dezelfde code en vendorbron, niet door een onafhankelijke leverancier of onderzoeker.','',
        '`python -m scripts.historical_validation verify` controleert freeze en uitvoerhashes. `replay` voert de vrijgegeven gepaarde run eenmaal uit; als een afgerond bewijs bestaat, controleert het alleen hashes. Geen parameterzoektocht of tussenresultaat-API. CSV-ledgers, prijsarrays en context blijven Gitignored. Publiek: dit aggregatierapport, kwartaal-CSV en JSON. Publicatiebewijs met exacte commit en productieadres wordt afzonderlijk vastgelegd na geslaagde tests/build.']
    return '\n'.join(lines)+'\n'


def replay():
    if VERIFY.exists():return dict(status='ALREADY_COMPLETED_HASH_VERIFICATION_ONLY',integrity=verify())
    integrity=verify()
    if not h.ignored(OUT/'run1/trades.csv'):raise ValueError('Private ledger directory not ignored')
    if (OUT/'access.json').exists():raise ValueError('Partial outcome access exists; inspect before any recovery')
    h.dump(OUT/'access.json',dict(status='RELEASED_PAIRED_RUN_STARTED',release_sha256=h.sha(RELEASE),date='2026-10-24'))
    first=one_run(OUT/'run1')
    print('First evaluation complete; running independent raw-source reproduction',flush=True)
    second=one_run(OUT/'run2')
    a={p.name:h.sha(p) for p in sorted((OUT/'run1').iterdir()) if p.is_file()}
    b={p.name:h.sha(p) for p in sorted((OUT/'run2').iterdir()) if p.is_file()}
    if a!=b:raise AssertionError('Independent outcome reproduction differs')
    h.dump(RESULT,first);h.dump(PUBLIC,first)
    text=report(first);REPORT.write_text(text);PUBLIC_REPORT.write_text(text)
    write_csv(ROOT/'public/reports/HISTORICAL_VALIDATION_QUARTERS.csv',first['quarterly'])
    paths=[RESULT,PUBLIC,REPORT,PUBLIC_REPORT,ROOT/'public/reports/HISTORICAL_VALIDATION_QUARTERS.csv']
    proof=dict(status='BYTE_IDENTICAL_RELEASED_HISTORICAL_REPLICATION',date='2026-10-24',
        first={str((OUT/'run1'/name).relative_to(ROOT)):digest for name,digest in a.items()},
        second={str((OUT/'run2'/name).relative_to(ROOT)):digest for name,digest in b.items()},
        published_files={str(p.relative_to(ROOT)):h.sha(p) for p in paths},
        release_sha256=h.sha(RELEASE),integrity=integrity,signals_computed=True,holdout_executed=True)
    h.dump(VERIFY,proof)
    h.dump(ROOT/'public/data/historical-validation-verification.json',dict(status=proof['status'],
        date=proof['date'],independently_recomputed_files=len(a),source_files=105,
        release_sha256=proof['release_sha256'],published_files=proof['published_files'],
        no_private_arrays=True,previous_state_preserved=True))
    verify()
    return dict(status=proof['status'],reproduced_files=len(a),evaluation_days=first['evaluation_days'],
        results={m:dict(net_points=row['points']['total'],net_atr=row['atr']['total'],
            p_holm4=row['atr']['p_holm4'],status=row['formal_status']) for m,row in first['variants']['PRIMARY_STRICT'].items()})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register','replay','verify'])
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
