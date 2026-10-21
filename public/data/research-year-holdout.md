# Jaar-holdout ORB15 — vaste regels, één primaire hypothese

**Formeel oordeel: HOLDOUT_FAILED.** Alleen ORB15, all-view, over 1 oktober 2025–30 september 2026 bepaalt dit oordeel. Geen parameterwijzigingen. De jaar-holdout is nu verbruikt.

Baseline v0.9 en de vNext159-onderzoeksstand blijven ongewijzigd. Gecombineerde historie en referenties zijn uitsluitend beschrijvend. Een positief resultaat is geen toestemming voor live handelen.

## Primaire vooraf vastgelegde criteria

| Criterium | Gehaald |
|---|---|
| sample_size | Ja |
| net_profit | Nee |
| profit_factor | Nee |
| positive_95pct_lower_bound | Nee |
| significant_primary_test | Nee |

Alle vijf criteria moeten slagen: ≥20 eligible dagen, netto >0, PF >1, tweezijdige block-bootstrap-p <0,05 en de ondergrens van het 95%-interval van het gemiddelde dagresultaat >0. Geen vervanging door gecombineerd resultaat of beste referentie.

## Jaar-holdout: 1 oktober 2025–30 september 2026

| Maatstaf | ORB15 primair | ORB5 referentie | London referentie | VWAP referentie |
|---|---:|---:|---:|---:|
| Eligible dagen | 249 | 249 | 249 | 249 |
| Trades | 216 | 225 | 113 | 77 |
| Netto NQ-punten | -616,350 | 161,625 | -526,675 | -124,825 |
| Netto USD | -12.327,000 | 3.232,500 | -10.533,500 | -2.496,500 |
| Profit factor | 0,946 | 1,014 | 0,923 | 0,958 |
| Maximale gesloten-trade drawdown (punten) | 1.896,175 | 2.234,725 | 1.609,675 | 737,375 |
| Maximale gesloten-trade drawdown (USD) | 37.923,500 | 44.694,500 | 32.193,500 | 14.747,500 |
| Grootste verliesdag (punten) | -220,975 | -220,975 | -220,975 | -184,475 |
| Grootste verliesdag (USD) | -4.419,500 | -4.419,500 | -4.419,500 | -3.689,500 |
| Top3 netto punten | 849,575 | 999,825 | 887,575 | 677,075 |
| Top3 / totale netto winst (%) | n.v.t. | 618,608 | n.v.t. | n.v.t. |
| Netto zonder top3 (punten) | -1.465,925 | -838,200 | -1.414,250 | -801,900 |
| 95%CI gemiddeld netto punten/eligible dag: laag | -16,117 | -16,285 | -12,753 | -5,537 |
| 95%CI gemiddeld netto punten/eligible dag: hoog | 11,322 | 17,018 | 8,830 | 5,027 |
| Tweezijdige p (nominaal) | 0,726637 | 0,942529 | 0,686657 | 0,864068 |
| Winrate | 44,4% | 43,1% | 38,1% | 40,3% |
| Datum grootste verliesdag | 2026-06-29 | 2026-06-29 | 2026-06-29 | 2026-07-02 |
| p na Holm, aanvullende familie8 | n.v.t. | 1,000000 | 1,000000 | 1,000000 |

Top3-aandeel is niet gedefinieerd bij nettoverlies of netto nul. Een aandeel boven100% wordt niet afgekapt. Grootste verliesdag is het minimum over alle eligible dagen inclusief nultrade-dagen. Drawdown gebruikt gerealiseerde gesloten trades met startwaarde0, niet intratrade mark-to-market.

### Maandverdeling

| Model | Maand | Eligible | Trades | Netto punten | Netto USD | Winrate | PF |
|---|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | 2025-10 | 23 | 19 | -286,025 | -5.720,50 | 36,8% | 0,650 |
| ORB15 (primair) | 2025-11 | 19 | 17 | 105,925 | 2.118,50 | 47,1% | 1,110 |
| ORB15 (primair) | 2025-12 | 20 | 17 | -350,575 | -7.011,50 | 41,2% | 0,606 |
| ORB15 (primair) | 2026-01 | 20 | 18 | -140,300 | -2.806,00 | 38,9% | 0,824 |
| ORB15 (primair) | 2026-02 | 19 | 19 | 654,975 | 13.099,50 | 57,9% | 1,734 |
| ORB15 (primair) | 2026-03 | 21 | 18 | -614,800 | -12.296,00 | 33,3% | 0,426 |
| ORB15 (primair) | 2026-04 | 20 | 18 | 141,200 | 2.824,00 | 55,6% | 1,220 |
| ORB15 (primair) | 2026-05 | 21 | 20 | -773,500 | -15.470,00 | 30,0% | 0,439 |
| ORB15 (primair) | 2026-06 | 21 | 18 | -62,800 | -1.256,00 | 44,4% | 0,950 |
| ORB15 (primair) | 2026-07 | 22 | 20 | 660,500 | 13.210,00 | 60,0% | 1,543 |
| ORB15 (primair) | 2026-08 | 21 | 14 | -238,150 | -4.763,00 | 35,7% | 0,708 |
| ORB15 (primair) | 2026-09 | 22 | 18 | 287,200 | 5.744,00 | 50,0% | 1,465 |
| ORB5 (referentie) | 2025-10 | 23 | 22 | -473,950 | -9.479,00 | 36,4% | 0,519 |
| ORB5 (referentie) | 2025-11 | 19 | 18 | 850,950 | 17.019,00 | 55,6% | 2,032 |
| ORB5 (referentie) | 2025-12 | 20 | 18 | 2,450 | 49,00 | 44,4% | 1,003 |
| ORB5 (referentie) | 2026-01 | 20 | 18 | 231,450 | 4.629,00 | 50,0% | 1,393 |
| ORB5 (referentie) | 2026-02 | 19 | 19 | 1.054,975 | 21.099,50 | 57,9% | 2,200 |
| ORB5 (referentie) | 2026-03 | 21 | 18 | -550,550 | -11.011,00 | 33,3% | 0,486 |
| ORB5 (referentie) | 2026-04 | 20 | 19 | -358,525 | -7.170,50 | 47,4% | 0,593 |
| ORB5 (referentie) | 2026-05 | 21 | 20 | -466,000 | -9.320,00 | 30,0% | 0,644 |
| ORB5 (referentie) | 2026-06 | 21 | 18 | 127,700 | 2.554,00 | 44,4% | 1,101 |
| ORB5 (referentie) | 2026-07 | 22 | 20 | 348,500 | 6.970,00 | 50,0% | 1,224 |
| ORB5 (referentie) | 2026-08 | 21 | 17 | -748,325 | -14.966,50 | 23,5% | 0,361 |
| ORB5 (referentie) | 2026-09 | 22 | 18 | 142,950 | 2.859,00 | 44,4% | 1,240 |
| London Sweep (referentie) | 2025-10 | 23 | 9 | -20,775 | -415,50 | 44,4% | 0,947 |
| London Sweep (referentie) | 2025-11 | 19 | 6 | 8,150 | 163,00 | 50,0% | 1,021 |
| London Sweep (referentie) | 2025-12 | 20 | 14 | 151,350 | 3.027,00 | 50,0% | 1,328 |
| London Sweep (referentie) | 2026-01 | 20 | 12 | -16,950 | -339,00 | 33,3% | 0,971 |
| London Sweep (referentie) | 2026-02 | 19 | 11 | 744,775 | 14.895,50 | 54,5% | 2,853 |
| London Sweep (referentie) | 2026-03 | 21 | 6 | -374,850 | -7.497,00 | 16,7% | 0,290 |
| London Sweep (referentie) | 2026-04 | 20 | 7 | -387,075 | -7.741,50 | 28,6% | 0,326 |
| London Sweep (referentie) | 2026-05 | 21 | 10 | -317,750 | -6.355,00 | 30,0% | 0,610 |
| London Sweep (referentie) | 2026-06 | 21 | 11 | 148,275 | 2.965,50 | 45,5% | 1,156 |
| London Sweep (referentie) | 2026-07 | 22 | 8 | -467,550 | -9.351,00 | 25,0% | 0,445 |
| London Sweep (referentie) | 2026-08 | 21 | 12 | -74,950 | -1.499,00 | 25,0% | 0,852 |
| London Sweep (referentie) | 2026-09 | 22 | 7 | 80,675 | 1.613,50 | 42,9% | 1,209 |
| VWAP Extreme (referentie) | 2025-10 | 23 | 6 | -94,100 | -1.882,00 | 33,3% | 0,623 |
| VWAP Extreme (referentie) | 2025-11 | 19 | 6 | 48,150 | 963,00 | 33,3% | 1,161 |
| VWAP Extreme (referentie) | 2025-12 | 20 | 7 | 38,675 | 773,50 | 57,1% | 1,155 |
| VWAP Extreme (referentie) | 2026-01 | 20 | 8 | -375,800 | -7.516,00 | 12,5% | 0,175 |
| VWAP Extreme (referentie) | 2026-02 | 19 | 8 | -140,300 | -2.806,00 | 25,0% | 0,591 |
| VWAP Extreme (referentie) | 2026-03 | 21 | 6 | 267,650 | 5.353,00 | 50,0% | 7,704 |
| VWAP Extreme (referentie) | 2026-04 | 20 | 9 | 204,225 | 4.084,50 | 66,7% | 2,238 |
| VWAP Extreme (referentie) | 2026-05 | 21 | 9 | 26,975 | 539,50 | 44,4% | 1,110 |
| VWAP Extreme (referentie) | 2026-06 | 21 | 5 | 169,375 | 3.387,50 | 40,0% | 1,513 |
| VWAP Extreme (referentie) | 2026-07 | 22 | 6 | -89,350 | -1.787,00 | 33,3% | 0,735 |
| VWAP Extreme (referentie) | 2026-08 | 21 | 3 | -194,675 | -3.893,50 | 0,0% | 0,000 |
| VWAP Extreme (referentie) | 2026-09 | 22 | 4 | 14,350 | 287,00 | 75,0% | 1,170 |

### Long versus short

| Model | Richting | Trades | Netto punten | Netto USD | Winrate | PF | Gemiddelde trade |
|---|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | long | 101 | 612,775 | 12.255,50 | 51,5% | 1,139 | 6,067 |
| ORB15 (primair) | short | 115 | -1.229,125 | -24.582,50 | 38,3% | 0,823 | -10,688 |
| ORB5 (referentie) | long | 107 | 222,175 | 4.443,50 | 46,7% | 1,044 | 2,076 |
| ORB5 (referentie) | short | 118 | -60,550 | -1.211,00 | 39,8% | 0,991 | -0,513 |
| London Sweep (referentie) | long | 58 | 386,450 | 7.729,00 | 39,7% | 1,127 | 6,663 |
| London Sweep (referentie) | short | 55 | -913,125 | -18.262,50 | 36,4% | 0,759 | -16,602 |
| VWAP Extreme (referentie) | long | 41 | -319,225 | -6.384,50 | 43,9% | 0,838 | -7,786 |
| VWAP Extreme (referentie) | short | 36 | 194,400 | 3.888,00 | 36,1% | 1,190 | 5,400 |

### MFE/MAE-verdelingen

| Model | Maatstaf | n | P05 | P25 | Mediaan | P75 | P95 |
|---|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | MFE_R_lower | 216 | 0,056 | 0,278 | 0,709 | 1,213 | 2,004 |
| ORB15 (primair) | MFE_R_bar_upper | 216 | 0,056 | 0,278 | 0,709 | 1,213 | 2,004 |
| ORB15 (primair) | MAE_R_lower | 216 | 0,095 | 0,334 | 0,864 | 1,000 | 1,000 |
| ORB15 (primair) | MAE_R_bar_upper | 216 | 0,095 | 0,334 | 0,864 | 1,000 | 1,000 |
| ORB15 (primair) | MFE_points_lower | 216 | 5,625 | 31,938 | 75,625 | 145,500 | 230,750 |
| ORB15 (primair) | MFE_points_bar_upper | 216 | 5,625 | 31,938 | 75,625 | 145,500 | 230,750 |
| ORB15 (primair) | MAE_points_lower | 216 | 8,938 | 38,688 | 76,375 | 105,312 | 145,062 |
| ORB15 (primair) | MAE_points_bar_upper | 216 | 8,938 | 38,688 | 76,375 | 105,312 | 145,062 |
| ORB15 (primair) | MFE_first_bar_minute | 216 | 0,000 | 4,000 | 31,500 | 70,000 | 118,250 |
| ORB15 (primair) | MAE_first_bar_minute | 216 | 0,000 | 4,750 | 17,000 | 58,500 | 97,500 |
| ORB5 (referentie) | MFE_R_lower | 225 | 0,042 | 0,329 | 0,763 | 1,498 | 2,005 |
| ORB5 (referentie) | MFE_R_bar_upper | 225 | 0,042 | 0,329 | 0,763 | 1,498 | 2,005 |
| ORB5 (referentie) | MAE_R_lower | 225 | 0,100 | 0,374 | 0,796 | 1,000 | 1,000 |
| ORB5 (referentie) | MAE_R_bar_upper | 225 | 0,100 | 0,374 | 0,796 | 1,000 | 1,000 |
| ORB5 (referentie) | MFE_points_lower | 225 | 5,250 | 36,750 | 78,250 | 160,750 | 236,050 |
| ORB5 (referentie) | MFE_points_bar_upper | 225 | 5,250 | 36,750 | 78,250 | 160,750 | 236,050 |
| ORB5 (referentie) | MAE_points_lower | 225 | 9,600 | 39,500 | 75,250 | 104,750 | 153,500 |
| ORB5 (referentie) | MAE_points_bar_upper | 225 | 9,600 | 39,500 | 75,250 | 104,750 | 153,500 |
| ORB5 (referentie) | MFE_first_bar_minute | 225 | 0,000 | 6,000 | 30,000 | 69,000 | 121,000 |
| ORB5 (referentie) | MAE_first_bar_minute | 225 | 0,000 | 5,000 | 17,000 | 56,000 | 113,600 |
| London Sweep (referentie) | MFE_R_lower | 113 | 0,133 | 0,291 | 0,878 | 1,683 | 2,004 |
| London Sweep (referentie) | MFE_R_bar_upper | 113 | 0,133 | 0,291 | 0,878 | 1,683 | 2,004 |
| London Sweep (referentie) | MAE_R_lower | 113 | 0,063 | 0,323 | 0,932 | 1,000 | 1,000 |
| London Sweep (referentie) | MAE_R_bar_upper | 113 | 0,063 | 0,323 | 0,932 | 1,000 | 1,000 |
| London Sweep (referentie) | MFE_points_lower | 113 | 10,050 | 37,500 | 95,250 | 177,500 | 243,000 |
| London Sweep (referentie) | MFE_points_bar_upper | 113 | 10,050 | 37,500 | 95,250 | 177,500 | 243,000 |
| London Sweep (referentie) | MAE_points_lower | 113 | 6,000 | 35,250 | 83,500 | 106,750 | 172,350 |
| London Sweep (referentie) | MAE_points_bar_upper | 113 | 6,000 | 35,250 | 83,500 | 106,750 | 172,350 |
| London Sweep (referentie) | MFE_first_bar_minute | 113 | 0,000 | 9,000 | 29,000 | 79,000 | 125,600 |
| London Sweep (referentie) | MAE_first_bar_minute | 113 | 0,000 | 6,000 | 26,000 | 60,000 | 112,800 |
| VWAP Extreme (referentie) | MFE_R_lower | 77 | 0,010 | 0,235 | 0,564 | 0,945 | 1,448 |
| VWAP Extreme (referentie) | MFE_R_bar_upper | 77 | 0,048 | 0,235 | 0,564 | 0,945 | 1,448 |
| VWAP Extreme (referentie) | MAE_R_lower | 77 | 0,088 | 0,296 | 0,569 | 0,998 | 1,000 |
| VWAP Extreme (referentie) | MAE_R_bar_upper | 77 | 0,088 | 0,296 | 0,569 | 0,998 | 1,000 |
| VWAP Extreme (referentie) | MFE_points_lower | 77 | 0,950 | 28,250 | 60,750 | 103,250 | 172,200 |
| VWAP Extreme (referentie) | MFE_points_bar_upper | 77 | 4,000 | 28,250 | 60,750 | 103,250 | 172,200 |
| VWAP Extreme (referentie) | MAE_points_lower | 77 | 9,000 | 32,250 | 61,000 | 83,250 | 126,400 |
| VWAP Extreme (referentie) | MAE_points_bar_upper | 77 | 9,000 | 32,250 | 61,000 | 83,250 | 126,400 |
| VWAP Extreme (referentie) | MFE_first_bar_minute | 77 | 0,000 | 3,000 | 15,000 | 36,000 | 67,800 |
| VWAP Extreme (referentie) | MAE_first_bar_minute | 77 | 0,000 | 3,000 | 14,000 | 42,000 | 80,000 |

MFE/MAE zijn intrabar-identificatiegrenzen, geen exacte tickvolgorde. Lower gebruikt voltooide eerdere bars plus de fill; upper gebruikt de exitbar binnen de vaste stop-/targetbarrières. Bij tijdexit is de laatste volledige minuut bekend.1R=afstand entry tot initiële stop vóór kosten. Tijd tot eerste bar-extreem is in minuten en kan binnen de exitminuut na de fill liggen.

### Kosten-gevoeligheid, onveranderde fills

| Model | USD roundtrip | Netto punten | Netto USD | Winrate | PF | Max drawdown punten |
|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | 24,50 | -616,350 | -12.327,00 | 44,4% | 0,946 | 1.896,175 |
| ORB15 (primair) | 44,50 | -832,350 | -16.647,00 | 43,5% | 0,927 | 2.029,175 |
| ORB15 (primair) | 64,50 | -1.048,350 | -20.967,00 | 43,5% | 0,910 | 2.163,200 |
| ORB5 (referentie) | 24,50 | 161,625 | 3.232,50 | 43,1% | 1,014 | 2.234,725 |
| ORB5 (referentie) | 44,50 | -63,375 | -1.267,50 | 42,2% | 0,995 | 2.345,725 |
| ORB5 (referentie) | 64,50 | -288,375 | -5.767,50 | 42,2% | 0,976 | 2.456,725 |
| London Sweep (referentie) | 24,50 | -526,675 | -10.533,50 | 38,1% | 0,923 | 1.609,675 |
| London Sweep (referentie) | 44,50 | -639,675 | -12.793,50 | 38,1% | 0,907 | 1.662,675 |
| London Sweep (referentie) | 64,50 | -752,675 | -15.053,50 | 38,1% | 0,892 | 1.715,675 |
| VWAP Extreme (referentie) | 24,50 | -124,825 | -2.496,50 | 40,3% | 0,958 | 737,375 |
| VWAP Extreme (referentie) | 44,50 | -201,825 | -4.036,50 | 40,3% | 0,934 | 752,375 |
| VWAP Extreme (referentie) | 64,50 | -278,825 | -5.576,50 | 39,0% | 0,910 | 767,375 |

### Clean-sensitiviteit (niet beslissend)

| Model | Eligible | Trades | Netto punten | PF |
|---|---:|---:|---:|---:|
| ORB15 (primair) | 248 | 215 | -512,625 | 0,954 |
| ORB5 (referentie) | 248 | 224 | 265,350 | 1,022 |
| London Sweep (referentie) | 248 | 113 | -526,675 | 0,923 |
| VWAP Extreme (referentie) | 248 | 77 | -124,825 | 0,958 |

ORB15 clean:95%CI gemiddeld dagresultaat [-15,692,11,844], nominaal p=0,773613, Holm8 p=1,000000. Dit vervangt de primaire all-view niet.

## Gecombineerd: 30 december 2024–30 september 2026 (beschrijvend)

| Maatstaf | ORB15 primair | ORB5 referentie | London referentie | VWAP referentie |
|---|---:|---:|---:|---:|
| Eligible dagen | 408 | 408 | 408 | 408 |
| Trades | 359 | 372 | 195 | 140 |
| Netto NQ-punten | 467,225 | -240,450 | -351,125 | -29,000 |
| Netto USD | 9.344,500 | -4.809,000 | -7.022,500 | -580,000 |
| Profit factor | 1,028 | 0,987 | 0,966 | 0,994 |
| Maximale gesloten-trade drawdown (punten) | 2.102,775 | 2.234,725 | 1.609,675 | 804,650 |
| Maximale gesloten-trade drawdown (USD) | 42.055,500 | 44.694,500 | 32.193,500 | 16.093,000 |
| Grootste verliesdag (punten) | -236,225 | -236,225 | -220,975 | -184,475 |
| Grootste verliesdag (USD) | -4.724,500 | -4.724,500 | -4.419,500 | -3.689,500 |
| Top3 netto punten | 955,325 | 1.094,825 | 912,075 | 713,325 |
| Top3 / totale netto winst (%) | 204,468 | n.v.t. | n.v.t. | n.v.t. |
| Netto zonder top3 (punten) | -488,100 | -1.335,275 | -1.263,200 | -742,325 |
| 95%CI gemiddeld netto punten/eligible dag: laag | -8,868 | -12,346 | -8,895 | -4,242 |
| 95%CI gemiddeld netto punten/eligible dag: hoog | 11,335 | 11,267 | 7,737 | 4,076 |
| Tweezijdige p (nominaal) | 0,836082 | 0,928536 | 0,839080 | 0,978011 |
| Winrate | 45,4% | 41,9% | 40,0% | 46,4% |
| Datum grootste verliesdag | 2025-04-23 | 2025-04-23 | 2026-06-29 | 2026-07-02 |
| p na Holm, aanvullende familie8 | 1,000000 | 1,000000 | 1,000000 | 1,000000 |

Top3-aandeel is niet gedefinieerd bij nettoverlies of netto nul. Een aandeel boven100% wordt niet afgekapt. Grootste verliesdag is het minimum over alle eligible dagen inclusief nultrade-dagen. Drawdown gebruikt gerealiseerde gesloten trades met startwaarde0, niet intratrade mark-to-market.

### Maandverdeling

| Model | Maand | Eligible | Trades | Netto punten | Netto USD | Winrate | PF |
|---|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | 2024-12 | 0 | 0 | 0,000 | 0,00 | n.v.t. | n.v.t. |
| ORB15 (primair) | 2025-01 | 5 | 5 | -2,375 | -47,50 | 60,0% | 0,987 |
| ORB15 (primair) | 2025-02 | 18 | 17 | 593,175 | 11.863,50 | 58,8% | 2,314 |
| ORB15 (primair) | 2025-03 | 19 | 16 | 90,900 | 1.818,00 | 43,8% | 1,109 |
| ORB15 (primair) | 2025-04 | 19 | 15 | 738,125 | 14.762,50 | 60,0% | 2,008 |
| ORB15 (primair) | 2025-05 | 21 | 19 | -144,025 | -2.880,50 | 36,8% | 0,823 |
| ORB15 (primair) | 2025-06 | 20 | 16 | 12,150 | 243,00 | 56,2% | 1,027 |
| ORB15 (primair) | 2025-07 | 20 | 19 | -157,275 | -3.145,50 | 31,6% | 0,732 |
| ORB15 (primair) | 2025-08 | 19 | 19 | -43,275 | -865,50 | 47,4% | 0,936 |
| ORB15 (primair) | 2025-09 | 18 | 17 | -3,825 | -76,50 | 41,2% | 0,991 |
| ORB15 (primair) | 2025-10 | 23 | 19 | -286,025 | -5.720,50 | 36,8% | 0,650 |
| ORB15 (primair) | 2025-11 | 19 | 17 | 105,925 | 2.118,50 | 47,1% | 1,110 |
| ORB15 (primair) | 2025-12 | 20 | 17 | -350,575 | -7.011,50 | 41,2% | 0,606 |
| ORB15 (primair) | 2026-01 | 20 | 18 | -140,300 | -2.806,00 | 38,9% | 0,824 |
| ORB15 (primair) | 2026-02 | 19 | 19 | 654,975 | 13.099,50 | 57,9% | 1,734 |
| ORB15 (primair) | 2026-03 | 21 | 18 | -614,800 | -12.296,00 | 33,3% | 0,426 |
| ORB15 (primair) | 2026-04 | 20 | 18 | 141,200 | 2.824,00 | 55,6% | 1,220 |
| ORB15 (primair) | 2026-05 | 21 | 20 | -773,500 | -15.470,00 | 30,0% | 0,439 |
| ORB15 (primair) | 2026-06 | 21 | 18 | -62,800 | -1.256,00 | 44,4% | 0,950 |
| ORB15 (primair) | 2026-07 | 22 | 20 | 660,500 | 13.210,00 | 60,0% | 1,543 |
| ORB15 (primair) | 2026-08 | 21 | 14 | -238,150 | -4.763,00 | 35,7% | 0,708 |
| ORB15 (primair) | 2026-09 | 22 | 18 | 287,200 | 5.744,00 | 50,0% | 1,465 |
| ORB5 (referentie) | 2024-12 | 0 | 0 | 0,000 | 0,00 | n.v.t. | n.v.t. |
| ORB5 (referentie) | 2025-01 | 5 | 5 | -207,125 | -4.142,50 | 40,0% | 0,278 |
| ORB5 (referentie) | 2025-02 | 18 | 17 | 704,175 | 14.083,50 | 58,8% | 2,559 |
| ORB5 (referentie) | 2025-03 | 19 | 16 | -294,850 | -5.897,00 | 31,2% | 0,721 |
| ORB5 (referentie) | 2025-04 | 19 | 16 | -238,850 | -4.777,00 | 37,5% | 0,800 |
| ORB5 (referentie) | 2025-05 | 21 | 19 | -92,775 | -1.855,50 | 31,6% | 0,889 |
| ORB5 (referentie) | 2025-06 | 20 | 19 | -296,275 | -5.925,50 | 36,8% | 0,626 |
| ORB5 (referentie) | 2025-07 | 20 | 19 | -93,775 | -1.875,50 | 31,6% | 0,850 |
| ORB5 (referentie) | 2025-08 | 19 | 19 | 420,975 | 8.419,50 | 57,9% | 1,761 |
| ORB5 (referentie) | 2025-09 | 18 | 17 | -303,575 | -6.071,50 | 35,3% | 0,509 |
| ORB5 (referentie) | 2025-10 | 23 | 22 | -473,950 | -9.479,00 | 36,4% | 0,519 |
| ORB5 (referentie) | 2025-11 | 19 | 18 | 850,950 | 17.019,00 | 55,6% | 2,032 |
| ORB5 (referentie) | 2025-12 | 20 | 18 | 2,450 | 49,00 | 44,4% | 1,003 |
| ORB5 (referentie) | 2026-01 | 20 | 18 | 231,450 | 4.629,00 | 50,0% | 1,393 |
| ORB5 (referentie) | 2026-02 | 19 | 19 | 1.054,975 | 21.099,50 | 57,9% | 2,200 |
| ORB5 (referentie) | 2026-03 | 21 | 18 | -550,550 | -11.011,00 | 33,3% | 0,486 |
| ORB5 (referentie) | 2026-04 | 20 | 19 | -358,525 | -7.170,50 | 47,4% | 0,593 |
| ORB5 (referentie) | 2026-05 | 21 | 20 | -466,000 | -9.320,00 | 30,0% | 0,644 |
| ORB5 (referentie) | 2026-06 | 21 | 18 | 127,700 | 2.554,00 | 44,4% | 1,101 |
| ORB5 (referentie) | 2026-07 | 22 | 20 | 348,500 | 6.970,00 | 50,0% | 1,224 |
| ORB5 (referentie) | 2026-08 | 21 | 17 | -748,325 | -14.966,50 | 23,5% | 0,361 |
| ORB5 (referentie) | 2026-09 | 22 | 18 | 142,950 | 2.859,00 | 44,4% | 1,240 |
| London Sweep (referentie) | 2024-12 | 0 | 0 | 0,000 | 0,00 | n.v.t. | n.v.t. |
| London Sweep (referentie) | 2025-01 | 5 | 2 | 359,300 | 7.186,00 | 100,0% | ∞ (geen verlies) |
| London Sweep (referentie) | 2025-02 | 18 | 9 | 35,475 | 709,50 | 44,4% | 1,080 |
| London Sweep (referentie) | 2025-03 | 19 | 11 | -938,475 | -18.769,50 | 9,1% | 0,162 |
| London Sweep (referentie) | 2025-04 | 19 | 5 | 643,375 | 12.867,50 | 100,0% | ∞ (geen verlies) |
| London Sweep (referentie) | 2025-05 | 21 | 6 | 18,650 | 373,00 | 50,0% | 1,101 |
| London Sweep (referentie) | 2025-06 | 20 | 12 | 157,050 | 3.141,00 | 50,0% | 1,436 |
| London Sweep (referentie) | 2025-07 | 20 | 16 | 267,400 | 5.348,00 | 50,0% | 1,590 |
| London Sweep (referentie) | 2025-08 | 19 | 10 | -44,250 | -885,00 | 40,0% | 0,890 |
| London Sweep (referentie) | 2025-09 | 18 | 11 | -322,975 | -6.459,50 | 18,2% | 0,295 |
| London Sweep (referentie) | 2025-10 | 23 | 9 | -20,775 | -415,50 | 44,4% | 0,947 |
| London Sweep (referentie) | 2025-11 | 19 | 6 | 8,150 | 163,00 | 50,0% | 1,021 |
| London Sweep (referentie) | 2025-12 | 20 | 14 | 151,350 | 3.027,00 | 50,0% | 1,328 |
| London Sweep (referentie) | 2026-01 | 20 | 12 | -16,950 | -339,00 | 33,3% | 0,971 |
| London Sweep (referentie) | 2026-02 | 19 | 11 | 744,775 | 14.895,50 | 54,5% | 2,853 |
| London Sweep (referentie) | 2026-03 | 21 | 6 | -374,850 | -7.497,00 | 16,7% | 0,290 |
| London Sweep (referentie) | 2026-04 | 20 | 7 | -387,075 | -7.741,50 | 28,6% | 0,326 |
| London Sweep (referentie) | 2026-05 | 21 | 10 | -317,750 | -6.355,00 | 30,0% | 0,610 |
| London Sweep (referentie) | 2026-06 | 21 | 11 | 148,275 | 2.965,50 | 45,5% | 1,156 |
| London Sweep (referentie) | 2026-07 | 22 | 8 | -467,550 | -9.351,00 | 25,0% | 0,445 |
| London Sweep (referentie) | 2026-08 | 21 | 12 | -74,950 | -1.499,00 | 25,0% | 0,852 |
| London Sweep (referentie) | 2026-09 | 22 | 7 | 80,675 | 1.613,50 | 42,9% | 1,209 |
| VWAP Extreme (referentie) | 2024-12 | 0 | 0 | 0,000 | 0,00 | n.v.t. | n.v.t. |
| VWAP Extreme (referentie) | 2025-01 | 5 | 2 | -101,450 | -2.029,00 | 0,0% | 0,000 |
| VWAP Extreme (referentie) | 2025-02 | 18 | 10 | 119,500 | 2.390,00 | 60,0% | 1,493 |
| VWAP Extreme (referentie) | 2025-03 | 19 | 7 | -39,075 | -781,50 | 57,1% | 0,860 |
| VWAP Extreme (referentie) | 2025-04 | 19 | 5 | -35,375 | -707,50 | 40,0% | 0,879 |
| VWAP Extreme (referentie) | 2025-05 | 21 | 6 | 131,900 | 2.638,00 | 66,7% | 2,725 |
| VWAP Extreme (referentie) | 2025-06 | 20 | 6 | 145,900 | 2.918,00 | 83,3% | 3,041 |
| VWAP Extreme (referentie) | 2025-07 | 20 | 10 | -96,750 | -1.935,00 | 40,0% | 0,642 |
| VWAP Extreme (referentie) | 2025-08 | 19 | 9 | -138,525 | -2.770,50 | 44,4% | 0,383 |
| VWAP Extreme (referentie) | 2025-09 | 18 | 8 | 109,700 | 2.194,00 | 62,5% | 1,969 |
| VWAP Extreme (referentie) | 2025-10 | 23 | 6 | -94,100 | -1.882,00 | 33,3% | 0,623 |
| VWAP Extreme (referentie) | 2025-11 | 19 | 6 | 48,150 | 963,00 | 33,3% | 1,161 |
| VWAP Extreme (referentie) | 2025-12 | 20 | 7 | 38,675 | 773,50 | 57,1% | 1,155 |
| VWAP Extreme (referentie) | 2026-01 | 20 | 8 | -375,800 | -7.516,00 | 12,5% | 0,175 |
| VWAP Extreme (referentie) | 2026-02 | 19 | 8 | -140,300 | -2.806,00 | 25,0% | 0,591 |
| VWAP Extreme (referentie) | 2026-03 | 21 | 6 | 267,650 | 5.353,00 | 50,0% | 7,704 |
| VWAP Extreme (referentie) | 2026-04 | 20 | 9 | 204,225 | 4.084,50 | 66,7% | 2,238 |
| VWAP Extreme (referentie) | 2026-05 | 21 | 9 | 26,975 | 539,50 | 44,4% | 1,110 |
| VWAP Extreme (referentie) | 2026-06 | 21 | 5 | 169,375 | 3.387,50 | 40,0% | 1,513 |
| VWAP Extreme (referentie) | 2026-07 | 22 | 6 | -89,350 | -1.787,00 | 33,3% | 0,735 |
| VWAP Extreme (referentie) | 2026-08 | 21 | 3 | -194,675 | -3.893,50 | 0,0% | 0,000 |
| VWAP Extreme (referentie) | 2026-09 | 22 | 4 | 14,350 | 287,00 | 75,0% | 1,170 |

### Long versus short

| Model | Richting | Trades | Netto punten | Netto USD | Winrate | PF | Gemiddelde trade |
|---|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | long | 168 | 791,450 | 15.829,00 | 51,8% | 1,120 | 4,711 |
| ORB15 (primair) | short | 191 | -324,225 | -6.484,50 | 39,8% | 0,967 | -1,698 |
| ORB5 (referentie) | long | 176 | -184,100 | -3.682,00 | 45,5% | 0,977 | -1,046 |
| ORB5 (referentie) | short | 196 | -56,350 | -1.127,00 | 38,8% | 0,994 | -0,287 |
| London Sweep (referentie) | long | 96 | 313,400 | 6.268,00 | 41,7% | 1,067 | 3,265 |
| London Sweep (referentie) | short | 99 | -664,525 | -13.290,50 | 38,4% | 0,881 | -6,712 |
| VWAP Extreme (referentie) | long | 73 | -369,425 | -7.388,50 | 47,9% | 0,877 | -5,061 |
| VWAP Extreme (referentie) | short | 67 | 340,425 | 6.808,50 | 44,8% | 1,204 | 5,081 |

### MFE/MAE-verdelingen

| Model | Maatstaf | n | P05 | P25 | Mediaan | P75 | P95 |
|---|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | MFE_R_lower | 359 | 0,076 | 0,320 | 0,716 | 1,324 | 2,004 |
| ORB15 (primair) | MFE_R_bar_upper | 359 | 0,076 | 0,320 | 0,716 | 1,324 | 2,004 |
| ORB15 (primair) | MAE_R_lower | 359 | 0,078 | 0,304 | 0,730 | 1,000 | 1,000 |
| ORB15 (primair) | MAE_R_bar_upper | 359 | 0,078 | 0,304 | 0,730 | 1,000 | 1,000 |
| ORB15 (primair) | MFE_points_lower | 359 | 5,975 | 28,250 | 69,500 | 128,000 | 221,925 |
| ORB15 (primair) | MFE_points_bar_upper | 359 | 5,975 | 28,250 | 69,500 | 128,000 | 221,925 |
| ORB15 (primair) | MAE_points_lower | 359 | 6,475 | 28,375 | 63,500 | 96,875 | 143,400 |
| ORB15 (primair) | MAE_points_bar_upper | 359 | 6,475 | 28,375 | 63,500 | 96,875 | 143,400 |
| ORB15 (primair) | MFE_first_bar_minute | 359 | 0,000 | 4,000 | 26,000 | 68,000 | 118,100 |
| ORB15 (primair) | MAE_first_bar_minute | 359 | 0,000 | 5,000 | 18,000 | 54,000 | 96,000 |
| ORB5 (referentie) | MFE_R_lower | 372 | 0,053 | 0,325 | 0,727 | 1,467 | 2,005 |
| ORB5 (referentie) | MFE_R_bar_upper | 372 | 0,053 | 0,325 | 0,727 | 1,467 | 2,005 |
| ORB5 (referentie) | MAE_R_lower | 372 | 0,087 | 0,348 | 0,829 | 1,000 | 1,000 |
| ORB5 (referentie) | MAE_R_bar_upper | 372 | 0,087 | 0,348 | 0,829 | 1,000 | 1,000 |
| ORB5 (referentie) | MFE_points_lower | 372 | 5,525 | 30,500 | 74,625 | 135,500 | 218,062 |
| ORB5 (referentie) | MFE_points_bar_upper | 372 | 5,525 | 30,500 | 74,625 | 135,500 | 218,062 |
| ORB5 (referentie) | MAE_points_lower | 372 | 7,913 | 34,000 | 65,625 | 99,812 | 147,125 |
| ORB5 (referentie) | MAE_points_bar_upper | 372 | 7,913 | 34,000 | 65,625 | 99,812 | 147,125 |
| ORB5 (referentie) | MFE_first_bar_minute | 372 | 0,000 | 5,000 | 24,000 | 63,000 | 121,450 |
| ORB5 (referentie) | MAE_first_bar_minute | 372 | 0,000 | 5,000 | 18,000 | 54,000 | 112,000 |
| London Sweep (referentie) | MFE_R_lower | 195 | 0,056 | 0,296 | 0,852 | 1,677 | 2,006 |
| London Sweep (referentie) | MFE_R_bar_upper | 195 | 0,056 | 0,296 | 0,852 | 1,677 | 2,006 |
| London Sweep (referentie) | MAE_R_lower | 195 | 0,034 | 0,310 | 0,932 | 1,000 | 1,000 |
| London Sweep (referentie) | MAE_R_bar_upper | 195 | 0,034 | 0,310 | 0,932 | 1,000 | 1,000 |
| London Sweep (referentie) | MFE_points_lower | 195 | 5,925 | 31,375 | 88,000 | 140,125 | 231,325 |
| London Sweep (referentie) | MFE_points_bar_upper | 195 | 5,925 | 31,375 | 88,000 | 140,125 | 231,325 |
| London Sweep (referentie) | MAE_points_lower | 195 | 3,350 | 31,500 | 64,500 | 103,250 | 146,850 |
| London Sweep (referentie) | MAE_points_bar_upper | 195 | 3,350 | 31,500 | 64,500 | 103,250 | 146,850 |
| London Sweep (referentie) | MFE_first_bar_minute | 195 | 0,000 | 7,500 | 28,000 | 70,500 | 121,200 |
| London Sweep (referentie) | MAE_first_bar_minute | 195 | 0,000 | 4,000 | 20,000 | 57,500 | 106,000 |
| VWAP Extreme (referentie) | MFE_R_lower | 140 | 0,044 | 0,247 | 0,624 | 0,946 | 1,543 |
| VWAP Extreme (referentie) | MFE_R_bar_upper | 140 | 0,057 | 0,247 | 0,624 | 0,946 | 1,543 |
| VWAP Extreme (referentie) | MAE_R_lower | 140 | 0,059 | 0,238 | 0,496 | 0,971 | 1,000 |
| VWAP Extreme (referentie) | MAE_R_bar_upper | 140 | 0,059 | 0,238 | 0,496 | 0,971 | 1,000 |
| VWAP Extreme (referentie) | MFE_points_lower | 140 | 2,425 | 25,312 | 52,000 | 88,500 | 164,762 |
| VWAP Extreme (referentie) | MFE_points_bar_upper | 140 | 3,688 | 25,312 | 52,000 | 88,500 | 164,762 |
| VWAP Extreme (referentie) | MAE_points_lower | 140 | 4,950 | 24,375 | 48,375 | 77,000 | 116,300 |
| VWAP Extreme (referentie) | MAE_points_bar_upper | 140 | 4,950 | 24,375 | 48,375 | 77,000 | 116,300 |
| VWAP Extreme (referentie) | MFE_first_bar_minute | 140 | 0,000 | 3,750 | 16,500 | 42,250 | 83,000 |
| VWAP Extreme (referentie) | MAE_first_bar_minute | 140 | 0,000 | 3,000 | 14,000 | 42,000 | 76,100 |

MFE/MAE zijn intrabar-identificatiegrenzen, geen exacte tickvolgorde. Lower gebruikt voltooide eerdere bars plus de fill; upper gebruikt de exitbar binnen de vaste stop-/targetbarrières. Bij tijdexit is de laatste volledige minuut bekend.1R=afstand entry tot initiële stop vóór kosten. Tijd tot eerste bar-extreem is in minuten en kan binnen de exitminuut na de fill liggen.

### Kosten-gevoeligheid, onveranderde fills

| Model | USD roundtrip | Netto punten | Netto USD | Winrate | PF | Max drawdown punten |
|---|---:|---:|---:|---:|---:|---:|
| ORB15 (primair) | 24,50 | 467,225 | 9.344,50 | 45,4% | 1,028 | 2.102,775 |
| ORB15 (primair) | 44,50 | 108,225 | 2.164,50 | 44,8% | 1,006 | 2.361,775 |
| ORB15 (primair) | 64,50 | -250,775 | -5.015,50 | 44,8% | 0,985 | 2.621,800 |
| ORB5 (referentie) | 24,50 | -240,450 | -4.809,00 | 41,9% | 0,987 | 2.234,725 |
| ORB5 (referentie) | 44,50 | -612,450 | -12.249,00 | 41,4% | 0,967 | 2.345,725 |
| ORB5 (referentie) | 64,50 | -984,450 | -19.689,00 | 41,4% | 0,948 | 2.456,725 |
| London Sweep (referentie) | 24,50 | -351,125 | -7.022,50 | 40,0% | 0,966 | 1.609,675 |
| London Sweep (referentie) | 44,50 | -546,125 | -10.922,50 | 40,0% | 0,947 | 1.662,675 |
| London Sweep (referentie) | 64,50 | -741,125 | -14.822,50 | 40,0% | 0,929 | 1.715,675 |
| VWAP Extreme (referentie) | 24,50 | -29,000 | -580,00 | 46,4% | 0,994 | 804,650 |
| VWAP Extreme (referentie) | 44,50 | -169,000 | -3.380,00 | 46,4% | 0,964 | 858,650 |
| VWAP Extreme (referentie) | 64,50 | -309,000 | -6.180,00 | 45,7% | 0,936 | 912,650 |

### Clean-sensitiviteit (niet beslissend)

| Model | Eligible | Trades | Netto punten | PF |
|---|---:|---:|---:|---:|
| ORB15 (primair) | 405 | 357 | 455,425 | 1,028 |
| ORB5 (referentie) | 405 | 370 | -336,000 | 0,982 |
| London Sweep (referentie) | 405 | 194 | -550,400 | 0,946 |
| VWAP Extreme (referentie) | 405 | 140 | -29,000 | 0,994 |

## Inferentie en beperkingen

De vooraf vastgelegde2000 circular moving-block bootstrapreplicaties gebruiken blokken van5eligible sessies en seed20261020. Eligible dagen zonder trade tellen als0; niet-eligible kalenderdagen worden niet als fictieve0 toegevoegd. CI is nominaal95% voor gemiddelde netto punten per eligible dag. De p-waarde is tweezijdig, gecentreerd: (1+extreme replicaties)/2001. CI en p zijn niet noodzakelijk exacte inversen.

One confirmatory year ORB15 all-view, unchanged raw p. Eight other requested/clean sensitivity p-values in one globally Holm-adjusted family, fixed before scoring. References and combined statistics descriptive only, never promotion.

De acht aanvullende toetsen zijn vóór de eerste signaalrun in de vrijgave vastgelegd: drie jaarreferenties, vier gecombineerde reeksen en ORB15jaar-clean. Nominale intervallen zijn geen simultane intervallen. Maand-, richting-, kosten- en excursietabellen zijn beschrijvend, zonder nieuwe hypothesetoetsen.

Kosten:$24,50RT=2ticks per kant plus$4,50commissie. Stress:$44,50 en$64,50RT met identieke fills. Bij stop en target in dezelfde minuut geldt de stop; ongunstige gapstop wordt tegen de slechtere open uitgevoerd. Eén contract per model, geen samengevoegd portfolio of compounding.

## Reproductie en onveranderde historie

Twee afzonderlijke Python-processen laden alle69geregistreerde bronbestanden opnieuw. Geen gecachte features of tradeledger wordt gebruikt om signalen te genereren. De vooraf verankerde private historische ledger en eligibility-datums worden alleen als onafhankelijke controle gebruikt. Alle deterministische outputs worden byte voor byte vergeleken. Dit bewijst reproduceerbaarheid van dezelfde implementatie, niet een tweede onafhankelijk geschreven engine of nieuwe statistische replicatie.

De historische435trades en780eligibility-regels blijven byte-identiek; alle73bevroren bestanden en het volledige voorbereidingspakket blijven geldig. De onbekende leveranciersvintages, gebruiksrechten, beperkte eerdere-niet-gebruikbewijzen en gereconstrueerde kalender blijven als beperking bestaan. De gebruiker heeft uitvoering met deze vastgelegde beperkingen expliciet vrijgegeven.

### Commando’s

- Nieuwe gecontroleerde werkmap, na herstel van private geregistreerde bronnen en voorbereidingsledgers: `.venv/bin/python -B -m scripts.year_holdout --run first` en daarna `--run reproduction`.
- Bestaande runs niet overschrijven: `.venv/bin/python -B -m scripts.year_holdout --compare`.
- Alle69bronhashes, beide ledgers en publicatie opnieuw controleren zonder derde scoringrun: `node scripts/verify-year-holdout`.
- Aggregaten uit beide runs reproduceren en vergelijken: `.venv/bin/python -B -m scripts.publish_year_holdout`.
- `npm run verify:freeze`; `.venv/bin/python -B -m scripts.oos_preparation.seal --verify`; `.venv/bin/python -m pytest -q`.
- Het vrijgavebestand staat in `research/year-holdout-release.json`; geen impliciete nieuwe vrijgave door een CLI-vlag. Eerste run en reproductie zijn per werkmap exclusief en worden niet overschreven.

**Deze jaarperiode is vanaf nu verbruikte onderzoeksdata. Geen nieuwe filters of parameters testen en dezelfde periode opnieuw als onafhankelijke holdout presenteren.**
