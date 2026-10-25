# Twee pijlers: schaal, benchmark, overnight-risico en portefeuille

DESCRIPTIVE_SCALE_BENCHMARK_RISK_PORTFOLIO_NOT_NEW_VALIDATION

Vaste regels op reeds bekeken ontwikkelingsdata; geen nieuwe onafhankelijke toets. A=16:00->volgende09:30 na sterke trenddag; B=P/+1ATR. Kosten1.225punt pertrade.

## Benchmark op gemeenschappelijke SMA20-populatie

| Blok | Groep | N | Netto pt/trade | Netto R/trade | Netto %/trade | PF pt | PF R | PF % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| COMBINED | A_ORIGINAL | 100 | 27.152 | 0.06546 | 0.12032 | 2.226 | 1.39598 | 1.64266 |
| COMBINED | A_MATCHED | 99 | 27.727 | 0.06769 | 0.12372 | 2.256 | 1.40927 | 1.66182 |
| COMBINED | BULL | 723 | 8.941 | 0.04667 | 0.06823 | 1.279 | 1.33150 | 1.34356 |
| COMBINED | ALL | 1006 | 8.162 | 0.03257 | 0.04632 | 1.188 | 1.19522 | 1.17519 |
| 2019_2021 | A_ORIGINAL | 73 | 3.957 | -0.01030 | 0.02192 | 1.161 | 0.95073 | 1.09377 |
| 2019_2021 | A_MATCHED | 72 | 4.424 | -0.00828 | 0.02522 | 1.181 | 0.96053 | 1.10778 |
| 2019_2021 | BULL | 479 | 7.144 | 0.04365 | 0.07251 | 1.349 | 1.30424 | 1.37944 |
| 2019_2021 | ALL | 618 | 5.288 | 0.02832 | 0.04662 | 1.205 | 1.17177 | 1.18969 |
| 2024_2026 | A_ORIGINAL | 27 | 89.868 | 0.27029 | 0.38638 | 6.742 | 6.74208 | 7.29539 |
| 2024_2026 | A_MATCHED | 27 | 89.868 | 0.27029 | 0.38638 | 6.742 | 6.74208 | 7.29539 |
| 2024_2026 | BULL | 244 | 12.468 | 0.05259 | 0.05984 | 1.227 | 1.38816 | 1.28047 |
| 2024_2026 | ALL | 388 | 12.738 | 0.03934 | 0.04584 | 1.178 | 1.23146 | 1.15589 |

## MAE in vooraf bekende ATR-eenheden

| Blok | Pad | N | P10 | P25 | P50 | P75 | P90 | P95 | Max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| COMBINED | observed_all | 100 | 0.0290 | 0.0674 | 0.1660 | 0.3969 | 0.7113 | 1.1507 | 2.6409 |
| COMBINED | complete | 86 | 0.0321 | 0.0641 | 0.1697 | 0.4019 | 0.7800 | 1.1548 | 2.6409 |
| 2019_2021 | observed_all | 73 | 0.0180 | 0.0595 | 0.1742 | 0.4870 | 0.7810 | 1.2388 | 2.6409 |
| 2019_2021 | complete | 60 | 0.0189 | 0.0594 | 0.2023 | 0.5105 | 0.8466 | 1.3854 | 2.6409 |
| 2024_2026 | observed_all | 27 | 0.0479 | 0.0795 | 0.1429 | 0.2310 | 0.3477 | 0.3888 | 0.9767 |
| 2024_2026 | complete | 26 | 0.0473 | 0.0777 | 0.1496 | 0.2460 | 0.3485 | 0.3914 | 0.9767 |

## Portefeuille (R per vooraf bekende ATR, raw points apart)

| Blok | Model | N | Netto R | Netto pt | PF R | Sharpe dagelijks R | DD R | DD pt | +R kwartalen |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| COMBINED | A | 100 | 6.54596 | 2715.250 | 1.396 | 0.540 | 5.37490 | 419.700 | 12/19 |
| COMBINED | B | 149 | 3.04559 | 415.725 | 1.160 | 0.336 | 3.31491 | 741.375 | 8/19 |
| COMBINED | A_PLUS_B | 249 | 9.59155 | 3130.975 | 1.270 | 0.626 | 5.68337 | 677.450 | 13/19 |
| COMBINED | A_STOP | 100 | 10.61104 | 3065.750 | 1.859 | 1.099 | 3.07135 | 290.375 | 11/19 |
| COMBINED | A_STOP_PLUS_B | 249 | 13.65663 | 3481.475 | 1.435 | 1.030 | 3.44323 | 677.450 | 13/19 |
| 2019_2021 | A | 73 | -0.75192 | 288.825 | 0.951 | -0.088 | 5.37490 | 419.700 | 7/12 |
| 2019_2021 | B | 97 | 1.43248 | 151.175 | 1.108 | 0.240 | 3.31491 | 651.700 | 4/12 |
| 2019_2021 | A_PLUS_B | 170 | 0.68057 | 440.000 | 1.024 | 0.064 | 5.68337 | 676.475 | 7/12 |
| 2019_2021 | A_STOP | 73 | 3.20500 | 606.075 | 1.287 | 0.517 | 3.07135 | 290.375 | 6/12 |
| 2019_2021 | A_STOP_PLUS_B | 170 | 4.63749 | 757.250 | 1.190 | 0.537 | 3.44323 | 610.625 | 7/12 |
| 2024_2026 | A | 27 | 7.29788 | 2426.425 | 6.742 | 2.098 | 1.21578 | 358.975 | 5/7 |
| 2024_2026 | B | 52 | 1.61311 | 264.550 | 1.279 | 0.523 | 1.40000 | 741.375 | 4/7 |
| 2024_2026 | A_PLUS_B | 79 | 8.91098 | 2690.975 | 2.264 | 1.919 | 1.79004 | 677.450 | 6/7 |
| 2024_2026 | A_STOP | 27 | 7.40604 | 2459.675 | 7.369 | 2.148 | 0.77577 | 260.425 | 5/7 |
| 2024_2026 | A_STOP_PLUS_B | 79 | 9.01915 | 2724.225 | 2.299 | 1.952 | 1.68188 | 677.450 | 6/7 |

## Stop: gepaarde controle uitsluitend volledige holdingpaden

| Blok | Variant | N | Netto R | Netto pt | PF R | DD R | DD pt |
|---|---|---:|---:|---:|---:|---:|---:|
| COMBINED | A | 86 | 3.96644 | 2458.650 | 1.252 | 6.73714 | 485.150 |
| COMBINED | A_STOP | 86 | 8.22742 | 2824.150 | 1.723 | 3.46807 | 289.400 |
| 2019_2021 | A | 60 | -3.13501 | 99.250 | 0.784 | 6.73714 | 485.150 |
| 2019_2021 | A_STOP | 60 | 1.01781 | 431.500 | 1.100 | 3.46807 | 289.400 |
| 2024_2026 | A | 26 | 7.10145 | 2359.400 | 6.588 | 1.21578 | 358.975 |
| 2024_2026 | A_STOP | 26 | 7.20961 | 2392.650 | 7.200 | 0.77577 | 260.425 |

## Beschikbaarheid en stopidentificatie

```json
{
  "2019_2021": {
    "entry_pool": 733,
    "SMA20_candidate_dates": 629,
    "cash_days": 749,
    "selected_not_in_common": [
      "2021-06-04"
    ],
    "benchmark_rejections": {
      "CONTRACT_SWITCH": 10,
      "NO_NEXT_CASH_SESSION": 1
    },
    "stop_reasons": {
      "NEXT_OPEN": 56,
      "STOP": 16,
      "STOP_GAP": 1
    },
    "original_A_parity": true,
    "original_B_parity": true,
    "executable_common_nights": 618,
    "selected_A": 73,
    "selected_complete_paths": 60,
    "original_missing_minutes": 17,
    "stopped_path_unidentified": 13
  },
  "2024_2026": {
    "entry_pool": 418,
    "SMA20_candidate_dates": 395,
    "cash_days": 422,
    "selected_not_in_common": [],
    "benchmark_rejections": {
      "CONTRACT_SWITCH": 6,
      "NO_NEXT_CASH_SESSION": 1
    },
    "stop_reasons": {
      "NEXT_OPEN": 26,
      "STOP": 1
    },
    "original_A_parity": true,
    "original_B_parity": true,
    "executable_common_nights": 388,
    "selected_A": 27,
    "selected_complete_paths": 26,
    "original_missing_minutes": 1,
    "stopped_path_unidentified": 1
  }
}
```

## Vooraf vastgelegde methode

- date: 2026-10-25
- status: DESCRIPTIVE_CONSUMED_DEVELOPMENT_AUDIT
- preservation: Preserve all previous files and price_volume outputs. Exactly original A100 and B149, recomputed from source with unchanged selectors. No other models, parameter fitting, reversed shorts, best-of choice, live approval, Git push or deployment.
- common: 1024 entry-session dates with PREOPEN SMA20 available (629old,395recent) inside fixed1151priorATR pool. These are candidate dates, not1024 guaranteed executable nights. Same next-actual-cash-session, same-contract, endpoint and usable-bar requirements as original A. No missing-price filling or crossing2021--2024.
- comparators: ALL on common dates; BULL on these same dates with completed current RTHclose>current terminal SMA20 (known at16:00, exactly the base condition of original A). A_MATCHED is original A intersect common executable nights; also retain original A100 separately if masks differ. Report membership difference rather than forcing100 into1024. BULL is not yesterday preopen bull: it is entry-time close>SMA20, matching original A.
- scaling: ATR14 known before entry-session09:30, never next-day ATR. netR=(exit-entry-1.225)/entry_session_priorATR; netpct=100*(exit-entry-1.225)/entry_price. Percentage sums descriptive arithmetic sums, not compounded capital returns. Costs applied once per execution, including stopped trades.
- MAE: Gross price excursion from actual16:00entry to minimum observed minute low before next09:30, also including exit09:30OPEN; never its low/close. Express positive adverse magnitude / priorATR. Incomplete holding paths give observed lower bounds; report all100 and complete-path subset separately.
- stop: ONE fixed catastrophe-stop from16:00entry through next actual cash09:30open:entry-0.50priorATR rounded TOWARDentry to0.25tick. A stop touch fills level; gap through stop fills worse actual minuteopen, may lose>0.50R. Earliest observed trigger only, no target, no restart; same total1.225pt friction. Maintenance/weekends have no invented print. Endpointbar only open can trigger. No extra stop-slippage grid.
- missing_stop: Same100 observed-path simulations reported conditionally; missing scheduled minutes before simulated exit mean actual first-stop outcome cannot be certified. Also paired original/stop results on fully observed original holding paths, not a fitted exclusion. Missing minutes after an already identified stop cannot change that fill. No unknown bars are assumed safe.
- portfolio: Primary A(original no stop)+B(original P/+1ATR), each full1/ATR unit per sequential position, no halfweight or fitted allocation. Raw points shown separately for1NQ/trade, not implied back-conversion of normalized sizing. Additional fixed A_STOP and A_STOP+B are labeled sensitivity, not chosen in hindsight.
- chronology: Assert chronological entry>=previous exit per model and combination. All positions flat before next daily16:00boundary. Daily scores realized by that boundary:overnight result assigned next actual cash session even if a stop occurred in prior civil evening; B to its exit session. Use every cash session incl flat/early-close days from first eligible date to last, not trade-only or only1151clean-entry dates. No zero days during2022--2024 gap.
- metrics: PF in R on net individual executions (also rawpoint/%PF for benchmark); report daily aggregated PF separately in JSON. Sharpe=sqrt252*mean full-cash-day netR/SD(ddof1), no account-risk-free/return-on-capital interpretation. MaxDD chronological observed minuteopens/closes plus known fills, fees atentry, in R and rawpoints. Quarterly netR and netpoints by daily16:00accounting session; report positive R quarters/quarters with trades.
- validation: Two periods and quarterly sequence are fixed-rule chronological stability, NOT new out-of-sample or honest walk-forward validation:both periods and survivor selection already consumed. No new significance tests or independent promotion.
- reproduce: Two source reconstructions, original A/B numeric and membership parity, normalization/fee identities, nonoverlap assertions, protected-file checks and byte-identical outputs.

## Kwartaalstabiliteit op uitstap-/cash-boundary-datum

| Blok | Model | Kwartaal | N | Netto R | Netto pt |
|---|---|---|---:|---:|---:|
| COMBINED | A | 2019Q1 | 4 | -0.22277 | -12.900 |
| COMBINED | A | 2019Q2 | 7 | -3.46760 | -252.825 |
| COMBINED | A | 2019Q3 | 5 | 0.31447 | 25.875 |
| COMBINED | A | 2019Q4 | 4 | 0.31295 | 24.350 |
| COMBINED | A | 2020Q1 | 8 | 1.31560 | 192.200 |
| COMBINED | A | 2020Q2 | 5 | -0.66766 | -121.125 |
| COMBINED | A | 2020Q3 | 4 | 0.70291 | 202.600 |
| COMBINED | A | 2020Q4 | 5 | 1.07514 | 206.375 |
| COMBINED | A | 2021Q1 | 5 | -0.87950 | -131.375 |
| COMBINED | A | 2021Q2 | 5 | -0.33220 | -59.875 |
| COMBINED | A | 2021Q3 | 13 | 0.29162 | 52.825 |
| COMBINED | A | 2021Q4 | 8 | 0.80511 | 162.700 |
| COMBINED | A | 2025Q1 | 1 | 0.19643 | 67.025 |
| COMBINED | A | 2025Q2 | 5 | 1.10533 | 477.875 |
| COMBINED | A | 2025Q3 | 10 | 3.96111 | 945.500 |
| COMBINED | A | 2025Q4 | 2 | 0.66876 | 150.800 |
| COMBINED | A | 2026Q1 | 1 | -0.61148 | -187.975 |
| COMBINED | A | 2026Q2 | 5 | 2.07512 | 960.125 |
| COMBINED | A | 2026Q3 | 3 | -0.09740 | 13.075 |
| COMBINED | B | 2019Q1 | 7 | -0.60640 | -66.575 |
| COMBINED | B | 2019Q2 | 10 | -0.07752 | -15.000 |
| COMBINED | B | 2019Q3 | 11 | -0.50058 | -34.975 |
| COMBINED | B | 2019Q4 | 7 | 1.64735 | 111.675 |
| COMBINED | B | 2020Q1 | 10 | -0.08948 | -30.750 |
| COMBINED | B | 2020Q2 | 4 | 1.24100 | 234.350 |
| COMBINED | B | 2020Q3 | 2 | -0.22481 | -52.950 |
| COMBINED | B | 2020Q4 | 9 | -0.13868 | -92.525 |
| COMBINED | B | 2021Q1 | 10 | -0.60713 | -88.000 |
| COMBINED | B | 2021Q2 | 11 | -0.88055 | -139.975 |
| COMBINED | B | 2021Q3 | 11 | 0.66171 | 134.025 |
| COMBINED | B | 2021Q4 | 5 | 1.00757 | 191.875 |
| COMBINED | B | 2025Q1 | 4 | 0.58333 | 205.100 |
| COMBINED | B | 2025Q2 | 6 | -0.44702 | -134.350 |
| COMBINED | B | 2025Q3 | 14 | 0.99572 | 249.100 |
| COMBINED | B | 2025Q4 | 6 | -0.17551 | -110.600 |
| COMBINED | B | 2026Q1 | 5 | 0.65438 | 257.125 |
| COMBINED | B | 2026Q2 | 9 | 0.16146 | -68.025 |
| COMBINED | B | 2026Q3 | 8 | -0.15925 | -133.800 |
| COMBINED | A_PLUS_B | 2019Q1 | 11 | -0.82916 | -79.475 |
| COMBINED | A_PLUS_B | 2019Q2 | 17 | -3.54512 | -267.825 |
| COMBINED | A_PLUS_B | 2019Q3 | 16 | -0.18611 | -9.100 |
| COMBINED | A_PLUS_B | 2019Q4 | 11 | 1.96031 | 136.025 |
| COMBINED | A_PLUS_B | 2020Q1 | 18 | 1.22612 | 161.450 |
| COMBINED | A_PLUS_B | 2020Q2 | 9 | 0.57334 | 113.225 |
| COMBINED | A_PLUS_B | 2020Q3 | 6 | 0.47810 | 149.650 |
| COMBINED | A_PLUS_B | 2020Q4 | 14 | 0.93646 | 113.850 |
| COMBINED | A_PLUS_B | 2021Q1 | 15 | -1.48663 | -219.375 |
| COMBINED | A_PLUS_B | 2021Q2 | 16 | -1.21275 | -199.850 |
| COMBINED | A_PLUS_B | 2021Q3 | 24 | 0.95334 | 186.850 |
| COMBINED | A_PLUS_B | 2021Q4 | 13 | 1.81268 | 354.575 |
| COMBINED | A_PLUS_B | 2025Q1 | 5 | 0.77976 | 272.125 |
| COMBINED | A_PLUS_B | 2025Q2 | 11 | 0.65831 | 343.525 |
| COMBINED | A_PLUS_B | 2025Q3 | 24 | 4.95683 | 1194.600 |
| COMBINED | A_PLUS_B | 2025Q4 | 8 | 0.49325 | 40.200 |
| COMBINED | A_PLUS_B | 2026Q1 | 6 | 0.04290 | 69.150 |
| COMBINED | A_PLUS_B | 2026Q2 | 14 | 2.23658 | 892.100 |
| COMBINED | A_PLUS_B | 2026Q3 | 11 | -0.25665 | -120.725 |
| COMBINED | A_STOP | 2019Q1 | 4 | -0.41866 | -27.900 |
| COMBINED | A_STOP | 2019Q2 | 7 | -1.06534 | -77.825 |
| COMBINED | A_STOP | 2019Q3 | 5 | -0.21967 | -24.125 |
| COMBINED | A_STOP | 2019Q4 | 4 | 0.38260 | 29.600 |
| COMBINED | A_STOP | 2020Q1 | 8 | 2.23317 | 244.700 |
| COMBINED | A_STOP | 2020Q2 | 5 | -0.78760 | -141.875 |
| COMBINED | A_STOP | 2020Q3 | 4 | 1.33569 | 306.850 |
| COMBINED | A_STOP | 2020Q4 | 5 | 1.07514 | 206.375 |
| COMBINED | A_STOP | 2021Q1 | 5 | -0.42448 | -115.875 |
| COMBINED | A_STOP | 2021Q2 | 5 | -0.33220 | -59.875 |
| COMBINED | A_STOP | 2021Q3 | 13 | 0.58751 | 96.325 |
| COMBINED | A_STOP | 2021Q4 | 8 | 0.83884 | 169.700 |
| COMBINED | A_STOP | 2025Q1 | 1 | 0.19643 | 67.025 |
| COMBINED | A_STOP | 2025Q2 | 5 | 1.10533 | 477.875 |
| COMBINED | A_STOP | 2025Q3 | 10 | 3.96111 | 945.500 |
| COMBINED | A_STOP | 2025Q4 | 2 | 0.66876 | 150.800 |
| COMBINED | A_STOP | 2026Q1 | 1 | -0.50332 | -154.725 |
| COMBINED | A_STOP | 2026Q2 | 5 | 2.07512 | 960.125 |
| COMBINED | A_STOP | 2026Q3 | 3 | -0.09740 | 13.075 |
| COMBINED | A_STOP_PLUS_B | 2019Q1 | 11 | -1.02506 | -94.475 |
| COMBINED | A_STOP_PLUS_B | 2019Q2 | 17 | -1.14286 | -92.825 |
| COMBINED | A_STOP_PLUS_B | 2019Q3 | 16 | -0.72024 | -59.100 |
| COMBINED | A_STOP_PLUS_B | 2019Q4 | 11 | 2.02996 | 141.275 |
| COMBINED | A_STOP_PLUS_B | 2020Q1 | 18 | 2.14369 | 213.950 |
| COMBINED | A_STOP_PLUS_B | 2020Q2 | 9 | 0.45340 | 92.475 |
| COMBINED | A_STOP_PLUS_B | 2020Q3 | 6 | 1.11087 | 253.900 |
| COMBINED | A_STOP_PLUS_B | 2020Q4 | 14 | 0.93646 | 113.850 |
| COMBINED | A_STOP_PLUS_B | 2021Q1 | 15 | -1.03161 | -203.875 |
| COMBINED | A_STOP_PLUS_B | 2021Q2 | 16 | -1.21275 | -199.850 |
| COMBINED | A_STOP_PLUS_B | 2021Q3 | 24 | 1.24922 | 230.350 |
| COMBINED | A_STOP_PLUS_B | 2021Q4 | 13 | 1.84641 | 361.575 |
| COMBINED | A_STOP_PLUS_B | 2025Q1 | 5 | 0.77976 | 272.125 |
| COMBINED | A_STOP_PLUS_B | 2025Q2 | 11 | 0.65831 | 343.525 |
| COMBINED | A_STOP_PLUS_B | 2025Q3 | 24 | 4.95683 | 1194.600 |
| COMBINED | A_STOP_PLUS_B | 2025Q4 | 8 | 0.49325 | 40.200 |
| COMBINED | A_STOP_PLUS_B | 2026Q1 | 6 | 0.15106 | 102.400 |
| COMBINED | A_STOP_PLUS_B | 2026Q2 | 14 | 2.23658 | 892.100 |
| COMBINED | A_STOP_PLUS_B | 2026Q3 | 11 | -0.25665 | -120.725 |
| 2019_2021 | A | 2019Q1 | 4 | -0.22277 | -12.900 |
| 2019_2021 | A | 2019Q2 | 7 | -3.46760 | -252.825 |
| 2019_2021 | A | 2019Q3 | 5 | 0.31447 | 25.875 |
| 2019_2021 | A | 2019Q4 | 4 | 0.31295 | 24.350 |
| 2019_2021 | A | 2020Q1 | 8 | 1.31560 | 192.200 |
| 2019_2021 | A | 2020Q2 | 5 | -0.66766 | -121.125 |
| 2019_2021 | A | 2020Q3 | 4 | 0.70291 | 202.600 |
| 2019_2021 | A | 2020Q4 | 5 | 1.07514 | 206.375 |
| 2019_2021 | A | 2021Q1 | 5 | -0.87950 | -131.375 |
| 2019_2021 | A | 2021Q2 | 5 | -0.33220 | -59.875 |
| 2019_2021 | A | 2021Q3 | 13 | 0.29162 | 52.825 |
| 2019_2021 | A | 2021Q4 | 8 | 0.80511 | 162.700 |
| 2019_2021 | B | 2019Q1 | 7 | -0.60640 | -66.575 |
| 2019_2021 | B | 2019Q2 | 10 | -0.07752 | -15.000 |
| 2019_2021 | B | 2019Q3 | 11 | -0.50058 | -34.975 |
| 2019_2021 | B | 2019Q4 | 7 | 1.64735 | 111.675 |
| 2019_2021 | B | 2020Q1 | 10 | -0.08948 | -30.750 |
| 2019_2021 | B | 2020Q2 | 4 | 1.24100 | 234.350 |
| 2019_2021 | B | 2020Q3 | 2 | -0.22481 | -52.950 |
| 2019_2021 | B | 2020Q4 | 9 | -0.13868 | -92.525 |
| 2019_2021 | B | 2021Q1 | 10 | -0.60713 | -88.000 |
| 2019_2021 | B | 2021Q2 | 11 | -0.88055 | -139.975 |
| 2019_2021 | B | 2021Q3 | 11 | 0.66171 | 134.025 |
| 2019_2021 | B | 2021Q4 | 5 | 1.00757 | 191.875 |
| 2019_2021 | A_PLUS_B | 2019Q1 | 11 | -0.82916 | -79.475 |
| 2019_2021 | A_PLUS_B | 2019Q2 | 17 | -3.54512 | -267.825 |
| 2019_2021 | A_PLUS_B | 2019Q3 | 16 | -0.18611 | -9.100 |
| 2019_2021 | A_PLUS_B | 2019Q4 | 11 | 1.96031 | 136.025 |
| 2019_2021 | A_PLUS_B | 2020Q1 | 18 | 1.22612 | 161.450 |
| 2019_2021 | A_PLUS_B | 2020Q2 | 9 | 0.57334 | 113.225 |
| 2019_2021 | A_PLUS_B | 2020Q3 | 6 | 0.47810 | 149.650 |
| 2019_2021 | A_PLUS_B | 2020Q4 | 14 | 0.93646 | 113.850 |
| 2019_2021 | A_PLUS_B | 2021Q1 | 15 | -1.48663 | -219.375 |
| 2019_2021 | A_PLUS_B | 2021Q2 | 16 | -1.21275 | -199.850 |
| 2019_2021 | A_PLUS_B | 2021Q3 | 24 | 0.95334 | 186.850 |
| 2019_2021 | A_PLUS_B | 2021Q4 | 13 | 1.81268 | 354.575 |
| 2019_2021 | A_STOP | 2019Q1 | 4 | -0.41866 | -27.900 |
| 2019_2021 | A_STOP | 2019Q2 | 7 | -1.06534 | -77.825 |
| 2019_2021 | A_STOP | 2019Q3 | 5 | -0.21967 | -24.125 |
| 2019_2021 | A_STOP | 2019Q4 | 4 | 0.38260 | 29.600 |
| 2019_2021 | A_STOP | 2020Q1 | 8 | 2.23317 | 244.700 |
| 2019_2021 | A_STOP | 2020Q2 | 5 | -0.78760 | -141.875 |
| 2019_2021 | A_STOP | 2020Q3 | 4 | 1.33569 | 306.850 |
| 2019_2021 | A_STOP | 2020Q4 | 5 | 1.07514 | 206.375 |
| 2019_2021 | A_STOP | 2021Q1 | 5 | -0.42448 | -115.875 |
| 2019_2021 | A_STOP | 2021Q2 | 5 | -0.33220 | -59.875 |
| 2019_2021 | A_STOP | 2021Q3 | 13 | 0.58751 | 96.325 |
| 2019_2021 | A_STOP | 2021Q4 | 8 | 0.83884 | 169.700 |
| 2019_2021 | A_STOP_PLUS_B | 2019Q1 | 11 | -1.02506 | -94.475 |
| 2019_2021 | A_STOP_PLUS_B | 2019Q2 | 17 | -1.14286 | -92.825 |
| 2019_2021 | A_STOP_PLUS_B | 2019Q3 | 16 | -0.72024 | -59.100 |
| 2019_2021 | A_STOP_PLUS_B | 2019Q4 | 11 | 2.02996 | 141.275 |
| 2019_2021 | A_STOP_PLUS_B | 2020Q1 | 18 | 2.14369 | 213.950 |
| 2019_2021 | A_STOP_PLUS_B | 2020Q2 | 9 | 0.45340 | 92.475 |
| 2019_2021 | A_STOP_PLUS_B | 2020Q3 | 6 | 1.11087 | 253.900 |
| 2019_2021 | A_STOP_PLUS_B | 2020Q4 | 14 | 0.93646 | 113.850 |
| 2019_2021 | A_STOP_PLUS_B | 2021Q1 | 15 | -1.03161 | -203.875 |
| 2019_2021 | A_STOP_PLUS_B | 2021Q2 | 16 | -1.21275 | -199.850 |
| 2019_2021 | A_STOP_PLUS_B | 2021Q3 | 24 | 1.24922 | 230.350 |
| 2019_2021 | A_STOP_PLUS_B | 2021Q4 | 13 | 1.84641 | 361.575 |
| 2024_2026 | A | 2025Q1 | 1 | 0.19643 | 67.025 |
| 2024_2026 | A | 2025Q2 | 5 | 1.10533 | 477.875 |
| 2024_2026 | A | 2025Q3 | 10 | 3.96111 | 945.500 |
| 2024_2026 | A | 2025Q4 | 2 | 0.66876 | 150.800 |
| 2024_2026 | A | 2026Q1 | 1 | -0.61148 | -187.975 |
| 2024_2026 | A | 2026Q2 | 5 | 2.07512 | 960.125 |
| 2024_2026 | A | 2026Q3 | 3 | -0.09740 | 13.075 |
| 2024_2026 | B | 2025Q1 | 4 | 0.58333 | 205.100 |
| 2024_2026 | B | 2025Q2 | 6 | -0.44702 | -134.350 |
| 2024_2026 | B | 2025Q3 | 14 | 0.99572 | 249.100 |
| 2024_2026 | B | 2025Q4 | 6 | -0.17551 | -110.600 |
| 2024_2026 | B | 2026Q1 | 5 | 0.65438 | 257.125 |
| 2024_2026 | B | 2026Q2 | 9 | 0.16146 | -68.025 |
| 2024_2026 | B | 2026Q3 | 8 | -0.15925 | -133.800 |
| 2024_2026 | A_PLUS_B | 2025Q1 | 5 | 0.77976 | 272.125 |
| 2024_2026 | A_PLUS_B | 2025Q2 | 11 | 0.65831 | 343.525 |
| 2024_2026 | A_PLUS_B | 2025Q3 | 24 | 4.95683 | 1194.600 |
| 2024_2026 | A_PLUS_B | 2025Q4 | 8 | 0.49325 | 40.200 |
| 2024_2026 | A_PLUS_B | 2026Q1 | 6 | 0.04290 | 69.150 |
| 2024_2026 | A_PLUS_B | 2026Q2 | 14 | 2.23658 | 892.100 |
| 2024_2026 | A_PLUS_B | 2026Q3 | 11 | -0.25665 | -120.725 |
| 2024_2026 | A_STOP | 2025Q1 | 1 | 0.19643 | 67.025 |
| 2024_2026 | A_STOP | 2025Q2 | 5 | 1.10533 | 477.875 |
| 2024_2026 | A_STOP | 2025Q3 | 10 | 3.96111 | 945.500 |
| 2024_2026 | A_STOP | 2025Q4 | 2 | 0.66876 | 150.800 |
| 2024_2026 | A_STOP | 2026Q1 | 1 | -0.50332 | -154.725 |
| 2024_2026 | A_STOP | 2026Q2 | 5 | 2.07512 | 960.125 |
| 2024_2026 | A_STOP | 2026Q3 | 3 | -0.09740 | 13.075 |
| 2024_2026 | A_STOP_PLUS_B | 2025Q1 | 5 | 0.77976 | 272.125 |
| 2024_2026 | A_STOP_PLUS_B | 2025Q2 | 11 | 0.65831 | 343.525 |
| 2024_2026 | A_STOP_PLUS_B | 2025Q3 | 24 | 4.95683 | 1194.600 |
| 2024_2026 | A_STOP_PLUS_B | 2025Q4 | 8 | 0.49325 | 40.200 |
| 2024_2026 | A_STOP_PLUS_B | 2026Q1 | 6 | 0.15106 | 102.400 |
| 2024_2026 | A_STOP_PLUS_B | 2026Q2 | 14 | 2.23658 | 892.100 |
| 2024_2026 | A_STOP_PLUS_B | 2026Q3 | 11 | -0.25665 | -120.725 |
