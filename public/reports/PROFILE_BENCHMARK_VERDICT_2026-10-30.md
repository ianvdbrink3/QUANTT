# Profielen versus eenvoudige referenties — 30 oktober 2026

Doorlopend **2019-01-02 t/m 2026-10-28**, 1967 volledige cashsessies. Ontwikkelingsdata, geen onafhankelijke validatie. Geen parameters gekozen op basis van deze uitkomsten.

## Wat werkelijk berekend is

Dezelfde `features`, `classify`, `sleeve_targets` en gewichten als de bestaande studie. Zonder stortingen reproduceert de nieuwe runner de oude drie S1-uit-profielen op het oude tijdvenster tot <1e-12 per dag. Er is geen nieuw filter of alternatief stopbeleid toegevoegd.

De profielen houden eerst max(10,1% NAV) cash aan. Herweging is betaald op maand-/regimewissels; de bestaande dagelijkse cap-trims blijven aanwezig. Dit is een allocatiebacktest, geen replay van de lokale bot met lotgroottes, 5bp-kostenpoort, settlement, handmatige drawdown-reset of echte brokerquotes.

Vorige afgeronde slotbar bepaalt de volgende officiële opening. Het definitieve huidige slot wordt nooit als instap gebruikt. Eindliquidatie op 28 oktober is een vooraf gekozen onderzoeksgrens. Fractionele stukken, cashrente nul, belasting uitgesloten. Dag-NAV onderschat mogelijk intraday verliezen.

Splits worden niet opnieuw toegepast op reeds split-gecorrigeerde OHLC. Werkelijke dividenden worden eenmaal aan de vorige eigenaar toegekend op ex-date; dat is economische herbelegging, geen bewezen betaaldagcash. TQQQ-prijzen bevatten de fondsfinanciering al.

Maandinleg: januari 2019 is uitsluitend de begininleg. Vanaf februari komt 100 na de opening op de eerste cashdag beschikbaar; aankoop volgt op de eerstvolgende opening, tegen werkelijke historische ETF-koersen. Bij bear-regime blijft de storting cash. Rendement en drawdown worden flow-gecorrigeerd berekend; stortingen zijn geen rendement.

## S1 blijft onbekend, geen fictief volledige lijn

Vereiste S1-nachten: **169**; exacte ankers: **112**; complete geobserveerde stoppaden: **4**. Ontbrekende ankers 57; onvolledige stoppaden 108. Ook 2022: {'required': 1, 'anchors': 1, 'complete_stop_paths': 0, 'missing_anchors': 0, 'incomplete_stop_paths': 1}.

Voorzichtig 50/0/25/25 en Gebalanceerd 60/30/10 mét S1 houden daarom status **CENSORED_UNKNOWN_S1_PATHS**: eindvermogen, CAGR, DD en Sharpe onbekend. Geen same-close dagbarinvulling en geen ontbrekende nacht als nulrendement. De getoonde berekenbare profielen zijn expliciet **S1 uit**; die reservering blijft cash.

## Valuta en kosten

Hoofdweergave EUR: cash in euro; ETF-aankoop/verkoop gebruikt de laatst vóór die datum gepubliceerde ECB USD-per-EUR-referentie; dagwaardering gebruikt de actuele beschikbare ECB-fix. Dit is historische FX-referentiewaardering, geen bewezen uitvoerbare wisselkoers. FX-spread/conversiecommissie en belastingen ontbreken. De aparte USD-weergave houdt de oude studies vergelijkbaar; zij mag niet als werkelijk euroresultaat worden gelabeld.

Kosten zijn vaste aannames van 2 en 10 bp RT, naar koop-/verkoopnotional. Werkelijke brokerminimumkosten kunnen hoger zijn. [ECB API](https://data.ecb.europa.eu/help/api/data-examples), [publicatie rond16:00CET](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html).

## Volledige reeks — zuivere groei zonder bijstorten

### EUR · 2 bp RT

| Regel | Eindwaarde vanaf1.000 | CAGR% | Groei% | MaxDD% | Sharpe | Langste onderwater sessies / kalenderdagen |
|---|---:|---:|---:|---:|---:|---:|
| Voorzichtig · S1 uit | 1988.85 | 9.190 | 98.88 | 13.93 | 1.039 | 382 / 558 |
| Gebalanceerd · S1 uit | 4425.43 | 20.949 | 342.54 | 25.80 | 1.003 | 382 / 558 |
| Aanvallend · state-machine | 8268.92 | 31.015 | 726.89 | 38.26 | 0.898 | 382 / 558 |
| QQQ TREND200 | 3823.01 | 18.707 | 282.30 | 27.12 | 1.039 | 384 / 562 |
| Gewoon QQQ Buy & Hold | 5180.52 | 23.410 | 418.05 | 31.21 | 0.985 | 495 / 721 |
| TQQQ TREND200 · extra referentie | 12827.55 | 38.581 | 1182.75 | 51.11 | 0.917 | 380 / 556 |
### USD · 2 bp RT

| Regel | Eindwaarde vanaf1.000 | CAGR% | Groei% | MaxDD% | Sharpe | Langste onderwater sessies / kalenderdagen |
|---|---:|---:|---:|---:|---:|---:|
| Voorzichtig · S1 uit | 2002.42 | 9.285 | 100.24 | 11.77 | 1.081 | 365 / 531 |
| Gebalanceerd · S1 uit | 4501.69 | 21.213 | 350.17 | 22.77 | 1.023 | 383 / 559 |
| Aanvallend · state-machine | 8481.05 | 31.440 | 748.11 | 37.88 | 0.907 | 382 / 558 |
| QQQ TREND200 | 3893.12 | 18.983 | 289.31 | 23.09 | 1.082 | 365 / 531 |
| Gewoon QQQ Buy & Hold | 5037.10 | 22.968 | 403.71 | 35.12 | 0.988 | 493 / 716 |
| TQQQ TREND200 · extra referentie | 12973.36 | 38.782 | 1197.34 | 48.14 | 0.920 | 379 / 552 |

## Vermogensopbouw —1.000 start +100 per maand, EUR2bp

| Regel | Eigen inleg | Eindvermogen | Winst boven inleg |
|---|---:|---:|---:|
| Voorzichtig · S1 uit | 10300.00 | 15619.23 | 5319.23 |
| Gebalanceerd · S1 uit | 10300.00 | 25135.98 | 14835.98 |
| Aanvallend · state-machine | 10300.00 | 35329.20 | 25029.20 |
| QQQ TREND200 | 10300.00 | 24211.24 | 13911.24 |
| Gewoon QQQ Buy & Hold | 10300.00 | 26185.10 | 15885.10 |
| TQQQ TREND200 · extra referentie | 10300.00 | 53246.36 | 42946.36 |

## 2022 apart — bestaande posities uit2021 blijven bestaan

De jaarcijfers komen uit de doorlopende replay, niet een gunstig herstartmoment in cash. Rendement en DD gebruiken het NAV-slot vóór2022 als start. Het dashboard toont bij2022 de bestaande vermogenslijn; het herstart geen portefeuille.

| Regel | Valuta | RTbp | Rendement2022% | MaxDD2022% | Sharpe2022 |
|---|---|---:|---:|---:|---:|
| Voorzichtig · S1 uit | USD | 2 | -7.32 | 7.75 | -2.485 |
| Gebalanceerd · S1 uit | USD | 2 | -13.04 | 14.26 | -2.039 |
| Aanvallend · state-machine | USD | 2 | -15.15 | 17.89 | -1.328 |
| QQQ TREND200 | USD | 2 | -14.53 | 15.35 | -2.484 |
| Gewoon QQQ Buy & Hold | USD | 2 | -32.58 | 34.83 | -1.070 |
| TQQQ TREND200 · extra referentie | USD | 2 | -19.01 | 22.06 | -1.262 |
| Voorzichtig · S1 uit | USD | 10 | -7.48 | 7.92 | -2.528 |
| Gebalanceerd · S1 uit | USD | 10 | -13.24 | 14.45 | -2.068 |
| Aanvallend · state-machine | USD | 10 | -15.19 | 17.91 | -1.331 |
| QQQ TREND200 | USD | 10 | -14.84 | 15.65 | -2.527 |
| Gewoon QQQ Buy & Hold | USD | 10 | -32.58 | 34.83 | -1.070 |
| TQQQ TREND200 · extra referentie | USD | 10 | -19.04 | 22.06 | -1.265 |
| Voorzichtig · S1 uit | EUR | 2 | -7.26 | 7.58 | -2.473 |
| Gebalanceerd · S1 uit | EUR | 2 | -13.00 | 14.03 | -2.030 |
| Aanvallend · state-machine | EUR | 2 | -15.27 | 17.80 | -1.340 |
| QQQ TREND200 | EUR | 2 | -14.41 | 15.01 | -2.473 |
| Gewoon QQQ Buy & Hold | EUR | 2 | -28.41 | 30.39 | -0.868 |
| TQQQ TREND200 · extra referentie | EUR | 2 | -19.30 | 22.14 | -1.286 |
| Voorzichtig · S1 uit | EUR | 10 | -7.42 | 7.74 | -2.516 |
| Gebalanceerd · S1 uit | EUR | 10 | -13.20 | 14.22 | -2.060 |
| Aanvallend · state-machine | EUR | 10 | -15.31 | 17.82 | -1.343 |
| QQQ TREND200 | EUR | 10 | -14.72 | 15.31 | -2.516 |
| Gewoon QQQ Buy & Hold | EUR | 10 | -28.41 | 30.39 | -0.868 |
| TQQQ TREND200 · extra referentie | EUR | 10 | -19.34 | 22.14 | -1.289 |

## Meerwaarde — zonder mooipraterij

- **EUR Voorzichtig · S1 uit** — Gewoon QQQ Buy & Hold: lager eindvermogen (-3191.68), lagere DD (13.93% vs31.21%); QQQ TREND200: lager eindvermogen (-1834.16), lagere DD (13.93% vs27.12%); TQQQ TREND200 · extra referentie: lager eindvermogen (-10838.70), lagere DD (13.93% vs51.11%).
- **EUR Gebalanceerd · S1 uit** — Gewoon QQQ Buy & Hold: lager eindvermogen (-755.10), lagere DD (25.80% vs31.21%); QQQ TREND200: hoger eindvermogen (+602.42), lagere DD (25.80% vs27.12%); TQQQ TREND200 · extra referentie: lager eindvermogen (-8402.12), lagere DD (25.80% vs51.11%).
- **EUR Aanvallend · state-machine** — Gewoon QQQ Buy & Hold: hoger eindvermogen (+3088.40), hogere DD (38.26% vs31.21%); QQQ TREND200: hoger eindvermogen (+4445.92), hogere DD (38.26% vs27.12%); TQQQ TREND200 · extra referentie: lager eindvermogen (-4558.62), lagere DD (38.26% vs51.11%).
- **USD Voorzichtig · S1 uit** — Gewoon QQQ Buy & Hold: lager eindvermogen (-3034.68), lagere DD (11.77% vs35.12%); QQQ TREND200: lager eindvermogen (-1890.70), lagere DD (11.77% vs23.09%); TQQQ TREND200 · extra referentie: lager eindvermogen (-10970.94), lagere DD (11.77% vs48.14%).
- **USD Gebalanceerd · S1 uit** — Gewoon QQQ Buy & Hold: lager eindvermogen (-535.41), lagere DD (22.77% vs35.12%); QQQ TREND200: hoger eindvermogen (+608.57), lagere DD (22.77% vs23.09%); TQQQ TREND200 · extra referentie: lager eindvermogen (-8471.68), lagere DD (22.77% vs48.14%).
- **USD Aanvallend · state-machine** — Gewoon QQQ Buy & Hold: hoger eindvermogen (+3443.95), hogere DD (37.88% vs35.12%); QQQ TREND200: hoger eindvermogen (+4587.93), hogere DD (37.88% vs23.09%); TQQQ TREND200 · extra referentie: lager eindvermogen (-4492.31), lagere DD (37.88% vs48.14%).

De eerder geciteerde19,6%/40,8% komen uit een andere begindatum/einddatum. De nieuwe gelijktijdige referenties hierboven hebben exact dezelfde2019-01-02–2026-10-28-periode. Een lagere DD is geen garantie voor nachtrust; herstelduur en hefboomverliezen blijven relevant.

De complete2/10bp-matrix staat in `research/PROFILE_BENCHMARK_RESULTS_2026-10-30.csv`. Het openbare JSON bevat uitsluitend afgeleide NAV-curves en aggregaten. Bron-OHLC, individuele orders en ledgers blijven lokaal. De oude6/8/10%-scenario’s blijven als bevroren archief bestaan, maar zijn geen actieve onderzoeksuitkomst meer en verdwijnen uit de standaardgrafiek.

## Reproductie

Benodigd: Python met numpy, pandas, python-dateutil en requests. Kopieer de onveranderde dagelijkse en minuutbestanden volgens de twee bronregisters onder data/raw; plaats de ECB-CSV op het geregistreerde relatieve pad. Er is geen brokerlogin, private ledger of betaald account nodig.

`python -m scripts.profile_benchmark --verify` laadt opnieuw brondata, controleert hashes en geeft alleen bij byte-identieke uitkomsten vrij. `research/profile-benchmark-register-2026-10-30.json` legt bron-/codehashes en het outputhash vast. De toekomstsimulator is uitsluitend door de gebruiker ingestelde rekenkunde, zonder profielrendementsclaim.
