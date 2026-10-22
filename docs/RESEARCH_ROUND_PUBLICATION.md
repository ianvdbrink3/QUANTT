# Definitieve vastlegging onderzoeksronde — 22 oktober 2026

## Besluit

`AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md` is de enige actuele formele kandidaat. Beide horizons zijn parallel co-primair binnen Holm2. De onafhankelijke toets is nog niet vrijgegeven; de bestaande 435 dagen blijven ontdekkingsdata.

`MORNING_RECOVERY_ANATOMY.md` en `MORNING_RECOVERY_PRECISION.md` zijn afgesloten beschrijvende rapporten (`CLOSED_DESCRIPTIVE_NOT_CANDIDATE`). Dit is een onderzoeksbesluit wegens beperkte precisie en brede excursies, geen universeel bewijs dat ochtendherstel afwezig is.

De drie publieke Markdown-downloads zijn byte-identieke kopieën. Eerdere lokale publicatiebeperkingen in deze historische rapporten worden niet herschreven; de gebruiker heeft deze release later expliciet toegestaan. Het register en `/research/nq#research-round` tonen de actuele status.

## Uitgevoerde lokale releasecontroles

- Volledige suite: **420 tests geslaagd** (414 bestaande + 6 publicatiecontroles).
- Typecontrole en productiebuild geslaagd; statisch dashboard bevat alle drie rapportlinks en beide actuele onderzoeksstatussen.
- `npm run verify:research`: volledige bronreproductie geslaagd; 106.678 bars, 42 eligible dagen, 37 ORB15-trades, +919,425 punten.
- `npm run verify:holdout`: volledige historische bronreproductie geslaagd; 81 eligible dagen, 76 ORB15-trades, -627,60 punten, `HOLDOUT_FAILED` ongewijzigd.
- `npm run verify:continuous -- --output <nieuwe genegeerde lokale map>`: historische continuous-reproductie exact gelijk aan de bestaande publieke referentie. Geen publicatie-overschrijving.
- `node scripts/verify-year-holdout`: 69 bronhashes en beide reeds vastgelegde jaarreproducties gecontroleerd; byte-identieke resultaten; geen derde jaar-scoring.
- `npm run verify:freeze`: 73 bevroren bestanden ongewijzigd. Archiefcontrole: 115 beschermde bestanden en vier modellen `ARCHIVED_NOT_VALIDATED` ongewijzigd.
- Hash-/replaybewijs gecontroleerd voor causal-map, afternoon-specificity/falsification, kandidaat v1/v2 en beide ochtendrapporten. Geen nieuwe 15:00-backtest, geen nieuwe hypothese of optimalisatie.

## Publicatiegrens

`scripts/publish_research_round.py` exporteert uitsluitend de drie rapporten, bevroren specificatie, geaggregeerde tabellen en afsluitstatus. `research/research-round-publication.json` registreert de SHA-256 van alle 14 publieke bestanden. Het gedeelde register is uitgebreid; uitsluitend de navigatie-indexhash van de oude falsificatiepublicatie is daarop bijgewerkt. De oude wetenschappelijke rapporten blijven ongewijzigd.

De productierelease wordt vanuit een apart webpakket opgebouwd: uitsluitend `app`, `components`, `lib`, `public` en expliciete bouwconfiguratie. Geen private CSV's, bronbars, meetarrays, lokale artifacts, virtuele omgeving of privé-datamappen. De volledige 420-testcontrole en bronreproducties zijn lokaal uitgevoerd; dit document claimt geen onafhankelijke CI-run zonder private bronnen.
