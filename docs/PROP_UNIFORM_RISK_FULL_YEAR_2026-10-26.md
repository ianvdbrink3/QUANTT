# Uniform dollar-risico en doorlopende payouts — 26 oktober 2026

Status: ONTWIKKELINGSCONTROLE, GEEN ONAFHANKELIJK GEVALIDEERD PROP-MODEL.

Alle669starts met252cashsessies:498oud (2019–2021),171recent (feitelijkvanafjanuari2025).
Drie vaste budgets $300/$350/$400 en één vooraf gekozen plafond van6MNQ voor beide
pijlers. S1 behoudt de .50ATR-stop; S2 krijgt afzonderlijk de bestaande .50/.75ATR
stopvarianten. De gewone regels/signalen blijven intact. Max8 is niet extra gezocht.

## Risico en kasstromen

Aantalcontracten=max(0,min(6,floor(budget/(2*stopafstand+$3,22)))). Geen minimum1.
Als de formule0oplevert wordt geen order geplaatst, geen fee gerekend, geen timer
gereset en geen tijdslot gereserveerd. Ook bij actual-fees-risico>1,25budget wordt
overgeslagen. Topstepnormaal3,22/MNQ,Builder6,50/MNQ: de laatste kan iets bovenbudget
liggen doordat de gevraagde size-formule3,22gebruikt, maar nooit boven1,25budget.
Dit begrenst nominaal stoprisico; gaps kunnen een stop-fill verslechteren.

De bestaande synthetische keep-alive blijft: nul bruto,3,22kosten,flatopcash-noon,
zesNYkalenderdagen met vervroeging voor weekend/feestdag. Geen bewezen één-seconde
fill of expliciete firmacceptatie. Geobserveerde bars bewijzen geen stille ontbrekende
minuten. Huidige2026accountregels worden retrospectief toegepast op NQalsMNQproxy.

Vanafdezelfdeaccountpath worden zowel de eerste2payouts als alle latere payouts
geteld. Na payout2 blijven alle saldo-/vloer-/consistentie-/fee-regels gelden.
Netto=ontvangen aandeel na winstdeling minus aankoop,abonnementen en activatie.
Geen onopgenomen equity als inkomen,geen retries,geen belasting/FX/API/transferkosten.
TweeMNQbetekent$4perpunt: $3.000targetvraagt750puntenvóórkosten, niet1.500punten.

## Volledig jaar versus eerste twee payouts

Elke rij is gemiddeld per ALLE gestarte accounts, inclusief niet-geslaagde starts.
Payoutaantallen en mediane passtijd zijn geen onafhankelijke replicaties. De oude
controle stopt niet meer bij2, zodat het effect van de eerdere truncatie apart staat.

| Firm | Model | Budget/profiel | Periode | Starts | Pass % | Mediane dagen tot pass | Netto $ eerste2 | Netto $ jaar | Extra cash na2 | Gem. payouts | Max. payouts | Live-overgang onbekend |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_300 | 2019_2021 | 498 | 17.87 | 166.0 | -564.70 | -564.70 | 0.00 | 0.07 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_300 | 2024_2026 | 171 | 61.40 | 102.0 | -501.83 | -501.83 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_300 | COMBINED | 669 | 29.00 | 132.0 | -548.63 | -548.63 | 0.00 | 0.05 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_350 | 2019_2021 | 498 | 17.87 | 166.0 | -558.76 | -558.76 | 0.00 | 0.05 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_350 | 2024_2026 | 171 | 68.42 | 91.0 | -470.45 | -470.45 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_350 | COMBINED | 669 | 30.79 | 129.0 | -536.19 | -536.19 | 0.00 | 0.04 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_400 | 2019_2021 | 498 | 36.35 | 148.0 | -461.27 | -461.27 | 0.00 | 0.16 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_400 | 2024_2026 | 171 | 68.42 | 91.0 | -453.60 | -453.60 | 0.00 | 0.09 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | UNIFORM_400 | COMBINED | 669 | 44.54 | 109.0 | -459.31 | -459.31 | 0.00 | 0.14 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_300 | 2019_2021 | 498 | 0.20 | 64.0 | -636.41 | -636.41 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_300 | 2024_2026 | 171 | 60.23 | 122.0 | -530.18 | -530.18 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_300 | COMBINED | 669 | 15.55 | 121.5 | -609.26 | -609.26 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_350 | 2019_2021 | 498 | 3.61 | 80.5 | -545.27 | -545.27 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_350 | 2024_2026 | 171 | 61.40 | 118.0 | -413.29 | -413.29 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_350 | COMBINED | 669 | 18.39 | 109.0 | -511.54 | -511.54 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_400 | 2019_2021 | 498 | 17.47 | 73.0 | -424.52 | -424.52 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_400 | 2024_2026 | 171 | 61.40 | 102.0 | -333.33 | -333.33 | 0.00 | 0.08 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | UNIFORM_400 | COMBINED | 669 | 28.70 | 92.0 | -401.21 | -401.21 | 0.00 | 0.02 | 1 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_300 | 2019_2021 | 498 | 51.61 | 128.0 | -439.94 | -439.94 | 0.00 | 0.30 | 2 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_300 | 2024_2026 | 171 | 69.59 | 58.0 | 278.87 | 637.57 | 358.70 | 1.81 | 4 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_300 | COMBINED | 669 | 56.20 | 97.0 | -256.21 | -164.52 | 91.69 | 0.68 | 4 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_350 | 2019_2021 | 498 | 54.42 | 97.0 | -367.27 | -367.27 | 0.00 | 0.32 | 2 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_350 | 2024_2026 | 171 | 69.59 | 55.0 | 510.62 | 1067.75 | 557.13 | 1.91 | 4 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_350 | COMBINED | 669 | 58.30 | 82.0 | -142.88 | -0.47 | 142.41 | 0.72 | 4 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_400 | 2019_2021 | 498 | 48.80 | 64.0 | -160.88 | -159.23 | 1.65 | 0.51 | 3 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_400 | 2024_2026 | 171 | 69.59 | 59.0 | 484.14 | 1073.30 | 589.16 | 1.96 | 4 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP050 | UNIFORM_400 | COMBINED | 669 | 54.11 | 62.0 | 3.99 | 155.81 | 151.82 | 0.88 | 4 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_300 | 2019_2021 | 498 | 31.93 | 178.0 | -536.68 | -536.68 | 0.00 | 0.10 | 2 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_300 | 2024_2026 | 171 | 0.00 | — | -637.00 | -637.00 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_300 | COMBINED | 669 | 23.77 | 178.0 | -562.32 | -562.32 | 0.00 | 0.07 | 2 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_350 | 2019_2021 | 498 | 37.55 | 108.0 | -382.26 | -382.26 | 0.00 | 0.23 | 2 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_350 | 2024_2026 | 171 | 0.00 | — | -561.06 | -561.06 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_350 | COMBINED | 669 | 27.95 | 108.0 | -427.96 | -427.96 | 0.00 | 0.17 | 2 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_400 | 2019_2021 | 498 | 53.82 | 96.0 | -156.38 | -113.76 | 42.62 | 0.75 | 3 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_400 | 2024_2026 | 171 | 68.42 | 86.0 | -289.25 | -289.25 | 0.00 | 0.29 | 1 | 0 |
| TOPSTEP_STANDARD | S2-Judas-STOP075 | UNIFORM_400 | COMBINED | 669 | 57.55 | 91.0 | -190.34 | -158.62 | 31.73 | 0.63 | 3 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 27.71 | 171.5 | -589.04 | -589.04 | 0.00 | 0.09 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 90.06 | 65.0 | 588.36 | 588.36 | 0.00 | 0.89 | 2 | 0 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 43.65 | 131.5 | -288.09 | -288.09 | 0.00 | 0.30 | 2 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 0.20 | 206.0 | -637.10 | -637.10 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 76.02 | 67.0 | 88.58 | 88.58 | 0.00 | 0.39 | 1 | 0 |
| TOPSTEP_STANDARD | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 19.58 | 67.0 | -451.61 | -451.61 | 0.00 | 0.10 | 1 | 0 |
| TOPSTEP_STANDARD | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 41.16 | 138.0 | -231.21 | -231.21 | 0.00 | 0.38 | 2 | 0 |
| TOPSTEP_STANDARD | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 57.31 | 29.5 | 354.35 | 802.27 | 447.93 | 1.09 | 7 | 0 |
| TOPSTEP_STANDARD | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 45.29 | 96.0 | -81.54 | 32.96 | 114.49 | 0.56 | 7 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_300 | 2019_2021 | 498 | 17.87 | 166.0 | -587.37 | -587.37 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_300 | 2024_2026 | 171 | 61.40 | 102.0 | -501.83 | -501.83 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_300 | COMBINED | 669 | 29.00 | 132.0 | -565.51 | -565.51 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_350 | 2019_2021 | 498 | 17.87 | 166.0 | -576.26 | -576.26 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_350 | 2024_2026 | 171 | 68.42 | 91.0 | -228.26 | -228.26 | 0.00 | 0.60 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_350 | COMBINED | 669 | 30.79 | 129.0 | -487.31 | -487.31 | 0.00 | 0.15 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_400 | 2019_2021 | 498 | 36.35 | 148.0 | -541.20 | -541.20 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_400 | 2024_2026 | 171 | 68.42 | 91.0 | -228.26 | -228.26 | 0.00 | 0.60 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | UNIFORM_400 | COMBINED | 669 | 44.54 | 109.0 | -461.21 | -461.21 | 0.00 | 0.15 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_300 | 2019_2021 | 498 | 0.20 | 64.0 | -636.41 | -636.41 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_300 | 2024_2026 | 171 | 60.23 | 122.0 | -530.18 | -530.18 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_300 | COMBINED | 669 | 15.55 | 121.5 | -609.26 | -609.26 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_350 | 2019_2021 | 498 | 3.61 | 80.5 | -545.27 | -545.27 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_350 | 2024_2026 | 171 | 61.40 | 118.0 | -413.29 | -413.29 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_350 | COMBINED | 669 | 18.39 | 109.0 | -511.54 | -511.54 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_400 | 2019_2021 | 498 | 17.47 | 73.0 | -424.52 | -424.52 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_400 | 2024_2026 | 171 | 61.40 | 102.0 | -245.21 | -245.21 | 0.00 | 0.29 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | UNIFORM_400 | COMBINED | 669 | 28.70 | 92.0 | -378.69 | -378.69 | 0.00 | 0.07 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_300 | 2019_2021 | 498 | 51.61 | 128.0 | -462.99 | -462.99 | 0.00 | 0.14 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_300 | 2024_2026 | 171 | 69.59 | 58.0 | 347.34 | 834.18 | 486.84 | 1.78 | 3 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_300 | COMBINED | 669 | 56.20 | 97.0 | -255.86 | -131.43 | 124.44 | 0.56 | 3 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_350 | 2019_2021 | 498 | 54.42 | 97.0 | -370.55 | -370.55 | 0.00 | 0.18 | 2 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_350 | 2024_2026 | 171 | 69.59 | 55.0 | 675.33 | 1179.56 | 504.23 | 1.80 | 3 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_350 | COMBINED | 669 | 58.30 | 82.0 | -103.22 | 25.66 | 128.88 | 0.60 | 3 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_400 | 2019_2021 | 498 | 48.80 | 64.0 | -241.78 | -241.78 | 0.00 | 0.20 | 2 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_400 | 2024_2026 | 171 | 69.59 | 59.0 | 653.11 | 943.29 | 290.18 | 1.50 | 3 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP050 | UNIFORM_400 | COMBINED | 669 | 54.11 | 62.0 | -13.04 | 61.13 | 74.17 | 0.53 | 3 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_300 | 2019_2021 | 498 | 31.93 | 178.0 | -544.54 | -544.54 | 0.00 | 0.03 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_300 | 2024_2026 | 171 | 0.00 | — | -637.00 | -637.00 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_300 | COMBINED | 669 | 23.77 | 178.0 | -568.18 | -568.18 | 0.00 | 0.02 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_350 | 2019_2021 | 498 | 37.55 | 108.0 | -425.52 | -425.52 | 0.00 | 0.06 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_350 | 2024_2026 | 171 | 0.00 | — | -561.06 | -561.06 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_350 | COMBINED | 669 | 27.95 | 108.0 | -460.17 | -460.17 | 0.00 | 0.04 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_400 | 2019_2021 | 498 | 53.82 | 96.0 | -203.39 | -203.39 | 0.00 | 0.31 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_400 | 2024_2026 | 171 | 68.42 | 86.0 | -40.03 | -40.03 | 0.00 | 0.69 | 2 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas-STOP075 | UNIFORM_400 | COMBINED | 669 | 57.55 | 91.0 | -161.64 | -161.64 | 0.00 | 0.41 | 2 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 27.71 | 171.5 | -624.17 | -624.17 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 90.06 | 65.0 | 147.58 | 147.58 | 0.00 | 0.61 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 43.65 | 131.5 | -426.91 | -426.91 | 0.00 | 0.16 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 0.20 | 206.0 | -637.10 | -637.10 | 0.00 | 0.00 | 0 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 76.02 | 67.0 | 266.33 | 266.33 | 0.00 | 0.60 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 19.58 | 67.0 | -406.18 | -406.18 | 0.00 | 0.15 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 41.16 | 138.0 | -301.76 | -301.76 | 0.00 | 0.11 | 1 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 57.31 | 29.5 | 406.10 | 727.03 | 320.93 | 0.73 | 5 | 0 |
| TOPSTEP_CONSISTENCY | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 45.29 | 96.0 | -120.83 | -38.79 | 82.03 | 0.27 | 5 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_300 | 2019_2021 | 498 | 12.45 | 155.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_300 | 2024_2026 | 171 | 61.40 | 102.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_300 | COMBINED | 669 | 24.96 | 133.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 12.45 | 155.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 61.40 | 102.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 24.96 | 133.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_350 | 2019_2021 | 498 | 10.84 | 151.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_350 | 2024_2026 | 171 | 67.84 | 91.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_350 | COMBINED | 669 | 25.41 | 118.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 10.84 | 151.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 67.84 | 91.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 25.41 | 118.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_400 | 2019_2021 | 498 | 32.73 | 158.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_400 | 2024_2026 | 171 | 67.84 | 91.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_400 | COMBINED | 669 | 41.70 | 126.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 32.73 | 158.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 67.84 | 91.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 41.70 | 126.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_300 | 2019_2021 | 498 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_300 | 2024_2026 | 171 | 60.23 | 122.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_300 | COMBINED | 669 | 15.40 | 122.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 60.23 | 122.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 15.40 | 122.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_350 | 2019_2021 | 498 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_350 | 2024_2026 | 171 | 61.40 | 118.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_350 | COMBINED | 669 | 15.70 | 118.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 61.40 | 118.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 15.70 | 118.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_400 | 2019_2021 | 498 | 12.25 | 68.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_400 | 2024_2026 | 171 | 61.40 | 105.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_400 | COMBINED | 669 | 24.81 | 93.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 12.25 | 68.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 61.40 | 105.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 24.81 | 93.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_300 | 2019_2021 | 498 | 22.69 | 168.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_300 | 2024_2026 | 171 | 69.59 | 60.0 | 113.20 | 113.20 | 0.00 | 0.59 | 1 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_300 | COMBINED | 669 | 34.68 | 97.0 | -84.96 | -84.96 | 0.00 | 0.15 | 1 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 22.69 | 168.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 69.59 | 60.0 | 113.20 | 113.20 | 0.00 | 0.59 | 1 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 34.68 | 97.0 | -84.96 | -84.96 | 0.00 | 0.15 | 1 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_350 | 2019_2021 | 498 | 22.49 | 98.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_350 | 2024_2026 | 171 | 69.59 | 57.0 | 322.75 | 322.75 | 0.00 | 0.78 | 2 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_350 | COMBINED | 669 | 34.53 | 84.0 | -31.40 | -31.40 | 0.00 | 0.20 | 2 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 22.49 | 98.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 69.59 | 57.0 | 322.75 | 322.75 | 0.00 | 0.78 | 2 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 34.53 | 84.0 | -31.40 | -31.40 | 0.00 | 0.20 | 2 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_400 | 2019_2021 | 498 | 43.17 | 72.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_400 | 2024_2026 | 171 | 69.59 | 60.0 | 397.69 | 419.50 | 21.81 | 0.98 | 3 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_400 | COMBINED | 669 | 49.93 | 69.0 | -12.24 | -6.67 | 5.57 | 0.25 | 3 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 43.17 | 72.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 69.59 | 60.0 | 397.69 | 419.50 | 21.81 | 0.98 | 3 | 0 |
| MFFU_BUILDER | S2-Judas-STOP050 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 49.93 | 69.0 | -12.24 | -6.67 | 5.57 | 0.25 | 3 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_300 | 2019_2021 | 498 | 9.64 | 237.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_300 | 2024_2026 | 171 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_300 | COMBINED | 669 | 7.17 | 237.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 9.64 | 237.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_300_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 7.17 | 237.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_350 | 2019_2021 | 498 | 21.69 | 194.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_350 | 2024_2026 | 171 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_350 | COMBINED | 669 | 16.14 | 194.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 21.69 | 194.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_350_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 16.14 | 194.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_400 | 2019_2021 | 498 | 37.35 | 98.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_400 | 2024_2026 | 171 | 68.42 | 88.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_400 | COMBINED | 669 | 45.29 | 94.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2019_2021 | 498 | 37.35 | 98.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | 2024_2026 | 171 | 68.42 | 88.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas-STOP075 | UNIFORM_400_CONTINUED_SIM_COUNTERFACTUAL | COMBINED | 669 | 45.29 | 94.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 19.28 | 177.0 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 100.00 | 76.0 | 126.69 | 126.69 | 0.00 | 0.39 | 1 | 0 |
| MFFU_BUILDER | S1-Judas-Bull0930 | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 39.91 | 136.0 | -81.51 | -81.51 | 0.00 | 0.10 | 1 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 0.00 | — | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 69.59 | 72.0 | -1.62 | -1.62 | 0.00 | 0.29 | 1 | 0 |
| MFFU_BUILDER | S1-Judas-0830 | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 17.79 | 72.0 | -114.31 | -114.31 | 0.00 | 0.07 | 1 | 0 |
| MFFU_BUILDER | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2019_2021 | 498 | 30.92 | 180.5 | -153.00 | -153.00 | 0.00 | 0.00 | 0 | 0 |
| MFFU_BUILDER | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | 2024_2026 | 171 | 81.87 | 32.5 | 289.39 | ONBEKEND | 432.53 | 0.86 | 5 | 12 |
| MFFU_BUILDER | S2-Judas | LEGACY_SIZING_CONTINUE_AFTER_TWO | COMBINED | 669 | 43.95 | 69.5 | -39.92 | ONBEKEND | 110.56 | 0.22 | 5 | 12 |

## Grenzen aan de jaarprojectie

Topstep kan een XFA op discretionaire beoordeling naar Live overzetten; er is geen
vast payoutaantal. De jaarprojectie veronderstelt daarom dat XFAregels blijven
gelden; dit is geen voorspelling van een echte Live-callup of daaropvolgende cash.

Builder staat maximaal5Sim-payouts toe, daarna gelden andereLive-regels. De
hoofdvariant stopt die bekende Sim-fase na5 en markeert de ontbrekende verdere
levenscyclus. Jaar-netto staat danONBEKEND; reeds ontvangen cash wordt behouden.
CONTINUED_SIM_COUNTERFACTUAL toont daarnaast de volledige252dagen alsof dezelfde
Simregels mochten doorlopen. Dit kwantificeert6+payouts, maar is geen koopbaar
account of geverifieerdeLive-simulatie. GeenLive-startkapitaal of transferbedrag
verzonnen. Alle vorige rapporten blijven byte-identiek naast deze uitbreiding.

Nominale risico's,0-size-skips,payoutkansen en staten staan volledig in deCSV/JSON.
Reproduceren: python -m scripts.prop_uniform register,paths,run,verify. Eerst6021
bestaandeaccountpaths exact gereproduceerd, daarna dubbele byte-identiekeaccountreplay.
Private bronnen/prijsrecords/accountledgers blijvenGitignored. Dezelfde669starts
zijn hergebruikte ontwikkelingsdata,geen onafhankelijke validatie of causaliteitsbewijs.

## Officiële bronnen

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
- [topstep_callup](https://help.topstep.com/en/articles/13747178-live-funded-account-call-up-and-call-down-process)
- [topstep_live](https://help.topstep.com/en/articles/10657969-live-funded-account-parameters)
- [builder_live](https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide)
