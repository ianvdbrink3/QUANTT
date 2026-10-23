"""Two authorized NQH24 exports: private intake only, never signal/outcome scoring."""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from datetime import datetime, date, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path('/Users/ianvandenbrink/Downloads')
RAW = ROOT / 'data/raw/independent-pilot'
SCHEMA = ['Time', 'Open', 'High', 'Low', 'Latest', 'Change', '%Change', 'Volume']
BLOCKS = [
    ('nqh24_intraday-1min_historical-data-10-22-2026.csv', '2024-01-22', '2024-02-02'),
    ('nqh24_intraday-1min_historical-data-10-22-2026-2.csv', '2024-02-05', '2024-02-16'),
]
CHI, NY = ZoneInfo('America/Chicago'), ZoneInfo('America/New_York')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tracked_hashes():
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    return {name: digest((ROOT/name).read_bytes()) for name in names if name and (ROOT/name).is_file()}


def inspect_file(source, start, end):
    payload = source.read_bytes()
    reader = csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
    if reader.fieldnames != SCHEMA:
        raise ValueError('Unexpected columns: ' + str(reader.fieldnames))
    times, footer, issues = [], [], Counter()
    for row in reader:
        if row['Time'].startswith('Downloaded from Barchart.com as of '):
            footer.append(row)
            if any(row.get(k) not in ('', None) for k in SCHEMA[1:]):
                issues['malformed_footer'] += 1
            continue
        try:
            local = datetime.strptime(row['Time'], '%Y-%m-%d %H:%M').replace(tzinfo=CHI)
            utc = local.astimezone(timezone.utc)
            if utc.astimezone(CHI) != local:
                issues['invalid_local_time'] += 1
            prices = [Decimal(row[k]) for k in ('Open', 'High', 'Low', 'Latest')]
            volume = Decimal(row['Volume'])
            if not all(p.is_finite() and p > 0 for p in prices):
                issues['invalid_price'] += 1
            elif any(p*4 != (p*4).to_integral_value() for p in prices):
                issues['off_tick_price'] += 1
            if all(p.is_finite() for p in prices):
                if prices[1] < max(prices) or prices[2] > min(prices):
                    issues['ohlc_incoherent'] += 1
            if not volume.is_finite() or volume <= 0 or volume != volume.to_integral_value():
                issues['invalid_volume'] += 1
            times.append(utc)
        except (ValueError, InvalidOperation, TypeError, KeyError):
            issues['unparseable_row'] += 1
    if len(footer) != 1:
        issues['footer_count'] += 1
    if not times:
        raise ValueError('Empty export')
    duplicate_count = len(times) - len(set(times))
    if duplicate_count:
        issues['duplicate_timestamps'] += duplicate_count
    if times != sorted(times):
        issues['not_ascending'] += 1
    observed = set(times)
    days = []
    day, last = date.fromisoformat(start), date.fromisoformat(end)
    while day <= last:
        if day.weekday() < 5:
            first = datetime.combine(day, time(9, 30), NY).astimezone(timezone.utc)
            expected = {first + timedelta(minutes=i) for i in range(390)}
            missing = sorted(expected-observed)
            days.append(dict(day=day.isoformat(), expected_rth_minutes=390,
                             present_rth_minutes=len(expected & observed),
                             missing_rth_minutes=len(missing),
                             data_quality_flag='RTH_GAP_UNEXPLAINED' if missing else 'RTH_LABELS_COMPLETE',
                             missing_rth_ny=[t.astimezone(NY).strftime('%H:%M') for t in missing]))
        day += timedelta(days=1)
    out_of_range = sum(not start <= t.astimezone(CHI).date().isoformat() <= end for t in times)
    if out_of_range:
        issues['source_civil_date_out_of_requested_range'] += out_of_range
    return dict(filename=source.name, sha256=digest(payload), bytes=len(payload),
                contract='NQH24', columns=reader.fieldnames, requested_start=start, requested_end=end,
                bars=len(times), footer_rows=len(footer), first_utc=min(times).isoformat(),
                last_utc=max(times).isoformat(), first_chicago=min(times).astimezone(CHI).isoformat(),
                last_chicago=max(times).astimezone(CHI).isoformat(),
                first_new_york=min(times).astimezone(NY).isoformat(),
                last_new_york=max(times).astimezone(NY).isoformat(),
                complete_rth_days=sum(not d['missing_rth_minutes'] for d in days),
                quality_issue_counts=dict(issues), days=days), observed


def run():
    before = tracked_hashes()
    records, sets = [], []
    for name, start, end in BLOCKS:
        source, target = DOWNLOADS/name, RAW/name
        ignored = subprocess.run(['git', 'check-ignore', '-q', str(target.relative_to(ROOT))], cwd=ROOT)
        if ignored.returncode != 0:
            raise ValueError('Raw target is not Gitignored')
        record, observed = inspect_file(source, start, end)
        payload = source.read_bytes()
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != payload:
            raise ValueError('Refusing to overwrite differing private raw bytes')
        if not target.exists():
            with target.open('xb') as stream:
                stream.write(payload)
        if digest(target.read_bytes()) != record['sha256']:
            raise ValueError('Private copy differs')
        record['private_copy'] = str(target.relative_to(ROOT))
        record['private_copy_byte_identical'] = True
        record['private_copy_gitignored'] = True
        records.append(record)
        sets.append(observed)
    if before != tracked_hashes():
        raise ValueError('Tracked baseline changed during intake')
    result = dict(status='TECHNICAL_INTAKE_ONLY_NO_HYPOTHESIS_TEST', as_of='2026-10-22',
                  source_url='https://www.barchart.com/futures/quotes/NQH24/historical-download',
                  source_timezone='America/Chicago', analysis_timezone='America/New_York',
                  timezone_basis='Barchart historical-download page help: futures timestamps in CT',
                  bar_interval_status='BAR_START_SUPPORTED_INTERNAL_ONLY',
                  tracked_files_unchanged=len(before), total_bars=sum(r['bars'] for r in records),
                  overlapping_timestamps=len(sets[0] & sets[1]),
                  complete_rth_days=sum(r['complete_rth_days'] for r in records),
                  missing_rth_minutes=sum(d['missing_rth_minutes'] for r in records for d in r['days']),
                  signals_computed=False, returns_computed=False, candidate_test_released=False,
                  licensing_status='EXISTING_TRIAL_EXPORT_NOT_REDISTRIBUTION_CLEARANCE', files=records)
    (ROOT/'research/nqh24-intake-pilot.json').write_text(json.dumps(result, indent=2)+'\n')
    lines = ['# NQH24 technische intakepilot', '',
             '22 oktober 2026. Twee 1-minuutexports via bestaande Barchart-toegang. Geen nieuwe aankoop, signaal-, cohort- of rendementsberekening. Geen onafhankelijke toets vrijgegeven.', '',
             '| Gevraagd blok | Bars | Volledige RTH-dagen | Ontbrekende RTH-minuten |',
             '|---|---:|---:|---:|']
    for r in records:
        lines.append(f"| {r['requested_start']} – {r['requested_end']} | {r['bars']} | {r['complete_rth_days']} | {sum(d['missing_rth_minutes'] for d in r['days'])} |")
    lines += ['', f"Totaal: {result['total_bars']} bars, {result['complete_rth_days']} volledige RTH-dagen. Overlap tussen bestanden: {result['overlapping_timestamps']} tijdstempels.", '',
              '## Integriteit en beperkingen', '',
              '- De bronbestanden zijn ongewijzigd gekopieerd naar `data/raw/independent-pilot/`, met byte-identieke SHA-256-controle en geverifieerde Gitignore. Downloads blijven intact.',
              '- Het lokale register `research/nqh24-intake-pilot.json` bevat bronhashes, kolommen, UTC/Chicago/New York-grenzen, afzonderlijke kwaliteitsbevindingen en de RTH-minuutdekking per dag.',
              '- RTH-dekking betekent uitsluitend 390 labels van 09:30 t/m 15:59 New York. Geen volledige Globex-kalendercertificering. Deze blokken bevatten geen DST-overgang of contractrollover. Geen bewijs van tick-level fills of onafhankelijk gevalideerde barconventie.',
              '- Elke export begint op maandag om 00:00 Chicago (01:00 New York). Het eerste overnight-prefix vanaf zondag 18:00 New York is daardoor niet volledig opgenomen. RTH-dekking en volledige sessiedekking zijn niet hetzelfde.',
              '- NQH24-identiteit berust op de geobserveerde contractpagina/exportkeuze en bestandsnaam. De CSV heeft geen contractkolom, bid/ask, ticks of orderfills. Volume omvat volgens de bronhulp alleen kwalificerende new-last-price trades, niet noodzakelijk alle CME-transactietypes.',
              '- Dit is een technische beschikbaarheidsproef, geen volledige onafhankelijke steekproef, ATR-opwarmgarantie of bevestigend onderzoek. Geen 15:00-cohort of uitkomsten berekend. De eerdere inferentie- en uitvoeringsblokkades blijven gelden.',
              '- Bestaande tijdelijke proeftoegang is geen permanent gratis abonnement. Exporttoegang is geen toestemming voor herpublicatie van ruwe marktdata. Geen accountwijziging, commit, push of deployment uitgevoerd.',
              f"- Alle {len(before)} bestaande gevolgde bestanden bleven byte-identiek, inclusief de bevroren specificatie en archiefbestanden.", '',
              '## Ontbrekende RTH-labels', '',
              'Onderstaande gaten zijn onverklaard: deze intake stelt niet vast of sprake is van een officiële handelsstop, afwezige kwalificerende transacties of een bronprobleem. Geen forward-fill of uitsluiting op basis van rendement.', '']
    for r in records:
        for d in r['days']:
            if d['missing_rth_minutes']:
                lines.append(f"- {d['day']}: {', '.join(d['missing_rth_ny'])} New York. Status `{d['data_quality_flag']}`.")
    lines += ['',
              '## Feitelijke bestandscontroles', '']
    for r in records:
        lines += [f"### {r['filename']}", '', f"- SHA-256: `{r['sha256']}`", f"- Chicago: {r['first_chicago']} t/m {r['last_chicago']}.",
                  f"- Kwaliteitsbevindingen (leeg = geen fout in de genoemde structurele controles): `{json.dumps(r['quality_issue_counts'], sort_keys=True)}`.", '']
    (ROOT/'docs/NQH24_INTAKE_PILOT.md').write_text('\n'.join(lines))
    assert tracked_hashes() == before
    print(json.dumps({k: result[k] for k in ('status', 'total_bars', 'complete_rth_days', 'missing_rth_minutes', 'overlapping_timestamps', 'tracked_files_unchanged')}))


if __name__ == '__main__':
    run()
