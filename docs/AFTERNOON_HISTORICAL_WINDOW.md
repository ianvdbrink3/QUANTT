# Vastgelegd historisch replicatievenster

22 oktober2026. Alleen stap1 en2. Geen nieuwe uitkomsten, cohortselectie, backtest, download of publicatie.

Vast venster: **2019-01-02 t/m 2021-12-31**. Opwarming vanaf **2018-11-19**. Classificatie: `FIXED_HISTORICAL_REPLICATION_WINDOW_NOT_PROSPECTIVE_CERTIFIED`. Status: `DATE_WINDOW_FIXED_OUTCOME_RELEASE_BLOCKED`.

## Waarom deze periode

De oude inventaris begint voor intradaylabels bij 2022-01-02T23:00:00, voor minuutlabels bij 2022-12-26T18:01:00. Daarmee ligt2019-2021 vóór alle daarin aangetroffen intradaybestanden. De technische NQH24-pilot en alle435 ontdekkingsdagen tellen niet mee. De grootst gemelde oude minuutreeks begint pas26december2022, ongeacht de bestandsnaam2022-2025.

**Niet overclaimen:** oudere dag-, week- en maanddata waren al aanwezig en onderzocht. In de geïnspecteerde lokale stukken is geen specifieke15:00-kandidaatuitkomst over2019-2021 aangetroffen. Dat is geen sluitend bewijs van nul eerdere inzage op de hele computer/in alle chats. Dit is historische out-of-period replicatie, geen prospectieve forwardproef en geen gecertificeerd onaangeraakte dataset. Bij bewijs van eerdere kandidaat-specifieke inzage vervalt bevestigende interpretatie; niet automatisch een ander gunstig venster kiezen.

## Stopregel en informatie

De kalender telt783 maandag-vrijdagposities. Dat is nadrukkelijk geen claim over het aantalCME-sessies, schone/eligible dagen of events. Die aantallen blijven onbekend totdat een alleen-kwaliteit-intake met officiële kalender gereed is. De nieuwe blokmeetlat reserveert640 weekdagposities voor uitkomsten en143 voor vooraf gekozen tussenruimte/staart. Daardoor verandert de toetssteekproef expliciet ten opzichte vanv2; geen stille herweging van resultaten.

| Blok | Vanaf | T/m | Weekdagposities |
|---|---|---|---:|
| 1 | 2019-01-02 | 2019-04-23 | 80 |
| 2 | 2019-05-22 | 2019-09-10 | 80 |
| 3 | 2019-10-09 | 2020-01-28 | 80 |
| 4 | 2020-02-26 | 2020-06-16 | 80 |
| 5 | 2020-07-15 | 2020-11-03 | 80 |
| 6 | 2020-12-02 | 2021-03-23 | 80 |
| 7 | 2021-04-21 | 2021-08-10 | 80 |
| 8 | 2021-09-08 | 2021-12-28 | 80 |

Tussen blokken liggen telkens20 weekdagposities zonder bevestigende uitkomst. Die dagen mogen wel causale ATR-opwarming leveren. Minimaal120 geselecteerde gemeenschappelijke observaties totaal en8 per blok; andersDATA_INSUFFICIENT, geen verlenging. De kandidaatregels, twee horizons en1,225pt frictie blijven gelijk. Het historische effect is geen verwachte toekomstige winst.

## Vrijgavepoort

1. Synthetische methoderonde beoordelen. Een falende kalibratie betekent géén methodeswitch en géén eindtoets. Een geslaagde benchmark is geen universele5%-garantie.
2. Eerst alle contract-CSV’s en bronhashes registreren, officiële kalender/haltes/DST verzoenen, volume-rollovers zonder uitkomsten vastleggen en parity met de oude kandidaat bewijzen. Geen parameterwijziging.
3. Beide horizons gebruiken dezelfde volledigeRTH-dagen. Officiële verkorte dagen zijn niet corrupt, maar niet geschikt voor deze volledigeRTH-steekproef. Geen forward-fill, vervangende datum of gunstige endpointverschuiving.
4. Maak vóór uitkomstvrijgave een definitieve bron-/kwaliteitslock. Eén afzonderlijke expliciete vrijgave is nog nodig. Geen tussentijdseP&L, stop zodra significant, uitbreiding bij tegenvaller of samenvoegen met de435 ontdekkingsdagen.
5. BAR_START_SUPPORTED_INTERNAL_ONLY en ontbrekend tick/BBO/fill-bewijs blijven staan. Zelfs statistische ondersteuning valideert geen gegarandeerd uitvoerbaar/live winstgevend model.

Exacte kwaliteitseisen en stopregel: `research/afternoon-historical-window.json`. Exacte bestandslijst: `docs/NQ_HISTORICAL_DOWNLOAD_LIST.md` en machineleesbareJSON. Deze registratie wijzigtv2/de huidige pointer niet en publiceert niets.
