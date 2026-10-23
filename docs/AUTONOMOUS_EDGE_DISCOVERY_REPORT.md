# AUTONOMOUS EDGE DISCOVERY REPORT

22 oktober 2026. Alle vijf aangevraagde fasen zijn uitgevoerd. Eén begrensde ronde met25 vooraf vastgelegde uitkomsten, geen parametergrid. Geen nieuwe synthetische kalibratie, aankoop, download of externe publicatie. Beschermde archieven en de v2-specificatie blijven byte-identiek.

## Eindoordeel

**Geen nieuw model is als robuust, onafhankelijk gevalideerd winstgevend model aangetoond.** De15:00-2 minutenregel voldoet op de verbruikte ontdekkingsdata aan de operationele ontdekkingsschermen, maar de oudere continuous-bron geeft juist een negatieve tegenuitkomst. Die bron is niet gecertificeerd en de individuele-contractfragmenten zijn te klein voor bevestiging. Geen reddingsfilter of omgekeerd signaal toegevoegd.

Onderzocht:435 vaste RTH-dagen; 186 lokale CSV-paden /109 unieke byte-inhouden. Extra technische sessies tellen per bron op tot558, maar zijn niet allemaal onafhankelijk: 539 verschillende extra kalenderdatums. Overlappende vendors worden nooit gepoold.

## Vooraf vastgelegde keuzes en grenzen

- ToM1A: exact10:00, bevestiging09:59 close boven09:30 open. Geen10:30/VWAP-alternatieven uitgeprobeerd.
- ToM1B:18:00 open tot10:29 close. ToM-signaal is alleen kalenderafhankelijk en dus vóór entry bekend. Volledigheid van de latere nacht is uitsluitend een technische evaluatiepoort, niet een vooruitkijkend handelsfilter.
- ToM1C: uitsluiting boven vooraf bekendeP90 van60 eerdere bekende ATR14-waarnemingen, geen halvering/sizing. Ontbrekende opwarming is geen laag-volatiel regime.
- Vrijdag: twee vooraf expliciet concurrerende richtingen vanaf13:30 op basis van de weektrend. Inventory: efficiency>=0,70, range<=0,8 ATR en RVOL>=1,5 op20 vooraf volledige nachten. Geen drempel versoepeld nadat nul events bleek.
- Compressie: alleen gesloten5m-bars, eerste bevestiging, volgende baropen, vaste RTH-close. Sweep: exact één kant, bevestiging na eerste30 minuten, twee vaste uitstappen. Geen stops of targets die de 1m-intrabarvolgorde zouden veronderstellen.
-12 kalender/ATR-interactiecellen plus de ongewijzigde v2-referentie zijn afzonderlijke verkennende uitkomsten. Geen aanpassing van v2, geen nieuwe actuele modelpointer.
- EénNQ,1,225 punt/$24,50 per ronde. Alle entries opbaropen na bevestiging; exits op een vooraf vastgelegde voltooide close. Geen tick/BBO-fillcertificering. Slippage-stress is aanvullend, geen bewijs dat de basisfrictie historisch toereikend was.

## Fase1 — Maandwisseling ontmanteld

### Volledig tijdpad van alle81 oorspronkelijke ToM-dagen

| Deelvenster | N | Gemiddeld bruto pt | P10 | Mediaan | P90 |
|---|---:|---:|---:|---:|---:|
| overnight_points | 78 | -5.89 | -222.82 | 2.00 | 208.90 |
| opening_gap | 78 | 0.19 | -0.50 | 0.25 | 0.75 |
| morning | 81 | 39.43 | -167.00 | 47.50 | 212.00 |
| midday | 81 | 2.69 | -163.00 | 26.75 | 145.25 |
| afternoon | 81 | 12.95 | -104.25 | 19.00 | 129.50 |
| bridge1100 | 81 | 0.04 | -0.75 | 0.00 | 0.75 |
| bridge1400 | 81 | -0.02 | -0.50 | 0.00 | 0.50 |
| rth_points | 81 | 55.10 | -223.50 | 91.75 | 329.50 |

Morning=09:30–11:00, midday=11:00–14:00, afternoon=14:00–16:00; overnight=18:00–09:30. Endpoint is steeds de laatste voltooide minuutclose. De twee interbarbruggen maken de som exact gelijk aan de brutoRTH-beweging. De openinggap verbindt09:29 close met09:30 open. Alle81 dagen blijven staan; slechts78 hebben de volledige nacht voor de overnightvergelijking. Geen overnight-toeschrijving uit onvolledige bars.

### Dagpositie binnen het vierdaagse venster

| Positie | N RTH | Ochtend gem. | Middag gem. | Slotdeel gem. | Totaal RTH gem. |
|---|---:|---:|---:|---:|---:|
| T-1 | 20 | -6.96 | -1.84 | 51.04 | 42.25 |
| T+1 | 21 | 66.01 | 10.93 | -18.95 | 57.88 |
| T+2 | 20 | 69.71 | -17.12 | 31.27 | 84.16 |
| T+3 | 20 | 27.64 | 18.40 | -9.95 | 35.98 |

### Grootste verliesdagen: waar ontstond het verlies?

| Dag | Positie | Ochtend pt | Middag pt | Slotdeel pt | Bruto RTH pt |
|---|---|---:|---:|---:|---:|
| 2025-03-03 | T+1 | -198.25 | -110.75 | -273.75 | -582.75 |
| 2026-07-02 | T+2 | -236.00 | -501.75 | 198.50 | -538.25 |
| 2026-02-03 | T+2 | -317.25 | -372.00 | 200.00 | -489.25 |
| 2025-07-31 | T-1 | -205.25 | -151.75 | -35.75 | -393.25 |
| 2026-02-04 | T+3 | -233.25 | -227.25 | 71.00 | -391.00 |

De verliesdag3 maart2025 is niet alleen een vroege capitulatie: ook na14:00 gaat273,75 punt verloren. Andere grote verliezen worden juist in de middag gedeeltelijk teruggewonnen. Dit is tijdpadbeschrijving, geen reden om achteraf een nieuw uitstaptijdstip te kiezen.

### De drie vaste varianten tegenover de ongewijzigde basis

| Model | N | Netto pt | PF | Win% | Positieve kwartalen | 95% MBB5 gemiddelde | Holm25 signflip |
|---|---:|---:|---:|---:|---|---|---:|
| TOM_RTH | 81 | 4364.02 | 1.706 | 64.20 | 5/7 | [1.82; 105.68] | 1.00000 |
| TOM_TREND_1000 | 50 | 1170.50 | 1.314 | 68.00 | 5/7 | [-32.59; 84.16] | 1.00000 |
| TOM_OVERNIGHT_1030 | 78 | 2274.95 | 1.443 | 56.41 | 4/7 | [-16.80; 73.67] | 1.00000 |
| TOM_ATR_CAP | 61 | 2491.28 | 1.516 | 60.66 | 4/6 | [-24.35; 107.51] | 1.00000 |

ATR-cap op vergelijkbare voorgeschiedenis: 66 ToM-dagen hebben de60 ATR-waarnemingen. De baseline op precies die voorgeschiedenis levert3149.90 punt; de cap2491.28 punt. 15 vroegeToM-dagen vallen weg door ontbrekende opwarming. Die verandering mag niet aan de cap worden toegeschreven.

**Geen van de drie varianten heeft een positieve95%-ondergrens.** De basis is exact dezelfde81 trades/+4.364,025 punt als tevoren. Het nieuwe MBB5-interval ligt nipt boven nul, terwijl de eerder vastgelegde maandblok-bootstrap[-0,11;+111,69] bevatte. Dat is gevoeligheid voor de onzekerheidsmethode, geen verbetering van de strategie. Beide blijven zichtbaar; Holm25 geeft de basis geen significantie.

## Fase2 — Volledige Master Scorecard

Alle25 uitkomsten staan hieronder, inclusief lege cellen. Rangschikking: eerst het vooraf gedefinieerde ontdekkingsscherm, dan Holm25-signflip, danPF; geen keuze op één fraai kwartaal.

| Rang | Model | N | Netto pt | PF | Win% | Kwartalen +% | 95% MBB5 | Ruwe signflip p | Holm25 | Groep8 Holm25 |
|---:|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | AFTERNOON_V2_2 | 162 | 724.05 | 2.511 | 63.58 | 100.00 | [2.27; 6.81] | 0.000050 | 0.001250 | 1.000000 |
| 2 | AFTERNOON_TOM_YES_MID_2 | 13 | 140.08 | 9.156 | 76.92 | 100.00 | [2.53; 20.88] | 0.014648 | 0.351562 | 1.000000 |
| 3 | AFTERNOON_TOM_NO_HIGH_2 | 32 | 220.55 | 3.131 | 65.62 | 80.00 | [0.99; 12.46] | 0.018320 | 0.421360 | 1.000000 |
| 4 | AFTERNOON_V2_15 | 162 | 1084.80 | 1.699 | 58.02 | 71.43 | [0.91; 12.16] | 0.020000 | 0.440000 | 1.000000 |
| 5 | AFTERNOON_TOM_YES_HIGH_2 | 6 | 58.40 | n.v.t. | 100.00 | 100.00 | [5.28; 14.38] | 0.031250 | 0.656250 | 1.000000 |
| 6 | AFTERNOON_TOM_YES_HIGH_15 | 6 | 136.40 | 13.179 | 66.67 | 100.00 | [4.59; 39.27] | 0.125000 | 1.000000 | 1.000000 |
| 7 | AFTERNOON_TOM_YES_LOW_15 | 11 | 84.03 | 2.745 | 63.64 | 60.00 | [-4.89; 23.74] | 0.286133 | 1.000000 | 1.000000 |
| 8 | AFTERNOON_TOM_YES_LOW_2 | 11 | 29.52 | 2.624 | 72.73 | 80.00 | [-2.42; 6.67] | 0.224609 | 1.000000 | 1.000000 |
| 9 | AFTERNOON_TOM_NO_MID_2 | 38 | 145.95 | 2.189 | 50.00 | 66.67 | [-1.03; 9.80] | 0.134280 | 1.000000 | 1.000000 |
| 10 | AFTERNOON_TOM_NO_HIGH_15 | 32 | 268.55 | 1.828 | 62.50 | 80.00 | [-4.22; 19.14] | 0.221140 | 1.000000 | 1.000000 |
| 11 | TOM_RTH | 81 | 4364.02 | 1.706 | 64.20 | 71.43 | [1.82; 105.68] | 0.053820 | 1.000000 | 1.000000 |
| 12 | AFTERNOON_TOM_NO_MID_15 | 38 | 243.70 | 1.665 | 55.26 | 66.67 | [-5.97; 20.76] | 0.363980 | 1.000000 | 1.000000 |
| 13 | AFTERNOON_TOM_YES_MID_15 | 13 | 107.07 | 1.616 | 69.23 | 75.00 | [-16.04; 24.87] | 0.553467 | 1.000000 | 1.000000 |
| 14 | TOM_ATR_CAP | 61 | 2491.28 | 1.516 | 60.66 | 66.67 | [-24.35; 107.51] | 0.198360 | 1.000000 | 1.000000 |
| 15 | FRIDAY_CONT | 85 | 1345.88 | 1.450 | 50.59 | 85.71 | [-9.13; 41.87] | 0.232780 | 1.000000 | 1.000000 |
| 16 | SWEEP_REV_1200 | 63 | 1396.83 | 1.445 | 50.79 | 71.43 | [-17.64; 70.28] | 0.362160 | 1.000000 | 1.000000 |
| 17 | TOM_OVERNIGHT_1030 | 78 | 2274.95 | 1.443 | 56.41 | 57.14 | [-16.80; 73.67] | 0.220720 | 1.000000 | 1.000000 |
| 18 | COMPRESSED_BREAK5 | 109 | 2119.48 | 1.356 | 54.13 | 71.43 | [-13.88; 54.10] | 0.212790 | 1.000000 | 1.000000 |
| 19 | TOM_TREND_1000 | 50 | 1170.50 | 1.314 | 68.00 | 71.43 | [-32.59; 84.16] | 0.456340 | 1.000000 | 1.000000 |
| 20 | AFTERNOON_TOM_NO_LOW_2 | 43 | 16.82 | 1.119 | 58.14 | 50.00 | [-2.47; 3.41] | 0.784820 | 1.000000 | 1.000000 |
| 21 | SWEEP_REV_1600 | 63 | -98.93 | 0.978 | 55.56 | 42.86 | [-48.93; 46.62] | 0.949870 | 1.000000 | 1.000000 |
| 22 | AFTERNOON_TOM_NO_LOW_15 | 43 | -20.42 | 0.954 | 48.84 | 33.33 | [-10.50; 8.93] | 0.917270 | 1.000000 | 1.000000 |
| 23 | FRIDAY_REVERT | 85 | -1554.12 | 0.651 | 45.88 | 14.29 | [-43.72; 6.88] | 0.168440 | 1.000000 | 1.000000 |
| 24 | ON_INVENTORY_CONT | 0 | 0.00 | n.v.t. | n.v.t. | n.v.t. | n.v.t. | 1.000000 | 1.000000 | 1.000000 |
| 25 | ON_INVENTORY_REVERT | 0 | 0.00 | n.v.t. | n.v.t. | n.v.t. | n.v.t. | 1.000000 | 1.000000 | 1.000000 |

### Onvoorwaardelijke benchmark per model

| Model | Gem. netto pt | Zelfde klok/directionele benchmark | Verschil pt | Zelfde eventdagen blind long |
|---|---:|---:|---:|---:|
| AFTERNOON_V2_2 | 4.47 | 0.75 | 3.72 | 4.47 |
| AFTERNOON_TOM_YES_MID_2 | 10.78 | 0.75 | 10.02 | 10.78 |
| AFTERNOON_TOM_NO_HIGH_2 | 6.89 | 0.75 | 6.14 | 6.89 |
| AFTERNOON_V2_15 | 6.70 | -0.43 | 7.13 | 6.70 |
| AFTERNOON_TOM_YES_HIGH_2 | 9.73 | 0.75 | 8.98 | 9.73 |
| AFTERNOON_TOM_YES_HIGH_15 | 22.73 | -0.43 | 23.17 | 22.73 |
| AFTERNOON_TOM_YES_LOW_15 | 7.64 | -0.43 | 8.07 | 7.64 |
| AFTERNOON_TOM_YES_LOW_2 | 2.68 | 0.75 | 1.93 | 2.68 |
| AFTERNOON_TOM_NO_MID_2 | 3.84 | 0.75 | 3.09 | 3.84 |
| AFTERNOON_TOM_NO_HIGH_15 | 8.39 | -0.43 | 8.83 | 8.39 |
| TOM_RTH | 53.88 | 2.01 | 51.87 | 53.88 |
| AFTERNOON_TOM_NO_MID_15 | 6.41 | -0.43 | 6.85 | 6.41 |
| AFTERNOON_TOM_YES_MID_15 | 8.24 | -0.43 | 8.67 | 8.24 |
| TOM_ATR_CAP | 40.84 | 2.01 | 38.83 | 40.84 |
| FRIDAY_CONT | 15.83 | -1.13 | 16.97 | -16.98 |
| SWEEP_REV_1200 | 22.17 | -1.22 | 23.39 | -4.97 |
| TOM_OVERNIGHT_1030 | 29.17 | 7.24 | 21.93 | 29.17 |
| COMPRESSED_BREAK5 | 19.44 | -1.07 | 20.51 | -4.29 |
| TOM_TREND_1000 | 23.41 | 2.18 | 21.23 | 23.41 |
| AFTERNOON_TOM_NO_LOW_2 | 0.39 | 0.75 | -0.36 | 0.39 |
| SWEEP_REV_1600 | -1.57 | -1.28 | -0.29 | -6.48 |
| AFTERNOON_TOM_NO_LOW_15 | -0.47 | -0.43 | -0.04 | -0.47 |
| FRIDAY_REVERT | -18.28 | -1.32 | -16.97 | -16.98 |
| ON_INVENTORY_CONT | n.v.t. | n.v.t. | n.v.t. | n.v.t. |
| ON_INVENTORY_REVERT | n.v.t. | n.v.t. | n.v.t. | n.v.t. |

Voor variabele5m-entry wordt de identieke entry-/exitklok op alle complete dagen gebruikt, met dezelfde oriëntatie en kosten. Dit is een beschrijvende benchmark, geen causaal experiment of extra p-toets. Voor overnight staan alleen nachten met de volledige vereiste vensters in de benchmark.

### Waarom inventory geen events gaf

```json
{
  "counts": {
    "total": 435,
    "complete_overnight": 413,
    "known_atr": 397,
    "known_20night_rvol": 110,
    "efficiency_at_least_07": 22,
    "range_at_most_08atr": 74,
    "rvol_at_least_15": 9,
    "all_three_conditions": 0
  },
  "interpretation": "Zero events is feasibility/data insufficiency, not evidence that the inventory mechanism is false. No conditions relaxed after inspection. Individual-condition counts use the same final known-history population, not successive conditional counts."
}
```

### Toetsmethode en grenzen

-10.000 MBB5-resamples op de oorspronkelijke weekdagkalender, dagclusters en ratio somP&L/aantal geselecteerde events. Niet-geselecteerde dagen zijn nul-invloed, geen verzonnen nultrade. Nominale95%-intervallen, niet gelijktijdig over25 modellen.
- Tweezijdige signflip van hele dagclusters: exacte enumeratie bij<=16 eventdagen, anders99.999 MonteCarlo-trekkingen met plus-onecorrectie. De **Holm-formule is exact**, de MonteCarlo-ruwe p is **niet exact**. Geldigheid veronderstelt passende gezamenlijke teken-symmetrie; niet universeel gewaarborgd bij seriële afhankelijkheid.
- De conservatieve toets gebruikt dezelfde8 blokken,20 weekdag-gaps, SE×sqrt(1,25), tdf7, minimaal8 events/blok én120 gescoorde events totaal. Geen poort verlaagd of nieuwe kalibratie gestart. De162v2-events leveren na vaste gaps109 gescoorde events: DATA_INSUFFICIENT, p1. Een signflip-succes wordt niet verkocht als goedkeuring door die conservatieve toets.
- De originele v2 HAC5/Holm2-uitvoer wordt als afzonderlijke, ongewijzigde-receptreplay weergegeven; geen aanpassing van de bevroren specificatie. Deze ontdekkingsronde en fragmenten zijn niet het oorspronkelijke definitieve fixed-end holdoutvenster.

## Fase3 — Alle lokale bronnen en de aparte historische controles

| Bron/fragment | Periode | Complete dagen | Blootstellings-/validatiestatus |
|---|---|---:|---|
| CONTRACT_2018_WARMUP | 2018-11-19–2018-12-31 | 26 | ADDITIONAL_HISTORICAL_WARMUP_EXPLORATORY |
| CONTRACT_2019_FRAGMENT | 2019-01-02–2019-01-11 | 8 | SMALL_HISTORICAL_REPLICATION_FRAGMENT_NOT_FIXED_END_TEST |
| CONTRACT_PILOT_2024 | 2024-01-22–2024-02-16 | 19 | PRIOR_TECHNICAL_PILOT_NO_CERTIFIED_ABSOLUTE_BLINDNESS |
| CONTINUOUS_2022_2024_UNVERIFIED | 2022-12-27–2024-12-27 | 493 | Prior project exposure; missing contract chain; backadjustment and timestamp publication-vintage unverified. Static-vintage sensitivity, NOT independent causal NQ validation. |
| VENDOR_SAMPLE_OCT2026 | 2026-10-01–2026-10-16 | 12 | No explicit contract identity or overlap warmup. Already downloaded historical sample, not prospective forward. |

AlleCSV’s zijn gehasht en byte-identieke kopieën gegroepeerd. De69 geregistreerde ontdekkingsbronnen zijn opnieuw streng geladen. Hogere timeframes worden niet opgeschaald. De grote continuous-reeks is alleen vóór30 december2024 gescoord, ET bar-endlabel vast één minuut terug, zoals reeds vóór deze ronde gedocumenteerd. De FirstRate-sample is een gedownloade historische oktober2026 sample, geen na preregistratie verzamelde forwardreeks.

Contractfragment2018 gebruikt de vastgelegde volume-overgang14 december/activatie17 december en causale additive offsets voor indicatoren, nooit voor ruwe fills. De acht januaridagen krijgen uitsluitend vooraf bekende opwarming. H24 en de FirstRate-sample lenen geen ontbrekende60 ATR-dagen van een andere leverancier of een ander jaar.

Historische selectie vóór inzage: besteToM-variant opPF onder positievePF>1,30 varianten = **TOM_ATR_CAP**. Verder v2-paar,ToM-basis als referentie en alle positievePF>1,30 fase2 rijen. Exacte lijst staat in historical-release.json. Niet-geselecteerde modellen krijgen geen nieuwe historische outcome-evaluatie en blijven p1 in de familie. Daarnaast Holm over alle125 rijen van de vijf bron/fragmentfamilies; geen gunstigste bron uitzoeken.

| Fragment | Model | N | Netto pt | PF | 95% MBB5 gemiddelde | Holm alle historische bronnen |
|---|---|---:|---:|---:|---|---:|
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_NO_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_NO_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_NO_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_NO_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_YES_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_YES_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_YES_LOW_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_YES_LOW_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_YES_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_TOM_YES_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_V2_15 | 3 | -26.68 | 0.288 | [-10.35; 10.78] | 1.000000 |
| CONTRACT_2018_WARMUP | AFTERNOON_V2_2 | 3 | -25.18 | 0.067 | [-26.98; 1.52] | 1.000000 |
| CONTRACT_2018_WARMUP | COMPRESSED_BREAK5 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | FRIDAY_CONT | 5 | 152.38 | 3.531 | [-18.48; 77.97] | 1.000000 |
| CONTRACT_2018_WARMUP | SWEEP_REV_1200 | 6 | 160.15 | 19.355 | [7.69; 39.13] | 1.000000 |
| CONTRACT_2018_WARMUP | TOM_ATR_CAP | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2018_WARMUP | TOM_RTH | 5 | -52.63 | 0.809 | [-74.14; 181.03] | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_NO_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_NO_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_NO_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_NO_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_YES_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_YES_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_YES_LOW_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_YES_LOW_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_YES_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_TOM_YES_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_15 | 4 | 30.85 | 3.631 | [5.07; 19.27] | 1.000000 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_2 | 4 | 16.35 | n.v.t. | [3.78; 6.40] | 1.000000 |
| CONTRACT_2019_FRAGMENT | COMPRESSED_BREAK5 | 4 | -211.65 | 0.111 | [-98.22; 3.65] | 1.000000 |
| CONTRACT_2019_FRAGMENT | FRIDAY_CONT | 2 | 7.55 | 1.504 | [-14.97; 22.52] | 1.000000 |
| CONTRACT_2019_FRAGMENT | SWEEP_REV_1200 | 2 | 16.80 | 5.226 | [4.27; 20.77] | 1.000000 |
| CONTRACT_2019_FRAGMENT | TOM_ATR_CAP | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_2019_FRAGMENT | TOM_RTH | 3 | 216.33 | 2.803 | [27.65; 175.28] | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_NO_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_NO_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_NO_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_NO_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_YES_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_YES_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_YES_LOW_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_YES_LOW_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_YES_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_TOM_YES_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_V2_15 | 1 | 0.03 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | AFTERNOON_V2_2 | 1 | -1.73 | 0.000 | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | COMPRESSED_BREAK5 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | FRIDAY_CONT | 4 | 90.85 | 7.067 | [-10.91; 36.27] | 1.000000 |
| CONTRACT_PILOT_2024 | SWEEP_REV_1200 | 3 | 74.83 | 1.921 | [-81.22; 110.28] | 1.000000 |
| CONTRACT_PILOT_2024 | TOM_ATR_CAP | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| CONTRACT_PILOT_2024 | TOM_RTH | 4 | 164.10 | 1.867 | [-162.47; 108.86] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 44 | -210.40 | 0.457 | [-10.25; 0.39] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 44 | -296.90 | 0.142 | [-9.63; -3.80] | 0.002480 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 44 | 90.35 | 1.319 | [-3.06; 7.14] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 44 | -179.40 | 0.326 | [-8.70; -0.75] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_15 | 13 | -27.43 | 0.718 | [-15.31; 7.87] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 13 | 23.32 | 1.442 | [-5.55; 9.75] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_15 | 13 | -188.92 | 0.280 | [-33.73; 3.58] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_2 | 13 | -69.17 | 0.164 | [-10.86; -1.09] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_15 | 13 | -88.67 | 0.466 | [-18.73; 5.82] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_2 | 13 | -50.68 | 0.296 | [-7.88; -0.32] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 205 | -565.12 | 0.699 | [-5.68; 0.11] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 205 | -667.13 | 0.413 | [-4.82; -1.73] | 0.001250 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 106 | 1306.40 | 1.271 | [-15.13; 40.89] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 99 | -232.77 | 0.910 | [-14.69; 11.90] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 70 | 588.50 | 1.272 | [-12.98; 31.33] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 61 | 588.02 | 1.191 | [-19.57; 40.48] | 1.000000 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 90 | 1440.25 | 1.322 | [-13.63; 44.63] | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_NO_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_NO_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_NO_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_NO_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_YES_HIGH_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_YES_HIGH_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_YES_LOW_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_YES_LOW_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_YES_MID_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_TOM_YES_MID_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_V2_15 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | AFTERNOON_V2_2 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | COMPRESSED_BREAK5 | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | FRIDAY_CONT | 2 | 133.80 | n.v.t. | [22.52; 111.28] | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | SWEEP_REV_1200 | 2 | 9.05 | 1.101 | [-89.47; 98.53] | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | TOM_ATR_CAP | 0 | 0.00 | n.v.t. | n.v.t. | 1.000000 |
| VENDOR_SAMPLE_OCT2026 | TOM_RTH | 3 | 177.32 | 2.706 | [-51.97; 281.27] | 1.000000 |

**Bronstatus is bepalend:** de493 oudere complete sessies geven meer informatie dan acht dagen, maar de contractketen, adjustmentmethode, publicatievintages en absolute eerdere niet-inzage zijn niet bewezen. Die resultaten zijn een afzonderlijke static-vintage-brongevoeligheidscontrole, niet gecertificeerd onafhankelijk point-in-time bewijs. De H24-datums overlappen grotendeels met die bron; geen onafhankelijke replicaties optellen.

### Gedocumenteerde volledigheidscorrectie: geen waargenomen verliestrade

Eén reeds vastgelegde cel, AFTERNOON_TOM_YES_HIGH_2, heeft6 winnaars en dus geen eindige geschattePF. De eerste mechanische selectie behandelde PF=n.v.t. als niet-kwalificerend. Om geen all-win-cel aan de historische controle te onttrekken, is die cel aanvullend geëvalueerd. Het oorspronkelijke bronslot, de oorspronkelijke selectierelease en originele historische uitvoer zijn bewaard. Een apart addendum is vastgelegd vóór uitkomstberekening van deze ontbrekende cel. Geen nieuwe hypothese, filter, horizon, periode of kleinere familie; alle25/125 correcties zijn opnieuw inclusief die cel berekend. De no-lossPF blijft n.v.t., niet een als bewezen verkochte oneindigePF. Dit is een expliciete volledigheidscorrectie ná de eerste geselecteerde bronuitkomsten, geen claim dat het addendum een onafhankelijke preregistratie is.

### Vaste-conventie bronvergelijking op reeds verbruikte overlap

```json
{
  "status": "FIXED_TIMESTAMP_CONVENTION_SOURCE_PARITY_CHECK",
  "common_rth_minutes": 94348,
  "common_days": 246,
  "volume_exact_fraction": 0.8945499639632001,
  "minute_open_close_move_exact_fraction": 0.912621359223301,
  "minute_range_exact_fraction": 0.9779645567473608,
  "daily_close_offset_constant_fraction": 0.02032520325203252,
  "minute_open_close_difference_abs_median": 0.0,
  "fifteen00_two_minute_anchor_days": 237,
  "fifteen00_two_minute_move_exact_fraction": 0.9451476793248945,
  "fifteen00_two_minute_move_difference_abs_median": 0.0,
  "source_sha256": "1577e60a7feab411e49da7a56c7052a64738cd1757cfd60aa11fd783ff43b60b",
  "caveat": "Common observed2024-2025dates only, not proof of older contract chain or vendor independence. Shared feed possible. No shift search, no rules changed, no certification of publication vintage or tick fills."
}
```

### Overige lokale containers: geen gemiste NQ-historie

Ook de bekende project-Parquet/ZIP-containers zijn metadata-only gecontroleerd, zonder archieven uit te pakken of CFDs als futures te herlabelen. De afgeleide NQ-master bevat106.678 reeds verbruikte bars. De twee USATECHIDXUSD-Parquetbestanden zijn elk1.440 Dukascopy-CFD-bars; de NSXUSD-archieven zijn geen NQ-contractbestanden of niet-importeerbare ZIPs. Geen extra ongebruikte NQ-holdout gevonden in deze bekende containers.

| Bestand | Rijen indien Parquet | Classificatie |
|---|---:|---|
| USATECHIDXUSD-1m.parquet | 1440 | DUKASCOPY_INDEX_CFD_NOT_CME_NQ_FUTURES |
| USATECHIDXUSD-1m.parquet | 1440 | DUKASCOPY_INDEX_CFD_NOT_CME_NQ_FUTURES |
| NQ_point_in_time_1min.parquet | 106678 | DERIVED_ALREADY_CONSUMED_NQ_MASTER_NOT_ADDITIONAL_HISTORY |
| 2024.zip | n.v.t. | HISTDATA_NSXUSD_CFD_ARCHIVE_NOT_NQ_CONTRACTS |
| 2025.zip | n.v.t. | HISTDATA_NSXUSD_CFD_ARCHIVE_NOT_NQ_CONTRACTS |

Dit betreft de afgesproken projectdatamappen en bekende containers, niet de volledige persoonlijke schijf. Private metadata/hashes staan in non-csv-containers.json.

### Bevroren v2: oorspronkelijke inferentie afzonderlijk

```json
{
  "discovery": [
    {
      "horizon": 2,
      "n": 162,
      "status": "FROZEN_HAC5_FRAGMENT_ONLY",
      "delta": 4.469444444444444,
      "se_HAC5": 1.1659368255475682,
      "se_CR1": 1.0785582504904143,
      "ci95": [
        2.166942966881715,
        6.771945922007173
      ],
      "p_raw": 0.00018098248701005134,
      "df": 161,
      "event_days": 162,
      "p_holm2": 0.0003619649740201027
    },
    {
      "horizon": 15,
      "n": 162,
      "status": "FROZEN_HAC5_FRAGMENT_ONLY",
      "delta": 6.696296296296297,
      "se_HAC5": 2.870031942932051,
      "se_CR1": 2.85094247871437,
      "ci95": [
        1.0285339918079792,
        12.364058600784615
      ],
      "p_raw": 0.02087547365395604,
      "df": 161,
      "event_days": 162,
      "p_holm2": 0.02087547365395604
    }
  ],
  "historical": {
    "CONTRACT_2018_WARMUP": [
      {
        "horizon": 2,
        "n": 3,
        "status": "FROZEN_HAC5_FRAGMENT_ONLY",
        "delta": -8.391666666666667,
        "se_HAC5": 9.224313685199728,
        "se_CR1": 9.29867075327317,
        "ci95": [
          -48.0806851243566,
          31.297351791023267
        ],
        "p_raw": 0.45899157627005865,
        "df": 2,
        "event_days": 3,
        "p_holm2": 0.7303366110735993
      },
      {
        "horizon": 15,
        "n": 3,
        "status": "FROZEN_HAC5_FRAGMENT_ONLY",
        "delta": -8.891666666666667,
        "se_HAC5": 7.652311439713519,
        "se_CR1": 12.28340117575114,
        "ci95": [
          -41.816905371643074,
          24.033572038309742
        ],
        "p_raw": 0.36516830553679963,
        "df": 2,
        "event_days": 3,
        "p_holm2": 0.7303366110735993
      }
    ],
    "CONTRACT_2019_FRAGMENT": [
      {
        "horizon": 2,
        "n": 4,
        "status": "FROZEN_HAC5_FRAGMENT_ONLY",
        "delta": 4.0875,
        "se_HAC5": 1.1851676657052927,
        "se_CR1": 1.511673327805978,
        "ci95": [
          0.31576754113447514,
          7.859232458865526
        ],
        "p_raw": 0.04097009686499666,
        "df": 3,
        "event_days": 4,
        "p_holm2": 0.08194019372999332
      },
      {
        "horizon": 15,
        "n": 4,
        "status": "FROZEN_HAC5_FRAGMENT_ONLY",
        "delta": 7.7125,
        "se_HAC5": 5.135839232107597,
        "se_CR1": 7.195466599417534,
        "ci95": [
          -8.632032588751935,
          24.057032588751937
        ],
        "p_raw": 0.23017572605016623,
        "df": 3,
        "event_days": 4,
        "p_holm2": 0.23017572605016623
      }
    ],
    "CONTRACT_PILOT_2024": [
      {
        "horizon": 2,
        "n": 1,
        "p_raw": 1.0,
        "status": "DATA_INSUFFICIENT",
        "p_holm2": 1.0
      },
      {
        "horizon": 15,
        "n": 1,
        "p_raw": 1.0,
        "status": "DATA_INSUFFICIENT",
        "p_holm2": 1.0
      }
    ],
    "CONTINUOUS_2022_2024_UNVERIFIED": [
      {
        "horizon": 2,
        "n": 205,
        "status": "FROZEN_HAC5_FRAGMENT_ONLY",
        "delta": -3.254268292682928,
        "se_HAC5": 0.7895340312577798,
        "se_CR1": 0.7366673113747538,
        "ci95": [
          -4.810961663038237,
          -1.6975749223276186
        ],
        "p_raw": 5.4672911936372046e-05,
        "df": 204,
        "event_days": 205,
        "p_holm2": 0.00010934582387274409
      },
      {
        "horizon": 15,
        "n": 205,
        "status": "FROZEN_HAC5_FRAGMENT_ONLY",
        "delta": -2.756707317073171,
        "se_HAC5": 1.4931373173942442,
        "se_CR1": 1.5136754567572483,
        "ci95": [
          -5.700667768423035,
          0.187253134276693
        ],
        "p_raw": 0.06630446646177826,
        "df": 204,
        "event_days": 205,
        "p_holm2": 0.06630446646177826
      }
    ],
    "VENDOR_SAMPLE_OCT2026": [
      {
        "horizon": 2,
        "n": 0,
        "p_raw": 1.0,
        "status": "DATA_INSUFFICIENT",
        "p_holm2": 1.0
      },
      {
        "horizon": 15,
        "n": 0,
        "p_raw": 1.0,
        "status": "DATA_INSUFFICIENT",
        "p_holm2": 1.0
      }
    ]
  }
}
```

Een klein fragment met vier winstgevende events kan een smal naïef interval geven. Dat vult geen vaste driejaarsproef en de Holmcorrectie/informatiepoort/kwartaalvereiste blijven gelden. Geen HOLDOUT_PASSED op basis van deze fragmenten.

## Fase4 — Falsificatie en uitvoeringsrisico

Alle netto positieve rijen krijgen onderstaande controles; ook negatieve rijen blijven in de JSON. Sharpe/Sortino zijn geannualiseerde ratio’s van één-contract dagpunt-P&L inclusief nul op niet-handelsweekdagen, geen rendement op geïnvesteerd kapitaal. Gesloten-equityDD dekt intraday margin calls niet af.

| Model | DD pt | Slechtste dag pt | Max verliesreeks | Dag Sharpe | Dag Sortino | Top3/net% | Netto zonder top3 | LODO gem. min/max | LOQO gem. min/max | Netto +2ticks/kant |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| AFTERNOON_V2_2 | 56.72 | -31.73 | 4 | 2.98 | 6.41 | 21.49 | 568.47 | [4.09; 4.69] | [3.46; 5.39] | 562.05 |
| AFTERNOON_TOM_YES_MID_2 | 16.70 | -14.97 | 2 | 1.73 | 6.89 | 62.52 | 52.50 | [8.98; 12.92] | [6.58; 13.81] | 127.08 |
| AFTERNOON_TOM_NO_HIGH_2 | 41.92 | -23.73 | 3 | 1.71 | 3.97 | 49.00 | 112.47 | [5.45; 7.88] | [4.98; 8.20] | 188.55 |
| AFTERNOON_V2_15 | 214.43 | -115.97 | 5 | 1.73 | 2.78 | 31.63 | 741.73 | [5.82; 7.46] | [3.78; 8.81] | 922.80 |
| AFTERNOON_TOM_YES_HIGH_2 | 0.00 | 0.00 | 0 | 1.58 | n.v.t. | 73.33 | 15.57 | [8.22; 11.67] | [8.22; 11.61] | 52.40 |
| AFTERNOON_TOM_YES_HIGH_15 | 7.97 | -7.97 | 1 | 1.36 | 11.76 | 84.18 | 21.58 | [18.62; 28.88] | [18.62; 26.09] | 130.40 |
| AFTERNOON_TOM_YES_LOW_15 | 31.22 | -31.23 | 2 | 0.83 | 1.85 | 128.92 | -24.30 | [3.90; 11.53] | [-1.07; 11.34] | 73.03 |
| AFTERNOON_TOM_YES_LOW_2 | 15.20 | -11.47 | 2 | 0.93 | 1.76 | 104.40 | -1.30 | [1.70; 4.10] | [1.49; 4.97] | 18.52 |
| AFTERNOON_TOM_NO_MID_2 | 37.80 | -22.98 | 4 | 1.12 | 2.72 | 83.64 | 23.88 | [2.19; 4.57] | [1.18; 5.67] | 107.95 |
| AFTERNOON_TOM_NO_HIGH_15 | 130.68 | -115.22 | 3 | 0.92 | 1.44 | 75.90 | 64.72 | [5.96; 12.38] | [6.32; 10.16] | 236.55 |
| TOM_RTH | 1307.07 | -583.98 | 5 | 1.44 | 2.32 | 37.81 | 2714.20 | [46.52; 61.85] | [37.75; 65.99] | 4283.02 |
| AFTERNOON_TOM_NO_MID_15 | 108.65 | -102.22 | 6 | 0.70 | 1.24 | 136.37 | -88.62 | [2.59; 9.35] | [2.84; 12.37] | 205.70 |
| AFTERNOON_TOM_YES_MID_15 | 155.95 | -115.97 | 2 | 0.48 | 0.64 | 141.56 | -44.50 | [2.82; 18.59] | [3.75; 18.24] | 94.07 |
| TOM_ATR_CAP | 1559.63 | -539.48 | 5 | 0.96 | 1.53 | 66.22 | 841.45 | [30.82; 50.51] | [25.37; 54.92] | 2430.28 |
| FRIDAY_CONT | 985.23 | -328.23 | 5 | 0.89 | 1.46 | 78.17 | 293.80 | [10.99; 19.93] | [4.47; 31.04] | 1260.88 |
| SWEEP_REV_1200 | 582.40 | -310.48 | 4 | 0.72 | 1.44 | 110.77 | -150.50 | [6.78; 27.54] | [13.82; 32.85] | 1333.83 |
| TOM_OVERNIGHT_1030 | 1433.40 | -368.98 | 7 | 0.91 | 1.55 | 66.00 | 773.38 | [21.39; 34.34] | [13.84; 41.91] | 2196.95 |
| COMPRESSED_BREAK5 | 1445.15 | -366.23 | 5 | 0.92 | 1.42 | 53.50 | 985.65 | [15.89; 23.02] | [11.74; 29.55] | 2010.48 |
| TOM_TREND_1000 | 947.77 | -721.23 | 3 | 0.56 | 0.75 | 92.06 | 92.92 | [15.48; 38.61] | [12.55; 41.88] | 1120.50 |
| AFTERNOON_TOM_NO_LOW_2 | 58.43 | -20.98 | 3 | 0.21 | 0.30 | 355.57 | -43.00 | [-0.23; 0.90] | [-0.55; 1.45] | -26.18 |

Operationele risicopoort vóór de run: DD<=50%netgain, top3<=50%net, netto zondertop3>0, minimaleLOQOmean>0, netto positief bij2 extraticks/kant. Dit is een onderzoeksvergelijking en geen veilige positiegrootte voor een onbekende rekening. AlleMAE/MFE-percentielen hieronder blijven daarom zichtbaar.

| Model | MFE P25 | MFE mediaan | MFE P75 | MAE P25 | MAE mediaan | MAE P75 | MAE P90 | MAE/ATR P95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AFTERNOON_V2_2 | 5.00 | 8.75 | 16.25 | 2.25 | 4.50 | 10.44 | 17.18 | 0.06 |
| AFTERNOON_TOM_YES_MID_2 | 8.00 | 15.25 | 24.50 | 1.50 | 2.50 | 8.75 | 14.40 | 0.05 |
| AFTERNOON_TOM_NO_HIGH_2 | 7.19 | 13.62 | 24.50 | 2.25 | 3.75 | 9.12 | 16.25 | 0.05 |
| AFTERNOON_V2_15 | 8.75 | 21.62 | 41.38 | 4.31 | 9.88 | 21.25 | 38.63 | 0.17 |
| AFTERNOON_TOM_YES_HIGH_2 | 9.75 | 14.38 | 22.38 | 1.50 | 3.38 | 6.19 | 6.75 | 0.01 |
| AFTERNOON_TOM_YES_HIGH_15 | 20.62 | 39.62 | 42.31 | 2.81 | 6.12 | 12.81 | 17.88 | 0.04 |
| AFTERNOON_TOM_YES_LOW_15 | 10.12 | 15.75 | 25.25 | 6.12 | 6.75 | 8.62 | 20.00 | 0.08 |
| AFTERNOON_TOM_YES_LOW_2 | 6.75 | 7.75 | 11.12 | 2.75 | 3.75 | 5.50 | 9.25 | 0.04 |
| AFTERNOON_TOM_NO_MID_2 | 3.56 | 6.12 | 15.94 | 1.56 | 3.62 | 12.50 | 18.25 | 0.05 |
| AFTERNOON_TOM_NO_HIGH_15 | 12.12 | 28.88 | 45.31 | 3.19 | 11.25 | 21.38 | 34.05 | 0.09 |
| TOM_RTH | 96.25 | 190.00 | 272.75 | 45.75 | 102.25 | 234.75 | 364.00 | 1.50 |
| AFTERNOON_TOM_NO_MID_15 | 8.62 | 19.00 | 31.12 | 3.94 | 9.75 | 16.50 | 44.65 | 0.17 |
| AFTERNOON_TOM_YES_MID_15 | 17.50 | 35.25 | 43.25 | 1.50 | 9.25 | 22.75 | 38.30 | 0.18 |
| TOM_ATR_CAP | 65.50 | 164.25 | 256.00 | 44.50 | 98.25 | 234.75 | 382.25 | 1.49 |
| FRIDAY_CONT | 24.75 | 59.25 | 93.75 | 22.75 | 48.75 | 98.25 | 201.80 | 0.63 |
| SWEEP_REV_1200 | 54.12 | 107.50 | 185.12 | 30.12 | 66.25 | 131.00 | 207.80 | 0.68 |
| TOM_OVERNIGHT_1030 | 63.88 | 114.00 | 241.88 | 87.69 | 152.88 | 263.38 | 409.77 | 1.30 |
| COMPRESSED_BREAK5 | 44.50 | 127.50 | 221.50 | 60.00 | 106.25 | 180.00 | 301.25 | 0.83 |
| TOM_TREND_1000 | 57.62 | 131.12 | 232.94 | 53.25 | 100.12 | 206.94 | 330.82 | 1.00 |
| AFTERNOON_TOM_NO_LOW_2 | 3.62 | 6.75 | 10.75 | 2.38 | 4.75 | 10.25 | 15.10 | 0.06 |
| SWEEP_REV_1600 | 78.00 | 123.00 | 221.12 | 37.62 | 94.25 | 195.25 | 331.60 | 1.02 |
| AFTERNOON_TOM_NO_LOW_15 | 6.38 | 13.75 | 31.62 | 4.62 | 12.75 | 29.75 | 49.95 | 0.22 |
| FRIDAY_REVERT | 22.75 | 48.75 | 98.25 | 24.75 | 59.25 | 93.75 | 203.30 | 0.54 |

### Alle ontdekkingskwartalen per model

| Model | Kwartaal | N | Netto pt | Gemiddeld netto pt |
|---|---|---:|---:|---:|
| AFTERNOON_V2_2 | 2025Q1 | 17 | 76.67 | 4.51 |
| AFTERNOON_V2_2 | 2025Q2 | 21 | 12.52 | 0.60 |
| AFTERNOON_V2_2 | 2025Q3 | 29 | 7.48 | 0.26 |
| AFTERNOON_V2_2 | 2025Q4 | 16 | 67.90 | 4.24 |
| AFTERNOON_V2_2 | 2026Q1 | 24 | 246.35 | 10.26 |
| AFTERNOON_V2_2 | 2026Q2 | 35 | 235.12 | 6.72 |
| AFTERNOON_V2_2 | 2026Q3 | 20 | 78.00 | 3.90 |
| AFTERNOON_TOM_YES_MID_2 | 2025Q3 | 3 | 23.32 | 7.77 |
| AFTERNOON_TOM_YES_MID_2 | 2026Q1 | 5 | 29.62 | 5.92 |
| AFTERNOON_TOM_YES_MID_2 | 2026Q2 | 2 | 12.80 | 6.40 |
| AFTERNOON_TOM_YES_MID_2 | 2026Q3 | 3 | 74.33 | 24.78 |
| AFTERNOON_TOM_NO_HIGH_2 | 2025Q3 | 1 | 2.52 | 2.52 |
| AFTERNOON_TOM_NO_HIGH_2 | 2025Q4 | 8 | 35.20 | 4.40 |
| AFTERNOON_TOM_NO_HIGH_2 | 2026Q1 | 7 | 95.92 | 13.70 |
| AFTERNOON_TOM_NO_HIGH_2 | 2026Q2 | 14 | 112.35 | 8.03 |
| AFTERNOON_TOM_NO_HIGH_2 | 2026Q3 | 2 | -25.45 | -12.73 |
| AFTERNOON_V2_15 | 2025Q1 | 17 | 146.92 | 8.64 |
| AFTERNOON_V2_15 | 2025Q2 | 21 | 219.28 | 10.44 |
| AFTERNOON_V2_15 | 2025Q3 | 29 | -86.28 | -2.98 |
| AFTERNOON_V2_15 | 2025Q4 | 16 | 170.90 | 10.68 |
| AFTERNOON_V2_15 | 2026Q1 | 24 | 84.35 | 3.51 |
| AFTERNOON_V2_15 | 2026Q2 | 35 | 604.38 | 17.27 |
| AFTERNOON_V2_15 | 2026Q3 | 20 | -54.75 | -2.74 |
| AFTERNOON_TOM_YES_HIGH_2 | 2025Q2 | 1 | 17.27 | 17.27 |
| AFTERNOON_TOM_YES_HIGH_2 | 2025Q4 | 2 | 17.55 | 8.78 |
| AFTERNOON_TOM_YES_HIGH_2 | 2026Q2 | 3 | 23.57 | 7.86 |
| AFTERNOON_TOM_YES_HIGH_15 | 2025Q2 | 1 | 43.27 | 43.27 |
| AFTERNOON_TOM_YES_HIGH_15 | 2025Q4 | 2 | 32.05 | 16.02 |
| AFTERNOON_TOM_YES_HIGH_15 | 2026Q2 | 3 | 61.07 | 20.36 |
| AFTERNOON_TOM_YES_LOW_15 | 2025Q2 | 3 | -6.67 | -2.22 |
| AFTERNOON_TOM_YES_LOW_15 | 2025Q3 | 2 | 8.55 | 4.28 |
| AFTERNOON_TOM_YES_LOW_15 | 2026Q1 | 1 | 2.27 | 2.27 |
| AFTERNOON_TOM_YES_LOW_15 | 2026Q2 | 3 | 92.58 | 30.86 |
| AFTERNOON_TOM_YES_LOW_15 | 2026Q3 | 2 | -12.70 | -6.35 |
| AFTERNOON_TOM_YES_LOW_2 | 2025Q2 | 3 | 10.57 | 3.52 |
| AFTERNOON_TOM_YES_LOW_2 | 2025Q3 | 2 | 12.80 | 6.40 |
| AFTERNOON_TOM_YES_LOW_2 | 2026Q1 | 1 | 3.77 | 3.77 |
| AFTERNOON_TOM_YES_LOW_2 | 2026Q2 | 3 | 17.57 | 5.86 |
| AFTERNOON_TOM_YES_LOW_2 | 2026Q3 | 2 | -15.20 | -7.60 |
| AFTERNOON_TOM_NO_MID_2 | 2025Q2 | 4 | -31.90 | -7.97 |
| AFTERNOON_TOM_NO_MID_2 | 2025Q3 | 12 | -1.45 | -0.12 |
| AFTERNOON_TOM_NO_MID_2 | 2025Q4 | 4 | 17.35 | 4.34 |
| AFTERNOON_TOM_NO_MID_2 | 2026Q1 | 5 | 107.12 | 21.43 |
| AFTERNOON_TOM_NO_MID_2 | 2026Q2 | 5 | 32.88 | 6.57 |
| AFTERNOON_TOM_NO_MID_2 | 2026Q3 | 8 | 21.95 | 2.74 |
| AFTERNOON_TOM_NO_HIGH_15 | 2025Q3 | 1 | 2.02 | 2.02 |
| AFTERNOON_TOM_NO_HIGH_15 | 2025Q4 | 8 | 110.95 | 13.87 |
| AFTERNOON_TOM_NO_HIGH_15 | 2026Q1 | 7 | 36.92 | 5.27 |
| AFTERNOON_TOM_NO_HIGH_15 | 2026Q2 | 14 | 154.85 | 11.06 |
| AFTERNOON_TOM_NO_HIGH_15 | 2026Q3 | 2 | -36.20 | -18.10 |
| TOM_RTH | 2025Q1 | 12 | 814.55 | 67.88 |
| TOM_RTH | 2025Q2 | 12 | 1225.80 | 102.15 |
| TOM_RTH | 2025Q3 | 11 | -254.97 | -23.18 |
| TOM_RTH | 2025Q4 | 11 | -59.72 | -5.43 |
| TOM_RTH | 2026Q1 | 11 | 437.02 | 39.73 |
| TOM_RTH | 2026Q2 | 12 | 1759.55 | 146.63 |
| TOM_RTH | 2026Q3 | 12 | 441.80 | 36.82 |
| AFTERNOON_TOM_NO_MID_15 | 2025Q2 | 4 | -11.90 | -2.97 |
| AFTERNOON_TOM_NO_MID_15 | 2025Q3 | 12 | -77.95 | -6.50 |
| AFTERNOON_TOM_NO_MID_15 | 2025Q4 | 4 | 33.85 | 8.46 |
| AFTERNOON_TOM_NO_MID_15 | 2026Q1 | 5 | 127.12 | 25.43 |
| AFTERNOON_TOM_NO_MID_15 | 2026Q2 | 5 | 149.88 | 29.98 |
| AFTERNOON_TOM_NO_MID_15 | 2026Q3 | 8 | 22.70 | 2.84 |
| AFTERNOON_TOM_YES_MID_15 | 2025Q3 | 3 | 37.33 | 12.44 |
| AFTERNOON_TOM_YES_MID_15 | 2026Q1 | 5 | -38.87 | -7.77 |
| AFTERNOON_TOM_YES_MID_15 | 2026Q2 | 2 | 39.05 | 19.52 |
| AFTERNOON_TOM_YES_MID_15 | 2026Q3 | 3 | 69.58 | 23.19 |
| TOM_ATR_CAP | 2025Q2 | 9 | 826.23 | 91.80 |
| TOM_ATR_CAP | 2025Q3 | 11 | -254.97 | -23.18 |
| TOM_ATR_CAP | 2025Q4 | 9 | -312.27 | -34.70 |
| TOM_ATR_CAP | 2026Q1 | 11 | 437.02 | 39.73 |
| TOM_ATR_CAP | 2026Q2 | 10 | 1197.25 | 119.72 |
| TOM_ATR_CAP | 2026Q3 | 11 | 598.02 | 54.37 |
| FRIDAY_CONT | 2025Q1 | 13 | -888.92 | -68.38 |
| FRIDAY_CONT | 2025Q2 | 12 | 316.05 | 26.34 |
| FRIDAY_CONT | 2025Q3 | 12 | 59.30 | 4.94 |
| FRIDAY_CONT | 2025Q4 | 12 | 310.05 | 25.84 |
| FRIDAY_CONT | 2026Q1 | 13 | 66.83 | 5.14 |
| FRIDAY_CONT | 2026Q2 | 11 | 463.27 | 42.12 |
| FRIDAY_CONT | 2026Q3 | 12 | 1019.30 | 84.94 |
| SWEEP_REV_1200 | 2025Q1 | 5 | 84.37 | 16.87 |
| SWEEP_REV_1200 | 2025Q2 | 4 | 450.60 | 112.65 |
| SWEEP_REV_1200 | 2025Q3 | 14 | -212.90 | -15.21 |
| SWEEP_REV_1200 | 2025Q4 | 11 | -30.97 | -2.82 |
| SWEEP_REV_1200 | 2026Q1 | 13 | 227.57 | 17.51 |
| SWEEP_REV_1200 | 2026Q2 | 6 | 609.15 | 101.52 |
| SWEEP_REV_1200 | 2026Q3 | 10 | 269.00 | 26.90 |
| TOM_OVERNIGHT_1030 | 2025Q1 | 11 | -5.48 | -0.50 |
| TOM_OVERNIGHT_1030 | 2025Q2 | 11 | 355.77 | 32.34 |
| TOM_OVERNIGHT_1030 | 2025Q3 | 11 | -532.73 | -48.43 |
| TOM_OVERNIGHT_1030 | 2025Q4 | 11 | -203.72 | -18.52 |
| TOM_OVERNIGHT_1030 | 2026Q1 | 10 | 924.50 | 92.45 |
| TOM_OVERNIGHT_1030 | 2026Q2 | 12 | 1361.55 | 113.46 |
| TOM_OVERNIGHT_1030 | 2026Q3 | 12 | 375.05 | 31.25 |
| COMPRESSED_BREAK5 | 2025Q1 | 12 | 150.80 | 12.57 |
| COMPRESSED_BREAK5 | 2025Q2 | 23 | -421.43 | -18.32 |
| COMPRESSED_BREAK5 | 2025Q3 | 11 | -122.72 | -11.16 |
| COMPRESSED_BREAK5 | 2025Q4 | 14 | 498.35 | 35.60 |
| COMPRESSED_BREAK5 | 2026Q1 | 11 | 500.02 | 45.46 |
| COMPRESSED_BREAK5 | 2026Q2 | 17 | 427.92 | 25.17 |
| COMPRESSED_BREAK5 | 2026Q3 | 21 | 1086.53 | 51.74 |
| TOM_TREND_1000 | 2025Q1 | 8 | 360.45 | 45.06 |
| TOM_TREND_1000 | 2025Q2 | 7 | 454.18 | 64.88 |
| TOM_TREND_1000 | 2025Q3 | 5 | -129.38 | -25.87 |
| TOM_TREND_1000 | 2025Q4 | 5 | 27.62 | 5.52 |
| TOM_TREND_1000 | 2026Q1 | 7 | 630.92 | 90.13 |
| TOM_TREND_1000 | 2026Q2 | 9 | 373.48 | 41.50 |
| TOM_TREND_1000 | 2026Q3 | 9 | -546.78 | -60.75 |
| AFTERNOON_TOM_NO_LOW_2 | 2025Q2 | 11 | -19.48 | -1.77 |
| AFTERNOON_TOM_NO_LOW_2 | 2025Q3 | 11 | -29.72 | -2.70 |
| AFTERNOON_TOM_NO_LOW_2 | 2025Q4 | 2 | -2.20 | -1.10 |
| AFTERNOON_TOM_NO_LOW_2 | 2026Q1 | 6 | 9.90 | 1.65 |
| AFTERNOON_TOM_NO_LOW_2 | 2026Q2 | 8 | 35.95 | 4.49 |
| AFTERNOON_TOM_NO_LOW_2 | 2026Q3 | 5 | 22.37 | 4.47 |
| SWEEP_REV_1600 | 2025Q1 | 5 | 565.38 | 113.07 |
| SWEEP_REV_1600 | 2025Q2 | 4 | 421.60 | 105.40 |
| SWEEP_REV_1600 | 2025Q3 | 14 | -413.15 | -29.51 |
| SWEEP_REV_1600 | 2025Q4 | 11 | -13.72 | -1.25 |
| SWEEP_REV_1600 | 2026Q1 | 13 | -463.68 | -35.67 |
| SWEEP_REV_1600 | 2026Q2 | 6 | -217.35 | -36.23 |
| SWEEP_REV_1600 | 2026Q3 | 10 | 22.00 | 2.20 |
| AFTERNOON_TOM_NO_LOW_15 | 2025Q2 | 11 | 76.03 | 6.91 |
| AFTERNOON_TOM_NO_LOW_15 | 2025Q3 | 11 | -56.23 | -5.11 |
| AFTERNOON_TOM_NO_LOW_15 | 2025Q4 | 2 | -5.95 | -2.97 |
| AFTERNOON_TOM_NO_LOW_15 | 2026Q1 | 6 | -43.10 | -7.18 |
| AFTERNOON_TOM_NO_LOW_15 | 2026Q2 | 8 | 106.95 | 13.37 |
| AFTERNOON_TOM_NO_LOW_15 | 2026Q3 | 5 | -98.12 | -19.62 |
| FRIDAY_REVERT | 2025Q1 | 13 | 857.08 | 65.93 |
| FRIDAY_REVERT | 2025Q2 | 12 | -345.45 | -28.79 |
| FRIDAY_REVERT | 2025Q3 | 12 | -88.70 | -7.39 |
| FRIDAY_REVERT | 2025Q4 | 12 | -339.45 | -28.29 |
| FRIDAY_REVERT | 2026Q1 | 13 | -98.67 | -7.59 |
| FRIDAY_REVERT | 2026Q2 | 11 | -490.23 | -44.57 |
| FRIDAY_REVERT | 2026Q3 | 12 | -1048.70 | -87.39 |

### Historische positieve rijen: dezelfde risico- en kwartaalcijfers

Dezelfde metrics,LODO/LOQO,Sharpe/Sortino,MFE/MAE en kostenscenario’s zijn ook voor ieder historisch model berekend in de lokale historischeJSON. Hieronder staan alle historische rijen met positieve nettoP&L, inclusief kleine fragmenten; nergens wordt een te kleine steekproef gepromoveerd.

| Bron | Model | N | DD pt | Grootste verliesdag | Top3/net% | LODO | LOQO | MFE mediaan | MAE mediaan | +2ticks net pt |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|
| CONTRACT_2018_WARMUP | FRIDAY_CONT | 5 | 54.47 | -54.48 | 139.51 | [17.40; 51.71] | n.v.t. | 99.00 | 28.50 | 147.38 |
| CONTRACT_2018_WARMUP | SWEEP_REV_1200 | 6 | 8.72 | -8.72 | 95.89 | [12.93; 33.78] | n.v.t. | 59.62 | 24.38 | 154.15 |
| CONTRACT_2019_FRAGMENT | TOM_RTH | 3 | 119.97 | -119.97 | 155.46 | [20.53; 168.15] | n.v.t. | 199.00 | 18.50 | 213.33 |
| CONTRACT_2019_FRAGMENT | FRIDAY_CONT | 2 | 14.97 | -14.97 | 298.34 | [-14.97; 22.52] | n.v.t. | 19.38 | 24.12 | 5.55 |
| CONTRACT_2019_FRAGMENT | SWEEP_REV_1200 | 2 | 3.98 | -3.98 | 123.66 | [-3.98; 20.77] | n.v.t. | 78.12 | 24.00 | 14.80 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_2 | 4 | 0.00 | 0.00 | 98.32 | [3.03; 5.36] | n.v.t. | 7.12 | 2.25 | 12.35 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_15 | 4 | 11.72 | -11.72 | 138.01 | [2.86; 14.19] | n.v.t. | 14.50 | 3.12 | 26.85 |
| CONTRACT_PILOT_2024 | TOM_RTH | 4 | 162.47 | -162.47 | 215.30 | [-18.89; 108.86] | n.v.t. | 115.38 | 105.50 | 160.10 |
| CONTRACT_PILOT_2024 | FRIDAY_CONT | 4 | 14.97 | -14.97 | 116.48 | [2.19; 35.27] | n.v.t. | 50.88 | 33.38 | 86.85 |
| CONTRACT_PILOT_2024 | SWEEP_REV_1200 | 3 | 81.22 | -81.22 | 208.55 | [-17.72; 78.03] | n.v.t. | 117.25 | 43.50 | 71.83 |
| CONTRACT_PILOT_2024 | AFTERNOON_V2_15 | 1 | 0.00 | 0.00 | 100.00 | n.v.t. | n.v.t. | 7.25 | 15.25 | -0.97 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 90 | 1149.75 | -499.23 | 54.53 | [13.09; 21.79] | [7.32; 21.60] | 106.50 | 69.62 | 1350.25 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 61 | 700.55 | -466.73 | 125.43 | [5.25; 17.58] | [6.01; 18.48] | 105.00 | 78.75 | 527.02 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 106 | 1236.70 | -416.23 | 106.73 | [5.46; 16.41] | [6.36; 19.79] | 75.75 | 76.12 | 1200.40 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 70 | 632.40 | -168.97 | 130.64 | [4.51; 10.98] | [2.97; 14.86] | 72.88 | 47.50 | 518.50 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 13 | 22.43 | -10.47 | 311.15 | [-0.77; 2.82] | [-2.13; 3.52] | 3.50 | 6.25 | 10.32 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 44 | 90.38 | -43.98 | 144.52 | [0.91; 3.12] | [0.42; 2.88] | 12.50 | 10.75 | 46.35 |
| VENDOR_SAMPLE_OCT2026 | TOM_RTH | 3 | 103.95 | -78.97 | 158.62 | [-51.97; 128.15] | n.v.t. | 134.75 | 159.75 | 174.32 |
| VENDOR_SAMPLE_OCT2026 | FRIDAY_CONT | 2 | 0.00 | 0.00 | 100.00 | [22.53; 111.28] | n.v.t. | 139.88 | 49.50 | 131.80 |
| VENDOR_SAMPLE_OCT2026 | SWEEP_REV_1200 | 2 | 89.47 | -89.47 | 1088.67 | [-89.47; 98.53] | n.v.t. | 78.12 | 102.38 | 7.05 |

### Volledige kostengevoeligheid op ontdekkingsdata

| Model | N | $24,50 netto pt | $34,50 netto pt | $44,50 netto pt | Gem. bij $44,50 |
|---|---:|---:|---:|---:|---:|
| AFTERNOON_V2_2 | 162 | 724.05 | 643.05 | 562.05 | 3.47 |
| AFTERNOON_TOM_YES_MID_2 | 13 | 140.08 | 133.58 | 127.08 | 9.78 |
| AFTERNOON_TOM_NO_HIGH_2 | 32 | 220.55 | 204.55 | 188.55 | 5.89 |
| AFTERNOON_V2_15 | 162 | 1084.80 | 1003.80 | 922.80 | 5.70 |
| AFTERNOON_TOM_YES_HIGH_2 | 6 | 58.40 | 55.40 | 52.40 | 8.73 |
| AFTERNOON_TOM_YES_HIGH_15 | 6 | 136.40 | 133.40 | 130.40 | 21.73 |
| AFTERNOON_TOM_YES_LOW_15 | 11 | 84.03 | 78.53 | 73.03 | 6.64 |
| AFTERNOON_TOM_YES_LOW_2 | 11 | 29.52 | 24.02 | 18.52 | 1.68 |
| AFTERNOON_TOM_NO_MID_2 | 38 | 145.95 | 126.95 | 107.95 | 2.84 |
| AFTERNOON_TOM_NO_HIGH_15 | 32 | 268.55 | 252.55 | 236.55 | 7.39 |
| TOM_RTH | 81 | 4364.02 | 4323.52 | 4283.02 | 52.88 |
| AFTERNOON_TOM_NO_MID_15 | 38 | 243.70 | 224.70 | 205.70 | 5.41 |
| AFTERNOON_TOM_YES_MID_15 | 13 | 107.07 | 100.57 | 94.07 | 7.24 |
| TOM_ATR_CAP | 61 | 2491.28 | 2460.78 | 2430.28 | 39.84 |
| FRIDAY_CONT | 85 | 1345.88 | 1303.38 | 1260.88 | 14.83 |
| SWEEP_REV_1200 | 63 | 1396.83 | 1365.33 | 1333.83 | 21.17 |
| TOM_OVERNIGHT_1030 | 78 | 2274.95 | 2235.95 | 2196.95 | 28.17 |
| COMPRESSED_BREAK5 | 109 | 2119.48 | 2064.98 | 2010.48 | 18.44 |
| TOM_TREND_1000 | 50 | 1170.50 | 1145.50 | 1120.50 | 22.41 |
| AFTERNOON_TOM_NO_LOW_2 | 43 | 16.82 | -4.68 | -26.18 | -0.61 |
| SWEEP_REV_1600 | 63 | -98.93 | -130.43 | -161.93 | -2.57 |
| AFTERNOON_TOM_NO_LOW_15 | 43 | -20.42 | -41.92 | -63.42 | -1.47 |
| FRIDAY_REVERT | 85 | -1554.12 | -1596.62 | -1639.12 | -19.28 |

### Historische kalenderkwartalen per geselecteerde rij

| Bron | Model | Kwartaal | N | Netto pt |
|---|---|---|---:|---:|
| CONTRACT_2018_WARMUP | AFTERNOON_V2_15 | 2018Q4 | 3 | -26.68 |
| CONTRACT_2018_WARMUP | AFTERNOON_V2_2 | 2018Q4 | 3 | -25.18 |
| CONTRACT_2018_WARMUP | FRIDAY_CONT | 2018Q4 | 5 | 152.38 |
| CONTRACT_2018_WARMUP | SWEEP_REV_1200 | 2018Q4 | 6 | 160.15 |
| CONTRACT_2018_WARMUP | TOM_RTH | 2018Q4 | 5 | -52.62 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_15 | 2019Q1 | 4 | 30.85 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_2 | 2019Q1 | 4 | 16.35 |
| CONTRACT_2019_FRAGMENT | COMPRESSED_BREAK5 | 2019Q1 | 4 | -211.65 |
| CONTRACT_2019_FRAGMENT | FRIDAY_CONT | 2019Q1 | 2 | 7.55 |
| CONTRACT_2019_FRAGMENT | SWEEP_REV_1200 | 2019Q1 | 2 | 16.80 |
| CONTRACT_2019_FRAGMENT | TOM_RTH | 2019Q1 | 3 | 216.33 |
| CONTRACT_PILOT_2024 | AFTERNOON_V2_15 | 2024Q1 | 1 | 0.03 |
| CONTRACT_PILOT_2024 | AFTERNOON_V2_2 | 2024Q1 | 1 | -1.73 |
| CONTRACT_PILOT_2024 | FRIDAY_CONT | 2024Q1 | 4 | 90.85 |
| CONTRACT_PILOT_2024 | SWEEP_REV_1200 | 2024Q1 | 3 | 74.83 |
| CONTRACT_PILOT_2024 | TOM_RTH | 2024Q1 | 4 | 164.10 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 2023Q2 | 6 | 4.90 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 2023Q3 | 6 | -27.85 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 2023Q4 | 6 | 19.65 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 2024Q1 | 10 | -68.75 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 2024Q2 | 5 | 19.88 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 2024Q3 | 9 | -142.28 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_15 | 2024Q4 | 2 | -15.95 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 2023Q2 | 6 | -55.10 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 2023Q3 | 6 | -27.35 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 2023Q4 | 6 | 3.15 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 2024Q1 | 10 | -75.75 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 2024Q2 | 5 | -36.62 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 2024Q3 | 9 | -89.77 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_HIGH_2 | 2024Q4 | 2 | -15.45 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 2023Q2 | 4 | 19.60 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 2023Q3 | 12 | -1.95 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 2023Q4 | 5 | 7.12 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 2024Q1 | 2 | -8.45 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 2024Q2 | 8 | 75.20 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 2024Q3 | 6 | -3.35 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 2024Q4 | 7 | 2.17 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 2023Q2 | 4 | -13.40 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 2023Q3 | 12 | -14.70 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 2023Q4 | 5 | -9.38 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 2024Q1 | 2 | -21.20 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 2024Q2 | 8 | 12.70 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 2024Q3 | 6 | -90.35 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_2 | 2024Q4 | 7 | -43.07 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_15 | 2023Q2 | 1 | 7.28 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_15 | 2023Q3 | 4 | -60.40 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_15 | 2023Q4 | 3 | 39.82 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_15 | 2024Q1 | 1 | 0.03 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_15 | 2024Q2 | 3 | 7.58 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_15 | 2024Q3 | 1 | -21.73 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 2023Q2 | 1 | -10.22 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 2023Q3 | 4 | -8.40 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 2023Q4 | 3 | 44.57 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 2024Q1 | 1 | -7.22 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 2024Q2 | 3 | 9.07 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 2024Q3 | 1 | -4.47 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_15 | 2023Q2 | 3 | -88.42 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_15 | 2023Q4 | 2 | -13.20 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_15 | 2024Q1 | 2 | -22.95 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_15 | 2024Q2 | 2 | -113.20 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_15 | 2024Q3 | 1 | 24.02 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_15 | 2024Q4 | 3 | 24.82 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_2 | 2023Q2 | 3 | 0.08 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_2 | 2023Q4 | 2 | -12.45 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_2 | 2024Q1 | 2 | -12.95 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_2 | 2024Q2 | 2 | -34.95 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_2 | 2024Q3 | 1 | -6.72 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_LOW_2 | 2024Q4 | 3 | -2.17 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_15 | 2023Q2 | 3 | -58.18 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_15 | 2023Q3 | 1 | -39.48 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_15 | 2023Q4 | 2 | 29.80 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_15 | 2024Q2 | 1 | 8.03 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_15 | 2024Q3 | 3 | -42.68 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_15 | 2024Q4 | 3 | 13.82 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_2 | 2023Q2 | 3 | -26.68 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_2 | 2023Q3 | 1 | -13.97 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_2 | 2023Q4 | 2 | 0.30 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_2 | 2024Q2 | 1 | -0.23 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_2 | 2024Q3 | 3 | 0.08 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_MID_2 | 2024Q4 | 3 | -10.18 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2023Q1 | 23 | -42.18 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2023Q2 | 33 | -193.93 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2023Q3 | 27 | -126.33 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2023Q4 | 30 | 44.50 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2024Q1 | 18 | -124.55 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2024Q2 | 25 | 16.12 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2024Q3 | 21 | -201.22 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_15 | 2024Q4 | 28 | 62.45 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2023Q1 | 23 | 53.82 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2023Q2 | 33 | -127.42 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2023Q3 | 27 | -92.07 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2023Q4 | 30 | -9.50 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2024Q1 | 18 | -127.05 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2024Q2 | 25 | -64.38 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2024Q3 | 21 | -202.22 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_V2_2 | 2024Q4 | 28 | -98.30 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2023Q1 | 12 | 435.30 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2023Q2 | 8 | -157.55 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2023Q3 | 14 | 274.35 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2023Q4 | 16 | -474.35 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2024Q1 | 14 | -86.40 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2024Q2 | 15 | 727.88 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2024Q3 | 14 | -41.65 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 2024Q4 | 13 | 628.83 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2022Q4 | 1 | -122.47 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2023Q1 | 13 | -187.67 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2023Q2 | 12 | 42.30 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2023Q3 | 13 | 256.83 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2023Q4 | 12 | 184.05 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2024Q1 | 12 | 117.80 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2024Q2 | 13 | -336.67 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2024Q3 | 11 | -164.47 |
| CONTINUOUS_2022_2024_UNVERIFIED | FRIDAY_CONT | 2024Q4 | 12 | -22.45 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2023Q1 | 7 | 282.43 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2023Q2 | 6 | -362.35 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2023Q3 | 9 | -107.27 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2023Q4 | 9 | 79.73 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2024Q1 | 12 | 49.05 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2024Q2 | 10 | 118.25 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2024Q3 | 7 | 401.68 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 2024Q4 | 10 | 127.00 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 2023Q2 | 9 | 159.48 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 2023Q3 | 7 | -409.82 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 2023Q4 | 9 | 275.48 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 2024Q1 | 11 | -25.22 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 2024Q2 | 8 | 249.70 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 2024Q3 | 7 | 187.92 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 2024Q4 | 10 | 150.50 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2022Q4 | 1 | 109.78 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2023Q1 | 12 | 869.05 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2023Q2 | 11 | 153.78 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2023Q3 | 11 | -266.22 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2023Q4 | 12 | 695.55 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2024Q1 | 12 | -97.95 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2024Q2 | 12 | 13.80 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2024Q3 | 9 | -188.03 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 2024Q4 | 10 | 150.50 |
| VENDOR_SAMPLE_OCT2026 | FRIDAY_CONT | 2026Q4 | 2 | 133.80 |
| VENDOR_SAMPLE_OCT2026 | SWEEP_REV_1200 | 2026Q4 | 2 | 9.05 |
| VENDOR_SAMPLE_OCT2026 | TOM_RTH | 2026Q4 | 3 | 177.32 |

### Historische positieve rijen: Sharpe, Sortino, verliesreeks en beide extra fricties

| Bron | Model | Sharpe | Sortino | Verliesreeks | Netto bij $34,50 | Netto bij $44,50 |
|---|---|---:|---:|---:|---:|---:|
| CONTRACT_2018_WARMUP | FRIDAY_CONT | 3.20 | 7.93 | 1 | 149.88 | 147.38 |
| CONTRACT_2018_WARMUP | SWEEP_REV_1200 | 4.40 | 52.33 | 1 | 157.15 | 154.15 |
| CONTRACT_2019_FRAGMENT | TOM_RTH | 4.45 | 10.12 | 1 | 214.83 | 213.33 |
| CONTRACT_2019_FRAGMENT | FRIDAY_CONT | 1.47 | 2.83 | 1 | 6.55 | 5.55 |
| CONTRACT_2019_FRAGMENT | SWEEP_REV_1200 | 4.34 | 23.72 | 1 | 15.80 | 14.80 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_2 | 11.01 | n.v.t. | 0 | 14.35 | 12.35 |
| CONTRACT_2019_FRAGMENT | AFTERNOON_V2_15 | 5.95 | 14.77 | 1 | 28.85 | 26.85 |
| CONTRACT_PILOT_2024 | TOM_RTH | 1.87 | 3.54 | 1 | 162.10 | 160.10 |
| CONTRACT_PILOT_2024 | FRIDAY_CONT | 3.67 | 21.53 | 1 | 88.85 | 86.85 |
| CONTRACT_PILOT_2024 | SWEEP_REV_1200 | 1.80 | 3.27 | 1 | 73.33 | 71.83 |
| CONTRACT_PILOT_2024 | AFTERNOON_V2_15 | 3.55 | n.v.t. | 0 | -0.47 | -0.97 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 0.71 | 0.97 | 5 | 1395.25 | 1350.25 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_ATR_CAP | 0.37 | 0.50 | 5 | 557.52 | 527.02 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 0.61 | 1.03 | 7 | 1253.40 | 1200.40 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 0.53 | 0.90 | 8 | 553.50 | 518.50 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_YES_HIGH_2 | 0.33 | 0.76 | 3 | 16.82 | 10.32 |
| CONTINUOUS_2022_2024_UNVERIFIED | AFTERNOON_TOM_NO_MID_15 | 0.47 | 0.74 | 3 | 68.35 | 46.35 |
| VENDOR_SAMPLE_OCT2026 | TOM_RTH | 2.69 | 9.81 | 2 | 175.82 | 174.32 |
| VENDOR_SAMPLE_OCT2026 | FRIDAY_CONT | 5.50 | n.v.t. | 0 | 132.80 | 131.80 |
| VENDOR_SAMPLE_OCT2026 | SWEEP_REV_1200 | 0.30 | 0.46 | 1 | 8.05 | 7.05 |

## Fase5 — Tests, herberekening en lokale dashboardpagina

Op alle435 ontdekkingsdagen: 4785 toekomst-afknipcontroles en evenveel latere-barmutaties. Kalender,voorgaandeATR/volume, bevestiging/fill,horizons, legefamiliecellen en nulbeginkapitaal worden apart getest. Historische prefixcontroles staan per bron geregistreerd.

Verificatie-evidence (volledige suite, tweede bronherlaad-run, hashes, build/typecheck en browser) wordt afzonderlijk vastgelegd in research/edge-marathon-verification.json. Alleen dat bestand is bewijs van een daadwerkelijk uitgevoerde verificatie; deze rapporttekst claimt geen niet-uitgevoerde test.

Lokale dashboarduitbreiding: /research/marathon. Afgeleide totalen en tabellen staan in public/data/edge-marathon.json; geen privateCSV’s, tradeledgers, ruwe arrays of absolutebronpaden. Het oude dashboard en alle beschermde bestanden blijven intact. Geen externe synchronisatie gevraagd of uitgevoerd.

### Reproduceren

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.edge_marathon.runner verify
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.edge_marathon.runner discovery
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.edge_marathon.runner history
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.complete_marathon_zero_loss
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.audit_marathon_source_overlap
.venv/bin/python -m scripts.report_edge_marathon
.venv/bin/python -m pytest -q
```

Geen wijzigingen na teleurstellende uitkomsten: geen nieuw tijdstip, anderevolumegrens, omkering van de15:00-regel of gunstigsteperiode. Meer modellen op dezelfde verbruikte data krijgen niet vanzelf onafhankelijke bewijskracht.


## Daadwerkelijk uitgevoerde eindverificatie

**530 tests geslaagd**, typecheck en productiebuild geslaagd. Afzonderlijk geschreven signaal-/fill-referentie: **2436 events** met dezelfde beslissingen, ankers, kosten en excursies. Deze deelt de bronparser/context en is dus technische verificatie, geen onafhankelijke onderzoeker of marktvalidatie.

De volledige tweede bronherlaad-run is byte-identiek. Exacte aantallen en hashes van de uiteindelijke uitvoer staan in research/edge-marathon-verification.json. Het metadata-only containeronderzoek verandert geen modeluitkomst. Alle115 beschermde archiefbestanden, de73 bevroren onderzoeksbestanden en de v2-specificatie zijn gecontroleerd en intact.

De oude registratieverifiers bevatten nog de tekst outcomesnotreleased/newruns0. Dat zijn ongewijzigde verklaringen van hun oorspronkelijke registratie, geen uitspraak dat deze nieuwe marathon geen fragmentuitkomsten berekende. Het volledige fixed-end venster2019–2021is niet voltooid of als geslaagde proef geclaimd.

Holm25/125 corrigeert uitsluitend deze begrensde families, niet alle eerdere scans of adaptieve modelvorming op reeds verbruikte data. Nieuwe synthetische kalibratiestudies zijn niet gedraaid.

## Primaire bronnen en volledige protocolhash

- https://docs.lib.purdue.edu/ciberwp/43/
- https://www.newyorkfed.org/research/staff_reports/sr917
- https://repub.eur.nl/pub/131621
- https://www.princeton.edu/~umueller/tstat.pdf
- https://ir.theice.com/press/news-details/2023/NYSE-Group-Announces-2024-2025-and-2026-Holiday-and-Early-Closings-Calendar/default.aspx

Protocol SHA256: 7db6747e5f8adf745a100700b42fafb15476b0b866fad8502cc3f5bbc150d21b
Implementatie/bronslot SHA256: 48bab2e6c1fa8901193cc60271309b1936143a5289285cbc281492db7be546bb
Allebronhashes en privatepaden blijven in het lokale genegeerde bronregister. Publieke resultaatJSON bevat alleen afgeleide statistiek.
