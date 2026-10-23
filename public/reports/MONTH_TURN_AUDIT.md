# Audit oorspronkelijke maandwisselregel

## Oordeel

De oorspronkelijke maandwisselregel blijft netto positief in beide gebruikte bronnen. De vaste audit levert geen consistente, voor alle vier contrasten gecorrigeerde bevestiging van extra kalendermeerwaarde. Niet promoveren tot bewezen winstmodel. Geen filters toevoegen op basis van deze uitslag.

Alle cijfers zijn aanvullend verkennend onderzoek op reeds gebruikte gegevens. Geen nieuwe holdout of gevalideerd winstmodel. De oorspronkelijke regels, v0.9/vNext en de 15:00-v2-specificatie blijven ongewijzigd.

## Regel en benchmark

Long op de laatste cashhandelsdag en eerste drie cashhandelsdagen van de maand, van de09:30-open tot de15:59-closebar. De twee december2024-startdagen blijven volgens de bestaande onvolledige-maandregel buiten ToM, maar tellen wel mee in de long-benchmark. Eén NQ-contract, $20 per punt, $24,50 roundtrip =1,225punt. Geen stops, targets of nieuwe filters.

Alleen de bestaande complete sessies tellen mee. Een volledige sessie is een technische evaluatie-eis, geen op voorhand bekende handelsfilter. Datakwaliteit blijft een beperking van de simulatie.

De dagelijkse long-benchmark bevat ook maandwisseldagen. De complementaire niet-ToM-groep is de zuivere beschrijvende kalendervergelijking. Vergelijk opbrengst per blootgestelde dag: de totale winst van81 tegen435 posities is geen gelijk-exposurevergelijking.

## Hoofdvergelijking

| Bron | Groep | Dagen | Netto totaal pt | Gemiddeld netto pt/dag | Mediaan | Win% | PF | Gesloten-trade DD pt |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Ontdekking | Maandwissel | 81 | 4364.025 | 53.877 | 90.525 | 64.2 | 1.706 | 1307.075 |
| Ontdekking | Andere dagen | 354 | -3491.400 | -9.863 | -1.475 | 49.4 | 0.895 | 4338.525 |
| Ontdekking | Alle dagen long | 435 | 872.625 | 2.006 | 13.525 | 52.2 | 1.022 | 4149.825 |
| Oudere onbevestigde bron | Maandwissel | 90 | 1440.250 | 16.003 | 42.400 | 62.2 | 1.322 | 1149.750 |
| Oudere onbevestigde bron | Andere dagen | 403 | 1171.825 | 2.908 | 15.525 | 54.1 | 1.051 | 2924.500 |
| Oudere onbevestigde bron | Alle dagen long | 493 | 2612.075 | 5.298 | 20.275 | 55.6 | 1.095 | 3047.600 |

## Benchmarkmeerwaarde en onzekerheid

Vooraf vastgelegde2-maands moving-blockbootstrap,10.000 herhalingen, gehele maanden als clusters en gepoolde sommen/aantallen. Geen gelijke weging van daggemiddelden of maanden met verschillende aantallen trades. Exact vier aanvullende verkennende contrasten; Holm4. Intervallen zijn nominaal95%, niet simultaan. De p-waarden zijn benaderende nulgecentreerde bootstrapwaarden, geen exacte randomisatietoets. Zwakke afhankelijkheid/stationariteit en beperkte aantallen maanden begrenzen de geldigheid. Deze correctie wist de eerdere modelselectie en25/125-toetsenfamilies niet uit.

| Bron | Eenheid | ToM N / andere N | Gem. ToM | Gem. andere | Verschil | 95%-interval verschil | Ruwe p | Holm4 p |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Ontdekking | Netto pt | 81 / 354 | 53.87685 | -9.86271 | 63.73956 | [12.05023; 116.35700] | 0.01590 | 0.06359 |
| Ontdekking | Netto pt / voorafATR | 78 / 340 | 0.10913 | -0.02630 | 0.13542 | [-0.02410; 0.28576] | 0.08309 | 0.24928 |
| Oudere bron | Netto pt | 90 / 403 | 16.00278 | 2.90775 | 13.09502 | [-23.10383; 43.06438] | 0.45365 | 0.66813 |
| Oudere bron | Netto pt / voorafATR | 86 / 391 | 0.08633 | 0.01268 | 0.07364 | [-0.08249; 0.21457] | 0.33407 | 0.66813 |

De vaste frictie is voor elke long-dag gelijk en valt daardoor uit het ruwe verschil tussen groepsgemiddelden weg. Zij blijft wel volledig in elk modelresultaat verwerkt. Een positief gemiddeld ToM-resultaat is niet automatisch een significante kalenderpremie.

## Volatiliteitsvergelijking zonder toekomstige informatie

### DISCOVERY

Gemeenschappelijke steekproef met vooraf bekendeATR14: 418 dagen; 78 ToM en 340 andere dagen. OntbrekendeATR: 3 ToM en 14 andere dagen. Deze dagen blijven gewoon in het oorspronkelijke modelresultaat staan.

Gemiddelde voorafATR: ToM 403.07pt, andere dagen 424.24pt. Op precies die gemeenschappelijke steekproef: gemiddelde netto ToM 55.313pt, andere dagen -7.727pt.

### CONTINUOUS_2022_2024_UNVERIFIED

Gemeenschappelijke steekproef met vooraf bekendeATR14: 477 dagen; 86 ToM en 391 andere dagen. OntbrekendeATR: 4 ToM en 12 andere dagen. Deze dagen blijven gewoon in het oorspronkelijke modelresultaat staan.

Gemiddelde voorafATR: ToM 239.11pt, andere dagen 248.60pt. Op precies die gemeenschappelijke steekproef: gemiddelde netto ToM 19.199pt, andere dagen 2.060pt.

ATR-normalisatie is een aanvullende beschrijvende vergelijking, geen positiegrootteregel of causale identificatie. Regime, prijsniveau en andere kalenderkenmerken kunnen nog verschillen. Er is geen volatiliteitsgrens geoptimaliseerd.

## Concentratie, drawdown en excursies

| Bron | Top3 aandeel netto | Netto zonder top3 pt | Gesloten DD pt | Minuut-close DD pt | Slechtste dag pt | MAE mediaan / P95 / max pt |
|---|---:|---:|---:|---:|---:|---|
| DISCOVERY | 37.8% | 2714.200 | 1307.075 | 1512.825 | -583.975 | 102.25 / 497.00 / 747.75 |
| CONTINUOUS_2022_2024_UNVERIFIED | 54.5% | 654.925 | 1149.750 | 1320.225 | -499.225 | 69.62 / 331.89 / 657.00 |

Minuut-close-drawdown gebruikt de waargenomen minuutcloses en rekent de volledige roundtripfrictie bij entry. Dit is geen tick-drawdown en geen gegarandeerde intrabar-worst-case. MAE wordt gemeten vanaf de entry tot het vastgelegde einde, niet vanaf een achteraf gekozen stop. Vermenigvuldig punten met$20 voor éénNQ. Zonder rekeninggrootte, marginhistorie en risicobudget volgt hieruit geen oordeel dat het kapitaalrisico aanvaardbaar is.

### Weglaatcontroles DISCOVERY

Top3-datums: 2026-08-04, 2026-03-31, 2026-08-03. Leave-one-day-out gemiddeld netto: [46.522; 61.850]pt. Leave-one-quarter-out gemiddeld netto: [37.746; 65.986]pt. MFE mediaan/P95: 190.00/545.25pt.

| Weggelaten kwartaal | Overige trades | Netto totaal pt | Gemiddeld netto pt |
|---|---:|---:|---:|
| 2025Q1 | 69 | 3549.475 | 51.442 |
| 2025Q2 | 69 | 3138.225 | 45.482 |
| 2025Q3 | 70 | 4619.000 | 65.986 |
| 2025Q4 | 70 | 4423.750 | 63.196 |
| 2026Q1 | 70 | 3927.000 | 56.100 |
| 2026Q2 | 69 | 2604.475 | 37.746 |
| 2026Q3 | 69 | 3922.225 | 56.844 |
### Weglaatcontroles CONTINUOUS_2022_2024_UNVERIFIED

Top3-datums: 2023-02-01, 2024-07-02, 2024-03-01. Leave-one-day-out gemiddeld netto: [13.090; 21.792]pt. Leave-one-quarter-out gemiddeld netto: [7.323; 21.601]pt. MFE mediaan/P95: 106.50/272.31pt.

| Weggelaten kwartaal | Overige trades | Netto totaal pt | Gemiddeld netto pt |
|---|---:|---:|---:|
| 2022Q4 | 89 | 1330.475 | 14.949 |
| 2023Q1 | 78 | 571.200 | 7.323 |
| 2023Q2 | 79 | 1286.475 | 16.284 |
| 2023Q3 | 79 | 1706.475 | 21.601 |
| 2023Q4 | 78 | 744.700 | 9.547 |
| 2024Q1 | 78 | 1538.200 | 19.721 |
| 2024Q2 | 78 | 1426.450 | 18.288 |
| 2024Q3 | 81 | 1628.275 | 20.102 |
| 2024Q4 | 80 | 1289.750 | 16.122 |

Deze weglaatcontroles zijn stresstests. Geen enkele datum of kwartaal wordt op basis hiervan uit toekomstige handelsregels verwijderd.

## Kosten en vaste entryvertragingen

Hetzelfde vooraf vastgelegde ToM-cohort, entry op09:30/09:31/09:35-open en steeds dezelfde15:59-closeproxy. Geen gekozen winnaar onder de negen scenario’s. Kosten34,50/44,50USD betekenen1/2 extraNQ-ticks per leg BOVENOP de vaste24,50USD.

| Bron | Entryvertraging min | RT kosten USD | Trades | Netto pt | Gem. netto pt | PF | Gesloten DD pt |
|---|---:|---:|---:|---:|---:|---:|---:|
| DISCOVERY | 0 | 24.50 | 81 | 4364.025 | 53.877 | 1.706 | 1307.075 |
| DISCOVERY | 0 | 34.50 | 81 | 4323.525 | 53.377 | 1.698 | 1320.575 |
| DISCOVERY | 0 | 44.50 | 81 | 4283.025 | 52.877 | 1.690 | 1334.075 |
| DISCOVERY | 1 | 24.50 | 81 | 4114.025 | 50.790 | 1.673 | 1350.825 |
| DISCOVERY | 1 | 34.50 | 81 | 4073.525 | 50.290 | 1.665 | 1359.325 |
| DISCOVERY | 1 | 44.50 | 81 | 4033.025 | 49.790 | 1.656 | 1367.825 |
| DISCOVERY | 5 | 24.50 | 81 | 3669.025 | 45.297 | 1.627 | 1072.800 |
| DISCOVERY | 5 | 34.50 | 81 | 3628.525 | 44.797 | 1.619 | 1076.800 |
| DISCOVERY | 5 | 44.50 | 81 | 3588.025 | 44.297 | 1.610 | 1080.800 |
| CONTINUOUS_2022_2024_UNVERIFIED | 0 | 24.50 | 90 | 1440.250 | 16.003 | 1.322 | 1149.750 |
| CONTINUOUS_2022_2024_UNVERIFIED | 0 | 34.50 | 90 | 1395.250 | 15.503 | 1.311 | 1154.750 |
| CONTINUOUS_2022_2024_UNVERIFIED | 0 | 44.50 | 90 | 1350.250 | 15.003 | 1.300 | 1159.750 |
| CONTINUOUS_2022_2024_UNVERIFIED | 1 | 24.50 | 90 | 1357.500 | 15.083 | 1.316 | 1093.250 |
| CONTINUOUS_2022_2024_UNVERIFIED | 1 | 34.50 | 90 | 1312.500 | 14.583 | 1.304 | 1098.250 |
| CONTINUOUS_2022_2024_UNVERIFIED | 1 | 44.50 | 90 | 1267.500 | 14.083 | 1.292 | 1103.250 |
| CONTINUOUS_2022_2024_UNVERIFIED | 5 | 24.50 | 90 | 1335.250 | 14.836 | 1.324 | 1128.250 |
| CONTINUOUS_2022_2024_UNVERIFIED | 5 | 34.50 | 90 | 1290.250 | 14.336 | 1.312 | 1133.250 |
| CONTINUOUS_2022_2024_UNVERIFIED | 5 | 44.50 | 90 | 1245.250 | 13.836 | 1.300 | 1138.250 |

Minuutopens en closes zijn meetankers, geen bewijs van uitvoerbare beursfills. Geen bid/ask-, queue-, orderlatency- of publicatievintagebewijs. De vaste kalenderselectie is vóór entry bekend, maar de latere technische volledigheid van een dag is dat niet.

## Kwartalen

| Bron | Kwartaal | ToM N | ToM netto pt | ToM gem. | Andere N | Andere gem. | Verschil gem. |
|---|---|---:|---:|---:|---:|---:|---:|
| DISCOVERY | 2024Q4 | 0 | 0.000 | n.v.t. | 2 | -117.850 | n.v.t. |
| DISCOVERY | 2025Q1 | 12 | 814.550 | 67.879 | 48 | -52.011 | 119.891 |
| DISCOVERY | 2025Q2 | 12 | 1225.800 | 102.150 | 50 | 42.165 | 59.985 |
| DISCOVERY | 2025Q3 | 11 | -254.975 | -23.180 | 52 | 7.371 | -30.551 |
| DISCOVERY | 2025Q4 | 11 | -59.725 | -5.430 | 51 | -37.352 | 31.923 |
| DISCOVERY | 2026Q1 | 11 | 437.025 | 39.730 | 49 | -28.337 | 68.067 |
| DISCOVERY | 2026Q2 | 12 | 1759.550 | 146.629 | 50 | 24.250 | 122.379 |
| DISCOVERY | 2026Q3 | 12 | 441.800 | 36.817 | 52 | -22.494 | 59.311 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2022Q4 | 1 | 109.775 | 109.775 | 3 | -40.142 | 149.917 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2023Q1 | 12 | 869.050 | 72.421 | 50 | 30.070 | 42.351 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2023Q2 | 11 | 153.775 | 13.980 | 50 | 29.150 | -15.170 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2023Q3 | 11 | -266.225 | -24.202 | 51 | -15.053 | -9.149 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2023Q4 | 12 | 695.550 | 57.962 | 50 | 11.505 | 46.457 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2024Q1 | 12 | -97.950 | -8.162 | 49 | 9.999 | -18.162 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2024Q2 | 12 | 13.800 | 1.150 | 51 | -0.686 | 1.836 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2024Q3 | 9 | -188.025 | -20.892 | 49 | -29.424 | 8.532 |
| CONTINUOUS_2022_2024_UNVERIFIED | 2024Q4 | 10 | 150.500 | 15.050 | 50 | -9.790 | 24.840 |

## Bronvergelijking

BestaandeNQH24-pilot tegen de generieke reeks: 19 volledige gemeenschappelijkeRTH-dagen. RTH-open/closebeweging exact gelijk: 52.6%. Mediane absolute afwijking 0.000pt, maximum 2.500pt. Op 4 ToM-dagen samen bedraagt generic minus contract 1.750pt. Dit certificeert niet de hele oudere keten. De eerdere15,5pt-afwijking op het twee-minutenanker van31januari blijft staan.

De493 oudere dagen zijn een afzonderlijke gevoeligheidsbron, geen onafhankelijke validatie. Geen pooling van vendors, geen tijdverschuivingszoektocht, geen wijziging van bronbytes of rollregels.

## Reproductie en beperkingen

Beide oorspronkelijke ToM-ledgers zijn exact op geselecteerde datums, bruto/netto enMFE/MAE gereproduceerd. 497 bestaande bestanden worden opSHA-256 bewaakt. Nieuwe analyses zijn apart opgeslagen; geen oude rapporten overschreven. De eindverificatie staat inresearch/month-turn-audit-verification.json. Publieke exports bevatten alleen afgeleide aggregaten; dagelijkse ledgers en brondata blijven privé. Er is geen aankoop, download, live order, Git-push of Vercel-publicatie uitgevoerd.

Het doel is benchmarkmeerwaarde beoordelen, niet achteraf een winstmodel claimen. Een publicatie over dagelijkse aandelenrendementen bij maandwissel bewijst geenNQ-RTH-edge of institutionele oorzaak: [McConnell en Xu](https://docs.lib.purdue.edu/ciberwp/43/). Herhaald selecteren op dezelfde historie blijft gevoelig voor [backtestoverfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).
