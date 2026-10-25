# Rolling prop-challenge simulator

EXPLORATORY_ROLLING_ACCOUNT_RESEARCH_NOT_INDEPENDENT_VALIDATION

Exploratieve selectie op reeds gebruikte ontwikkelingsdata. Rolling vensters overlappen; percentages zijn historische frequenties, geen onafhankelijke slagingskans. Geen orders, aankopen of funded-certificering.

## Vast universum en noemers

{"combinations": 319, "profiles": 9, "valid_cells": 2487, "excluded_cells": 384, "ranking_rows": 14922}

{"2019_2021": {"sessions": 749, "start": "2019-01-14", "end": "2021-12-31", "windows": {"21": 729, "42": 708, "63": 687}}, "2024_2026": {"sessions": 422, "start": "2025-01-27", "end": "2026-09-30", "windows": {"21": 402, "42": 381, "63": 360}}}

Alle volledige 21/42/63-sessievensters binnen elk echt tijdperk; nooit over de datakloof heen. De 21-sessiebenadering is niet exact 30 kalenderdagen. Private uitkomsten blijven lokaal.

## Ranglijst per firma en horizon

### TOPSTEP · 21 sessies

| Combinatie | Sizing | Pass oud % | Pass recent % | Pass samen % | Fail % | Bron onbeslist % | Trades/poging | Kosten/pass $ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 5.90 | 18.16 | 10.26 | 29.35 | 43.24 | 7.69 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_AM | FIXED_3 | 5.76 | 17.41 | 9.90 | 29.80 | 43.68 | 7.24 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 5.49 | 18.91 | 10.26 | 30.06 | 42.09 | 7.89 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_AM | FIXED_3 | 5.49 | 18.16 | 9.99 | 30.50 | 42.79 | 7.43 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 5.35 | 17.66 | 9.73 | 30.68 | 42.62 | 8.41 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 5.21 | 17.41 | 9.55 | 31.12 | 43.32 | 7.98 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1 | FIXED_3 | 5.08 | 18.91 | 9.99 | 28.91 | 43.94 | 7.56 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 4.94 | 18.16 | 9.64 | 31.21 | 41.73 | 8.69 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 4.94 | 17.66 | 9.46 | 31.65 | 42.35 | 8.26 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+SB_AM | FIXED_3 | 4.94 | 15.17 | 8.58 | 24.14 | 46.24 | 6.38 | onbeslist |

0/2487 cellen halen de vooraf genoteerde beschrijvende 10%-grens in beide tijdperken. Dit is geen validatielabel.
Geen combinatie met zowel die tweeperiodegrens als een volledig opgeloste kostenproxy.

### TOPSTEP · 42 sessies

| Combinatie | Sizing | Pass oud % | Pass recent % | Pass samen % | Fail % | Bron onbeslist % | Trades/poging | Kosten/pass $ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S2_STOP050+J1M_TIME+PULLBACK+SB_AM | FIXED_3 | 14.83 | 23.88 | 18.00 | 24.06 | 51.61 | 8.33 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 14.55 | 20.21 | 16.53 | 32.32 | 47.66 | 9.23 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 13.84 | 19.16 | 15.70 | 31.86 | 48.85 | 9.06 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 13.56 | 19.42 | 15.61 | 33.61 | 47.20 | 10.13 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 13.56 | 18.90 | 15.43 | 32.32 | 49.04 | 9.88 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1 | FIXED_3 | 13.42 | 20.47 | 15.89 | 31.96 | 48.67 | 9.17 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+SB_AM | FIXED_3 | 13.28 | 21.52 | 16.16 | 25.99 | 51.24 | 7.65 | onbeslist |
| S2_STOP050+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 12.99 | 20.21 | 15.52 | 35.08 | 46.19 | 9.52 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 12.85 | 18.90 | 14.97 | 34.07 | 47.29 | 9.64 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1 | FIXED_3 | 12.71 | 19.42 | 15.06 | 31.59 | 49.77 | 8.89 | onbeslist |

62/2487 cellen halen de vooraf genoteerde beschrijvende 10%-grens in beide tijdperken. Dit is geen validatielabel.
Laagste onvoorwaardelijke kostenproxy onder die grens: NONE+J0830+ICT1+SB_AM+SB_PM / CUSHION_400 / $838.25

### TOPSTEP · 63 sessies

| Combinatie | Sizing | Pass oud % | Pass recent % | Pass samen % | Fail % | Bron onbeslist % | Trades/poging | Kosten/pass $ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| NONE+JBULL0930+PULLBACK+ICT1+SB_PM | RISK_400 | 21.98 | 24.17 | 22.73 | 49.47 | 0.00 | 18.42 | 702.82 |
| NONE+JBULL0930+PULLBACK+ICT1+SB_AM+SB_PM | RISK_400 | 20.52 | 35.83 | 25.79 | 50.14 | 0.00 | 18.26 | 625.57 |
| NONE+J1M_TIME+PULLBACK+ICT1+SB_PM | RISK_400 | 20.38 | 21.94 | 20.92 | 50.14 | 0.00 | 18.29 | 726.26 |
| NONE+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | RISK_400 | 19.65 | 35.28 | 25.02 | 52.63 | 0.00 | 17.64 | 616.37 |
| NONE+JBULL0930+ICT1+SB_PM | RISK_400 | 19.65 | 28.33 | 22.64 | 46.32 | 0.00 | 15.25 | 706.40 |
| NONE+J1M_TIME+ICT1+SB_PM | RISK_400 | 18.92 | 21.39 | 19.77 | 48.62 | 0.00 | 15.17 | 762.57 |
| NONE+J1M_TIME+ICT1+SB_AM+SB_PM | RISK_400 | 18.78 | 35.28 | 24.45 | 49.67 | 0.00 | 14.89 | 623.69 |
| NONE+JBULL0930+ICT1+SB_AM+SB_PM | RISK_400 | 18.63 | 35.83 | 24.55 | 49.19 | 0.00 | 15.23 | 652.73 |
| S2_STOP050+J1M_TIME+PULLBACK+SB_AM | FIXED_3 | 17.03 | 28.33 | 20.92 | 24.83 | 53.68 | 8.75 | onbeslist |
| NONE+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 16.89 | 25.00 | 19.68 | 38.59 | 0.00 | 16.92 | 756.74 |

207/2487 cellen halen de vooraf genoteerde beschrijvende 10%-grens in beide tijdperken. Dit is geen validatielabel.
Laagste onvoorwaardelijke kostenproxy onder die grens: NONE+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM / RISK_400 / $616.37

### MFFU_EOD · 21 sessies

| Combinatie | Sizing | Pass oud % | Pass recent % | Pass samen % | Fail % | Bron onbeslist % | Trades/poging | Kosten/pass $ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S2_NO_STOP+J1M_TIME+ICT1+SB_AM | FIXED_3 | 3.98 | 3.23 | 3.71 | 52.25 | 41.73 | 6.17 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 3.98 | 3.23 | 3.71 | 49.16 | 42.00 | 7.09 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 3.84 | 2.99 | 3.54 | 49.07 | 42.26 | 7.38 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_PM | FIXED_3 | 3.02 | 2.99 | 3.01 | 49.07 | 42.62 | 7.01 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 3.98 | 2.74 | 3.54 | 49.34 | 41.64 | 7.50 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_PM | FIXED_3 | 2.88 | 2.74 | 2.83 | 48.63 | 42.97 | 7.29 | onbeslist |
| S2_NO_STOP+J0830+ICT1+SB_AM+SB_PM | FIXED_3 | 2.61 | 2.74 | 2.65 | 47.13 | 44.12 | 7.38 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1 | FIXED_3 | 2.88 | 2.49 | 2.74 | 52.17 | 42.44 | 6.12 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_PM | FIXED_3 | 2.88 | 2.49 | 2.74 | 48.98 | 42.62 | 7.43 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1+SB_PM | FIXED_3 | 2.88 | 2.49 | 2.74 | 48.45 | 42.79 | 7.74 | onbeslist |

0/2487 cellen halen de vooraf genoteerde beschrijvende 10%-grens in beide tijdperken. Dit is geen validatielabel.
Geen combinatie met zowel die tweeperiodegrens als een volledig opgeloste kostenproxy.

### MFFU_EOD · 42 sessies

| Combinatie | Sizing | Pass oud % | Pass recent % | Pass samen % | Fail % | Bron onbeslist % | Trades/poging | Kosten/pass $ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S2_NO_STOP+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 4.38 | 3.94 | 4.22 | 51.42 | 43.43 | 7.60 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 4.24 | 3.94 | 4.13 | 51.24 | 43.71 | 7.88 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 4.10 | 3.94 | 4.04 | 51.52 | 43.53 | 8.38 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_AM | FIXED_3 | 3.81 | 3.94 | 3.86 | 52.71 | 43.43 | 6.52 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 4.38 | 3.67 | 4.13 | 51.88 | 43.07 | 8.07 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_AM | FIXED_3 | 4.10 | 3.67 | 3.95 | 53.17 | 42.88 | 6.27 | onbeslist |
| S2_STOP075+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 3.81 | 3.67 | 3.76 | 53.17 | 43.07 | 6.97 | onbeslist |
| S2_NO_STOP+J1M_TIME+PULLBACK+ICT1+SB_AM | FIXED_3 | 3.81 | 3.41 | 3.67 | 53.54 | 42.79 | 6.73 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_PM | FIXED_3 | 3.39 | 4.46 | 3.76 | 51.24 | 44.08 | 7.48 | onbeslist |
| S2_STOP075+J1M_TIME+ICT1+SB_PM | FIXED_3 | 3.25 | 4.46 | 3.67 | 50.96 | 44.44 | 7.77 | onbeslist |

0/2487 cellen halen de vooraf genoteerde beschrijvende 10%-grens in beide tijdperken. Dit is geen validatielabel.
Geen combinatie met zowel die tweeperiodegrens als een volledig opgeloste kostenproxy.

### MFFU_EOD · 63 sessies

| Combinatie | Sizing | Pass oud % | Pass recent % | Pass samen % | Fail % | Bron onbeslist % | Trades/poging | Kosten/pass $ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S2_NO_STOP+J0830+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 3.20 | 3.61 | 3.34 | 47.18 | 49.47 | 8.60 | onbeslist |
| S2_NO_STOP+J0830+PULLBACK+ICT1+SB_PM | FIXED_3 | 3.20 | 3.33 | 3.25 | 46.99 | 49.76 | 8.56 | onbeslist |
| S2_NO_STOP+J0830+ICT1+SB_AM+SB_PM | FIXED_3 | 2.77 | 4.17 | 3.25 | 49.38 | 47.37 | 8.08 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_PM | FIXED_3 | 2.77 | 3.89 | 3.15 | 52.53 | 44.32 | 7.44 | onbeslist |
| S2_NO_STOP+J0830+ICT1+SB_PM | FIXED_3 | 2.77 | 3.33 | 2.96 | 49.76 | 47.28 | 8.09 | onbeslist |
| S2_STOP075+J0830+PULLBACK+ICT1+SB_AM+SB_PM | FIXED_3 | 2.77 | 3.33 | 2.96 | 48.90 | 48.14 | 9.01 | onbeslist |
| S2_STOP075+J0830+PULLBACK+ICT1+SB_PM | FIXED_3 | 2.77 | 3.06 | 2.87 | 48.62 | 48.52 | 8.99 | onbeslist |
| S2_NO_STOP+J1M_TIME+ICT1+SB_AM+SB_PM | FIXED_3 | 2.62 | 3.89 | 3.06 | 52.53 | 44.41 | 7.56 | onbeslist |
| S2_NO_STOP+NONE+ICT1+SB_AM+SB_PM | FIXED_3 | 2.62 | 3.89 | 3.06 | 52.82 | 44.13 | 7.36 | onbeslist |
| S2_NO_STOP+NONE+ICT1+SB_PM | FIXED_3 | 2.62 | 3.89 | 3.06 | 52.63 | 44.32 | 7.21 | onbeslist |

0/2487 cellen halen de vooraf genoteerde beschrijvende 10%-grens in beide tijdperken. Dit is geen validatielabel.
Geen combinatie met zowel die tweeperiodegrens als een volledig opgeloste kostenproxy.

## Bron- en uitvoeringskwaliteit

{
  "signal_counts": {
    "J0830": {
      "orders": 153,
      "fills": 100,
      "late_excluded": 0
    },
    "JBULL0930": {
      "orders": 84,
      "fills": 57,
      "late_excluded": 0
    },
    "J1M_TIME": {
      "orders": 128,
      "fills": 90,
      "late_excluded": 0
    },
    "ICT1": {
      "orders": 253,
      "fills": 208,
      "late_excluded": 253
    },
    "SB_AM": {
      "orders": 36,
      "fills": 26,
      "late_excluded": 0
    },
    "SB_PM": {
      "orders": 168,
      "fills": 134,
      "late_excluded": 0
    },
    "PULLBACK": {
      "orders": 121,
      "fills": 121,
      "late_excluded": 28
    }
  },
  "cutoff_checks": 1224,
  "kernel_parity": "EXACT_FROZEN_STRICT_FILL_PRICE_PARITY",
  "night_quality": {
    "S1_STOP050": {
      "trades": 102,
      "incomplete": 15
    },
    "S2_NO_STOP": {
      "trades": 735,
      "incomplete": 104
    },
    "S2_STOP050": {
      "trades": 735,
      "incomplete": 101
    },
    "S2_STOP075": {
      "trades": 735,
      "incomplete": 104
    }
  }
}

## Kosteninterpretatie

Topstep: $49 per begonnen 21-sessieblok plus $149 activatie per geslaagde poging. Apart worden echte kalenderdatums en 30-dagen-rebilling berekend. Reset $49 vervangt heraanschaf $49; geen dubbeltelling. $99 is uitsluitend een gevraagde stressaanname, niet de officiële 50K-resetprijs.
MFFU: Rapid EOD 50K, $225 eenmalige lijstprijs, geen maandverlenging en $0 activatie. Promotieprijzen en belasting niet verwerkt. $3,22 roundtrip is daar een gestandaardiseerde kostenaanname, geen bevestigde MFFU-quote.
Kosten/pass = totale kosten van alle pogingen / geslaagde pogingen + activatie. Dit is een empirische herstartproxy; bij een horizonlimiet worden onvoltooide pogingen als beëindigd verondersteld. Het is geen exacte optimale resetplanning of onafhankelijke verwachtingswaarde. Bij onbesliste bronpaden blijft de onvoorwaardelijke kostenproxy leeg. De resolved-path proxy mag niet als ranglijstredding worden gebruikt.

## Grenzen van de conclusie

Een model dat veel trades neemt is niet automatisch beter. Een losse voor-10:15 Judas-entry kan tot15:55 bezet blijven en blokkeert late pijlers. De nieuwe gestapelde modellen en sizingregels zijn niet out-of-sample getoetst. Selecteren op de hoogste rolling passrate is extra data-mining; geen promotion naar gevalideerd.
1-minuut OHLC bewijst geen queuefills of tickvolgorde. De adverse bar-bound kan een verliesvloer conservatief raken die met bekende open/closeprijzen niet aantoonbaar geraakt is. Onbekende nachtminuten veroorzaken een apart onbeslist resultaat. NQ-prijzen zijn een MNQ-proxy; een deel van2019 ligt vóór MNQ-introductie.
Topstep kan tijdelijk microcontractlimieten verlagen; een geverifieerde volledige historische nieuwskalender ontbreekt voor deze actuele2026regels. Daarom zijn accountpercentages conditioneel aan het gesimuleerde regelprofiel en geen volledige prop-compliance. MFFU-inactiviteit gebruikt een conservatieve kalenderdagdiagnose; exacte activatietijd is onbekend.

## Exacte vastgelegde methode

- **status**: EXPLORATORY_ROLLING_ACCOUNT_RESEARCH_NOT_INDEPENDENT_VALIDATION
- **date**: 2026-10-25
- **baseline**: 2d4b795de9547951ab2ed755b4d4dfa08fb37255
- **sample**: All1171 cash dates in two eras, with pre-existing ATR/SMA warmup. Every start with a full21/42/63session followup for that horizon. No2021--2024 bridge, no flat missingyears, no same-date multiple minis/micros. Different horizon denominators and omitted right-edge starts explicit.
- **universe**: 319 combinations:5night choices includingnone x4morning choices includingnone x16subsets of4late components minusempty. Nine sizing profiles. No-stop night cannot be assigned finite exact-stop dollar risk:384 inadmissible cells reported,2487valid combination/sizing cells. No forced12--30 tradequota or extra signals.
- **selection**: Only existing kernels. Published TRADE_THROUGH results select SB_AM/PM by maximum minimum-era dailyATRSharpe among variants positiveATR inboth eras; ties minimum-era ATR then name. Chosen AM5m bullCONT2R, PM1m bothCONT2R. ICT1 fixed1m bothON3R. Original pullback firstsignal restricted to>=10:15, as are first ICT1/AM orders; no search for a later signal after exclusion. Three Judas specs exact, no newMSS.
- **overlap**: One account position or pending limit at a time. Order activation sorts first, then prioritynight,Judas,ICT1,SBAM,pullback,SBPM. Busy until confirmedexit minute+1 for intrabar exit, or exactopen exit. No early flatten at10:15, no using later fill/PnL to choose an earlier candidate. Sizing rejection doesnot reserve order slot. Unfilled placedlimits do reserve it. No netting across sleeves.
- **execution**: Frozen causal strict1tick trade-through entry and stop-first unresolvedSL/TP. Night exact18:00 andnext09:30 samepreknown contract, .50/.75priorATR stops rounded towardentry. .75andbroad.50 are NEW research overlays. No gapfill clipping. No tickcertificate at18:00:05, no MNQquote/queueproof; historicalNQproxy includes pre-MNQlaunch data.
- **sizing**: FIXED1/2/3. RISK200/300/400=floor(budget/(2USD*actualstoppts+3.22)), max3night/max10intraday, firmcapapplied. Budgetsmallerthan1MNQ=>skip. CUSHIONsamebase:headroom<1500=>0.5x, else realizednet>750=>1.5x. New-orderbudget halves at80% ofconsistency*3000dailyprofit;zero at100%. Cushionbudget<=headroom-100. No retroactive winnerclipping, no sizedtargetoptimization; actualgapriskunbounded.
- **floor**: Startnet0,floor-2000; MLL tested through heldbar adverseOHLC and observedopen/close separately. Conservative possiblebreach counted separately from observed. Ratchet onlyEOD to max(previous,min(lock,peakEOD-2000)), lockTopstep0/MFFU100. EODpassafterallclosedtrades, net>=3000, bestday<=consistency*net, minimumactivecashdays2/4. No DLL unlessspecified, no invented ceilinglossfill.
- **gaps**: Missing scheduled holdingminute beforeactualexit creates UNRESOLVED_SOURCE_PATH, never retroactive signalfilter or zero-filled survival. Knownpricebreach strictly beforegap may terminate first. Unknown remains inall-start denominator. Primarypasslower=knownpasses/N; sourceupper=(knownpasses+unknown)/N. Conditionalresolvedcost labeled; no unconditionalcostclaim withunknownpaths.
- **firms**: Current2026 TopstepTC50K55%/EOD2000 and MFFURapidEOD50K30%/EOD2000,min4,7calendarday inactivity. Inactivity conservative day-level clock from activation/lastactualfill, no keepalive; exactvendoractivationtimestampunknown. These tests do not certify allrisk/newsrestrictions or futurefundedpayouts. Defaultmax10MNQ can exceed temporaryTopstep3micro newswindowcap; withoutverifiedhistoricaleventcalendar allrankingsremain conditional.
- **costs**: 3.22USD/MNQroundtrip once peractualfill, charged atentry; fixed1.22fee+assumed2slippage notcurrentMFFUquote. MainTopstep49initial+49per21sessionextension,149activationperpass. Calendar30dayrebilling sensitivity uses realdates separately. MFFUEOD225listpriceonce,norenewal,noactivation;promos/VATexcluded. Topstepreset49 REPLACES49freshentry,neverdoublecharged;99reset isuserstressnotofficial50Kprice. Costproxy=sumattemptfees/passes+activation assumes restartafterhorizon and empiricalretry mix; overlapping starts are not independent renewaltrials. Unknownpaths=>unconditionalcostnull.
- **ranking**: Sort eligible min(era21passrate)>=10% separately from allcells; this transparent researchscreen isnot evidence of healthyfutureodds. Mainrankingmin-era pass thencombinedpass thenfee; costrankingseparate. Costeligible requires resolvedunconditionalcost inboth eras. Showallrows,including failures,unknowns,lowvolume andzeros. Nonoverlapping-phase0 starts reported as dependencecheck; no binomialCI/confirmatoryp on overlappingstartwindows.
- **publication**: Two fresh source reconstructions, deterministicprivatecandidates/outcomes andpublicaggregate byteparity. All744 priortrackedfiles byteidentical; localuncommittedbot notsilentlypublished. Publiconlyaggregates, fullrankingCSV, methodologyandinteractivepage. No brokerorders,noaccountcreation,nopurchases.

## Officiële bronnen

- [topstep_parameters](https://help.topstep.com/en/articles/8284197-trading-combine-parameters)
- [topstep_floor](https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit)
- [topstep_consistency](https://help.topstep.com/en/articles/8284208-consistency-at-topstep)
- [topstep_subscription](https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions)
- [topstep_pricing](https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions)
- [topstep_risk_adjustments](https://help.topstep.com/en/articles/13613539-risk-adjustments-high-risk-high-volatility)
- [mffu_parameters](https://help.myfundedfutures.com/en/articles/16158363-rapid-eod-50k-a-comprehensive-look)
- [mffu_eval](https://help.myfundedfutures.com/en/articles/11802636-traders-evaluation-simplified)
- [mffu_prices](https://myfundedfutures.com/)
- [mffu_hours](https://help.myfundedfutures.com/en/articles/9558251-permitted-times-to-trade)
