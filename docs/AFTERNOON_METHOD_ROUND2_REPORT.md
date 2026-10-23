# Conservatieve methoderonde 2

CALIBRATION_SCREEN_PASSED_LIMITED_SCOPE_NOT_MARKET_VALIDATION

720,000 synthetische panels; 0/396 gelijktijdige bovengrenzen boven 6%; maximum 5.26%.

De vaste variantiefactor 1,25 is vóór de nieuwe seeds vastgelegd: SE × sqrt(1,25). Geen wijziging aan cohort, kosten, horizons, kandidaat v2 of het historische testvenster. Alpha blijft 5%; 6% blijft uitsluitend de numerieke screentolerantie. Geen marktuitkomsten gelezen.

## Diagnose ronde 1

Een overschreden Monte-Carlo-bovengrens is niet automatisch bewijs van werkelijke alpha-inflatie. Het JSON bevat per falende cel ook een simultane ondergrens: alleen boven 5% heet bewijs van inflatie. De analytische AR(0,95)-variantieverhouding (maximum 1,2029) toont daarnaast concrete restafhankelijkheid; dit is geen geschatte NQ-correlatie.

## Powerprijs bij 783 weekdagen

| Model | Netto-effect 2m/15m | SD-factor | Oude power % | Conservatieve power % |
|---|---|---:|---:|---:|
| GAUSSIAN_IID | [4, 0] | 1 | 89.79 | 83.46 |
| GAUSSIAN_IID | [4, 0] | 1.5 | 55.70 | 44.96 |
| GAUSSIAN_IID | [0, 4] | 1 | 19.25 | 13.77 |
| GAUSSIAN_IID | [0, 4] | 1.5 | 9.43 | 6.68 |
| MA19 | [4, 0] | 1 | 18.73 | 13.09 |
| MA19 | [4, 0] | 1.5 | 8.73 | 5.62 |
| MA19 | [0, 4] | 1 | 4.06 | 2.53 |
| MA19 | [0, 4] | 1.5 | 2.70 | 1.67 |
| AR095 | [4, 0] | 1 | 13.59 | 9.55 |
| AR095 | [4, 0] | 1.5 | 7.58 | 5.01 |
| AR095 | [0, 4] | 1 | 4.12 | 2.69 |
| AR095 | [0, 4] | 1.5 | 3.07 | 1.87 |

Dit is een beperkte synthetische schermtest, geen universele eindige-steekproefgarantie. De niet-mengende negatieve controle wordt apart zichtbaar gehouden. Ook bij een geslaagde schermtest blijft een expliciet inferentie-addendum nodig vóór een onafhankelijke markttest. De bevroren specificatie wordt niet stil aangepast.
