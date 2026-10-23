"""Metadata-only sample/download registration. Never opens a market CSV."""
import argparse
import hashlib
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from scripts.afternoon_inference_round import ROOT, PROTOCOL, LOCK, partition, sha, dump, verify_lock

WINDOW = ROOT/'research/afternoon-historical-window.json'
PLAN = ROOT/'research/afternoon-historical-download-plan.json'
WINDOW_LOCK = ROOT/'research/afternoon-historical-window-lock.json'


def expiry(year, month):
    day = date(year, month, 1)
    while day.weekday() != 4:
        day += timedelta(days=1)
    return day+timedelta(days=14)


def chunks(start, end):
    start, end = date.fromisoformat(start), date.fromisoformat(end)
    rows = []
    while start <= end:
        last = min(start+timedelta(days=13), end)
        rows.append((start, last))
        start = last+timedelta(days=1)
    return rows


def downloads():
    scopes = [('NQZ18', '2018-11-19', '2018-12-21', 'WARMUP_ONLY')]
    for year in (2019,2020,2021):
        for month, letter in ((3,'H'),(6,'M'),(9,'U'),(12,'Z')):
            py, pm = (year-1,12) if month == 3 else (year,month-3)
            start = expiry(py,pm)-timedelta(days=18)
            scopes.append((f'NQ{letter}{year%100:02}',str(start),str(expiry(year,month)), 'CONTRACT_OVERLAP_AND_FIXED_WINDOW'))
    scopes.append(('NQH22','2021-11-29','2021-12-31','DECEMBER2021_ROLL_ONLY_NO2022_OUTCOMES'))
    rows = []
    for contract, start, end, role in scopes:
        for a,b in chunks(start,end):
            rows.append(dict(sequence=len(rows)+1, contract=contract, start_iso=str(a), end_iso=str(b),
                             start_mmddyyyy=a.strftime('%m/%d/%Y'),end_mmddyyyy=b.strftime('%m/%d/%Y'),
                             role=role, frequency='Intraday',minutes=1,order='Ascending Date',
                             total_volume_and_open_interest=False, nearby=False,
                             source_url=f'https://www.barchart.com/futures/quotes/{contract}/historical-download'))
    return rows


def evidence():
    inventory = json.loads((ROOT/'artifacts/independent-data-inventory.json').read_text())
    unique = list({r['sha256']:r for r in inventory['records']}.values())
    minute = [r for r in unique if ('1min' in r['filename'].lower() or '1_minute' in r['filename'].lower()) and r.get('first_source_timestamp')]
    intraday = [r for r in unique if not any(x in r['filename'].lower() for x in ('daily','weekly','monthly','1day')) and r.get('first_source_timestamp')]
    requested = {x['contract'].lower() for x in downloads()}
    existing = sorted(p.name for p in Path('/Users/ianvandenbrink/Downloads').glob('nq*_*.csv') if p.name.split('_')[0].lower() in requested)
    audit = ROOT.parent/'reports/NQ-data-audit-2026-10-19.md'
    return dict(scope='Prior metadata inventory, audited report, local source-code/report references and current Downloads filenames. Not a full computer/chat/access-history forensic proof.',
                inventory_sha256=sha(ROOT/'artifacts/independent-data-inventory.json'),
                prior_audit_sha256=sha(audit), earliest_prior_minute_source_label=min(r['first_source_timestamp'] for r in minute),
                earliest_prior_intraday_source_label=min(r['first_source_timestamp'] for r in intraday),
                prior_daily_weekly_monthly_access=True,
                known_candidate_specific_outcome_evidence_in_window=False,
                absolute_non_exposure_proven=False, prospective_data=False,
                requested_contract_files_in_downloads=existing,
                nqh24_pilot_excluded=True, consumed_435_days_excluded=True,
                new_csv_content_parsed=False, new_market_outcomes_read=False)


def register():
    verify_lock()
    p = json.loads(PROTOCOL.read_text())
    days = pd.bdate_range(p['window']['start'],p['window']['end']).strftime('%Y-%m-%d').tolist()
    if len(days) != 783:
        raise ValueError('Locked weekday planning grid changed')
    blocks, scored, width = partition(len(days))
    plan = downloads()
    inventory_evidence = evidence()
    window = dict(id='NQ-AFTERNOON-HISTORICAL-REPLICATION-2019-2021',
        status='DATE_WINDOW_FIXED_OUTCOME_RELEASE_BLOCKED',
        registered_on='2026-10-22', start=days[0], end=days[-1], warmup_start=p['window']['warmup_start'],
        discovery_overlap=False, classification=p['window']['classification'],
        independence_evidence=inventory_evidence, calendar_weekdays=783,
        complete_rth_days=None, technical_eligible_days=None, selected_event_days=None,
        unknown_count_reason='No requested-year source CSV is parsed and official calendars/quality/rollovers have not been verified; weekdays are NOT exchange sessions or eligible days.',
        inference_blocks=[dict(group=j+1,start=days[int(block[0])],end=days[int(block[-1])],weekdays=width) for j,block in enumerate(blocks)],
        scored_weekdays=len(scored), guard_or_tail_weekdays=len(days)-len(scored),
        scored_date_hash=hashlib.sha256('\n'.join(days[int(i)] for i in scored).encode()).hexdigest(),
        interpretation='No zero-PnL fabrication: unselected/closed/failed-quality slots are zero moment-scores, not selected zero-return observations.',
        unchanged_candidate='research/afternoon-candidate-v2.json', candidate_sha256=sha(ROOT/'research/afternoon-candidate-v2.json'),
        method_addendum='research/afternoon-method-round-protocol.json',method_protocol_sha256=sha(PROTOCOL),
        costs=dict(roundtrip_usd=24.5,net_points_deduction=1.225,point_value_usd=20),
        required_quality=dict(timezone='America/Chicago source -> UTC -> America/New_York',
            interval='BAR_START_SUPPORTED_INTERNAL_ONLY',
            strict_shared_sample='Require complete normal RTH09:30-15:59 plus09:29 boundary, all selection and both horizon labels; valid prior ATR14. Official early-close sessions are not vendor corruption but cannot enter the full-RTH shared sample.',
            warmup='Only 14 prior valid complete RTH true ranges in the frozen continuous point-in-time context; no current or future returns. Carry history across guard dates; no artificial reset at a statistical block boundary.',
            official_calendar='MUST_VERIFY_BEFORE_OUTCOME_RELEASE; 2018 warmup and2019-2021 holidays, early closes, extraordinary halts and both DST transitions each year. Do not classify every weekday as an exchange session.',
            raw='Individual unadjusted contracts. Deduplicate identical contract/timestamp bars; conflicting overlaps fail. Never fill missing OHLCV or move a timestamp to improve an effect.',
            roll=p['window']['roll'], minimum_information='>=120 selected common observations total and >=8 in each fixed inference block; no event-count extension.',
            hashes='Lock all sourceSHA256, calendar, volume decisions, partitions, quality and adaptation-parity BEFORE any new outcomes are scored.'),
        no_peeking=p['window']['stop'], market_outcomes_computed=False, candidate_test_released=False,
        publication_authorized=False)
    plan_obj=dict(status='INSTRUCTIONS_ONLY_NOT_DOWNLOADED', frequency='Intraday 1 minute',
                  pricing='Existing trial entitlement only; no purchase, renewal, account or quota promise.',
                  max_records_observed=20000, vendor_help_older_limit=10000,
                  records_limit_note='Observed current form on22Oct2026 showed20000; old2020help says10000. If actual account allows only10000, stop and version the acquisition split before use; do not accept truncated exports.',
                  requested_files=len(plan), contracts=len({x['contract'] for x in plan}),
                  reason_for_sunday_ends='Inclusive14calendar-day blocks include Sunday evening Globex minutes. Monday-Friday-only exports would miss the Sunday session prefix.',
                  coverage='Requests through nominal third-Friday expiry provide old/new overlap, NOT a prespecified rollover date. Final H22 stops31Dec2021. First warmup export starts19Nov2018; its missing Sunday prefix is not a test-day omission.',
                  rows=plan)
    if WINDOW_LOCK.exists():
        verify()
        print('Existing window/download lock verified; no redefinition.')
        return
    if WINDOW.exists() or PLAN.exists():
        raise ValueError('Partial registration exists; do not overwrite')
    dump(WINDOW,window); dump(PLAN,plan_obj)
    write_report(window,plan_obj)
    files=[WINDOW,PLAN,ROOT/'docs/AFTERNOON_HISTORICAL_WINDOW.md',ROOT/'docs/NQ_HISTORICAL_DOWNLOAD_LIST.md',Path(__file__)]
    dump(WINDOW_LOCK,dict(status='WINDOW_AND_ACQUISITION_PLAN_LOCKED_NO_OUTCOMES',
         files_sha256={str(f.relative_to(ROOT)):sha(f) for f in files},
         candidate_test_released=False,absolute_independence_certified=False))
    verify()
    print(json.dumps(dict(weekdays=len(days),scored_weekdays=len(scored),files=len(plan),contracts=plan_obj['contracts'],candidate_test_released=False)))


def write_report(w,p):
    e=w['independence_evidence']
    lines=['# Vastgelegd historisch replicatievenster', '',
        '22 oktober2026. Alleen stap1 en2. Geen nieuwe uitkomsten, cohortselectie, backtest, download of publicatie.', '',
        f"Vast venster: **{w['start']} t/m {w['end']}**. Opwarming vanaf **{w['warmup_start']}**. Classificatie: `{w['classification']}`. Status: `{w['status']}`.", '',
        '## Waarom deze periode', '',
        f"De oude inventaris begint voor intradaylabels bij {e['earliest_prior_intraday_source_label']}, voor minuutlabels bij {e['earliest_prior_minute_source_label']}. Daarmee ligt2019-2021 vóór alle daarin aangetroffen intradaybestanden. De technische NQH24-pilot en alle435 ontdekkingsdagen tellen niet mee. De grootst gemelde oude minuutreeks begint pas26december2022, ongeacht de bestandsnaam2022-2025.", '',
        '**Niet overclaimen:** oudere dag-, week- en maanddata waren al aanwezig en onderzocht. In de geïnspecteerde lokale stukken is geen specifieke15:00-kandidaatuitkomst over2019-2021 aangetroffen. Dat is geen sluitend bewijs van nul eerdere inzage op de hele computer/in alle chats. Dit is historische out-of-period replicatie, geen prospectieve forwardproef en geen gecertificeerd onaangeraakte dataset. Bij bewijs van eerdere kandidaat-specifieke inzage vervalt bevestigende interpretatie; niet automatisch een ander gunstig venster kiezen.', '',
        '## Stopregel en informatie', '',
        f"De kalender telt{w['calendar_weekdays']} maandag-vrijdagposities. Dat is nadrukkelijk geen claim over het aantalCME-sessies, schone/eligible dagen of events. Die aantallen blijven onbekend totdat een alleen-kwaliteit-intake met officiële kalender gereed is. De nieuwe blokmeetlat reserveert{w['scored_weekdays']} weekdagposities voor uitkomsten en{w['guard_or_tail_weekdays']} voor vooraf gekozen tussenruimte/staart. Daardoor verandert de toetssteekproef expliciet ten opzichte vanv2; geen stille herweging van resultaten.", '',
        '| Blok | Vanaf | T/m | Weekdagposities |','|---|---|---|---:|']
    for b in w['inference_blocks']:
        lines.append(f"| {b['group']} | {b['start']} | {b['end']} | {b['weekdays']} |")
    lines += ['', 'Tussen blokken liggen telkens20 weekdagposities zonder bevestigende uitkomst. Die dagen mogen wel causale ATR-opwarming leveren. Minimaal120 geselecteerde gemeenschappelijke observaties totaal en8 per blok; andersDATA_INSUFFICIENT, geen verlenging. De kandidaatregels, twee horizons en1,225pt frictie blijven gelijk. Het historische effect is geen verwachte toekomstige winst.', '',
        '## Vrijgavepoort', '',
        '1. Synthetische methoderonde beoordelen. Een falende kalibratie betekent géén methodeswitch en géén eindtoets. Een geslaagde benchmark is geen universele5%-garantie.',
        '2. Eerst alle contract-CSV’s en bronhashes registreren, officiële kalender/haltes/DST verzoenen, volume-rollovers zonder uitkomsten vastleggen en parity met de oude kandidaat bewijzen. Geen parameterwijziging.',
        '3. Beide horizons gebruiken dezelfde volledigeRTH-dagen. Officiële verkorte dagen zijn niet corrupt, maar niet geschikt voor deze volledigeRTH-steekproef. Geen forward-fill, vervangende datum of gunstige endpointverschuiving.',
        '4. Maak vóór uitkomstvrijgave een definitieve bron-/kwaliteitslock. Eén afzonderlijke expliciete vrijgave is nog nodig. Geen tussentijdseP&L, stop zodra significant, uitbreiding bij tegenvaller of samenvoegen met de435 ontdekkingsdagen.',
        '5. BAR_START_SUPPORTED_INTERNAL_ONLY en ontbrekend tick/BBO/fill-bewijs blijven staan. Zelfs statistische ondersteuning valideert geen gegarandeerd uitvoerbaar/live winstgevend model.', '',
        'Exacte kwaliteitseisen en stopregel: `research/afternoon-historical-window.json`. Exacte bestandslijst: `docs/NQ_HISTORICAL_DOWNLOAD_LIST.md` en machineleesbareJSON. Deze registratie wijzigtv2/de huidige pointer niet en publiceert niets.', '']
    (ROOT/'docs/AFTERNOON_HISTORICAL_WINDOW.md').write_text('\n'.join(lines))
    d=['# NQ-contractbestanden om op te halen', '',
       f"Plan voor2019-2021 plus opwarming/rolloveroverlap: **{p['requested_files']} CSV-downloads, {p['contracts']} afzonderlijke contracten**. Dit is een bestellijst, geen uitgevoerde download of garantie van beschikbare historie/quotum.", '',
       '## Instellingen voor ieder bestand', '',
       '- Gebruik Barchart Historical Data van het genoemde contract. **Intraday**, **min1**, **Ascending Date**.',
       '- Geen Nearby/continuous, geen back-adjustment, **Total Volume and Open Interest uit** (contractvolume nodig). Volledige beschikbare sessies, geenRTH-filter.',
       '- Datums hieronder zijn**MM/DD/YYYY**, inclusief beide grenzen. Blokken eindigen zo mogelijk zondag om de zondagavondhandel mee te nemen. Kort laatste blok per contract is bewust.',
       '- Bewaar de origineleCSV inclusief footer. Niet inExcel opslaan/knippen. Bronhashes bij intake, ruwe data nooit naarGitHub/Vercel.',
       '- Alleen bestaande toegang zonder nieuwe kosten. Stop bij betaalverzoek, verlopen toegang, daglimiet of afgekapt bestand. Geen abonnement starten/verlengen.20000records was de geobserveerde formulierlimiet; de oudereBarchart-help noemt10000. Bij afwijkend accountlimiet eerst het intakeplan versiegewijs splitsen.',
       '- De eerste drie bestanden zijn uitsluitend opwarming. DeNQH24-bestanden zijn technische pilot en vervangen geen blok uit dit plan.', '',
       '## Complete vaste downloadlijst', '',
       '| # | Contract | Start | Einde |', '|---:|---|---|---|']
    for row in p['rows']:
        d.append(f"| {row['sequence']} | [{row['contract']}]({row['source_url']}) | {row['start_mmddyyyy']} | {row['end_mmddyyyy']} |")
    d += ['', '## Aantal per contract', '', '| Contract | Bestanden |','|---|---:|']
    for contract,n in Counter(x['contract'] for x in p['rows']).items(): d.append(f'| {contract} | {n} |')
    d += ['', 'Het aanvragen tot de nominale expiratievrijdag is een acquisitiegrens, geen vooraf gekozen kalenderrollover. De daadwerkelijke switch volgt pas uit de vastgelegde volumeroute. NQH22 levert alleen december2021 tot12/31/2021, geen2022-toetsdata. Feestdagen/vroege sluitingen worden vóór enig uitkomstgebruik afzonderlijk officieel geverifieerd.', '',
          'Bron: [Barchart historische-downloadhulp](https://help.barchart.com/support/solutions/articles/242748-how-can-i-download-historical-data-). Bestaande geobserveerde accountrechten zijn tijdelijk. Geen toezegging dat alle gevraagde oudere contracten niet-leeg beschikbaar zijn.', '']
    (ROOT/'docs/NQ_HISTORICAL_DOWNLOAD_LIST.md').write_text('\n'.join(d))


def verify():
    verify_lock()
    lock=json.loads(WINDOW_LOCK.read_text())
    for name,digest in lock['files_sha256'].items():
        if sha(ROOT/name)!=digest: raise ValueError('Fixed-window artifact changed: '+name)
    return lock


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    if args.verify: verify();print('Window and download instructions byte-identical; outcomes not released.')
    else: register()
