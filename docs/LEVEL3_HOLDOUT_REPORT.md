# Niveau 3 — ORB 15m holdout-validatie

Periode: 18 april–30 september 2025. Alleen ORB 15m is de primaire hypothese. De overige drie schermen zijn referenties.

## Eindoordeel

**HOLDOUT_FAILED**. Dit is een historische vaste-regels-vervolgtest, geen prospectieve registratie of garantie voor live rendement.

| Maatstaf | Holdout | Gecombineerd dec 2024–sep 2025 |
|---|---:|---:|
| Eligible sessies | 81.000 | 123.000 |
| Trades | 76.000 | 113.000 |
| Netto NQ-punten | -627.600 | 291.825 |
| Netto USD, één NQ | -12,552.000 | 5,836.500 |
| Winrate (fractie) | 0.408 | 0.451 |
| Profit factor | 0.792 | 1.063 |
| Maximale gerealiseerde drawdown, punten | 1,047.775 | 1,047.775 |
| Maximale gerealiseerde drawdown, USD | 20,955.500 | 20,955.500 |
| Grootste verliesdag, punten | -236.225 | -236.225 |
| Beste 3 / netto winst (%) | niet beschikbaar | 298.235 |
| Netto zonder beste 3, punten | -1,141.675 | -578.500 |
| 95% CI ondergrens gemiddelde eligible dag | -19.881 | -11.123 |
| 95% CI bovengrens gemiddelde eligible dag | 3.466 | 17.802 |
| Tweezijdige bootstrap p | 0.203 | 0.743 |

Grootste verliesdag holdout: 2025-04-23. Drawdown is closed-trade equity, niet intratrade mark-to-market.

## Datadekking

117 geplande open civil-sessiondagen; 117 met bars; 81 eligible ORB15; 79 in de clean-sensitiviteit.
30 ontbrekende minuten in geselecteerde sessies na kalendercorrectie. Feestdagen worden als special_session gemarkeerd, niet automatisch als corrupt.
De primaire all-view vereist een volledige VWAP-prefix tot 12:00 en onveranderde ATR-/volumewarmup. Een gat na 12:00 kan in all-view blijven, maar niet in clean-view.
Good Friday 18 april is gesloten. De kalender gebruikt NY civil-sessiondagen zoals de bevroren engine, niet CME clearing TradeDate. Juli 4 kan daardoor apart van de officiële clearingdatum voorkomen.

## Rollover vooraf vastgelegd

- NQM25 → NQU25: beslissing 2025-06-16, volumes 169439 versus 262268; ingang 2025-06-17 (2025-06-16T22:00:00+00:00).
- NQU25 → NQZ25: beslissing 2025-09-16, volumes 94415 versus 320653; ingang 2025-09-17 (2025-09-16T22:00:00+00:00).

Vergelijking: eerste inkomende volume-overwicht in een afgesloten sessie; overstap volgende sessie. Geen strategie-uitkomsten gebruikt. Vorige sessievolume wordt vóór de volgende opening bekend verondersteld, niet vendor-vintage geverifieerd.

## Warmup en uitval per contract

| Contract | Sessies | ATR-ready | ORB15 eligible |
|---|---:|---:|---:|
| NQM25 | 41 | 41 | 39 |
| NQU25 | 66 | 48 | 42 |
| NQZ25 | 10 | 0 | 0 |

Geen ATR of historische volumereferentie tussen contracten overgedragen. Dunne pre-rollcontracten leveren onvoldoende volledige RTH-historie, vooral voor NQZ25. Niet-eligible dagen hebben geen backtestresultaat. Een volledig verzamelde kalenderperiode is dus geen volledig verhandelde holdout.

## Statistiek en kosten

Exact bevroren engine: 2 ticks slippage per kant plus $4,50 RT commissie = $24,50 = 1,225 NQ-punten. Signaal na voltooide bar, entry volgende minuutopen, stop vóór target bij beide geraakt, alle posities vóór 12:00 NY gesloten. Geen contractoverstap met open positie.
2000 circular moving-block bootstrapreplicaties, blokken van 5 eligible dagen, seed 20261020. CI is voor gemiddelde dag-PnL inclusief nullen op eligible dagen zonder trade. P-waarde tweezijdig rond gecentreerde nulverdeling. Kalendergaten tussen eligible dagen zijn niet gevuld met fictieve trades.
Enige primaire hypothese: ORB15, all-view. Geen multipliciteitscorrectie voor die ene primaire holdouttest. Referenties en clean-view zijn sensitiviteiten. Gecombineerde statistiek hergebruikt de ontdekkingsperiode en is geen onafhankelijke bevestiging.
Passregel vooraf: >=20 eligible dagen, positieve nettowinst, PF>1, CI-ondergrens>0 en p<0,05. Concentratierisico wordt gerapporteerd, geen achteraf toegevoegde passdrempel.

## Reproduceerbaarheid en beperkingen

Oorspronkelijke ORB15-ledger exact gereproduceerd: True. Frozen engine SHA-256: `8fbf6cb7ced7fe0338cca164de1f3cbde8b3d03eb92738bde4616829cd541d8b`.
Alle 30 bron-CSV-hashes staan in research/holdout-protocol.json. Ruwe bars, trades en Parquet blijven in genegeerde lokale mappen. Publiek alleen aggregaten en bron-/codehashes.
Historische CME-kalenderpagina toont inmiddels 2026. De historische sluitingen zijn gereconstrueerd uit onderstaande contemporaine data-aanbieder-/brokerschema’s en vergeleken met de bars; geen afzonderlijk gecertificeerd CME-2025-kalenderbestand. Geen toestemming tot herdistributie van ruwe Barchart-data verondersteld.

De blinde volgorde is lokaal in Git vastgelegd vóór de eerste signaalrun. De data waren vooraf op kwaliteit bekeken; dit is geen extern geregistreerde of onafhankelijk uitgevoerde studie. Na deze test is deze holdout verbruikt. Niet optimaliseren en dezelfde periode opnieuw als holdout presenteren.

Kalenderbronnen:

- https://www.cmegroup.com/trading-hours.html
- https://hedgingmarkets.com/wp-content/uploads/2025/02/CME-Good-Friday-2025-Holiday-Schedule.xlsx
- https://iqhelp.dtn.com/juneteenth-2025-holiday-exchange-schedule-2/
- https://iqhelp.dtn.com/fourth-of-july-service-hours-2025/
- https://iqhelp.dtn.com/labor-day-holiday-schedule-2025/
- https://help.oneuptrader.com/article/521-us-memorial-holiday-trading-schedule-2025

## Referentieschermen (niet promoten op basis van deze run)

| Scherm | Trades | Netto punten | PF | p |
|---|---:|---:|---:|---:|
| A_London_sweep | 44 | -374.900 | 0.765 | 0.436 |
| B_ORB5 | 78 | -619.050 | 0.818 | 0.439 |
| B_ORB15 | 76 | -627.600 | 0.792 | 0.203 |
| C_VWAP_extreme | 31 | -167.725 | 0.766 | 0.485 |
