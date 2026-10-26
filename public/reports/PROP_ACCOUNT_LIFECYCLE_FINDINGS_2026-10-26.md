# Levenscyclus: netto cash en interpretatie — 26 oktober 2026

Deze tabellen horen bij PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md. Alle regels,
kosten, payout-beleid en de 252-sessiehorizon zijn vóór de accountreplay vastgelegd.
Geen nieuwe kandidaat is toegevoegd: Judas blijft de enige intraday-motor.

## Netto dollars per gestart account: beide perioden afzonderlijk

De band hieronder is een wiskundige identificatiegrens, GEEN 95%-interval en GEEN
geschatte waarschijnlijkheidsverdeling. Bekende paden gebruiken hun werkelijke cash
tot tweede payout/jaargrens/falen. Bij een onopgelost bronpad is de ondergrens:
reeds ontvangen cash minus maximaal mogelijke abonnementen/activatie binnen het
venster. De bovengrens voegt maximaal twee toegestane payouts toe minus al betaalde
fees. De bovengrens is nadrukkelijk geen aannemelijk best-case rendement.

Daarmee hoeft geen winst of verlies voor ontbrekende minuten te worden verzonnen.
Een positieve ondergrens geldt alleen voor deze historische jaarcohorten, dit
payout-beleid en de modelaannames; geen bewijs van toekomstige winstgevendheid.
De all-start puntverwachting is ONBEKEND zolang bronpaden onopgelost zijn. Het
gemiddelde van alleen opgeloste accounts is selectief en vervangt die niet.

| Route | Model | MNQ | Periode | Starts | Passes | Payout1 | Payout2 | Onbekende paden | Netto $/start: ondergrens | Bovengrens |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 2597.95 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 1 | 2024_2026 | 171 | 135 | 14 | 0 | 14 | -534.01 | -178.93 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 1 | COMBINED | 669 | 135 | 14 | 0 | 416 | -700.21 | 1888.17 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 2 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 2597.95 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 2 | 2024_2026 | 171 | 140 | 89 | 0 | 14 | 156.90 | 511.98 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 2 | COMBINED | 669 | 140 | 89 | 0 | 416 | -523.61 | 2064.77 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 2597.95 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 1 | 2024_2026 | 171 | 66 | 0 | 0 | 14 | -535.35 | -180.27 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 1 | COMBINED | 669 | 66 | 0 | 0 | 416 | -700.55 | 1887.82 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 2 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 2597.95 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 2 | 2024_2026 | 171 | 105 | 72 | 0 | 14 | 127.15 | 482.22 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 2 | COMBINED | 669 | 105 | 72 | 0 | 416 | -531.21 | 2057.16 |
| TOPSTEP_STANDARD | S2-Judas | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 498 | -786.00 | 3504.46 |
| TOPSTEP_STANDARD | S2-Judas | 1 | 2024_2026 | 171 | 0 | 0 | 0 | 171 | -786.00 | 3528.94 |
| TOPSTEP_STANDARD | S2-Judas | 1 | COMBINED | 669 | 0 | 0 | 0 | 669 | -786.00 | 3510.72 |
| TOPSTEP_STANDARD | S2-Judas | 2 | 2019_2021 | 498 | 1 | 0 | 0 | 456 | -726.40 | 3206.45 |
| TOPSTEP_STANDARD | S2-Judas | 2 | 2024_2026 | 171 | 6 | 0 | 0 | 109 | -520.53 | 2226.75 |
| TOPSTEP_STANDARD | S2-Judas | 2 | COMBINED | 669 | 7 | 0 | 0 | 565 | -673.78 | 2956.03 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 4050.97 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 1 | 2024_2026 | 171 | 135 | 0 | 0 | 14 | -562.52 | -60.08 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 1 | COMBINED | 669 | 135 | 0 | 0 | 416 | -707.50 | 3000.16 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 2 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 4050.97 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 2 | 2024_2026 | 171 | 140 | 102 | 0 | 14 | 192.51 | 694.96 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 2 | COMBINED | 669 | 140 | 102 | 0 | 416 | -514.51 | 3193.15 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 4050.97 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 1 | 2024_2026 | 171 | 66 | 0 | 0 | 14 | -535.35 | -32.91 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 1 | COMBINED | 669 | 66 | 0 | 0 | 416 | -700.55 | 3007.11 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 2 | 2019_2021 | 498 | 0 | 0 | 0 | 402 | -757.28 | 4050.97 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 2 | 2024_2026 | 171 | 105 | 91 | 35 | 14 | 403.68 | 906.12 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 2 | COMBINED | 669 | 105 | 91 | 35 | 416 | -460.53 | 3247.13 |
| TOPSTEP_CONSISTENCY | S2-Judas | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 498 | -786.00 | 5304.46 |
| TOPSTEP_CONSISTENCY | S2-Judas | 1 | 2024_2026 | 171 | 0 | 0 | 0 | 171 | -786.00 | 5328.94 |
| TOPSTEP_CONSISTENCY | S2-Judas | 1 | COMBINED | 669 | 0 | 0 | 0 | 669 | -786.00 | 5310.72 |
| TOPSTEP_CONSISTENCY | S2-Judas | 2 | 2019_2021 | 498 | 1 | 0 | 0 | 456 | -726.40 | 4854.64 |
| TOPSTEP_CONSISTENCY | S2-Judas | 2 | 2024_2026 | 171 | 6 | 0 | 0 | 109 | -520.53 | 3374.12 |
| TOPSTEP_CONSISTENCY | S2-Judas | 2 | COMBINED | 669 | 7 | 0 | 0 | 565 | -673.78 | 4476.21 |
| MFFU_BUILDER | S1-Judas-Bull0930 | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 49 | -153.00 | 161.86 |
| MFFU_BUILDER | S1-Judas-Bull0930 | 1 | 2024_2026 | 171 | 0 | 0 | 0 | 5 | -153.00 | -59.43 |
| MFFU_BUILDER | S1-Judas-Bull0930 | 1 | COMBINED | 669 | 0 | 0 | 0 | 54 | -153.00 | 105.30 |
| MFFU_BUILDER | S1-Judas-Bull0930 | 2 | 2019_2021 | 498 | 0 | 0 | 0 | 49 | -153.00 | 161.86 |
| MFFU_BUILDER | S1-Judas-Bull0930 | 2 | 2024_2026 | 171 | 0 | 0 | 0 | 5 | -153.00 | -59.43 |
| MFFU_BUILDER | S1-Judas-Bull0930 | 2 | COMBINED | 669 | 0 | 0 | 0 | 54 | -153.00 | 105.30 |
| MFFU_BUILDER | S1-Judas-0830 | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 50 | -153.00 | 168.29 |
| MFFU_BUILDER | S1-Judas-0830 | 1 | 2024_2026 | 171 | 0 | 0 | 0 | 5 | -153.00 | -59.43 |
| MFFU_BUILDER | S1-Judas-0830 | 1 | COMBINED | 669 | 0 | 0 | 0 | 55 | -153.00 | 110.08 |
| MFFU_BUILDER | S1-Judas-0830 | 2 | 2019_2021 | 498 | 0 | 0 | 0 | 50 | -153.00 | 168.29 |
| MFFU_BUILDER | S1-Judas-0830 | 2 | 2024_2026 | 171 | 0 | 0 | 0 | 5 | -153.00 | -59.43 |
| MFFU_BUILDER | S1-Judas-0830 | 2 | COMBINED | 669 | 0 | 0 | 0 | 55 | -153.00 | 110.08 |
| MFFU_BUILDER | S2-Judas | 1 | 2019_2021 | 498 | 0 | 0 | 0 | 306 | -153.00 | 1813.27 |
| MFFU_BUILDER | S2-Judas | 1 | 2024_2026 | 171 | 0 | 0 | 0 | 110 | -153.00 | 1905.48 |
| MFFU_BUILDER | S2-Judas | 1 | COMBINED | 669 | 0 | 0 | 0 | 416 | -153.00 | 1836.84 |
| MFFU_BUILDER | S2-Judas | 2 | 2019_2021 | 498 | 1 | 0 | 0 | 277 | -153.00 | 1626.92 |
| MFFU_BUILDER | S2-Judas | 2 | 2024_2026 | 171 | 8 | 0 | 0 | 105 | -153.00 | 1811.91 |
| MFFU_BUILDER | S2-Judas | 2 | COMBINED | 669 | 9 | 0 | 0 | 382 | -153.00 | 1674.20 |

## Onderzoeksconclusie

De huidige bronnen rechtvaardigen geen algemeen winstgevend prop-model in beide
perioden. In de 252-sessievergelijking zijn er bij Topstep Standard wel eerste
payouts, maar geen tweede bekende payouts. De aparte Consistency-route kent bij
S1-Judas-0830 op 2 MNQ wel twee payouts; die starts liggen in het recente blok.
Deze route is vooraf als aparte vergelijking vastgelegd en vervangt Standard niet
achteraf als hoofdroute.

Het recente S1-blok op 2 MNQ heeft zelfs bij de conservatieve ontbrekende-padgrenzen
een positief cashresultaat voor Topstep Standard. Dat is een waargenomen plaatselijk
resultaat. Het oudere blok bevat te veel onopgeloste nachtpaden om dezelfde conclusie
te trekken. Een nul bekende evaluatiepasses daar is geen bewijs van nul werkelijke
slaagkans. Overlappende starts geven geen onafhankelijke replicaties.

Builder heeft voor de selectieve kernen geen bekende pass of payout. De meeste
bekende afsluitingen komen door de conservatief toegepaste zeven-kalenderdagenregel,
niet door verliesvloer. De aanvullende officiële policy zegt 'could be closed';
dit is een model van sluiting, geen zekerheid over discretionaire handhaving.
De los gerapporteerde variant zonder eval-inactiviteit helpt oorzaken scheiden,
maar verandert niets aan de officiële funded-inactiviteitslimiet.

Geen extra setup, contractopschaling of keep-alive is gebruikt om een gewenste
uitkomst af te dwingen. Een nieuw intraday-model is niet nodig om de conclusie
van deze afgebakende opdracht te beantwoorden. S1/S2 en eerdere studies blijven
als benchmarks intact; deze simulatie is geen live-handelvrijgave.

## Bestanden en controle

- Volledige regels/tabellen: `docs/PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md`.
- Alle 144 aggregaten: `public/data/prop-lifecycle/summary.csv` en `summary.json`.
- Iedere accountstart, tijd tot pass, fees en milestones: privé in
  `artifacts/prop-lifecycle/run1/accounts.csv` en `accounts.json.gz`.
- Hashbewijs dubbele accountreplay: `research/prop-lifecycle-verification.json`.
- Nieuwe dashboardroute: `/research/prop-lifecycle`; alleen aggregaten zijn publiek.

Gebruikte resultaat-SHA-256: `bdadc3e158ce8247dda36b63d3560619ff1e92e499d03d3318216eac4313fab4`.
