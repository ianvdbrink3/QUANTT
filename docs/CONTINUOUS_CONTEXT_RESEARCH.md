# Continuous indicator research — vNext

**EXPLORATORY_NOT_NEW_HOLDOUT**. Baseline v0.9 blijft ongewijzigd. Periode 30 december 2024–30 september 2025; niet tien volledige maanden.

## Methode

Point-in-time additieve Panama-aanpassing. Intern raw minus de cumulatieve reeds bekende spread; historische PDH/PDL worden naar de huidige contractbasis vertaald. ATR gebruikt 14 eerder afgesloten geldige RTH true ranges. Intraday OHLCV, VWAP, signalen en fills blijven op het actieve ruwe contract. De vaste strategiecode en $24,50 RT blijven gelijk. Een nieuwe ATR verandert wel stops/targets op bestaande dagen: dit is niet uitsluitend het toevoegen van verloren trades.

| Roll | Laatste gezamenlijke RTH-closebar UTC | Spread (nieuw−oud) |
|---|---|---:|
| 2025-03-19 | 2025-03-18T19:59:00+00:00 | 205.25 |
| 2025-06-17 | 2025-06-16T19:59:00+00:00 | 227.50 |
| 2025-09-17 | 2025-09-16T19:59:00+00:00 | 238.25 |

De spread is pas bekend na voltooiing van de minuutbar. Dit zijn vendor-last-closes, geen officiële settlements. Geen latere rollspread herberekent een eerdere beslissing.

## Dekking ORB15

| Contract | Sessies | Baseline eligible | vNext eligible | Extra | ATR ontbreekt |
|---|---:|---:|---:|---:|---:|
| NQH25 | 56 | 33 | 33 | 0 | 19 |
| NQM25 | 63 | 48 | 56 | 8 | 0 |
| NQU25 | 66 | 42 | 53 | 11 | 0 |
| NQZ25 | 10 | 0 | 6 | 6 | 0 |

Alle rollover-ATR-gaten verdwijnen, maar niet alle eligibility-gaten: contracteigen same-clock volume-opwarming en complete vereiste minuten blijven verplicht. Ook de initiële H25-opwarming blijft bestaan.

## Vaste regels, nieuwe indicatorhistorie

| Strategie | Periode | Eligible | Trades | Netto pt | PF | Winrate |
|---|---|---:|---:|---:|---:|---:|
| A_London_sweep | Dec–sep | 159 | 82 | 175.550 | 1.051 | 42.7% |
| B_ORB5 | Dec–sep | 148 | 140 | -801.000 | 0.877 | 39.3% |
| B_ORB15 | Dec–sep | 148 | 137 | 535.175 | 1.098 | 44.5% |
| C_VWAP_extreme | Dec–sep | 159 | 63 | 95.825 | 1.057 | 54.0% |
| A_London_sweep | Apr–sep reeds bekeken | 106 | 58 | 248.450 | 1.134 | 44.8% |
| B_ORB5 | Apr–sep reeds bekeken | 98 | 94 | -581.900 | 0.850 | 38.3% |
| B_ORB15 | Apr–sep reeds bekeken | 98 | 92 | -619.200 | 0.821 | 40.2% |
| C_VWAP_extreme | Apr–sep reeds bekeken | 106 | 40 | 95.500 | 1.118 | 55.0% |

### Effect ontleed

| Strategie | Extra dagen | Extra-dag trades | Extra-dag netto pt | Gemeenschappelijke dagen: vNext pt | Gemeenschappelijke dagen: baseline pt |
|---|---:|---:|---:|---:|---:|
| A_London_sweep | 36 | 20 | 314.250 | -138.700 | -138.700 |
| B_ORB5 | 25 | 24 | -216.400 | -584.600 | -584.850 |
| B_ORB15 | 25 | 24 | 243.100 | 292.075 | 291.825 |
| C_VWAP_extreme | 36 | 13 | 180.575 | -84.750 | -84.750 |

## Featurebeschikbaarheid

- ticks: UNAVAILABLE: raw source contains OHLCV only; no trade count. All relative-ticks/intensity outputs null.
- opening_context: 09:30 open is known at 09:30; masked for earlier/equal-time entries.
- opening_volume: First 15 completed 1m bars known at 09:45. RVOL uses previous 14 active sessions only; masked for earlier trades.
- distance: Signed distance from completed signal close to current-basis PDH/PDL, not unknown next-open entry price.
- daily_export: Timestamped feature snapshots, NOT a claim every field was known before every trade.

RVOL is het openingsvolume gedeeld door het gemiddelde van de vorige 14 actieve sessies, niet het gemiddelde van achteraf geselecteerde geschikte dagen. Een incompleet historisch openingsvenster maakt deze RVOL tijdelijk onbekend. Voor London-trades vóór 09:30 zijn de volledige overnight-range en openingslocatie onbekend; voor elke entry vóór 09:45 is de volledige 15m-RVOL onbekend. Deze rijen worden niet met toekomstige waarden aangevuld. PDH/PDL na een onvolledige vorige RTH blijven onbekend.

## Beschrijvende feature-matrix

| Strategie | Feature | Groep | n | Gemiddeld netto pt | Mediane MFE pt |
|---|---|---|---:|---:|---:|
| A_London_sweep | opening_location | GAP_ABOVE_PDH | 18 | 41.053 | 73.625 |
| A_London_sweep | opening_location | GAP_BELOW_PDL | 6 | -55.975 | 35.500 |
| A_London_sweep | opening_location | INSIDE_PRIOR_RANGE | 41 | 6.080 | 79.000 |
| A_London_sweep | overnight_regime | COMPRESSED | 32 | 11.283 | 80.875 |
| A_London_sweep | overnight_regime | EXPANDED | 3 | 67.942 | 140.500 |
| A_London_sweep | overnight_regime | MIDDLE | 34 | 6.679 | 47.875 |
| A_London_sweep | opening_RVOL14 | continuous_complete_cases | 33 | -0.930 | 54.500 |
| A_London_sweep | overnight_range_ATR | continuous_complete_cases | 69 | 11.478 | 72.000 |
| B_ORB15 | opening_location | GAP_ABOVE_PDH | 34 | 4.238 | 57.750 |
| B_ORB15 | opening_location | GAP_BELOW_PDL | 21 | 21.061 | 110.500 |
| B_ORB15 | opening_location | INSIDE_PRIOR_RANGE | 78 | -0.347 | 49.500 |
| B_ORB15 | overnight_regime | COMPRESSED | 56 | 17.668 | 58.000 |
| B_ORB15 | overnight_regime | EXPANDED | 8 | 11.494 | 73.625 |
| B_ORB15 | overnight_regime | MIDDLE | 73 | -7.482 | 56.000 |
| B_ORB15 | opening_RVOL14 | continuous_complete_cases | 134 | 3.616 | 56.250 |
| B_ORB15 | overnight_range_ATR | continuous_complete_cases | 137 | 3.906 | 56.500 |
| B_ORB5 | opening_location | GAP_ABOVE_PDH | 34 | 1.393 | 72.625 |
| B_ORB5 | opening_location | GAP_BELOW_PDL | 21 | -24.392 | 75.000 |
| B_ORB5 | opening_location | INSIDE_PRIOR_RANGE | 81 | -4.188 | 58.750 |
| B_ORB5 | overnight_regime | COMPRESSED | 57 | -0.725 | 53.500 |
| B_ORB5 | overnight_regime | EXPANDED | 8 | -57.787 | 68.000 |
| B_ORB5 | overnight_regime | MIDDLE | 75 | -3.965 | 74.500 |
| B_ORB5 | opening_RVOL14 | continuous_complete_cases | 77 | -6.670 | 56.500 |
| B_ORB5 | overnight_range_ATR | continuous_complete_cases | 140 | -5.721 | 63.000 |
| C_VWAP_extreme | opening_location | GAP_ABOVE_PDH | 14 | -21.868 | 54.125 |
| C_VWAP_extreme | opening_location | GAP_BELOW_PDL | 8 | 36.181 | 90.875 |
| C_VWAP_extreme | opening_location | INSIDE_PRIOR_RANGE | 38 | -1.186 | 44.000 |
| C_VWAP_extreme | overnight_regime | COMPRESSED | 29 | 6.973 | 56.500 |
| C_VWAP_extreme | overnight_regime | EXPANDED | 2 | 140.650 | 312.250 |
| C_VWAP_extreme | overnight_regime | MIDDLE | 32 | -12.116 | 44.375 |
| C_VWAP_extreme | opening_RVOL14 | continuous_complete_cases | 62 | 1.618 | 50.125 |
| C_VWAP_extreme | overnight_range_ATR | continuous_complete_cases | 63 | 1.521 | 51.750 |

De groepsrijen kunnen door ontbrekende of nog onbekende features minder trades bevatten dan de strategietotalen. Geen optelling tussen verschillende features of strategieën.

## Correctie voor meervoudig toetsen

Exploratory centered circular 5-observed-session block bootstrap, 2000 draws, seed 20261021; missing/non-trade days retained in resampling. Global Holm over all 40 contrasts (4 strategies x 5 features/contrasts x 2 outcomes). Untestable p=1 retained. Approximate observational inference, not causal or independent validation.

No fitted cutoffs. Prior-location pairs; continuous RVOL and overnight/ATR Spearman. Overnight compressed<0.5 and expanded>1.2 are descriptive existing-regime groups only. MFE is the frozen minute-bar bound through exit, not tick-exact.

| Strategie | Feature / contrast | Uitkomst | n | Effect | Ruwe p | Globale Holm p |
|---|---|---|---:|---:|---:|---:|
| A_London_sweep | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | net_points | 59 | -34.9729 | 0.2499 | 1.0000 |
| A_London_sweep | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | mfe_bar_bound_points | 59 | -15.4143 | 0.4668 | 1.0000 |
| A_London_sweep | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | net_points | 47 | 62.0549 | 1.0000 | 1.0000 |
| A_London_sweep | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | mfe_bar_bound_points | 47 | 21.0996 | 1.0000 | 1.0000 |
| A_London_sweep | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | net_points | 24 | 97.0278 | 1.0000 | 1.0000 |
| A_London_sweep | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | mfe_bar_bound_points | 24 | 36.5139 | 1.0000 | 1.0000 |
| A_London_sweep | opening_RVOL14 | net_points | 33 | -0.1479 | 0.3613 | 1.0000 |
| A_London_sweep | opening_RVOL14 | mfe_bar_bound_points | 33 | -0.0587 | 0.7346 | 1.0000 |
| A_London_sweep | overnight_range_ATR | net_points | 69 | 0.0004 | 0.9970 | 1.0000 |
| A_London_sweep | overnight_range_ATR | mfe_bar_bound_points | 69 | -0.0055 | 0.9655 | 1.0000 |
| B_ORB15 | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | net_points | 112 | -4.5850 | 0.7876 | 1.0000 |
| B_ORB15 | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | mfe_bar_bound_points | 112 | 1.4555 | 0.8861 | 1.0000 |
| B_ORB15 | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | net_points | 99 | -21.4075 | 0.5022 | 1.0000 |
| B_ORB15 | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | mfe_bar_bound_points | 99 | -28.7903 | 0.1339 | 1.0000 |
| B_ORB15 | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | net_points | 55 | -16.8225 | 0.5887 | 1.0000 |
| B_ORB15 | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | mfe_bar_bound_points | 55 | -30.2458 | 0.1639 | 1.0000 |
| B_ORB15 | opening_RVOL14 | net_points | 134 | -0.0272 | 0.7791 | 1.0000 |
| B_ORB15 | opening_RVOL14 | mfe_bar_bound_points | 134 | 0.0014 | 0.9910 | 1.0000 |
| B_ORB15 | overnight_range_ATR | net_points | 137 | -0.1321 | 0.0780 | 1.0000 |
| B_ORB15 | overnight_range_ATR | mfe_bar_bound_points | 137 | 0.0410 | 0.6377 | 1.0000 |
| B_ORB5 | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | net_points | 115 | -5.5806 | 0.7531 | 1.0000 |
| B_ORB5 | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | mfe_bar_bound_points | 115 | -1.5255 | 0.8761 | 1.0000 |
| B_ORB5 | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | net_points | 102 | 20.2037 | 0.4793 | 1.0000 |
| B_ORB5 | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | mfe_bar_bound_points | 102 | -6.3739 | 0.6912 | 1.0000 |
| B_ORB5 | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | net_points | 55 | 25.7843 | 0.4008 | 1.0000 |
| B_ORB5 | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | mfe_bar_bound_points | 55 | -4.8484 | 0.7906 | 1.0000 |
| B_ORB5 | opening_RVOL14 | net_points | 77 | -0.2228 | 0.0390 | 1.0000 |
| B_ORB5 | opening_RVOL14 | mfe_bar_bound_points | 77 | -0.0790 | 0.4783 | 1.0000 |
| B_ORB5 | overnight_range_ATR | net_points | 140 | -0.0478 | 0.5842 | 1.0000 |
| B_ORB5 | overnight_range_ATR | mfe_bar_bound_points | 140 | 0.1981 | 0.0165 | 0.6597 |
| C_VWAP_extreme | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | net_points | 52 | 20.6823 | 0.2941 | 1.0000 |
| C_VWAP_extreme | opening_location INSIDE_PRIOR_RANGE minus GAP_ABOVE_PDH | mfe_bar_bound_points | 52 | -1.4962 | 0.8833 | 1.0000 |
| C_VWAP_extreme | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | net_points | 46 | -37.3668 | 1.0000 | 1.0000 |
| C_VWAP_extreme | opening_location INSIDE_PRIOR_RANGE minus GAP_BELOW_PDL | mfe_bar_bound_points | 46 | -72.9918 | 1.0000 | 1.0000 |
| C_VWAP_extreme | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | net_points | 22 | -58.0491 | 1.0000 | 1.0000 |
| C_VWAP_extreme | opening_location GAP_ABOVE_PDH minus GAP_BELOW_PDL | mfe_bar_bound_points | 22 | -71.4955 | 1.0000 | 1.0000 |
| C_VWAP_extreme | opening_RVOL14 | net_points | 62 | -0.0109 | 0.9310 | 1.0000 |
| C_VWAP_extreme | opening_RVOL14 | mfe_bar_bound_points | 62 | -0.1075 | 0.4583 | 1.0000 |
| C_VWAP_extreme | overnight_range_ATR | net_points | 63 | -0.0233 | 0.8676 | 1.0000 |
| C_VWAP_extreme | overnight_range_ATR | mfe_bar_bound_points | 63 | -0.0750 | 0.5727 | 1.0000 |

Niet-testbare kleine/constante groepen tellen mee met p=1. Ruwe CI’s in JSON zijn niet multipliciteitsgecorrigeerd. Observatieverbanden, geen causale verklaringen, geen nieuwe filters of parameteroptimalisatie. Er is geen onafhankelijke holdout meer voor deze variant.

## Beperkingen

- No real ticks, order book or trade-level VWAP.
- Panama changes ATR-based risk/targets even on existing eligible dates; this is not merely appending lost trades.
- Same-clock signal-volume histories still contract-native; quality/prefix gates unchanged. Zero ATR loss is not a guarantee all calendar days become trade eligible.
- Spreads use vendor 15:59 minute closes, not official settlement; identical-clock prices may be asynchronous last trades.
- Entire dataset already observed: all vNext comparisons exploratory; no promotion or strategy selection.
- Initial history and holiday/incomplete-session exclusions remain. Period is Dec30 plus Jan-Sep, not ten complete months.
