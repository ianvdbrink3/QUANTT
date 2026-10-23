"""Quality-only historical import. Deliberately no strategy execution route.

Run: python -m scripts.prepare_historical_contracts register|run|verify|replay
Private outputs are Gitignored. Public outputs contain counts/flags, not bars.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.oos_preparation.adapter import (Calendar, FIELDS, SCHEMA, RENAME,
    at, determine_roll, session_dates, sha)
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation
from scripts.reproduce_research.continuous import roll_spreads
from scripts.causal_map.__main__ import prepare, clean

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'research/historical-preparation-protocol.json'
LOCK = ROOT/'research/historical-preparation-lock.json'
REGISTER = ROOT/'research/historical-2019-2021-complete-source-register.json'
OUT = ROOT/'artifacts/historical-preparation'
RESULT = ROOT/'research/historical-preparation-quality.json'
PUBLIC = ROOT/'public/data/historical-preparation.json'
REPORT = ROOT/'docs/HISTORICAL_2019_2021_PREPARATION.md'

CLOSED = set('''2018-11-22 2018-12-05 2018-12-25
2019-01-01 2019-01-21 2019-02-18 2019-04-19 2019-05-27 2019-07-04 2019-09-02 2019-11-28 2019-12-25
2020-01-01 2020-01-20 2020-02-17 2020-04-10 2020-05-25 2020-07-03 2020-09-07 2020-11-26 2020-12-25
2021-01-01 2021-01-18 2021-02-15 2021-04-02 2021-05-31 2021-07-05 2021-09-06 2021-11-25 2021-12-24'''.split())
HALF = set('2018-11-23 2018-12-24 2019-07-03 2019-11-29 2019-12-24 2020-11-27 2020-12-24 2021-11-26'.split())
FUTURES_CLOSED = set('2018-12-25 2019-01-01 2019-04-19 2019-12-25 2020-01-01 2020-04-10 2020-12-25 2021-01-01 2021-04-02 2021-12-24'.split())
HALT_DAYS = set('2020-03-09 2020-03-12 2020-03-16 2020-03-18'.split())
SOURCES = {
 'cash_calendar': 'https://ir.theice.com/press/news-details/2018/NYSE-Group-Announces-2019-2020-and-2021-Holiday-and-Early-Closings-Calendar/default.aspx',
 'pause_removal': 'https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2021/06/SER-8788.pdf',
 'mourning': 'https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2018/12/SER-8289.pdf',
 'halt_dates': 'https://www.nyse.com/article/assessing-nyse-model-performance',
 'halt_coordination': 'https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2020-14',
 'year_end_processing_not_trading_hours': 'https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-new-years-advisory.pdf',
 'expiry_rule_historical': 'https://www.cmegroup.com/market-regulation/files/16-081R_EXHA.pdf',
}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True, allow_nan=False)+'\n')


def ignored(path):
    return subprocess.run(['git', 'check-ignore', '-q', str(path)], cwd=ROOT).returncode == 0


class HistoricalCalendar(Calendar):
    """Civil-session diagnostic grid, not exchange clearing-date certification."""
    def __init__(self):
        closes = {d:'13:00' for d in CLOSED}
        closes.update({d:'13:15' for d in HALF})
        closes.update({d:None for d in FUTURES_CLOSED})
        closes['2018-12-05'] = '09:30'
        super().__init__(dict(reviewed_ranges=[['2018-11-19','2022-01-07']], closes_ny=closes))

    def grid(self, day, remove_observed_outage=False):
        ix = super().grid(day, remove_observed_outage)
        if day < '2021-06-28':
            ix = ix[(ix < at(day,'16:15')) | (ix >= at(day,'16:30'))]
        return ix


def cash_dates(start, end):
    from scripts.edge_marathon.features import cash_dates as legacy_dates
    # Preserve the existing reviewed calendar outside this new extension.
    legacy = set(legacy_dates(start,end))
    return [d for d in pd.bdate_range(start,end).strftime('%Y-%m-%d')
        if (d not in CLOSED if '2018'<=d[:4]<='2021' else d in legacy)]


def cash_context(day):
    """Extended calendar only; bit-identical to old logic on old supported years."""
    t = pd.Timestamp(day)
    dates = cash_dates(t.replace(day=1).strftime('%Y-%m-%d'), (t+pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d'))
    if day not in dates:
        return dict(tom=False, tom_position=None)
    i = dates.index(day)
    position = 'T-1' if i == len(dates)-1 else f'T+{i+1}' if i < 3 else None
    return dict(tom=position is not None, tom_position=position)


def expiry(contract):
    month = {'H':3,'M':6,'U':9,'Z':12}[contract[2]]
    first = pd.Timestamp(year=2000+int(contract[3:]), month=month, day=1)
    return (first + pd.offsets.WeekOfMonth(week=2,weekday=4)).strftime('%Y-%m-%d')


def numeric_flags(g):
    p = g[FIELDS[:4]].to_numpy(float)
    v = g.volume.to_numpy(float)
    finite = np.isfinite(g[FIELDS].to_numpy(float)).all(axis=1)
    coherent = (g.high >= g[FIELDS[:4]].max(axis=1)) & (g.low <= g[FIELDS[:4]].min(axis=1))
    tick = np.isclose(p*4, np.rint(p*4), atol=1e-8, rtol=0).all(axis=1)
    positive = (p>0).all(axis=1)
    volume = np.isfinite(v) & (v>0) & (v==np.rint(v))
    return pd.DataFrame(dict(nonfinite=~finite, incoherent=~coherent.to_numpy(), off_tick=~tick,
        nonpositive_price=~positive, invalid_volume=~volume),index=g.index)


def read_source(item):
    path = ROOT/item['private_copy']
    if sha(path) != item['sha256'] or not ignored(path):
        raise ValueError('Private source hash/Gitignore changed: '+item['filename'])
    original = Path('/Users/ianvandenbrink/Downloads')/item['filename']
    if sha(original) != item['sha256']:
        raise ValueError('Original source hash changed: '+item['filename'])
    raw = pd.read_csv(path)
    if list(raw.columns) != SCHEMA:
        raise ValueError('Source schema changed')
    t = pd.to_datetime(raw.Time, format='%Y-%m-%d %H:%M', errors='coerce')
    footer = raw[t.isna()]
    if not (len(footer)==1 and str(footer.Time.iloc[0]).startswith('Downloaded from Barchart.com as of ')
            and footer.drop(columns='Time').isna().all().all()):
        raise ValueError('Unexpected footer/non-bar record')
    ix = pd.DatetimeIndex(t[t.notna()]).tz_localize('America/Chicago', ambiguous='raise', nonexistent='raise').tz_convert('UTC')
    if not ix.is_monotonic_increasing:
        raise ValueError('Source not ascending')
    g = raw[t.notna()].rename(columns=RENAME)[FIELDS].apply(pd.to_numeric,errors='coerce')
    g.index = ix
    g['contract'] = item['contract']
    g['trade_date'] = session_dates(ix)
    flags = numeric_flags(g)
    g['numeric_valid'] = ~flags.any(axis=1)
    record = dict(filename=item['filename'],sequence=item['sequence'],contract=item['contract'],sha256=item['sha256'],
        bars=len(g),footer_rows=len(footer),duplicate_source_timestamps=int(ix.duplicated().sum()),
        possible_cap=len(g)>=19999,errors={k:int(v) for k,v in flags.sum().items()},
        numeric_valid=bool(g.numeric_valid.all()),embedded_contract_id=False,tick_count_field=False)
    return g, record


def reconcile(parts):
    full = pd.concat(parts).sort_index(kind='stable')
    keys = pd.MultiIndex.from_arrays([full.contract,full.index], names=['contract','utc'])
    dupe = full[keys.duplicated(keep=False)]
    conflict_keys = []
    if len(dupe):
        conflicts = dupe.groupby(['contract',dupe.index])[FIELDS].nunique(dropna=False).gt(1).any(axis=1)
        conflict_keys = list(conflicts[conflicts].index)
    conflicts_mask = keys.isin(conflict_keys)
    full['conflicting_duplicate'] = conflicts_mask
    # Keeping one identical record is safe; conflicting records remain marked
    # and will NEVER be fed into indicators or used to decide a volume roll.
    reconciled = full[~keys.duplicated(keep='first')].copy()
    reconciled['usable'] = reconciled.numeric_valid & ~reconciled.conflicting_duplicate
    return reconciled, dict(source_bars=len(full),unique_contract_bars=len(reconciled),
        duplicate_rows_removed=len(full)-len(reconciled),conflicting_keys=len(conflict_keys),
        conflicting_contract_timestamps=[dict(contract=c,utc=t.isoformat()) for c,t in conflict_keys])


def assess_day(g, day, contract, calendar):
    normal = day not in CLOSED and day not in HALF
    expected = calendar.grid(day)
    exp = expiry(contract)
    if day >= exp:
        expected = expected[expected < at(exp,'09:30')]
    rth = pd.date_range(at(day,'09:30'),at(day,'16:00'),freq='min',inclusive='left')
    good_index = g.index[g.usable]
    missing = rth.difference(good_index)
    boundary = at(day,'09:29') in good_index
    rth_complete = not len(missing)
    clean = bool(normal and rth_complete and boundary)
    prefix = pd.date_range(at((pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d'),'18:00'),at(day,'09:30'),freq='min',inclusive='left')
    return dict(day=day,contract=contract,bars=len(g),cash_closed=day in CLOSED,cash_half=day in HALF,
        normal_cash_session=normal,rth_valid_minutes=390-len(missing),rth_missing=len(missing),
        missing_rth_clocks=list(missing.tz_convert('America/New_York').strftime('%H:%M')),
        boundary_0929=boundary,clean_full_RTH=clean,overnight_complete=not len(prefix.difference(good_index)),
        numeric_bad_bars=int((~g.numeric_valid).sum()),conflict_bars=int(g.conflicting_duplicate.sum()),
        expected_session_minutes=len(expected),session_missing=len(expected.difference(good_index)),
        unexpected_session_minutes=len(g.index.difference(expected)),expiry_or_later=day>=exp,
        known_circuit_breaker_date=day in HALT_DAYS,
        gap_classification=('DOCUMENTED_CASH_HALT_DATE_EXACT_FUTURES_MINUTES_UNCERTIFIED' if len(missing) and day in HALT_DAYS
            else 'UNEXPLAINED_MISSING_MINUTES_NOT_AUTOMATICALLY_CORRUPT' if normal and len(missing) and day<exp
            else 'SCHEDULED_CASH_EXCEPTION_OR_EXPIRY' if not normal or day>=exp else 'COMPLETE'))


def register():
    if LOCK.exists():
        return verify()
    names = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    snap = {n:sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}
    lock = dict(status='QUALITY_METHOD_LOCKED_BEFORE_NUMERIC_IMPORT',protected_files=snap,
        source_register_sha256=sha(REGISTER),protocol_sha256=sha(PROTOCOL),outcome_release=False)
    dump(LOCK,lock)
    return verify()


def verify():
    lock = json.loads(LOCK.read_text())
    for name,digest in lock['protected_files'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Protected pre-existing bytes changed: '+name)
    if sha(REGISTER)!=lock['source_register_sha256'] or sha(PROTOCOL)!=lock['protocol_sha256']:
        raise ValueError('Source/protocol changed')
    from scripts.survivor_portfolio import verify as verify_survivors
    prior = verify_survivors()
    return dict(protected_files=len(lock['protected_files']),previous_freeze_files=len(prior['protected_files']),outcome_release=False)


def roll_route(full, contracts, calendar):
    usable = full[full.usable].copy()
    schedule = [Activation(contracts[0],'2018-11-19')]
    records = []; failure = None
    for old,new in zip(contracts,contracts[1:]):
        try:
            end = min(expiry(old), '2021-12-31')
            r = determine_roll(usable,old,new,calendar,end)
            # Independent prefix proof. No future volume or joint close needed.
            truncated = usable[usable.trade_date.le(r['decision_session'])]
            if determine_roll(truncated,old,new,calendar,r['decision_session']) != r:
                raise AssertionError('Future-dependent rollover')
            evidence = []
            for contract in (old,new):
                g = usable[(usable.contract==contract)&(usable.trade_date==r['decision_session'])]
                ix = calendar.grid(r['decision_session'])
                evidence.append(dict(contract=contract,bars=len(g),expected=len(ix),
                    missing=len(ix.difference(g.index)),unexpected=len(g.index.difference(ix))))
            prior_joint = sorted(set(usable[usable.contract.eq(old)].trade_date)&set(usable[usable.contract.eq(new)].trade_date))
            r.update(future_cutoff_verified=True,coverage=evidence,
                overlap_starts=prior_joint[0] if prior_joint else None,
                decision_on_calendar_exception=r['decision_session'] in CLOSED|HALF,
                complete_observed_minute_coverage=all(e['missing']==0 and e['unexpected']==0 for e in evidence))
            r['status'] = 'OBSERVED_VENDOR_VOLUME_RULE_NOT_INDEPENDENT_VOLUME_CERTIFICATION'
            records.append(r)
            schedule.append(Activation(new,r['effective_session']))
        except ValueError as exc:
            failure = dict(old=old,new=new,error=str(exc))
            break  # No calendar or return-selected fallback.
    return schedule, records, failure


def contexts(active, days, calendar, rolls):
    # Reuse the frozen prior-ATR/PD/overnight routine, NOT any strategy selector.
    source = active[active.usable].copy()
    return prepare(source,days,calendar,rolls)


def run():
    verification = verify()
    manifest = json.loads(REGISTER.read_text())
    parts=[]; files=[]
    for item in manifest['files']:
        g, record = read_source(item);parts.append(g);files.append(record)
    full, duplicates = reconcile(parts)
    del parts
    calendar = HistoricalCalendar()
    plan = json.loads((ROOT/'research/afternoon-historical-download-plan.json').read_text())
    contracts = list(dict.fromkeys(r['contract'] for r in plan['rows']))
    quality=[]
    for contract,g in full.groupby('contract',sort=False):
        lookup = dict(tuple(g.groupby('trade_date',sort=True)))
        for day in pd.bdate_range(g.trade_date.min(),min(g.trade_date.max(),'2021-12-31')).strftime('%Y-%m-%d'):
            quality.append(assess_day(lookup.get(day,g.iloc[:0]),day,contract,calendar))
    schedule, roll_records, failure = roll_route(full,contracts,calendar)
    active = select_active(full,schedule)
    if failure:
        # Do not silently extend the last demonstrated contract to infinity.
        active = active[active.trade_date.lt(expiry(schedule[-1].contract))]
    active = active[active.trade_date.between('2018-11-19','2021-12-31')]
    rolls = roll_spreads(full[full.usable],schedule)
    days = [d for d in pd.bdate_range('2018-11-19','2021-12-31').strftime('%Y-%m-%d') if len(calendar.grid(d))]
    state = contexts(active,days,calendar,rolls)
    lookup = dict(tuple(active.groupby('trade_date',sort=True)))
    daily=[]; private_context=[]
    for day in days:
        contract = next((s.contract for s in reversed(schedule) if s.session<=day),None)
        g = lookup.get(day,active.iloc[:0])
        row = assess_day(g,day,contract,calendar)
        ctx = state[day][1]
        atr = bool(np.isfinite(ctx['atr']) and ctx['atr']>0)
        prior = bool(np.isfinite(ctx['PDH']) and np.isfinite(ctx['PDL']))
        row.update(prior_ATR14_ready=atr,prior_day_context_ready=prior,
            TOM_RTH_technical=bool(row['clean_full_RTH'] and atr),
            COMPRESSED_BREAK5_technical=bool(row['clean_full_RTH'] and atr and prior),
            SWEEP_REV_1200_technical=bool(row['clean_full_RTH'] and atr and row['overnight_complete']),
            exposure='PREVIOUSLY_INSPECTED' if '2019-01-02'<=day<='2019-01-11' else 'REGISTERED_REMAINDER' if day>='2019-01-14' else 'WARMUP')
        daily.append(row)
        private_context.append(dict(day=day,contract=contract,atr14_prior=ctx['atr'],PDH=ctx['PDH'],PDL=ctx['PDL'],
            ONH=ctx['ONH'],ONL=ctx['ONL']))
    groups = {}
    for label,a,b in [('FULL_2019_2021','2019-01-02','2021-12-31'),('REGISTERED_REMAINDER','2019-01-14','2021-12-31')]:
        q = [r for r in daily if a<=r['day']<=b]
        normal = [r for r in q if r['normal_cash_session']]
        groups[label] = dict(cash_sessions=len(cash_dates(a,b)),normal_cash_sessions=len(normal),cash_half_sessions=sum(r['cash_half'] for r in q),
            clean_full_RTH=sum(r['clean_full_RTH'] for r in q),prior_ATR_ready_clean=sum(r['TOM_RTH_technical'] for r in q),
            technical_by_model={m:sum(r[m+'_technical'] for r in q) for m in ('TOM_RTH','COMPRESSED_BREAK5','SWEEP_REV_1200')},
            missing_standard_days=[dict(day=r['day'],missing=r['rth_missing'],classification=r['gap_classification']) for r in normal if not r['clean_full_RTH']],
            usable_months=len({r['day'][:7] for r in q if r['TOM_RTH_technical']}))
    ds = []
    for transition in ['2019-03-10','2019-11-03','2020-03-08','2020-11-01','2021-03-14','2021-11-07']:
        after = pd.Timestamp(transition)+pd.Timedelta(days=1)
        before = pd.Timestamp(transition)-pd.Timedelta(days=2)
        pair=[]
        for stamp in (before,after):
            d = stamp.strftime('%Y-%m-%d');t=at(d,'09:30')
            pair.append(dict(day=d,open_utc=t.isoformat(),open_bar_present=t in active.index))
        ds.append(dict(transition=transition,sessions=pair))
    numeric_errors = {k:sum(f['errors'][k] for f in files) for k in files[0]['errors']}
    blockers = ['EXPLICIT_OUTCOME_RELEASE_REQUIRED','DATE_SPECIFIC_CME_HOLIDAY_AND_HALT_GRID_NOT_FULLY_CERTIFIED',
        'NEW_FULL_WINDOW_ROUTE_OUTCOME_PARITY_NOT_EXECUTED','LICENSE_AND_INDEPENDENT_VENDOR_VALIDATION_UNCONFIRMED']
    if failure: blockers.append('VOLUME_ROLL_CHAIN_INCOMPLETE')
    if duplicates['conflicting_keys']: blockers.append('CONFLICTING_SOURCE_BARS')
    if any(numeric_errors.values()): blockers.append('NUMERIC_SOURCE_ERRORS')
    if any(not r['complete_observed_minute_coverage'] for r in roll_records): blockers.append('ROLL_VOLUME_INTERIOR_MINUTE_GAPS')
    summary = dict(status='QUALITY_AUDITED_CONDITIONAL_READINESS_NOT_RELEASED',signals_computed=False,holdout_executed=False,
        source_files=len(files),plan_blocks=103,contracts=len(contracts),**duplicates,numeric_errors=numeric_errors,
        physical_source_hashes_verified=True,private_sources_gitignored=True,possible_capped_files=sum(f['possible_cap'] for f in files),
        active_unique_bars=len(active),rollover_count=len(roll_records),rollover_failure=failure,groups=groups,
        rollovers=roll_records,blockers=blockers,integrity=verification,DST_transitions=ds,
        calendar_status='OFFICIAL_CASH_CALENDAR_AND_PAUSE_CHANGE; FULL_CME_EXCEPTION_GRID_PROVISIONAL',sources=SOURCES,
        limitations=json.loads(PROTOCOL.read_text())['limitations'],external_publication=False,
        contract_identity='FIXED_PLAN_AND_FILENAME_NO_EMBEDDED_EXCHANGE_ID',bar_interval='BAR_START_SUPPORTED_INTERNAL_ONLY')
    OUT.mkdir(parents=True,exist_ok=True)
    if not ignored(OUT/'contract-bars.parquet'):
        raise ValueError('Private output not Gitignored')
    full.to_parquet(OUT/'contract-bars.parquet',compression='zstd')
    active.to_parquet(OUT/'active-bars.parquet',compression='zstd')
    dump(OUT/'prior-context.json',private_context)
    dump(OUT/'contract-day-quality.json',quality)
    dump(OUT/'active-day-quality.json',daily)
    dump(OUT/'source-numeric-quality.json',files)
    dump(RESULT,summary)
    dump(PUBLIC,summary)
    REPORT.write_text(report(summary))
    verify()
    print(json.dumps(clean({k:summary[k] for k in ('status','source_files','source_bars','unique_contract_bars','duplicate_rows_removed','numeric_errors','active_unique_bars','rollover_count','rollover_failure','groups','blockers')}),indent=2))
    return summary


def report(r):
    lines=['# Historische NQ-contractreeks 2019–2021: kwaliteitscontrole en import','',r['status'],'',
        'Geen strategie-signalen, toekomstig rendement, trades of P&L berekend. De onafhankelijke toets is niet vrijgegeven. Bron-CSV’s, bestaande regels en oude rapporten blijven ongewijzigd.','',
        f"105 fysieke CSV’s / 103 planblokken / 14 contracten. {r['source_bars']:,} bronbars → {r['unique_contract_bars']:,} unieke contractminuten. {r['duplicate_rows_removed']:,} identieke overlaprecords verwijderd; {r['conflicting_keys']} conflicterende sleutels. Actieve voorlopige reeks: {r['active_unique_bars']:,} bars.",'',
        '## Technische beschikbaarheid, geen signalentelling','',
        '| Periode | Cashsessies incl. halve dagen | Normaal | Schoon 390 +09:29 | ATR-ready | Compressie-context | Sweep-context |','|---|---:|---:|---:|---:|---:|---:|']
    for label,g in r['groups'].items():
        m=g['technical_by_model'];lines.append(f"| {label} | {g['cash_sessions']} | {g['normal_cash_sessions']} | {g['clean_full_RTH']} | {m['TOM_RTH']} | {m['COMPRESSED_BREAK5']} | {m['SWEEP_REV_1200']} |")
    lines += ['', 'TOM-kolom telt uitsluitend ATR-ready evaluatiedagen, niet maandwissels. Compressie telt beschikbare ATR/PDH/PDL, niet de compressiedrempel of uitbraken. Sweep telt volledige nachtcontext, niet sweep-events. De 8 reeds geïnspecteerde januaridagen tellen niet mee in REGISTERED_REMAINDER. De tellingen zijn voorwaardelijk zolang kalender-/rolloverpunten openstaan.','',
        '## Prijzen, tijd en volume','',
        f"Numerieke fouten per categorie: `{r['numeric_errors']}`. Afkappingswaarschuwingen: {r['possible_capped_files']}. Bronhashes van originelen en privé-kopieën opnieuw gecontroleerd. Ontbrekende minuten nooit gevuld, tegenstrijdige records nooit stilzwijgend gekozen.",
        '', 'Chicago-bronlabels worden met IANA-DST naar UTC en New York geconverteerd. Alle zes DST-weekenden hebben expliciete controle op de omringende cash-open labels. Dit valideert de conversie, niet onafhankelijk de vendor-timestampconventie. Volume is positief geheel vendorvolume, niet tegen officiële CME-dagtotalen bevestigd. CSV bevat geen ticks, bid/ask of intern contract-ID.','',
        '## Causale volume-overgangen','', '| Van | Naar | Beslissessie | Actief vanaf | Oude volume | Nieuwe volume | Ontbrekende minuten oud/nieuw |','|---|---|---|---|---:|---:|---|']
    for z in r['rollovers']:
        lines.append(f"| {z['from']} | {z['to']} | {z['decision_session']} | {z['effective_session']} | {z['old_volume']:,} | {z['new_volume']:,} | {' / '.join(str(e['missing']) for e in z['coverage'])} |")
    if r['rollover_failure']:lines+=['',str(r['rollover_failure'])]
    lines += ['', 'Alle getoonde overgangen zijn opnieuw uitsluitend uit een afgekapt bestand t/m de beslissessie gereproduceerd. Activering volgende sessie, spread laatste gemeenschappelijke voltooide15:59-bar vóór activering. Actieve ruwe OHLCV blijft onverschoven. Geen kalenderfallback of selectie op strategie-uitkomst. De bestaande60-minuten-endpointtolerantie certificeert geen ontbrekende interne vendorvolume-minuten.','',
        '## Kalender en afwijkende dagen','',
        'Officiële cashkalender:27 feestdagen en6 vroege sluitingen in2019–2021. Cashdagen zijn niet gelijk aan CME clearing trade dates. De dagelijkse16:15–16:30NY-pauze geldt uitsluitend vóór28juni2021. Expiratie is apart gemarkeerd, geen rollovertrigger. Voor alle datum-specifieke futuresfeestdagen is nog geen volledige primaire urenmatrix teruggevonden. De kalender blijft daarom deels voorlopig.','',
        '9,12,16en18maart2020 zijn gedocumenteerde circuit-breakerdagen. Ontbrekende minuten op die datums worden als halt-geassocieerd gemarkeerd, maar niet zonder exact NQ-bewijs uit de verwachte RTH-grid geschrapt. Deze dagen worden niet kunstmatig390-minuten-eligible gemaakt. Ook geen prijs-fills om een complete simulatie te construeren.','',
        '| Normale datum met onvoldoende RTH/boundary | Ontbrekende RTH-minuten | Classificatie |','|---|---:|---|']
    for z in r['groups']['FULL_2019_2021']['missing_standard_days']:
        lines.append(f"| {z['day']} | {z['missing']} | {z['classification']} |")
    lines += ['', '## Openstaande vrijgavevoorwaarden','']+[f'- {b}' for b in r['blockers']]
    lines += ['', 'Geen oordeel over winstgevendheid of onafhankelijke bevestiging. Geen Git-push of productie-uitrol. Licentie/redistributie en onafhankelijke volume-/tickvalidatie ontbreken. Kleine ontbrekende-volume-intervallen mogen no-trade-minuten zijn; zij bewijzen op zichzelf geen corrupte bron.','',
        '## Lokale reproduceerbaarheid','',
        '`python -m scripts.prepare_historical_contracts verify` controleert de freeze. `python -m scripts.prepare_historical_contracts run` maakt uitsluitend kwaliteits- en importuitvoer. `python -m scripts.prepare_historical_contracts replay` controleert byte-identieke dubbele import. Geen optie voor strategie-uitkomsten aanwezig.',
        '', 'Privé: artifacts/historical-preparation/contract-bars.parquet, active-bars.parquet, prior-context.json en volledige dag-/bronkwaliteitsregisters. Publiek geschikt: alleen research/historical-preparation-quality.json en public/data/historical-preparation.json met tellingen/vlaggen, geen minuutarrays. De spreadsheetrichtlijnen sturen bronbehoud en expliciete missing-values; geen brondata gerepareerd.','',
        '## Primaire bronnen','']+[f'- [{k}]({v})' for k,v in SOURCES.items()]
    return '\n'.join(lines)+'\n'


def replay():
    run()
    names = [RESULT,PUBLIC,REPORT]+sorted(OUT.glob('*'))
    before = {str(p.relative_to(ROOT)):sha(p) for p in names if p.is_file()}
    run()
    after = {str(p.relative_to(ROOT)):sha(p) for p in names if p.is_file()}
    if before != after:
        raise AssertionError('Nonidentical quality/import replay')
    result = dict(status='BYTE_IDENTICAL_QUALITY_ONLY_REPLAY',files_sha256=after,**verify(),signals_computed=False)
    dump(ROOT/'research/historical-preparation-verification.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','verify','run','replay']);args=p.parse_args()
    value=globals()[args.action]()
    if args.action in ('register','verify','replay'):print(json.dumps(value,indent=2))
