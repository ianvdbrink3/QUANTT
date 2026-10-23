"""Locked local source comparison and count-only planning; no new model run."""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.afternoon_inference_round import partition
from scripts.edge_marathon.data import basic_frame
from scripts.oos_preparation.adapter import at, combine, load_csv, sha

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'research/independent-confirmation-readiness-protocol.json'
LOCK = ROOT / 'research/independent-confirmation-readiness-lock.json'
RESULT = ROOT / 'research/independent-confirmation-readiness-results.json'
REPORT = ROOT / 'docs/INDEPENDENT_CONFIRMATION_READINESS.md'
PRIVATE = ROOT / 'artifacts/independent-confirmation-readiness'
SOURCE_REGISTER = ROOT / 'artifacts/edge-marathon/source-register.json'


def write_json(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x' if exclusive else 'w') as handle:
        handle.write(json.dumps(value, indent=2, allow_nan=False) + '\n')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def source_records():
    records = json.loads(SOURCE_REGISTER.read_text())['records']
    names = {
        'Dataset_NQ_1min_2022_2025.csv',
        'nqh24_intraday-1min_historical-data-10-22-2026.csv',
        'nqh24_intraday-1min_historical-data-10-22-2026-2.csv',
    }
    result = sorted((r for r in records if r['filename'] in names), key=lambda r: r['filename'])
    if {r['filename'] for r in result} != names:
        raise ValueError('Missing exact existing pilot source; do not substitute dates/files')
    return result


def prepare():
    if LOCK.exists():
        verify()
        return
    if PROTOCOL.exists():
        raise ValueError('Partial registration exists; do not overwrite')
    protocol = dict(
        id='INDEPENDENT-CONFIRMATION-READINESS-20261022',
        status='TECHNICAL_SOURCE_AUDIT_AND_INFORMATION_PLANNING_ONLY',
        authorization='User accepted checking older negative evidence first and asked how to obtain120 scored observations.',
        sample=dict(start='2024-01-22', end='2024-02-16', contract='NQH24',
                    rule='All dates of both existing technical-pilot exports, not selected on returns or candidate membership.'),
        timestamps=dict(contract='America/Chicago, existing start-label interpretation',
                        generic='America/New_York, existing bar-end minus1minute normalization',
                        search=False),
        measurements=['all common RTH bars: volume, within-bar OC movement, high-low range, daily price-offset variation',
                      'unconditional raw15:00open to15:01close and15:14close anchor differences, no cohort or costs'],
        sources=[dict(filename=r['filename'], sha256=r['sha256']) for r in source_records()],
        planning=dict(input='Existing discovery selected dates ONLY; do not read PnL columns.',
                      method='Exactly8 equal weekday blocks with20 unscored weekdays between blocks; leftover tail not scored.',
                      min_total=120, min_each_block=8, lengths_weekdays=[260, 520, 783],
                      projection='Existing scored-event frequency, not a power calculation or guaranteed future frequency.'),
        boundaries=dict(candidate_v2_unchanged=True, original_v2_method='HAC5 with Holm2',
                        group_method='Separate conservative addendum/proposal, not a silently substituted v2 rule',
                        new_strategy_signals=False, new_strategy_pnl=False, new_confirmatory_test=False,
                        forward_feed_connected=False, forward_test_started=False, downloads=False,
                        purchases=False, git_publication=False, vercel_publication=False),
        interpretation='This is a same-date vendor/contract technical comparison, not statistical independent validation. '
                       'Existing older continuous negative evidence is retained;19 pilot days cannot certify all493 older days. '
                       'A fixed final test cannot be extended until120 or significance is reached.',
        method_source='https://www.princeton.edu/~umueller/tstat.pdf',
    )
    write_json(PROTOCOL, protocol, exclusive=True)
    names = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT
    ).decode().split('\0')
    protected = {name: sha(ROOT / name) for name in names if name and (ROOT / name).is_file()}
    write_json(LOCK, dict(protocol_sha256=sha(PROTOCOL), protected_files=protected,
                          source_register_sha256=sha(SOURCE_REGISTER)), exclusive=True)
    print(f'Locked local comparison and count-only plan; preserved {len(protected)} existing files.')


def verify():
    lock = json.loads(LOCK.read_text())
    if sha(PROTOCOL) != lock['protocol_sha256'] or sha(SOURCE_REGISTER) != lock['source_register_sha256']:
        raise ValueError('Registration or source register changed')
    for name, expected in lock['protected_files'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Existing file changed: ' + name)
    expected_sources = json.loads(PROTOCOL.read_text())['sources']
    records = source_records()
    if expected_sources != [dict(filename=r['filename'], sha256=r['sha256']) for r in records]:
        raise ValueError('Selected source identity changed')
    for record in records:
        for path in record['paths']:
            if sha(Path(path)) != record['sha256']:
                raise ValueError('Raw source bytes changed')
    return lock


def count_information(calendar, selected_dates):
    """One unique selected day per horizon; horizons are not extra observations."""
    if len(set(calendar)) != len(calendar) or calendar != sorted(calendar):
        raise ValueError('Unique chronological calendar required')
    selected = set(selected_dates)
    if len(selected) != len(selected_dates) or not selected <= set(calendar):
        raise ValueError('Unique selected dates must belong to calendar')
    groups, scored, width = partition(len(calendar))
    counts = [sum(calendar[int(i)] in selected for i in block) for block in groups]
    total = sum(counts)
    return dict(weekday_positions=len(calendar), block_width_weekdays=width,
                scored_weekday_positions=len(scored), guard_or_tail_positions=len(calendar)-len(scored),
                selected_days=len(selected), scored_selected_days=total,
                selected_in_guard_or_tail=len(selected)-total, per_block=counts,
                minimum_total_satisfied=total >= 120, minimum_each_satisfied=min(counts) >= 8,
                information_gate_satisfied=total >= 120 and min(counts) >= 8)


def planning():
    # Read existing decisions/dates, not prices or outcome columns; no strategy run.
    with (ROOT / 'artifacts/edge-marathon/discovery-trades.csv').open() as handle:
        selected = [r['day'] for r in csv.DictReader(handle) if r['model'] == 'AFTERNOON_V2_2']
    calendar = pd.bdate_range('2024-12-30', '2026-09-30').strftime('%Y-%m-%d').tolist()
    info = count_information(calendar, selected)
    old = json.loads((ROOT / 'artifacts/edge-marathon/discovery.json').read_text())
    expected = old['models']['AFTERNOON_V2_2']['inference']
    if info['per_block'] != expected['conservative_group_counts'] or info['scored_selected_days'] != expected['conservative_scored_events']:
        raise ValueError('Existing scored-count reproduction failed')
    frequency = info['scored_selected_days'] / info['scored_weekday_positions']
    rows = []
    for length in json.loads(PROTOCOL.read_text())['planning']['lengths_weekdays']:
        _, indexes, width = partition(length)
        rows.append(dict(approximate_years=length/260, weekday_positions=length,
                         scored_weekday_positions=len(indexes), guard_or_tail_positions=length-len(indexes),
                         projected_selected_days=len(indexes)*frequency,
                         projected_selected_per_block=width*frequency))
    window = json.loads((ROOT / 'research/afternoon-historical-window.json').read_text())
    plan = json.loads((ROOT / 'research/afternoon-historical-download-plan.json').read_text())
    intake = json.loads((ROOT / 'research/afternoon-historical-intake-batch01.json').read_text())
    received = set(intake['authorized_plan_sequences'])
    pending = [row for row in plan['rows'] if row['sequence'] not in received]
    return dict(discovery_count_reproduced=info, complete_rth_days=old['complete_days'],
                selected_per_complete_rth_day=len(selected)/old['complete_days'],
                selected_per_scored_weekday=frequency, projections=rows,
                projection_limit='Historical frequency only; holidays and quality failures already affect that frequency. '
                                 'Future quality, selection and dependence may differ.120 is an information floor, not80% power or guaranteed independence. '
                                 'These are alternative planning lengths, not rolling testing opportunities or an adopted forward endpoint.',
                original_v2_method_unchanged=True, existing_109_are_discovery_not_new_confirmation=True,
                historical_route=dict(start=window['start'], end=window['end'],
                                      scored_weekdays=window['scored_weekdays'], planned_exports=len(plan['rows']),
                                      first_batch_received_exports=intake['received_files'], pending_exports=len(pending),
                                      next_three_requests=pending[:3],
                                      status='MISSING_DATA_NOT_NEW_OUTCOME_RELEASE',
                                      access_disclosure='2019Jan2-Jan11 already inspected during authorized marathon; original window retained, not called wholly blind.'),
                forward_route=dict(status='NOT_STARTED_NO_VERIFIED_FEED_OR_FINAL_CALENDAR',
                                   requirements=['lawful existing feed without new charges', 'immutable future start/end dates and calendar blocks',
                                                 'warmup, rollovers, quality and full record of all scheduled dates',
                                                 'timestamped cohort decision before outcome; both horizons and separate execution evidence'],
                                   stopping='One registered final endpoint; insufficient information stays inconclusive. No extension to120.'))


def describe(values):
    values = np.asarray(values, float)
    return dict(n=len(values), exact_fraction=float(np.isclose(values, 0, atol=1e-8, rtol=0).mean()),
                median_abs_points=float(np.median(abs(values))),
                p90_abs_points=float(np.quantile(abs(values), .9)), max_abs_points=float(abs(values).max()))


def source_comparison():
    p = json.loads(PROTOCOL.read_text())['sample']
    records = source_records()
    generic_row = next(r for r in records if r['filename'].startswith('Dataset_'))
    generic = basic_frame(generic_row['paths'][0], 'GENERIC')
    contract = combine([load_csv(r['paths'][0], p['contract']) for r in records
                        if r['filename'].lower().startswith('nqh24_')], p['start'], p['end'])
    common = generic.index.intersection(contract.index)
    clocks = common.tz_convert('America/New_York').strftime('%H:%M')
    common = common[(clocks >= '09:30') & (clocks < '16:00')]
    a, b = generic.loc[common], contract.loc[common]
    minute_oc = (a.close-a.open).to_numpy() - (b.close-b.open).to_numpy()
    ranges = (a.high-a.low).to_numpy() - (b.high-b.low).to_numpy()
    offsets = pd.DataFrame(dict(day=b.trade_date.to_numpy(), offset=(a.close-b.close).to_numpy()))
    offset_ranges = offsets.groupby('day').offset.agg(lambda x: float(x.max()-x.min()))
    anchors, quality = [], []
    for day in pd.bdate_range(p['start'], p['end']).strftime('%Y-%m-%d'):
        grid = pd.date_range(at(day, '09:30'), at(day, '16:00'), freq='min', inclusive='left')
        missing_a = len(grid.difference(generic.index)); missing_b = len(grid.difference(contract.index))
        quality.append(dict(day=day, generic_missing_rth=missing_a, contract_missing_rth=missing_b,
                            common_full_rth=missing_a == 0 and missing_b == 0))
        t = at(day, '15:00')
        for minutes, end in [(2, '15:01'), (15, '15:14')]:
            u = at(day, end)
            if any(v not in frame.index for frame in (generic, contract) for v in (t, u)):
                continue
            ga = float(generic.at[u, 'close']-generic.at[t, 'open'])
            gb = float(contract.at[u, 'close']-contract.at[t, 'open'])
            anchors.append(dict(day=day, minutes=minutes, generic_raw_move=ga, contract_raw_move=gb,
                                generic_minus_contract=ga-gb))
    result = dict(status='LIMITED_OLDER_SAME_DATE_SOURCE_COMPARISON_COMPLETED_NOT_CONFIRMATION',
                  window=p, common_rth_minutes=len(common), common_days=int(b.trade_date.nunique()),
                  complete_common_rth_days=sum(r['common_full_rth'] for r in quality),
                  volume_exact_fraction=float((a.volume.to_numpy() == b.volume.to_numpy()).mean()),
                  minute_oc_difference=describe(minute_oc), minute_range_difference=describe(ranges),
                  constant_daily_close_offset_fraction=float(np.isclose(offset_ranges, 0).mean()),
                  maximum_intraday_close_offset_variation_points=float(offset_ranges.max()),
                  anchor_difference={str(n): describe([r['generic_minus_contract'] for r in anchors if r['minutes'] == n])
                                     for n in (2, 15)}, quality=quality,
                  no_cohort_reselected=True, no_new_strategy_pnl=True,
                  limitation='Only existing NQH24 pilot overlap, not all493 older complete RTH days. '
                             'No contract-level2023 coverage, full historical roll chain, independent tick/BBO source or provenance certification. '
                             'Agreement on this pilot cannot clear the older negative result; disagreement cannot justify discarding it without diagnosis.')
    write_json(PRIVATE / 'anchor-comparison.json', anchors)
    return result


def render(result):
    p = result['information_planning']; i = p['discovery_count_reproduced']; c = result['source_comparison']
    lines = [
        '# Onafhankelijke bevestiging: broncontrole en steekproefplanning', '',
        '## Uitgevoerd', '',
        'Lokale technische bronvergelijking op vooraf vastgelegde bestaande pilotbestanden, plus reproductie van waarnemingstellingen. '
        'Geen nieuwe strategie-, cohort- of P&L-run, aankoop, download, Git-push of productiepublicatie. Kandidaat v2 blijft byte-identiek.', '',
        '## Wat telt als één van de120?', '',
        'Eén unieke dag met de bevroren14:30-UP-selectie, geldige vooraf bekendeATR14 en geldige gezamenlijke horizondata. '
        'De2m- en15m-uitkomst zijn twee gekoppelde toetsen, niet twee waarnemingen. '
        'Alleen geselecteerde dagen binnen de8 vooraf vastgelegde meetblokken tellen voor de conservatieve informatiepoort. '
        'Tussen de blokken blijven7×20 weekdagen ongescoord; ook de vaste reststaart telt niet. '
        'Niet-geselecteerde dagen krijgen geen verzonnen trade. Hun nul-momentscore in de kalender is geen geselecteerde nulrendementswaarneming.', '',
        f'Bestaande ontdekking: {p["complete_rth_days"]} volledigeRTH-dagen, {i["weekday_positions"]} weekdagposities, '
        f'{i["selected_days"]} geselecteerde dagen, {i["scored_selected_days"]} gescoorde dagen, '
        f'{i["selected_in_guard_or_tail"]} geselecteerde dagen in gaps/reststaart. '
        f'Blokaantallen: {i["per_block"]}. Minimaal120 totaal én8 per blok vereist. '
        'Deze109 blijven ontdekkingsdata: elf nieuwe dagen erbij zijn geen onafhankelijke bevestiging.', '',
        '## Hoe lang verzamelen?', '',
        f'Waargenomen selectie: {100*p["selected_per_complete_rth_day"]:.2f}% per volledigeRTH-dag; '
        f'binnen de meetblokken {100*p["selected_per_scored_weekday"]:.2f}% per weekdagpositie. '
        'Onderstaande planning gebruikt alleen bestaande selectiedatums, geen nieuwe rendementen.', '',
        '| Vooraf gekozen venster (raming) | Weekdagen | Gescoorde weekdagposities | Verwachte geselecteerde dagen | Verwacht per blok |',
        '|---|---:|---:|---:|---:|',
    ]
    for r in p['projections']:
        lines.append(f'| circa{r["approximate_years"]:.1f} jaar | {r["weekday_positions"]} | '
                     f'{r["scored_weekday_positions"]} | {r["projected_selected_days"]:.1f} | '
                     f'{r["projected_selected_per_block"]:.1f} |')
    lines += ['', 'Dit zijn frequentieramingen, geen powerberekening, zekerheid of formeel gekozen forward-einddatum. '
              'Twee jaar ligt qua verwachte aantallen slechts beperkt boven de120-grens. '
              'Drie jaar geeft meer informatieruimte, maar ook120 waarnemingen bewijzen geen edge en garanderen geen80%power. '
              'Niet doorlopen totdat120 of significantie verschijnt. Bij het vaste eindpunt kan DATA_INSUFFICIENT de juiste uitkomst zijn.', '',
              '## Status van de toetsmethode', '',
              'De oorspronkelijke v2-specificatie gebruiktHAC5 metHolm2. De120-grens hoort bij de afzonderlijke conservatieve gegroepeerde methode. '
              'Die grens is een projectkeuze, geen universele statistische wet. De8 groepen zijn de inferentie-eenheden. '
              'Gaps maken dagen niet aantoonbaar onafhankelijk. De factor1,25 uit de tweede synthetische ronde is een voorstel en wijzigt v2 niet automatisch. '
              'Een toekomstige vrijgave moet vooraf aangeven welke methode formeel beslist, met behoud van alle bestaande registraties.', '',
              '[Primaire methodologische bron: Ibragimov en Müller](https://www.princeton.edu/~umueller/tstat.pdf). '
              'De geldigheid vraagt passende onafhankelijkheids-/normaliteitsbenaderingen tussen groepen; ons specifieke120-minimum volgt niet uit die publicatie.', '',
              '## Oudere bronvergelijking', '',
              f'Alle bestaandeNQH24-pilotdatums {c["window"]["start"]} t/m {c["window"]["end"]}: '
              f'{c["common_days"]} dagen met gedeeldeRTH-minuten, {c["complete_common_rth_days"]} volledig gemeenschappelijkeRTH-dagen, '
              f'{c["common_rth_minutes"]} gemeenschappelijke minuten. '
              'GenericET-labels zijn uitsluitend met de al vastgelegde min1minuut vertaald; BarchartCT blijft op de bestaande startlabelconventie. Geen tijdverschuivingszoektocht.', '',
              '| Vergelijking generic minusNQH24 | Aantal | Exact gelijk | Mediane absolute afwijking (pt) | P90 absolute afwijking (pt) | Max (pt) |',
              '|---|---:|---:|---:|---:|---:|']
    measures = [('Minuut open-close', c['minute_oc_difference']), ('Minuut high-low', c['minute_range_difference'])]
    measures += [(f'Onvoorwaardelijk15:00→{end}', c['anchor_difference'][str(n)]) for n, end in [(2, '15:01close'), (15, '15:14close')]]
    for label, row in measures:
        lines.append(f'| {label} | {row["n"]} | {100*row["exact_fraction"]:.2f}% | '
                     f'{row["median_abs_points"]:.3f} | {row["p90_abs_points"]:.3f} | {row["max_abs_points"]:.3f} |')
    lines += ['', f'Volume exact gelijk: {100*c["volume_exact_fraction"]:.2f}%. '
              f'Constante dag-offset in closes: {100*c["constant_daily_close_offset_fraction"]:.2f}% van gedeelde dagen. '
              f'Grootste intradayvariatie in de prijs-offset: {c["maximum_intraday_close_offset_variation_points"]:.3f}pt.', '',
              c['limitation'], '',
              'Dit is geen bevestiging of herselectie van de15:00-kandidaat. De eerdere negatieve oudere uitkomst blijft staan. '
              'Ontbrekend: volledige contractgeïdentificeerde brondekking voor het oudere tegenbewijs en verifieerbare roll-/publicatieherkomst.', '',
              '## Twee routes, strikt gescheiden', '',
              '1. Historische replicatie2019–2021: bestaande vaste kalender behouden;103 geplandeexports,6 in de eerste batch ontvangen,97 nog ontbrekend volgens het oorspronkelijke register. '
              'Die aantallen zijn geen actuele bevestiging van gratis exportrechten. Januari2019 is deels al ingezien en blijft expliciet gemeld. '
              'Geen nieuwe eindtoets gestart. De volledige kalender heeft640 gescoorde weekdagposities, geen640 gegarandeerde events.', '',
              '2. Prospectieve schaduwtest: nog niet gestart. Eerst een rechtmatige bestaande feed zonder nieuwe kosten, een onveranderlijke toekomstige start/einddatum, '
              'vaste kalenderblokken en vooraf vastgelegde formele meetlat. Cohortbesluit vóór de uitkomst vastleggen, beide horizons meten, '
              'uitvoeringsgegevens apart van bar-ankers houden. Geen echte orders of prijsfeed gekoppeld in deze ronde.', '',
              'Gebruik geenCFD,ES, extra horizons of dubbele leverancierskopieën omNQ-dagen aan te vullen. '
              'Historische en forwardresultaten blijven aparte bewijslagen; niet achteraf samenvoegen om een drempel te halen.', '',
              '## Eerstvolgende drie bestaande historische downloadblokken', '',
              '| Contract | Vanaf (MM/DD/YYYY) | Tot en met |', '|---|---|---|']
    for r in p['historical_route']['next_three_requests']:
        lines.append(f'| {r["contract"]} | {r["start_mmddyyyy"]} | {r["end_mmddyyyy"]} |')
    lines += ['', 'Alleen ophalen als bestaande exportrechten dit zonder aankoop/verlenging toestaan. '
              'Deze lijst voltooit het oude vaste venster en is niet automatisch de aanvullende brondekking voor het negatieve2023–2024-tegenbewijs.', '',
              '## Controle', '',
              f'{result["preserved_files"]} bestaande bestanden voor en na de run opSHA-256 gelijk; '
              'de bestaande530-teststand en rapporten worden niet overschreven. Nieuwe tests/resultaten zijn aanvullend. '
              'Protocol en bronhashes zijn vóór deze beperkte vergelijking vastgelegd. Private ankerdetails blijven onderartifacts/.', '']
    return '\n'.join(lines)


def run():
    lock = verify()
    result = dict(status='LOCAL_READINESS_COMPLETED_INDEPENDENT_CONFIRMATION_NOT_OBTAINED',
                  protocol_sha256=sha(PROTOCOL), preserved_files=len(lock['protected_files']),
                  information_planning=planning(), source_comparison=source_comparison(),
                  candidate_unchanged=True, independent_test_started=False)
    verify()
    write_json(RESULT, result)
    REPORT.write_text(render(result))
    print(json.dumps(dict(status=result['status'],
                          counts=result['information_planning']['discovery_count_reproduced'],
                          source_comparison=result['source_comparison']['anchor_difference']), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'verify'])
    args = parser.parse_args()
    {'prepare': prepare, 'run': run, 'verify': verify}[args.action]()
