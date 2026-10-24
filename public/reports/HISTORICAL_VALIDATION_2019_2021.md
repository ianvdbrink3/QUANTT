# Onafhankelijke historische toets: drie bevroren modellen

REGISTERED_HISTORICAL_REPLICATION_COMPLETED_WITH_ACCEPTED_SOURCE_LIMITS

24 oktober 2026. Formele uitkomstvrijgave door de gebruiker met expliciete aanvaarding van de bekende bronbeperkingen. Geen parameters, rollovers, prijzen of eerdere rapporten aangepast. Dit is historische replicatie, geen prospectieve of onafhankelijk-vendor-gecertificeerde proef.

## Vooraf vastgelegde steekproef en varianten

Beslissende periode: 2019-01-14 t/m 2021-12-31. De8 eerder bekeken dagen2–11januari2019 zijn uitgesloten, maar mogen als vooraf bekende opwarming dienen. Er zijn 36 bruikbare kalendermaanden en 733 gemeenschappelijke evaluatiedagen. Niet elke evaluatiedag geeft een signaal.

Primair: negen voorlopige datums blind uitgesloten, plus ontbrekende RTH-/09:29-ankerbars en onbruikbare ATR. Secundair: beschikbare data van de negen datums meenemen waar bestaande full-RTH-regels dat toestaan. Geen aanvulling van ontbrekende minuten, geen speciale feestdagtrades. De negen waren al niet eligible of vallen buiten het venster. Daarom zijn de twee vooraf vastgelegde evaluatiemaskers identiek. Dezelfde indicatorhistorie blijft in beide varianten behouden. Een nuleffect in deze gevoeligheidscontrole valideert die historie NIET onafhankelijk.

Per-model context: maandwisseling733, compressie705, sweep619dagen. Dagen zonder benodigde modelspecifieke context blijven voor die sleeve zonder positie. Het gemeenschappelijke dagelijkse statistiekuniversum blijft733dagen, inclusief nul-posities. Geen ToM-selectie op alleen aanwezige kalenderdagen.

## Primair: ruwe NQ-punten en dollars

| Model | Componenttrades | Actieve dagen | Netto pt | Netto $ | PF | Winrate | DD dag pt | DD minuut pt | Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Maandwisseling | 137 | 137 | 295.425 | 5908.50 | 1.050 | 57.66% | 1218.550 | 1391.400 | 0.123 |
| Compressie-uitbraak | 201 | 201 | -293.725 | -5874.50 | 0.958 | 47.76% | 1214.925 | 1421.875 | -0.132 |
| Vroege sweep tot12:00 | 90 | 90 | -680.250 | -13605.00 | 0.750 | 43.33% | 1112.425 | 1247.375 | -0.619 |
| Gelijke1/3-combinatie | 428 | 366 | -226.183 | -4523.67 | 0.952 | 50.55% | 1059.933 | 1125.175 | -0.195 |

NQwaarde$20/punt. Kosten$24,50RT=1,225punt per volledige componenttrade, reeds in netto verwerkt. Portfolio=precies1/3 per model, niet3contracten en geen herverdeling bij afwezige signalen. Portfoliopunten zijn theoretische gewogen contractpunten. PF/winrate op geaggregeerde actieve dagen; portfolio-tradetelling betreft componentuitvoeringen. Geen MNQ- of werkelijk brokerfill-resultaat geclaimd.

## Primair: vooraf bekende ATR14-eenheden en geregistreerde toetsen

| Model | Netto ATR | PF ATR | DD dag ATR | DD minuut ATR | Gem. ATR/dag | 95% CI gem. ATR/dag | Ruwe p | Holm4 p | Gereserveerde Holm6 p | Formeel oordeel |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| Maandwisseling | 1.02433 | 1.029 | 7.93187 | 8.99631 | 0.001397 | [-0.016743; 0.022952] | 0.89471 | 1.00000 | 1.00000 | NO_STATISTICAL_SUPPORT |
| Compressie-uitbraak | -2.91865 | 0.922 | 5.81342 | 6.49355 | -0.003982 | [-0.018421; 0.011961] | 0.60574 | 1.00000 | 1.00000 | NO_STATISTICAL_SUPPORT |
| Vroege sweep tot12:00 | -2.25884 | 0.843 | 4.63469 | 4.76478 | -0.003082 | [-0.016122; 0.009009] | 0.62624 | 1.00000 | 1.00000 | NO_STATISTICAL_SUPPORT |
| Gelijke1/3-combinatie | -1.38439 | 0.948 | 4.28950 | 4.49178 | -0.001889 | [-0.011137; 0.008902] | 0.70913 | 1.00000 | 1.00000 | NO_STATISTICAL_SUPPORT |

1ATR is een schaalmaat, geen stop of maximale schade. Alle vier primaire toetsen betreffen het dagelijkse nettoATR-gemiddelde; ruwepuntenp-waarden zijn uitsluitend beschrijvend. Exact de geregistreerde gezamenlijke2-maands moving-blockbootstrap,10.000trekkingen,seed20261022311. CI95 is nominaal, niet meervoudig gecorrigeerd. De hierna getoonde Bonferroni4-intervallen geven afzonderlijk een benaderende simultane95%-band. Bootstrap veronderstelt voldoende stabiele afhankelijkheid; dekking is geen garantie.

| Model | Simultane95%-band gem. ATR/dag (Bonf4) | Nominale95% CI totale ATR bij vaste N | 95% CI Sharpe ATR | Ruwepunten Holm4 p (beschrijvend) |
|---|---|---|---|---:|
| Maandwisseling | [-0.022566; 0.027910] | [-12.27251; 16.82387] | [-0.929; 1.294] | 1.00000 |
| Compressie-uitbraak | [-0.022541; 0.015910] | [-13.50235; 8.76758] | [-1.274; 0.811] | 1.00000 |
| Vroege sweep tot12:00 | [-0.019973; 0.011978] | [-11.81758; 6.60337] | [-1.897; 1.125] | 1.00000 |
| Gelijke1/3-combinatie | [-0.014116; 0.011399] | [-8.16347; 6.52537] | [-1.303; 1.099] | 1.00000 |

Holm4: de4vooraf geregistreerde co-primaire ATR-toetsen. Voor een projectbrede claim daarnaast Holm6, met de2niet uitgevoerde afternoonhypothesen op p=1; die twee strategieën zijn niet gedraaid. Minimaal24maanden en30ATR-readytrades per signaal. De combinatie vereist voldoende informatie voor alle3. Een secundaire uitkomst kan een falende primaire toets niet redden. STATISTICAL_SUPPORT_ON_REGISTERED_REMAINDER is niet hetzelfde als bewezen toekomstige winstgevendheid of toestemming voor echt geld.

## Secundaire inclusie en verschil met primair

| Model | Trades | Netto pt | Netto ATR | PF punten / ATR | Winrate | DD dag pt / ATR | Holm4 ATR p, beschrijvend | Δ pt | Δ ATR |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|
| Maandwisseling | 137 | 295.425 | 1.02433 | 1.050 / 1.029 | 57.66% | 1218.550 / 7.93187 | 1.00000 | 0.000 | 0.00000 |
| Compressie-uitbraak | 201 | -293.725 | -2.91865 | 0.958 / 0.922 | 47.76% | 1214.925 / 5.81342 | 1.00000 | 0.000 | 0.00000 |
| Vroege sweep tot12:00 | 90 | -680.250 | -2.25884 | 0.750 / 0.843 | 43.33% | 1112.425 / 4.63469 | 1.00000 | 0.000 | 0.00000 |
| Gelijke1/3-combinatie | 428 | -226.183 | -1.38439 | 0.952 / 0.948 | 50.55% | 1059.933 / 4.28950 | 1.00000 | 0.000 | 0.00000 |

## Alle kwartalen: vaste eindperiode, geen selectie

| Kwartaal | Model | Trades | Primair netto pt | Primair netto ATR | Inclusie netto pt | Inclusie netto ATR |
|---|---|---:|---:|---:|---:|---:|
| 2019Q1 | Maandwisseling | 9 | 162.225 | 1.34274 | 162.225 | 1.34274 |
| 2019Q1 | Compressie-uitbraak | 13 | -50.675 | -0.58343 | -50.675 | -0.58343 |
| 2019Q1 | Vroege sweep tot12:00 | 7 | 79.675 | 0.82948 | 79.675 | 0.82948 |
| 2019Q1 | Gelijke1/3-combinatie | 29 | 63.742 | 0.52960 | 63.742 | 0.52960 |
| 2019Q2 | Maandwisseling | 12 | -76.200 | -0.95422 | -76.200 | -0.95422 |
| 2019Q2 | Compressie-uitbraak | 20 | 221.250 | 1.94852 | 221.250 | 1.94852 |
| 2019Q2 | Vroege sweep tot12:00 | 3 | 27.075 | 0.01225 | 27.075 | 0.01225 |
| 2019Q2 | Gelijke1/3-combinatie | 35 | 57.375 | 0.33552 | 57.375 | 0.33552 |
| 2019Q3 | Maandwisseling | 11 | -324.475 | -3.77628 | -324.475 | -3.77628 |
| 2019Q3 | Compressie-uitbraak | 20 | -69.500 | -0.65947 | -69.500 | -0.65947 |
| 2019Q3 | Vroege sweep tot12:00 | 4 | 19.350 | 0.30442 | 19.350 | 0.30442 |
| 2019Q3 | Gelijke1/3-combinatie | 35 | -124.875 | -1.37711 | -124.875 | -1.37711 |
| 2019Q4 | Maandwisseling | 11 | -124.725 | -1.41119 | -124.725 | -1.41119 |
| 2019Q4 | Compressie-uitbraak | 20 | -82.750 | -1.67045 | -82.750 | -1.67045 |
| 2019Q4 | Vroege sweep tot12:00 | 3 | 1.575 | 0.10240 | 1.575 | 0.10240 |
| 2019Q4 | Gelijke1/3-combinatie | 34 | -68.633 | -0.99308 | -68.633 | -0.99308 |
| 2020Q1 | Maandwisseling | 12 | 593.800 | 4.68392 | 593.800 | 4.68392 |
| 2020Q1 | Compressie-uitbraak | 8 | -169.300 | -0.20425 | -169.300 | -0.20425 |
| 2020Q1 | Vroege sweep tot12:00 | 7 | -29.575 | -0.75783 | -29.575 | -0.75783 |
| 2020Q1 | Gelijke1/3-combinatie | 27 | 131.642 | 1.24061 | 131.642 | 1.24061 |
| 2020Q2 | Maandwisseling | 12 | 472.800 | 2.17735 | 472.800 | 2.17735 |
| 2020Q2 | Compressie-uitbraak | 21 | 110.275 | -0.29463 | 110.275 | -0.29463 |
| 2020Q2 | Vroege sweep tot12:00 | 7 | -222.825 | -0.93207 | -222.825 | -0.93207 |
| 2020Q2 | Gelijke1/3-combinatie | 40 | 120.083 | 0.31688 | 120.083 | 0.31688 |
| 2020Q3 | Maandwisseling | 10 | 553.250 | 2.44928 | 553.250 | 2.44928 |
| 2020Q3 | Compressie-uitbraak | 14 | 495.100 | 2.58563 | 495.100 | 2.58563 |
| 2020Q3 | Vroege sweep tot12:00 | 9 | 179.725 | 0.88419 | 179.725 | 0.88419 |
| 2020Q3 | Gelijke1/3-combinatie | 33 | 409.358 | 1.97303 | 409.358 | 1.97303 |
| 2020Q4 | Maandwisseling | 12 | 257.300 | 1.18217 | 257.300 | 1.18217 |
| 2020Q4 | Compressie-uitbraak | 20 | -505.500 | -2.07766 | -505.500 | -2.07766 |
| 2020Q4 | Vroege sweep tot12:00 | 8 | 267.700 | 0.92032 | 267.700 | 0.92032 |
| 2020Q4 | Gelijke1/3-combinatie | 40 | 6.500 | 0.00827 | 6.500 | 0.00827 |
| 2021Q1 | Maandwisseling | 12 | -503.950 | -2.07211 | -503.950 | -2.07211 |
| 2021Q1 | Compressie-uitbraak | 16 | -282.100 | -1.40428 | -282.100 | -1.40428 |
| 2021Q1 | Vroege sweep tot12:00 | 14 | -894.400 | -3.64665 | -894.400 | -3.64665 |
| 2021Q1 | Gelijke1/3-combinatie | 42 | -560.150 | -2.37435 | -560.150 | -2.37435 |
| 2021Q2 | Maandwisseling | 12 | -327.700 | -1.99937 | -327.700 | -1.99937 |
| 2021Q2 | Compressie-uitbraak | 17 | -71.825 | 0.07454 | -71.825 | 0.07454 |
| 2021Q2 | Vroege sweep tot12:00 | 7 | 24.675 | 0.04554 | 24.675 | 0.04554 |
| 2021Q2 | Gelijke1/3-combinatie | 36 | -124.950 | -0.62643 | -124.950 | -0.62643 |
| 2021Q3 | Maandwisseling | 12 | 80.050 | 0.79725 | 80.050 | 0.79725 |
| 2021Q3 | Compressie-uitbraak | 15 | -227.625 | -1.63044 | -227.625 | -1.63044 |
| 2021Q3 | Vroege sweep tot12:00 | 11 | 183.525 | 1.45882 | 183.525 | 1.45882 |
| 2021Q3 | Gelijke1/3-combinatie | 38 | 11.983 | 0.20854 | 11.983 | 0.20854 |
| 2021Q4 | Maandwisseling | 12 | -466.950 | -1.39519 | -466.950 | -1.39519 |
| 2021Q4 | Compressie-uitbraak | 17 | 338.925 | 0.99727 | 338.925 | 0.99727 |
| 2021Q4 | Vroege sweep tot12:00 | 10 | -316.750 | -1.47970 | -316.750 | -1.47970 |
| 2021Q4 | Gelijke1/3-combinatie | 39 | -148.258 | -0.62587 | -148.258 | -0.62587 |

## Uitvoerings- en bronbeperkingen

Exacte volgende minuutopen en laatste minuutclose zijn OHLCV-proxies, geen tick-level uitvoeringsbewijs. Geen stops/targets of intrabar-volgordeclaim. Minuut-DD gebruikt minuutcloses met volledigeRT-frictie bij entry, niet de slechtst mogelijke tickroute. De2019–2021-reeks is niet prospectief en absolute niet-blootstelling aan alle marktinformatie is niet aantoonbaar.

De gebruiker heeft de resterende bronbeperkingen expliciet geaccepteerd:
- CROPPED_TABLES_REQUIRE_FULL_PRIMARY_PROVENANCE
- NQ_HALT_SECONDS_NOT_INDEPENDENTLY_CERTIFIED
- VENDOR_MISSING_MINUTE_SEMANTICS_AND_VOLUME_UNIVERSE_UNRESOLVED
- EARLIEST_TRUE_VOLUME_CROSSOVER_NOT_CERTIFIED
- LICENSE_AND_TICK_FILL_VALIDATION_UNCONFIRMED
- EXPLICIT_OUTCOME_RELEASE_REQUIRED

EXPLICIT_OUTCOME_RELEASE_REQUIRED in het historische voorbereidingsrapport is met dit aparte vrijgavebesluit afgehandeld; het oude rapport blijft als historische stand ongewijzigd. De andere beperkingen zijn aanvaard, niet technisch opgelost. De Barchart-vraag is nog open. Geen wijziging van rolloverdatum op basis van P&L.

## Reproductie, publicatie en privacy

Twee volledige runs vanaf alle105originele gehashteCSV-kopieën, opnieuw ontdubbeld, met opnieuw gereproduceerde volume-route, onveranderde spreads en exact dezelfde kalender-v2-context. Trade-/dagledgers, context en alle uitvoerbytes worden vergeleken voordat publieke bestanden worden geschreven. De reproductie is onafhankelijk uitgevoerd met dezelfde code en vendorbron, niet door een onafhankelijke leverancier of onderzoeker.

`python -m scripts.historical_validation verify` controleert freeze en uitvoerhashes. `replay` voert de vrijgegeven gepaarde run eenmaal uit; als een afgerond bewijs bestaat, controleert het alleen hashes. Geen parameterzoektocht of tussenresultaat-API. CSV-ledgers, prijsarrays en context blijven Gitignored. Publiek: dit aggregatierapport, kwartaal-CSV en JSON. Publicatiebewijs met exacte commit en productieadres wordt afzonderlijk vastgelegd na geslaagde tests/build.
