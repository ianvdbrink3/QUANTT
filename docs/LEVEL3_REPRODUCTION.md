# Niveau 3: vaste-regels holdout-reproductie

De historische vervolgperiode is 18 april–30 september 2025. ORB 15m is de enige primaire hypothese. Dit is een historische registratie vóór de signaalrun, geen prospectieve studie. Na de eerste run is deze holdout verbruikt.

## Lokaal opnieuw uitvoeren

Gebruik dezelfde Python-omgeving als Niveau 2, met dependencies uit `requirements-lock.txt`, en Node.js 22 of nieuwer. Installeer de Python-dependencies in een virtuele omgeving. Zet alle 30 originele bestanden uit `research/holdout-protocol.json` in `data/raw/`. De elf oorspronkelijke bestanden zijn ook nodig voor opwarmhistorie en de exacte Niveau-2-ledgercontrole.

```sh
npm run verify:holdout
```

Een andere private bronmap kan met:

```sh
npm run verify:holdout -- --raw-dir /absolute/private/raw
```

Het commando leest uitsluitend de ruwe CSV's, geen eerder berekende master of trades. Het verifieert SHA-256-hashes, ontdubbelt per contract, weigert conflicterende overlap, bepaalt de volume-rollovers opnieuw, bouwt alle features per contract/session en voert de ongewijzigde strategie-engine uit. Vervolgens controleert het de originele ORB15-tradeledger, kosten/fills en alle publieke holdout-resultaten tegen de vastgelegde eerste run.

Een geslaagde technische reproductie meldt `REPRODUCTION PASS`. Dat is **niet** hetzelfde als een geslaagde tradinghypothese: de afzonderlijke status kan `HOLDOUT_FAILED` zijn. Een ontbrekend bronbestand, gewijzigde hash, afwijkend resultaat of uitgeschakelde Python-assertions levert een niet-nul exitcode op.

Gedetailleerde bars, Parquet, sessies, kwaliteitsvlaggen, eligibility, trades en verificatierapport komen onder de genegeerde map `artifacts/holdout-*/`. De originele CSV's worden nooit aangepast en heel `/data/raw/` staat in `.gitignore`. Publiek komen alleen aggregaten zonder entry-/exitprijzen of ruwe bars.

## Volgorde en bestanden

1. `scripts/reproduce_research/holdout_data.py` kopieerde de expliciet aangeleverde bestanden veilig en legde hashes, kalender, passregel en volume-rollovers vast in `research/holdout-protocol.json`. Deze datastap bevat geen strategie-aanroep en is vóór de signaalrun apart gecommit.
2. `scripts/reproduce_research/holdout.py` gebruikt `engine.build_features`, `engine.hypotheses`, `engine.simulate`, `engine.metrics` en `engine.bootstrap` uit de bevroren Niveau-2-engine. Alleen de verwachte kalender-minutengrid en selectie van contract/sessie worden uitgebreid.
3. De eenmalige eerste run schreef `research/holdout-reference.json`, `public/data/research-holdout.json` en `docs/LEVEL3_HOLDOUT_REPORT.md`. `--record-first-run` weigert een bestaande referentie te overschrijven. Gebruik die optie niet om een tegenvallende uitkomst te vervangen.
4. Een tweede volledige run via `verify:holdout` vergelek alle resultaten vanaf de bron opnieuw. De bestaande Niveau-2-JSON's blijven ongewijzigd, zodat `verify:research` zijn oorspronkelijke referenties behoudt.

## Vooraf vastgelegde regels

- Eerste inkomende contract met groter geobserveerd afgesloten sessievolume dan het uitgaande contract. Selectie is onomkeerbaar, pas vanaf de volgende sessie om 18:00 New York. Geen prijs-, signaal- of PnL-selectie.
- De eerste/laatste bronranden mogen geen afgeknotte sessievolumevergelijking veroorzaken. De expliciete randcontroles staan in `rollovers`; dunne minuten worden niet als fictieve nulvolumebars toegevoegd.
- Geen open positie over een sessie- of contractgrens. Alle strategieën sluiten vóór 12:00 NY. Returns, VWAP, ATR en volumereferenties worden nooit tussen contracten geleend of back-adjusted.
- Exact $24,50 per roundtrip voor één NQ: twee ticks slippage per kant plus $4,50 commissie. Worst-case stop vóór target als beide in dezelfde minuut geraakt worden.
- Primaire kwaliteitsview `all`: de oorspronkelijke strenge vereiste vensters en VWAP-prefix moeten compleet zijn. De `clean`-view is uitsluitend een vooraf bekende sensitiviteit en geen tweede primaire toets.
- ATR vereist 14 geldige voltooide eerdere RTH true ranges van hetzelfde contract. Ontbrekende opwarmhistorie blijft ontbrekend. De definitieve rapportage toont daardoor expliciet de uitval per contract.
- Bootstrap: exact de oorspronkelijke 2000 circular moving-block replicaties, blokken van vijf eligible sessies, seed 20261020, tweezijdige gecentreerde p-waarde. Nul-tradedagen onder de eligible sessies blijven in de verdeling.
- Promotie alleen bij minstens 20 eligible sessies, netto winst > 0, PF > 1, 95%-intervalondergrens van gemiddelde dag-PnL > 0 en primaire p < 0,05. De gecombineerde dataset is beschrijvend, niet een tweede onafhankelijke toets.

## Kalender en bewijsgrenzen

De engine behoudt NY civil-sessiondagen (18:00 vorige kalenderdag tot sluiting), niet de officiële CME clearing TradeDate. Good Friday 18 april is gesloten. Memorial Day, Juneteenth, 4 juli en Labor Day sluiten om 13:00 NY; 3 juli om 13:15 NY. De volgende avondopening start weer een nieuwe civil-sessiondag. Een export tot 30 september 23:59 bevat al een deel van de 1-oktobersessie; die wordt uitgesloten.

De historische CME-webpagina serveert nu een andere jaarkalender. Daarom zijn de historische sluitingen gereconstrueerd uit de in het protocol genoemde contemporaine broker-/datavendorschema's, gecontroleerd tegen de bars, en nadrukkelijk niet aangeduid als apart CME-gecertificeerde kalender. Het volume is de som van de aangeleverde bars, niet onafhankelijk geverifieerd tegen exchange-totalen. Beschikbaarheid vóór de volgende sessieopening blijft een expliciete informatie-timingaanname.

Een positieve vaste-regels holdout bewijst geen live uitvoerbaarheid. Een negatieve of niet-significante holdout rechtvaardigt geen promotie. Geen optimalisatie op deze inmiddels bekeken periode en daarna dezelfde periode opnieuw als ongeziene holdout presenteren.
