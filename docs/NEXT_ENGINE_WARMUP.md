# Overlap-first ATR voor de volgende engineversie

De bevroren 0.9-engine en haar publieke resultaten blijven ongewijzigd. Deze
versie is een aparte onderzoeksingang, geen stilzwijgende wijziging van productie.

`scripts/reproduce_research/next_engine.py` biedt `ContractATRCache` en
`prepare_with_overlap(full, schedule, calendar_grid=..., require_day1_atr=True)`.
Geef ALLE opgeschoonde contractbars mee, inclusief inactieve overlap; pas de
actieve-contractselectie nooit vóór deze ingang toe. Gebruik `Activation`-objecten
voor de vooraf vastgelegde rollovers. De cache neemt uitsluitend 14 geldige,
vooraf afgesloten RTH true ranges van hetzelfde contract op. De huidige dag en
latere dagen beïnvloeden de startstatus niet. Bij onvoldoende historie stopt de
standaardingang vóór featureberekening met `WarmupNotReady`. Alleen diagnostiek
mag de expliciete optie `require_day1_atr=False` gebruiken; dit forceert geen ATR
of eligibility. Geen forward-fill, kortere ATR of overdracht van contractprijzen.

De bestaande 0.9-engine berekent features al vóór actieve selectie. De verbetering
is dus een expliciete cache en een controle vóór de berekening, geen magische
herstelmethode voor ontbrekende historie. De cache wordt onafhankelijk vergeleken
met de contracteigen ATR van de bestaande featureberekening. De tijdelijke
kalenderinjectie volgt de bestaande onderzoeksarchitectuur; deze ingang is voor
één proces/run, niet voor gelijktijdige kalenderconfiguraties in meerdere threads.

Tests: `.venv/bin/python -m pytest tests/test_next_engine.py -q`.
De positieve end-to-endtest gebruikt complete synthetische overlap en controleert
dat alle vier bestaande strategieën werkelijk eligible zijn op de eerste
rolloverdag. Andere tests bewijzen blokkering bij onvoldoende historie en bij een
ontbrekende prefixminuut, geen look-ahead, geen cross-contract prijssprong,
duplicate-afwijzing en verplichte tijdzone/schedule-validatie. ATR-gereed betekent
niet automatisch dat overige kwaliteits- en volumevoorwaarden vervallen.

Reproduceerbare audit van de bestaande dataset en referenties:

```
.venv/bin/python -m scripts.reproduce_research.audit_next --run artifacts/holdout-7u52wd25
```

De runmap moet de geverifieerde private holdout-bestanden bevatten. De audit
controleert alle 30 bronhashes, de bevroren code/protocol/referentie en zes private
outputhashes. Hij controleert de cache tegen alle geselecteerde sessies en schrijft
alleen naar de genegeerde map `artifacts/next-engine-audit/`. Geen nieuwe
strategieparameters, publieke exports, Git-push of deployment.

Met de huidige bestanden zijn NQU25 op 17 juni en NQZ25 op 17 september NIET
dag-1-gereed: respectievelijk 1 en 2 geldige voorafgaande true ranges. Voor een
garantie zonder uitval is voldoende complete contracteigen voorgeschiedenis nodig
(doorgaans minstens 15 complete RTH-sessies; bij gaten meer). De bestaande data
kan die garantie niet dragen. Geen succesvolle test mag dat suggereren.
