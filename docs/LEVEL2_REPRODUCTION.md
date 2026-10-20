# Niveau 2 — reproductie vanaf private Barchart-minuutbars

Deze repository bevat nu de volledige implementatie achter `public/data/nq-overnight.json` en `public/data/research09.json`. Geen vooraf berekende masterdataset of trade-lijst is nodig als invoer. De runner gebruikt een nieuwe lege uitvoermap bij elke run.

Niveau 2 betekent hier: een andere gebruiker kan dezelfde vastgelegde implementatie opnieuw uitvoeren op exact dezelfde bronbestanden. Het is **geen tweede onafhankelijk geschreven backtester**, geen onafhankelijke CME-herkomstcontrole, geen ongeopende holdout en geen trading-edge-validatie.

## Installatie

Node.js >=22 en Python >=3.11 (getest met de versies in requirements-lock.txt):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
npm ci
```

Windows: maak de venv met `py -m venv .venv` en gebruik `.venv\Scripts\python.exe`. De Node-launcher herkent beide venv-layouts. Een andere interpreter kan expliciet via de omgevingsvariabele `PYTHON` worden gekozen. Er worden niet stilzwijgend afhankelijkheden geïnstalleerd of data gedownload.

## Private bronbestanden

Plaats de **11 originele downloads**, met ongewijzigde bestandsnamen én bytes, in `data/raw/`:

- NQH25: `nqh25_intraday-1min_historical-data-10-19-2026.csv` en suffixen `-2` t/m `-8`.
- NQM25: `nqm25_intraday-1min_historical-data-10-19-2026.csv` en suffixen `-2` en `-3`.

De exacte SHA-256-hashes, namen en aantallen staan in `research/reproduction-manifest.json`. Ze worden tevens tegen `source_csv_hashes` in het gepubliceerde NQ-rapport gecontroleerd. De identieke OHLCV-export in twee H25-downloads blijft als afzonderlijk origineel bronbestand opgenomen: hun downloadvoetregels en bestandsbytes verschillen.

De hele map `/data/raw/` is gitignored, voor elk bestandstype en alle submappen. Geen `.gitkeep` of voorbeeldmarktdata nodig. Ook `artifacts/`, `.venv` en `node_modules` zijn uitgesloten. Gebruik nooit `git add -f` voor brondata.

## Volledige verificatie

```sh
npm run verify:research
```

Of rechtstreeks: `./scripts/reproduce-research`. Dit doet achtereenvolgens:

1. Bronhashes én bytehashes van de twee vastgelegde publieke rapporten controleren. Ontbrekende of gewijzigde bestanden geven exitcode 1, niet een gedeeltelijke succesmelding.
2. Alle 11 CSV's opnieuw lezen, voetregels herkennen, Chicago-tijd inclusief DST omzetten naar UTC en identieke overlap ontdubbelen. Tegenstrijdige overlap is fataal.
3. Features eerst per contract/handelsdag berekenen, contractspecifieke ATR-opwarming en voorgaande RTH-levels gebruiken, daarna pas H25 t/m 18 maart en M25 vanaf handelsdag 19 maart selecteren.
4. Baselines, de vier strategieën, kosten, stop/target-uitvoering, kwaliteitsaudit, helften, bootstrap en robuustheidscontroles opnieuw berekenen. Ook prefix-invariantie, exact Parquet/CSV-herlezen en PnL-reconciliatie worden getest.
5. De 0.9 CSV→Parquet-importgate en beschrijvende research opnieuw uitvoeren, en **beide** JSON-bundles naar de private runmap genereren.
6. Alle waarden/structuren in beide JSON-bundles vergelijken met de gepubliceerde referenties. Alleen `generated_at`, de master-Parquet-bytehash en `sources[].staged_sha256` vallen buiten de semantische vergelijking: die zijn run-/serialisatiemetadata en worden afzonderlijk gerapporteerd. De bron-CSV-hashes, canonieke datasetfingerprints, run-ID's, alle tradesamenvattingen, checks, equity-curves en resultaatvelden blijven verplicht. Integers/strings/structuren exact; floats met absolute tolerantie 1e-9, geen relatieve tolerantie.

Verplichte einduitkomst:

| Controle | Referentie |
|---|---:|
| Geselecteerde minuutbars | 106.678 |
| Geschikte dagen, ORB15, all-view | 42 |
| ORB15-trades | 37 |
| ORB15 netto punten, onafgerond | 919,425 |
| ORB15 netto punten, decimaal half-up afgerond | +919,43 |

De clean-view heeft 41 geschikte dagen; die niet verwarren met de gevraagde 42. De kosten zijn 1,225 punt per round trip: 2 ticks slippage per kant plus $4,50 commissie bij $20/punt.

Ook de volledige 37 onderliggende ORB15-trades worden via een canonieke SHA-256-fingerprint tegen de oorspronkelijke private tradelijst gecontroleerd: inclusief tijdstempels, richting, stop/target en fills. Alleen de hash staat in Git, niet de uitvoeringsprijzen of de private tradelijst. Een andere combinatie trades met hetzelfde totaal voldoet dus niet.

De runmap `artifacts/reproduction-*/` bevat `verification-report.json`, de volledige master, features, trades, audits en de twee gegenereerde JSON-bestanden onder `public/data/`. Deze map blijft privé. De standaardverificatie wijzigt de gepubliceerde rapporten niet.

`npm run verify:research -- --hashes-only` is een snelle voorcontrole en wordt expliciet **niet** als Niveau 2 gerapporteerd. `--raw-dir /andere/map` wordt ondersteund. Python `-O` wordt geweigerd, zodat assertions niet kunnen verdwijnen.

## De vastgelegde release opnieuw exporteren

```sh
npm run reproduce:research
```

Dit voert eveneens de volledige verificatie uit en schrijft daarna beide rapporten naar de echte `public/data/`-map, uitsluitend als de bytes overeenkomen met de vastgelegde release. De oorspronkelijke release-timestamp blijft behouden; de actuele runtijd staat in het verificatierapport. Bij afwijkende serialisatiebytes blijven de nieuwe bestanden privé en wordt niets gepubliceerd. De referentiemanifest-hashes worden nooit automatisch aangepast om een afwijking te laten slagen.

## Codekaart

- `scripts/reproduce-research`: uitvoerbare, platformneutrale Node-launcher.
- `scripts/reproduce_research/cli.py`: broncontrole, verse run, volledige rapportvergelijking en exitcodes.
- `barchart.py`: strikte bronparser en handelsdatumtoekenning.
- `engine.py`: volledige vastgelegde feature-, baseline-, backtest- en statistiekimplementatie van de nachtbatch.
- `audit_outputs.py`: aanvullende controles op onderliggende trades, kostenidentiteit en M25-levels bij rollover.
- `publish.py`: 0.9-import, spiegelrichtingscontroles en uiteindelijke JSON-export.
- Bestaande `src/quantlab/`-modules: importer, contractvalidatie en de apart gelabelde beschrijvende 0.9-events.

Geen lokale gebruikerspaden, ChatGPT-context, aanvullende chats of sibling-repositories zijn vereist. De oorspronkelijke algoritmeregels zijn niet op deze nieuwe run geoptimaliseerd. Reproductie maakt de eerder gevonden ORB15-kandidaat controleerbaar, niet statistisch bewezen.
