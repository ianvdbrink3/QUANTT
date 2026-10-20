# ORB 15m post-mortem en contracteigen ATR-opwarming

Beschrijvend onderzoek op inmiddels bekeken data. Geen parameteroptimalisatie, nieuwe edgeclaim of wijziging aan de bevroren 0.9-engine/holdout.

## Vergelijking van de vooraf bestaande eligible sessies

| Maatstaf | In-sample: 42 eligible dagen | Holdout: 81 eligible dagen |
|---|---:|---:|
| Gemiddelde ORB15, punten | 129.44 (n=42) | 89.87 (n=81) |
| Gemiddelde ORB15 / eerdere ATR, % | 29.23 (n=42) | 28.91 (n=81) |
| Gemiddelde eerdere 14-RTH ATR, punten | 466.72 (n=42) | 355.52 (n=81) |
| Gemiddelde gerealiseerde RTH-range die dag, punten | 474.04 (n=41) | 264.09 (n=79) |
| Gemiddelde MFE tot exitbar, bovengrens in punten | 115.92 (n=37) | 62.27 (n=76) |
| Gemiddelde MAE tot exitbar, bovengrens in punten | 74.36 (n=37) | 56.76 (n=76) |
| Gemiddelde MFE / ATR, exitbar-bovengrens | 0.28 (n=37) | 0.19 (n=76) |
| Gemiddelde MAE / ATR, exitbar-bovengrens | 0.16 (n=37) | 0.17 (n=76) |
| Gemiddelde MFE eerste vaste 15 minuten, punten | 73.64 (n=37) | 35.84 (n=76) |
| Gemiddelde MAE eerste vaste 15 minuten, punten | 52.35 (n=37) | 34.83 (n=76) |

De openingsrange was in absolute punten kleiner en de eerdere RTH-ATR lager. De openingsrange als percentage van die ATR bleef vrijwel gelijk. De winst kwam in-sample volledig uit shorts; in de holdout werden juist shorts verlieslatend. De snelle terugkeer in de ORB-range nam niet toe. Dit onderbouwt geen verhaal dat meer snelle failed breakouts het verlies veroorzaakten.

ATR is de ongewijzigde SMA van de laatste 14 geldige RTH true ranges, uitsluitend vóór de onderzochte dag en van hetzelfde contract. De gerealiseerde dagrange is een aparte achterafmeting, geen signaalinput. ORB/ATR-statistiek betreft alle eligible dagen; MFE/MAE betreft alleen de werkelijk geselecteerde trades.

## Long versus short

| Periode/richting | Trades | Netto punten | Gemiddelde/trade | Winrate | PF |
|---|---:|---:|---:|---:|---:|
| In-sample long | 18 | -213.55 | -11.86 | 44.44% | 0.78 |
| In-sample short | 19 | 1132.98 | 59.63 | 63.16% | 2.71 |
| Holdout long | 33 | 29.08 | 0.88 | 54.55% | 1.03 |
| Holdout short | 43 | -656.67 | -15.27 | 30.23% | 0.67 |

## Failed breakout: definitie vóór deze beschrijvende telling

Een terugkeer betekent ten minste één voltooide minuutclose binnen de oorspronkelijke 09:30–09:45 ORB-range, inclusief de grenzen. De klok start bij de echte entry (minuut na het signaal). Primair betekent direct: binnen de eerste 5 minuten. Ook 1 en 15 minuten worden getoond, niet gebruikt om een parameter te kiezen. Dit zijn vaste post-entryvensters, onafhankelijk van een eerdere SL/TP-exit; dus geen handelssignaal of claim dat de positie bij terugkeer nog open was.

| Venster | In-sample | Holdout |
|---|---:|---:|
| 1 minuten | 7/37 (18.92%) | 8/76 (10.53%) |
| 5 minuten | 15/37 (40.54%) | 28/76 (36.84%) |
| 15 minuten | 22/37 (59.46%) | 43/76 (56.58%) |

Bij de entry-open al binnen de range: 1 in-sample en 0 holdout.
MFE/MAE tot exit gebruikt de oorspronkelijke bar-bounds: de high/low van de exitminuut kan na de exit zijn ontstaan. De vaste 15-minutenpaden zijn marktbeschrijving na entry, geen alternatief doorgerekend exitmodel. Uit minuutbars is de exacte intrabarvolgorde niet afleidbaar.

## ATR-rolloverdiagnose

**De engine warmt het niet-actieve contract al op vóór de selectie van het actieve contract.** `build_features(full)` draait per contract over alle beschikbare bronbars; pas daarna wordt de rolloverselectie toegepast. Er is geen bewuste reset op de rollover. De beperking is de kwaliteit en lengte van de contracteigen RTH-historie.

| Inkomend contract | Overlapdagen vóór roll | Volledige RTH vóór roll | Geldige TR vóór roll | Eerste ATR-ready dag | Actieve dagen zonder ATR² |
|---|---:|---:|---:|---|---:|
| NQU25 | 11 | 2 | 1 | 2025-07-11 | 18 |
| NQZ25 | 12 | 3 | 2 | niet bereikt t/m 30 september | 10 |

² Alleen de datums waarop dit contract actief is binnen de beschikbare onderzoeksperiode, niet een voorspelling voor latere dagen.
Voor een geldige true range moeten zowel de huidige als de voorafgaande geobserveerde sessie een volledige RTH hebben. Een dun verhandeld contract met veel minuten zonder bar mist daardoor meer dan alleen kalenderdagen. Feestdagen en een enkele ontbrekende RTH-minuut kunnen de 14 geldige observaties verder spreiden.

## Volgende engine-generatie: ontwerp, niet retrospectief toegepast

1. Bewaar een contracteigen as-of-featurestaat, ook voor niet-actieve contracten. Sleutel: contract, RTH-definitie, kwaliteitsbeleid, bronhash en laatste voltooide sessie. Nooit een doorlopende back-adjusted reeks als ATR-bron gebruiken.
2. Voer vóór iedere roll een readiness-gate uit: >=14 geldige eerdere TR-observaties, controle op vorige close en afzonderlijk voldoende same-clock volumehistorie en complete overnight-prefix. Niet alleen ATR bepaalt eligibility.
3. Bestaande overlap hergebruiken is al ondersteund en geeft met deze bestanden geen nulverlies. Verzamel voor volgende studies voldoende eerdere contracteigen historie vóór de roll. Onder de strikte volledige-minuutregel is doorgaans minstens 15 volledige RTH-sessies nodig; feestdagen/gaten kunnen meer geschiedenis vereisen.
4. Alternatief uitsluitend voor een nieuwe, vooraf vastgelegde engine: betrouwbare contracteigen RTH-dagaggregaten met exact dezelfde 09:30–16:00 NY-definitie en aantoonbare as-of-beschikbaarheid, of expliciete vendorbevestiging dat ontbrekende minuten echt geen transacties betekenen. Niet stilzwijgend lege minuten forward-fillen of ontbrekende bars als bewezen nulhandel behandelen.
5. Nul ATR-uitval bij roll is alleen mogelijk als die gate vooraf slaagt. Geen garantie met de huidige ruwe bestanden; geen features van het uitgaande contract lenen. De bevroren HOLDOUT_FAILED-uitkomst blijft intact.

## Interpretatiegrenzen

Dit vergelijkt geselecteerde eligible dagen en trades, niet alle kalenderdagen. De septembercontract-warmup veroorzaakt selectieve dekking. Verschillen in volatiliteit of failed-breakoutpercentages zijn beschrijvende samenhang, geen aangetoonde oorzaak van verlies. Er is geen parameter of richting gewijzigd en geen nieuwe strategie geselecteerd.

Reproduceren: eerst `npm run verify:holdout`, daarna `npm run diagnose:orb15`. Bron- en inputhashes staan in de publieke diagnose-export; ruwe bars en uitvoeringsprijzen blijven privé.
