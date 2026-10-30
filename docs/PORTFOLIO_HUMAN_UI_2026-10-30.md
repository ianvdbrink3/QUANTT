# Portfolio OS — begrijpelijke interface en koersgrafieken

Lokale pagina: http://127.0.0.1:3013/portfolio-os.

## Wat is veranderd

De terminal is vervangen door een overzicht met Nederlandse uitleg, een gedateerde modelsamenvatting, betekenisvolle kleuraccenten en een grote interactieve koersgrafiek. Technische hashes, oorspronkelijke dagbrieven en controlegegevens blijven beschikbaar achter uitklapbare details.

De profielknoppen heten Voorzichtig, Gebalanceerd en Aanvallend. Een gekleurde verdelingsbalk en bedragen per onderdeel geven de bestaande gewichten weer. Profielkeuze blijft een preview: de actieve regels, de bestaande simulatie en de verliesgrens veranderen niet. De aparte kasbuffer is uitgelegd, ook waar een profiel 0% vrije cash vermeldt.

De kostencheck toont orderkosten, totale heen-en-terugkosten in euro's, het percentage van de aankoop en het bedrag dat bij de gekozen kostenlimiet nodig is. De normale grenzen blijven 0,05% en 0,10%; er is geen nieuwe 0,25%-regel ingevoerd. Geen vaste commissie wordt niet als kosteloos handelen omschreven. Eurobedragen en percentages gebruiken één gelijktijdige invoersnapshot om tijdelijk tegenstrijdige getallen tijdens een API-verversing te voorkomen.

## Historische koersgrafiek

- De bestaande, op SHA-256 gecontroleerde dagelijkse bronbestanden leveren 1.967 beursdagen per fonds, van 2 januari 2019 tot 28 oktober 2026. De data vóór 2019 blijft opwarming voor gemiddelden.
- Keuze tussen QQQ en TQQQ; drie maanden, één jaar, kalenderjaar 2022 en de volledige beschikbare historie. De geselecteerde auditpeildatum knipt toekomstige chartpunten af.
- Slotkoers, 20-daags gemiddelde en de 200-daagse lijn; die laatste kleurt rood in de cashstand. Achtergrondkleuren geven de oorspronkelijke QQQ-modelclassificatie bij dagslot weer.
- Zoom, verschuiven van het tijdvenster, inspectie per dag en pijltjestoetsen werken zonder nieuwe chartbibliotheek.
- Koersen zijn split-gecorrigeerde prijsdata. De grafiek is geen total-returngrafiek en bevat geen dividendrendement.
- Achtergrondkleur is een berekende modelstand, geen gereconstrueerde rekeningpositie. De 2022-weergave wordt niet als bewijs gepresenteerd dat de daadwerkelijke agent toen een crash ontweek.
- Pijlen komen uitsluitend uit werkelijk gelogde historische simulatie-fills in de geselecteerde auditperiode, op hun geregistreerde fillprijs. Het ingestelde minuutanker staat in de omschrijving. Geen verzonnen fills buiten die auditperiode.
- Holle ruitjes zijn uitsluitend S1-signaalkandidaten. De nachtmodule staat uit; een ruitje is geen nachtorder of bewezen uitvoering.

De dataset is lokaal voorbereid met `python -m portfolio_agent.chart_data` en staat uitsluitend onder `artifacts/portfolio_agent/chart_daily.json`. De read-only route `/api/portfolio-chart` gebruikt dezelfde lokale host-/originbeveiliging als de bestaande OS-route en blokkeert productie. Geen ruwe CSV of volledige koersreeks is openbaar gepubliceerd.

## TradingView

Lokaal laadt het tweede grafiektabblad de officiële Advanced Chart-widget pas na een klik. De openbare versie opent deze externe grafiek standaard; de volledige lokale historie wordt niet meegestuurd. QQQ/TQQQ en twee dagelijkse Moving Averages met lengte 20 en 200 zijn vooraf ingesteld. De provider kan vertraagde koersen of een alternatieve beursfeed tonen; de widget is onafhankelijk van onze signalen en uitvoeringsbewijzen. Geen account, API-key of brokerverbinding toegevoegd.

De widget is in de lokale browser met beide lengtes 20 en 200 gezien; TradingView meldde vertraagde data. In de laatste productiebuildcontrole laadde het externe frame soms zonder koerswaarden. Dit is geen gevalideerde livefeed; de directe TradingView-link blijft beschikbaar. De interne modelsamenvatting gebruikt uitsluitend de gedateerde export. De integratie volgt het [officiële React-voorbeeld voor technische analyse](https://www.tradingview.com/widget-docs/widgets/charts/advanced-chart/demos/technical-analysis/). De uitgestelde scriptinvoeging voorkomt een voortijdige invoeging tijdens de voorbereidende React StrictMode-mount.

## Groei versus eigen inleg

De groeigrafiek gebruikt de bestaande rekenformule en bestaande profielaannames van 6%, 8% en 10% per jaar. Alle eindpunten zijn tegen de bevroren scenario-CSV gecontroleerd. Een start van €1.000 en €100 per maand levert €13.000 eigen inleg na tien jaar; het defensieve rekenvoorbeeld blijft €18.038,19. Dit is een aanname, geen gemeten modelrendement of rendementsbelofte. Het bestaande, flow-gecorrigeerde Unit-NAV-verloop blijft apart beschikbaar in de portefeuillekaart.

## Verificatie en behoud

De oude presentatietest voor een verplicht 36px/100vh-terminalraster is aangepast aan deze expliciet vervangende ontwerpopdracht. Signaal-, accounting-, kosten-, onderzoeks- en beveiligingsregels zijn niet gewijzigd. Nieuwe tests controleren chartwaarden tegen de bestaande kernel, toekomst-afknipping, werkelijke auditfills, kalenderdekking, planningsberekeningen en bescherming van de bestaande bestanden.

De volledige suite telt 1.747 geslaagde tests; elf aanvullende openbare-exporttests slagen eveneens. Vier bestaande NumPy-waarschuwingen blijven aanwezig. TypeScript en de productiebuild slagen. Het beschermingsregister bevat 846 eerder bestaande bestanden, inclusief onderzoeksresultaten, de bestaande agentcode en gepubliceerde samenvattingen.

In de browser zijn de Nederlandse weergave, de echte 2022-data (251 beursdagen), TQQQ over de volledige historie (1.967 dagen), wisselen tussen fondsen, zoom, verschuiven en profiel-/inlegpreview gecontroleerd. De in-app browserverbinding viel later weg; de controle is via Safari voortgezet. Na ontgrendeling is de kostencorrectie alsnog in de browser bevestigd: bij een aankoop van €1.000 toont IBKR direct €2,90 heen-en-terugkosten en DEGIRO €2,40. De 0,10%-poort toont voor DEGIRO €2.333,34 extra sparen en 24 maanden bij €100 per maand. De browserconsole was tijdens deze eindcontrole schoon.

Screenshots, het testverslag en het hashregister staan in `artifacts/portfolio_agent/human-redesign/`. De gebruiker heeft de publicatie op GitHub main en Vercel-productie goedgekeurd. De volledige koersreeksen en lokale ledger blijven buiten deze release.
