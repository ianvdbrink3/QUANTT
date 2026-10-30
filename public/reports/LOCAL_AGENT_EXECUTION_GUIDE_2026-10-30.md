# QUANT lokale agent — uitvoering en aansluitgids

Datum: 30 oktober 2026. **Alleen advies en afzonderlijk te activeren DEMO-uitvoering. Echte orders zijn in deze software onmogelijk.** De gebruiker heeft nog geen brokeraccount. De softwaretest is geen geverifieerde Trading 212-verbinding of bewijs van toekomstig rendement.

## De zes stappen: wat af is en wat extern bewijs nodig heeft

| Stap | Geleverd | Resterende voorwaarde |
|---|---|---|
| 1 Producten | Exact ISIN-/ticker-/valuta-/schema-/beursurenbindingsmodel; geen stilzwijgende vervanging | Jouw echte democatalogus en productrechten ontbreken. Geen product is voor orders vrijgegeven. |
| 2 Dagelijkse agent | Nieuwe brondata, huidige drie profielen, NY/DST-kalender, historische cache gescheiden, dagelijkse updates en heartbeat | Tweede onafhankelijke bron is bij de eerste draai niet bevestigd. Dat blokkeert nieuwe demo-risico-orders. |
| 3 Orderadministratie | Duurzame outbox, claims vóór POST, één identiteit per dag/sleeve/richting, gedeeltelijke fills, cash/fees, herstart en onzekerheidsblokkade | Brokeruitvoeringen moeten nog op een echt demo-account worden waargenomen. |
| 4 Dashboard | Lokale controlekamer; gepubliceerde bouwstatus; bronstand, heartbeat, gewenste gewichten, blockers en proef-teller | Vercel heeft bewust geen verbinding met de Mac of broker. De openbare bouwstatus is een snapshot. |
| 5 Trading 212 | Officiële v0 demo-client met REST-contract- en lokale HTTP-tests | Geen demo-account, sleutels, productbindingen of geverifieerde uitvoeringsquote-feed aanwezig. |
| 6 Operationele proef | Vast kwalificatieprotocol en storingsproeven | **0/20 echte volledige demo-sessies**. Historische fixtures tellen nooit als forwardbewijs. |

De bestaande backtests en hun bronbestanden blijven byte-identiek. De nieuwe modules staan onder `portfolio_agent/forward/` en delen de bestaande `features`, `advise`, `classify`, `sleeve_targets` en gewichten. Er wordt geen nieuwe strategie of geoptimaliseerde parameter ingevoerd.

## Wat de agent nu doet

De Mac controleert iedere minuut of er een nieuw, voltooid QQQ/TQQQ-dagbarpaar beschikbaar moet zijn. Dagdata komt uit een nieuwe, aparte Yahoo-bronopslag; een onafhankelijke Stooq-slotprijscontrole probeert dezelfde datum te bevestigen. De vaste 10bp-afwijkingsgrens is een datakwaliteitscontrole, geen handelsfilter. Een ontbrekende tweede bron is geen bevestiging.

Een cashdag geldt pas tien minuten na het officiële slot als voltooid. Weekenden, feestdagen, vroege sluitingen en de afzonderlijke Amerikaanse/Europese DST-overgangen worden met tijdzones behandeld. De primaire bronbar is split-aangepaste prijsdata; het actuele signaal gebruikt geen toekomstige dividend-aangepaste prijzen. De download is één huidige bronversie en bewijst niet de historische publicatietijd van vroegere correcties.

Een tijdens de handelsdag opgeslagen gedeeltelijke bar wordt later **niet** door het verstrijken van de tijd tot definitieve bar gepromoveerd. De cache wordt steeds op haar oorspronkelijke ontvangstmoment geïnterpreteerd. Voor een nieuwe afgesloten dag is een nieuwe download nodig. Bronbytes zijn onveranderlijk en op SHA-256 vastgelegd. De oorspronkelijke onderzoeksdata wordt niet overschreven.

De actuele adviesgewichten worden voor alle drie profielen getoond, vóór de bestaande aparte cashbuffer. S1 en S2 zijn uitgeschakeld. Een LLM mag uitleg geven, maar heeft geen orderfunctie en kan de rekenregels niet aanpassen.

## Producten eerst: geen geërfde QQQ/TQQQ-rendementen

Het rekeningproduct wordt gekoppeld op exact broker-ticker én ISIN, primaire valuta, werkelijk workingScheduleId, minimale notional, lotgrootte en prijstik. De actuele instrumenten-/exchange-respons en rekeningrechten moeten overeenstemmen. Niet-afgeronde product-/sessie-/historiecontroles blokkeren orders.

- EQQQ, ISIN IE0032077012, blijft een eerder vastgelegde kandidaat. Huidige demobeschikbaarheid is niet aangetoond.
- Xtrackers NASDAQ100 UCITS ETF1C, ISIN IE00BMFKG444, is bij de issuer gecontroleerd. De issuer noemt 21 januari 2021 als introductiedatum; een eigen 2019-historie mag dus niet worden verzonnen. De issuerpagina toont een Londense notering: dat bewijst geen EUR-notering of beschikbaarheid op jouw rekening.
- QQQ3, ISIN IE00BLRPRL42, is een eerder genoemde **debt-ETP**, geen TQQQ of automatisch geschikte vervanger. De nieuwe standaardbinding accepteert uitsluitend geverifieerde ETF-structuren; dit product blijft geblokkeerd.

Een andere beurs, valuta, distributieklasse of openingstijd kan andere resultaten geven. Daarom blijft `bindings: []` de distributiestandaard. De benodigde productcontrole wordt geen mechanisme om een ongetest instrument stilzwijgend mee te laten handelen.

## Dagelijkse demo-executie zodra de ontbrekende voorwaarden zijn vervuld

1. Gebruik uitsluitend de voltooide vorige US-cashdag voor de bestaande SMA20/SMA200/ATR14/HIGH_VOL-classificatie.
2. Bereken de bestaande maandelijkse aanvulling/regimewijzigingen en dagelijkse exposure-trims. Eerst de bestaande reserve van max(10,1% strategisch NAV).
3. Plan op 09:31 NY, met een venster van vijf minuten. Dit is de bestaande operationele minuutconventie; het is **geen bewijs** van identieke fills aan de officiële dagopenprijzen uit de benchmark.
4. Gebruik het geverifieerde werkrooster van het brokerproduct. Een Europees product erft niet automatisch de Amerikaanse handelsuren.
5. Gebruik actuele, geverifieerde bid/ask-quotes met herkomst, prijsvaluta en tijdstempel, maximaal twee seconden oud. De gecontroleerde API-specificatie biedt ons geen bevestigde, gedateerde bid/ask-feed; `currentPrice` uit posities wordt daarom niet als NBBO of verse uitvoeringsquote voorgesteld.
6. De client verzendt uitsluitend DAY-limietorders naar `https://demo.trading212.com/api/v0`. Verkoop gebruikt een negatieve quantity. Geen market-/stop-/OCO-constructie wordt gefingeerd.
7. Claims en intenties worden vóór de POST gecommit. De officiële API is niet idempotent; een timeout wordt nooit blind opnieuw verzonden. Een onbekende aanvraag blokkeert nieuwe risico-orders, ook na herstart.
8. Een ACK is geen fill. De prijs, hoeveelheid en belastingen/fees komen uit de historische brokerfills. Annuleringsacceptatie is geen definitieve annulering; een gelijktijdige late fill blijft geldig.
9. Verkoopopbrengsten die nog niet `availableToTrade` zijn worden niet vooruit uitgegeven. Dit veld wordt niet als bewezen banksettlement aangeduid. Niet-uitgevoerde of geweigerde orders leveren geen fictieve backtestfill op. Per identiteit is er maximaal één aanvraag; restbedragen kunnen cash blijven.
10. Een verlopen ordermoment krijgt `EXECUTION_WINDOW_MISSED_NO_BACKFILL`. Er komen geen inhaalorders met zogenaamd eerdere prijzen.

Quotes worden later door een werkelijk geverifieerde lokale feed in `artifacts/portfolio_agent/forward/execution-quotes.json` aangeleverd. Het bestand moet uitsluitend door de eigenaar leesbaar zijn (0600), met schema1, ticker, bid, ask, currency, observed_at, provider, source_sha256, synthetic en verified_execution_quote. Een fixture of vertraagde gratis koers mag niet simpelweg het label verified krijgen. Zonder deze feed blijft automatische demo-uitvoering geblokkeerd.

## Cash, risico en herstel

De brokerrekening moet voor deze proef leeg en exclusief zijn; onbekende posities, Pies, onbekende orders of cashverschillen blokkeren nieuwe risico-opbouw. Posities, tradefill-notional, gerapporteerde belastingen/fees en nieuwe stortingen/onttrekkingen worden tegen de demo-cashhistorie gecontroleerd. Alleen maximaal één cent rapportageafronding is toegestaan. Onvolledige paginering/cashhistorie wordt niet als nul gelezen; de accountcontrole blijft dan geblokkeerd. Twee afzonderlijke afwijkende snapshots leiden tot een blijvende reconciliatieblokkade; een eerste afwijking blokkeert al orders maar kan een REST-race zijn.

Het strategisch beginbudget is1.000. Bij een demo met50.000 wordt de overige49.000 niet stilzwijgend als risicobuffer of positiebudget gebruikt. De bestaande profielwaarschuwingen zijn10/20/35% en hardgrenzen15/25/40%. Stortingen verhogen units en worden niet als winst of drawdownherstel geteld. Bij een waarschuwing worden nieuwe3x-toevoegingen geblokkeerd; een harde grens vraagt menselijke controle. Betrouwbaar bevestigde risico-verlagende verkopen blijven mogelijk binnen de sessie-/quote-/ordercontroles. Dit garandeert geen maximale verliesgrens, bijvoorbeeld bij slaapstand, gaps of een koersfeedstoring.

Een bekende order kan later opnieuw worden uitgelezen en gereconcilieerd. Een onbekende POST zonder broker-ID vereist menselijke controle in de demo voordat een verbinding aan een order kan worden toegekend. Geen automatisch gokken op 'waarschijnlijk deze order' en geen automatische herstart die de verliespiek of ordergeschiedenis wist. Verwijder de SQLite-database nooit om een blokkade te omzeilen.

Voor cashhistorie met meer dan één pagina blijft de eerste versie conservatief geblokkeerd totdat de volledige historie is gereconcilieerd. Orderfillhistorie heeft een duurzame cursor over opeenvolgende polls. Dit is een expliciete beperking; zonder bewezen complete rekeninghistorie mag de proef geen groene status krijgen.

## Zonder rekening nu starten en stoppen

Vanuit de repository, met de bestaande Python-omgeving:

```
.venv/bin/python -m portfolio_agent.forward once
.venv/bin/python -m portfolio_agent.forward status
.venv/bin/python -m portfolio_agent.forward service-install
.venv/bin/python -m portfolio_agent.forward service-stop
```

De geïnstalleerde macOS LaunchAgent start bij login en herstart bij een crash, standaard uitsluitend in ADVICE_ONLY. De Mac moet ingeschakeld en wakker zijn. De installer wijzigt geen slaap- of beveiligingsinstellingen. De agent heeft geen betaalde LLM, VPS of dataset nodig. Zijn gewone controle bevat geen LLM-aanroep. Privéstatus en database staan uitsluitend onder `artifacts/portfolio_agent/forward/`.

De dubbele-klikbestanden `tools/start-portfolio-advice.command` en `tools/stop-portfolio-advice.command` voeren dezelfde lokale commando’s uit. De stopactie bewaart database en bronnen.

## Later jouw Trading 212-demo koppelen

1. Maak zelf een Trading 212 Invest-demo aan en accepteer zelf de voorwaarden. Je hoeft voor deze bouwfase niets te kopen.
2. Genereer zelf demo-API-sleutels in de app. Gebruik de benodigde leesrechten; orderrechten zijn pas nodig voor de expliciete demo-orderproef. **Stuur geen sleutels of wachtwoorden in deze chat.**
3. Voer lokaal `.venv/bin/python -m portfolio_agent.forward setup-demo-secrets` uit. Beide invoeren zijn verborgen. De gegevens staan in een eigenaar-only bestand buiten Git/Vercel en niet in de LaunchAgent-plist.
4. Laat de alleen-lezen accountcontrole eerst de echte catalogus, valuta, beursuren, fracties en historische productbasis vastleggen. Bevestig een onafhankelijke dagbron en een werkelijk bruikbare uitvoeringsquote-feed.
5. Alleen nadat die controles werkelijk slagen kan een lokale configuratie in DEMO worden gezet. De distributiestandaard blijft ADVICE_ONLY; er bestaat geen LIVE-modus, live-host of webknop voor brokerorders.

De website bevat uitsluitend een veilige bouwstatus. Een actuele lokale status wordt alleen via de lokale read-only route gelezen. Brokergegevens, ruwe koersbestanden, sleutels, posities, aantallen en limietprijzen worden niet naar Vercel verstuurd.

## Twintig echte observatiedagen

Een sessie telt uitsluitend wanneer dezelfde configuratie vanaf uiterlijk09:20 NY tot ten minste tien minuten na het echte slot verbonden en gecontroleerd is, zonder heartbeatgat groter dan driemaal het pollinterval. Huidige data, onafhankelijke broncontrole, sluitende demo-administratie en bekende orderstatussen zijn verplicht. Eén datum telt één keer. Wijziging van de configuratie start een nieuwe bewijsreeks.

Een historische replay, lokale testserver, gesimuleerde tijd of een run alleen bij het slot telt niet als een echte volledige demodag. De technische tests bewijzen softwaregedrag en worden apart gerapporteerd. Twintig dagen bewijzen evenmin statistisch dat de strategie winstgevend is. Er zijn nu nul gekwalificeerde demo-observatiedagen.

## Primaire documentatie gecontroleerd

- [Trading 212 API-beperkingen, primaire valuta en demo](https://docs.trading212.com/api/section/general-information/api-limitations).
- [Officiële OpenAPI-specificatie](https://docs.trading212.com/_bundle/api.json?download=): account summary, positions, instrument/exchange metadata, limietorders, GET/DELETE op order-ID en historische tradefills. De lokale bronhash staat in het verificatieregister.
- [Xtrackers issuer en introductiedatum](https://etf.dws.com/en-gb/IE00BMFKG444-nasdaq-100-ucits-etf-1c/).
- [NYSE-kalender](https://www.nyse.com/trade/hours-calendars) en [Nasdaq-kalender](https://nasdaqtrader.com/Trader.aspx?id=Calendar).

## Uitgevoerde oplevercontroles

- Volledige Python-suite: **1.818 geslaagd** (waarvan 60 nieuwe forwardtests); vier bestaande numerieke waarschuwingen uit onderzoekstests, geen testfouten.
- Dashboard/privacy: **17 geslaagd**; TypeScript-controle en productiebuild geslaagd.
- 846 beschermde lokale onderzoeksbestanden en 209 eerder vastgelegde releasebestanden byte-identiek. De eerdere historische benchmarkexport is niet herberekend of gewijzigd.
- Lokale productiebuild: de privéstatusroute geeft HTTP 403 met alleen LOCAL_ONLY.
- macOS-adviesdienst daadwerkelijk geregistreerd en draaiend; één gecontroleerde herstart geeft een nieuw proces zonder nieuwe orders. Nul verzonden/gevulde/onzekere orders.
- Nieuwe bronstand gecontroleerd t/m 29 oktober 2026; de tweede bron is niet bevestigd. Geen brokeraccount of uitvoeringsquote-feed.
- Werkelijke gekwalificeerde demo-observaties: **0/20**. Technische tests zijn geen brokerbewijs.

Reproduceer de softwarecontroles met `.venv/bin/python -m pytest -q`, `node --test tests/portfolio-public.test.mjs tests/portfolio-forward.test.mjs`, `npm run typecheck` en `npm run build`. Doe een productiebuild in een afzonderlijke checkout als een ontwikkelserver draait.
