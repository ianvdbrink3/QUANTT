# December-overlap en bulkdata: besluit 21 oktober 2026

## Conclusie

Het kleine december-overlapgat is daadwerkelijk gedicht en onafhankelijk van strategie-uitkomsten gecontroleerd. Voor de verdere verzameling is Databento historische pay-as-you-go minuutdata mijn eerste kandidaat: de openbare calculator toont **$9,51 voor vijf jaar NQ OHLCV-1m**, circa **145,9 MB**, zonder abonnement. Ik selecteerde expliciet NQ E-mini Nasdaq-100 Futures, niet Micro NQ, met weergegeven UTC-datums 30 september 2021–30 september 2026. Dit is een prijsraming, geen accountgebonden definitieve offerte of bewijs van precieze intraday-dekking. De bestaande Barchart-bron blijft de referentie voor de bevroren onderzoekslijn. Er is niets gekocht, geen account aangemaakt en geen toekomstig handelsresultaat bekeken.

## 1. Wat nu daadwerkelijk op schijf staat

Via de bestaande aangemelde Barchart Premier-sessie zijn vier bedoelde bestanden opgehaald en hash-gecontroleerd opgeslagen in de genegeerde lokale raw-map:

| Contract | Gekozen Chicago-kalenderdatums | Bars |
| --- | --- | ---: |
| NQZ25 | 10–19 december 2025 | 9.692 |
| NQH26 | 30 november–9 december 2025 | 3.015 |
| NQH26 | 8–17 december 2025 | 8.244 |
| NQH26 | 16–19 december 2025 | 5.100 |

De 26.051 nieuwe bronregels zijn niet hetzelfde als nieuwe actieve bars: contracten en downloadblokken overlappen. Alle vier blijven als afzonderlijke oorspronkelijke bestanden bewaard. SHA-256, eerste/laatste UTC-tijdstempel, contract en rijenaantal staan in de nieuwe openbare herkomstexport. De ruwe bars blijven privé.

Een vijfde download kwam door verkeerd ingevulde Barchart-datumvelden uit op februari–maart 2026 en de recordlimiet. Die is na schema-/datumbereikcontrole expliciet uitgesloten en niet aan de raw-map toegevoegd. Het oorspronkelijke downloadbestand is niet verwijderd. Ook daarop zijn geen features of signalen berekend. De uitsluiting is vastgelegd zodat de downloadhistorie niet ten onrechte als foutloos of nooit ingezien wordt voorgesteld.

Barchart-datums zijn Chicago-tijd, niet New York en niet UTC. Daarom begint het eerste incoming-blok op zondag 30 november: de avondsessie hoort bij de civil-NY handelsdatum 1 december. De adapter zet expliciet America/Chicago naar UTC om en gebruikt de bestaande 18:00–17:00 New York-sessiedefinitie. Dit is niet automatisch de officiële clearing-TradeDate.

## 2. Rollover en kwaliteit, zonder handelsuitkomsten

De bestaande volume-regel is ongewijzigd hergebruikt. Alleen voltooide sessies tellen. Een incoming contract moet de bestaande start-/einddekking halen en strikt meer contractvolume hebben dan het outgoing contract. De switch wordt pas de volgende sessie actief. Een voorafgaande boundary-gekwalificeerde outgoing-dominante sessie is ook aanwezig.

De eerste kwalificerende crossover is sessiedatum **15 december 2025**. De actieve overgang naar NQH26 is daarom **handelsdatum 16 december**, vanaf **15 december 18:00 New York / 23:00 UTC**. De gemeenschappelijke 15:59 NY-close die de spread bepaalt, is beschikbaar om 16:00 NY, vóór activering. Dit levert geen toestemming op om indicatoren of strategieën te draaien.

Over de geselecteerde actieve reeks 1–19 december:

- 15 gewone handels-/sessiedatums.
- 20.700 unieke bars, precies 15 × 1.380 minuten.
- 15 volledige sessies en 15 volledige overnight-tot-12:00-prefixen.
- Nul ontbrekende actieve minuten en nul conflicterende OHLCV-overlap.
- 7.458 identieke overlapregels verwijderd binnen de onderzochte contractblokken, inclusief overlap met bestaande bronnen. Prijzen zijn niet aangepast.
- Strategie-eligible dagen: bewust **niet berekend**.

De incoming NQH26-reeks is vóór de liquiditeitsmigratie veel dunner. Dat is geen reden om ontbrekende minuten automatisch op te vullen of het actieve NQZ25-contract af te keuren. Na de overstap is juist de actieve NQH26-reeks volledig. Het expirerend NQZ25-bestand eindigt op 19 december om 09:29 NY; dat wordt niet als een vereiste volledige actieve handelsdag behandeld.

De gewone-weekdagkalender is slechts voor 1–19 december uitgebreid in een aparte auditregistratie. De historische kalender en bevroren rapporten zijn niet herschreven. Kerst en de volledige 2026-productkalender blijven afzonderlijk te controleren. Het resultaat is een technisch sterke vendor-audit, geen CME-certificering of garantie dat geen enkele broncorrectie ooit zal optreden.

Reproductie: `npm run verify:december-overlap`. Dit controleert geregistreerde hashes opnieuw, reconciliëert overlap en bepaalt uitsluitend kwaliteit en volume-switch. `--stage` kopieert byte-identiek en weigert afwijkende bestaande bestanden. `--publish` exporteert alleen geaggregeerde kwaliteit en herkomst, geen marktprijsbars, dagelijkse volumes, spreadprijzen of strategie-uitkomsten.

## 3. Bulkroute: vergelijking

| Route | Wat is bevestigd? | Kosten binnen €25–€50? | Besluit |
| --- | --- | --- | --- |
| Databento historical usage-based | CME Globex, OHLCV-1m, afzonderlijke instrumenten, API/batch, geen verplicht maandabonnement voor historische pay-as-you-go | Openbare vijfjaarsraming NQ: $9,51 / 145,9 MB, dus waarschijnlijk ruim passend. Exacte aanvraag/valuta/btw/rechten nog bevestigen | Eerste keuze om exact te laten offreren |
| Barchart bestaande Premier-sessie | Werkende CSV-downloads, contracten, 1 minuut, maximaal 20.000 records per verzoek | Deze downloads vragen geen nieuwe aankoop in de huidige sessie. Bestaand abonnement is niet daardoor gratis | Zelfde-bron terugvalroute voor de huidige holdout |
| FirstRate Data NQ | Individuele contracten plus continuous, 1m-bestanden en ruime historie | Aanschafprijs was niet zichtbaar in tekstweergave of ingeladen productpagina. $99,95 betreft jaarlijkse updates, niet bewezen de aanschafprijs | Reserveoptie, eerst concrete aankoopprijs en licentie bevestigen |

Databento biedt nieuwe teams $125 tegoed, één keer per team, met zes maanden geldigheid. Dat is niet hetzelfde als onbeperkte gratis historische data. Het tegoed kan verlopen of al verbruikt zijn. De voorgestelde route vereist geen Standard-abonnement van $199 per maand. Er is geen account aangemaakt of kredietsaldo ingezien.

De gratis metadata-/symbology-API kan een prijsraming geven voordat historische tijdreeksen worden besteld. Het volgende concrete product is daarom een definitieve afgebakende prijsopgave, geen automatische download. De publieke calculator is inmiddels daadwerkelijk bediend en het bedrag gecontroleerd; er is niet op Start request geklikt. Kosten hangen af van symbolen, schema en periode. CSV versus JSON maakt de onderliggende factureringsbasis niet gratis. Herhaald streamen kan opnieuw kosten; een goed afgebakende batch verdient daarom de voorkeur na goedkeuring.

FirstRate biedt naast bewerkte continuous ook afzonderlijke contracten. Alleen die laatste passen rechtstreeks bij onze eigen rollovercontrole. De licentie staat intern onderzoek en bepaalde afgeleide publicaties toe, maar kent beperkingen op verspreiding en vraagt bronvermelding bij publicatie. Dat is geen vrijbrief om ruwe bestanden in een publieke repo of dashboard te zetten. Licentievoorwaarden moeten voor het werkelijke gebruik worden beoordeeld, ook bij Databento en Barchart.

## 4. Exacte aanvraag die nu voorbereid is

De machineleesbare aanvraag staat in `research/bulk-data-request-plan.json`, zonder API-sleutel en zonder koopbevoegdheid:

1. **NQ resterende verzamelperiode** na de nu gecontroleerde decemberweek t/m 30 september 2026. Schema OHLCV-1m, GLBX.MDP3, alleen NQ-outrights. Vraag eerst de prijs en recorddekking op. De civil-NY sessiegrenzen worden naar UTC omgerekend.
2. **NQ vijfjaarsvergelijking** oktober 2021–september 2026, apart geprijsd. Dit is een dataverzameloptie, geen nieuwe definitie van onafhankelijke holdout.
3. **ES vijf jaar**, alleen als afzonderlijke optionele offerte. ES is niet noodzakelijk voor de bevroren NQ-hypothese. Een extra instrument automatisch mee testen zou opnieuw onderzoek en multipliciteit toevoegen.

Een parent-aanvraag zoals NQ.FUT bevat meerdere individuele looptijden, niet alleen het frontcontract. Dat bewaart overlap maar kan duurder zijn dan gerichte contractvensters. Voor die laatste moeten eerst vendor-instrumentdefinities en expiraties worden gemapt. Barchart-symbolen met tweecijferig jaar mogen niet blind als Databento raw symbols worden gebruikt.

Een complete offerte moet bruto USD, bruikbaar tegoed, netto USD, eventuele btw/valutakosten, recordaantallen, bytes, exacte dekking en rechten voor lokale analyse en geaggregeerde publicatie tonen. Pas daarna is vast te stellen of dit binnen het eerdere budget past. Zonder expliciete aankooptoestemming volgt geen betaalde aanvraag of nieuw abonnement.

## 5. Belangrijkste methodologische risico: wisselen van leverancier

Echte beursdata van twee leveranciers hoeft niet dezelfde minuutbars op te leveren. Barchart vermeldt dat intraday-downloads alleen transacties meenemen die voor een nieuwe last price kwalificeren. Databento documenteert eigen aggregatie-/timestampconventies, geen bar als er niet is gehandeld, en mogelijke verschillen door trade conditions en correcties.

Dat kan invloed hebben op highs/lows, volumes, VWAP-proxy, RVOL en dus signalen, ook bij identieke strategieregels. Alleen de toekomstige periode op een andere leverancier testen en verschillen volledig aan marktregime toeschrijven zou daarom onzorgvuldig zijn.

Vóór een overstap hoort een **vendor-bridge-audit op de al verbruikte 2025-data**: dezelfde individuele contracten/minuten vergelijken op tijdzone, barlabels, datagaten, kwartpuntticks, OHLC-afwijkingen, volumes en inputpariteit. De vendor wordt niet gekozen op toekomstige winst. Bij materiële verschillen blijft de bevroren Barchart-test gescheiden, of volgt een expliciet aparte databron-/engineversie met vooraf vastgelegde beoordeling. Geen stilzwijgende vermenging.

Minuut-OHLCV bevat bovendien geen werkelijk aantal transacties/ticks, spread, aggressor of koersvolgorde binnen de minuut. Volume/ticks kan niet betrouwbaar uit alleen OHLCV worden gereconstrueerd. Voor werkelijk microstructuuronderzoek hoort trades/TBBO een afzonderlijke kosten-/noodzaakafweging te krijgen, niet alvast de duurdere standaarddownload te worden.

## 6. Wat ik adviseer om nu wel en niet te doen

**Wel:** deze decemberaanvulling bewaren; de nieuwe crossover vastleggen; eerst NQ-minuutbulk exact prijzen; eventuele bronwissel op verbruikte overlap controleren; kalender, rechten en resterende dekking afronden voordat de toekomstige test wordt vrijgegeven.

**Niet:** een los kwartaal tussentijds scoren, de frozen regels aanpassen, kooptegoed met gegarandeerd gratis verwarren, meerdere jaren reeds bekeken data als nieuwe onafhankelijke bevestiging presenteren, of de vijfjaarsoptie verkopen als garantie op significantie.

De eerdere circa 12% kwartaalpower en 38% jaarpower waren scenario's bij een verondersteld echt effect van +10 netto punten per geschikte dag en de gemeten historische spreiding. Ze zijn geen vast natuurkundig kenmerk van NQ. Afhankelijkheid, regimewisselingen, selectie, kosten en effectgrootte kunnen het benodigde aantal dagen veranderen. Meer kalenderjaren helpt doorgaans met precisie, maar creëert op zichzelf geen edge en herstelt geen gebruikte holdout.

De volledige toekomstige periode is nog niet gereed. Het decembergat is nu gesloten, maar de resterende NQH26-/NQM26-/NQU26-/NQZ26-dekking, overlaps en bijzondere beursuren moeten nog worden verzameld/gecontroleerd. De status blijft **holdout niet gescoord**.

## Bronnen, gecontroleerd 21 oktober 2026

- [Databento prijzen en historisch pay-as-you-go](https://databento.com/pricing/).
- [Databento tegoedvoorwaarden en facturering](https://databento.com/docs/faqs/usage-pricing-and-data-credits).
- [Databento metadata, symbology en get_cost](https://databento.com/docs/api-historical).
- [Databento OHLCV-conventies](https://www.databento.tech/docs/schemas/ohlcv).
- [FirstRate NQ individuele contracten](https://firstratedata.com/i/futures/NQ) en [licentie](https://firstratedata.com/about/license).
- [Barchart NQH26 downloadpagina en ingebouwde Help](https://www.barchart.com/futures/quotes/NQH26/historical-download).
- [CME handelsuren](https://www.cmegroup.com/trading-hours.html) en [NQ contractpagina](https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html). De dynamische contractpagina leverde geen complete historische productkalender in tekstweergave op.
