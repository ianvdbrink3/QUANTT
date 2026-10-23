"""Metadata-only inventory. No numeric OHLCV, signals or candidate outcomes."""
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

from scripts.inventory_nq_dates import inspect

ROOT = Path(__file__).resolve().parents[1]


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def extra_dates(path, key):
    values = pd.read_csv(path, usecols=[key])[key]
    fmt = '%m/%d/%Y %H:%M' if key.lower() == 'timestamp et' else 'mixed'
    valid = pd.to_datetime(values, format=fmt, errors='coerce').dropna()
    days = valid.dt.strftime('%Y-%m-%d')
    return dict(rows_before_consumed=int((days < '2024-12-30').sum()),
        rows_after_consumed=int((days > '2026-09-30').sum()),
        civil_dates_before_consumed=int(days[days < '2024-12-30'].nunique()),
        civil_dates_after_consumed=int(days[days > '2026-09-30'].nunique()),
        date_warning='Source civil labels only; not quality-validated NY RTH sessions')


def classify(record, registered):
    if not record.get('rows_with_timestamp', 0):
        return 'EMPTY_OR_UNREADABLE_NOT_DATA'
    if record.get('sha256') in registered:
        return 'REGISTERED_DISCOVERY_OR_WARMUP_NOT_NEW_HOLDOUT'
    if record['rows_before_consumed'] or record['rows_after_consumed']:
        return 'OUTSIDE_DATE_LABELS_PRESENT_PROVENANCE_QUALITY_CONTAMINATION_UNVERIFIED'
    return 'CONSUMED_PERIOD_OR_NON1M_NOT_INDEPENDENT'


def run():
    roots = [Path('/Users/ianvandenbrink/Downloads'), ROOT / 'data', ROOT.parent / 'data', ROOT.parent / 'Quantt/data']
    paths = set()
    for root in roots:
        if root.exists():
            paths.update(p.resolve() for p in root.rglob('*.csv') if 'nq' in p.name.lower() and p.is_file())
    manifest = json.loads((ROOT / 'research/oos-year-sources.json').read_text())
    registered = {r['sha256'] for r in manifest['sources'] + manifest['warmup_sources']}
    records = []
    errors = []
    by_hash = {}
    for path in sorted(paths):
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in by_hash:
                record = dict(by_hash[digest])
            else:
                record = inspect(path)
                if record.get('timestamp_column'):
                    record.update(extra_dates(path, record['timestamp_column']))
                record['sha256'] = digest
                by_hash[digest] = dict(record)
            record['filename'] = path.name
            record['path'] = str(path)
            record['classification'] = classify(record, registered)
            records.append(record)
        except Exception as exc:
            errors.append(dict(path=str(path), error=str(exc)))
    unique = list({r['sha256']: r for r in records}.values())
    outside = [r for r in unique if r['classification'].startswith('OUTSIDE_DATE')]
    summary = dict(status='NO_VERIFIED_INDEPENDENT_TEST_DATA_READY',
        files_scanned=len(paths), records=len(records), unique_byte_contents=len(unique),
        registered_unique_source_contents=len(registered),
        outside_date_label_files=len(outside), inventory_errors=len(errors),
        verified_independent_test_days=0, technical_eligible_independent_days=None,
        eligible_count_reason='No new quality/contract/contamination audit or sample release; not a claim zero technically possible sessions.',
        observed_new_hypothesis_outcomes=False, ohlcv_numeric_analysis=False,
        current_barchart_entitlement='NOT_VERIFIED_NO_EXISTING_ENABLED_BROWSER_TAB',
        no_paid_account_or_purchase=True,
        coverage_scope='Downloads recursively and four explicitly listed project data roots; not a whole-disk search; CSV only; no archives extracted')
    dump(ROOT / 'artifacts/independent-data-inventory.json', dict(summary=summary,
        roots=[str(p) for p in roots], records=records, errors=errors))
    dump(ROOT / 'research/independent-data-inventory-summary.json', summary)
    report(summary, unique)
    print(json.dumps(summary, indent=2))


def report(summary, records):
    relevant = [r for r in records if (r.get('rows_before_consumed') or r.get('rows_after_consumed')) and r.get('sha256')]
    rows = []
    for r in sorted(relevant, key=lambda r: r['filename']):
        rows.append(f"| {r['filename']} | {r.get('rows_with_timestamp', 0)} | {r.get('first_source_timestamp')} | {r.get('last_source_timestamp')} | {r.get('rows_before_consumed', 0)} | {r.get('rows_after_consumed', 0)} |")
    empty17 = [r for r in records if re.match('nqm17_', r['filename'], re.I)]
    lines = ['# Inventaris onafhankelijke data — 22 oktober 2026', '',
        '## Besluit', '',
        '**Geen gratis, volledige, contractgeïdentificeerde en onafhankelijk vrijgegeven NQ-dataset is in deze inventaris bewezen beschikbaar.** Dit is geen uitspraak dat nergens gratis data bestaat. Er is geen nieuwe toets gestart, geen account geopend, geen API-query met kosten uitgevoerd en niets gedownload of gekocht.', '',
        f"{summary['files_scanned']} bestanden geïnspecteerd; {summary['unique_byte_contents']} unieke byte-inhouden; {summary['inventory_errors']} inventarisfouten. Alleen headers, timestamps, aantallen en SHA-256; geen numerieke OHLCV-analyse van nieuwe/onbevestigde data. Volledig lokaal paden-/hashregister: genegeerd `artifacts/independent-data-inventory.json`.", '',
        'De inventaris betreft CSV-bestanden met NQ in de naam in Downloads en expliciete lokale projectdatamappen. Geen volledige schijfdoorzoeking of archiefextractie. Datums zijn bronlabels, geen vastgestelde NY-sessies; rijen zijn geen unieke bruikbare minuten of eligible dagen.', '',
        '## Lokale routes', '',
        '| Bron | Feitelijke toestand | Beoordeling voor v2 |', '|---|---|---|',
        '| Geregistreerde Barchart NQH25 t/m NQZ26 | De bronhashes van de verbruikte 2024-12-30 t/m 2026-09-30 reeks zijn bekend; exports kunnen randen buiten dit venster bevatten | Geen nieuwe holdout door bestanden te hernoemen, opnieuw te downloaden of van leverancier te wisselen |',
        '| Dataset_NQ_1min_2022_2025.csv | Oudere datums aanwezig; bronlabel ET; geen contractkolom of bewezen rollschema | Niet testklaar. Eerder in project bekeken; exacte eerdere uitkomsten/toegang niet volledig aantoonbaar. Een paar ongeziene rijen zijn geen gecertificeerde onafhankelijke dataset |',
        '| archive/NQ_in_* | Diverse timeframes, continue symboolreeks; hoofdzakelijk reeds verbruikte periode | Niet uitwisselbaar met afzonderlijke NQ-contracten; hogere timeframes niet terug te bouwen tot de benodigde minuten |',
        '| frd_sample_futures_NQ | Twee weken recente samples, inclusief 1m; lokale documentatie beschrijft Eastern en startlabels | Mogelijke kleine technische bronvergelijking, geen meerjarige gratis validatiereeks. Warmup/contractbasis en eerder gebruik onbevestigd; niet stilzwijgend als forward aanmerken |',
        '| NQM17-bestanden | ' + ', '.join(str(r.get('rows_with_timestamp', 0)) for r in empty17) + ' parsebare timestamps | Bestandsnaam 2017 bewijst geen historische data; lege exports niet gebruiken |', '',
        '### Alle unieke bestanden met bronlabels buiten de verbruikte periode', '',
        '| Bestand | Timestamp-rijen | Eerste label | Laatste label | Rijen vóór 2024-12-30 | Rijen na 2026-09-30 |', '|---|---:|---|---|---:|---:|'] + rows
    lines += ['', 'De volledige regel kan tegelijk een groot verbruikt middenstuk bevatten. Buitenvenster-rijen zijn uitsluitend metadata-geïnventariseerd, niet gescoord. Een avondprefix vóór een nieuwe NY-handelsdag is geen extra onafhankelijke volledige sessie.', '',
        '## Rechten, herkomst en besmettingsrisico', '',
        '- De lokale Kaggle-metadata noemt CC0-1.0; dat is de claim van de uploader, geen onafhankelijk bewijs van beurs-/vendorrechten, bronauthenticiteit of complete contractidentiteit. Niet publiek herdistribueren op basis van die claim alleen.',
        '- Het FirstRate-readme beschrijft startlabels en Eastern tijd. Dat is leveranciersdocumentatie voor die bron, geen bewijs voor Barchart-labels of uitvoerbare tickfills. De [FirstRate-licentie](https://firstratedata.com/about/license) staat afgeleide rapporten toe maar niet ruwe herdistributie; toepasselijkheid op een concrete sample blijft te controleren.',
        '- Oudere historie kan historische replicatie zijn, niet prospectief bewijs. De oude generieke datasets waren eerder in het project aanwezig en besproken. Alleen filenamen/logs kunnen absolute niet-inzage niet bewijzen. Alle 435 ontdekkingsdagen blijven verbruikt, ook op een andere vendor.',
        '- Het bestaande lokale rapport `reports/NQ-data-audit-2026-10-19.md` documenteert dat de grote CSV al volledig op prijsstructuur/VWAP/hiaten is geaudit: vermoeden van additive back-adjustment, onbevestigde contractketen, close-labels en mogelijke Excel-afkapping bij 1.048.575 datarijen. De H25/Z25-audits raadpleegden ook haar timestamps. Dit is aangetoond eerder gebruik, niet automatisch bewijs dat de specifieke 15:00-uitkomsten vóór 2024-12-30 zijn getest. De contamination-audit blijft daarom open, niet stilzwijgend schoon of definitief uitgesloten.',
        '- Een onafgebroken forwardreeks moet pas na een vooraf vastgelegde startdatum en vrijgave beginnen. Reeds aanwezige oktober-2026-samples zijn niet automatisch forward sinds een registratie van 22 oktober.', '',
        '## Externe gratis routes: actuele publieke bronnen gecontroleerd', '',
        '| Route | Wat de primaire bron ondersteunt | Wat niet is vastgesteld | Besluit bij budget €0 |', '|---|---|---|---|',
        '| Barchart bestaande toegang | [Lidmaatschapsvergelijking](https://www.barchart.com/membership-comparison) onderscheidt gratis algemene downloads van hogere lidmaatschappen; [historische downloadpagina](https://www.barchart.com/stocks/quotes/-TOOL/historical-download) beschrijft intraday-downloads en een 20.000-recordlimiet | Historische NQ-minuutexports zijn niet bewezen inbegrepen bij gratis toegang. Publieke directe pagina geeft verificatie; geen bestaande Barchart-tab in ingeschakelde browser. Actueel abonnement/resterende rechten niet uitgelezen | Alleen een rechtmatig bestaande exportmogelijkheid benutten als zonder betaling bevestigd. Geen nieuw proefabonnement of verlenging |',
        '| FirstRate samples | [FAQ](https://firstratedata.com/about/FAQ) biedt twee weken recente samples en geen andere sampleperioden | Geen kosteloze meerjarige NQ-contracthistorie of onbeperkte dagelijkse collectie bewezen | Alleen kans voor beperkte broncontrole; geen hoofdroute voor power |',
        '| algoseek Sandbox | [Publieke sandboxpagina](https://algoseek.com/sandbox/) noemt maximaal één jaar data en geen creditcard | Geen bevestigde NQ-exportrechten, gekozen perioden of volledigheid in het bestaande account; gebruiker liep eerder tegen Contact Us aan | Geen hernieuwde belofte van gratis NQ. Niet testklaar |',
        '| Databento introductietegoed | [Officiële credits-FAQ](https://databento.com/docs/faqs/usage-pricing-and-data-credits) noemt $125 voor nieuwe gebruikers, zes maanden geldig, één keer per team en geen maandabonnement voor historische usage-based data | Geen onbeperkte gratis bron; geen bevestigde accountgeschiktheid, queryprijs, resterend tegoed of afwezigheid betaalverplichtingen. De [billingdocumentatie](https://databento.com/docs/portal/billing) noemt onbeperkt gebruik als standaard zonder maandlimiet; een limiet is niet automatisch een bewezen harde €0-grens per aanvraag | Mogelijke eenmalige kosteloze historische route als tegoed, quote, licentie en blokkade op eigen betalingen vooraf aantoonbaar zijn. Nu geen account, toggle, API-query of download uitgevoerd |',
        '| CME settlementpagina’s | [CME](https://www.cmegroup.com/trading/about-settlements.html) beschrijft dagelijkse settlementstatistieken als referentie | Geen individuele 15:00/15:01/15:14-transacties; settlement is geen minutebar | Ongeschikt voor certificatie van het twee-minuteneffect of fills |', '',
        'De Barchart-publieke zoekindex en de rechtstreeks geopende verificatiepagina leveren niet hetzelfde bewijs als een actuele accountcontrole. Gratis tabeldownloads zijn niet hetzelfde als gratis historische minuutexports. Geen Cloudflare-omzeiling of loginpoging gedaan.', '',
        '## Werkbelasting en volgende beslissing', '',
        'Een technisch proefpakket via al bestaande toegestane exports: twee vooraf gekozen, volledige 2-weekse contractblokken bij gewone weken en een aparte DST-/rollovercontrole. Niet nu downloaden en geen uitkomsten inspecteren. Volledige sessies en ATR14-opwarmhistorie zijn nodig; alleen het kwartier ophalen volstaat niet voor selectie.', '',
        'Bij 20.000 records/request is twee kalenderweken van ongeveer tien volledige futuresessies (~13.800 1m-bars) doorgaans een passend blok, geen garantie bij specifieke grenzen. Voor een geheel jaar is circa 26 basisblokken nodig, plus contractoverlap, herstel van gaten en opwarming. Bij één hypothetisch toegestane export/dag dus minstens circa 26 handmatige downloadmomenten/jaar, niet een bewezen gratis recht of vaste kalenderplanning. Dit is een werkraming, geen bestellijst.', '',
        '**Eindoordeel: formele onafhankelijke toets voorlopig NIET VRIJGEVEN.** Geen geverifieerde gratis onafhankelijke hoofdbron. Eerst actuele bestaande Barchart-exportrechten zonder nieuwe kosten vaststellen, of wachten op aantoonbaar bruikbare kosteloze contractdata. De huidige samples kunnen een beperkte technische vergelijking helpen, maar lossen het steekproefprobleem niet op. Geen collector, nieuwe strategie of eindtoets gebouwd.', '']
    (ROOT / 'docs/INDEPENDENT_DATA_INVENTORY.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    run()
