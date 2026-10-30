# QUANT: twee brokerroutes na controle van API-voorwaarden

30 oktober 2026. Dit is een haalbaarheidsverkenning, geen bewijs voor winstgevendheid of opdracht om een rekening te openen. Geen account, abonnement of aankoop is gedaan. De beoogde geautomatiseerde Trading 212-uitvoering staat geblokkeerd; de lokale marktanalyse en historische resultaten blijven beschikbaar.

## Wat het officiële document zegt

De [actuele API-voorwaarden van Trading 212](https://www.trading212.com/legal-documentation/API-Terms_EN.pdf), gekoppeld vanuit de [officiële API-documentatie](https://docs.trading212.com/api/section/authentication), vermelden als laatste wijziging 17 oktober 2025 en noemen Trading 212 EU GmbH. Artikel 4.2(a) verbiedt algoritmisch handelen via de API. Artikel 11 omschrijft dat onder meer als een algoritme dat zelfstandig orderparameters bepaalt met beperkte of geen menselijke tussenkomst. De beoogde automatische beslis- en uitvoeringsroute lijkt onder deze definitie te vallen. Artikel 6.7 noemt voorafgaande schriftelijke toestemming voor gebruik van een aangepaste interface. Artikel 7.1(b) zegt dat API-marktdata niet realtime is.

Artikel 3.4 vermeldt dat API-orders door de systematic internaliser van Trading 212 worden verwerkt. Een Milan-notering is dus op zichzelf geen bewijs dat een order op het Milanese orderboek wordt uitgevoerd of dat die quote de daadwerkelijke uitvoeringsprijs is.

De documentatie noemt expliciet een demo voor applicatietests, terwijl de voorwaarden in de aangehaalde tekst niet afzonderlijk toelichten hoe het verbod op demo-orders wordt toegepast. Evenmin is hier vastgesteld hoe artikel 6.7 specifiek op deze persoonlijke alleen-lezenclient wordt toegepast. Vraag Trading 212 om die punten te verduidelijken; ga niet uit van een uitzondering. De periodieke broker-API-verbinding is daarom uit voorzorg gepauzeerd. De gebruiker heeft geen orders laten plaatsen. De webinterface en de historische demo-uitlezing bewijzen geen toestemming voor een bot.

Een eerder gevonden zoekresultaat gaf een 2023-versie met dezelfde URL; het document dat de huidige officiële help en documentatie daadwerkelijk linken bevat elf pagina's en een versie uit 2025. Een eerder bericht dat alleen schriftelijke toestemming noemde was onvolledig en is gecorrigeerd.

## Route A: Trading 212 met eigen beoordeling

De lokale agent kan zelfstandig openbare dagbronnen controleren en een advies of melding tonen. De gebruiker kan vervolgens zelf de brokerapp raadplegen en zelf een beslissing nemen. Dat is een te onderzoeken werkvorm: Trading 212 moet bevestigen of de gewenste gegevenskoppeling en de precieze menselijke beslisprocedure onder zijn voorwaarden passen. Het is geen vrijbrief om alsnog orderparameters automatisch via zijn API te laten bepalen of verzenden.

De eerder gevonden EQQQ- en QQQ3-noteringen zijn potentiële producten, geen gevalideerde vervanging van de Amerikaanse QQQ/TQQQ-reeks. QQQ3 is een schuld-ETP met dagelijkse 3× blootstelling. Productbeschikbaarheid, actuele kosten, grootte van orders en de waarde van de eigen Europese producthistorie blijven onopgelost. Bij de nieuwste inventarisatie waren er onverklaarde OHLC-tegenstrijdigheden in de beschikbare gratis dagbron. Daarom kan de gemelde Amerikaanse backtest niet als werkelijk Europees rendement worden overgenomen.

## Route B: geautomatiseerde uitvoering bij een andere broker

[IBKR beschrijft](https://www.interactivebrokers.com/en/trading/ib-api.php) expliciet een API voor geautomatiseerde strategieën. De [papierrekening](https://ibkrcampus.com/campus/glossary-terms/paper-trading-account/) kan met de API gebruikt worden; gesimuleerde fills zijn geen bewijs van live fills. IBKR-bronnen verschillen over de precieze voorwaarden voor toegang tot de paperomgeving en realtime data; dit moet voor de rekening en entiteit worden bevestigd voordat die route uitvoerbaar wordt genoemd.

[IBKR prijslijst marktdata](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php) toont enkele Europese pakketten als fee waived en ook betaalde pakketten. [De API-documentatie](https://www.interactivebrokers.com/docs/tws-api/doc/md/introduction) vermeldt een betaald abonnement als algemene voorwaarde voor API-marktdata behalve vertraagde watchlistdata. Het is daardoor nog niet bewezen dat de exact benodigde EQQQ/QQQ3 bied- en laatkoersen, met juiste handelsplaats en bruikbare tijdstempel, kosteloos via de API verkrijgbaar zijn. Een andere handelsplaats dan de uitgevoerde order is niet automatisch dezelfde quote. Geen abonnement is aangeschaft.

### Kostenvrije-datahypothese: Xetra-notering

[WisdomTree](https://www.wisdomtree.eu/en-ie/etps/equities/wisdomtree-nasdaq-100-3x-daily-leveraged) vermeldt voor hetzelfde ISIN IE00BLRPRL42 naast Milaan een EUR-notering op Xetra onder `3QQQ`. Dit bevestigt het bestaan van de notering, niet dat IBKR deze voor deze gebruiker of in fracties aanbiedt. IBKR vermeldt een pakket `Deutsche Boerse ETFs` waarvan de non-professional-fee wordt kwijtgescholden, maar de algemene API-documentatie noemt betaalde datatoegang voor realtime marktdata. Omdat 3QQQ juridisch een schuld-ETP is, is nog niet vastgesteld dat het in het ETF-pakket valt, dat een persoonlijke API dit realtime mag gebruiken, dat bid én ask met bruikbare bron- en tijdstempels worden geleverd, of dat de koers past bij de feitelijke uitvoeringsplaats. Dit is dus een concreet gratis onderzoeksspoor, geen geverifieerde feed en geen vrijgave om noteringen te verwisselen.

### Kostenvoorbeeld voor de bestaande kleine rekening

Volgens de [IBKR-prijslijst voor Italië](https://www.interactivebrokers.com/en/pricing/commissions-stocks.php) geldt bij het laagste genoemde tiered aandelen-/ETF-tarief 0,05% per order met minimaal €1,25 per order. De tabel noemt dit minimum ook voor in aanmerking komende fracties. Onderstaande som veronderstelt dat dit tarief en de betrokken ordertypen echt van toepassing zijn, dat koop en verkoop elk één afzonderlijke order zijn en dat de orderwaarden gelijk blijven. Dit is alleen commissie; spreads, andere beurskosten, valutakosten en belastingen ontbreken.

| Waarde per kant | Koop + verkoop: commissie | Deel van orderwaarde |
|---:|---:|---:|
| €100 | minimaal €2,50 | 2,50% / 250 bp |
| €500 | minimaal €2,50 | 0,50% / 50 bp |
| €1.000 | minimaal €2,50 | 0,25% / 25 bp |

Voor de genoemde 0,05% per kant is de commissie over twee kanten alleen al minimaal 0,10% of 10 bp, vóór eventuele andere kosten. Bij grotere volumes of een ander toepasselijk tarief kan dit verschillen; het is geen persoonlijke offerte. Onze bestaande kostenlimiet van 5 bp voor de volledige transactie past dus niet bij dit specifieke voorbeeld, ook niet wanneer de vaste minimumbedragen geen rol meer spelen. Bovendien is een portefeuille van €1.000 verdeeld over meerdere onderdelen: de individuele orders kunnen kleiner zijn dan €1.000.

IBKR ondersteunt [fractionele handel in bepaalde producten](https://www.interactivebrokers.com/en/general/about/ibkr-fact-sheet.php); dit bevestigt niet dat juist deze Europese ETP en notering fractioneel, per API en voor dit rekeningtype verhandelbaar zijn. [IBKR wijst erop](https://www.interactivebrokers.com/campus/trading-lessons/trading-overseas-with-ibkr/) dat voor veel Amerikaanse ETF's een Europees essentieel-informatiedocument ontbreekt en retailtoegang daardoor beperkt kan zijn. Verander een Europees product niet stilzwijgend terug in QQQ/TQQQ.

### Aanvullende kandidaat: Saxo OpenAPI

[Saxo beschrijft](https://developer.saxobank.com/openapi/learn/writing-an-openapi-application) een eigen applicatie voor particuliere klanten en een SIM-omgeving. Voor een live-app moet een klant een aanvraag doen; [de aanvraaginstructies](https://developer.saxobank.com/openapi/learn/direct-clients-request-for-openapi-application-credentials-for-the-live-environ) vereisen een gevulde live-rekening en een eerder gemaakte SIM-app. Een aanvraag kan aan beoordeling onderhevig zijn. Het bestaan van de API is geen bewijs dat de concrete toepassing, instrumenten, datagebruiksrechten of deze gebruiker zijn goedgekeurd. Er is geen rekening geopend of aanvraag gedaan.

Volgens [Saxo's Nederlandse ETF-pagina](https://www.home.saxo/nl-nl/products/etf) beginnen transactiekosten op Euronext Amsterdam bij €2 per transactie en op Xetra bij €3 per transactie. Als een geschikt product en tarief daadwerkelijk daaronder vallen, zijn twee transacties van €100 dus ten minste €4 respectievelijk €6, oftewel 4% respectievelijk 6% van de orderwaarde, vóór spread en eventuele overige kosten. Dit is een illustratie voor die beurs en dit algemene tarief, geen offerte en geen vaststelling dat QQQ3 daar onder deze voorwaarden verhandelbaar is. [Saxo noemt ook een service fee](https://www.home.saxo/nl-nl/campaigns/invest-for-less) en specifieke voorwaarden voor eventueel transactietegoed. De informatie over realtime koersen op het platform bewijst nog niet de juiste API-rechten of een quote jonger dan twee seconden voor het exacte instrument.

Saxo vermeldt XNAS met ISIN IE00BMFKG444 op Xetra in een [Poolse productlijst](https://www.home.saxo/pl-pl/rates-and-conditions/etf/etfs-available). Een [Belgische lijst uit april 2023](https://www.help.saxo/hc/nl-be/articles/10618812028573-Lijst-Exchange-Traded-Notes-ETN-update-27-april-2023) vermeldt ook 3QQQ met ISIN IE00BLRPRL42 op Xetra. Dit zijn aanwijzingen voor instrumentdekking, geen bevestiging van actuele beschikbaarheid of fracties voor een Nederlandse klant. Saxo's [OpenAPI-datahandleiding](https://developer.saxobank.com/excel/user-guide/enabling-market-data) zegt bovendien dat marktdata voor niet-valutaproducten in externe applicaties standaard uitstaat en afzonderlijk aangevraagd/geactiveerd moet worden. Daarmee blijven de prijs, rechten en actuele bied- en laatkoersen van het specifieke product te controleren.

### Afbakening Alpaca

[Alpaca's documentatie voor individuele accounts](https://docs.alpaca.markets/us/docs/account-plans) beschrijft automatische handel en noemt op die pagina Amerikaanse beursgenoteerde aandelen en bepaalde crypto als ondersteunde markten. [De Europese documentatie](https://docs.alpaca.markets/eu/docs/getting-started) richt zich op zakelijke fintechpartners en noemt Europese aandelen als onderdeel van een toekomstige roadmap. Dit bewijst daarom niet dat onze Europese ETP voor een Nederlandse particuliere rekening beschikbaar is. Amerikaanse QQQ/TQQQ, EUR-noteringen en juridische producttoegang mogen niet als uitwisselbaar worden behandeld.

## Volgorde om daadwerkelijk verder te kunnen

1. Houd de Trading 212-verbinding gepauzeerd totdat de broker de toepassing van de voorwaarden op de eigen alleen-lezenclient en een eventuele demo bevestigt. Neem voor vragen zelf contact op; QUANT verstuurt niets namens de gebruiker.
2. Onderzoek onafhankelijk welke gereguleerde broker de gewenste API-automatisering, EUR-noteringen, fracties en ordertypen ondersteunt, met de volledige kosten en gegevensrechten voor een Nederlandse particuliere rekening.
3. Controleer de Europese producthistorie, valutablootstelling en beschikbare uitvoeringstijden apart van de Amerikaanse onderzoeksreeks.
4. Vergelijk vervolgens een op kosten getoetst, vooraf vastgelegd pad met een eenvoudige benchmark. Een demo kan storingen en interfacegedrag tonen; een echte edge of live fills bewijst zij niet.
5. Kies pas daarna of er een account of betaalde data nodig is. Het huidige budget sluit automatische maandelijkse uitgaven uit zonder een nieuwe keuze van de gebruiker.

## Klaarstaande vragen aan Trading 212

Onderstaande tekst is een concept voor de gebruiker. Er is niets verzonden en er staan geen sleutel- of rekeninggegevens in.

> Voor mijn eigen Invest-oefenrekening ontwikkel ik een lokale toepassing. De API-voorwaarden van 17 oktober 2025 verbieden algoritmische handel en noemen voorafgaande schriftelijke toestemming voor aangepaste interfaces. Kunt u schriftelijk verduidelijken: (1) geldt het verbod ook voor uitsluitend gesimuleerde demo-orders; (2) is voor een persoonlijke client die alleen rekeninggegevens leest voorafgaande toestemming vereist; en (3) welke vorm van door mij persoonlijk beoordeelde en handmatig geplaatste orders is toegestaan als een afzonderlijke toepassing alleen een advies toont? Ik vraag geen uitzondering en zal geen geautomatiseerde API-orders plaatsen voordat dit duidelijk is.
