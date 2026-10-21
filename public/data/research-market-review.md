# Afgesloten modellen, uitvoeringsaudit en ruw NQ-marktgedrag

## 1. Archivering

**ORB5, ORB15, London Sweep en VWAP Extreme: `ARCHIVED_NOT_VALIDATED`.** Dit geldt voor Baseline v0.9, vNext159 en de vaste jaar-holdout. Geen tuning, reddingsfilters of hergebruik als kandidaat. Historische reproductie en uitvoeringstoetsen blijven toegestaan. Het eerdere `HOLDOUT_FAILED` is niet overschreven. Niet-gevalideerd betekent niet dat iedere denkbare variant universeel weerlegd is.

Archiefregistratie beschermt 115 bestanden op SHA-256. De bestaande 73 bevroren bestanden, het voorbereidingspakket, de jaarresultaten en de strategiecode blijven ongewijzigd.

## 2. Onafhankelijke controle van de meetlat

Nieuwe code-inspectie en handmatig afgeleide synthetische voorbeelden, los van de bestaande reproductietest. Geen onafhankelijke tick-/brokerfill-certificatie en geen tweede volledige simulator. Er zijn geen nieuwe strategie-signalen op echte data berekend.

### Exacte timing en ordertypen

| Aspect | Werkelijke code-aanname |
|---|---|
| Signaal | Afgeronde minuutbar t; timestamp is het begin van die bar. Signaal van 09:45 is pas om 09:46 bekend. |
| Entry | Ruwe open van exact t+1. Het signaal van de 09:45-bar wordt dus op de 09:46-open gevuld. Frictie wordt apart afgetrokken, niet in de ledgerprijs verwerkt. |
| Stop-entry / limit-entry | Niet geïmplementeerd. Alle vier modellen gebruiken next-open market fills, ook ORB en VWAP Extreme. Geen resting breakout-stop of VWAP-limit-entry. |
| Entry en stop in dezelfde minuut | Entry op baropen, bracket direct actief. Deze bar wordt inclusief high/low direct gescand; ook direct verlies is mogelijk. |
| Stop en target in dezelfde minuut | Stop wint. Stop-long: min(stop, baropen); stop-short: max(stop, baropen). Ongunstige gap dus slechter dan stopniveau. |
| Target | Een touch van high/low telt als fill op exact target. Gunstige gaps krijgen geen betere prijs. Werkelijke queue/bid/ask/tickvolgorde ontbreken. |
| Tijdsluiting | Close van de bar 11:59–12:00 NY. exit_bar_utc verwijst naar 11:59 als barlabel, niet naar bewezen executietijd. |
| Afronding | SL-afstand wordt naar beneden op 0,25 afgerond, vaste TP-afstand naar boven. Dichtere stops zijn niet onder alle omstandigheden conservatief. VWAP-target wordt bij long omlaag en bij short omhoog afgerond. |
| VWAP | Per onverschoven contract/handelsdag vanaf 18:00 NY: cumulatief Σ[Volume × (High+Low+Close)/3] / ΣVolume. Gewogen populatie-SD van dezelfde HLC3-proxy. Geen transactie-VWAP. |
| Beschikbaarheid VWAP | Inclusief de actuele afgeronde bar; pas bekend op timestamp+1min. Bij ontbrekende prefix rekent de primitieve functie vanaf de eerste waargenomen bar; de eligibility-gate blokkeert incomplete 18:00–12:00-prefixen. |
| Basiskosten | $24,50RT = 2 ticks per kant ($20) + $4,50 commissie. 1 tick = 0,25 NQ-punt = $5. |
| Extra stopfrictie | +1 tick per stop-fill: +$5 per stop-exit, dus $29,50RT op stoptrades. +2 ticks: +$10, dus $34,50RT. Overige exits blijven $24,50. Er zijn geen stop-entries om extra te belasten. |

Broncode (vastgelegde commit, geen wijzigingen): [build_features](https://github.com/ianvdbrink3/QUANTT/blob/9c890b1aa752f6941768c50c55f35ee779dbe903/scripts/reproduce_research/engine.py#L112), [simulate](https://github.com/ianvdbrink3/QUANTT/blob/9c890b1aa752f6941768c50c55f35ee779dbe903/scripts/reproduce_research/engine.py#L261), [hypotheses](https://github.com/ianvdbrink3/QUANTT/blob/9c890b1aa752f6941768c50c55f35ee779dbe903/scripts/reproduce_research/engine.py#L301).

### Wat is conservatief?

- Stop priority when both barriers hit; adverse stop gaps use the worse open; favorable target gaps get no improvement.
- No interpolation for missing required minutes; no signal-close fill; constant friction also charged on target/time exits.

### Blinde vlekken en mogelijke optimistische aannames

- Next-open fill assumes zero compute/transmission latency, executable size and no spread/queue restrictions beyond flat fees.
- A target touch is assumed filled: queue position, bid/ask side and traded size are unknown. A minute low/high is not proof a limit order filled.
- Same-minute bracket readiness and exact intrabar sequence are unobserved; stop-first does not make all fills conservatively certified.
- A session VWAP computed from HLC3 is not exchange tick VWAP; historical vendor timestamps/bar-start convention and publication vintage are not independently certified.
- Flat2tick-per-side slippage is not calibrated by volatility, spread, order type or stop cascades. Added stop friction is sensitivity only, not an estimated fill distribution.
- At12:00 an immediate close fill at the previous minute last trade is an idealization; exact timestamp and latency remain unknown.

London kan sweep, terugkeer en VWAP-kruising uit dezelfde afgeronde minuut afleiden; de tickvolgorde daarvan is niet bewezen. De entry vindt wel pas daarna plaats. ORB vereist een afgeronde close buiten de range; een eerdere aanraking van de rangegrens is geen entry.

### Feitelijke conflicten in de bestaande ledgers

| Periode | Model | Trades | Stop-exits | Stop op entrybar | Target op entrybar | SL+TP in één bar |
|---|---|---|---|---|---|---|
| year | London Sweep | 113 | 55 | 0 | 0 | 0 |
| year | ORB15 | 216 | 92 | 0 | 0 | 0 |
| year | ORB5 | 225 | 94 | 0 | 0 | 0 |
| year | VWAP Extreme | 77 | 19 | 1 | 0 | 0 |
| combined | London Sweep | 195 | 95 | 1 | 0 | 0 |
| combined | ORB15 | 359 | 145 | 0 | 0 | 0 |
| combined | ORB5 | 372 | 161 | 0 | 0 | 0 |
| combined | VWAP Extreme | 140 | 33 | 1 | 0 | 0 |

Geen SL+TP-conflicten in deze ledger bewijst niet dat de simulator alle mogelijke liveconflicten correct behandelt. Synthetische controles behandelen deze grensgevallen apart.

### Alleen rekenkundige extra stopfrictie op ongewijzigde trades

| Periode | Model | Extra ticks/stop | Extra USD totaal | Netto NQ-punten | Netto USD | PF |
|---|---|---|---|---|---|---|
| year | London Sweep | 0 | 0,00 | -526,675 | -10.533,50 | 0,923 |
| year | London Sweep | 1 | 275,00 | -540,425 | -10.808,50 | 0,921 |
| year | London Sweep | 2 | 550,00 | -554,175 | -11.083,50 | 0,919 |
| year | ORB15 | 0 | 0,00 | -616,350 | -12.327,00 | 0,946 |
| year | ORB15 | 1 | 460,00 | -639,350 | -12.787,00 | 0,944 |
| year | ORB15 | 2 | 920,00 | -662,350 | -13.247,00 | 0,942 |
| year | ORB5 | 0 | 0,00 | 161,625 | 3.232,50 | 1,014 |
| year | ORB5 | 1 | 470,00 | 138,125 | 2.762,50 | 1,012 |
| year | ORB5 | 2 | 940,00 | 114,625 | 2.292,50 | 1,010 |
| year | VWAP Extreme | 0 | 0,00 | -124,825 | -2.496,50 | 0,958 |
| year | VWAP Extreme | 1 | 95,00 | -129,575 | -2.591,50 | 0,957 |
| year | VWAP Extreme | 2 | 190,00 | -134,325 | -2.686,50 | 0,955 |
| combined | London Sweep | 0 | 0,00 | -351,125 | -7.022,50 | 0,966 |
| combined | London Sweep | 1 | 475,00 | -374,875 | -7.497,50 | 0,964 |
| combined | London Sweep | 2 | 950,00 | -398,625 | -7.972,50 | 0,961 |
| combined | ORB15 | 0 | 0,00 | 467,225 | 9.344,50 | 1,028 |
| combined | ORB15 | 1 | 725,00 | 430,975 | 8.619,50 | 1,026 |
| combined | ORB15 | 2 | 1.450,00 | 394,725 | 7.894,50 | 1,024 |
| combined | ORB5 | 0 | 0,00 | -240,450 | -4.809,00 | 0,987 |
| combined | ORB5 | 1 | 805,00 | -280,700 | -5.614,00 | 0,985 |
| combined | ORB5 | 2 | 1.610,00 | -320,950 | -6.419,00 | 0,983 |
| combined | VWAP Extreme | 0 | 0,00 | -29,000 | -580,00 | 0,994 |
| combined | VWAP Extreme | 1 | 165,00 | -37,250 | -745,00 | 0,992 |
| combined | VWAP Extreme | 2 | 330,00 | -45,500 | -910,00 | 0,990 |

Deze gevoeligheid schat geen werkelijke slippageverdeling en wijzigt geen archived P&L. Hogere kosten veranderen hier geen signalen, stopniveaus, exits of intrabar-volgorde.

## 3. Strategie-vrij ruw marktgedrag

Periode: 2024-12-30–2026-09-30. 69 hash-gecontroleerde bronnen, 454 geplande sessies, **435 complete RTH-sessies** met 09:29-grensclose; 19 uitgesloten. 431 huidige sessies hebben bruikbare vorige-sessiegegevens in hetzelfde contract. Andere aantallen dan strategie-eligible dagen zijn bewust: geen ATR-/volume-opwarmfilter.

Geen entries, stops, targets, kosten of modelselectie. Positief/negatief betekent alleen prijsrichting; geen winst/verlies van een uitvoerbare positie. Alle data zijn eerder verbruikt. Dit is verkenning, geen nieuwe validatie.

### Vooraf vastgelegde meetdefinities

- **session_sample**: Exact 390 scheduled and observed RTH bars [09:30,16:00) America/New_York plus observed 09:29 boundary close. Exclude early closes, gaps and missing days. ATR, overnight completeness and strategy eligibility are NOT selection criteria. Keep an explicit exclusion register.
- **cross_day**: Previous scheduled trading session, never last available valid session. Previous same-contract RTH must exactly match its calendar including early closes; otherwise missing. PDH/PDL and prior close use the incoming contract's own historical bars, not another contract. Current sessions always full RTH.
- **returns**: 10000*log(endpoint close / boundary close), in basis points, with point differences also exported. First boundary is 09:29 close, not 09:30 open. No fees, entries, exits or profit interpretation.
- **half_hours**: 13 disjoint windows anchored09:30. Close-to-close signed returns, high-low range in points/log-bps, realized root sum squared 1m log returns in bps (separate from high-low), and fraction of same-contract full RTH volume. Mean, median, P05/P25/P75/P95 and positive fraction.
- **intraday_autocorrelation**: Pearson lag1 of adjacent NON-overlapping 5,15,30,60min close-to-close windows, anchored09:30, within a single RTH session only. Discard incomplete final60min window. Pool pair sufficient statistics, resample entire chronological days. No lag search.
- **daily_correlations**: Lag1 of same-contract RTH close-to-close returns on adjacent scheduled sessions; and same-day correlation of prior same-contract RTH close ->09:30 open overnight return versus09:30 open ->15:59 close RTH return. No stale-day bridging.
- **events**: RECORD_HIGH/RECORD_LOW: every strict new running RTH high/low from second bar, compared only to earlier completed bars. PDH_TOUCH/PDL_TOUCH: first bar each day with low<=previous session same-contract level<=high. A gap over a level without observed touch is NOT a touch. Repeated equal record prices not counted. Both labels in same bar allowed.
- **event_outcome**: Event known only at event-minute close. Signed raw close-to-close log-bps and point difference from that close to15m,60m or15:59 close; never use touched level as executable price. Require positive elapsed horizon and exact contiguous bars. Omit censored horizons, report counts separately; do not pool horizons or add mirrored long/short returns.
- **event_weighting**: Export event-weighted distribution and event-weighted mean CI/p plus equal-event-day mean CI/p. Record-heavy days may dominate event-weighted values. All overlapping events remain clustered in their original day; no independence claim.

Alle rendementen in de inferentietabellen zijn log-basispunten: 10.000 × ln(C1/C0). 1 bp = 0,01% log-rendement. Close-to-close begint bij de vorige minuutclose; de eerste halfuurgrens is dus 09:29-close, niet 09:30-open. RTH-slot = 15:59-minuteclose, bekend om 16:00 NY.

High-low range is een spreidingsmaat, niet gerealiseerde variantie. Daarom staat daarnaast RV = wortel van de som van gekwadrateerde 1m-logrendementen. Volumeaandeel is ten opzichte van RTH-volume, niet de volledige Globex-dag.

### Onzekerheid en meervoudig toetsen

4.000 circular moving-block bootstrapreplicaties, blokken van vijf chronologische geplande sessies, seed 20261022. Hele dagen inclusief alle overlappende events worden gezamenlijk gewogen. Uitgesloten of observatieloze dagen blijven als maskers in de chronologie; ze worden geen fictieve nulrendementen. Intervallen zijn nominale 95%-percentielintervallen, niet simultaan. P-waarden zijn tweezijdig en gecentreerd, (1 + extremere replicaties)/(B_valid + 1), een benaderende exploratieve nulwaardetoets. CI en p zijn niet exact elkaars inversen. De kleinste resolutie is 1/4001.

Eén globale Holm-familie van **43** toetsen: 13 gemiddelde halfuurrendementen, zes correlaties, twaalf eventgewogen en twaalf daggewogen gemiddelde vervolgrendementen. Niet-berekenbare toetsen blijven met p=1 in de correctie. Geen nulwaardetoets op positief-gedefinieerde high-low range, RV of volumeaandeel, en geen afzonderlijke toetsen op quantielen. Alle toetsen blijven in de export staan.

### A. Halfuurstructuur: richting, spreiding en volume

| NY-start | Maatstaf | N | Gemiddeld | 95%CI gemiddelde | Mediaan | 95%CI mediaan | P05 | P25 | P75 | P95 | p nominaal | p Holm43 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 09:30 | return_bps | 435 | 0,043 | [-4,659; 4,677] | 2,074 | [-0,698; 7,621] | -77,374 | -27,237 | 28,932 | 73,182 | 0,982254 | 1,000000 |
| 09:30 | return_points | 435 | -0,182 | [-11,555; 10,827] | 5,250 | [-1,750; 17,500] | -196,200 | -67,250 | 72,625 | 185,075 | n.v.t. | n.v.t. |
| 09:30 | range_bps | 435 | 67,304 | [62,271; 72,425] | 60,250 | [57,097; 67,008] | 29,579 | 43,977 | 82,399 | 122,148 | n.v.t. | n.v.t. |
| 09:30 | range_points | 435 | 165,744 | [153,422; 178,260] | 153,750 | [140,747; 164,375] | 68,625 | 109,125 | 204,000 | 310,525 | n.v.t. | n.v.t. |
| 09:30 | realized_rv_bps | 435 | 40,922 | [38,085; 44,021] | 38,438 | [35,419; 41,113] | 21,246 | 28,750 | 48,922 | 69,817 | n.v.t. | n.v.t. |
| 09:30 | volume_share | 435 | 0,164 | [0,160; 0,169] | 0,164 | [0,158; 0,169] | 0,116 | 0,143 | 0,185 | 0,220 | n.v.t. | n.v.t. |
| 10:00 | return_bps | 435 | 0,488 | [-2,681; 3,602] | 3,009 | [-0,380; 6,679] | -60,540 | -16,141 | 20,015 | 54,020 | 0,756061 | 1,000000 |
| 10:00 | return_points | 435 | 1,112 | [-6,399; 8,522] | 7,500 | [-1,000; 15,250] | -156,550 | -41,875 | 52,375 | 138,125 | n.v.t. | n.v.t. |
| 10:00 | range_bps | 435 | 54,300 | [49,219; 60,301] | 46,459 | [41,690; 52,111] | 20,432 | 31,921 | 68,945 | 106,777 | n.v.t. | n.v.t. |
| 10:00 | range_points | 435 | 132,268 | [121,229; 144,244] | 112,750 | [102,500; 130,500] | 50,925 | 80,125 | 166,125 | 257,675 | n.v.t. | n.v.t. |
| 10:00 | realized_rv_bps | 435 | 33,645 | [30,558; 37,246] | 29,682 | [27,558; 32,750] | 14,886 | 20,922 | 40,904 | 59,775 | n.v.t. | n.v.t. |
| 10:00 | volume_share | 435 | 0,118 | [0,116; 0,121] | 0,118 | [0,114; 0,121] | 0,080 | 0,104 | 0,132 | 0,162 | n.v.t. | n.v.t. |
| 10:30 | return_bps | 435 | -0,898 | [-3,618; 1,813] | 0,872 | [-2,314; 4,604] | -51,551 | -16,341 | 17,559 | 42,116 | 0,521870 | 1,000000 |
| 10:30 | return_points | 435 | -2,305 | [-9,075; 4,435] | 2,250 | [-5,250; 10,625] | -131,425 | -39,375 | 46,000 | 107,100 | n.v.t. | n.v.t. |
| 10:30 | range_bps | 435 | 45,556 | [41,428; 50,382] | 39,540 | [36,733; 42,741] | 16,655 | 26,916 | 57,535 | 90,015 | n.v.t. | n.v.t. |
| 10:30 | range_points | 435 | 111,571 | [101,899; 121,654] | 97,750 | [90,250; 104,500] | 39,500 | 67,375 | 141,000 | 221,225 | n.v.t. | n.v.t. |
| 10:30 | realized_rv_bps | 435 | 28,574 | [26,160; 31,257] | 25,529 | [23,229; 27,906] | 12,607 | 18,049 | 34,289 | 52,527 | n.v.t. | n.v.t. |
| 10:30 | volume_share | 435 | 0,095 | [0,093; 0,097] | 0,094 | [0,091; 0,095] | 0,068 | 0,082 | 0,105 | 0,128 | n.v.t. | n.v.t. |
| 11:00 | return_bps | 435 | -0,273 | [-2,814; 2,161] | 1,700 | [-0,733; 3,591] | -46,876 | -11,800 | 15,114 | 40,278 | 0,833292 | 1,000000 |
| 11:00 | return_points | 435 | -0,072 | [-5,947; 5,811] | 4,250 | [-2,000; 9,250] | -123,400 | -28,000 | 37,500 | 102,350 | n.v.t. | n.v.t. |
| 11:00 | range_bps | 435 | 40,131 | [35,960; 45,016] | 32,918 | [30,573; 36,592] | 15,013 | 22,372 | 46,664 | 87,285 | n.v.t. | n.v.t. |
| 11:00 | range_points | 435 | 97,596 | [88,581; 107,385] | 82,750 | [72,500; 90,500] | 34,600 | 57,250 | 121,000 | 210,375 | n.v.t. | n.v.t. |
| 11:00 | realized_rv_bps | 435 | 24,766 | [22,495; 27,445] | 21,230 | [19,371; 23,163] | 11,091 | 15,515 | 29,766 | 48,926 | n.v.t. | n.v.t. |
| 11:00 | volume_share | 435 | 0,079 | [0,078; 0,081] | 0,077 | [0,075; 0,079] | 0,056 | 0,068 | 0,088 | 0,110 | n.v.t. | n.v.t. |
| 11:30 | return_bps | 435 | 0,383 | [-1,729; 2,538] | 0,409 | [-0,905; 2,665] | -38,366 | -11,632 | 14,126 | 36,097 | 0,718820 | 1,000000 |
| 11:30 | return_points | 435 | 0,893 | [-4,222; 6,215] | 0,750 | [-2,500; 7,000] | -91,725 | -28,625 | 35,375 | 92,100 | n.v.t. | n.v.t. |
| 11:30 | range_bps | 435 | 36,305 | [33,124; 39,878] | 31,857 | [28,387; 33,762] | 13,574 | 20,780 | 44,241 | 82,456 | n.v.t. | n.v.t. |
| 11:30 | range_points | 435 | 88,349 | [81,365; 95,704] | 76,000 | [70,750; 81,503] | 32,925 | 52,250 | 112,500 | 182,725 | n.v.t. | n.v.t. |
| 11:30 | realized_rv_bps | 435 | 22,776 | [20,776; 25,122] | 19,835 | [18,285; 21,436] | 9,181 | 14,317 | 28,174 | 45,786 | n.v.t. | n.v.t. |
| 11:30 | volume_share | 435 | 0,071 | [0,069; 0,072] | 0,068 | [0,067; 0,069] | 0,051 | 0,060 | 0,077 | 0,099 | n.v.t. | n.v.t. |
| 12:00 | return_bps | 435 | 1,015 | [-1,205; 3,224] | 1,802 | [-0,269; 3,789] | -39,343 | -8,947 | 12,690 | 39,896 | 0,367408 | 1,000000 |
| 12:00 | return_points | 435 | 2,709 | [-2,779; 8,153] | 4,500 | [-0,750; 9,000] | -97,375 | -22,750 | 32,625 | 95,600 | n.v.t. | n.v.t. |
| 12:00 | range_bps | 435 | 33,664 | [30,524; 37,283] | 26,982 | [24,566; 29,874] | 12,154 | 18,706 | 42,829 | 74,129 | n.v.t. | n.v.t. |
| 12:00 | range_points | 435 | 81,544 | [74,786; 88,779] | 67,750 | [61,250; 74,250] | 30,175 | 46,625 | 102,625 | 173,800 | n.v.t. | n.v.t. |
| 12:00 | realized_rv_bps | 435 | 20,859 | [18,925; 23,076] | 17,840 | [16,025; 19,243] | 8,717 | 12,715 | 25,293 | 41,507 | n.v.t. | n.v.t. |
| 12:00 | volume_share | 435 | 0,061 | [0,059; 0,062] | 0,057 | [0,056; 0,058] | 0,042 | 0,051 | 0,068 | 0,092 | n.v.t. | n.v.t. |
| 12:30 | return_bps | 435 | -0,836 | [-2,875; 1,264] | -0,163 | [-1,103; 1,490] | -35,580 | -11,157 | 10,090 | 27,720 | 0,439640 | 1,000000 |
| 12:30 | return_points | 435 | -1,899 | [-6,557; 2,893] | -0,500 | [-3,000; 3,500] | -86,200 | -28,875 | 25,625 | 70,900 | n.v.t. | n.v.t. |
| 12:30 | range_bps | 435 | 31,681 | [28,389; 35,447] | 25,851 | [23,673; 27,971] | 10,805 | 17,190 | 38,300 | 71,177 | n.v.t. | n.v.t. |
| 12:30 | range_points | 435 | 76,357 | [69,497; 83,808] | 65,500 | [59,500; 70,000] | 26,850 | 44,375 | 94,125 | 167,575 | n.v.t. | n.v.t. |
| 12:30 | realized_rv_bps | 435 | 19,830 | [17,895; 22,079] | 16,444 | [14,697; 18,306] | 7,723 | 11,600 | 24,127 | 42,422 | n.v.t. | n.v.t. |
| 12:30 | volume_share | 435 | 0,055 | [0,054; 0,057] | 0,053 | [0,051; 0,055] | 0,037 | 0,046 | 0,062 | 0,082 | n.v.t. | n.v.t. |
| 13:00 | return_bps | 435 | 1,024 | [-1,792; 4,488] | 0,500 | [-1,458; 1,935] | -35,500 | -10,616 | 9,961 | 32,475 | 0,521620 | 1,000000 |
| 13:00 | return_points | 435 | 2,362 | [-3,808; 9,520] | 1,250 | [-3,500; 4,375] | -85,500 | -28,625 | 24,000 | 81,800 | n.v.t. | n.v.t. |
| 13:00 | range_bps | 435 | 33,294 | [28,349; 40,516] | 25,534 | [23,261; 28,376] | 10,989 | 17,422 | 37,823 | 68,649 | n.v.t. | n.v.t. |
| 13:00 | range_points | 435 | 79,109 | [69,676; 92,049] | 64,500 | [59,000; 70,000] | 26,925 | 43,250 | 93,125 | 156,175 | n.v.t. | n.v.t. |
| 13:00 | realized_rv_bps | 435 | 20,477 | [17,653; 24,354] | 16,305 | [14,606; 17,918] | 7,366 | 11,324 | 24,143 | 40,701 | n.v.t. | n.v.t. |
| 13:00 | volume_share | 435 | 0,054 | [0,052; 0,055] | 0,051 | [0,049; 0,052] | 0,036 | 0,044 | 0,060 | 0,077 | n.v.t. | n.v.t. |
| 13:30 | return_bps | 435 | 1,894 | [-0,878; 5,397] | 0,941 | [-0,597; 2,515] | -30,721 | -9,556 | 10,054 | 33,578 | 0,231442 | 1,000000 |
| 13:30 | return_points | 435 | 4,048 | [-1,830; 10,918] | 2,750 | [-1,750; 5,750] | -74,600 | -23,125 | 25,250 | 87,725 | n.v.t. | n.v.t. |
| 13:30 | range_bps | 435 | 30,339 | [26,547; 35,082] | 23,518 | [20,891; 27,200] | 9,777 | 15,628 | 37,462 | 66,817 | n.v.t. | n.v.t. |
| 13:30 | range_points | 435 | 72,380 | [65,051; 81,003] | 57,500 | [52,122; 65,125] | 24,175 | 39,750 | 90,375 | 164,150 | n.v.t. | n.v.t. |
| 13:30 | realized_rv_bps | 435 | 18,906 | [16,534; 21,991] | 15,197 | [13,463; 16,601] | 6,382 | 10,486 | 22,417 | 41,938 | n.v.t. | n.v.t. |
| 13:30 | volume_share | 435 | 0,050 | [0,049; 0,052] | 0,047 | [0,045; 0,049] | 0,032 | 0,040 | 0,057 | 0,078 | n.v.t. | n.v.t. |
| 14:00 | return_bps | 435 | 0,238 | [-2,267; 2,588] | -0,647 | [-1,781; 0,921] | -33,103 | -8,799 | 10,212 | 33,663 | 0,852037 | 1,000000 |
| 14:00 | return_points | 435 | 0,306 | [-5,061; 5,584] | -1,500 | [-4,750; 2,000] | -83,100 | -22,125 | 26,250 | 82,825 | n.v.t. | n.v.t. |
| 14:00 | range_bps | 435 | 30,033 | [27,002; 33,834] | 22,973 | [20,950; 25,829] | 9,201 | 15,209 | 36,738 | 69,533 | n.v.t. | n.v.t. |
| 14:00 | range_points | 435 | 72,072 | [66,005; 79,032] | 57,000 | [51,875; 64,378] | 22,175 | 39,250 | 90,750 | 161,225 | n.v.t. | n.v.t. |
| 14:00 | realized_rv_bps | 435 | 18,385 | [16,515; 20,663] | 14,687 | [13,731; 15,901] | 6,489 | 10,463 | 22,732 | 42,366 | n.v.t. | n.v.t. |
| 14:00 | volume_share | 435 | 0,052 | [0,050; 0,053] | 0,048 | [0,046; 0,050] | 0,033 | 0,041 | 0,058 | 0,081 | n.v.t. | n.v.t. |
| 14:30 | return_bps | 435 | -1,197 | [-3,348; 0,959] | -0,383 | [-1,781; 1,351] | -37,953 | -9,258 | 8,283 | 26,790 | 0,285929 | 1,000000 |
| 14:30 | return_points | 435 | -3,124 | [-8,183; 2,048] | -1,000 | [-5,000; 3,500] | -86,575 | -22,625 | 20,500 | 64,575 | n.v.t. | n.v.t. |
| 14:30 | range_bps | 435 | 28,932 | [25,914; 32,603] | 22,083 | [19,583; 24,667] | 8,938 | 15,042 | 33,971 | 75,350 | n.v.t. | n.v.t. |
| 14:30 | range_points | 435 | 69,762 | [63,599; 76,757] | 54,250 | [50,250; 59,000] | 21,675 | 38,125 | 83,500 | 168,600 | n.v.t. | n.v.t. |
| 14:30 | realized_rv_bps | 435 | 18,147 | [16,280; 20,393] | 14,163 | [12,792; 15,965] | 6,165 | 9,660 | 22,040 | 40,713 | n.v.t. | n.v.t. |
| 14:30 | volume_share | 435 | 0,050 | [0,048; 0,052] | 0,046 | [0,045; 0,047] | 0,032 | 0,039 | 0,054 | 0,082 | n.v.t. | n.v.t. |
| 15:00 | return_bps | 435 | -1,228 | [-3,087; 0,575] | -0,195 | [-1,687; 1,401] | -37,828 | -9,829 | 8,949 | 30,994 | 0,188453 | 1,000000 |
| 15:00 | return_points | 435 | -2,517 | [-6,897; 1,807] | -0,500 | [-4,000; 3,500] | -95,600 | -23,750 | 21,375 | 77,200 | n.v.t. | n.v.t. |
| 15:00 | range_bps | 435 | 29,950 | [26,170; 34,356] | 21,457 | [19,370; 23,713] | 8,712 | 14,364 | 37,266 | 75,218 | n.v.t. | n.v.t. |
| 15:00 | range_points | 435 | 71,972 | [64,081; 80,837] | 52,750 | [49,000; 59,125] | 22,425 | 36,500 | 84,000 | 174,950 | n.v.t. | n.v.t. |
| 15:00 | realized_rv_bps | 435 | 18,024 | [16,064; 20,255] | 14,089 | [12,508; 15,830] | 6,343 | 9,550 | 21,419 | 42,064 | n.v.t. | n.v.t. |
| 15:00 | volume_share | 435 | 0,053 | [0,051; 0,055] | 0,049 | [0,047; 0,050] | 0,034 | 0,041 | 0,058 | 0,087 | n.v.t. | n.v.t. |
| 15:30 | return_bps | 435 | 1,085 | [-1,504; 3,591] | 0,597 | [-0,684; 3,323] | -42,114 | -10,384 | 13,289 | 43,178 | 0,423644 | 1,000000 |
| 15:30 | return_points | 435 | 2,006 | [-4,251; 7,978] | 1,750 | [-1,750; 8,250] | -99,850 | -26,750 | 32,000 | 102,775 | n.v.t. | n.v.t. |
| 15:30 | range_bps | 435 | 36,442 | [32,463; 40,772] | 28,155 | [25,800; 32,328] | 14,022 | 19,692 | 44,708 | 82,927 | n.v.t. | n.v.t. |
| 15:30 | range_points | 435 | 87,252 | [79,325; 95,394] | 70,250 | [63,750; 78,000] | 35,100 | 49,750 | 104,875 | 179,000 | n.v.t. | n.v.t. |
| 15:30 | realized_rv_bps | 435 | 22,230 | [19,984; 24,823] | 18,242 | [16,637; 19,776] | 9,243 | 13,174 | 26,756 | 48,049 | n.v.t. | n.v.t. |
| 15:30 | volume_share | 435 | 0,097 | [0,095; 0,099] | 0,094 | [0,091; 0,098] | 0,070 | 0,083 | 0,109 | 0,131 | n.v.t. | n.v.t. |

volume_share is een fractie (0,10 = 10%). Alle halfuren hebben dezelfde 435 complete sessies.

### B. Autocorrelatie en Overnight versus RTH

| Meting | Paren | Dagen | Pearson r | 95%CI | p nominaal | p Holm43 |
|---|---|---|---|---|---|---|
| intraday_5m_lag1 | 33495 | 435 | 0,005669 | [-0,017; 0,024] | 0,597101 | 1,000000 |
| intraday_15m_lag1 | 10875 | 435 | -0,023359 | [-0,059; 0,016] | 0,244439 | 1,000000 |
| intraday_30m_lag1 | 5220 | 435 | -0,002952 | [-0,058; 0,043] | 0,919770 | 1,000000 |
| intraday_60m_lag1 | 2175 | 435 | 0,046210 | [-0,061; 0,140] | 0,453387 | 1,000000 |
| daily_RTH_close_close_lag1 | 413 | 413 | -0,076626 | [-0,225; 0,079] | 0,351912 | 1,000000 |
| overnight_vs_same_day_RTH | 431 | 431 | -0,098475 | [-0,183; 0,002] | 0,039990 | 1,000000 |

Het aantal intraday paren is geen aantal onafhankelijke waarnemingen. De onzekerheid resamplet dagen, geen losse paren. Daily close-to-close bevat de tussenliggende overnight; de aparte RTH-beweging is open-to-close. Er wordt niet over een ontbrekende vorige geplande sessie heen gesprongen.

### C. Vervolgrendementen na waargenomen extremen

| Event | Horizon | Weging | N | Dagen | Gem. bp | 95%CI gem. | Mediaan bp | 95%CI med. | P05 | P25 | P75 | P95 | Fractie >0 | p nominaal | p Holm43 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RECORD_HIGH | 15m | event | 7699 | 388 | 0,352 | [-0,554; 1,249] | 0,407 | [0,000; 0,873] | -31,037 | -7,785 | 9,100 | 30,105 | 0,515 | 0,445639 | 1,000000 |
| RECORD_HIGH | 15m | equal_event_day | 388 | 388 | -7,323 | [-9,225; -5,591] | -2,126 | [-3,243; -1,411] | -43,498 | -12,063 | 2,549 | 12,502 | 0,371 | 0,000250 | 0,010747 |
| RECORD_HIGH | 60m | event | 7326 | 384 | -0,032 | [-2,734; 2,359] | 2,568 | [0,374; 4,340] | -64,380 | -15,264 | 18,132 | 51,140 | 0,538 | 0,978505 | 1,000000 |
| RECORD_HIGH | 60m | equal_event_day | 384 | 384 | -17,348 | [-21,232; -13,588] | -7,595 | [-11,441; -4,024] | -87,847 | -32,893 | 6,861 | 20,849 | 0,404 | 0,000250 | 0,010747 |
| RECORD_HIGH | rth_close | event | 7940 | 389 | 0,633 | [-5,511; 6,675] | 2,452 | [-1,247; 6,211] | -102,499 | -25,094 | 32,054 | 95,255 | 0,527 | 0,845789 | 1,000000 |
| RECORD_HIGH | rth_close | equal_event_day | 389 | 389 | -33,157 | [-41,829; -25,498] | -12,595 | [-22,650; -6,881] | -169,723 | -62,282 | 13,032 | 46,070 | 0,386 | 0,000250 | 0,010747 |
| RECORD_LOW | 15m | event | 6247 | 400 | 0,460 | [-1,266; 2,197] | 0,796 | [-0,348; 2,240] | -44,630 | -15,236 | 16,093 | 44,522 | 0,516 | 0,597601 | 1,000000 |
| RECORD_LOW | 15m | equal_event_day | 400 | 400 | 11,140 | [9,012; 13,338] | 7,345 | [5,256; 8,837] | -16,613 | -1,542 | 19,427 | 48,758 | 0,710 | 0,000250 | 0,010747 |
| RECORD_LOW | 60m | event | 5887 | 400 | -0,793 | [-4,808; 3,344] | 0,603 | [-2,561; 3,844] | -85,928 | -26,600 | 27,387 | 77,130 | 0,505 | 0,706073 | 1,000000 |
| RECORD_LOW | 60m | equal_event_day | 400 | 400 | 22,545 | [18,756; 26,320] | 16,852 | [13,271; 21,518] | -34,305 | -4,619 | 42,318 | 92,030 | 0,708 | 0,000250 | 0,010747 |
| RECORD_LOW | rth_close | event | 6360 | 400 | -1,348 | [-11,812; 8,620] | 4,156 | [-2,607; 10,018] | -146,288 | -37,721 | 43,415 | 122,682 | 0,529 | 0,789303 | 1,000000 |
| RECORD_LOW | rth_close | equal_event_day | 400 | 400 | 37,357 | [31,205; 43,472] | 28,164 | [20,507; 34,398] | -55,826 | -0,901 | 71,603 | 147,767 | 0,738 | 0,000250 | 0,010747 |
| PDH_TOUCH | 15m | event | 211 | 211 | -2,977 | [-8,196; 1,360] | 0,429 | [-2,746; 4,457] | -59,470 | -13,400 | 15,233 | 39,671 | 0,517 | 0,224194 | 1,000000 |
| PDH_TOUCH | 15m | equal_event_day | 211 | 211 | -2,977 | [-8,196; 1,360] | 0,429 | [-2,746; 4,457] | -59,470 | -13,400 | 15,233 | 39,671 | 0,517 | 0,224194 | 1,000000 |
| PDH_TOUCH | 60m | event | 208 | 208 | -4,084 | [-11,114; 2,153] | -1,528 | [-4,533; 3,840] | -73,015 | -18,535 | 18,523 | 58,885 | 0,490 | 0,222444 | 1,000000 |
| PDH_TOUCH | 60m | equal_event_day | 208 | 208 | -4,084 | [-11,114; 2,153] | -1,528 | [-4,533; 3,840] | -73,015 | -18,535 | 18,523 | 58,885 | 0,490 | 0,222444 | 1,000000 |
| PDH_TOUCH | rth_close | event | 213 | 213 | -0,141 | [-10,294; 9,387] | 6,978 | [1,596; 14,742] | -124,740 | -25,591 | 40,612 | 100,508 | 0,573 | 0,971007 | 1,000000 |
| PDH_TOUCH | rth_close | equal_event_day | 213 | 213 | -0,141 | [-10,294; 9,387] | 6,978 | [1,596; 14,742] | -124,740 | -25,591 | 40,612 | 100,508 | 0,573 | 0,971007 | 1,000000 |
| PDL_TOUCH | 15m | event | 164 | 164 | -4,284 | [-9,088; 0,578] | -0,569 | [-7,043; 4,049] | -54,009 | -23,089 | 14,571 | 36,335 | 0,463 | 0,082729 | 1,000000 |
| PDL_TOUCH | 15m | equal_event_day | 164 | 164 | -4,284 | [-9,088; 0,578] | -0,569 | [-7,043; 4,049] | -54,009 | -23,089 | 14,571 | 36,335 | 0,463 | 0,082729 | 1,000000 |
| PDL_TOUCH | 60m | event | 158 | 158 | -2,062 | [-9,751; 5,358] | 3,302 | [-5,921; 14,055] | -88,646 | -32,968 | 30,283 | 68,039 | 0,519 | 0,584604 | 1,000000 |
| PDL_TOUCH | 60m | equal_event_day | 158 | 158 | -2,062 | [-9,751; 5,358] | 3,302 | [-5,921; 14,055] | -88,646 | -32,968 | 30,283 | 68,039 | 0,519 | 0,584604 | 1,000000 |
| PDL_TOUCH | rth_close | event | 164 | 164 | -5,115 | [-16,620; 6,070] | 3,293 | [-10,515; 14,235] | -121,708 | -48,279 | 39,476 | 105,317 | 0,524 | 0,379905 | 1,000000 |
| PDL_TOUCH | rth_close | equal_event_day | 164 | 164 | -5,115 | [-16,620; 6,070] | 3,293 | [-10,515; 14,235] | -121,708 | -48,279 | 39,476 | 105,317 | 0,524 | 0,379905 | 1,000000 |

**Weging is een ander estimand, geen robuustheidsstempel.** Eventgewogen telt ieder recordmoment even zwaar. Daggewogen neemt eerst per dag het gemiddelde van alle bruikbare events; dat gemiddelde is pas achteraf bekend en hangt af van het uiteindelijke aantal events van die dag. Eventrijke trenddagen en eventarme dagen krijgen daardoor een ander relatief gewicht. Geen van beide is een vooraf uitvoerbare positie of winstberekening. De daggewogen record-effecten mogen niet als tradeable mean-reversion-edge worden gepresenteerd.

De 15m-, 60m- en slotsteekproeven verschillen door rechtscensoring en tijdstip. Het slotvenster heeft variabele lengte. Een eerste PDH/PDL-touch na een gap kan terugkeer uit de andere richting zijn; deze analyse conditioneert niet op de benaderingsrichting. High en low kunnen in dezelfde bar geraakt worden; de volgorde is onbekend. Alle events overlappen mogelijk, maar blijven binnen hun dag geclusterd.

#### Puntverdelingen en werkelijke vensterlengte

| Event | Horizon | N | Gem. punten | Mediaan | P05 | P25 | P75 | P95 | Mediane minuten tot endpoint |
|---|---|---|---|---|---|---|---|---|---|
| RECORD_HIGH | 15m | 7699 | 0,792 | 1,000 | -75,750 | -19,000 | 22,500 | 75,250 | 15,000 |
| RECORD_HIGH | 60m | 7326 | -0,588 | 6,250 | -159,688 | -36,250 | 45,750 | 124,250 | 60,000 |
| RECORD_HIGH | rth_close | 7940 | 1,224 | 6,000 | -258,012 | -63,000 | 79,500 | 231,012 | 304,000 |
| RECORD_LOW | 15m | 6247 | 0,829 | 2,000 | -109,100 | -36,500 | 39,250 | 106,425 | 15,000 |
| RECORD_LOW | 60m | 5887 | -2,155 | 1,500 | -211,675 | -65,125 | 68,500 | 190,675 | 60,000 |
| RECORD_LOW | rth_close | 6360 | -1,839 | 10,250 | -352,500 | -91,312 | 107,562 | 297,012 | 324,000 |
| PDH_TOUCH | 15m | 211 | -6,953 | 1,000 | -142,375 | -32,125 | 37,500 | 112,625 | 15,000 |
| PDH_TOUCH | 60m | 208 | -10,070 | -4,125 | -198,475 | -51,438 | 47,500 | 146,900 | 60,000 |
| PDH_TOUCH | rth_close | 213 | -0,662 | 18,500 | -314,900 | -66,000 | 96,500 | 255,650 | 371,000 |
| PDL_TOUCH | 15m | 164 | -11,416 | -1,500 | -131,275 | -59,062 | 36,062 | 84,637 | 15,000 |
| PDL_TOUCH | 60m | 158 | -4,739 | 8,750 | -206,575 | -79,688 | 74,125 | 176,013 | 60,000 |
| PDL_TOUCH | rth_close | 164 | -14,134 | 7,625 | -304,200 | -113,000 | 99,688 | 240,862 | 360,000 |

### Uitsluitingsregister

| Datum | Contract | RTH-bars werkelijk | RTH-bars gepland | Redenen |
|---|---|---|---|---|
| 2025-01-09 | NQH25 | 0 | 0 | early_close_or_no_full_RTH |
| 2025-01-20 | NQH25 | 210 | 210 | early_close_or_no_full_RTH |
| 2025-02-17 | NQH25 | 210 | 210 | early_close_or_no_full_RTH |
| 2025-05-26 | NQM25 | 210 | 210 | early_close_or_no_full_RTH |
| 2025-06-19 | NQU25 | 210 | 210 | early_close_or_no_full_RTH |
| 2025-07-03 | NQU25 | 225 | 225 | early_close_or_no_full_RTH |
| 2025-07-04 | NQU25 | 210 | 210 | early_close_or_no_full_RTH |
| 2025-09-01 | NQU25 | 210 | 210 | early_close_or_no_full_RTH |
| 2025-11-27 | NQZ25 | 210 | 210 | early_close_or_no_full_RTH |
| 2025-11-28 | NQZ25 | 225 | 225 | early_close_or_no_full_RTH |
| 2025-12-24 | NQH26 | 225 | 225 | early_close_or_no_full_RTH |
| 2026-01-19 | NQH26 | 210 | 210 | early_close_or_no_full_RTH |
| 2026-02-16 | NQH26 | 210 | 210 | early_close_or_no_full_RTH |
| 2026-03-03 | NQH26 | 389 | 390 | missing_or_unexpected_RTH_minutes |
| 2026-04-03 | NQM26 | 0 | 0 | early_close_or_no_full_RTH, missing_09_29_boundary_close |
| 2026-05-25 | NQM26 | 210 | 210 | early_close_or_no_full_RTH |
| 2026-06-19 | NQU26 | 210 | 210 | early_close_or_no_full_RTH |
| 2026-07-03 | NQU26 | 210 | 210 | early_close_or_no_full_RTH |
| 2026-09-07 | NQU26 | 210 | 210 | early_close_or_no_full_RTH |

### Grenzen van deze metingen

All data previously consumed; exploratory conditional associations, not causal mechanisms, executable fills or independent validation. 5day blocks do not guarantee stationarity or eliminate all long-range dependence. Event horizon samples differ by censoring/time of day. No strategy/filter recommendations.

De kalender is de eerder gecontroleerde productspecifieke reconstructie; geen nieuwe CME-certificatie. Leveranciersvintages, tickvolgorde, gebruiksrechten en echte brokerfills zijn niet onafhankelijk bewezen. De volledige recordverdeling per minuut blijft privé; alleen aggregaten worden gepubliceerd.

## Reproductie en verificatie

- `.venv/bin/python -B -m scripts.archive_experiments` controleert de bestaande archiefregistratie; overschrijft die niet.
- `.venv/bin/python -B -m scripts.execution_reality_audit` leest uitsluitend vastgelegde ledgers en code.
- `.venv/bin/python -B -m scripts.raw_market` laadt bron-CSV’s en gebruikt een runtimeblokkade op strategie-, feature- en simulatiefuncties.
- `.venv/bin/python -B -m scripts.publish_market_review` bouwt rapport en aggregatentabellen.
- `.venv/bin/python -m pytest -q`; `npm run typecheck`; `npm run build`.
- `node scripts/verify-year-holdout` verifieert de eerdere twee runs zonder nieuwe signalen.

Protocol SHA-256: `7bb27512a6e431ebedf662521214557d59d9eb38924a99e6c7ee39af76b787f6`.
Bronregister SHA-256: `7ccaec21545428a51cd2cbcce3aa0483c85227faecd33ba7426113888e0d0c71`.
Engine SHA-256: `8fbf6cb7ced7fe0338cca164de1f3cbde8b3d03eb92738bde4616829cd541d8b`.

Geen nieuw handelsmodel, filter, parameterkeuze of promotievoorstel is onderdeel van deze publicatie.
