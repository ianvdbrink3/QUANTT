# Trading 212: feitelijke startcontrole en demo-protocol

30 oktober 2026. Status: **NOT_READY_FOR_DEMO_TRADING**. De echte Invest-demo is lokaal alleen-lezen gekoppeld; nul orders. De software is verder uitgewerkt, maar een volledige orderproef mag pas starten wanneer de nog ontbrekende product- en koersbewijzen aanwezig zijn. Geen historische prestaties worden aan andere fondsen toegeschreven.

## Wat daadwerkelijk is vastgesteld

De officiële demo-REST-API accepteert de lokaal ingevoerde sleutels. Rekeningoverzicht, posities, openstaande orders, instrumentcatalogus, beursroosters, transacties en dividenden zijn uitgelezen. De administratie sluit aan. De sleutel heeft brede rechten, maar de lokale configuratie staat op ADVICE_ONLY en de daadwerkelijk gebruikte REST-client weigert POST en DELETE. Er worden dus ook geen oude orders stilzwijgend geannuleerd terwijl de agent alleen-lezen staat.

De dienst draait via macOS launchd en controleert iedere minuut. Slaapstand en netwerkuitval kunnen deze werking onderbreken. De dienst past geen energie- of beveiligingsinstellingen aan. Een heartbeatgat tijdens de vereiste sessie wordt geregistreerd; een gemist ordermoment levert geen inhaalorder op.

Het rekeningbudget voor de strategie blijft maximaal 1.000, met de bestaande reserve van max(10, 1%). Extra virtueel demogeld telt niet als ongemelde positieruimte. S1 blijft uit. De bestaande signaalkernel, profielgewichten en historische prestatiebestanden worden niet gewijzigd.

## Zes stappen en hun bewijs

| Stap | Feitelijk geleverd | Nog nodig voor de volledige proef |
|---|---|---|
| 1 Exacte producten | Echte catalogus, ISIN, EUR-noteringen, issuerstructuur en beursroosters gecontroleerd; eigen dagdata apart opgeslagen en gehasht | Fractiegeschiktheid, minimumorder, prijstik en uitvoerbaarheid op jouw demo; productdatavrijgave; geen gelijkstelling met QQQ/TQQQ |
| 2 Dagelijkse agent | Nieuwe onveranderlijke Yahoo-bronnen, dezelfde vaste berekeningen, onafhankelijke Nasdaq-controle en hercontrole iedere 15 minuten bij publicatievertraging | De slotdatum moet daadwerkelijk bij beide bronnen gepubliceerd zijn |
| 3 Administratie | Duurzame outbox, geen blinde POST-herhaling, gedeeltelijke/late fills, cashpaginering en bron-/codebinding van proefdagen | Werkelijke demo-fills moeten na expliciete start nog worden waargenomen |
| 4 Controlekamer | Actuele lokale status plus gedateerde openbare publicatiestand, volledige startcheck en productoverzicht | Openbare website is geen brokerverbinding en heeft geen orderknoppen |
| 5 Brokerclient | Echte demo-authenticatie en alleen-lezen aansluiting bewezen | Exacte verse uitvoeringsquotes en vrijgegeven productbindingen |
| 6 Twintig sessies | Vast protocol, kalender, kwalificatie en storingsproeven | **0/20 echte gekwalificeerde sessies**; geen fixture of replay wordt als echte demodag geteld |

## Exacte productinventarisatie

| Broker-ticker | ISIN | Notering | Juridische vorm | Beursrooster |
|---|---|---|---|---|
| EQQQm_EQ | IE0032077012 | EUR, Milan | Uitkerende UCITS ETF |75|
| XNASd_EQ | IE00BMFKG444 | EUR, Xetra | Herbeleggende UCITS ETF |166|
| QQQ3m_EQ | IE00BLRPRL42 | EUR, Milan | Swapgebaseerd, gedekt schuld-ETP met dagelijkse 3× blootstelling |75|

De catalogus noemt QQQ3 een ETF. De issuer en beurs classificeren het als schuld-ETP/ETN. Dat bredere brokerlabel vervangt de juridische productcontrole niet. Het product is geen TQQQ. Een EUR-notering maakt de onderliggende valutablootstelling niet automatisch afgedekt.

De [officiële Trading 212-productpagina voor QQQ3.IT](https://www.trading212.com/nl/trading-instruments/invest/QQQ3.IT) is ook rechtstreeks in Safari geopend. De pagina bevestigt EUR, Borsa Italiana en ISIN IE00BLRPRL42. De algemene tekst over fracties vanaf €1 bewijst niet de productspecifieke rechten of orderminimums van deze rekening. Na afzonderlijke toestemming is via deze productpagina ook QQQ3 · MIL in de ingelogde Invest-oefenomgeving geopend, gevolgd door het lege aankoopticket in EUR. Geen bedrag of aantal is ingevuld; Order bekijken en orderbevestiging zijn niet bediend. Het lege ticket toonde geen bevestigde minimumorder of prijstik. Het is zonder order verlaten. Deze beperkte inspectie bevestigt de aanwezigheid van het product en ticket, maar bewijst nog geen fractionele fill, minimumorder, prijstik of API-orderacceptatie.

De bronnen zijn de [Invesco-productpagina](https://www.invesco.com/uk/en/financial-products/etfs/invesco-eqqq-nasdaq-100-ucits-etf-dist.html), [Xtrackers-productpagina](https://etf.dws.com/en-gb/IE00BMFKG444-nasdaq-100-ucits-etf-1c/), [WisdomTree-productpagina](https://www.wisdomtree.eu/en-ie/etps/equities/wisdomtree-nasdaq-100-3x-daily-leveraged) en de [Milanese instrumentpagina](https://www.borsaitaliana.it/borsa/etc-etn/scheda/IE00BLRPRL42-ETFP.html).

Het brokerrooster ondersteunt maandag 2 november 2026 om 09:31 New York voor de gecontroleerde EUR-noteringen. Door de Amerikaanse wintertijdwissel is dat **15:31 Nederland**. Het rooster wordt echt opnieuw opgehaald wanneer de metadata een uur oud is; hergebruik van een cache verlengt zijn vervaldatum niet.

## Producthistorie: controle zonder nieuwe strategie-backtest

De nieuwe eigen bronbestanden blijven lokaal en worden niet in bestaande datasets verwerkt. Gecontroleerd is op unieke datums, valuta, notering, niet-eindige waarden, niet-positieve prijzen en OHLC-samenhang.

| Dagbron | Rijen | Eerste–laatste datum | Niet-eindige bars | OHLC buiten eigen range | Totaal verdachte bars |
|---|---:|---|---:|---:|---:|
| EQQQ.MI |2.497|2017-01-02–2026-10-30|2|75|77|
| XNAS.DE |1.470|2021-01-27–2026-10-30|2|0|2|
| QQQ3.MI |2.497|2017-01-02–2026-10-30|2|142|144|

Alle drie hebben nul dubbele datums. Bij EQQQ liggen75 OHLC-afwijkingen meer dan één cent buiten de aangegeven range; bij QQQ3 zijn dat 121. Er is geen automatische reparatie, forward-fill of verwijdering toegepast. De precieze datums staan alleen in het lokale auditbestand. Dit onderscheidt een bronafwijking van een bewezen marktfout: oorzaak en correctie zijn nog niet onafhankelijk vastgesteld.

XNAS heeft geen eigen 2019/2020-prijshistorie in deze bron. De eigen producthistorie wordt dus niet kunstmatig verlengd met QQQ. Dag-openprijzen van Europese beurzen bewijzen ook geen uitvoering om 09:31 New York. Deze audit is geen rendementstest en rechtvaardigt geen overname van bestaande CAGR-, Sharpe- of drawdowncijfers.

## Dagbronnen: publicatievertraging blijft zichtbaar

De primaire signaalinputs blijven de gecontroleerde afgeronde US-dagbars. De nieuwe Nasdaq-parser eist een succesvolle inhoudelijke respons, het juiste symbool, exact één rij voor de gevraagde datum en een eindige positieve slotprijs. HTTP200, een gisterenrij en een lege tabel tellen niet als bevestiging.

De controle op 29 oktober 2026 is met echte bronbytes uitgevoerd. Verschil met Yahoo: QQQ ongeveer 0,000375 bp en TQQQ 0,000308 bp, dus binnen de al bestaande 10 bp-datakwaliteitsgrens. Dat bewijst de aansluiting voor 29 oktober, niet voor de nog niet bevestigde 30 oktober. Dezelfde datum wordt bij vertraging iedere 15 minuten opnieuw gecontroleerd, zonder de primaire inputbestanden te overschrijven.

Stooq gaf bij deze controle HTML met een browserverificatie terug. Dat is geen koers-CSV. De agent omzeilt die controle niet en geeft de bron niet het label bevestigd.

## Uitvoeringsquotes: de materiële resterende afhankelijkheid

De op 30 oktober opgehaalde officiële [Trading212 OpenAPI-specificatie](https://docs.trading212.com/_bundle/api.json?download=) heeft 17 paden. Er is geen daarin bevestigde bid-/laatkoersfeed. Een position.currentPrice wordt niet als een twee seconden verse uitvoeringsquote opgevoerd.

De officiële openbare [Milanese boekpagina van QQQ3](https://www.borsaitaliana.it/borsa/etc-etn/dettaglio.html?isin=IE00BLRPRL42&lang=it&mic=ETFP) en [die van EQQQ](https://www.borsaitaliana.it/borsa/etf/dettaglio.html?isin=IE0032077012&lang=it&mic=ETFP) vermelden expliciet 15 minuten vertraging. Daarmee is die bron ongeschikt voor de vastgelegde twee-secondenpoort. Een verse downloadtijd verandert de ouderdom van de beurskoers niet.

[Deutsche Börse](https://live.deutsche-boerse.com/en/app) noemt gratis realtimeETF/ETP-schermkoersen voor ingelogde gebruikers. Dat is een relevante onderzoekslijn, maar bewijst nog geen programmeerbare, toegestane feed met de juiste notering, bid/ask en tijdstempels. Voor QQQ3 is in deze demo bovendien Milan als EUR-notering gevonden; een Xetra-koers wordt niet stilzwijgend daarvoor gebruikt.

Er is momenteel geen geverifieerde provider aangesloten die de vereiste verse uitvoeringsquotes levert. Geen aankoop, nieuwe betaalde rekening of abonnement is gestart. De poort wordt niet versoepeld om toch groen te krijgen.

## Fracties, geld en herstel

Trading212 publiceert [prijsafhankelijke hoeveelheidsprecisie](https://helpcentre.trading212.com/hc/en-us/articles/9511997937437-Can-I-trade-with-fractional-shares). De planner rondt nu conservatief volgens die grenzen en de afzonderlijke productlot af. De uitwisselingslot van één stuk bewijst geen fractionele brokerrechten. De minimale orderwaarde en prijstik blijven productspecifiek te bevestigen.

De transacties en dividenden worden met een duurzame pagineringscursor verzameld. Een ontbrekende pagina telt niet als nul. Identieke referenties worden gededupliceerd; gewijzigde inhoud onder dezelfde referentie blokkeert reconciliatie. De geverifieerde historie kan bij een nieuwe, chronologisch gecontroleerde kop aansluiten. Bij onvolledige historie wacht de engine; hij verklaart niet na twee verwachte pagineringspolls ten onrechte de rekening corrupt.

Rente op vrij geld en uitleenrente tellen als opbrengst, niet als een nieuwe storting. Deposits veranderen de risicounits; dividend en rente niet. Onzekere orders blokkeren nieuwe aankopen ook na herstart. De transportclient heeft daarnaast een onafhankelijke alleen-lezenblokkade. Een verkoop met bevestigde hoeveelheid en verse quote kan in expliciet vrijgegeven DEMO-modus risicoreductie uitvoeren, ook wanneer nieuwe aankopen door ontbrekende dagbevestiging worden geweigerd.

## Protocol voor twintig echte sessies

1. Begin uitsluitend met dezelfde expliciet vrijgegeven demo-configuratie, bron- en productdefinitie. Er bestaat geen LIVE-host of LIVE-modus.
2. De policyhash omvat ook de uitvoeringscode en gedeelde signaalkernel. Een code- of regelwijziging begint een nieuwe bewijsreeks; oude waarnemingen blijven bewaard.
3. Start de controle uiterlijk 09:20 New York. Van dat moment tot het officiële RTH-slot moet elke vereiste controle slagen, zonder gat groter dan driemaal het pollinterval.
4. Tijdens 09:31–09:36 en zolang orders werken zijn werkelijke verse uitvoeringsquotes verplicht. Normale beursstilte na sluiting van een Europese beurs wordt niet als een ontbrekende realtimequote voor een al voorbij ordervenster behandeld.
5. Registreer de bronhashes die gedurende de sessie zijn gebruikt. Een volledig gecontroleerde RTH-sessie krijgt pas ten minste 10 minuten na het slot een afsluitcontrole van broker, cash, orders en blijvende blokkades.
6. Een nog niet gepubliceerde nieuwe dagslotrij voor de volgende orderdag wist geen correcte voorgaande sessie uit. Ontbrekende data tijdens de daadwerkelijke vereiste sessie blokkeert wel de dagkwalificatie.
7. Een geïnjecteerde testclient, replay of losse poll bij het slot kan geen echte proefdag scoren. De dag moet zijn gestart met werkelijke officiële demo-authenticatie en alle uitvoeringseisen.
8. Nul trades op een geldig gecontroleerde dag is toegestaan als de bevroren regels geen order vereisen. Niet-uitgevoerde orders worden niet als fills geboekt.

Als alle ontbrekende voorwaarden vóór maandag 2 november vervuld zijn, is 30 november 2026 theoretisch de twintigste US-beurssessie. Thanksgiving 26 november is gesloten; 27 november heeft een vroege sluiting. Dit rooster is geen ingeplande order, starttoezegging of voltooid bewijs. De huidige teller blijft **0/20**.

## Reproduceerbare controle en vrijgavemoment

- `.venv/bin/python -m portfolio_agent.forward preflight`: actuele alleen-lezen bron-/brokercontrole met alle acht startpoorten.
- `.venv/bin/python scripts/audit_trading212_readiness.py`: herleidbare audit van de lokaal bewaarde productbronnen en huidige bewijsstand; geen backtest of order.
- `.venv/bin/python -m pytest -q`: onderzoeks- en agentsuite.
- `node --test tests/portfolio-public.test.mjs tests/portfolio-forward.test.mjs`: publieke inhoud en privacygrenzen.
- `npm run typecheck` en `npm run build`: dashboardcontrole; bouw in een afzonderlijke checkout als een ontwikkelserver draait.

Voor vrijgave ontbreken nu: dezelfde actuele dag bij de onafhankelijke bron, concrete productspecifieke uitvoeringsbewijzen, een geverifieerde verse quoteprovider en daarna de expliciete lokale demo-orderstart. Er wordt geen toestemming gevraagd zolang die technische afhankelijkheden niet concreet zijn opgelost. De startcontrole maakt deze ontbrekende bewijzen zichtbaar; ze vult ze niet zelf met aannames in.
