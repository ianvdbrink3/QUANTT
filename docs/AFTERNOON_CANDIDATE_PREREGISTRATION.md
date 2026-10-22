# Bevroren kandidaat: vast 14:30-UP-cohort, meting vanaf 15:00

Registratiedatum: 22 oktober 2026. ID: `NQ-1430-FIXED-UP-1500-V1`.

Status: **CANDIDATE_SPEC_FROZEN_INDEPENDENT_TEST_NOT_RELEASED**. Dit legt de kandidaat en twee uitkomsten vast. Er is geen nieuwe backtest op de 435 ontdekkingsdagen uitgevoerd. Een toekomstige onafhankelijke toets is nog niet vrijgegeven.

| Onderdeel | Bevroren definitie |
|---|---|
| Tijdzone | America/New_York, DST-bewust |
| Selectietijd | 14:30, uitsluitend voltooide bars 09:30 t/m 14:29 |
| Richting | Close 14:29 strikt boven Open 09:30; vlakke en DOWN-dagen uitgesloten |
| Range | Hoogste High minus laagste Low van 09:30 t/m 14:29 |
| Relatieve range | Range / vooraf bekende ATR14 in **[0,5; 1,2)** |
| ATR | Bevroren contextmodule: rekenkundig gemiddelde van 14 eerdere geldige volledige-RTH true ranges; huidige dag uitgesloten |
| Contractcontinuïteit | Vooraf bekende volume-rollover en causale Panama-spreads uitsluitend voor meerdaagse context; onderzoeksprijzen zijn ruwe actieve contractprijzen |
| Cohortbevriezing | Eenmaal om 14:30; geen herselectie om 15:00 |
| Primaire uitkomst | **15:00 Open → 15:14 Close**, bekend om 15:15 |
| Secundaire uitkomst | **15:00 Open → 15:01 Close**, bekend om 15:02 |
| Rendement | Direct eindclose minus beginopen; inter-bar gaps inbegrepen. Daarnaast 10.000 × ln(eindclose/beginopen) |
| Multipliciteit | Twee tweezijdige toetsen in **één Holm2-familie**, alpha 0,05 |
| Statistische maatstaf | Gemiddeld bruto opwaarts log-bp-rendement per geselecteerde dag; dezelfde bevroren dagscore/HAC(5)-methode, CR1-SE alleen beschrijvend |
| Primaire beoordeling | Positieve primaire schatting én primaire Holm2 p<0,05 nodig voor ondersteuning van positieve drift. Een positieve secundaire toets kan een falende primaire toets niet redden |
| Kosten | Ongewijzigde beschrijvende aftrek 1,225 pt = $24,50 per NQ-roundtrip; geen nieuwe netto-winsthypothese of fill-simulator |
| Uitvoering | Open/close zijn onderzoeksankers, niet bewezen uitvoerbare fills. Geen stops, targets, sizing of geoptimaliseerde vertraging |
| Kwaliteit | Volledige selectieprefix, vooraf bekende ATR en volledig gezamenlijk venster 15:00–15:14 voor beide uitkomsten. Geen imputatie of uitkomstgestuurde uitsluitingen |

De primaire 15-minutenhorizon bestond vóór de minuutinspectie. De hier expliciet gekozen open is niet het oudere 14:59-close-anker. De twee-minutenvariant is achteraf ontdekt. De reeds bekende circa +5,69 punten bruto op het vaste cohort is daarom uitsluitend ontdekkingsinformatie, geen onafhankelijke bevestiging. Geen nieuwe 15:00-rendementen zijn voor deze registratie berekend.

## Grenzen en vrijgavevoorwaarde

- **BAR_START_SUPPORTED_INTERNAL_ONLY**: interne patronen ondersteunen startlabels; exacte secondegrenzen en een eventuele systematische vendorverschuiving zijn niet onafhankelijk gecertificeerd.
- Alle 435 bestaande RTH-dagen van 30 december 2024 t/m 30 september 2026 zijn verbruikt voor ontdekking. Een later onafhankelijke steekproef mag deze niet als nieuwe validatie meetellen.
- Geen tick-, bid/ask-, queue- of latencybewijs voor uitvoering op 15:00:00. Ondersteuning van bruto drift is geen certificering van een netto handelsedge.
- De Treasury-close is geen geïdentificeerde oorzaak. Het effect wordt niet aan die verklaring gekoppeld in de formele hypothese.
- Vóór het lezen van nieuwe uitkomsten moet een afzonderlijk gehasht addendum het exacte onafhankelijke datavenster of een uitkomstonafhankelijk vast stopaantal, informatie-/poweronderbouwing, opwarming, bronhashes en kwaliteitsuitsluitingen vastleggen. Tot dan blijft de toets **niet vrijgegeven**. Geen tussentijds gluren of verlengen na een tegenvallende uitkomst.
- Beide horizons blijven altijd zichtbaar. Geen wisselen van primaire horizon na de uitslag. Ontbrekende of onberekenbare toetsen houden een p=1-plaats in Holm2.

De volledige machineleesbare specificatie staat in `research/afternoon-candidate-v1.json`. Een append-only lock legt de specificatie, dit document en de gebruikte context-/inferentiecode op SHA-256 vast. Dit registreert geen toekomstige gegevensverzameling, betaalde bron, GitHub-push of productie-uitrol.
