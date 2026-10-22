# Precisie ochtendherstel:29 versus40 Gap-Down-dagen

Dit is een vooraf afzonderlijk vastgelegde precisie-uitbreiding op bestaande ontdekkingsdata, geen onafhankelijke validatie of nieuw handelsmodel. Alleen09:45 Open→10:29 Close wordt gemeten, bruto en opwaarts positief. De indeling gebruikt09:30 Open→09:44 Close. Geen eerste-kwartierbar of09:44close/open-gap zit in de uitkomst.

## 1. Twee gevraagde betrouwbaarheidsintervallen

| Grootheid | Schatting pt | HAC(5) nominaal95%-BI pt | Block-bootstrap nominaal95%-BI pt |
|---|---:|---|---|
| Gemiddelde29 doorzakkende Gap-Down-dagen | 57,46 | [-4,40; 119,32] | [0,62; 119,89] |
| Verschil29 doorzakkend minus40 opverend | 52,13 | [-22,07; 126,33] | [-16,93; 127,25] |

Het gemiddelde van de40 opverende dagen blijft +5,325 pt. Alle69 eerder berekende vervolgrendementen en de29/40-indeling zijn ongewijzigd.

Hoofdmethode: één invloedsscore per oorspronkelijke geplande handelsdag op de454-dagenkalender. Niet-geselecteerde dagen hebben nulinvloed, geen fictief nulrendement. Bartlett-HAC met lags1–5; geselecteerde-dagen-correctie29/28 voor het gemiddelde en69/68 voor het contrast; t-vrijheidsgraden28 voor beide. Contrastscores worden op dezelfde dagkalender afgetrokken om temporele covariantie te behouden. CR1-sensitiviteits-SE staat in JSON/CSV.

Gevoeligheidscontrole:20.000 circular moving-block bootstrapreplicaties van vijf geplande sessies, seed20261022. Hele dagrecords en groepsmaskers worden samen geresampled; beide conditionele gemiddelden worden per replicatie opnieuw berekend. Alle20.000 replicaties hebben beide groepen. De intervallen zijn percentielintervallen, geen studentized of simultane intervallen.

**Beide95%-intervallen zijn puntsgewijs en verkennend, niet gecorrigeerd voor de eerdere zoektocht of voor gezamenlijke dekking.** Kleine aantallen en regimestructuur kunnen de dekking beperken. Het contrastinterval bevat nul bij beide methoden. Voor het29-dagengemiddelde ligt de bootstrapondergrens net boven nul terwijl de HAC-ondergrens eronder ligt: geen methode-onafhankelijke conclusie van positieve verwachting. Er zijn geen nieuwe p-waarden berekend.

## 2. Alle kalenderkwartalen

| Kwartaal | N doorzakkend | Gem. pt | Mediaan pt | N opverend | Gem. pt | Mediaan pt | Mediane MFE doorzakkend | Mediane MAE doorzakkend |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024Q4 | 0 | — | — | 0 | — | — | — | — |
| 2025Q1 | 4 | -78,06 | -94,00 | 8 | 50,12 | 53,88 | 91,50 | 139,25 |
| 2025Q2 | 4 | 115,81 | 8,38 | 8 | -3,66 | 21,25 | 172,50 | 96,00 |
| 2025Q3 | 2 | 129,00 | 129,00 | 1 | 29,75 | 29,75 | 140,00 | 61,25 |
| 2025Q4 | 5 | 80,95 | 91,25 | 4 | 47,62 | 31,62 | 190,25 | 31,50 |
| 2026Q1 | 6 | -16,54 | 0,75 | 8 | -11,53 | 30,12 | 80,12 | 84,75 |
| 2026Q2 | 5 | 95,20 | 115,00 | 3 | -7,00 | -45,50 | 150,75 | 75,25 |
| 2026Q3 | 3 | 158,58 | 81,25 | 8 | -33,22 | -4,75 | 95,50 | 9,25 |

De29 doorzakkende dagen hebben in vijf van zeven niet-lege kwartalen een positief gemiddelde.2025Q1 en2026Q1 zijn negatief. Kwartaalgroepen bevatten slechts2–6 doorzakkende dagen;2024Q4 bevat geen Gap-Down-dagen. Geen kwartalen geselecteerd of weggelaten.

## 3. MFE/MAE van de29 doorzakkende dagen

Onderzoeksanker=09:45 Open. MFE=max(High van09:45 t/m10:29)−anker; MAE=anker−min(Low in hetzelfde venster). Beide zijn positieve afstanden in NQ-punten, geen uitvoerbare target/stop of bekende intraminuutvolgorde. De eerste en laatste45-minutenbar tellen mee; geen prijzen uit09:30–09:44 of vanaf10:30.

| Maat | N | Gemiddeld | Minimum | P10 | P25 | Mediaan | P75 | P90 | Maximum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mfe_points | 29 | 183,24 | 1,75 | 28,75 | 62,75 | 122,25 | 204,00 | 276,40 | 1606,00 |
| mae_points | 29 | 88,22 | 3,00 | 8,90 | 22,25 | 75,25 | 119,50 | 192,05 | 285,00 |

De maximale waargenomen MFE is 1606,00 punten op 2025-04-07. Deze bronwaarneming is behouden en niet afgeknipt; de grote maximale excursie trekt het MFE-gemiddelde omhoog ten opzichte van de mediaan. Dit is geen onafhankelijke vendor- of tickcertificatie.

## Afzonderlijke15:00-specificatie v2

Zie AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md en research/afternoon-candidate-v2.json. Twee parallelle primaire netto-puntentoetsen, één Holm2-familie, geen inhoudelijke horizon-gate. V1 blijft als historisch beslisspoor bewaard. Geen nieuwe15:00-uitkomsten op de435 dagen. De toekomstige onafhankelijke toets blijft geblokkeerd totdat het steekproef-/stopplan vooraf is vastgelegd.

## Verificatie

69 bronbestanden gehasht;29 excursiepaden opnieuw uit de bron geladen met byte-identieke replay; bestaande69 vervolgrendementen ongewijzigd;115 beschermde archiefbestanden en eerdere rapporten ongewijzigd. Geen nieuwe strategie, p-waarden of15:00-run. Ruwe prijzen en dagpaden blijven in de genegeerde artifacts-map. Geen GitHub/Vercel-publicatie in deze opdracht.

Protocol SHA-256: `765820a6d24e7a1b056cc33c7d690061aa84c4e513636929f8efa0a86b8e9237`.
