# Asymmetrisch regime-model: ontwikkelingsverkenning

EXPLORATORY_DEVELOPMENT_NOT_INDEPENDENT_VALIDATION

Pool: 1168sessies; 1151met vooraf bekende ATR. 1onbepaalbare eersteOCO-richtingen, 2dagen zonder limietfill. Geen onafhankelijke bevestiging, geen parameterzoektocht.

| Model | N | Bruto pt | Netto pt | Winrate | PF | Max DD pt | Positieve handelskwartalen |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_FIXED | 99 | -1606.250 | -1727.525 | 43.4343% | 0.7220 | 2943.425 | 8/19 |
| A_BREAKEVEN | 99 | -1625.000 | -1746.275 | 41.4141% | 0.7104 | 3073.925 | 7/19 |
| B_FADE | 663 | -98.250 | -910.425 | 63.8009% | 0.9451 | 2877.200 | 6/19 |
| A_FIXED_PLUS_B | 762 | -1704.500 | -2637.950 | 61.1549% | 0.8842 | 4342.225 | 5/19 |
| A_BREAKEVEN_PLUS_B | 762 | -1723.250 | -2656.700 | 60.8924% | 0.8825 | 4360.975 | 6/19 |

| Kwartaal | A vast | A breakeven | B fade | A vast+B | A breakeven+B |
|---|---:|---:|---:|---:|---:|
| 2019Q1 | +226.625 | +226.625 | -233.125 | -6.500 | -6.500 |
| 2019Q2 | +193.425 | +193.425 | -9.825 | +183.600 | +183.600 |
| 2019Q3 | -158.400 | -116.150 | -364.800 | -523.200 | -480.950 |
| 2019Q4 | -38.900 | -38.900 | -164.725 | -203.625 | -203.625 |
| 2020Q1 | +40.475 | +40.475 | +74.100 | +114.575 | +114.575 |
| 2020Q2 | -30.700 | -30.700 | -640.325 | -671.025 | -671.025 |
| 2020Q3 | -218.850 | -132.100 | -33.825 | -252.675 | -165.925 |
| 2020Q4 | +134.550 | +134.550 | -488.550 | -354.000 | -354.000 |
| 2021Q1 | -319.875 | -337.125 | +40.725 | -279.150 | -296.400 |
| 2021Q2 | +36.625 | +36.625 | -236.800 | -200.175 | -200.175 |
| 2021Q3 | +24.375 | +24.375 | -83.625 | -59.250 | -59.250 |
| 2021Q4 | -63.875 | -63.875 | -149.150 | -213.025 | -213.025 |
| 2024Q4 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| 2025Q1 | +204.900 | +204.900 | -369.050 | -164.150 | -164.150 |
| 2025Q2 | +49.800 | -137.700 | +648.175 | +697.975 | +510.475 |
| 2025Q3 | -643.775 | -643.775 | -372.475 | -1016.250 | -1016.250 |
| 2025Q4 | -483.375 | -483.375 | -87.625 | -571.000 | -571.000 |
| 2026Q1 | -186.075 | -129.075 | +167.000 | -19.075 | +37.925 |
| 2026Q2 | -147.075 | -147.075 | +320.625 | +173.550 | +173.550 |
| 2026Q3 | -347.400 | -347.400 | +1072.850 | +725.450 | +725.450 |

## Vooraf vastgelegde uitvoeringsaannames

- date: 2026-10-24
- status: EXPLORATORY_CONSUMED_DEVELOPMENT_POOL
- sample: Exactly previously released733 historical sessions2019Jan14-2021Dec31 plus435 complete recent sessions2024Dec30-2026Sep30; no2022-24 generic source and no first8 historical dates added.
- regime: At10:00, only completed09:30..09:59 bars plus prior-knownATR14. A: range30>0.60ATR and09:59close strictly outside first15range, direction outward. B: range30<0.40ATR. Boundaries and intermediate regimes idle.
- A: Enter10:00open, stop0.5ATR, exit15:45open. Separately registered alternative moves stop to entry after completed bar reaches+1.0ATR; activation next bar only, initial stop takes priority in activation bar.
- B: From10:00 resting OCO sell limit H30 or buy limit L30; first identifiable side only, max1trade/day, stop0.35ATR from fill, target09:30open, unfilled orders canceled/position flat15:45open.
- limits: Require1tick trade-through to certify resting entry/target fill, no favorable price improvement. An order marketable at minute open is filled conservatively at its limit. If both OCO entries first cross inside the same minute with neither established at open, mark UNKNOWN_FIRST_OCO and leave its P&L unavailable, never choose a future-profitable side.
- conflicts: Position at bar open: adverse stop before target if both reachable. Intrabar limit-entry bar: stop counts; target only if entry established at open or closing beyond target proves post-entry crossing. Otherwise do not credit unproven target in entry bar.
- risk: 1NQ/filled trade. 1R=initial entry-stop distance, not account-risk budget. Stops rounded toward entry to0.25tick, trigger+ATR rounded away from entry; gap-through stop at adverse bar open can lose more than1R. No artificial loss cap.
- costs: Fixed$24.50NQ RT=1.225points per filled trade, no additional slippage subtraction or netting credits.
- reporting: Only pooled performance, N=filled trades, gross/netpoints, net winrate/PF, maximum marked drawdown and every quarter. DD on chronological minute opens/closes and known stop/target fills; not worst-tick DD. A+B is regime switching with1contract, not optimized weights.
- ambiguity: UNKNOWN_FIRST_OCO days are explicitly unavailable for B and combined models, not zero-return trades. Report their count and exclude from simulated P&L; full-pool performance would remain unidentified if any occur.
- restrictions: No optimization, pvalue fishing, new independent-validation claim, purchases, Git commit/push or deployment. Preserve all earlier bytes.
