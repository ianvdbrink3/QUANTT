# ICT versus B, S1 en S2 — vaste beschrijvende vergelijking

EXPLORATORY_CONSUMED_DEVELOPMENT_POOL_NOT_INDEPENDENT_VALIDATION

- candidate: Positive net ATR-R in BOTH eras with touch AND one-tick trade-through; combinedN>=30 reported as descriptive sample-size label, not tuned exclusion.
- dominates_B: For each era: greater total net ATR-R AND higher trade PF_ATR_R AND higher daily Sharpe_ATR_R than frozen B. DD is reported as a separate tradeoff; no claim of general dominance if worse DD.
- portfolio: For BOTH eras and BOTH S1/S2 baselines: equal0.5/0.5 separate sleeves improve daily Sharpe and do not increase DAILY close DD, plus positive standalone in both eras under bothfill assumptions. Diagnostic only; no third-pillar promotion.
- significance: All Holm480 tests remain reported. Already-consumed development pool and selection cannot provide independent validation, even when p passes.

## Aantallen

- positive_both_eras_both_fills: 26/80
- touch_exceeds_B_return_PF_sharpe_both_eras: 7/80
- descriptive_portfolio_condition: 11/80
- incremental_holm480_all_periods: 0/80

## Alle varianten

| Variant | N | Netto ATR-R | Positief beide perioden en fills | B hoger rendement/PF/Sharpe beide perioden | Portefeuilleconditie beide baselines/perioden | Holm480 meerwaarde alle perioden |
|---|---:|---:|---|---|---|---|
| ICT1_1m_BOTH_ON_REVERSAL_2R | 433 | 5.961308 | True | False | False | False |
| ICT1_1m_BOTH_ON_REVERSAL_3R | 433 | 7.519032 | True | False | False | False |
| ICT1_1m_BOTH_ON_REVERSAL_OPPOSITE_ON | 429 | 6.176019 | False | False | False | False |
| ICT1_1m_BOTH_PRE_REVERSAL_2R | 706 | -8.776534 | False | False | False | False |
| ICT1_1m_BOTH_PRE_REVERSAL_3R | 706 | -4.856495 | False | False | False | False |
| ICT1_1m_BOTH_PRE_REVERSAL_OPPOSITE_ON | 585 | -3.789070 | False | False | False | False |
| ICT2_1m_BOTH_AM_FADE_2R | 449 | -7.217318 | False | False | False | False |
| ICT2_1m_BOTH_AM_FADE_3R | 449 | -7.080130 | False | False | False | False |
| ICT2_1m_BOTH_AM_CONTINUE_2R | 283 | -0.895653 | False | False | False | False |
| ICT2_1m_BOTH_AM_CONTINUE_3R | 283 | 0.313101 | False | False | False | False |
| ICT2_1m_BOTH_PM_FADE_2R | 216 | -2.035119 | False | False | False | False |
| ICT2_1m_BOTH_PM_FADE_3R | 216 | -1.746418 | False | False | False | False |
| ICT2_1m_BOTH_PM_CONTINUE_2R | 137 | 1.546684 | True | False | True | False |
| ICT2_1m_BOTH_PM_CONTINUE_3R | 137 | -0.281115 | False | False | False | False |
| ICT3_1m_BOTH_OPEN0930_JUDAS_2R | 140 | 0.841518 | True | False | False | False |
| ICT3_1m_BOTH_OPEN0930_JUDAS_3R | 140 | 3.457428 | True | False | False | False |
| ICT3_1m_BOTH_OPEN0930_JUDAS_TIME | 140 | 4.154577 | True | False | False | False |
| ICT3_1m_BOTH_OPEN0830_JUDAS_2R | 164 | -0.176705 | False | False | False | False |
| ICT3_1m_BOTH_OPEN0830_JUDAS_3R | 164 | 2.382609 | False | False | False | False |
| ICT3_1m_BOTH_OPEN0830_JUDAS_TIME | 164 | 1.400353 | False | False | False | False |
| ICT1_1m_BULL_LONG_ON_REVERSAL_2R | 129 | -0.338660 | False | False | False | False |
| ICT1_1m_BULL_LONG_ON_REVERSAL_3R | 129 | -1.364508 | False | False | False | False |
| ICT1_1m_BULL_LONG_ON_REVERSAL_OPPOSITE_ON | 128 | -1.604762 | False | False | False | False |
| ICT1_1m_BULL_LONG_PRE_REVERSAL_2R | 286 | -5.987341 | False | False | False | False |
| ICT1_1m_BULL_LONG_PRE_REVERSAL_3R | 286 | -6.626458 | False | False | False | False |
| ICT1_1m_BULL_LONG_PRE_REVERSAL_OPPOSITE_ON | 233 | -5.349276 | False | False | False | False |
| ICT2_1m_BULL_LONG_AM_FADE_2R | 150 | -4.782785 | False | False | False | False |
| ICT2_1m_BULL_LONG_AM_FADE_3R | 150 | -3.639056 | False | False | False | False |
| ICT2_1m_BULL_LONG_AM_CONTINUE_2R | 66 | -0.209230 | False | False | False | False |
| ICT2_1m_BULL_LONG_AM_CONTINUE_3R | 66 | -0.358090 | False | False | False | False |
| ICT2_1m_BULL_LONG_PM_FADE_2R | 64 | -1.239014 | False | False | False | False |
| ICT2_1m_BULL_LONG_PM_FADE_3R | 64 | -0.479516 | False | False | False | False |
| ICT2_1m_BULL_LONG_PM_CONTINUE_2R | 44 | -0.777779 | False | False | False | False |
| ICT2_1m_BULL_LONG_PM_CONTINUE_3R | 44 | 0.028669 | False | False | False | False |
| ICT3_1m_BULL_LONG_OPEN0930_JUDAS_2R | 91 | 2.446811 | True | False | False | False |
| ICT3_1m_BULL_LONG_OPEN0930_JUDAS_3R | 91 | 3.872041 | True | False | False | False |
| ICT3_1m_BULL_LONG_OPEN0930_JUDAS_TIME | 91 | 4.127495 | True | True | False | False |
| ICT3_1m_BULL_LONG_OPEN0830_JUDAS_2R | 107 | 0.247773 | False | False | False | False |
| ICT3_1m_BULL_LONG_OPEN0830_JUDAS_3R | 107 | 1.902510 | False | False | False | False |
| ICT3_1m_BULL_LONG_OPEN0830_JUDAS_TIME | 107 | 1.310103 | False | False | False | False |
| ICT1_5m_BOTH_ON_REVERSAL_2R | 158 | 8.249554 | False | False | False | False |
| ICT1_5m_BOTH_ON_REVERSAL_3R | 158 | 6.811025 | False | False | False | False |
| ICT1_5m_BOTH_ON_REVERSAL_OPPOSITE_ON | 154 | 7.124334 | False | False | False | False |
| ICT1_5m_BOTH_PRE_REVERSAL_2R | 269 | -0.857365 | False | False | False | False |
| ICT1_5m_BOTH_PRE_REVERSAL_3R | 269 | -1.345596 | False | False | False | False |
| ICT1_5m_BOTH_PRE_REVERSAL_OPPOSITE_ON | 203 | 0.183554 | False | False | False | False |
| ICT2_5m_BOTH_AM_FADE_2R | 162 | -0.323925 | False | False | False | False |
| ICT2_5m_BOTH_AM_FADE_3R | 162 | 0.783538 | False | False | False | False |
| ICT2_5m_BOTH_AM_CONTINUE_2R | 91 | -0.324374 | False | False | False | False |
| ICT2_5m_BOTH_AM_CONTINUE_3R | 91 | 0.906226 | True | False | False | False |
| ICT2_5m_BOTH_PM_FADE_2R | 99 | -3.163526 | False | False | False | False |
| ICT2_5m_BOTH_PM_FADE_3R | 99 | -4.089576 | False | False | False | False |
| ICT2_5m_BOTH_PM_CONTINUE_2R | 72 | -0.968368 | False | False | False | False |
| ICT2_5m_BOTH_PM_CONTINUE_3R | 72 | -1.375897 | False | False | False | False |
| ICT3_5m_BOTH_OPEN0930_JUDAS_2R | 76 | 3.631151 | False | False | False | False |
| ICT3_5m_BOTH_OPEN0930_JUDAS_3R | 76 | 5.574499 | False | False | False | False |
| ICT3_5m_BOTH_OPEN0930_JUDAS_TIME | 76 | 4.981787 | False | False | False | False |
| ICT3_5m_BOTH_OPEN0830_JUDAS_2R | 100 | 6.669589 | True | True | False | False |
| ICT3_5m_BOTH_OPEN0830_JUDAS_3R | 100 | 6.387951 | True | True | False | False |
| ICT3_5m_BOTH_OPEN0830_JUDAS_TIME | 100 | 5.178469 | True | True | False | False |
| ICT1_5m_BULL_LONG_ON_REVERSAL_2R | 39 | 3.999813 | True | False | False | False |
| ICT1_5m_BULL_LONG_ON_REVERSAL_3R | 39 | 2.257128 | False | False | False | False |
| ICT1_5m_BULL_LONG_ON_REVERSAL_OPPOSITE_ON | 38 | 2.010058 | True | False | False | False |
| ICT1_5m_BULL_LONG_PRE_REVERSAL_2R | 88 | 2.130821 | True | False | False | False |
| ICT1_5m_BULL_LONG_PRE_REVERSAL_3R | 88 | -0.016036 | False | False | False | False |
| ICT1_5m_BULL_LONG_PRE_REVERSAL_OPPOSITE_ON | 60 | 0.454017 | False | False | False | False |
| ICT2_5m_BULL_LONG_AM_FADE_2R | 49 | 0.806786 | False | False | False | False |
| ICT2_5m_BULL_LONG_AM_FADE_3R | 49 | 1.907358 | True | False | True | False |
| ICT2_5m_BULL_LONG_AM_CONTINUE_2R | 26 | 0.653887 | True | False | True | False |
| ICT2_5m_BULL_LONG_AM_CONTINUE_3R | 26 | 0.099561 | False | False | False | False |
| ICT2_5m_BULL_LONG_PM_FADE_2R | 32 | 0.212306 | False | False | False | False |
| ICT2_5m_BULL_LONG_PM_FADE_3R | 32 | 0.244495 | False | False | False | False |
| ICT2_5m_BULL_LONG_PM_CONTINUE_2R | 23 | 0.956800 | True | False | True | False |
| ICT2_5m_BULL_LONG_PM_CONTINUE_3R | 23 | 1.103979 | True | False | True | False |
| ICT3_5m_BULL_LONG_OPEN0930_JUDAS_2R | 57 | 4.013209 | True | True | True | False |
| ICT3_5m_BULL_LONG_OPEN0930_JUDAS_3R | 57 | 4.015738 | True | True | True | False |
| ICT3_5m_BULL_LONG_OPEN0930_JUDAS_TIME | 57 | 3.956909 | True | True | True | False |
| ICT3_5m_BULL_LONG_OPEN0830_JUDAS_2R | 73 | 5.337573 | True | False | True | False |
| ICT3_5m_BULL_LONG_OPEN0830_JUDAS_3R | 73 | 5.171717 | True | False | True | False |
| ICT3_5m_BULL_LONG_OPEN0830_JUDAS_TIME | 73 | 5.284796 | True | False | True | False |

Geen van deze beschrijvende labels is een onafhankelijke goedkeuring. Lagere handelsfrequentie, kortere stopafstand en een andere risiconoemer kunnen PF/stopR fraaier laten lijken zonder S1/S2 op vergelijkbare blootstelling te overtreffen.
