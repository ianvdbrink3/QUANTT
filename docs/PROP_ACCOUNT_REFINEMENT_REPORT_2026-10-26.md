# Prop-account levenscyclus — gerichte verfijning, 26 oktober 2026

Status: CONDITIONELE ONTWIKKELINGSSCENARIO'S, GEEN GOEDGEKEURD LIVE-MODEL.
De strikte eerdere rapporten en grenzen blijven byte-identiek beschikbaar.

## Vooraf vastgelegde vergelijking

1. FROZEN_STRICT: oorspronkelijke bronbevriezing, vaste 1/2 MNQ, geen keep-alive.
2. OBSERVED_BARS: alle daadwerkelijk geobserveerde OHLC tijdens dezelfde bestaande
   trades; geen bevriezing op een ontbrekende minuut, geen forward-fill.
3. OBSERVED_KEEPALIVE: voorgaande plus één synthetische 1-MNQ nul-bruto roundtrip
   met $3,22 kosten na zes NY-kalenderdagen, vervroegd vóór weekend/feestdag waar
   nodig. Uitvoering om 12:00 op een cashdag, uitsluitend flat en zonder werkende
   order of dagelijkse soft-pause. Een normale trade reset de timer al.
4. R250/R300: dezelfde onderhoudsregel, maar Judas-size floor(budget /
   (stopafstand × $2 + $3,22)), minimaal1/maximaal6MNQ. Overnight blijft1/2MNQ.
   KA650 is een extra Builder-kostenscenario van $6,50 per onderhoudstrade.

Dit is géén meting van het werkelijke pass-percentage: voor ontbrekende minuten is
niet bewezen dat er geen transacties waren of dat een floor/stop niet geraakt werd.
Een één-seconde marktfill met exact nul bruto rendement is evenmin zichtbaar in
1-minuut OHLC. Keep-alive-acceptatie is niet expliciet bevestigd door de firms;
het kostenmodel is een onderzoeksaanname, geen brokerintegratie of regelvrijgave.

Alle starts op dezelfde252cashsessies (498oud+171recent), én elke1171start tot
eigen era-einde. Geen onafhankelijke steekproeven door overlappende starts. Fees,
funded-reset naar nul, payout-consistency, winstdeling, floor na opname en de twee
payouts zijn gelijk aan de bevroren simulator. Geen nieuwe trading-signalen.

## Alle scenario's — gecombineerd, 669 starts met gelijke jaarfollow-up

Payout-percentages hebben alle starts als noemer, niet alleen geslaagde evaluaties.
Tijd tot pass is conditioneel op de bekende passes; geen wachttijdvoorspelling voor
alle accounts. ON is de vaste overnight-size; Judas kan onder hybride sizing meer
contracten gebruiken. Netto dollars = ontvangen payouts na winstdeling minus aankoop,
abonnementen en activatie tot tweede payout of horizon/falen. Onopgenomen equity
is geen cash. Niet de totale levensduur-EV; geen belasting/FX/API/transferkosten.

| Firm/payout-route | Model | Profiel | ON | Pass % | Mediane cashdagen tot pass | Payout1 % | Payout2 % | Netto $/start | Onbekend % | Gem. keep-alives |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | FROZEN_STRICT | 1 | 20.18 | 135.0 | 2.09 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | FROZEN_STRICT | 2 | 20.93 | 61.5 | 13.30 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_BARS | 1 | 22.27 | 142.0 | 2.09 | 0.00 | -605.91 | 0.00 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_BARS | 2 | 23.02 | 65.0 | 15.40 | 0.00 | -404.28 | 0.00 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE | 1 | 20.63 | 139.5 | 4.78 | 0.00 | -593.68 | 0.00 | 50.32 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE | 2 | 22.27 | 64.0 | 15.70 | 3.29 | -351.02 | 0.00 | 48.48 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 20.63 | 134.5 | 5.23 | 0.00 | -591.04 | 0.00 | 50.32 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 31.24 | 105.0 | 20.03 | 0.30 | -344.04 | 0.00 | 49.86 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 31.24 | 144.0 | 7.03 | 0.00 | -570.93 | 0.00 | 50.14 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 43.65 | 131.5 | 26.76 | 2.84 | -288.09 | 0.00 | 50.01 |
| TOPSTEP_STANDARD | S1-Judas-0830 | FROZEN_STRICT | 1 | 9.87 | 138.5 | 0.00 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-0830 | FROZEN_STRICT | 2 | 15.70 | 59.0 | 10.76 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_BARS | 1 | 11.96 | 135.5 | 0.00 | 0.00 | -604.87 | 0.00 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_BARS | 2 | 18.24 | 62.0 | 12.86 | 1.94 | -379.32 | 0.00 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE | 1 | 11.66 | 135.0 | 0.00 | 0.00 | -603.61 | 0.00 | 43.17 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE | 2 | 17.79 | 61.0 | 12.41 | 1.94 | -386.45 | 0.00 | 40.63 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 15.55 | 119.5 | 0.00 | 0.00 | -585.67 | 0.00 | 42.62 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 19.43 | 75.5 | 7.32 | 0.00 | -487.56 | 0.00 | 41.71 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 17.49 | 106.0 | 1.94 | 0.00 | -566.69 | 0.00 | 42.25 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 19.58 | 67.0 | 10.01 | 0.00 | -451.61 | 0.00 | 41.92 |
| TOPSTEP_STANDARD | S2-Judas | FROZEN_STRICT | 1 | 0.00 | — | 0.00 | 0.00 | ONBEKEND | 100.00 | 0.00 |
| TOPSTEP_STANDARD | S2-Judas | FROZEN_STRICT | 2 | 1.05 | 8.0 | 0.00 | 0.00 | ONBEKEND | 84.45 | 0.00 |
| TOPSTEP_STANDARD | S2-Judas | OBSERVED_BARS | 1 | 20.48 | 58.0 | 17.49 | 14.95 | -372.42 | 0.00 | 0.00 |
| TOPSTEP_STANDARD | S2-Judas | OBSERVED_BARS | 2 | 45.89 | 96.0 | 32.74 | 7.03 | -85.39 | 0.00 | 0.00 |
| TOPSTEP_STANDARD | S2-Judas | OBSERVED_KEEPALIVE | 1 | 20.33 | 58.0 | 17.49 | 14.95 | -377.34 | 0.00 | 14.62 |
| TOPSTEP_STANDARD | S2-Judas | OBSERVED_KEEPALIVE | 2 | 45.29 | 96.0 | 38.71 | 6.88 | -81.54 | 0.00 | 7.23 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | FROZEN_STRICT | 1 | 20.18 | 135.0 | 0.00 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | FROZEN_STRICT | 2 | 20.93 | 61.5 | 15.25 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_BARS | 1 | 22.27 | 142.0 | 0.00 | 0.00 | -613.20 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_BARS | 2 | 23.02 | 65.0 | 17.34 | 0.00 | -395.18 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE | 1 | 20.63 | 139.5 | 0.00 | 0.00 | -612.22 | 0.00 | 50.32 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE | 2 | 22.27 | 64.0 | 17.34 | 0.00 | -387.12 | 0.00 | 48.61 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 20.63 | 134.5 | 0.00 | 0.00 | -610.46 | 0.00 | 50.32 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 31.24 | 105.0 | 15.70 | 0.00 | -447.87 | 0.00 | 49.46 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 31.24 | 144.0 | 0.00 | 0.00 | -600.27 | 0.00 | 50.14 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 43.65 | 131.5 | 15.70 | 0.00 | -426.91 | 0.00 | 50.03 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | FROZEN_STRICT | 1 | 9.87 | 138.5 | 0.00 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | FROZEN_STRICT | 2 | 15.70 | 59.0 | 13.60 | 5.23 | ONBEKEND | 62.18 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_BARS | 1 | 11.96 | 135.5 | 1.94 | 0.00 | -596.91 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_BARS | 2 | 18.24 | 62.0 | 15.70 | 7.32 | -317.52 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE | 1 | 11.66 | 135.0 | 1.94 | 0.00 | -595.89 | 0.00 | 42.99 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE | 2 | 17.79 | 61.0 | 15.70 | 7.32 | -309.51 | 0.00 | 39.59 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 15.55 | 119.5 | 4.33 | 0.00 | -566.72 | 0.00 | 42.18 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 19.43 | 75.5 | 15.40 | 0.00 | -411.61 | 0.00 | 41.32 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 17.49 | 106.0 | 7.32 | 0.00 | -543.25 | 0.00 | 41.76 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 19.58 | 67.0 | 15.40 | 0.00 | -406.18 | 0.00 | 41.60 |
| TOPSTEP_CONSISTENCY | S2-Judas | FROZEN_STRICT | 1 | 0.00 | — | 0.00 | 0.00 | ONBEKEND | 100.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S2-Judas | FROZEN_STRICT | 2 | 1.05 | 8.0 | 0.00 | 0.00 | ONBEKEND | 84.45 | 0.00 |
| TOPSTEP_CONSISTENCY | S2-Judas | OBSERVED_BARS | 1 | 20.48 | 58.0 | 16.74 | 14.20 | -371.29 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S2-Judas | OBSERVED_BARS | 2 | 45.89 | 96.0 | 18.54 | 3.59 | -123.70 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S2-Judas | OBSERVED_KEEPALIVE | 1 | 20.33 | 58.0 | 16.74 | 10.76 | -402.34 | 0.00 | 14.66 |
| TOPSTEP_CONSISTENCY | S2-Judas | OBSERVED_KEEPALIVE | 2 | 45.29 | 96.0 | 18.68 | 3.59 | -120.83 | 0.00 | 7.51 |
| MFFU_BUILDER | S1-Judas-Bull0930 | FROZEN_STRICT | 1 | 0.00 | — | 0.00 | 0.00 | ONBEKEND | 8.07 | 0.00 |
| MFFU_BUILDER | S1-Judas-Bull0930 | FROZEN_STRICT | 2 | 0.00 | — | 0.00 | 0.00 | ONBEKEND | 8.07 | 0.00 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_BARS | 1 | 0.00 | — | 0.00 | 0.00 | -153.00 | 0.00 | 0.00 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_BARS | 2 | 0.00 | — | 0.00 | 0.00 | -153.00 | 0.00 | 0.00 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE | 1 | 18.83 | 146.5 | 0.00 | 0.00 | -153.00 | 0.00 | 50.32 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE | 2 | 22.27 | 64.0 | 15.40 | 0.00 | -69.99 | 0.00 | 47.53 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 18.83 | 130.5 | 0.00 | 0.00 | -153.00 | 0.00 | 50.32 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 32.59 | 113.5 | 0.00 | 0.00 | -153.00 | 0.00 | 50.17 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 26.91 | 139.5 | 0.00 | 0.00 | -153.00 | 0.00 | 50.17 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 39.91 | 136.0 | 10.01 | 0.00 | -81.51 | 0.00 | 48.89 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250_KA650 | 1 | 18.24 | 128.5 | 0.00 | 0.00 | -153.00 | 0.00 | 50.32 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250_KA650 | 2 | 30.94 | 108.0 | 0.00 | 0.00 | -153.00 | 0.00 | 50.16 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300_KA650 | 1 | 25.26 | 134.0 | 0.00 | 0.00 | -153.00 | 0.00 | 50.13 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300_KA650 | 2 | 37.22 | 120.0 | 8.52 | 0.00 | -94.42 | 0.00 | 48.68 |
| MFFU_BUILDER | S1-Judas-0830 | FROZEN_STRICT | 1 | 0.00 | — | 0.00 | 0.00 | ONBEKEND | 8.22 | 0.00 |
| MFFU_BUILDER | S1-Judas-0830 | FROZEN_STRICT | 2 | 0.00 | — | 0.00 | 0.00 | ONBEKEND | 8.22 | 0.00 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_BARS | 1 | 0.00 | — | 0.00 | 0.00 | -153.00 | 0.00 | 0.00 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_BARS | 2 | 0.00 | — | 0.00 | 0.00 | -153.00 | 0.00 | 0.00 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE | 1 | 10.01 | 132.0 | 0.00 | 0.00 | -153.00 | 0.00 | 42.91 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE | 2 | 17.79 | 62.0 | 10.01 | 1.94 | -61.34 | 0.00 | 40.42 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 13.45 | 120.5 | 0.00 | 0.00 | -153.00 | 0.00 | 42.42 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 17.79 | 73.0 | 7.32 | 0.00 | -110.86 | 0.00 | 41.25 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 15.70 | 104.0 | 0.00 | 0.00 | -153.00 | 0.00 | 42.14 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 17.79 | 72.0 | 7.32 | 0.00 | -114.31 | 0.00 | 41.52 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250_KA650 | 1 | 10.01 | 132.0 | 0.00 | 0.00 | -153.00 | 0.00 | 42.91 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250_KA650 | 2 | 17.79 | 73.0 | 7.32 | 0.00 | -111.92 | 0.00 | 41.06 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300_KA650 | 1 | 14.95 | 107.5 | 0.00 | 0.00 | -153.00 | 0.00 | 42.21 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300_KA650 | 2 | 17.79 | 73.0 | 7.32 | 0.00 | -113.17 | 0.00 | 41.12 |
| MFFU_BUILDER | S2-Judas | FROZEN_STRICT | 1 | 0.00 | — | 0.00 | 0.00 | ONBEKEND | 62.18 | 0.00 |
| MFFU_BUILDER | S2-Judas | FROZEN_STRICT | 2 | 1.35 | 7.0 | 0.00 | 0.00 | ONBEKEND | 57.10 | 0.00 |
| MFFU_BUILDER | S2-Judas | OBSERVED_BARS | 1 | 7.03 | 40.0 | 0.00 | 0.00 | -153.00 | 0.00 | 0.00 |
| MFFU_BUILDER | S2-Judas | OBSERVED_BARS | 2 | 8.22 | 14.0 | 3.89 | 1.79 | -112.07 | 0.00 | 0.00 |
| MFFU_BUILDER | S2-Judas | OBSERVED_KEEPALIVE | 1 | 19.13 | 62.0 | 14.50 | 9.12 | -14.14 | 0.00 | 14.94 |
| MFFU_BUILDER | S2-Judas | OBSERVED_KEEPALIVE | 2 | 43.95 | 69.5 | 8.52 | 5.08 | -39.92 | 0.00 | 6.46 |

## Hybride profielen — beide historische perioden afzonderlijk

De minimum-1-clamp kan een $250/$300-budget overschrijden. Ook de $3,22 in de
size-formule kan de werkelijke gebruikte $6,50 Builder-kosten onderschatten.
Tellingen hieronder zijn account-executies over overlappende starts, geen unieke
trades. Grootste stoprisico is een nominale stopafstand+frictie, geen garantie bij gaps.

| Firm | Model | Profiel | ON | Periode | Pass % | Payout1 % | Payout2 % | Netto $/start | Budgetoverschrijdingen | Grootste nominaal Judas-stoprisico $ |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 252 | 382.22 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 2024_2026 | 80.70 | 20.47 | 0.00 | -457.20 | 290 | 373.22 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 2019_2021 | 11.04 | 0.00 | 0.00 | -635.84 | 252 | 382.22 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 2024_2026 | 90.06 | 78.36 | 1.17 | 505.78 | 221 | 373.22 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 2019_2021 | 14.26 | 0.00 | 0.00 | -631.48 | 252 | 382.22 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 2024_2026 | 80.70 | 27.49 | 0.00 | -394.57 | 182 | 373.22 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 2019_2021 | 27.71 | 9.04 | 0.00 | -589.04 | 252 | 382.22 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 2024_2026 | 90.06 | 78.36 | 11.11 | 588.36 | 155 | 373.22 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 10 | 301.72 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 2024_2026 | 60.82 | 0.00 | 0.00 | -436.20 | 409 | 672.22 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 10 | 301.72 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 2024_2026 | 76.02 | 28.65 | 0.00 | -52.34 | 323 | 677.72 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 10 | 301.72 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 2024_2026 | 68.42 | 7.60 | 0.00 | -361.92 | 405 | 672.22 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 2019_2021 | 0.20 | 0.00 | 0.00 | -637.10 | 10 | 301.72 |
| TOPSTEP_STANDARD | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 2024_2026 | 76.02 | 39.18 | 0.00 | 88.58 | 353 | 677.72 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 252 | 382.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 2024_2026 | 80.70 | 0.00 | 0.00 | -533.16 | 290 | 373.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 2019_2021 | 11.04 | 0.00 | 0.00 | -635.84 | 252 | 382.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 2024_2026 | 90.06 | 61.40 | 0.00 | 99.55 | 198 | 373.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 2019_2021 | 14.26 | 0.00 | 0.00 | -631.48 | 252 | 382.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 2024_2026 | 80.70 | 0.00 | 0.00 | -509.38 | 182 | 373.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 2019_2021 | 27.71 | 0.00 | 0.00 | -624.17 | 252 | 382.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 2024_2026 | 90.06 | 61.40 | 0.00 | 147.58 | 166 | 373.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 10 | 301.72 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 2024_2026 | 60.82 | 16.96 | 0.00 | -362.05 | 393 | 672.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 10 | 301.72 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 2024_2026 | 76.02 | 60.23 | 0.00 | 244.77 | 282 | 677.72 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -637.00 | 10 | 301.72 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 2024_2026 | 68.42 | 28.65 | 0.00 | -270.21 | 370 | 672.22 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 2019_2021 | 0.20 | 0.00 | 0.00 | -637.10 | 10 | 301.72 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 2024_2026 | 76.02 | 60.23 | 0.00 | 266.33 | 317 | 677.72 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -153.00 | 751 | 385.50 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 1 | 2024_2026 | 73.68 | 0.00 | 0.00 | -153.00 | 290 | 376.50 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 2019_2021 | 9.44 | 0.00 | 0.00 | -153.00 | 751 | 385.50 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R250 | 2 | 2024_2026 | 100.00 | 0.00 | 0.00 | -153.00 | 290 | 376.50 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 2019_2021 | 10.84 | 0.00 | 0.00 | -153.00 | 1152 | 385.50 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 1 | 2024_2026 | 73.68 | 0.00 | 0.00 | -153.00 | 182 | 376.50 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 2019_2021 | 19.28 | 0.00 | 0.00 | -153.00 | 1056 | 385.50 |
| MFFU_BUILDER | S1-Judas-Bull0930 | OBSERVED_KEEPALIVE_R300 | 2 | 2024_2026 | 100.00 | 39.18 | 0.00 | 126.69 | 182 | 376.50 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -153.00 | 818 | 305.00 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 1 | 2024_2026 | 52.63 | 0.00 | 0.00 | -153.00 | 392 | 675.50 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 2019_2021 | 0.00 | 0.00 | 0.00 | -153.00 | 818 | 305.00 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R250 | 2 | 2024_2026 | 69.59 | 28.65 | 0.00 | 11.85 | 235 | 540.00 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 2019_2021 | 0.00 | 0.00 | 0.00 | -153.00 | 1363 | 312.50 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 1 | 2024_2026 | 61.40 | 0.00 | 0.00 | -153.00 | 381 | 675.50 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 2019_2021 | 0.00 | 0.00 | 0.00 | -153.00 | 1363 | 312.50 |
| MFFU_BUILDER | S1-Judas-0830 | OBSERVED_KEEPALIVE_R300 | 2 | 2024_2026 | 69.59 | 28.65 | 0.00 | -1.62 | 270 | 540.00 |

## Controles en gebruik

De exacte oorspronkelijke accountvelden worden voor alle33.120oorspronkelijke
accountpaden van de drie officiële routes opnieuw vergeleken. Daarna twee nieuwe
deterministische replays met byte-identieke accountledgers en aggregaten. De private
bronnen, prijsrecords en accountledgers worden niet gepubliceerd. Regels en bronhashes
staan in research/prop-refinement-registration.json en het verificatiebewijs.

Nieuw dashboard: /research/prop-refinement; bevroren lifecycle: /research/prop-lifecycle.
Reproduceer: python -m scripts.prop_refinement register, paths, run, verify.
Alle selecties en profielen blijven ontwikkelingsonderzoek op reeds bekeken data.
Een hoger scenarioresultaat bewijst geen causaliteit van een edge of prop-goedkeuring.

## Officiële bronnen, geraadpleegd 26 oktober 2026

- [topstep_pricing](https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions)
- [topstep_subscription](https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions)
- [topstep_XFA](https://help.topstep.com/en/articles/8284215-express-funded-account-parameters)
- [topstep_payout](https://help.topstep.com/en/articles/8284233-topstep-payout-policy)
- [topstep_floor](https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit)
- [builder](https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide)
- [builder_one_time](https://myfundedfutures.com/)
- [builder_inactivity](https://help.myfundedfutures.com/en/articles/16596524-inactivity-rule-one-time-payment-model)
- [builder_payout_floor](https://help.myfundedfutures.com/en/articles/13745661-payout-policy-overview-best-and-fastest-prop-firm-payouts)
- [mffu_open_loss](https://help.myfundedfutures.com/en/articles/8348565-end-of-day-eod-drawdown-explained)
- [mffu_fair_play](https://help.myfundedfutures.com/en/articles/8444599-fair-play-and-prohibited-trading-practices)
- [topstep_scaling](https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan)
- [topstep_news](https://help.topstep.com/en/articles/13613539-risk-adjustments-high-risk-high-volatility)
