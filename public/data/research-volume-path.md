# vNext — volumecontinuïteit en post-entry paden

Periode: 30 december 2024–30 september 2025. Uitsluitend beschrijvend op reeds bekeken data. Baseline v0.9 én de eerdere continuous-export blijven ongewijzigd.

## Volumehistorie

Ongewijzigd: mediaan van maximaal 20 eerdere observaties van dezelfde NY-minuut, minimum 10; signaalvolume >1,5× referentie. Alleen de historie gebruikt nu de chronologische actieve contractstroom. Geen inactief volume toegevoegd, geen huidige/toekomstige sessie in de referentie. De aparte context-RVOL14 is niet de ORB-signaalfilter en is niet aangepast.

Alle vier strategieën hebben exact dezelfde 159 eligible datums. Dagen zonder trade blijven eligible. Overige kwaliteitsfilters, entry/exitregels, ATR, stops/targets en $24,50 roundtripkosten zijn gelijk aan de vorige continuous-variant.

## Uitkomsten bij gelijkgetrokken datums

| Strategie | Volumehistorie / datums | Dagen | Trades | Netto punten | PF | Winrate |
|---|---|---:|---:|---:|---:|---:|
| A_London_sweep | old_reference_common148 | 148 | 76 | -47.100 | 0.985 | 40.8% |
| A_London_sweep | active_reference_common148 | 148 | 76 | -47.100 | 0.985 | 40.8% |
| A_London_sweep | active_reference_full159 | 159 | 82 | 175.550 | 1.051 | 42.7% |
| A_London_sweep | active_reference_added11 | 11 | 6 | 222.650 | 2.043 | 66.7% |
| B_ORB5 | old_reference_common148 | 148 | 140 | -801.000 | 0.877 | 39.3% |
| B_ORB5 | active_reference_common148 | 148 | 138 | -457.300 | 0.925 | 39.9% |
| B_ORB5 | active_reference_full159 | 159 | 147 | -402.075 | 0.937 | 40.1% |
| B_ORB5 | active_reference_added11 | 11 | 9 | 55.225 | 1.187 | 44.4% |
| B_ORB15 | old_reference_common148 | 148 | 137 | 535.175 | 1.098 | 44.5% |
| B_ORB15 | active_reference_common148 | 148 | 135 | 995.875 | 1.199 | 46.7% |
| B_ORB15 | active_reference_full159 | 159 | 143 | 1083.575 | 1.210 | 46.9% |
| B_ORB15 | active_reference_added11 | 11 | 8 | 87.700 | 1.518 | 50.0% |
| C_VWAP_extreme | old_reference_common148 | 148 | 58 | -86.050 | 0.948 | 51.7% |
| C_VWAP_extreme | active_reference_common148 | 148 | 58 | -86.050 | 0.948 | 51.7% |
| C_VWAP_extreme | active_reference_full159 | 159 | 63 | 95.825 | 1.057 | 54.0% |
| C_VWAP_extreme | active_reference_added11 | 11 | 5 | 181.875 | 6.778 | 80.0% |

De eerste twee regels per strategie gebruiken dezelfde 148 dagen: verschil is uitsluitend de volumereferentie. De derde regel gebruikt alle 159 dagen; de vierde uitsluitend de 11 toegevoegde dagen. Dit is geen opgeteld portfolio.

## Grenzen van de meting

1R = absolute raw entry-to-initial-stop distance, before costs. Completed pre-exit bars plus the modeled exit price give a conservative lower excursion bound. Whole-exit-bar extremes give upper bounds, capped by the target for MFE and by the stop or known worse gapfill for MAE under the frozen execution model. At session-close exit the entire final bar is observed. Reached-R percentages are conservative intrabar identification intervals, not confidence intervals or exact tick-order percentages. Bounds include the execution endpoint. Timing of whole-bar extrema can include post-exit prices and is separate from completed-prefix timing. Model fills, not observed broker executions.

## Bereikt R-niveau en uiteindelijk netto resultaat

| Strategie | Niveau | Alle trades | Zeker bereikt | Mogelijk incl. zeker | Percentage [onder–boven] | Zekere hits: verlies / winst / vlak | Extra onzekere hits: verlies / winst / vlak |
|---|---:|---:|---:|---:|---:|---|---|
| A_London_sweep | +0.5R | 82 | 53 | 53 | 64.6–64.6% | 19 / 34 / 0 | 0 / 0 / 0 |
| A_London_sweep | +1.0R | 82 | 37 | 37 | 45.1–45.1% | 9 / 28 / 0 | 0 / 0 / 0 |
| A_London_sweep | +1.5R | 82 | 24 | 24 | 29.3–29.3% | 2 / 22 / 0 | 0 / 0 / 0 |
| B_ORB15 | +0.5R | 143 | 91 | 91 | 63.6–63.6% | 30 / 61 / 0 | 0 / 0 / 0 |
| B_ORB15 | +1.0R | 143 | 52 | 52 | 36.4–36.4% | 8 / 44 / 0 | 0 / 0 / 0 |
| B_ORB15 | +1.5R | 143 | 35 | 35 | 24.5–24.5% | 3 / 32 / 0 | 0 / 0 / 0 |
| B_ORB5 | +0.5R | 147 | 91 | 91 | 61.9–61.9% | 38 / 53 / 0 | 0 / 0 / 0 |
| B_ORB5 | +1.0R | 147 | 53 | 53 | 36.1–36.1% | 8 / 45 / 0 | 0 / 0 / 0 |
| B_ORB5 | +1.5R | 147 | 35 | 35 | 23.8–23.8% | 3 / 32 / 0 | 0 / 0 / 0 |
| C_VWAP_extreme | +0.5R | 63 | 38 | 38 | 60.3–60.3% | 7 / 31 / 0 | 0 / 0 / 0 |
| C_VWAP_extreme | +1.0R | 63 | 14 | 14 | 22.2–22.2% | 1 / 13 / 0 | 0 / 0 / 0 |
| C_VWAP_extreme | +1.5R | 63 | 4 | 4 | 6.3–6.3% | 0 / 4 / 0 | 0 / 0 / 0 |

Zeker en extra onzeker zijn disjunct; de netto-P&L-tekens zijn bekend. De bovengrenzen respecteren het gesimuleerde target en de stop (of bekende slechtere gapfill). Bij een sessie-exit op de laatste minuutclose is de volledige exitbar doorlopen en dus bekend. De JSON bevat daarnaast grenzen voor het conditionele verlies-/winstpercentage onder de trades die het niveau bereiken. De percentages zijn geen betrouwbaarheidsintervallen maar conservatieve intrabar-identificatiegrenzen.

## Tijd tot eerste minuutextreem

| Strategie | MFE mediaan [P25–P75] min | MAE mediaan [P25–P75] min | MFE in exitbar | MAE in exitbar |
|---|---|---|---:|---:|
| A_London_sweep | 24.00 [4.00–66.50] (n=82) | 15.50 [4.00–50.50] (n=82) | 17/82 | 40/82 |
| B_ORB15 | 21.00 [4.00–56.50] (n=143) | 20.00 [6.00–49.50] (n=143) | 21/143 | 54/143 |
| B_ORB5 | 19.00 [5.00–56.00] (n=147) | 19.00 [5.50–49.00] (n=147) | 26/147 | 68/147 |
| C_VWAP_extreme | 22.00 [4.00–57.50] (n=63) | 14.00 [3.00–33.50] (n=63) | 9/63 | 14/63 |

Tijd is het begin van de eerste minuutbar met het uiterste (eerste bij gelijke extremen). Bij nul positieve/negatieve excursie is het extremum al op entry bereikt: tijd 0, niet weggelaten. Minuut k betekent [k,k+1), niet een exact transactietijdstip. Deze volledige-bar-extremen kunnen in de exitminuut ná de fill vallen. Voor alleen volledig doorlopen minuten vóór de exitbar:

| Strategie | MFE prefix mediaan [P25–P75] min | MAE prefix mediaan [P25–P75] min |
|---|---|---|
| A_London_sweep | 24.00 [4.00–68.00] (n=81) | 12.50 [3.00–48.25] (n=80) |
| B_ORB15 | 20.50 [4.25–56.75] (n=142) | 20.00 [5.25–46.75] (n=142) |
| B_ORB5 | 18.00 [5.00–55.00] (n=146) | 15.00 [4.00–46.50] (n=147) |
| C_VWAP_extreme | 21.50 [4.50–54.75] (n=62) | 14.00 [2.50–32.50] (n=63) |

De prefix is niet de volledige trade: de exitminuut ontbreekt en trades zonder positieve/negatieve excursie in die prefix hebben geen extremumtijd. Exacte timing van de werkelijke trade-MFE/MAE is niet identificeerbaar uit deze bron.

## Netto resultaat per uitstapreden

| Strategie | Reden | Trades | Aandeel | Netto punten | Netto USD | Mediaan netto R [P25–P75] |
|---|---|---:|---:|---:|---:|---|
| A_London_sweep | target | 16 | 19.5% | 2184.150 | 43683.00 | 1.99 [1.98–1.99] (n=16) |
| A_London_sweep | stop | 40 | 48.8% | -3259.500 | -65190.00 | -1.02 [-1.02–-1.01] (n=40) |
| A_London_sweep | time_session | 26 | 31.7% | 1250.900 | 25018.00 | 0.49 [-0.00–1.07] (n=26) |
| B_ORB15 | target | 18 | 12.6% | 2764.450 | 55289.00 | 1.99 [1.99–1.99] (n=18) |
| B_ORB15 | stop | 53 | 37.1% | -4465.925 | -89318.50 | -1.02 [-1.02–-1.01] (n=53) |
| B_ORB15 | time_session | 72 | 50.3% | 2785.050 | 55701.00 | 0.38 [-0.06–0.86] (n=72) |
| B_ORB5 | target | 23 | 15.6% | 3279.825 | 65596.50 | 1.99 [1.99–1.99] (n=23) |
| B_ORB5 | stop | 67 | 45.6% | -5796.575 | -115931.50 | -1.02 [-1.02–-1.01] (n=67) |
| B_ORB5 | time_session | 57 | 38.8% | 2114.675 | 42293.50 | 0.25 [-0.16–0.86] (n=57) |
| C_VWAP_extreme | target | 7 | 11.1% | 481.925 | 9638.50 | 0.82 [0.61–0.97] (n=7) |
| C_VWAP_extreme | stop | 14 | 22.2% | -1072.900 | -21458.00 | -1.02 [-1.02–-1.01] (n=14) |
| C_VWAP_extreme | time_session | 42 | 66.7% | 686.800 | 13736.00 | 0.27 [-0.24–0.65] (n=42) |

Stop bevat stop_both: de ongewijzigde simulator neemt bij stop én target in dezelfde minuut de stop eerst. Netto R gebruikt kosten gedeeld door het initiële prijsrisico; 1R zelf is uitsluitend de afstand entry–initiële stop.

## Statistische toetsen

Geen inferentiële toetsen uitgevoerd. Alleen gemeten aantallen, percentages, kwantielen en intrabar-grenzen; daarom geen p-waarden of multipliciteitscorrectie nodig. Geen aanbevelingen, selectie van filters of parameterwijzigingen.

## Reproduceerbaarheid

Vanaf de 30 originele CSV-hashes: `.venv/bin/python -m scripts.reproduce_research.run_volume_path`. Private trades, eligibility en padgegevens blijven in `artifacts/volume-path-vnext/`. De JSON bevat bron-/codehashes en bewijs dat eerdere exports tijdens de run gelijk bleven.
