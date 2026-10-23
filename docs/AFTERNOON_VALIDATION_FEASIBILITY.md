# Haalbaarheid onafhankelijke 15:00-toets

22 oktober 2026. Planning, geen nieuwe backtest of onafhankelijke toets. V2 en alle eerdere rapporten blijven ongewijzigd.

## Vrijgavebesluit

**Nog niet vrijgeven.** De steekproefgetallen hieronder zijn indicatieve planning, geen gecertificeerde minimumomvang. Naast de nog niet bewezen gratis dataroute toont de nulkalibratie dat de bevroren tweezijdige HAC(5)/t-meetlat in dit empirische blokmodel niet overal de nominale 5% familieverwerpingen haalt. Holm corrigeert multipliciteit maar herstelt geen verkeerd gekalibreerde ruwe p-waarden. De kandidaat of meetlat is niet aangepast; een aparte kalibratiebeoordeling hoort vóór een toekomstige toetsvrijgave.

## Steekproef en aannamen

De vaste 14:30 UP-groep telt 162 dagen: 37.24% van 435 complete RTH-dagen en 35.68% van 454 geplande sessies. Niet de dynamische 167-dagengroep.
Bij de planningsaanname van 250 geplande sessies/jaar: gemiddeld 89.2 geselecteerde dagen/jaar. Blokbootstrapband voor de frequentie: 76.5–103.0. Dit is een interval voor geschatte frequentie, geen voorspellingsinterval of kalendergarantie. De historische frequentie omvat ook initiële ATR-opwarming en afgekeurde sessies; de toekomstige proef warmt vooraf op. De Wilson-iid-band staat als beschrijvende gevoeligheid in JSON, niet als afhankelijkheidsrobuust alternatief.

Alle ontdekkingsgemiddelden zijn vóór simulatie verwijderd. +2/+4/+6 zijn hypothetische NETTO punten na de bestaande 1,225 punten frictie. Geen van deze scenario’s is gekozen als formele minimaal relevante edge. Alleen reeds verbruikte bronankers op bestaande cohortdagen zijn voor variantie gebruikt; geen signalen of uitslagtoets op het ontdekkingsgemiddelde.

| Horizon | SD iid pt | HAC(5)-equivalent pt | HAC/iid variantie |
|---|---:|---:|---:|
| 2m | 13.73 | 14.84 | 1.169 |
| 15m | 36.29 | 36.53 | 1.013 |

Gepaarde correlatie beide horizons: 0.591. Kalender-score-autocorrelaties lag 1–5 staan in de JSON. HAC(5) en de indicatornul op niet-geselecteerde dagen volgen v2.

## Benodigde geselecteerde dagen voor 80% positieve ondersteuning

Noncentral-t-planningsbenadering met tweezijdige alpha 0,025 per horizon. Dit is de strenge eerste Holm-drempel: een voldoende route voor die horizon, niet de exacte gezamenlijke familiesucceskans. HAC-equivalente SD wordt voor toekomstige N constant verondersteld. Jaaromrekening is een verwachting op de totale kalenderfrequentie.

| Netto effect pt | 2m: dagen | 2m: jaren | 15m: dagen | 15m: jaren |
|---|---:|---:|---:|---:|
| +2 | 526 | 5.90 | 3174 | 35.58 |
| +4 | 134 | 1.50 | 796 | 8.92 |
| +6 | 61 | 0.68 | 355 | 3.98 |

Jaarbandbreedte door onzekerheid in selectiefrequentie alleen (niet door variantie/regime/onbekende edge):

| Effect pt | 2m jarenband | 15m jarenband |
|---|---:|---:|
| +2 | 5.11–6.87 | 30.82–41.47 |
| +4 | 1.30–1.75 | 7.73–10.40 |
| +6 | 0.59–0.80 | 3.45–4.64 |

### Hogere toekomstige spreiding

| Horizon | Effect pt | SD-factor | Benodigde dagen | Jaren |
|---|---:|---:|---:|---:|
| 2m | +2 | 1.25 | 821 | 9.20 |
| 2m | +2 | 1.5 | 1180 | 13.23 |
| 2m | +4 | 1.25 | 207 | 2.32 |
| 2m | +4 | 1.5 | 297 | 3.33 |
| 2m | +6 | 1.25 | 94 | 1.05 |
| 2m | +6 | 1.5 | 134 | 1.50 |
| 15m | +2 | 1.25 | 4958 | 55.58 |
| 15m | +2 | 1.5 | 7138 | 80.02 |
| 15m | +4 | 1.25 | 1242 | 13.92 |
| 15m | +4 | 1.5 | 1787 | 20.03 |
| 15m | +6 | 1.25 | 554 | 6.21 |
| 15m | +6 | 1.5 | 796 | 8.92 |

## Gezamenlijke Holm2-power

5.000 simulaties per vaste kalenderlengte; circulaire blokken van 20 geplande sessies. Gepaarde gecentreerde residuen én selectie/kwaliteit blijven samen. Beide gemiddelden en HAC(5)-SE worden per synthetisch panel opnieuw berekend. Twee tweezijdige p-waarden, exacte Holm2-step-down en positief eigen gemiddelde. Geen inhoudelijke horizon-gate. Een effect op slechts één horizon en een effect op beide worden apart getoond.

| Geplande sessies | Verwachte geselecteerd | Effect 2m | Effect 15m | Positief familiesucces % | MC-SE procentpunt |
|---|---:|---:|---:|---:|---:|
| 125 | 44.7 | 2 | 0 | 8.18 | 0.39 |
| 125 | 44.7 | 4 | 0 | 31.24 | 0.66 |
| 125 | 44.7 | 6 | 0 | 69.34 | 0.65 |
| 125 | 44.7 | 0 | 2 | 4.68 | 0.30 |
| 125 | 44.7 | 0 | 4 | 8.40 | 0.39 |
| 125 | 44.7 | 0 | 6 | 14.68 | 0.50 |
| 125 | 44.7 | 2 | 2 | 9.40 | 0.41 |
| 125 | 44.7 | 4 | 4 | 32.78 | 0.66 |
| 125 | 44.7 | 6 | 6 | 69.44 | 0.65 |
| 250 | 89.4 | 2 | 0 | 15.66 | 0.51 |
| 250 | 89.4 | 4 | 0 | 61.96 | 0.69 |
| 250 | 89.4 | 6 | 0 | 97.00 | 0.24 |
| 250 | 89.4 | 0 | 2 | 5.78 | 0.33 |
| 250 | 89.4 | 0 | 4 | 12.44 | 0.47 |
| 250 | 89.4 | 0 | 6 | 26.00 | 0.62 |
| 250 | 89.4 | 2 | 2 | 17.30 | 0.53 |
| 250 | 89.4 | 4 | 4 | 62.50 | 0.68 |
| 250 | 89.4 | 6 | 6 | 96.86 | 0.25 |
| 500 | 178.5 | 2 | 0 | 32.52 | 0.66 |
| 500 | 178.5 | 4 | 0 | 93.32 | 0.35 |
| 500 | 178.5 | 6 | 0 | 100.00 | 0.00 |
| 500 | 178.5 | 0 | 2 | 8.04 | 0.38 |
| 500 | 178.5 | 0 | 4 | 22.80 | 0.59 |
| 500 | 178.5 | 0 | 6 | 48.60 | 0.71 |
| 500 | 178.5 | 2 | 2 | 33.78 | 0.67 |
| 500 | 178.5 | 4 | 4 | 93.18 | 0.36 |
| 500 | 178.5 | 6 | 6 | 99.94 | 0.03 |
| 1000 | 357.1 | 2 | 0 | 61.94 | 0.69 |
| 1000 | 357.1 | 4 | 0 | 99.98 | 0.02 |
| 1000 | 357.1 | 6 | 0 | 100.00 | 0.00 |
| 1000 | 357.1 | 0 | 2 | 12.76 | 0.47 |
| 1000 | 357.1 | 0 | 4 | 44.24 | 0.70 |
| 1000 | 357.1 | 0 | 6 | 81.32 | 0.55 |
| 1000 | 357.1 | 2 | 2 | 62.72 | 0.68 |
| 1000 | 357.1 | 4 | 4 | 99.92 | 0.04 |
| 1000 | 357.1 | 6 | 6 | 100.00 | 0.00 |
| 2000 | 713.9 | 2 | 0 | 91.88 | 0.39 |
| 2000 | 713.9 | 4 | 0 | 100.00 | 0.00 |
| 2000 | 713.9 | 6 | 0 | 100.00 | 0.00 |
| 2000 | 713.9 | 0 | 2 | 22.60 | 0.59 |
| 2000 | 713.9 | 0 | 4 | 76.18 | 0.60 |
| 2000 | 713.9 | 0 | 6 | 98.82 | 0.15 |
| 2000 | 713.9 | 2 | 2 | 91.72 | 0.39 |
| 2000 | 713.9 | 4 | 4 | 100.00 | 0.00 |
| 2000 | 713.9 | 6 | 6 | 100.00 | 0.00 |
| 4000 | 1427.7 | 2 | 0 | 99.82 | 0.06 |
| 4000 | 1427.7 | 4 | 0 | 100.00 | 0.00 |
| 4000 | 1427.7 | 6 | 0 | 100.00 | 0.00 |
| 4000 | 1427.7 | 0 | 2 | 44.66 | 0.70 |
| 4000 | 1427.7 | 0 | 4 | 97.40 | 0.23 |
| 4000 | 1427.7 | 0 | 6 | 100.00 | 0.00 |
| 4000 | 1427.7 | 2 | 2 | 99.76 | 0.07 |
| 4000 | 1427.7 | 4 | 4 | 100.00 | 0.00 |
| 4000 | 1427.7 | 6 | 6 | 100.00 | 0.00 |
| 8000 | 2855.1 | 2 | 0 | 100.00 | 0.00 |
| 8000 | 2855.1 | 4 | 0 | 100.00 | 0.00 |
| 8000 | 2855.1 | 6 | 0 | 100.00 | 0.00 |
| 8000 | 2855.1 | 0 | 2 | 76.22 | 0.60 |
| 8000 | 2855.1 | 0 | 4 | 100.00 | 0.00 |
| 8000 | 2855.1 | 0 | 6 | 100.00 | 0.00 |
| 8000 | 2855.1 | 2 | 2 | 100.00 | 0.00 |
| 8000 | 2855.1 | 4 | 4 | 100.00 | 0.00 |
| 8000 | 2855.1 | 6 | 6 | 100.00 | 0.00 |

### Nulkalibratie

| Sessies | Onterecht positief familiesucces % | Holm-verwerping enige richting % | MC-SE positief procentpunt |
|---|---:|---:|---:|
| 125 | 2.84 | 10.18 | 0.23 |
| 250 | 2.50 | 7.86 | 0.22 |
| 500 | 2.90 | 6.94 | 0.24 |
| 1000 | 2.40 | 5.82 | 0.22 |
| 2000 | 2.98 | 6.34 | 0.24 |
| 4000 | 3.16 | 6.76 | 0.25 |
| 8000 | 2.90 | 6.16 | 0.24 |

**Kalibratiewaarschuwing:** tweezijdige Holm-verwerping in enige richting varieert in dit nulmodel van 5.82% tot 10.18% in plaats van nominale 5%. Positief familiesucces varieert afzonderlijk van 2.40% tot 3.16%. Negatieve verwerpingen zijn geen positieve kandidaatondersteuning, maar vallen wel onder de tweezijdige FWER-afspraak. Monte-Carlo-SE van alle verwerpingen staat in de JSON. Dit blokmodel is geen universele marktwaarheid; de afwijking is reden voor kalibratieonderzoek, niet bewijs dat de geobserveerde markt-asymmetrie afwezig is. Powerpercentages worden daarom niet als gegarandeerde toetskwaliteit gebruikt.

## Selectiefrequentie per kwartaal

| Kwartaal | Gepland | Compleet | Geselecteerd | % gepland |
|---|---:|---:|---:|---:|
| 2024Q4 | 2 | 2 | 0 | 0.00 |
| 2025Q1 | 63 | 60 | 17 | 26.98 |
| 2025Q2 | 64 | 62 | 21 | 32.81 |
| 2025Q3 | 66 | 63 | 29 | 43.94 |
| 2025Q4 | 65 | 62 | 16 | 24.62 |
| 2026Q1 | 63 | 60 | 24 | 38.10 |
| 2026Q2 | 65 | 62 | 35 | 53.85 |
| 2026Q3 | 66 | 64 | 20 | 30.30 |

2024Q4 is slechts een gedeeltelijk kwartaal. Geen kwartaal is verwijderd of gebruikt om een filter te maken.

## Besluit en beperkingen

Een klein netto-effect vraagt aanzienlijk meer informatie dan een groot effect. Een kort forwardtraject is geen gegarandeerde bevestiging; zonder uitkomstgestuurd verlengen moet onvoldoende informatie herkenbaar blijven. De steekproefomvang voor een definitieve toets is nog NIET vastgelegd.

De berekeningen zijn gevoelig voor slechts 162 geselecteerde ontdekkingsdagen, historische selectie van de kandidaat, regimeverandering, staarten, datakwaliteit en blocklengte. De cirkelverbinding en herhaling van een kort verleden kunnen toekomstige crises niet reconstrueren. De SD-sensitiviteiten zijn scenario’s, geen betrouwbaarheidsgrenzen. Geen tick-/bid-ask-/latencybewijs of echte fillvalidatie. +2/+4/+6 punten betreffen het ongewijzigde kostenmodel, niet gegarandeerde uitvoerbaarheid.

## Reproductie en bronnen

`python -m scripts.afternoon_feasibility` schrijft uitsluitend nieuwe planningsoutputs; geen bestaande rapporten of bronbestanden. Seed, protocol, hashes en alle scenario’s staan in `research/afternoon-feasibility-results.json`. De bronankers zijn niet openbaar geëxporteerd.

- [SciPy noncentral-t documentatie](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html).
- [Holm (1979), oorspronkelijke procedure](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf).
