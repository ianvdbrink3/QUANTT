# Stabiliteitsaudit vNext — doorlopende volumehistorie

**Beschrijvend, retrospectief, geen nieuwe holdout.** Geen handelsregel of parameter aangepast. Baseline v0.9 en beide eerdere vNext-exports blijven ongewijzigd. Periode 30 december 2024–30 september 2025; geen tien volledige maanden.

## Analyseplan en herleidbaarheid

Definities en bronhashes zijn vastgelegd vóór deze nieuwe uitsplitsingen. De oorspronkelijke trades en geaggregeerde uitkomsten waren al bekeken: dit is dus geen prospectieve preregistratie. Eerder geverifieerde private tradebestanden worden op hash, totale P&L en kosten gereconcilieerd; strategieën hoeven niet opnieuw gesimuleerd te worden.

First 20 observed active civil-session dates starting at each fixed roll, including incomplete/holiday observed sessions. Last window truncated at dataset end. Check changed trades outside, do not assume references become identical.

| Rollstart | Laatste sessie venster | Geobserveerde sessies |
|---|---|---:|
| 2025-03-19 | 2025-04-15 | 20 |
| 2025-06-17 | 2025-07-14 | 20 |
| 2025-09-17 | 2025-09-30 | 10 |

## Periode-uitkomsten en onzekerheid

Vier strategieën × drie perioden + vier gepaarde common148-verbeteringen = één globale Holm-familie van 16 toetsen. Tweezijdige gecentreerde circular block-bootstrap: 2000 replicaties, bloklengte 5 eligible sessies, seed 20261020. Eligible dagen zonder trade tellen als nul. Kalendergaten zijn geen fictieve nul-handelsdagen. CI’s hieronder zijn nominale 95%-intervallen per toets, niet gelijktijdige intervallen.

| Strategie | Periode | Dagen | Trades | Netto pt | PF | Winrate | Gem. pt/eligible dag | 95% CI daggemiddelde | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| London Sweep | Dec–sep | 159 | 82 | 175.550 | 1.051 | 42.7% | 1.104 | [-11.440; 13.911] | 1.000 |
| London Sweep | Dec–17 apr | 53 | 24 | -72.900 | 0.953 | 37.5% | -1.375 | [-32.068; 27.504] | 1.000 |
| London Sweep | 18 apr–sep (reeds bekeken) | 106 | 58 | 248.450 | 1.134 | 44.8% | 2.344 | [-9.130; 14.558] | 1.000 |
| ORB 5m | Dec–sep | 159 | 147 | -402.075 | 0.937 | 40.1% | -2.529 | [-17.372; 12.153] | 1.000 |
| ORB 5m | Dec–17 apr | 53 | 46 | 234.900 | 1.100 | 41.3% | 4.432 | [-20.845; 31.948] | 1.000 |
| ORB 5m | 18 apr–sep (reeds bekeken) | 106 | 101 | -636.975 | 0.844 | 39.6% | -6.009 | [-22.569; 10.131] | 1.000 |
| ORB 15m | Dec–sep | 159 | 143 | 1083.575 | 1.210 | 46.9% | 6.815 | [-5.568; 20.124] | 1.000 |
| ORB 15m | Dec–17 apr | 53 | 45 | 1356.125 | 1.766 | 53.3% | 25.587 | [-1.319; 57.776] | 1.000 |
| ORB 15m | 18 apr–sep (reeds bekeken) | 106 | 98 | -272.550 | 0.920 | 43.9% | -2.571 | [-13.459; 7.159] | 1.000 |
| VWAP Extreme | Dec–sep | 159 | 63 | 95.825 | 1.057 | 54.0% | 0.603 | [-5.331; 6.678] | 1.000 |
| VWAP Extreme | Dec–17 apr | 53 | 23 | 0.325 | 1.000 | 52.2% | 0.006 | [-14.551; 13.984] | 1.000 |
| VWAP Extreme | 18 apr–sep (reeds bekeken) | 106 | 40 | 95.500 | 1.118 | 55.0% | 0.901 | [-4.320; 6.341] | 1.000 |

Percentiel-CI en gecentreerde tweezijdige bootstrap-p zijn bij een scheve verdeling niet exacte inversen van elkaar. De nominale CI is geen vervanging voor de globale Holm-toets. Alle conclusies blijven retrospectief.

## Tradeverschillen op dezelfde 148 dagen

Oud = ATR-continuous met contractgebonden volume; nieuw = dezelfde ATR met actieve doorlopende volumehistorie. Per dag maximaal één trade per strategie. Toegevoegd/verwijderd betreft hier een gewijzigde trade op een al eligible common148-dag. De categorie extra_dates betreft de 11 datums buiten common148; die waren voor London/VWAP al eligible, dus hun extra-datumresultaat is géén winst door een gewijzigde volumefilter.

| Strategie | Categorie | Dagen | Oude trades | Nieuwe trades | Oud netto pt | Nieuw netto pt | Verschil pt |
|---|---|---:|---:|---:|---:|---:|---:|
| London Sweep | extra_dates_no_trade | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| London Sweep | extra_dates_outside_common148 | 6 | 0 | 6 | 0.000 | 222.650 | 222.650 |
| London Sweep | no_trade_both | 72 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| London Sweep | unchanged | 76 | 76 | 76 | -47.100 | -47.100 | 0.000 |
| ORB 5m | direction_changed | 4 | 4 | 4 | -159.650 | 94.350 | 254.000 |
| ORB 5m | entry_time_changed | 15 | 15 | 15 | 143.125 | 30.375 | -112.750 |
| ORB 5m | extra_dates_no_trade | 2 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| ORB 5m | extra_dates_outside_common148 | 9 | 0 | 9 | 0.000 | 55.225 | 55.225 |
| ORB 5m | no_trade_both | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| ORB 5m | removed_common | 2 | 2 | 0 | -202.450 | 0.000 | 202.450 |
| ORB 5m | unchanged | 119 | 119 | 119 | -582.025 | -582.025 | 0.000 |
| ORB 15m | direction_changed | 2 | 2 | 2 | -124.200 | 54.300 | 178.500 |
| ORB 15m | entry_time_changed | 10 | 10 | 10 | 959.500 | 900.250 | -59.250 |
| ORB 15m | extra_dates_no_trade | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| ORB 15m | extra_dates_outside_common148 | 8 | 0 | 8 | 0.000 | 87.700 | 87.700 |
| ORB 15m | no_trade_both | 11 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| ORB 15m | removed_common | 2 | 2 | 0 | -341.450 | 0.000 | 341.450 |
| ORB 15m | unchanged | 123 | 123 | 123 | 41.325 | 41.325 | 0.000 |
| VWAP Extreme | extra_dates_no_trade | 6 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| VWAP Extreme | extra_dates_outside_common148 | 5 | 0 | 5 | 0.000 | 181.875 | 181.875 |
| VWAP Extreme | no_trade_both | 90 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| VWAP Extreme | unchanged | 58 | 58 | 58 | -86.050 | -86.050 | 0.000 |

### Gepaard verschil binnen common148

| Strategie | Veranderde common-dagen | Daarvan buiten rollvenster | Gem. verschil pt/dag | 95% CI | Ruwe p | Globale Holm p |
|---|---:|---:|---:|---|---:|---:|
| London Sweep | 0 | 0 | 0.000 | [0.000; 0.000] | 1.000 | 1.000 |
| ORB 5m | 21 | 0 | 2.322 | [-3.152; 8.865] | 0.429 | 1.000 |
| ORB 15m | 14 | 0 | 3.113 | [0.425; 6.836] | 0.058 | 0.928 |
| VWAP Extreme | 0 | 0 | 0.000 | [0.000; 0.000] | 1.000 | 1.000 |

## Maanden en richting

Alle onderstaande uitsplitsingen zijn beschrijvend: geen extra p-waarden, geen selectie van de beste maand of richting.

| Strategie | Periode | Uitsplitsing | Groep | Eligible dagen | Trades | Netto pt | PF | Winrate |
|---|---|---|---|---:|---:|---:|---:|---:|
| London Sweep | Dec–sep | direction | long | 159 | 38 | -73.050 | 0.955 | 44.7% |
| London Sweep | Dec–sep | direction | short | 159 | 44 | 248.600 | 1.139 | 40.9% |
| London Sweep | Dec–17 apr | direction | long | 53 | 12 | -479.450 | 0.460 | 25.0% |
| London Sweep | Dec–17 apr | direction | short | 53 | 12 | 406.550 | 1.603 | 50.0% |
| London Sweep | 18 apr–sep (reeds bekeken) | direction | long | 106 | 26 | 406.400 | 1.547 | 53.8% |
| London Sweep | 18 apr–sep (reeds bekeken) | direction | short | 106 | 32 | -157.950 | 0.859 | 37.5% |
| London Sweep | Dec–sep | month | 2025-01 | 5 | 2 | 359.300 | — | 100.0% |
| London Sweep | Dec–sep | month | 2025-02 | 18 | 9 | 35.475 | 1.080 | 44.4% |
| London Sweep | Dec–sep | month | 2025-03 | 19 | 11 | -938.475 | 0.162 | 9.1% |
| London Sweep | Dec–sep | month | 2025-04 | 19 | 5 | 643.375 | — | 100.0% |
| London Sweep | Dec–sep | month | 2025-05 | 21 | 6 | 18.650 | 1.101 | 50.0% |
| London Sweep | Dec–sep | month | 2025-06 | 20 | 12 | 157.050 | 1.436 | 50.0% |
| London Sweep | Dec–sep | month | 2025-07 | 20 | 16 | 267.400 | 1.590 | 50.0% |
| London Sweep | Dec–sep | month | 2025-08 | 19 | 10 | -44.250 | 0.890 | 40.0% |
| London Sweep | Dec–sep | month | 2025-09 | 18 | 11 | -322.975 | 0.295 | 18.2% |
| ORB 5m | Dec–sep | direction | long | 159 | 69 | -406.275 | 0.864 | 43.5% |
| ORB 5m | Dec–sep | direction | short | 159 | 78 | 4.200 | 1.001 | 37.2% |
| ORB 5m | Dec–17 apr | direction | long | 53 | 24 | -459.900 | 0.625 | 33.3% |
| ORB 5m | Dec–17 apr | direction | short | 53 | 22 | 694.800 | 1.624 | 50.0% |
| ORB 5m | 18 apr–sep (reeds bekeken) | direction | long | 106 | 45 | 53.625 | 1.031 | 48.9% |
| ORB 5m | 18 apr–sep (reeds bekeken) | direction | short | 106 | 56 | -690.600 | 0.703 | 32.1% |
| ORB 5m | Dec–sep | month | 2025-01 | 5 | 5 | -207.125 | 0.278 | 40.0% |
| ORB 5m | Dec–sep | month | 2025-02 | 18 | 17 | 704.175 | 2.559 | 58.8% |
| ORB 5m | Dec–sep | month | 2025-03 | 19 | 16 | -294.850 | 0.721 | 31.2% |
| ORB 5m | Dec–sep | month | 2025-04 | 19 | 16 | -238.850 | 0.800 | 37.5% |
| ORB 5m | Dec–sep | month | 2025-05 | 21 | 19 | -92.775 | 0.889 | 31.6% |
| ORB 5m | Dec–sep | month | 2025-06 | 20 | 19 | -296.275 | 0.626 | 36.8% |
| ORB 5m | Dec–sep | month | 2025-07 | 20 | 19 | -93.775 | 0.850 | 31.6% |
| ORB 5m | Dec–sep | month | 2025-08 | 19 | 19 | 420.975 | 1.761 | 57.9% |
| ORB 5m | Dec–sep | month | 2025-09 | 18 | 17 | -303.575 | 0.509 | 35.3% |
| ORB 15m | Dec–sep | direction | long | 159 | 67 | 178.675 | 1.080 | 52.2% |
| ORB 15m | Dec–sep | direction | short | 159 | 76 | 904.900 | 1.308 | 42.1% |
| ORB 15m | Dec–17 apr | direction | long | 53 | 23 | -64.925 | 0.935 | 43.5% |
| ORB 15m | Dec–17 apr | direction | short | 53 | 22 | 1421.050 | 2.862 | 63.6% |
| ORB 15m | 18 apr–sep (reeds bekeken) | direction | long | 106 | 44 | 243.600 | 1.200 | 56.8% |
| ORB 15m | 18 apr–sep (reeds bekeken) | direction | short | 106 | 54 | -516.150 | 0.763 | 33.3% |
| ORB 15m | Dec–sep | month | 2025-01 | 5 | 5 | -2.375 | 0.987 | 60.0% |
| ORB 15m | Dec–sep | month | 2025-02 | 18 | 17 | 593.175 | 2.314 | 58.8% |
| ORB 15m | Dec–sep | month | 2025-03 | 19 | 16 | 90.900 | 1.109 | 43.8% |
| ORB 15m | Dec–sep | month | 2025-04 | 19 | 15 | 738.125 | 2.008 | 60.0% |
| ORB 15m | Dec–sep | month | 2025-05 | 21 | 19 | -144.025 | 0.823 | 36.8% |
| ORB 15m | Dec–sep | month | 2025-06 | 20 | 16 | 12.150 | 1.027 | 56.2% |
| ORB 15m | Dec–sep | month | 2025-07 | 20 | 19 | -157.275 | 0.732 | 31.6% |
| ORB 15m | Dec–sep | month | 2025-08 | 19 | 19 | -43.275 | 0.936 | 47.4% |
| ORB 15m | Dec–sep | month | 2025-09 | 18 | 17 | -3.825 | 0.991 | 41.2% |
| VWAP Extreme | Dec–sep | direction | long | 159 | 32 | -50.200 | 0.951 | 53.1% |
| VWAP Extreme | Dec–sep | direction | short | 159 | 31 | 146.025 | 1.226 | 54.8% |
| VWAP Extreme | Dec–17 apr | direction | long | 53 | 12 | 23.050 | 1.045 | 50.0% |
| VWAP Extreme | Dec–17 apr | direction | short | 53 | 11 | -22.725 | 0.933 | 54.5% |
| VWAP Extreme | 18 apr–sep (reeds bekeken) | direction | long | 106 | 20 | -73.250 | 0.856 | 55.0% |
| VWAP Extreme | 18 apr–sep (reeds bekeken) | direction | short | 106 | 20 | 168.750 | 1.553 | 55.0% |
| VWAP Extreme | Dec–sep | month | 2025-01 | 5 | 2 | -101.450 | 0.000 | 0.0% |
| VWAP Extreme | Dec–sep | month | 2025-02 | 18 | 10 | 119.500 | 1.493 | 60.0% |
| VWAP Extreme | Dec–sep | month | 2025-03 | 19 | 7 | -39.075 | 0.860 | 57.1% |
| VWAP Extreme | Dec–sep | month | 2025-04 | 19 | 5 | -35.375 | 0.879 | 40.0% |
| VWAP Extreme | Dec–sep | month | 2025-05 | 21 | 6 | 131.900 | 2.725 | 66.7% |
| VWAP Extreme | Dec–sep | month | 2025-06 | 20 | 6 | 145.900 | 3.041 | 83.3% |
| VWAP Extreme | Dec–sep | month | 2025-07 | 20 | 10 | -96.750 | 0.642 | 40.0% |
| VWAP Extreme | Dec–sep | month | 2025-08 | 19 | 9 | -138.525 | 0.383 | 44.4% |
| VWAP Extreme | Dec–sep | month | 2025-09 | 18 | 8 | 109.700 | 1.969 | 62.5% |

## Rollovervensters versus overige dagen

| Strategie | Periode | Venster | Dagen | Nieuwe trades | Nieuw netto pt | Common148 oud pt | Common148 nieuw pt | Common148 verschil pt | Veranderde common-dagen |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| London Sweep | Dec–sep | first20_after_roll | 45 | 22 | 527.550 | 304.900 | 304.900 | 0.000 | 0 |
| London Sweep | Dec–sep | outside_roll_window | 114 | 60 | -352.000 | -352.000 | -352.000 | 0.000 | 0 |
| London Sweep | Dec–17 apr | first20_after_roll | 18 | 7 | -37.575 | 105.150 | 105.150 | 0.000 | 0 |
| London Sweep | Dec–17 apr | outside_roll_window | 35 | 17 | -35.325 | -35.325 | -35.325 | 0.000 | 0 |
| London Sweep | 18 apr–sep (reeds bekeken) | first20_after_roll | 27 | 15 | 565.125 | 199.750 | 199.750 | 0.000 | 0 |
| London Sweep | 18 apr–sep (reeds bekeken) | outside_roll_window | 79 | 43 | -316.675 | -316.675 | -316.675 | 0.000 | 0 |
| ORB 5m | Dec–sep | first20_after_roll | 45 | 39 | -176.275 | -575.200 | -231.500 | 343.700 | 21 |
| ORB 5m | Dec–sep | outside_roll_window | 114 | 108 | -225.800 | -225.800 | -225.800 | 0.000 | 0 |
| ORB 5m | Dec–17 apr | first20_after_roll | 18 | 14 | -38.400 | -492.400 | 67.300 | 559.700 | 9 |
| ORB 5m | Dec–17 apr | outside_roll_window | 35 | 32 | 273.300 | 273.300 | 273.300 | 0.000 | 0 |
| ORB 5m | 18 apr–sep (reeds bekeken) | first20_after_roll | 27 | 25 | -137.875 | -82.800 | -298.800 | -216.000 | 12 |
| ORB 5m | 18 apr–sep (reeds bekeken) | outside_roll_window | 79 | 76 | -499.100 | -499.100 | -499.100 | 0.000 | 0 |
| ORB 15m | Dec–sep | first20_after_roll | 45 | 37 | 1158.175 | 609.775 | 1070.475 | 460.700 | 14 |
| ORB 15m | Dec–sep | outside_roll_window | 114 | 106 | -74.600 | -74.600 | -74.600 | 0.000 | 0 |
| ORB 15m | Dec–17 apr | first20_after_roll | 18 | 13 | 923.075 | 721.325 | 1028.775 | 307.450 | 8 |
| ORB 15m | Dec–17 apr | outside_roll_window | 35 | 32 | 433.050 | 433.050 | 433.050 | 0.000 | 0 |
| ORB 15m | 18 apr–sep (reeds bekeken) | first20_after_roll | 27 | 24 | 235.100 | -111.550 | 41.700 | 153.250 | 6 |
| ORB 15m | 18 apr–sep (reeds bekeken) | outside_roll_window | 79 | 74 | -507.650 | -507.650 | -507.650 | 0.000 | 0 |
| VWAP Extreme | Dec–sep | first20_after_roll | 45 | 16 | 250.650 | 68.775 | 68.775 | 0.000 | 0 |
| VWAP Extreme | Dec–sep | outside_roll_window | 114 | 47 | -154.825 | -154.825 | -154.825 | 0.000 | 0 |
| VWAP Extreme | Dec–17 apr | first20_after_roll | 18 | 6 | -3.600 | -3.600 | -3.600 | 0.000 | 0 |
| VWAP Extreme | Dec–17 apr | outside_roll_window | 35 | 17 | 3.925 | 3.925 | 3.925 | 0.000 | 0 |
| VWAP Extreme | 18 apr–sep (reeds bekeken) | first20_after_roll | 27 | 10 | 254.250 | 72.375 | 72.375 | 0.000 | 0 |
| VWAP Extreme | 18 apr–sep (reeds bekeken) | outside_roll_window | 79 | 30 | -158.750 | -158.750 | -158.750 | 0.000 | 0 |

## Uitbijters en kosten

Verwijder exact de drie hoogste netto trades per strategie/periode. Geen aangepaste entry/exit of parameterselectie. Bij netto verlies is top3/nettowinst niet gedefinieerd. De kostenscenario’s veranderen alleen de kosten op dezelfde fills: 2/4/6 ticks per kant plus $4,50 RT commissie = $24,50/$44,50/$64,50 per roundtrip.

| Strategie | Periode | Basis pt | Beste 3 pt | Beste 3 / nettowinst | Zonder beste 3 pt | $44,50 RT pt | $64,50 RT pt | Gerealiseerde max. DD pt |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| London Sweep | Dec–sep | 175.550 | 661.325 | 376.7% | -485.775 | 93.550 | 11.550 | 1119.250 |
| London Sweep | Dec–17 apr | -72.900 | 661.325 | — | -734.225 | -96.900 | -120.900 | 1119.250 |
| London Sweep | 18 apr–sep (reeds bekeken) | 248.450 | 412.825 | 166.2% | -164.375 | 190.450 | 132.450 | 505.250 |
| ORB 5m | Dec–sep | -402.075 | 815.825 | — | -1217.900 | -549.075 | -696.075 | 1332.325 |
| ORB 5m | Dec–17 apr | 234.900 | 815.825 | 347.3% | -580.925 | 188.900 | 142.900 | 772.250 |
| ORB 5m | 18 apr–sep (reeds bekeken) | -636.975 | 548.575 | — | -1185.550 | -737.975 | -838.975 | 1220.200 |
| ORB 15m | Dec–sep | 1083.575 | 871.325 | 80.4% | 212.250 | 940.575 | 797.575 | 792.450 |
| ORB 15m | Dec–17 apr | 1356.125 | 871.325 | 64.3% | 484.800 | 1311.125 | 1266.125 | 315.425 |
| ORB 15m | 18 apr–sep (reeds bekeken) | -272.550 | 514.075 | — | -786.625 | -370.550 | -468.550 | 792.450 |
| VWAP Extreme | Dec–sep | 95.825 | 436.075 | 455.1% | -340.250 | 32.825 | -30.175 | 310.625 |
| VWAP Extreme | Dec–17 apr | 0.325 | 436.075 | 134176.9% | -435.750 | -22.675 | -45.675 | 310.625 |
| VWAP Extreme | 18 apr–sep (reeds bekeken) | 95.500 | 223.075 | 233.6% | -127.575 | 55.500 | 15.500 | 283.875 |

## Grenzen

- Entire dataset already observed; no independent validation or causal claim.
- Holm applies to the 16 listed tests; subgroup and cost/outlier tables are descriptive, not additional p-value searches.
- Bootstrap intervals nominal 95%, not simultaneous; 2000 draws and few regimes limit precision.
- Higher-cost scenarios alter only costs on identical fills; no market-impact or order-book execution simulation.
- Rollover-window concentration also reflects where the reference construction differs; it is not independent evidence of a tradable rollover effect.
- Closed-trade drawdown only; strategies not combined as a portfolio.

Geen causale verklaring, geen strategiepromotie, geen nieuwe filters of geoptimaliseerde stops/targets. Dit rapport beschrijft alleen de reeds berekende vaste-regels-variant.

Reproductie met de geverifieerde private bestanden: `npm run research:volume-stability`. Publiceren van uitsluitend aggregaten: voeg `-- --publish` toe. Private tradeverschillen blijven in `artifacts/volume-stability/trade-attribution.csv`.
