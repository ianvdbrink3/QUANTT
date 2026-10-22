# 15:00-kandidaat v2: twee parallelle primaire horizons

Registratiedatum: 22 oktober 2026. ID: `NQ-1430-FIXED-UP-1500-V2`.

Status: **CANDIDATE_SPEC_FROZEN_INDEPENDENT_TEST_NOT_RELEASED**.

Deze versie vervangt v1 voor een toekomstige onafhankelijke toets. V1 en de eerdere ochtendrapporten blijven byte-identiek als historisch beslisspoor. Er is voor deze wijziging geen nieuwe 15:00-backtest of uitkomstberekening op de 435 ontdekkingsdagen uitgevoerd.

| Onderdeel | V2-specificatie |
|---|---|
| Cohort | Vast om 14:30 NY, uitsluitend voltooide 09:30–14:29-bars. Close 14:29 strikt boven Open 09:30; range / vooraf bekende ATR14 in [0,5; 1,2) |
| ATR en rollover | Dezelfde bevroren causale context, eerdere 14 geldige RTH true ranges, vooraf bekende Panama-basis voor indicatoren; ruwe actieve contractprijzen voor beide horizons |
| Parallelle primaire toets 2m | 15:00 Open → 15:01 Close, bekend om 15:02 |
| Parallelle primaire toets 15m | 15:00 Open → 15:14 Close, bekend om 15:15 |
| Netto maatstaf | Eindclose − beginopen − **1,225 NQ-punten** per geselecteerde dag; $24,50 vaste roundtripfrictie, multiplier $20/punt |
| Nulhypothese | Per horizon gemiddeld netto puntenrendement = 0; tweezijdige p-waarde. Positieve geschatte netto verwachting vereist voor positieve ondersteuning |
| Onzekerheid | Bestaande dag-invloedscores, Bartlett HAC(5), geselecteerde-dagen-correctie en t-vrijheidsgraden N−1. Eén inferentiemaatstaf: netto NQ-punten. Bruto punten/log-bp alleen beschrijvend |
| Multipliciteit | Eén Holm-familie van twee parallelle primaire toetsen, FWER alpha 0,05 |
| Holm-regel | Sorteer p(1)≤p(2). Eerste verwerping bij p(1)<0,025. Alleen als die nulhypothese verworpen is, kan p(2)<0,05 de tweede verwerpen. Equivalent: aangepaste p(1)=min(1,2p(1)); aangepaste p(2)=max(aangepaste p(1),p(2)) |
| Succes per horizon | Eigen Holm2-p<0,05 én eigen geschatte gemiddelde netto punten >0. Geen vereiste dat de andere horizon economisch positief of significant is |
| Familiesucces | Minstens één horizon voldoet aan zijn eigen succesregel. Altijd beide resultaten publiceren, ook negatieve. Dit is een disjunctieve regel, niet de co-primaire regel waarbij beide moeten slagen |
| Geen hiërarchische reddingsblokkade | De 2m-horizon mag ondersteuning krijgen wanneer de 15m-horizon faalt, en omgekeerd. De enige step-down-afhankelijkheid is de reguliere Holm-correctie op gerangschikte p-waarden, niet een inhoudelijke horizonvolgorde |
| Gemeenschappelijke steekproef | Dezelfde vooraf vastgelegde volledigheids- en kwaliteitsregels voor beide horizons. Geen uitkomstgestuurde verschuiving van labels, selectie, horizon of kosten |

## Expliciete wijziging ten opzichte van v1

V1 berekende al beide p-waarden met Holm2. De aanvullende primaire/secundaire interpretatieregel was een strengere beslisregel, geen fixed-sequence uitvoering die de tweede toets niet berekende. V2 verwijdert die aanvullende afhankelijkheid en maakt beide horizons parallel primair.

V2 toetst **netto punten tegen nul**, niet uitsluitend bruto log-bp tegen nul plus een losse positieve nettoschatting. Daardoor moet ondersteuning betrekking hebben op de vooraf gekozen frictieaanname. Dit is nog steeds geen bewijs van werkelijk haalbare fills of live winstgevendheid.

De twee-minutenhorizon is achteraf ontdekt op verbruikte data. De eerdere niet-significante restantmetingen bewijzen niet dat minuut 3–15 nul of zuivere ruis zijn. De eerder getoetste REST-component was bovendien 15:01–15:15 (14 minuten), niet een afzonderlijk getoetst 15:02–15:15-venster.

## Ongewijzigde beperkingen en vrijgavevoorwaarden

- **BAR_START_SUPPORTED_INTERNAL_ONLY**; geen onafhankelijke certificatie van exacte secondegrenzen of afwezigheid van een vendor-labelverschuiving.
- Alle 435 dagen van 30 december 2024 t/m 30 september 2026 blijven ontdekkingsdata. Geen nieuwe toets op deze dagen voor v2.
- Geen tick-, bid/ask-, queue- of latencybewijs voor uitvoering op 15:00:00 of de gekozen eindclose. Vaste kosten bewijzen geen uitvoerbaarheid.
- Geen geïdentificeerde Treasury-close-oorzaak, geen stops/targets, geen sizing of uitvoeringstuning.
- Geen onafhankelijke run vrijgegeven voordat een afzonderlijk addendum datavenster of uitkomstonafhankelijke stopregel, informatie-/poweronderbouwing, opwarming, bronhashes en uitsluitingen vastlegt. Geen optional stopping of verlenging na een tegenvallende uitslag.
- Ontbrekende/onberekenbare toetsen blijven met p=1 in de Holm2-familie. Een negatieve significante horizon is geen positieve kandidaat, maar wordt wel onverkort gerapporteerd.
- Deze lokale registratie autoriseert geen GitHub/Vercel-publicatie of toekomstige backtest.

De machineleesbare versie staat in `research/afternoon-candidate-v2.json`. `research/afternoon-candidate-current.json` wijst v2 aan als actuele specificatie. Een afzonderlijke v2-lock bewaart ook de v1-hashes.
