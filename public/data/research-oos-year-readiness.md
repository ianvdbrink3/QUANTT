# Jaar-holdout: voorbereiding afgerond, scoring geblokkeerd

Periode: 1 oktober 2025–30 september 2026. Alleen stappen1–3. Geen toekomstige signalen, entries, trades of P&L berekend. ATR en volume uitsluitend als technische voorwaarden voor eligibility.

## Datakwaliteit

| Maatstaf | Aantal |
|---|---:|
| Bronbestanden nieuwe periode | 39 |
| Historische opwarmbestanden | 30 |
| Weekdagdatums / geplande sessies | 261 / 259 |
| Actieve unieke minuutbars | 354113 |
| Schone normale dagen | 243 |
| Kalenderconform complete dagen inclusief vroege sluitingen | 248 |
| Dagen met ontbrekende minuten | 11 |
| Gedocumenteerde storing, ontbrekende minuten | 645 |
| Onverklaarde ontbrekende minuten | 67 |
| Volledig ontbrekende sessies / onverwachte minuten | 0 / 0 |

Kerst2025 en Nieuwjaar2026 zijn de twee gesloten civiele dagen. Schone normale dag = exact1380minuten. Kalenderconform schoon = alle geplande minuten aanwezig, vroege sluiting toegestaan, maar geen ontbrekende storingsminuten. Er is geen imputatie.

## Technische eligibility

| Model | Dagen | Rol |
|---|---:|---|
| A_London_sweep | 249 | Uitsluitend beschrijvende referentie |
| B_ORB5 | 249 | Uitsluitend beschrijvende referentie |
| B_ORB15 | 249 | Enige primaire hypothese |
| C_VWAP_extreme | 249 | Uitsluitend beschrijvende referentie |

Frozen primary all-view: priorATR>0 + exact18NY-noon prefix; ORB also nonnull prior same-clock volume09:30-11:00. Not trade count or edge evidence. No imputation.

Een dag met alleen een gat na12:00 kan eligible blijven. Dit verklaart dat249 groter is dan248 kalenderconform complete dagen. Geen ATR-opwarmuitval na rollovers. De tien uitgesloten datums zijn voor alle modellen gelijk. ORB heeft één aanvullende volumegate-fout op een reeds uitgesloten dag; redenen mogen niet worden opgeteld.

2025-11-28, 2025-12-24, 2025-12-26, 2026-01-06, 2026-02-16, 2026-03-16, 2026-04-03, 2026-04-21, 2026-06-18, 2026-07-03

## Uitzonderingen per dag

| Datum | Geobserveerd / verwacht na storingsattributie | Onverklaard ontbrekend | Storing | Prefix tot12:00 volledig |
|---|---:|---:|---:|---|
| 2025-11-27 | 1140 / 1140 | 0 | 0 | Ja |
| 2025-11-28 | 508 / 510 | 2 | 645 | Nee |
| 2025-12-24 | 1152 / 1155 | 3 | 0 | Nee |
| 2025-12-26 | 1377 / 1380 | 3 | 0 | Nee |
| 2026-01-06 | 1379 / 1380 | 1 | 0 | Nee |
| 2026-01-19 | 1140 / 1140 | 0 | 0 | Ja |
| 2026-02-16 | 1138 / 1140 | 2 | 0 | Nee |
| 2026-03-03 | 1379 / 1380 | 1 | 0 | Ja |
| 2026-03-16 | 1379 / 1380 | 1 | 0 | Nee |
| 2026-04-03 | 909 / 915 | 6 | 0 | Nee |
| 2026-04-21 | 1379 / 1380 | 1 | 0 | Nee |
| 2026-05-25 | 1140 / 1140 | 0 | 0 | Ja |
| 2026-06-18 | 1334 / 1380 | 46 | 0 | Nee |
| 2026-06-19 | 1140 / 1140 | 0 | 0 | Ja |
| 2026-07-03 | 1139 / 1140 | 1 | 0 | Nee |
| 2026-09-07 | 1140 / 1140 | 0 | 0 | Ja |

Good Friday2026 sluit09:15NY en kan het vereiste18:00–12:00-venster niet vervullen. Thanksgiving en andere vroege sluitingen worden niet automatisch corrupt genoemd. Storingmaskering geldt alleen voor kwaliteitstoeschrijving, niet voor eligibility.

## Objectieve rollovers

| Contracten | Volumebesluit | Eerste actieve handelsdag |
|---|---|---|
| NQZ25 naar NQH26 | 2025-12-15 | 2025-12-16 |
| NQH26 naar NQM26 | 2026-03-16 | 2026-03-17 |
| NQM26 naar NQU26 | 2026-06-15 | 2026-06-16 |
| NQU26 naar NQZ26 | 2026-09-14 | 2026-09-15 |

Vaste eerste grensgekwalificeerde crossover, incoming waargenomen volume strikt groter dan outgoing; activeren18:00NY op de voorafgaande civiele kalenderdag. Geen kalenderfallback, geen intraday-overgang. Alle vier besluiten onveranderd bij verwijderen van toekomstige dagen. Op16maart ontbreekt één minuut in uitgaand H26; de vooraf vastgelegde boundary-regel eist geen volledige interne minutendekking. Geen claim van officiële CME-totalen.

De spread gebruikt uitsluitend de laatste gezamenlijke voltooide15:59NY-close vóór activering. Tijdstempels zijn publiek, prijzen en volumetotalen blijven privé met een publieke hash van de volledige ledger. Beide US-DST-overgangen zijn geautomatiseerd getest.

## Bewijs uitvoeringsroute

De nieuwe route selecteert actieve contracten en hergebruikt de bevroren continuousATR- en volumehistorie. Alleen voor de historische replay worden intraday features en signalen uitgevoerd. De guard weigert elke signaalroute met een datum na30september2025 vóór featureconstructie. Een runtime-tripwire blokkeert build_features/hypotheses/simulate/baseline/metrics/bootstrap tijdens de jaarvoorbereiding.

Alle30 historische bronnen opnieuw geladen. De nieuwe route reproduceert435 historische trades en780 eligibility-regels byte-identiek aan de SHA256-verankerde private vNext-ledgers. Alle vier modellen blijven159 historisch eligible dagen houden. Alle73 bevroren bestanden zijn byte-identiek. Het toekomstige jaar is hierbij niet gescoord.

## Reproductie

- `npm run verify:oos-year`: private geregistreerde bronnen en kalender opnieuw controleren, ATR-/volumevoorwaarden en eligibility opnieuw bepalen. Geen signalen.
- `npm run verify:oos-year-parity`: uitsluitend2024-12-30–2025-09-30, volledige historische-ledgerpariteit.
- `.venv/bin/python -m pytest -q`: synthetische regressies en integriteitscontroles; CI heeft geen rawdata nodig.
- `npm run verify:freeze`:73bestanden bytecontrole.
- `.venv/bin/python -m scripts.oos_preparation.seal --verify`: inhoudsadres van het preregistratie-pakket controleren.
- Rawdata staat in genegeerd `data/raw/`; private dagledger, exacte ontbrekende timestamps, indicatorstaat en roll-spreads in genegeerd `artifacts/oos-year-readiness/`.

## Grenzen en vrijgavemoment

Geen toekomstige trade-ledger aangetroffen bij controle van de datumkolommen in lokale onderzoeksartefacten. Onvolledige logs bewijzen nooit absoluut niet-gebruik. Calendars zijn productspecifieke broker-/leveranciersreconstructies, geen ondertekend historisch CME-certificaat. Leveranciersrechten en publicatievintages blijven niet onafhankelijk gecertificeerd. Geen ruwe data of individuele trades gepubliceerd. Niets gekocht.

De bestaande primaire ORB15-hypothese, $24,50RT, vaste periode, bootstrap en gezamenlijke slaagcriteria blijven onveranderd. Referenties mogen niet achteraf worden gepromoveerd. Een eventuele mislukking wordt niet gered door deelperiode, clean-view, extra filter of gecombineerde historie.

**STOP: wachten op expliciete vrijgave van Stap4, met kennis van de genoemde beperkingen. Dit pakket geeft zelf geen scoringtoestemming en bevat geen holdout-oordeel.**

## Kalenderbronnen

- research/oos-calendar-register.json
- research/holdout-protocol.json
- https://support.ninjatrader.com/eu/s/article/2026-Holiday-Trading-Hours?language=en_US
- https://www.ampfutures.com/news/christmas-holiday-trading-schedule
- https://www.ampfutures.com/news/new-year-holiday-trading-schedule
- https://www.ampfutures.com/news/holiday-trading-schedule-thanksgiving
- https://www.cmegroup.com/trading/equity-index/rolldates.html
