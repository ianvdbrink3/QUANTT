# Drie overlevers: vaste ATR-schaling en portefeuille

Status: EXPLORATORY_CONSUMED_DATA_ONLY — geen onafhankelijk bevestigd winstmodel. Beide bronnen zijn al gebruikt bij selectie. De oudere generieke bron blijft onbevestigd. ATR-schaling bewijst niet dat volatiliteit de eerdere p-waarde veroorzaakte.

1R = vooraf bekende ATR14, geen stop of verliesmaximum. NQ netto=(bruto−1,225)/ATR. Vaste derde per model, geen herverdeling van ongebruikt budget of kostennetting. Ontbrekende ATR geeft vooraf grootte nul, niet een achteraf berekende ATR. Alle435/493 kalenderdagen blijven in dagelijkse statistieken.

## Genormaliseerde NQ-resultaten

| Bron | Model | Trades met ATR / origineel | Netto R | DD dag / minuut R | Sharpe | 95% CI gemiddelde R/dag | Holm8 p |
|---|---|---:|---:|---:|---:|---|---:|
| DISCOVERY | TOM_RTH | 78 / 81 | 8.5118 | 4.9774 / 5.5256 | 1.099 | [-0.00833; 0.04327] | 0.9533 |
| DISCOVERY | COMPRESSED_BREAK5 | 109 / 109 | 2.3116 | 3.6366 / 3.9888 | 0.433 | [-0.01263; 0.02226] | 1.0000 |
| DISCOVERY | SWEEP_REV_1200 | 62 / 63 | 2.3975 | 1.7836 / 2.0824 | 0.548 | [-0.00327; 0.01520] | 1.0000 |
| DISCOVERY | PORTFOLIO_EQUAL_THIRD | vaste1/3 | 4.4069 | 1.9797 / 2.2255 | 1.278 | [-0.00141; 0.02029] | 0.5647 |
| CONTINUOUS_2022_2024_UNVERIFIED | TOM_RTH | 86 / 90 | 7.4241 | 3.7564 / 4.2403 | 0.963 | [-0.00961; 0.03712] | 1.0000 |
| CONTINUOUS_2022_2024_UNVERIFIED | COMPRESSED_BREAK5 | 106 / 106 | 4.5384 | 3.8433 / 4.9125 | 0.543 | [-0.01536; 0.02597] | 1.0000 |
| CONTINUOUS_2022_2024_UNVERIFIED | SWEEP_REV_1200 | 69 / 70 | 0.6974 | 3.0932 / 3.4698 | 0.165 | [-0.00997; 0.01403] | 1.0000 |
| CONTINUOUS_2022_2024_UNVERIFIED | PORTFOLIO_EQUAL_THIRD | vaste1/3 | 4.2200 | 1.8759 / 1.9811 | 1.060 | [-0.00378; 0.01816] | 0.9533 |

Sharpe = √252 × gemiddelde dagelijkse P&L in R / dagelijkse SD; geen account-ROI. Drawdown vanaf nul, markering op minuutclose met volledige RT-kosten bij entry; geen tick-worst-case. CI:10.000 gezamenlijke2-maands clusterbootstrap, nominaal95%, weinig maanden en stationariteit zijn beperkingen. Holm8 corrigeert alleen deze ronde, niet alle voorafgaande selectie.

## Dagcorrelaties (NQ netto R, inclusief nul-dagen)

| Bron | ToM–Compressie | ToM–Sweep | Compressie–Sweep | ATR-ready / alle dagen |
|---|---:|---:|---:|---:|
| DISCOVERY | -0.011 | 0.051 | -0.065 | 418 / 435 |
| CONTINUOUS_2022_2024_UNVERIFIED | -0.029 | 0.007 | -0.019 | 477 / 493 |

## MNQ-equivalent: vast rekenbudget $1.000 per ATR

Voorlopige kosten $6,50 per MNQ RT: $4,50 commissie/fees (onbevestigde aanname) +2ticks slippage per kant ($2). Niet $24,50/10. NQ-prijzen als proxy, geen MNQ-executiebewijs. Deelbaar: q=1000/(2×ATR), of1000/(3×2×ATR) per portefeuillesleeve. Geheel: floor(q), ook nul. Geen minimumcontract of achteraf verhoogd budget.

| Bron | Variant | Model | Contract-RT som | Netto $ | Minuut-DD $ | Sharpe |
|---|---|---|---:|---:|---:|---:|
| DISCOVERY | MNQ_FRACTIONAL | TOM_RTH | 107.331 | 8077.07 | 5709.35 | 1.044 |
| DISCOVERY | MNQ_FRACTIONAL | COMPRESSED_BREAK5 | 130.868 | 1781.54 | 4052.14 | 0.334 |
| DISCOVERY | MNQ_FRACTIONAL | SWEEP_REV_1200 | 84.393 | 2055.74 | 2196.54 | 0.470 |
| DISCOVERY | MNQ_FRACTIONAL | PORTFOLIO_EQUAL_THIRD | 107.530 | 3971.45 | 2402.38 | 1.152 |
| DISCOVERY | MNQ_INTEGER | TOM_RTH | 73.000 | 5366.00 | 4521.00 | 0.946 |
| DISCOVERY | MNQ_INTEGER | COMPRESSED_BREAK5 | 77.000 | -63.50 | 2832.00 | -0.017 |
| DISCOVERY | MNQ_INTEGER | SWEEP_REV_1200 | 55.000 | 2319.50 | 1603.50 | 0.657 |
| DISCOVERY | MNQ_INTEGER | PORTFOLIO_EQUAL_THIRD | 0.000 | 0.00 | 0.00 | n.v.t. |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_FRACTIONAL | TOM_RTH | 185.114 | 6674.38 | 4316.68 | 0.867 |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_FRACTIONAL | COMPRESSED_BREAK5 | 215.962 | 3663.80 | 5252.88 | 0.439 |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_FRACTIONAL | SWEEP_REV_1200 | 144.242 | 113.27 | 3614.27 | 0.027 |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_FRACTIONAL | PORTFOLIO_EQUAL_THIRD | 181.773 | 3483.81 | 2100.83 | 0.876 |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_INTEGER | TOM_RTH | 147.000 | 4280.00 | 3396.50 | 0.684 |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_INTEGER | COMPRESSED_BREAK5 | 171.000 | 2854.00 | 4760.00 | 0.402 |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_INTEGER | SWEEP_REV_1200 | 109.000 | 156.00 | 2987.00 | 0.049 |
| CONTINUOUS_2022_2024_UNVERIFIED | MNQ_INTEGER | PORTFOLIO_EQUAL_THIRD | 5.000 | -113.00 | 544.00 | -0.222 |

Deelbare contracten zijn niet verhandelbaar. Voor2019 vóór6mei bestaat alleen een hypothetisch MNQ-equivalent; MNQ was toen nog niet gelanceerd. Geen conclusie over marge, accountomvang, risicoacceptatie of toekomstige winst.

## Registratie en scheiding

De drie oorspronkelijke signalen plus vaste combinatie zijn apart geregistreerd voor2019–2021. De8 eerder bekeken januari2019-sessies blijven expliciet ontdekt; alleen het restant vanaf14januari kan nog een nieuwe uitkomsttoets vormen. Geen nieuwe2019–2021-signalen of rendementen in deze ronde berekend. Geen push of productiepublicatie.
