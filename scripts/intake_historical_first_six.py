"""Metadata-only receipt of six explicitly authorized Barchart downloads."""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
DOWNLOADS=Path('/Users/ianvandenbrink/Downloads')
RAW=ROOT/'data/raw/historical-replication-2019-2021'
SCHEMA=['Time','Open','High','Low','Latest','Change','%Change','Volume']
CHI=ZoneInfo('America/Chicago')
NY=ZoneInfo('America/New_York')
FILES=[
    'nqz18_intraday-1min_historical-data-10-22-2026.csv',
    'nqz18_intraday-1min_historical-data-10-22-2026-2.csv',
    'nqz18_intraday-1min_historical-data-10-22-2026-3.csv',
    'nqh19_intraday-1min_historical-data-10-22-2026.csv',
    'nqh19_intraday-1min_historical-data-10-22-2026-2.csv',
    'nqh19_intraday-1min_historical-data-10-22-2026-3.csv',
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot():
    names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    return {name:sha(ROOT/name) for name in names if name and (ROOT/name).is_file()}


def inspect(path, request):
    payload=path.read_bytes()
    reader=csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
    issues=Counter()
    if reader.fieldnames!=SCHEMA: issues['unexpected_columns']+=1
    stamps=[];footer=0
    for row in reader:
        label=row.get('Time','') or ''
        if label.startswith('Downloaded from Barchart.com as of '):
            footer+=1
            continue
        try:
            # Deliberately do not parse Open/High/Low/Latest/Volume numerically.
            stamp=datetime.strptime(label,'%Y-%m-%d %H:%M').replace(tzinfo=CHI)
        except ValueError:
            issues['invalid_timestamp_rows']+=1
            continue
        stamps.append(stamp)
        if not request['start_iso']<=stamp.date().isoformat()<=request['end_iso']:
            issues['outside_requested_source_civil_dates']+=1
        if any(row.get(field) in ('',None) for field in SCHEMA):
            issues['blank_fields']+=1
    if footer!=1: issues['footer_count_not_one']+=1
    if not stamps: issues['no_valid_bars']+=1
    if stamps!=sorted(stamps): issues['unordered_timestamps']+=1
    duplicates=len(stamps)-len(set(stamps))
    if duplicates: issues['duplicate_timestamps']+=duplicates
    if len(stamps)>=20000: issues['at_or_above_observed_record_cap']+=1
    gaps=Counter(int((b-a).total_seconds()/60) for a,b in zip(stamps,stamps[1:]) if b>a)
    first,last=(min(stamps),max(stamps)) if stamps else (None,None)
    result=dict(sequence=request['sequence'],filename=path.name,contract=request['contract'],
        requested_start=request['start_mmddyyyy'],requested_end=request['end_mmddyyyy'],
        sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),columns=reader.fieldnames,
        parsed_bars=len(stamps),footer_rows=footer,metadata_issue_counts=dict(issues),
        modal_positive_timestamp_spacing_minutes=gaps.most_common(1)[0][0] if gaps else None,
        first_chicago=first.isoformat() if first else None,last_chicago=last.isoformat() if last else None,
        first_utc=first.astimezone(timezone.utc).isoformat() if first else None,
        last_utc=last.astimezone(timezone.utc).isoformat() if last else None,
        first_new_york=first.astimezone(NY).isoformat() if first else None,
        last_new_york=last.astimezone(NY).isoformat() if last else None,
        requested_start_date_observed=any(t.date().isoformat()==request['start_iso'] for t in stamps),
        requested_end_date_observed=any(t.date().isoformat()==request['end_iso'] for t in stamps),
        numeric_ohlcv_parsed=False,source_url=request['source_url'])
    return result,set(stamps)


def stage(source,target):
    ignored=subprocess.run(['git','check-ignore','-q',str(target.relative_to(ROOT))],cwd=ROOT)
    if ignored.returncode: raise ValueError('Private target is not Gitignored')
    payload=source.read_bytes()
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=payload:
        raise ValueError('Refusing to overwrite different raw bytes')
    if not target.exists():
        with target.open('xb') as stream: stream.write(payload)
    if source.read_bytes()!=target.read_bytes(): raise ValueError('Raw copy not byte-identical')


def run():
    before=snapshot()
    plan_path=ROOT/'research/afternoon-historical-download-plan.json'
    requests=json.loads(plan_path.read_text())['rows'][:6]
    records=[];seen={};overlaps=0
    for filename,request in zip(FILES,requests):
        source=DOWNLOADS/filename
        if not filename.startswith(request['contract'].lower()+'_'):
            raise ValueError('Source contract/plan mismatch')
        if not source.is_file(): raise ValueError('Download not complete: '+filename)
        record,stamps=inspect(source,request)
        prior=seen.setdefault(request['contract'],set())
        overlap=len(prior & stamps);overlaps+=overlap;prior.update(stamps)
        record['within_contract_overlap_with_prior_files']=overlap
        target=RAW/filename
        stage(source,target)
        record['private_copy']=str(target.relative_to(ROOT))
        record['private_copy_gitignored']=True
        record['private_copy_byte_identical']=True
        records.append(record)
    if before!=snapshot(): raise ValueError('Tracked research changed during receipt')
    result=dict(status='SIX_DOWNLOADS_RECEIVED_METADATA_ONLY_NOT_VALIDATED_DATASET',
        as_of='2026-10-22',authorized_plan_sequences=[1,2,3,4,5,6],
        plan_sha256=sha(plan_path),requested_files=6,received_files=len(records),
        pending_full_plan_files=97,total_source_bars=sum(r['parsed_bars'] for r in records),
        within_contract_duplicate_overlap=overlaps,tracked_files_unchanged=len(before),
        metadata_flagged_files=sum(bool(r['metadata_issue_counts']) for r in records),
        numeric_ohlcv_parsed=False,signals_computed=False,cohort_computed=False,
        returns_computed=False,rollovers_computed=False,independent_test_released=False,
        paid_account_created=False,subscription_changed=False,publication=False,
        observed_account_daily_download_limit=250,observed_account_daily_used_after_batch=8,
        limits='Only headers/timestamps/row counts/footer/SHA256; no complete RTH/holiday/halt/expiration reconciliation or OHLCV numeric audit. No claim of high-quality trade-eligible days or execution evidence. Existing trial is not permanent free access.',
        files=records)
    registry=ROOT/'research/afternoon-historical-intake-batch01.json'
    registry.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    lines=['# Ontvangst eerste zes historische NQ-bestanden','',
        '22 oktober 2026. De expliciet genoemde zes exports zijn via de bestaande Barchart-sessie gedownload. Geen nieuwe aankoop, account, abonnementswijziging of uitkomstberekening. De overige 97 bestanden zijn niet opgehaald.','',
        '| # | Contract | Gevraagde start | Gevraagd einde | Minuutbars | Metadatavlaggen |',
        '|---:|---|---|---|---:|---|']
    for r in records:
        lines.append(f"| {r['sequence']} | {r['contract']} | {r['requested_start']} | {r['requested_end']} | {r['parsed_bars']} | {json.dumps(r['metadata_issue_counts'],sort_keys=True)} |")
    lines+=['',f"Totaal: **{result['total_source_bars']} bronbars**. Dit is niet het aantal unieke minuten van één actieve doorlopende reeks: NQZ18 en NQH19 overlappen bewust. Overlap binnen hetzelfde contract: **{overlaps}** tijdstempels. Twee verschillende contracten op hetzelfde tijdstip zijn geen duplicaat dat verwijderd moet worden.",'',
        '## Opslag en controle','',
        '- Originelen blijven in Downloads. Byte-identieke kopieën staan onder `data/raw/historical-replication-2019-2021/`. Gitignore is per bestand gecontroleerd. Niets naar GitHub of Vercel gestuurd.',
        '- Het lokale register `research/afternoon-historical-intake-batch01.json` bevat per bestand SHA-256, bestandsgrootte, kolommen, bars, footer, UTC/Chicago/New York-bereik en metadatawaarschuwingen. De eerder vergrendelde downloadlijst en het testvenster zijn niet gewijzigd.',
        '- Geen nieuwe OHLCV-waarden numeriek onderzocht. Alleen structuur en tijdstempels gecontroleerd; geen 15:00-waarden, cohort, rendement, volatiliteitsfeature, volumeroll of P&L berekend. De afgekeurde methoderonde blijft afgekeurd.',
        '- Geen claim over complete CME-sessies of trade-eligible dagen. Feestdagen, vroege sluitingen, bijzondere haltes en de aflopende NQZ18-expiratie moeten nog officieel worden verzoend. Een dun bestand van een aflopend contract is niet automatisch een mislukte download.',
        '- De zondagen zijn bewust inbegrepen. Eerste en laatste bronlabels zijn Chicago-civiele datums, niet noodzakelijk complete NY-handelsdagen. Het eerste maandagprefix begint om 00:00 Chicago, dus de voorafgaande zondagavond is daar niet compleet. Opwarming en uiteindelijke kwaliteit blijven afzonderlijke controles.',
        f"- Alle {len(before)} gevolgde bestanden bleven byte-identiek. De bestaande methode-/vensterlocks zijn apart verifieerbaar; de kandidaat blijft niet vrijgegeven.",'',
        '## Werkelijk ontvangen bronbereik (Chicago)','',
        '| # | Eerste label | Laatste label | Bytes |','|---:|---|---|---:|']
    for r in records: lines.append(f"| {r['sequence']} | {r['first_chicago']} | {r['last_chicago']} | {r['bytes']} |")
    lines+=['','De gebruikte spreadsheet-instructies beperken deze controle tot lezen en herleidbare bronregistratie. Er is geen werkblad herschreven, prijsserie aangevuld of CSV opnieuw geëxporteerd.','']
    (ROOT/'docs/NQ_HISTORICAL_INTAKE_BATCH01.md').write_text('\n'.join(lines))
    if before!=snapshot(): raise ValueError('Tracked research changed after report')
    print(json.dumps({k:result[k] for k in ('status','received_files','total_source_bars','metadata_flagged_files','within_contract_duplicate_overlap','tracked_files_unchanged')}))


if __name__=='__main__': run()
