# Judas — directe vervanging van pijler B

EXPLORATORY_POST_SELECTION_REPLACEMENT_NOT_INDEPENDENT_VALIDATION

S1/S2 baseline2ec3a07 en de volledige ICT-scan blijven ongewijzigd. Geen50/50-verdunning: volledige A+Judas, B exact verwijderd. Alle portefeuillematenR gebruiken vooraf bekende ATR14; initiële stopR hieronder alleen voor losse ICT-trades.

## Zeven varianten — strenge entry trade-through, gecombineerd

| Variant | N | Netto ATR-R | Netto stopR | Netto pt | Win% | PF ATR | PF stop | Sharpe ATR | Sharpe stop | DD ATR | DD stop | +kalenderkwartalen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ICT3_1m_BULL_LONG_OPEN0930_JUDAS_TIME | 90 | 4.624945 | 22.579523 | 1158.500000 | 43.333333 | 1.345539 | 1.455806 | 0.556084 | 0.645398 | 2.586534 | 8.239992 | 12/19 |
| ICT3_5m_BOTH_OPEN0830_JUDAS_2R | 100 | 6.669589 | 11.676062 | 1207.500000 | 46.000000 | 1.449403 | 1.236290 | 0.710064 | 0.443489 | 2.581509 | 8.664284 | 11/19 |
| ICT3_5m_BOTH_OPEN0830_JUDAS_3R | 100 | 6.387951 | 9.529900 | 1453.500000 | 44.000000 | 1.417657 | 1.187089 | 0.626729 | 0.345320 | 2.791283 | 9.004944 | 11/19 |
| ICT3_5m_BOTH_OPEN0830_JUDAS_TIME | 100 | 5.178469 | 7.283888 | 841.750000 | 44.000000 | 1.338578 | 1.142996 | 0.553000 | 0.272194 | 2.791283 | 9.004944 | 11/19 |
| ICT3_5m_BULL_LONG_OPEN0930_JUDAS_2R | 57 | 4.013209 | 13.192352 | 520.925000 | 54.385965 | 1.546389 | 1.576828 | 0.652917 | 0.697302 | 1.712847 | 5.172942 | 8/19 |
| ICT3_5m_BULL_LONG_OPEN0930_JUDAS_3R | 57 | 4.015738 | 13.138671 | 542.925000 | 54.385965 | 1.546734 | 1.574481 | 0.646258 | 0.684601 | 1.764542 | 6.040942 | 7/19 |
| ICT3_5m_BULL_LONG_OPEN0930_JUDAS_TIME | 57 | 3.956909 | 12.894652 | 530.175000 | 54.385965 | 1.538724 | 1.563811 | 0.639903 | 0.677851 | 1.764542 | 6.040942 | 7/19 |

## Portefeuilles — volledige oude en nieuwe vergelijking

| Periode | Model | N | Netto ATR-R | Netto pt | Win% | PF ATR-R | Sharpe | Mark-DD ATR-R | Mark-DD pt | +kalenderkwartalen |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019_2021 | S1_ORIGINAL | 172 | 5.568025 | 951.800 | 50.000 | 1.226766 | 0.631404 | 3.544729 | 625.100 | 7/12 |
| 2019_2021 | S2_ORIGINAL | 585 | 24.884535 | 4034.375 | 58.120 | 1.301434 | 1.359838 | 5.769347 | 745.775 | 10/12 |
| 2019_2021 | S1_JUDAS | 143 | 8.576419 | 1177.325 | 51.748 | 1.390231 | 0.968647 | 2.902943 | 434.875 | 8/12 |
| 2019_2021 | S2_JUDAS | 556 | 27.892929 | 4259.900 | 58.993 | 1.348759 | 1.533802 | 5.335828 | 812.000 | 12/12 |
| 2024_2026 | S1_ORIGINAL | 79 | 9.019145 | 2724.225 | 60.759 | 2.298846 | 1.952099 | 1.681878 | 677.450 | 6/7 |
| 2024_2026 | S2_ORIGINAL | 299 | 13.918962 | 3123.475 | 57.860 | 1.353553 | 1.497005 | 6.055709 | 3461.725 | 5/7 |
| 2024_2026 | S1_JUDAS | 59 | 9.634748 | 3290.475 | 59.322 | 2.814107 | 2.097581 | 2.814750 | 1071.525 | 4/7 |
| 2024_2026 | S2_JUDAS | 279 | 14.534565 | 3689.725 | 57.348 | 1.385166 | 1.517127 | 5.413555 | 2397.325 | 4/7 |
| COMBINED | S1_ORIGINAL | 251 | 14.587170 | 3676.025 | 53.386 | 1.463113 | 1.084526 | 3.544729 | 677.450 | 13/19 |
| COMBINED | S2_ORIGINAL | 884 | 38.803497 | 7157.850 | 58.032 | 1.318263 | 1.404941 | 6.055709 | 3461.725 | 15/19 |
| COMBINED | S1_JUDAS | 202 | 18.211167 | 4467.800 | 53.960 | 1.667349 | 1.353171 | 2.902943 | 1071.525 | 12/19 |
| COMBINED | S2_JUDAS | 835 | 42.427495 | 7949.625 | 58.443 | 1.360430 | 1.527889 | 5.413555 | 2397.325 | 16/19 |

## Onzekerheid — absolute portefeuilles en gepaarde meerwaarde

Nominaal95%basic moving2-maand-block-bootstrap,20.000trekkingen. Intervallen voor verwacht totaalR zijn het gemiddelde per cashdag ×vast aantal dagen. De gerealiseerde historische som zelf is niet onzeker. De gepaarde delta is voor beide vervangingen exact Judas−B en wordt daarom niet dubbel als bewijs geteld. Holm9 corrigeert deze nieuwe negen unieke contrasten; eerdere selectie uit80varianten blijft van toepassing.

| Periode | Contrast | Gemiddeld ATR-R/cashdag | 95%CI verwacht totaal ATR-R | p tweezijdig | Holm9 p | Familie95%Bonf9 totaal ATR-R |
|---|---|---:|---|---:|---:|---|
| 2019_2021 | S1_JUDAS | 0.01145049 | [-2.508897; 16.641750] | 0.115994 | 0.579971 | [-7.708288; 19.427933] |
| 2019_2021 | S2_JUDAS | 0.03724023 | [15.697309; 38.208550] | 0.000100 | 0.000900 | [10.194578; 42.452680] |
| 2019_2021 | JUDAS_MINUS_B | 0.00401655 | [-6.041815; 11.060278] | 0.520774 | 1.000000 | [-9.553574; 14.166380] |
| 2024_2026 | S1_JUDAS | 0.02283116 | [0.726817; 17.974494] | 0.033498 | 0.200990 | [-2.566883; 21.169414] |
| 2024_2026 | S2_JUDAS | 0.03444210 | [-4.276338; 33.039348] | 0.131893 | 0.579971 | [-12.903928; 39.157661] |
| 2024_2026 | JUDAS_MINUS_B | 0.00145877 | [-6.122943; 6.194295] | 0.847458 | 1.000000 | [-9.213106; 7.965421] |
| COMBINED | S1_JUDAS | 0.01555181 | [4.115693; 29.708901] | 0.013899 | 0.097295 | [-2.073407; 34.548119] |
| COMBINED | S2_JUDAS | 0.03623185 | [19.811730; 63.170964] | 0.000100 | 0.000900 | [10.766348; 71.297506] |
| COMBINED | JUDAS_MINUS_B | 0.00309479 | [-7.559244; 13.388417] | 0.542873 | 1.000000 | [-12.413658; 17.355422] |

## Overlap en datakwaliteit

```json
{
  "overlap": {
    "S1": {
      "overlap_pairs": 0,
      "overlap_minutes": 0
    },
    "S2": {
      "overlap_pairs": 0,
      "overlap_minutes": 0
    }
  },
  "quality": {
    "S1": {
      "2019_2021": {
        "N": 75,
        "incomplete_paths": 14,
        "unidentified_stop_paths": 14
      },
      "2024_2026": {
        "N": 27,
        "incomplete_paths": 1,
        "unidentified_stop_paths": 1
      }
    },
    "S2": {
      "2019_2021": {
        "N": 488,
        "incomplete_paths": 91,
        "unidentified_stop_paths": null
      },
      "2024_2026": {
        "N": 247,
        "incomplete_paths": 17,
        "unidentified_stop_paths": null
      }
    }
  }
}
```

Strengefill betreft één tick trade-through bij de FVG-entry; target-touch en conservatieve intrabarvolgorde blijven zoals bevroren in de ICT-studie. Mark-DD gebruikt waargenomen minuutopens/-closes en fills, geen bewezen worst-tick drawdown. Onvolledige overnightpaden en onbekende eerdere stoptriggers worden niet achteraf weggefilterd.

## Kwartalen — alle kalenderkwartalen inclusief nulposities

| Periode | Model | Kwartaal | N | Netto ATR-R | Netto pt |
|---|---|---|---:|---:|---:|
| 2019_2021 | S1_ORIGINAL | 2019Q1 | 11 | -1.025057 | -94.475 |
| 2019_2021 | S1_ORIGINAL | 2019Q2 | 17 | -1.142858 | -92.825 |
| 2019_2021 | S1_ORIGINAL | 2019Q3 | 16 | -0.720241 | -59.100 |
| 2019_2021 | S1_ORIGINAL | 2019Q4 | 11 | 2.029957 | 141.275 |
| 2019_2021 | S1_ORIGINAL | 2020Q1 | 18 | 2.143689 | 213.950 |
| 2019_2021 | S1_ORIGINAL | 2020Q2 | 10 | 1.485441 | 301.500 |
| 2019_2021 | S1_ORIGINAL | 2020Q3 | 6 | 1.110873 | 253.900 |
| 2019_2021 | S1_ORIGINAL | 2020Q4 | 14 | 0.936457 | 113.850 |
| 2019_2021 | S1_ORIGINAL | 2021Q1 | 15 | -1.031614 | -203.875 |
| 2019_2021 | S1_ORIGINAL | 2021Q2 | 17 | -1.314250 | -214.325 |
| 2019_2021 | S1_ORIGINAL | 2021Q3 | 24 | 1.249218 | 230.350 |
| 2019_2021 | S1_ORIGINAL | 2021Q4 | 13 | 1.846409 | 361.575 |
| 2019_2021 | S2_ORIGINAL | 2019Q1 | 57 | 1.852088 | 167.675 |
| 2019_2021 | S2_ORIGINAL | 2019Q2 | 51 | 3.730434 | 400.775 |
| 2019_2021 | S2_ORIGINAL | 2019Q3 | 50 | 1.600572 | 150.500 |
| 2019_2021 | S2_ORIGINAL | 2019Q4 | 58 | 5.227127 | 433.200 |
| 2019_2021 | S2_ORIGINAL | 2020Q1 | 44 | -1.854916 | -255.900 |
| 2019_2021 | S2_ORIGINAL | 2020Q2 | 45 | 5.140293 | 1091.125 |
| 2019_2021 | S2_ORIGINAL | 2020Q3 | 14 | 0.131433 | 32.350 |
| 2019_2021 | S2_ORIGINAL | 2020Q4 | 59 | 4.056090 | 995.475 |
| 2019_2021 | S2_ORIGINAL | 2021Q1 | 49 | -1.239905 | -251.775 |
| 2019_2021 | S2_ORIGINAL | 2021Q2 | 50 | 1.856357 | 474.500 |
| 2019_2021 | S2_ORIGINAL | 2021Q3 | 62 | 1.777666 | 290.800 |
| 2019_2021 | S2_ORIGINAL | 2021Q4 | 46 | 2.607297 | 505.650 |
| 2019_2021 | S1_JUDAS | 2019Q1 | 7 | 0.123311 | 9.425 |
| 2019_2021 | S1_JUDAS | 2019Q2 | 11 | -0.220982 | 11.275 |
| 2019_2021 | S1_JUDAS | 2019Q3 | 11 | -1.251107 | -136.975 |
| 2019_2021 | S1_JUDAS | 2019Q4 | 11 | 0.996562 | 36.025 |
| 2019_2021 | S1_JUDAS | 2020Q1 | 17 | 4.262195 | 380.425 |
| 2019_2021 | S1_JUDAS | 2020Q2 | 10 | -0.127604 | -2.750 |
| 2019_2021 | S1_JUDAS | 2020Q3 | 5 | 1.098306 | 251.125 |
| 2019_2021 | S1_JUDAS | 2020Q4 | 14 | 0.554255 | 145.600 |
| 2019_2021 | S1_JUDAS | 2021Q1 | 11 | 0.759448 | 215.275 |
| 2019_2021 | S1_JUDAS | 2021Q2 | 12 | 0.872253 | 129.300 |
| 2019_2021 | S1_JUDAS | 2021Q3 | 17 | 1.712729 | 323.925 |
| 2019_2021 | S1_JUDAS | 2021Q4 | 17 | -0.202947 | -185.325 |
| 2019_2021 | S2_JUDAS | 2019Q1 | 53 | 3.000456 | 271.575 |
| 2019_2021 | S2_JUDAS | 2019Q2 | 45 | 4.652310 | 504.875 |
| 2019_2021 | S2_JUDAS | 2019Q3 | 45 | 1.069706 | 72.625 |
| 2019_2021 | S2_JUDAS | 2019Q4 | 58 | 4.193732 | 327.950 |
| 2019_2021 | S2_JUDAS | 2020Q1 | 43 | 0.263589 | -89.425 |
| 2019_2021 | S2_JUDAS | 2020Q2 | 45 | 3.527247 | 786.875 |
| 2019_2021 | S2_JUDAS | 2020Q3 | 13 | 0.118867 | 29.575 |
| 2019_2021 | S2_JUDAS | 2020Q4 | 59 | 3.673888 | 1027.225 |
| 2019_2021 | S2_JUDAS | 2021Q1 | 45 | 0.551156 | 167.375 |
| 2019_2021 | S2_JUDAS | 2021Q2 | 45 | 4.042859 | 818.125 |
| 2019_2021 | S2_JUDAS | 2021Q3 | 55 | 2.241177 | 384.375 |
| 2019_2021 | S2_JUDAS | 2021Q4 | 50 | 0.557941 | -41.250 |
| 2024_2026 | S1_ORIGINAL | 2025Q1 | 5 | 0.779760 | 272.125 |
| 2024_2026 | S1_ORIGINAL | 2025Q2 | 11 | 0.658310 | 343.525 |
| 2024_2026 | S1_ORIGINAL | 2025Q3 | 24 | 4.956828 | 1194.600 |
| 2024_2026 | S1_ORIGINAL | 2025Q4 | 8 | 0.493255 | 40.200 |
| 2024_2026 | S1_ORIGINAL | 2026Q1 | 6 | 0.151058 | 102.400 |
| 2024_2026 | S1_ORIGINAL | 2026Q2 | 14 | 2.236580 | 892.100 |
| 2024_2026 | S1_ORIGINAL | 2026Q3 | 11 | -0.256647 | -120.725 |
| 2024_2026 | S2_ORIGINAL | 2025Q1 | 20 | -0.552855 | -228.000 |
| 2024_2026 | S2_ORIGINAL | 2025Q2 | 51 | 3.418691 | 1125.275 |
| 2024_2026 | S2_ORIGINAL | 2025Q3 | 68 | 7.616207 | 1773.200 |
| 2024_2026 | S2_ORIGINAL | 2025Q4 | 48 | 1.283866 | 390.700 |
| 2024_2026 | S2_ORIGINAL | 2026Q1 | 19 | 0.438255 | 186.725 |
| 2024_2026 | S2_ORIGINAL | 2026Q2 | 55 | 2.560396 | 735.625 |
| 2024_2026 | S2_ORIGINAL | 2026Q3 | 38 | -0.845599 | -860.050 |
| 2024_2026 | S1_JUDAS | 2025Q1 | 2 | 0.615596 | 210.050 |
| 2024_2026 | S1_JUDAS | 2025Q2 | 7 | 2.465530 | 1001.425 |
| 2024_2026 | S1_JUDAS | 2025Q3 | 12 | 4.769678 | 1124.550 |
| 2024_2026 | S1_JUDAS | 2025Q4 | 8 | -0.618455 | -347.050 |
| 2024_2026 | S1_JUDAS | 2026Q1 | 5 | -0.717430 | -234.375 |
| 2024_2026 | S1_JUDAS | 2026Q2 | 15 | 3.831679 | 1798.125 |
| 2024_2026 | S1_JUDAS | 2026Q3 | 10 | -0.711849 | -262.250 |
| 2024_2026 | S2_JUDAS | 2025Q1 | 17 | -0.717019 | -290.075 |
| 2024_2026 | S2_JUDAS | 2025Q2 | 47 | 5.225912 | 1783.175 |
| 2024_2026 | S2_JUDAS | 2025Q3 | 56 | 7.429057 | 1703.150 |
| 2024_2026 | S2_JUDAS | 2025Q4 | 48 | 0.172157 | 3.450 |
| 2024_2026 | S2_JUDAS | 2026Q1 | 18 | -0.430234 | -150.050 |
| 2024_2026 | S2_JUDAS | 2026Q2 | 56 | 4.155495 | 1641.650 |
| 2024_2026 | S2_JUDAS | 2026Q3 | 37 | -1.300801 | -1001.575 |
| COMBINED | S1_ORIGINAL | 2019Q1 | 11 | -1.025057 | -94.475 |
| COMBINED | S1_ORIGINAL | 2019Q2 | 17 | -1.142858 | -92.825 |
| COMBINED | S1_ORIGINAL | 2019Q3 | 16 | -0.720241 | -59.100 |
| COMBINED | S1_ORIGINAL | 2019Q4 | 11 | 2.029957 | 141.275 |
| COMBINED | S1_ORIGINAL | 2020Q1 | 18 | 2.143689 | 213.950 |
| COMBINED | S1_ORIGINAL | 2020Q2 | 10 | 1.485441 | 301.500 |
| COMBINED | S1_ORIGINAL | 2020Q3 | 6 | 1.110873 | 253.900 |
| COMBINED | S1_ORIGINAL | 2020Q4 | 14 | 0.936457 | 113.850 |
| COMBINED | S1_ORIGINAL | 2021Q1 | 15 | -1.031614 | -203.875 |
| COMBINED | S1_ORIGINAL | 2021Q2 | 17 | -1.314250 | -214.325 |
| COMBINED | S1_ORIGINAL | 2021Q3 | 24 | 1.249218 | 230.350 |
| COMBINED | S1_ORIGINAL | 2021Q4 | 13 | 1.846409 | 361.575 |
| COMBINED | S1_ORIGINAL | 2025Q1 | 5 | 0.779760 | 272.125 |
| COMBINED | S1_ORIGINAL | 2025Q2 | 11 | 0.658310 | 343.525 |
| COMBINED | S1_ORIGINAL | 2025Q3 | 24 | 4.956828 | 1194.600 |
| COMBINED | S1_ORIGINAL | 2025Q4 | 8 | 0.493255 | 40.200 |
| COMBINED | S1_ORIGINAL | 2026Q1 | 6 | 0.151058 | 102.400 |
| COMBINED | S1_ORIGINAL | 2026Q2 | 14 | 2.236580 | 892.100 |
| COMBINED | S1_ORIGINAL | 2026Q3 | 11 | -0.256647 | -120.725 |
| COMBINED | S2_ORIGINAL | 2019Q1 | 57 | 1.852088 | 167.675 |
| COMBINED | S2_ORIGINAL | 2019Q2 | 51 | 3.730434 | 400.775 |
| COMBINED | S2_ORIGINAL | 2019Q3 | 50 | 1.600572 | 150.500 |
| COMBINED | S2_ORIGINAL | 2019Q4 | 58 | 5.227127 | 433.200 |
| COMBINED | S2_ORIGINAL | 2020Q1 | 44 | -1.854916 | -255.900 |
| COMBINED | S2_ORIGINAL | 2020Q2 | 45 | 5.140293 | 1091.125 |
| COMBINED | S2_ORIGINAL | 2020Q3 | 14 | 0.131433 | 32.350 |
| COMBINED | S2_ORIGINAL | 2020Q4 | 59 | 4.056090 | 995.475 |
| COMBINED | S2_ORIGINAL | 2021Q1 | 49 | -1.239905 | -251.775 |
| COMBINED | S2_ORIGINAL | 2021Q2 | 50 | 1.856357 | 474.500 |
| COMBINED | S2_ORIGINAL | 2021Q3 | 62 | 1.777666 | 290.800 |
| COMBINED | S2_ORIGINAL | 2021Q4 | 46 | 2.607297 | 505.650 |
| COMBINED | S2_ORIGINAL | 2025Q1 | 20 | -0.552855 | -228.000 |
| COMBINED | S2_ORIGINAL | 2025Q2 | 51 | 3.418691 | 1125.275 |
| COMBINED | S2_ORIGINAL | 2025Q3 | 68 | 7.616207 | 1773.200 |
| COMBINED | S2_ORIGINAL | 2025Q4 | 48 | 1.283866 | 390.700 |
| COMBINED | S2_ORIGINAL | 2026Q1 | 19 | 0.438255 | 186.725 |
| COMBINED | S2_ORIGINAL | 2026Q2 | 55 | 2.560396 | 735.625 |
| COMBINED | S2_ORIGINAL | 2026Q3 | 38 | -0.845599 | -860.050 |
| COMBINED | S1_JUDAS | 2019Q1 | 7 | 0.123311 | 9.425 |
| COMBINED | S1_JUDAS | 2019Q2 | 11 | -0.220982 | 11.275 |
| COMBINED | S1_JUDAS | 2019Q3 | 11 | -1.251107 | -136.975 |
| COMBINED | S1_JUDAS | 2019Q4 | 11 | 0.996562 | 36.025 |
| COMBINED | S1_JUDAS | 2020Q1 | 17 | 4.262195 | 380.425 |
| COMBINED | S1_JUDAS | 2020Q2 | 10 | -0.127604 | -2.750 |
| COMBINED | S1_JUDAS | 2020Q3 | 5 | 1.098306 | 251.125 |
| COMBINED | S1_JUDAS | 2020Q4 | 14 | 0.554255 | 145.600 |
| COMBINED | S1_JUDAS | 2021Q1 | 11 | 0.759448 | 215.275 |
| COMBINED | S1_JUDAS | 2021Q2 | 12 | 0.872253 | 129.300 |
| COMBINED | S1_JUDAS | 2021Q3 | 17 | 1.712729 | 323.925 |
| COMBINED | S1_JUDAS | 2021Q4 | 17 | -0.202947 | -185.325 |
| COMBINED | S1_JUDAS | 2025Q1 | 2 | 0.615596 | 210.050 |
| COMBINED | S1_JUDAS | 2025Q2 | 7 | 2.465530 | 1001.425 |
| COMBINED | S1_JUDAS | 2025Q3 | 12 | 4.769678 | 1124.550 |
| COMBINED | S1_JUDAS | 2025Q4 | 8 | -0.618455 | -347.050 |
| COMBINED | S1_JUDAS | 2026Q1 | 5 | -0.717430 | -234.375 |
| COMBINED | S1_JUDAS | 2026Q2 | 15 | 3.831679 | 1798.125 |
| COMBINED | S1_JUDAS | 2026Q3 | 10 | -0.711849 | -262.250 |
| COMBINED | S2_JUDAS | 2019Q1 | 53 | 3.000456 | 271.575 |
| COMBINED | S2_JUDAS | 2019Q2 | 45 | 4.652310 | 504.875 |
| COMBINED | S2_JUDAS | 2019Q3 | 45 | 1.069706 | 72.625 |
| COMBINED | S2_JUDAS | 2019Q4 | 58 | 4.193732 | 327.950 |
| COMBINED | S2_JUDAS | 2020Q1 | 43 | 0.263589 | -89.425 |
| COMBINED | S2_JUDAS | 2020Q2 | 45 | 3.527247 | 786.875 |
| COMBINED | S2_JUDAS | 2020Q3 | 13 | 0.118867 | 29.575 |
| COMBINED | S2_JUDAS | 2020Q4 | 59 | 3.673888 | 1027.225 |
| COMBINED | S2_JUDAS | 2021Q1 | 45 | 0.551156 | 167.375 |
| COMBINED | S2_JUDAS | 2021Q2 | 45 | 4.042859 | 818.125 |
| COMBINED | S2_JUDAS | 2021Q3 | 55 | 2.241177 | 384.375 |
| COMBINED | S2_JUDAS | 2021Q4 | 50 | 0.557941 | -41.250 |
| COMBINED | S2_JUDAS | 2025Q1 | 17 | -0.717019 | -290.075 |
| COMBINED | S2_JUDAS | 2025Q2 | 47 | 5.225912 | 1783.175 |
| COMBINED | S2_JUDAS | 2025Q3 | 56 | 7.429057 | 1703.150 |
| COMBINED | S2_JUDAS | 2025Q4 | 48 | 0.172157 | 3.450 |
| COMBINED | S2_JUDAS | 2026Q1 | 18 | -0.430234 | -150.050 |
| COMBINED | S2_JUDAS | 2026Q2 | 56 | 4.155495 | 1641.650 |
| COMBINED | S2_JUDAS | 2026Q3 | 37 | -1.300801 | -1001.575 |

## Vaste methode

- date: 2026-10-25
- status: EXPLORATORY_POST_SELECTION_REPLACEMENT_NOT_INDEPENDENT_VALIDATION
- baseline_commit: 2ec3a07adcf2f1bc0301c267a4f410ce44b69905
- rules: Exactly selected ICT3_5m_BOTH_OPEN0830_JUDAS_2R, frozen one-tick trade-through entry, unchanged targets/stop/fee. S1-Judas=all original selective stopped A plus Judas; S2-Judas=all original broad unstopped bull nights plus Judas. Remove exactly original B149. No50/50 allocation or netting; each sequential position full original ATR exposure.
- strict_scope: Trade-through means one tick beyond the entry limit. Targets retain the frozen ICT touch/causal-order rules; it is not a tick-level or queue certificate. Overnight source/fill limitations remain identical to baseline.
- winner_check: Recheck ALL80 frozen variants in each era and both fill modes: total netATR-R,tradePF_ATR anddailySharpe must each be strictly greater than B. Never assume the earlier touch-only label alone proves this. Report all actual qualifying variants and both-fill metrics.
- units: PortfolioR=netpoints/priorATR14. Standalone ICT initialStopR uses initial stopdistance and is separately reported; NEVER sum initialStopR with overnight ATR-R. NQpoints1contract/execution; total1.225point($24.50)friction per executed leg; no MNQ-cost assumption.
- reconstruction: Twice reconstruct sources, frozen B selectors, exact chosen Judas chain/strict fills, and same-held-contract overnight paths. Match every frozen ledger execution and original S1/S2 full stats incl marked DD. Complete-path/stop-identification limits carried, not changed or silently dropped.
- chronology: Verify actual interval intersections for A and Judas, not only nominal RTH windows. Assert zero-overlap before summing at full size. All cash days749+422 included, zeros included, overnight assigned next cashdate, Judas samecashday. Report marked minuteopen/close DD plus fills, not unobservable tick-DD.
- inference: 20000 joint moving2calendar-month blocks, same fixed seeds as ICT scan2026102511/+1. Separate36old/21recent months; no era-gap blocks. Basic95%CIs and centered equal-tail two-sided p. Absolute S1-Judas andS2-Judas per3periods=6tests plus UNIQUE paired Judas-minus-B difference per3periods=3tests:Holm9. Also Bonferroni9 simultaneous95%totalR intervals. Delta exactly same for both portfolios and matches prior frozen ICT paired inference. Prior Holm480 and selection caveats remain; new Holm9 does not erase earlier scan.
- outputs: Append-only new code/report/aggregateCSV/JSON/local dashboard. ALL existing tracked and untracked research and benchmark files hash-preserved. No new strategy/signals/grid/exit optimization and no independent confirmation claim.
