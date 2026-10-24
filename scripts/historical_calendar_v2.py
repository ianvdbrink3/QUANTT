"""Append-only calendar preparation. No selectors, outcomes, trades or fills.

python -m scripts.historical_calendar_v2 register|verify|run|replay
Original preparation/evidence outputs are read-only inputs to this version.
"""
import argparse
import csv
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import prepare_historical_contracts as h

ROOT = h.ROOT
RAW = ROOT/'data/raw/historical-calendar-v2'
OUT = ROOT/'artifacts/historical-calendar-v2'
LOCK = ROOT/'research/historical-calendar-v2-lock.json'
CATALOG = ROOT/'research/historical-calendar-v2-sources.json'
RESULT = ROOT/'research/historical-calendar-v2.json'
PUBLIC = ROOT/'public/data/historical-calendar-v2.json'
REPORT = ROOT/'docs/HISTORICAL_CALENDAR_V2.md'
PUBLIC_REPORT = ROOT/'public/reports/HISTORICAL_CALENDAR_V2.md'
EXPORT = ROOT/'research/historical-calendar-v2-exceptions.csv'
VERIFICATION = ROOT/'research/historical-calendar-v2-verification.json'
MODELS = ('TOM_RTH','COMPRESSED_BREAK5','SWEEP_REV_1200')
KEYS = dict(atr14_prior='atr',PDH='PDH',PDL='PDL',ONH='ONH',ONL='ONL')
METHOD = {
    'version':'HISTORICAL_CALENDAR_V2_2026_10_23',
    'date':'2026-10-23','outcome_release':False,'missing_minutes_are_zero':False,
    'changes':{'2021-04-02':'09:15 America/New_York, not closed'},
    'rollovers':'All 13 original decisions, effective dates and joint-close spreads unchanged.',
    'context':'Frozen sequential true-range algorithm, 14 prior valid observations. A short/incomplete scheduled session clears previous RTH context; the following complete RTH does not add a TR without a previous complete RTH. No fallback range-only TR.',
    'eligibility':'390 complete RTH minutes, 09:29 boundary and prior positive ATR; compression also prior PDH/PDL; sweep also all 930 overnight minutes. No actual candidate conditions evaluated.',
    'source_policy':'Direct CME XLS cells strongest. Explicitly dated CME-labeled tables preserved by a broker are document-supported, not independently authenticated originals. Cropped attributed copies remain provisional. No product/year extrapolation.',
    'publication':'LOCAL_ONLY_NO_PUSH_NO_DEPLOY',
}

# Manual visual transcription of the dated Equity row, not broker prose/OCR.
# (dates, original/discovered attachment stem, close CT or fully CLOSED, grade)
TABLES = [
 ('2018-11-22','f9de7583ffdab003','12:00','CROPPED_ATTRIBUTED'),
 ('2018-11-23','f9de7583ffdab003','12:15','CROPPED_ATTRIBUTED'),
 ('2018-12-24','44e166353b70640b','12:15','CME_LABELED_PRESERVED'),
 ('2018-12-25','44e166353b70640b',None,'CME_LABELED_PRESERVED'),
 ('2019-01-01','7110df1ac3dc6ceb',None,'CME_LABELED_PRESERVED'),
 ('2019-01-21','28b20db2cd71e372','12:00','CROPPED_ATTRIBUTED'),
 ('2019-02-18','4f23a81d2c56e773','12:00','CROPPED_ATTRIBUTED'),
 ('2019-04-19','26c86781a6825bba',None,'CME_LABELED_PRESERVED'),
 ('2019-05-27','5e0889c2a9e18416','12:00','CME_LABELED_PRESERVED'),
 ('2019-07-03','fdebc93a06c62ff7','12:15','CME_LABELED_PRESERVED'),
 ('2019-07-04','fdebc93a06c62ff7','12:00','CME_LABELED_PRESERVED'),
 ('2019-09-02','1915aea4205d27b4','12:00','CME_LABELED_PRESERVED'),
 ('2019-11-28','fb4eb851a4f9720d','12:00','CME_LABELED_PRESERVED'),
 ('2019-11-29','fb4eb851a4f9720d','12:15','CME_LABELED_PRESERVED'),
 ('2019-12-24','7410f884c69063f7','12:15','CME_LABELED_PRESERVED'),
 ('2019-12-25','7410f884c69063f7',None,'CME_LABELED_PRESERVED'),
 ('2020-01-01','c92ab2412d680d30',None,'CME_LABELED_PRESERVED'),
 ('2020-01-20','ba317a8117fcc62d','12:00','CROPPED_ATTRIBUTED'),
 ('2020-02-17','88b06f6ea1934a2b','12:00','CROPPED_ATTRIBUTED'),
 ('2020-04-10','bdfa23d0f218c9d5',None,'CROPPED_ATTRIBUTED'),
 ('2020-05-25','2d4963dc848a2f20','12:00','CME_LABELED_PRESERVED'),
 ('2020-07-03','3df57f5cdb152fe6','12:00','CME_LABELED_PRESERVED'),
 ('2020-09-07','fffbc243ce60987f','12:00','CME_LABELED_PRESERVED'),
 ('2020-11-26','df94aec68b61b3e7','12:00','CME_LABELED_PRESERVED'),
 ('2020-11-27','df94aec68b61b3e7','12:15','CME_LABELED_PRESERVED'),
 ('2020-12-24','cd6a3a9855605f2a','12:15','CME_LABELED_PRESERVED'),
 ('2020-12-25','cd6a3a9855605f2a',None,'CME_LABELED_PRESERVED'),
 ('2021-01-01','1627e6c52e0dc54e',None,'CME_LABELED_PRESERVED'),
 ('2021-01-18','d00da2e28a231b0a','12:00','CROPPED_ATTRIBUTED'),
 ('2021-02-15','7479dbc63a96fa47','12:00','CROPPED_ATTRIBUTED'),
 ('2021-04-02','1732b7467c7b13de','08:15','CME_LABELED_PRESERVED'),
 ('2021-05-31','1580eab50674a0b4','12:00','CME_LABELED_PRESERVED'),
 ('2021-07-05','eec570e3fb47d601','12:00','CME_LABELED_PRESERVED'),
 ('2021-09-06','5c2ccaf4ef97bb6c','12:00','CME_LABELED_PRESERVED'),
 ('2021-11-25','71db2b5b929c70b4','12:00','CME_LABELED_PRESERVED'),
 ('2021-11-26','71db2b5b929c70b4','12:15','CME_LABELED_PRESERVED'),
 ('2021-12-24','706b0441b61a1813',None,'CME_LABELED_PRESERVED'),
]


def check_hashes(items):
    for name,digest in items.items():
        if h.sha(ROOT/name)!=digest:raise ValueError('Changed protected/source bytes: '+name)


def verify():
    lock=json.loads(LOCK.read_text())
    check_hashes({**lock['protected_files'],**lock['private_inputs'],**lock['source_bytes'],**lock['method_files']})
    if lock['method']!=METHOD:raise ValueError('Calendar method changed')
    return dict(protected_files=len(lock['protected_files']),private_inputs=len(lock['private_inputs']),
        source_documents=len(lock['source_bytes']),prior_freeze=h.verify(),signals_computed=False)


def build_catalog():
    manifest=json.loads((RAW/'download-manifest.json').read_text())
    docs={Path(r['path']).stem:r for r in manifest['sources'] if 'path' in r}
    old=json.loads((ROOT/'research/historical-evidence-audit.json').read_text())
    cells={r['day']:r for r in old['verified_CME_calendar_cells']}
    rows=[]
    for day,stem,ct,grade in TABLES:
        doc=docs[stem]
        check_hashes({doc['path']:doc['sha256']})
        ny=pd.Timestamp(f'{day} {ct}',tz='America/Chicago').tz_convert('America/New_York').strftime('%H:%M') if ct else None
        row=dict(day=day,product='Equity',close_ct=ct,close_ny=ny,grade=grade,
            source=doc['url'],parent=doc['parents'][0],source_sha256=doc['sha256'],
            private_source=doc['path'],date_scope=day,
            locator=f'Equity row; calendar date {day}; '+('CLOSED column' if ct is None else ('HALT column' if ct=='12:00' else 'CLOSE column')),
            transcription='MANUAL_VISUAL_REVIEW_NOT_OCR',year_visible_in_table=grade!='CROPPED_ATTRIBUTED',
            reopen_ct='17:00' if ct=='12:00' else None,
            reopen_scope='Same civil evening only for HALT; not inferred for full/early closures.')
        if day in cells:
            c=cells[day]
            if ct!=c['close_ct'] or ny!=c['close_ny']:raise ValueError('XLS and preserved table disagree')
            receipt=next(r for r in old['additional_source_receipts'] if r['sha256']==c['source_sha256'])
            row.update(grade='DIRECT_CME_XLS_VERIFIED',source=c['source'],source_sha256=c['source_sha256'],
                private_source=receipt['private_copy'],corroborating_table=doc['url'],
                locator=f"{c['sheet']} sheet, {c['cell']} zero-based cell, Equity Products; {c['action']} {ct} CT")
        rows.append(row)
    rows.append(dict(day='2018-12-05',product='US Equity Index futures',close_ct='08:30',close_ny='09:30',
        grade='PREVIOUSLY_REVIEWED_PRIMARY_NOTICE',source=h.SOURCES['mourning'],date_scope='2018-12-05',
        locator='SER-8289, US Equity Index futures/options halt; prior audit reference, no new local PDF receipt',
        source_sha256=None,private_source=None,year_visible_in_table=True,reopen_ct='17:00'))
    if {r['day'] for r in rows}!=h.CLOSED|h.HALF:raise ValueError('Incomplete exception register')
    return dict(method=METHOD,exceptions=sorted(rows,key=lambda r:r['day']),
        normal_year_end=dict(day='2021-12-31',close_ct='16:00',close_ny='17:00',grade='CME_LABELED_PRESERVED',
            source=docs['aba1477d249f6264']['url'],source_sha256=docs['aba1477d249f6264']['sha256'],
            locator='CME-labeled New Years Dec30 2021–Jan3 2022, Equity row Dec31 regular close; cash open.'),
        download_manifest_sha256=h.sha(RAW/'download-manifest.json'),
        attribution_limit='Preserved image provenance is not cryptographic CME-authorship certification; cropped tables remain provisional.')


def register():
    if LOCK.exists():return verify()
    h.dump(CATALOG,build_catalog())
    # All pre-existing tracked AND untracked work is protected, not only HEAD.
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    new={'scripts/collect_calendar_v2_sources.py','scripts/historical_calendar_v2.py','tests/test_historical_calendar_v2.py',str(CATALOG.relative_to(ROOT))}
    new|={n for n in names if n.startswith('app/research/historical-calendar-v2/')}
    protected={n:h.sha(ROOT/n) for n in names if n and n not in new and (ROOT/n).is_file()}
    inputs={str(p.relative_to(ROOT)):h.sha(p) for directory in (h.OUT,ROOT/'artifacts/historical-evidence')
        for p in directory.rglob('*') if p.is_file()}
    sources={str(p.relative_to(ROOT)):h.sha(p) for p in RAW.iterdir() if p.is_file()}
    sources.update({r['private_source']:r['source_sha256'] for r in json.loads(CATALOG.read_text())['exceptions'] if r.get('private_source')})
    method_files={n:h.sha(ROOT/n) for n in new if (ROOT/n).is_file() and not n.startswith('app/') and not n.startswith('tests/')}
    h.dump(LOCK,dict(method=METHOD,protected_files=protected,private_inputs=inputs,source_bytes=sources,
        method_files=method_files,anchor_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()))
    return verify()


class CalendarV2(h.HistoricalCalendar):
    def __init__(self):
        super().__init__()
        self.registry['closes_ny']['2021-04-02']='09:15'


def boundary_evidence(active,catalog,calendar):
    lookup=dict(tuple(active.groupby('trade_date')))
    rows=[]
    for spec in catalog['exceptions']:
        day=spec['day'];g=lookup.get(day,active.iloc[:0]);ix=calendar.grid(day)
        good=g.index[g.usable];old=h.HistoricalCalendar().grid(day)
        if spec['close_ny']!=calendar.registry['closes_ny'][day]:raise ValueError('Source/calendar mismatch')
        rows.append(dict(spec,expected_minutes=len(ix),observed_bars=len(g),missing_minutes=len(ix.difference(good)),
            unexpected_minutes=len(good.difference(ix)),old_expected_minutes=len(old),
            first_observed_ny=g.index.min().tz_convert('America/New_York').isoformat() if len(g) else None,
            last_observed_ny=g.index.max().tz_convert('America/New_York').isoformat() if len(g) else None,
            changed_grid=not old.equals(ix),missing_minute_meaning='UNKNOWN_NOT_ZERO_NOT_AUTOMATIC_CORRUPTION'))
    return rows


def same(a,b):
    return bool((not np.isfinite(a) and not np.isfinite(b)) or a==b)


def technical_context(active,rolls,calendar,prefix=True):
    days=[d for d in pd.bdate_range('2018-11-19','2021-12-31').strftime('%Y-%m-%d') if len(calendar.grid(d))]
    state=h.contexts(active,days,calendar,rolls)
    previous={r['day']:r for r in json.loads((h.OUT/'prior-context.json').read_text())}
    quality=json.loads((h.OUT/'active-day-quality.json').read_text())
    daily=[];private=[];changed=[]
    for day in days:
        ctx=state[day][1]
        private.append(dict(day=day,**{name:ctx[key] for name,key in KEYS.items()}))
        if day in previous:
            fields=[name for name,key in KEYS.items() if not same(np.nan if previous[day][name] is None else previous[day][name],ctx[key])]
            if fields:changed.append(dict(day=day,fields=fields))
        old=next((r for r in quality if r['day']==day),None)
        if old:
            atr=bool(np.isfinite(ctx['atr']) and ctx['atr']>0)
            pdready=bool(np.isfinite(ctx['PDH']) and np.isfinite(ctx['PDL']))
            daily.append(dict(day=day,clean_full_RTH=old['clean_full_RTH'],cash_half=old['cash_half'],normal_cash_session=old['normal_cash_session'],
                TOM_RTH=bool(old['clean_full_RTH'] and atr),
                COMPRESSED_BREAK5=bool(old['clean_full_RTH'] and atr and pdready),
                SWEEP_REV_1200=bool(old['clean_full_RTH'] and atr and old['overnight_complete'])))
    groups={}
    for label,start in [('FULL_2019_2021','2019-01-02'),('REGISTERED_REMAINDER','2019-01-14')]:
        q=[r for r in daily if start<=r['day']<='2021-12-31']
        groups[label]=dict(cash_sessions=len(h.cash_dates(start,'2021-12-31')),
            normal_cash_sessions=sum(r['normal_cash_session'] for r in q),cash_half_sessions=sum(r['cash_half'] for r in q),
            clean_full_RTH=sum(r['clean_full_RTH'] for r in q),technical_by_model={m:sum(r[m] for r in q) for m in MODELS})
    return days,state,private,daily,changed,groups


def cutoff_checks(active,days,state,calendar,rolls,targets):
    checks=[]
    for day in sorted(set(targets)&set(days)):
        cutoff=h.at(day,'09:30')
        restricted=h.contexts(active[active.index<cutoff],[d for d in days if d<=day],calendar,
            [r for r in rolls if r['session']<=day])
        for key in (*KEYS.values(),'prior_close'):
            if not same(restricted[day][1][key],state[day][1][key]):raise AssertionError('Future-sensitive context: '+day+' '+key)
        checks.append(dict(day=day,cutoff_utc=cutoff.isoformat(),future_removed=True,context_identical=True))
    return checks


def write_csv(rows):
    cols=['day','grade','close_ct','close_ny','expected_minutes','observed_bars','missing_minutes','unexpected_minutes','changed_grid','source','source_sha256','locator']
    with EXPORT.open('w',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)


def run():
    integrity=verify();catalog=json.loads(CATALOG.read_text());OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(h.REGISTER.read_text());parts=[]
    for item in manifest['files']:
        frame,_=h.read_source(item);parts.append(frame)
    rebuilt,duplicates=h.reconcile(parts);del parts
    full=pd.read_parquet(h.OUT/'contract-bars.parquet')
    pd.testing.assert_frame_equal(rebuilt,full);del rebuilt
    active=pd.read_parquet(h.OUT/'active-bars.parquet')
    baseline=json.loads(h.RESULT.read_text());calendar=CalendarV2()
    schedule=[h.Activation('NQZ18','2018-11-19')]+[h.Activation(r['to'],r['effective_session']) for r in baseline['rollovers']]
    spreads=h.roll_spreads(full[full.usable],schedule)
    # A separate active-contract selection proves no row/price switch was changed.
    from scripts.oos_preparation.route import select_active
    selected=select_active(full,schedule)
    selected=selected[selected.trade_date.between('2018-11-19','2021-12-31')]
    pd.testing.assert_frame_equal(selected,active)
    print('105 raw source hashes + exact reconstructed bars verified',flush=True)
    rows=boundary_evidence(active,catalog,calendar)
    days,state,private,daily,changed,groups=technical_context(active,spreads,calendar)
    transitions=['2019-03-10','2019-11-03','2020-03-08','2020-11-01','2021-03-14','2021-11-07']
    dst=[]
    for transition in transitions:
        for delta in (-2,1):
            day=(pd.Timestamp(transition)+pd.Timedelta(days=delta)).strftime('%Y-%m-%d')
            stamp=h.at(day,'09:30')
            dst.append(dict(transition=transition,day=day,open_utc=stamp.isoformat(),open_bar_present=stamp in active.index))
    targets=[r['effective_session'] for r in baseline['rollovers']]+[r['day'] for r in changed]+[r['day'] for r in dst]+sorted(h.HALT_DAYS)+['2021-04-02']
    print('Rechecking causality at changed sessions, rollovers, DST and halt days',flush=True)
    checks=cutoff_checks(active,days,state,calendar,spreads,targets)
    provisional=[r['day'] for r in rows if r['grade']=='CROPPED_ATTRIBUTED']
    grades={grade:sum(r['grade']==grade for r in rows) for grade in sorted({r['grade'] for r in rows})}
    safe_rows=[{k:v for k,v in r.items() if k!='private_source'} for r in rows]
    r=dict(status='CALENDAR_V2_COMPLETE_CONDITIONAL_NOT_RELEASED',method=METHOD,integrity=integrity,
        source_files_verified=len(manifest['files']),raw_to_cached_exact=True,active_bars_unchanged=True,
        reconciliation=duplicates,calendar_cases=len(rows),source_grades=grades,
        remaining_provisional_dates=provisional,exceptions=safe_rows,normal_year_end=catalog['normal_year_end'],
        groups_before=baseline['groups'],groups_after=groups,context_changed=changed,
        cutoff_checks=checks,DST_checks=dst,rollovers_unchanged=13,spreads_unchanged=True,
        source_catalog_sha256=h.sha(CATALOG),code_sha256=h.sha(Path(__file__)),
        release_approved=False,signals_computed=False,holdout_executed=False,raw_data_public=False,
        remaining_blockers=['CROPPED_TABLES_REQUIRE_FULL_PRIMARY_PROVENANCE',
            'NQ_HALT_SECONDS_NOT_INDEPENDENTLY_CERTIFIED','VENDOR_MISSING_MINUTE_SEMANTICS_AND_VOLUME_UNIVERSE_UNRESOLVED',
            'EARLIEST_TRUE_VOLUME_CROSSOVER_NOT_CERTIFIED','LICENSE_AND_TICK_FILL_VALIDATION_UNCONFIRMED',
            'EXPLICIT_OUTCOME_RELEASE_REQUIRED'],
        no_backtest_run=True,publication='LOCAL_ONLY_NO_PUSH_NO_DEPLOY')
    h.dump(OUT/'prior-context.json',private);h.dump(OUT/'technical-days.json',daily)
    h.dump(OUT/'fixed-spreads.json',[{k:(v.isoformat() if isinstance(v,pd.Timestamp) else v) for k,v in s.items()} for s in spreads])
    h.dump(RESULT,r);h.dump(PUBLIC,r);write_csv(safe_rows)
    text=report(r);REPORT.write_text(text);PUBLIC_REPORT.write_text(text)
    verify()
    return dict(status=r['status'],source_grades=grades,technical_days=groups,changed_days=len(changed),cutoff_tests=len(checks))


def report(r):
    lines=['# Historische kalender v2 — afzonderlijke technische voorbereiding','',r['status'],'',
        '23 oktober 2026. Geen signalen, cohortselectie, trades, forward returns of P&L berekend. Geen Git-push of productie-uitrol. De oude voorbereiding en rapporten blijven byte-identiek.','',
        '## Besluit','',
        'De kalendercorrectie is apart geïmplementeerd en reproduceerbaar doorgerekend. Dit is géén definitieve goedkeuring van de onafhankelijke test: volume-/vendorvragen en een deel van de primaire bronherkomst blijven open. Een volledig uitgevoerde audit is niet hetzelfde als een volledig gecertificeerde bron.','',
        '## Wat is echt gewijzigd?','',
        'Alleen 2 april 2021: futures open tot 08:15 Chicago = 09:15 New York (13:15 UTC), ondanks gesloten cashmarkt. De verwachte sessie heeft 915 minuten; er zijn 910 vendorbars tot 09:14. Vijf ontbrekende minuten blijven onbekend, niet nul. De andere 37 uitzonderingsgrids zijn niet aangepast. Expiraties, 13 rollovers, joint-close spreads en alle ruwe OHLCV blijven gelijk.','',
        'De oude contextfunctie wordt exact hergebruikt: ATR is het gemiddelde van 14 eerdere geldige true ranges. Een korte/onvolledige geplande sessie wist de vorige-RTH-context. De eerstvolgende volledige sessie produceert dan geen true range zonder vorige volledige RTH; er wordt geen dagrange als vervanging ingevoerd. Dit is expliciet de bevroren architectuur, niet een nieuw geoptimaliseerd ATR-beleid.','',
        '## Bronsterkte, zonder schijnzekerheid','',
        '| Bewijsklasse | Uitzonderingen |','|---|---:|']
    lines += [f'| {k} | {v} |' for k,v in r['source_grades'].items()]
    lines += ['',
        'Alle 38 uitzonderingen zijn afzonderlijk beoordeeld. Een gedateerde, CME-gelabelde afbeelding op een brokerwebsite ondersteunt de getranscribeerde Equity-uren, maar is niet cryptografisch geauthenticeerd door CME. Bijgesneden tabellen missen de volledige titel/jaarcontext en blijven voorlopig. De 3 directe CME-XLS-cellen uit de eerdere audit zijn opnieuw tegen de tabelaflezing gecontroleerd. De rouwdag blijft op het eerder beoordeelde primaire CME-bericht gebaseerd; geen nieuwe lokale PDF-hash geclaimd.','',
        'Nog voorlopig wegens bijgesneden bron: '+', '.join(r['remaining_provisional_dates'])+'.',
        'Cashsessiedatum, kalenderdatum en exchange clearing trade date zijn verschillende begrippen. Meerdere vakantiesessies kunnen één clearingdatum delen. Deze ronde verandert de volume-aggregatie niet en bewijst geen officiële volume-crossover.','',
        '## Technische beschikbaarheid vóór → na','',
        '| Periode | Cashsessies | Schoon 390+09:29 | ATR-context | Compressie-context | Sweep-context |','|---|---:|---:|---:|---:|---:|']
    for label,new in r['groups_after'].items():
        old=r['groups_before'][label];a=old['technical_by_model'];b=new['technical_by_model']
        lines.append(f"| {label} | {new['cash_sessions']} | {new['clean_full_RTH']} | {a['TOM_RTH']} → {b['TOM_RTH']} | {a['COMPRESSED_BREAK5']} → {b['COMPRESSED_BREAK5']} | {a['SWEEP_REV_1200']} → {b['SWEEP_REV_1200']} |")
    lines += ['',
        'Alleen technische context, geen aantal signalen of handelsmogelijkheden. FULL bevat 8 eerder bekeken januaridagen; REGISTERED_REMAINDER begint 14 januari 2019. De 6 halve cashdagen blijven niet eligible voor volledige-RTH-modellen. Geen haltdag of ontbrekende boundary is synthetisch gerepareerd.','',
        f"ATR/PD-context verandert op {len(r['context_changed'])} datums. De beschikbaarheid van PDH/PDL vervalt op 5 april 2021, waardoor één compressie-contextdag afvalt. De overige verschillen betreffen de daaropvolgende ATR-historie. Nachtcontext en actieve prijsbars worden niet aangepast.",'',
        '| Datum | Gewijzigde vooraf bekende contextvelden |','|---|---|']
    lines += [f"| {z['day']} | {', '.join(z['fields'])} |" for z in r['context_changed']]
    lines += ['', '## Elke kalenderuitzondering en de aanwezige bars','',
        '| Datum | Grens NY | Verwacht | Aanwezig | Ontbreekt | Buiten grid | Bewijs |','|---|---|---:|---:|---:|---:|---|']
    for z in r['exceptions']:
        lines.append(f"| {z['day']} | {z['close_ny'] or 'gesloten'} | {z['expected_minutes']} | {z['observed_bars']} | {z['missing_minutes']} | {z['unexpected_minutes']} | [{z['grade']}]({z['source']}) |")
    lines += ['',
        'Verwacht/ontbreekt is een nominaal bar-start-grid, geen bewijs van werkelijk continu handelen of feedcompleetheid. De vijf ontbrekende minuten op 2 april zijn niet automatisch corrupt. De kalender ondersteunt 31 december 2021 als normale Equity-sessie; die dag wordt niet wegens een clearingbericht gesloten verklaard. Bronhashes en precieze rij-/kolomverwijzingen staan in historical-calendar-v2-sources.json en de uitzonderingen-CSV.','',
        '## Causaliteit, DST en bronbehoud','',
        f"{r['source_files_verified']} ruwe CSV’s opnieuw geparseerd en SHA-256 gecontroleerd bij origineel én privé-kopie. De ontdubbelde bars zijn exact gelijk aan de oorspronkelijke Parquet. Alle {r['integrity']['protected_files']} bestaande bestanden en {r['integrity']['private_inputs']} private audit-/voorbereidingsbestanden blijven byte-identiek.",
        f"Toekomst-afkniptest op {len(r['cutoff_checks'])} verschillende openingen: alle 13 rollovers, gewijzigde contextdagen, zes DST-weekenden en de vier haltdagen. Alleen gegevens vóór 09:30 beschikbaar; ATR/PD/nachtcontext exact gelijk. Chicago/NY-conversie gebruikt de echte IANA-zones, geen vaste UTC-offset.",'',
        '## Nog niet vrijgeven','']+[f'- {b}' for b in r['remaining_blockers']]
    lines += ['',
        'Barchart heeft de eerder gestelde ondersteuningsvraag ontvangen. Deze ronde leest geen inbox en claimt geen ontvangen inhoudelijk antwoord. Ontbrekende minuten worden niet als nulvolume geïnterpreteerd; dagvolume vervangt nooit stilzwijgend het minuutvolume. Geen aankoop, accountaanmaak, nieuwe externe berichten of wijziging van kandidaatregels.','',
        '## Reproductie en bestanden','',
        '`python -m scripts.historical_calendar_v2 verify` controleert de beschermde staat. `run` voert alleen kalender-/contextcontrole uit; `replay` doet twee onafhankelijke bronherberekeningen en vergelijkt uitvoerbytes. Gebruik de bestaande onderzoeksomgeving; geen nieuw strategiecommando. De aparte broncollector downloadt alleen werkelijk aangetroffen openbare links en geeft zelf nooit bewijsgoedkeuring.','',
        'Lokaal dashboard: /research/historical-calendar-v2. Publieke-safe JSON/Markdown bevatten tellingen, bronverwijzingen en kwaliteitsvlaggen, geen prijs-, ATR- of minuutarrays. Alle ruwe tabellen/CSV’s en numerieke context blijven Gitignored. De spreadsheetwerkwijze is gevolgd voor ongewijzigde bronbytes, expliciete missings en traceerbare aflezingen.']
    return '\n'.join(lines)+'\n'


def replay():
    first=run()
    paths=[RESULT,PUBLIC,REPORT,PUBLIC_REPORT,EXPORT]+sorted(OUT.glob('*.json'))
    a={str(p.relative_to(ROOT)):h.sha(p) for p in paths}
    run()
    b={str(p.relative_to(ROOT)):h.sha(p) for p in paths}
    if a!=b:raise AssertionError('Calendar v2 replay changed bytes')
    result=dict(status='BYTE_IDENTICAL_CALENDAR_V2_REPLAY',files_sha256=b,integrity=verify(),summary=first,
        signals_computed=False,holdout_executed=False)
    h.dump(VERIFICATION,result)
    return dict(status=result['status'],files=len(b),summary=first)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register','verify','run','replay'])
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
