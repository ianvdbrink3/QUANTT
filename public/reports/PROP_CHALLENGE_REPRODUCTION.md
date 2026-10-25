# Rolling prop-challenge — reproductie en interpretatie

Deze module is een afzonderlijke onderzoeksuitbreiding. De eerdere 744 vastgelegde bestanden, signalen, prijsseries, bronregistraties en gepubliceerde resultaten blijven ongewijzigd. Het systeem verstuurt geen orders en maakt geen prop-accounts aan.

## Reproduceren

Gebruik de bestaande Python-onderzoeksomgeving met `requirements-lock.txt` en `requirements-historical-evidence.txt` en de privé-bronbestanden in de bestaande lokale datamappen. Publiceren van de software verleent geen rechten op de brondata.

```sh
.venv/bin/python -m scripts.prop_challenge register
.venv/bin/python -m scripts.prop_challenge replay
.venv/bin/python -m scripts.prop_challenge verify
.venv/bin/python -m scripts.prop_challenge publish
.venv/bin/python -m pytest tests/test_prop_challenge.py -q
```

`replay` reconstrueert de geselecteerde kernels en nachttrajecten twee keer vanaf de geregistreerde bronnen. Dit kan geruime tijd duren. De twee numerieke runs, ranglijsten, broncontrole, kandidaatregisters en compacte lokale rolling ledgers moeten byte-identiek zijn. De werkwijze en het eindige universum staan in `research/prop-challenge-registration.json`; de codehashes staan afzonderlijk in `research/prop-challenge-code-lock.json`. De enige opslagamendering vervangt grote redundante JSON-startvensters door deterministische binaire compressie; regels en parameters veranderen daarmee niet.

`scripts/verify-prop-challenge` biedt hetzelfde commando zonder de bevroren package.json te wijzigen:

```sh
.venv/bin/python scripts/verify-prop-challenge verify
```

Privé-uitvoer staat onder `artifacts/prop-challenge/run1` en `run2`. Een binaire ledger bevat per combinatie, sizingprofiel, firma, tijdperk en horizon alle startuitkomsten. De volgorde van starts volgt de afzonderlijke `cash-calendar.json`. Iedere start met een volledig opvolgvenster komt precies eenmaal voor. De laatste 20/41/62 datums zonder volledig venster voor die horizon worden expliciet niet meegerekend. Geen start wordt over de datakloof heen vervolgd.

`scripts.prop_challenge.read_outcomes` is een importeerbare lezer: `read(path)` geeft de celkop en een NumPy-structuurarray terug. De velden zijn status, sessies tot uitkomst, tradeaantal, rekeningcoördinaat, 21-sessie factureringskosten, werkelijke kalenderfactureringskosten, overlapweigeringen, sizingweigeringen en totale contracten. Bij een floorbreuk is het veld `net` uitsluitend een marker op de geraakte verliesgrens, geen nagebootste liquidatiefill of werkelijk realiseerbare eind-P&L. De simulator gebruikt die marker nooit om verder te handelen en leidt er geen verliesverwachting uit af. Er staan geen bron-OHLCV-arrays in de publieke export.

## Exacte strekking

- 319 samengestelde modellen, negen sizingprofielen, 2.487 toegestane model/sizingcellen, twee firma's en drie horizons. De 384 overige cellen hebben een ongestopte nachtpositie en kunnen dus niet als exact stop-dollarbudget worden gesized.
- De AM/PM Silver Bullet-keuze is gemaakt op de reeds gepubliceerde ontwikkelingsresultaten, met de laagste Sharpe van de twee perioden als maatstaf. Dit is uitdrukkelijk geen onafhankelijke selectie.
- De eerste bestaande pullback/ICT-1/AM-order wordt uitsluitend toegelaten vanaf 10:15. Een eerder eerste signaal wordt niet vervangen door een later, achteraf aantrekkelijker signaal.
- Werkelijke orderactivatie en positiebezetting bepalen de overlap. Een ongevulde, geplaatste limietorder blokkeert ook nieuwe signalen. Een door sizing geweigerde order blokkeert niet.
- De floor stijgt uitsluitend op het dagslot, maar kan door open verlies intraday worden geraakt. Bij éénminuut-OHLC blijft soms alleen een conservatieve mogelijke breuk aantoonbaar; deze staat los van een bekende open/closebreuk.
- Ontbrekende holdingminuten leiden vanaf het eerste gat tot een onbesliste bronuitkomst, niet tot fictieve survival of retroactieve signaaluitsluiting. Bekende verliezen strikt vóór het gat kunnen eerder een floorbreuk vaststellen.
- De bestendigheid van signalen en het uitblijven van bugs bewijzen geen toekomstige winstgevendheid. De 1.171 sessies zijn al ingezien. Er wordt niet gepromoveerd naar een onafhankelijk gevalideerd model.

## Kosten

De primaire simulator gebruikt de expliciet gevraagde benadering van 21 handelsdagen per maand. Een tweede berekening telt 30 kalenderdagen vanaf iedere start op de echte datums. Beide zijn rekenconventies voor evaluatiepogingen; de exacte checkout-/activatietijd is niet bekend.

Topstep gebruikt $49 per begonnen periode en $149 activatie per geslaagde poging. Een $49 reset vervangt een verse $49 evaluatie en wordt niet dubbel geteld. De gevraagde $99 reset is alleen een stressscenario. Er wordt geen optimale resetdatum gezocht.

MFFU Rapid EOD 50K gebruikt een eenmalige lijstprijs van $225, geen maandverlenging en geen activatiekosten. Actuele promoties en belasting veranderen het aankoopbedrag. $3,22 per MNQ-roundtrip is een uniforme onderzoeksaanname en geen bevestigde MFFU-kostenquote.

De kosten per pass zijn een empirische herstartproxy: alle betaalde pogingen, inclusief onvoltooide pogingen die bij de horizon worden beëindigd, gedeeld door het aantal passes, plus activatie. Overlappende starts vormen geen onafhankelijke reeks herhaalde aankopen. Bij een onbeslist bronpad is de onvoorwaardelijke kostenproxy niet vast te stellen. De apart gemarkeerde resolved-path-kosten zijn conditioneel en kunnen selectievertekening bevatten. Automatiseringsabonnementen, VPS, wisselkoers, btw en toekomstige funded-payoutvoorwaarden zijn niet inbegrepen.

## Publiceren

De nieuwe pagina `/research/prop-challenge` en een toegevoegde layout-link op `/research/prop-firm` laten de oude onderzoeksbestanden intact. De releasebuilder neemt uitsluitend gecommitteerde frontendbestanden, openbare aggregaten en rapporten mee. Privé-CSV's, de lokale bot, individuele tradeledgers en rolling startvensters gaan niet naar Vercel.

`python -m scripts.publish_prop_challenge` maakt de uitgebreide publieke CSV met afzonderlijke regels per tijdperk en gecombineerde boekhouding, inclusief floorbreuktypen, kalenderfacturering en de resetkostensensitiviteit. Dit commando voert geen extra signalen of parameterzoektocht uit.
