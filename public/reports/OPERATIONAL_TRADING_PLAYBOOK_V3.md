# QUANT — Operationeel playbook V3: referentie en prop-uren

De onderstaande oorspronkelijke specificatie blijft ongewijzigd. S1/S2 met B zijn de vaste referentie; Judas-vervanging en 18:00 zijn afzonderlijke ontwikkelingsvarianten, niet onafhankelijk gevalideerd. De nieuwe uitvoeringsgids staat in het aanhangsel.

[Alle ICT-varianten](/research/ict) · [Zeven Judas-varianten](/research/judas-replacement) · [Prop-uren en risico](/research/prop-firm)

---

# QUANT — Operationeel onderzoeks- en position-sizing-playbook

Versie: 25 oktober 2026. Status: `EXPLORATORY_NOT_INDEPENDENTLY_VALIDATED`.

Dit is de uitvoeringsspecificatie voor reproductie en paperuitvoering van twee geselecteerde ontwikkelingsmodellen. Het document plaatst geen orders en promoveert de modellen niet tot bewezen winstsystemen. Alle genoemde regels zijn afkomstig uit de bestaande berekeningscode; de overnight-route is apart herberekend met causale same-contract uitvoering. Strategieparameters blijven ongewijzigd; de oude resultaten en het oude playbook zijn als archief bewaard.

**S1 — selectief met overnight-stop:** sterke-trenddag-overnight met vaste 0,50 ATR-stop, plus intraday pullback B. In de onderzochte data is de waargenomen drawdown lager dan bij S2.

**S2 — breed zonder overnight-stop:** bull-overnight na slot boven SMA20, plus exact dezelfde intraday pullback B. Dit heeft het hoogste totale netto R van de vijf consolidatievarianten op deze ontwikkelingspool.

Beide perioden zijn al gebruikt bij selectie: 2019–2021 en het afzonderlijke blok eind 2024–september 2026. De berekening bevat 1.151 technisch geschikte instapsessies, 1.171 cashsessies voor de dagelijkse boekhouding en 19 kwartalen. Er is geen aaneengesloten vijfjarige trackrecord; 2022–2024 wordt niet overbrugd. Een gemeten drawdown is geen toekomstige verlieslimiet.

## 1. Tijd, prijzen en dagelijkse voorbereiding

1. Alle beslissingen gebruiken `America/New_York` met de echte DST-kalender. Geen vaste UTC-offset. De Barchart-bron is Chicago-tijd en wordt eerst via `America/Chicago` naar UTC en New York omgezet.
2. De engine gebruikt minuutbars met intern ondersteunde bar-startconventie: label 09:30 is de minuut vanaf 09:30; het slot van de 15:59-bar is pas om 16:00 definitief. Status: `BAR_START_SUPPORTED_INTERNAL_ONLY`. Er is geen onafhankelijk tick-, latency-, queue- of exact-16:00-fillbewijs.
3. Normale RTH is 09:30–16:00, 390 voltooide minuutbars. Gebruik het bestaande kalenderregister voor feestdagen en vroege sluitingen. Een normale handelsdag wordt niet kunstmatig ingekort; een vroege sluiting wordt niet tot 16:00 aangevuld.
4. Lees het geregistreerde actieve contract, de reeds bekende roll-spreads en de gevalideerde bronhashes. Gebruik onverschoven contractprijzen voor signaal, stop, target en uitvoering. Geen continu-contractsprong in handels-P&L.
5. Controleer vóór 09:30 de ATR-beschikbaarheid en bewaar de vastgezette waarde `A = ATR14_prior` gedurende de hele dag en de daaropvolgende overnight-positie. Gebruik nooit de ATR van morgen om de positie van vandaag te schalen.
6. Ontbrekende prijzen of indicatorhistorie blijven onbekend. Geen forward-fill, nulvolume-invulling of terugwerkende vervanging. De historische kwaliteitsmaskers blijven bewaard. Een toekomstige ontbrekende bar is geen live kenbare instapfilter: registreer bij paperuitvoering de werkelijk beschikbare data en eventuele feitelijke fills, en markeer het resultaat als niet exact reproduceerbaar wanneer een vereist anker ontbreekt. Verwijder geen bekende verliezen achteraf.

## 2. Exacte ATR14 vóór de sessie

Dit is een eenvoudig gemiddelde van true ranges, **geen Wilder-ATR** en geen gemiddelde van alleen high-low.

Voor handelsdag d is de op die dag bekende cumulatieve Panama-offset `O_d` de som van vastgelegde spreads waarvan de activatiesessie uiterlijk d is. Een spread moet vóór gebruik beschikbaar zijn. Voor een volledige normale RTH-dag:

`H*_d = max(RTH high_d) - O_d`

`L*_d = min(RTH low_d) - O_d`

`C*_d = close(15:59_d) - O_d`

Als zowel deze als de onmiddellijk voorafgaande geplande RTH-sessie volledig zijn:

`TR_d = max(H*_d-L*_d, abs(H*_d-C*_{d-1}), abs(L*_d-C*_{d-1}))`

Vóór 09:30 van d:

`A_d = mean(laatste 14 eerder geldige TR-observaties)`

De huidige dag wordt pas na voltooiing aan de historie toegevoegd. Een onvolledige of korte geplande sessie maakt de vorige-RTH-context ongeldig; de volgende volledige sessie voegt zonder geldige vorige close geen TR toe. De opgebouwde geldige TR-historie blijft bestaan. Daardoor zijn het niet altijd de laatste 14 kalender- of cashdagen. Bij minder dan 14 geldige eerdere TR's of niet-positieve ATR is er geen positie.

Bron van de exacte volgorde: `scripts/causal_map/__main__.py::prepare`, gebruikt door beide bronroutes. De indicatorreeks is point-in-time doorlopend; een toekomstige roll-spread herschrijft geen eerdere beslissingen.

## 3. Twee verschillende SMA20-momenten

De dagelijkse close is een **RTH-slotproxy**, geen CME-settlement. De cashkalender bevat ook bekende korte cashsessies. De SMA-routine gebruikt daarvoor de laatste verwachte RTH-minuut van het vastgelegde futureskalenderrooster, begrensd op 16:00. Een onvolledige cashsessie levert een onbekende close op; zij wordt niet overgeslagen om toch 20 waarnemingen te krijgen.

**Vóór 09:30 — filter voor B:**

`SMA20_prior(d) = mean(20 direct voorafgaande cashsessie-closes in huidige prijsbasis)`

`bull_preopen(d) = close_gisteren > SMA20_prior(d)`

Alle 20 closes moeten beschikbaar zijn. Met `C*_j = C_raw,j - O_j` wordt de SMA in de huidige contractbasis `mean(C*_j) + O_d`. Zo vormt een contractspread geen fictieve trend.

**Om 16:00 — overnight-filter voor A en S2:**

`SMA20_terminal(d) = mean(19 vorige cashsessie-closes + de zojuist voltooide close_d)`

Gebruik dezelfde point-in-time basisomrekening. Deze SMA is pas na de 15:59-bar definitief. Voor de brede S2-populatie moet daarnaast de SMA20 vóór 09:30 beschikbaar zijn, precies zoals in de oorspronkelijke 723 bull-nachten uit het archief. S1-A vereist de terminale SMA maar geen preopen bull-status. Dit verklaart waarom één oorspronkelijke A-dag buiten de vooraf bekende SMA20-benchmarkpopulatie valt; voeg geen uitzonderingsdatum als handelsregel toe.

## 4. Pijler B — trend-aligned intraday pullback

Deze pijler is voor S1 en S2 identiek. Alleen long, maximaal één eerste bevestigde setup per dag; geen herinstap na stop of target.

1. Vóór 09:30 moet `bull_preopen = true` en `A > 0` bekend zijn.
2. Vorm vaste 5-minutenbars vanaf 09:30: open van de eerste minuut, maximum high, minimum low, close van minuut vijf, som van de vijf minuutvolumes.
3. Bevestigingsgrenzen zijn uitsluitend 09:45 tot en met 14:30 NY. Een omkeerbar 09:40–09:44 wordt dus om 09:45 beoordeeld en kan op de 09:45-open instappen.
4. Bepaal vóór het begin van de omkeerbar de lopende RTH-high `H_pre`. Neem de meest recente minuut die deze high heeft geraakt. De pullback-low `L_pre` is de laagste low NA die piekminuut en vóór de omkeerbar. De low uit de piekminuut zelf bewijst geen high-voor-low-volgorde en telt niet mee.
5. Vereis `H_pre - L_pre >= 0,50 * A`. De pullback moet dus vóór de omkeerbar al bestaan; een wick van alleen de omkeerbar creëert geen setup.
6. De voltooide omkeerbar moet tegelijk voldoen aan `Close > Open`, `Close > High_vorige_5m_bar` en `Volume > 1,5 * gemiddelde_volume_vorige_20_5m_bars`.
7. De volumereferentie bevat exact 20 eerdere voltooide RTH-5m-bars, inclusief eerdere cashsessies waar beschikbaar. De triggerbar telt niet mee. Ontbrekende/ongeldige blokken wissen de volumestaart; geen overnight-volumebars toevoegen en geen extra time-of-day-filter gebruiken.
8. Instapprijs `E`: open van de eerstvolgende minuut na bevestiging. Eerste signaal is bindend; kies niet achteraf een latere mooiere setup.
9. Initiële stop, met tick `t=0,25`:

`S_B = min(min(L_pre, Low_omkeerbar)-t, floor((E-0,35*A)/t)*t)`

De stop ligt dus onder de structurele low en minstens circa 0,35 ATR van de entry. De afstand is niet tot 0,35 ATR begrensd.

10. Vast target:

`T_B = ceil((E+A)/t)*t`

11. Stop blijft ongewijzigd; geen trailing of breakeven. Tijdsexit is de **15:55-open**, niet de 15:55-close. Een eerder geraakte stop of target beëindigt de positie.

## 5. S1 — selectieve overnight met vaste catastrofestop

Beoordeel na voltooiing van 15:59, met de vóór 09:30 vastgezette ATR A:

`Range_RTH = H_d - L_d`

`CloseLocation = (C_d-L_d)/(H_d-L_d)`

Er is uitsluitend een overnight-long als de volledige normale RTH bekend is, `H_d>L_d`, `Range_RTH > 0,85*A`, `CloseLocation >= 0,85` en `C_d > SMA20_terminal(d)`.

Instapanker: de **16:00-minuutopen** op het actieve onverschoven contract. Dit is een onderzoeksfill na de slotbevestiging, geen bewezen milliseconde-uitvoering op de eerste print. Een gemiste paper/live-entry krijgt geen achteraf ingevulde oude open; een andere feitelijke entry wordt als afwijking geregistreerd.

Vaste stop vanaf entry E:

`S_A = ceil((E-0,50*A)/0,25)*0,25`

De afronding is naar de entry toe. Bij een stop-touch wordt het stopniveau gebruikt; bij een open door de stop de ongunstigere minuutopen. Een gap en frictie kunnen het nettoverlies groter maken dan 0,50 ATR. Geen target, herinstap, stopverruiming of winstafhankelijke aanpassing.

Zonder eerdere stop: exit op de **09:30-open van de eerstvolgende daadwerkelijke cashsessie**. Weekend of cashfeestdag wordt niet voor een gewone volgende werkdag aangezien. Geen 09:30-low/close na de uitstap gebruiken. In S1 is B vóór de eventuele 16:00-entry uiterlijk om 15:55 flat.

## 6. S2 — brede bull-overnight zonder overnight-stop

De intraday B-regels blijven exact gelijk. Voor de overnight-pijler zijn vereist: volledige huidige RTH, positieve vooraf bekende ATR, beschikbare preopen SMA20-populatie en `C_d > SMA20_terminal(d)`.

Instap 16:00-open; exit volgende daadwerkelijke cashsessie 09:30-open. Geen range- of close-location-voorwaarde. Een sterke trenddag krijgt dezelfde enkele basispositie: niet nog een extra A-positie. Er is **geen overnight-stop**, target of intraday breakeven in deze onderzochte S2-variant. Een stop toevoegen verandert de variant en hoort niet stilzwijgend bij deze resultaten.

Een vaste maximale verliesafstand ontbreekt. Er kan daarom geen MNQ-omvang worden afgeleid die een maximaal overnight-verlies van exact 1R kapitaal garandeert. ATR-schaling is wel te berekenen, maar is geen verliesplafond.

## 7. Contractrollovers en kalender

Gebruik voor reproductie de reeds vastgelegde rollovers uit `research/historical-rollover-evidence.csv`, `research/holdout-protocol.json` en `research/oos-year-rollovers.json`; herselecteer geen datum op basis van rendement.

De gebruikte volume-route zoekt de eerste gezamenlijk waargenomen sessie waarin de som van het nieuwe contractvolume strikt groter is dan die van het oude, met de bestaande dekkingsvoorwaarden. Oude data moeten de verwachte sessiegrenzen dekken; voor het nieuwe contract gelden de geregistreerde maximaal 60 minuten marge aan begin/eind. Activatie is de eerstvolgende futures-handelsdag, vanaf 18:00 NY op de voorafgaande civiele datum. Ontbreekt objectief bewijs of vereiste overlap, dan is de route onbekend; geen kalender- of P&L-gestuurde fallback.

De indicator-spread is `close_nieuw - close_oud` op de laatste gezamenlijke voltooide 15:59-bar vóór activatie, beschikbaar na die minuut. Pas alleen indicatorcoördinaten aan. Bewaar uitvoering, stops en targets in de ruwe basis van het actieve contract.

**Bindende contractkeuze — `PREOPEN_ROUTE_SAME_CONTRACT_TO_NEXT_CASH_OPEN`:**

1. Vóór 09:30 wordt het reeds voor de huidige RTH-sessie geactiveerde kwartaalcontract X vastgezet. Alleen een volume-besluit uit een eerdere afgesloten futures-sessie met activatie uiterlijk vóór de huidige 09:30 mag worden gebruikt. Het afgeronde volume van vandaag en het actieve contract van morgen mogen de keuze van vandaag niet veranderen.
2. Controleer dan al de bekende expiratiekalender en de eerstvolgende echte cashsessie. Als de geplande volgende 09:30 op of ná de derde-vrijdag-expiratie van X ligt, kies vóór de huidige RTH het volgende kwartaalcontract (H→M→U→Z→H). Dus uiterlijk de dag vóór expiratie het nieuwe contract, ook bij een tussenliggende cashfeestdag. Alle RTH-signalen en indicatoren moeten dezelfde gekozen basis hebben; zonder die vooraf beschikbare historie is er geen complete beslissing. Nooit na entry de contractbasis repareren. In deze dataset zijn nul kalenderoverrides nodig: alle geregistreerde RTH-rollovers liggen al vóór deze grens.
3. Leg om 15:55 X expliciet vast bij de beslissing, inclusief selectietijd, expiratie en het beschikbare vorige routebesluit. De MNQ-order krijgt exact dezelfde maand/jaar als NQ-X (bijvoorbeeld NQM25 → MNQM25); geen automatisch doorlopend symbool gebruiken. Dit is een contractspecificatie, geen bewijs van MNQ-fills.
4. Bevestig na de 15:59-bar de overnight-voorwaarden op X. De onderzoeksentry is de 16:00-open van X. Alle stops en de volgende daadwerkelijke cash-09:30-exit gebruiken uitsluitend X. Een latere volume-switch of indicatorroll om 18:00 verandert de bestaande positie niet. De volgende RTH kan het nieuwe contract gebruiken nadat X om 09:30 is gesloten; B start pas vanaf 09:45.
5. Rollover-nachten blijven meetellen wanneer beide ankers in X aanwezig zijn. Geen contractspread in handels-P&L, geen overboeking, geen achteraf-uitsluiting op basis van morgen. Een ontbrekend anker wordt als onbekend bronresultaat gemeld: niet nul, geen vervangende prijs uit het nieuwe contract en geen live voorspelbaar kwaliteitsfilter. De contractkeuze zelf hangt nooit van de aanwezigheid of uitkomst van de toekomstige exit af.

De bronreplay bewijst deze informatievolgorde en bewaart de keuze vóór het uitlezen van de holdingprijzen. Dit certificeert de contractlogica onder de bestaande bron- en kalenderaannames; het levert geen onafhankelijk bewijs van historische publicatietijdstippen, quote-spreads of exacte first-print fills.

## 8. Uitvoeringsaannames, kwaliteit en administratie

Stopverlies krijgt voorrang wanneer een minuutbar zowel stop als target kan raken en de volgorde onbekend is. Een reeds bij de minuutopen uitvoerbaar target komt vóór een latere intrabar-stop. Een rustend target vereist één tick trade-through; geen gunstiger prijsverbetering. Voor intrabar-limietentries wordt een target alleen geteld wanneer de entry bij open vaststond of een close voorbij het target een latere crossing bewijst. Deze aannames zijn reproduceerbaar, niet tick-gecertificeerd.

Backtestfrictie is totaal **$24,50 per NQ-roundtrip = 1,225 NQ-punt**, ook bij een stop. Twee opeenvolgende pijlers betalen twee volledige roundtrips; geen kostennetting. Deze NQ-aanname is geen daadwerkelijke MNQ-brokerquote en mag niet door tien worden gedeeld om MNQ-kosten te bepalen.

Bewaar per paperbeslissing lokaal: tijdstip, contract, bronstatus, vooraf vastgezette ATR, beide SMA-momenten, alleen toen bekende setupwaarden, geplande/feitelijke orderprijzen, feitelijke kosten, filltijden en afwijkingen. Dag-/tradeledgers en minuutbars blijven privé. Bij datagaten geen verdwenen stop aannemen. De actuele aantallen onvolledige holdingpaden en niet-identificeerbare stopuitkomsten staan per periode in het causale rapport en op het dashboard; de historische aantallen blijven in het archiefrapport. Een CI over gesimuleerde P&L modelleert deze brononzekerheid niet.

Portefeuilleposities worden op tijdstempels op niet-overlap gecontroleerd. Dag-P&L wordt vóór de volgende 16:00-boundary geboekt: overnight op de volgende cashsessie, B op de huidige sessie. Gebruik ook vlakke cashdagen voor Sharpe. R is genormaliseerde P&L; de gepubliceerde punten zijn daarnaast 1 NQ per uitvoering. Dit is geen account-ROI.

## 9. MNQ-formules per zelf gekozen kapitaalbudget

Definieer zelf `E_account` als accountwaarde in USD en `r` als budgetfractie; `K = E_account * r` USD. Dit playbook schrijft geen geschikte accountgrootte of risicofractie voor.

MNQ heeft $2 per indexpunt en een tick van 0,25 punt = $0,50. Bron: [CME MNQ-contractspecificaties](https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html), gecontroleerd 25 oktober 2026. NQ-signalen en fills blijven een proxy: deze dataset bevat geen afzonderlijke MNQ-orderboek-/fillvalidatie. De twee historische perioden omvatten ook tijd vóór introductie van MNQ; presenteer de formule daar niet als daadwerkelijk verhandelde MNQ-trackrecord.

**A. ATR-blootstelling vergelijkbaar met de onderzoeksnormalisatie:**

`q_ATR = floor(K / (2 * A))`

Een beweging van 1 ATR vertegenwoordigt hiermee ten hoogste K aan bruto prijsverandering, vóór kosten. Dit is geen maximaal verliesbudget. Gebruik alleen gehele niet-negatieve contracten; q=0 blijft nul. Geen minimum van één contract afdwingen.

**B. Gepland stoprisico voor S1-A en B:**

Met feitelijke stopafstand `d = E-S > 0` en eigen bevestigde totale MNQ-roundtripfrictie `c_MNQ` USD per contract:

`q_stop = floor(K / (2*d + c_MNQ))`

Voor S1-A gebruikt d de werkelijk tick-afgeronde 0,50-ATR-stop. Voor B gebruikt d de structurele/minimale stop die hierboven is berekend; veronderstel niet automatisch d=0,35*A. Gebruik broker-/beurskosten plus een expliciete uitvoeringsfrictie-aanname in c_MNQ, zonder dubbeltellen. Onbekende kosten blijven onbekend. Zonder die invoer wordt geen stopbudget-uitkomst als compleet gepresenteerd.

Een afzonderlijke gewenste gap-/slippagebuffer g in punten kan in het PLANNINGSbudget worden opgenomen via `2*(d+g)+c_MNQ`; ook dat garandeert geen maximum bij grotere gaps. De rekenhulp gebruikt geen verborgen buffer.

**Voor S2-overnight is q_stop niet gedefinieerd.** Gebruik daar q_ATR uitsluitend als blootstellingsmaat. De geobserveerde max-DD of 95%-CI mag niet als stopafstand of gegarandeerd kapitaalrisico in de noemer worden ingevuld.

**C. Onafhankelijke margecap:**

`q_margin = floor(vrij_beschikbaar_margebudget / bevestigde_overnight_marge_per_MNQ)`

`q_final = min(q_gekozen_budgetmethode, q_margin)`

Gebruik actuele broker-over-nightmarge; intraday korting dekt de overnight-pijler niet. Zonder bevestigde margegegevens is de uitkomst alleen een budgetberekening, niet een afgeronde ordergrootte. Verhoog een positie niet uitsluitend omdat de vorige pijler die dag winst maakte. De vaste modellen gebruiken opeenvolgende blootstelling, geen twee gelijktijdige volledige risicobudgetten.

ATR-sizing en sizing op stopafstand zijn **verschillende blootstellingen**. De laatste kan bijvoorbeeld bij d=0,50*A ongeveer tweemaal de ATR-positie geven. De gepubliceerde R-tabellen gelden niet automatisch voor deze nieuwe gehele MNQ-aantallen, kosten, margecaps of stop-risk-gewichten. Er is in deze publicatie geen nieuwe MNQ-sizing-backtest uitgevoerd.

Rekenvoorbeeld, geen account- of brokeradvies: K=$1.000 en A=200 geven q_ATR=2. Bij d=100 en een uitsluitend illustratieve c_MNQ=$6,50 geeft q_stop=4 vóór margecap. Het verschil is een andere risicomethode, geen gratis extra capaciteit. $6,50 is hier geen bevestigde kostprijs.

## 10. Wat deze publicatie wel vastlegt

De actuele cijfers staan in `SAME_CONTRACT_CAUSAL_EXECUTION.md`, inclusief de volledige vergelijking met het onveranderde `REGIME_CONSOLIDATION_STATISTICS.md`. Alle bestaande trades moeten exact dezelfde prijzen en netto-uitkomst houden; alleen extra same-contract nachten kunnen verschillen veroorzaken. De twee bronreconstructies moeten byte-identieke uitvoer opleveren.

Reproductie: `python -m scripts.same_contract verify`. Volledige replay: `python -m scripts.same_contract replay` (idempotent na bestaande verificatie); twee onafhankelijke herberekeningen worden bij de eerste replay opgeslagen. `python -m scripts.same_contract register` legt methode en code vóór de uitkomsten vast. Publicatie: `python -m scripts.publish_operational_playbook`. De resultaten blijven ontwikkelingsonderzoek, geen onafhankelijke validatie of live-goedkeuring.

Exacte nieuwe uitvoeringsroute: `scripts/same_contract/core.py` en `__main__.py`. Bevroren onderliggende code: `scripts/price_volume/core.py` en `__main__.py`, `scripts/two_pillar/core.py`, `scripts/regime_consolidation/core.py`, `inference.py` en `__main__.py`. Ruwe CSV's en private ledgers blijven buiten Git-updates en productie-upload.


---

# Prop-firmhaalbaarheid en uitvoeringsarchitectuur

Versie 25 oktober 2026. Status: `RETROSPECTIVE_FEASIBILITY_NOT_ACCOUNT_OR_PROFITABILITY_CERTIFICATION`.

Dit is een uitvoeringsontwerp voor paperonderzoek, geen geactiveerde handelsbot, accountgoedkeuring of bewijs van toekomstige winst. Baseline `2ec3a07`, de oorspronkelijke S1/S2-modellen en hun playbook blijven byte-identiek. De volledige ICT-studie, zeven geselecteerde Judas-varianten en directe pijlervervanging blijven afzonderlijke ontwikkelingsrapporten. De nieuwe 18:00-route verandert uitsluitend het overnight-instapmoment en de daarbij behorende stopreferentie. Zij is geen onafhankelijke validatie.

## 1. Wat de officiële regels werkelijk toestaan

Topstep sluit futuresposities uiterlijk om **15:10 Chicago / 16:10 New York**; het risicosysteem kan vanaf 15:08 Chicago beginnen afbouwen. Op normale dagen heropent het handelsvenster om 17:00 Chicago / 18:00 New York. Vrijdagavond is geen heropening. Eerdere product- en feestdagafsluitingen gaan voor. De CME-onderhoudspauze 17:00–18:00 NY is niet hetzelfde als de eerdere prop-firm-flatperiode. [Topstep handelsuren](https://help.topstep.com/en/articles/8284206-when-and-what-products-can-i-trade), [MFFU handelsuren](https://help.myfundedfutures.com/en/articles/9558251-permitted-times-to-trade).

**Topstep:** eigen algoritmen zijn onder voorwaarden toegestaan via TopstepX/ProjectX in de ondersteunde **gesimuleerde** omgeving. Deze API-route geldt niet voor een Live Funded Account. Orders en orderlogica moeten vanaf het persoonlijke apparaat lopen; geen VPS, VPN of externe server die ordertriggers doorstuurt. API-toegang heeft een afzonderlijke betaalde entitlement. Voor deze opdracht is niets gekocht of geactiveerd. [TopstepX API-beleid](https://help.topstep.com/en/articles/11187768-topstepx-api-access).

**MFFU:** de actuele fair-playregels verbieden eigen automatisering niet in algemene zin. Zij verbieden onder meer HFT en exploitatie van simulatiefills. De hieronder beschreven handmatige route is dus een uitvoeringskeuze, geen omweg rond een botverbod. MFFU ondersteunt onder andere Tradovate en TradingView; TopstepX is de Topstep-route en wordt hier niet als MFFU-platform voorgesteld. [MFFU fair play](https://help.myfundedfutures.com/en/articles/8444599-fair-play-and-prohibited-trading-practices), [ondersteunde platforms](https://help.myfundedfutures.com/en/articles/8528335-overview-of-supported-platforms-at-mffu).

De toepasselijke persoonlijke overeenkomst en accountfase blijven beslissend. Een passende handelsklok alleen rechtvaardigt nooit de claim “100% regelconform”.

## 2. Twee afzonderlijke uitvoeringsvarianten

### Eigen broker: oorspronkelijke 16:00-route

Bevestig het signaal na het sluiten van minuut 15:59. De onderzoeksentry is de 16:00-open; zonder eerdere stop volgt de exit op de eerstvolgende echte cashsessie om 09:30. Deze route blijft de vaste eigenbrokerreferentie. Zij kruist in de gereconstrueerde data bij alle 102 selectieve en 735 brede nachten een prop-flatvenster en is daarvoor ongeschikt.

### Prop-uren: 18:00-route

1. Neem exact hetzelfde signaal, dezelfde vooraf bekende ATR14 en hetzelfde vooraf gekozen contract van de signaaldag. Bepaal vóór instap de volgende echte cashsessie uit de kalender.
2. Kies de **18:00 NY op de kalenderdag direct vóór die geplande 09:30-exit**. Donderdag→vrijdag gebruikt donderdag 18:00; vrijdag→maandag gebruikt zondag 18:00. Na een cashfeestdag op maandag gebruikt de variant maandag 18:00→dinsdag 09:30, niet zondag→dinsdag over een extra 16:10-flatvenster.
3. Dit stelt het signaal op gesloten cashdagen uit; het wordt niet opnieuw met toekomstige prijzen beoordeeld. De laatste cashbias kan dus enkele kalenderdagen oud zijn. Deze kalenderwijziging is expliciet onderdeel van de onderzochte variant.
4. Vereis de exacte 18:00-open en 09:30-open in hetzelfde contract. Geen instap op de eerste later beschikbare minuut; geen vervangingscontract kiezen omdat het achteraf betere dekking heeft.
5. **S1-A:** long bij terminale close boven SMA20, RTH-range >0,85 vooraf bekende ATR14 en close in de bovenste 15% van die range. De stop vanaf de nieuwe entry E is `ceil((E-0,50*A)/0,25)*0,25`; geen target. Een gap door de stop krijgt de ongunstigere open. **S2-A:** long op de oorspronkelijke brede bull-populatie bij terminale close boven SMA20, zonder strategie-stop. Een ingevoegde bracketstop zou een ander model zijn.
6. Exit uiterlijk 09:30-open, of eerder bij de vaste S1-stop. Een later op dezelfde dag actieve Judas-positie mag pas na deze uitstap worden geopend.

Alle 837 bedoelde overnightentries hebben beide exacte eindankers. Toch zijn 15/102 selectieve en 104/735 brede nachttrajecten onvolledig. Voor die 15 selectieve nachten is het feitelijke stopverloop niet volledig identificeerbaar. Ontbrekende minuten zijn niet geïnterpoleerd; de uitkomsten en risico-oordelen blijven daarom voorwaardelijk.

## 3. Causale indicatoren en contractkeuze

De ongewijzigde definities van de referentie staan in het oorspronkelijke operationele playbook. ATR14 is het eenvoudige gemiddelde van de laatste 14 eerder geldige RTH-true-ranges van de point-in-time Panama-indicatorreeks, geen Wilder-ATR. Vóór 09:30 wordt `A` vastgezet. De huidige RTH wordt pas na voltooiing aan de historie toegevoegd. SMA20 gebruikt twintig opeenvolgende beschikbare cashsessie-closes, in de op dat moment bekende prijsbasis; geen futures-settlementprijs en geen overslaan van ontbrekende closes.

Voor Judas staat de bias vóór 09:30 vast: gisteren boven de vooraf bekende SMA20 is bullish; eronder bearish; gelijk of onbekend geeft geen betreffende richting. Voor overnight gebruikt de terminale SMA de negentien eerdere closes en de zojuist voltooide huidige close. Om 15:55 is deze laatste selectie dus slechts voorlopig. **Een definitieve 15:55-alert mag de nog onbekende 15:59-close niet gebruiken.**

Het actieve RTH-contract wordt vóór de sessie vastgezet uit het geregistreerde causale rolloverrooster. De positie blijft in datzelfde onverschoven contract tot de exit. Geen beslissing op basis van het later afgeronde sessievolume. Het contract moet ná de geplande 09:30-exit expireren; zo niet, is vóór instap een reeds vastgelegde geldige nieuwe contractkeuze nodig of volgt geen order. Een volgende RTH-Judas kan op de nieuwe actieve expiry handelen terwijl de oude nachtpositie eerst in haar oorspronkelijke expiry wordt gesloten. MNQ gebruikt de overeenkomende expiratie van het NQ-signaalcontract, nooit blind het continu-symbool.

## 4. Exacte twee Judas-specificaties

Beide gebruiken vaste, complete 5m-bars vanaf 09:30; maximaal de eerste geldige order per dag. De oorspronkelijke strenge backtestfill vereist één tick handel dóór de entrylimiet. Dit is een gevoeligheidsaanname, geen beursgarantie op een echte queuefill.

| Regel | S1/S2-Judas-0830 | S1-Judas-Bull0930 |
|---|---|---|
| Richting | Long met bullish SMA20-bias; gespiegeld short met bearish bias | Alleen long met bullish SMA20-bias |
| Shakeout-anker | Exacte 08:30-open | Exacte 09:30-open |
| Shakeout | Long: low ≤ anker−0,15 A; short: high ≥ anker+0,15 A | Dezelfde longregel |
| Ontwikkeltijd sweep | Voltooide bars vanaf 09:30 met bar-start vóór 10:15 | Idem |
| FVG-bevestiging | Na voltooide derde bar, strikt vóór 10:30 | Idem |
| Herstelvoorwaarde | Bullish FVG-close boven 09:30-open; bearish eronder | Bullish FVG-close boven 09:30-open |
| Target | +2 initiële stopR | +2 initiële stopR |
| Tijdsexit | 15:55-open, of reeds vastgelegde eerdere kalendergrens | Idem |

Bullish FVG: `Low[t]-High[t-2] ≥0,03*A` én `Close[t-1]-Open[t-1] ≥0,03*A`. Bearish: `Low[t-2]-High[t] ≥0,03*A` én `Open[t-1]-Close[t-1] ≥0,03*A`. De sweep moet al voltooid zijn vóór het begin van de middelste displacementbar. Het sweep-extremum wordt alleen met tot de bevestiging voltooide bars bijgewerkt. Een bar die beide sweeprichtingen tegelijk raakt levert geen bewijs van volgorde.

Longlimiet `E=Low[t]`; shortlimiet `E=High[t]`. Longstop is de laagste van sweep-low−1 tick en E−0,10 A, neerwaarts op ticks afgerond; shortstop de hoogste van sweep-high+1 tick en E+0,10 A, opwaarts afgerond. `stopR=abs(E-S)`; target `E+2*stopR` long of `E-2*stopR` short. Annuleer de eerste ongevulde order om 10:30; zoek geen mooiere tweede FVG. De Judas-specificatie heeft de oorspronkelijke reclaim/FVG-keten; het extra fractal-MSS-criterium van ICT-1 wordt niet achteraf aan Judas toegevoegd.

Orderactivering vindt pas ná de derde barclose plaats. Stops winnen bij onbewijsbare entry/stop/target-volgorde binnen één minuut. De live/paperroute registreert de werkelijke fills en kan geen historische open of limietfill terugboeken. Noch stopR noch dollarverlies is gegarandeerd door een stoporder.

## 5. Dollar- en accountrisico

De NQ-vergelijking houdt $24,50 (=1,225 punt) per roundtrip. Voor MNQ is bruto P&L `2 USD * punten * q`; trek **per contract** werkelijke MNQ-kosten af. Topstep publiceert $1,22 RT. Met de vaste gevoeligheidsaanname van twee ticks slippage per kant komt dit op $3,22. $6,50 en $9,50 zijn afzonderlijke vaste stressaannames; $6,50 is geen bevestigde MFFU-brokerquote. [Topstep-kosten](https://help.topstep.com/en/articles/8284213-topstepx-commissions-and-fees).

De studie rekent vaste 1, 2 en 3 MNQ door. Zij kiest niet achteraf de beste omvang. Een ATR-genormaliseerd onderzoeksbudget K geeft een rekenhoeveelheid `floor(K/(2*A))`, maar is zonder harde stop **geen maximaal kapitaalrisico**. Bij een vaste stopafstand d is de geplande verliesreserve per contract `2*d + kosten + gapreserve`; een operationele hoeveelheid mag nooit groter zijn dan zowel de strategiehoeveelheid, platformlimiet als het beschikbare verliesvloer-/DLL-budget toelaat. Zo'n dynamische risicobeperking is niet in de ongewijzigde resultaten verwerkt en vereist een eigen paperlog.

Een EOD-trailing limiet begint op −D en stijgt na het dagslot tot `max(vorige vloer, min(lock, hoogste EOD-netto-equity-D))`. De vloer daalt nooit. Topstep lockt bij nul, de gemodelleerde MFFU-EOD-profielen bij +$100. **Intraday open verlies kan de bestaande vloer wel raken.** Daarom toetsen we zowel open/close-markeringen als een conservatieve OHLC-adverse-grens. Bij een target kan de slechtste minuutextremiteit ná de uitstap liggen; zo'n hit is apart als potentieel aangeduid. [Topstep MLL](https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit), [MFFU EOD](https://help.myfundedfutures.com/en/articles/8348565-end-of-day-eod-drawdown-explained).

| Actueel profiel | MLL 50K / 100K | DLL 50K / 100K | Consistency |
|---|---|---|---|
| Topstep Trading Combine | $2.000 / $3.000 EOD | TopstepX optioneel $1.000 / $2.000 | 55% bij target $3.000 / $6.000 |
| MFFU Rapid EOD 50K evaluatie | $2.000; geen gelijknamig 100K-EOD-plan gemodelleerd | Geen | 30%, ten minste vier actieve dagen |
| MFFU Rapid 100K evaluatie | $3.000 EOD | Geen | 50%, ten minste twee actieve dagen |
| MFFU Builder 50K / 100K evaluatie | $2.000 / $3.000 EOD | $1.000 / $1.750 | Geen evaluatie-consistency |
| MFFU Builder simulated funded | $2.000 / $3.000 EOD | $1.000 / $1.750 | 50% per relevante payoutcyclus |

Een DLL is een handelsstop voor die sessie, geen automatische MLL-accountbreuk. Na de eerste DLL-trigger is de ongewijzigde historische rest-P&L slechts een schaduwpad: de firma zou orders kunnen sluiten/blokkeren. Rapid 100K **funded** heeft intraday trailing drawdown en wordt hier uitdrukkelijk niet als EOD-account doorgerekend. [Topstep DLL](https://help.topstep.com/en/articles/10490293-daily-loss-limit-in-the-trading-combine-and-express-funded-account), [Topstep consistency](https://help.topstep.com/en/articles/8284208-consistency-at-topstep), [MFFU Rapid 50K](https://help.myfundedfutures.com/en/articles/16158363-rapid-eod-50k-a-comprehensive-look), [MFFU Rapid 100K](https://help.myfundedfutures.com/en/articles/13286542-rapid-plan-100k-a-comprehensive-look), [Builder 50K](https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide), [Builder 100K](https://help.myfundedfutures.com/en/articles/17005296-builder-plan-100k-comprehensive-guide).

De MFFU-30%-toets gebruikt `grootste positieve dag / totale NETTO winst sinds accountstart of relevante cyclus`, niet de grootste trade of het aandeel in bruto winsten. Verlies wist de beste dag niet. Bij totale winst ≤0 is de ratio ongedefinieerd. Overschrijden is een hogere vereiste winst, geen accountbreuk: voor een beste dag W is bij 30% minimaal `W/0,30` totale winst nodig. De rapportage toont zowel de eerste target+consistencydatum vóór risicotrigger als de eindratio. De volledige historische eindratio bewijst geen payoutgeschiktheid. [MFFU consistency](https://help.myfundedfutures.com/en/articles/11994562-consistency-rule-at-my-fundedfutures).

Accounts starten per tijdperk opnieuw op nul, zonder winsten uit 2021 naar 2024 mee te nemen. Geen payouts, abonnementskosten, resets of funded scaling zijn gesimuleerd. Lange signaalpauzes geven bij MFFU-profielen met zeven kalenderdagen inactiviteit een reëel knelpunt; Topstep XFA kan na langdurige inactiviteit worden gesloten. De conservatieve kalenderdiagnose vervangt geen exact activeringstijdstip. Geen extra fictieve trades om de teller te resetten.

MFFU Rapid EOD simulated funded heeft bovendien nieuwsrestricties; een nachtpositie kan om 08:30 T1-nieuws meemaken. Zonder gevalideerde nieuwskalender kan dit profiel **niet** als conform worden bestempeld. Builder staat nieuws in de geïnspecteerde eval/sim-fase toe; dat is geen vrijbrief voor andere fases. Alle oorspronkelijke datagaten, NQ-als-MNQ-proxy, pre-MNQ-launchhistorie en ontbrekend tickfillbewijs blijven beperkingen.

## 6. Topstep: uitsluitend lokale paper-/simarchitectuur

De blauwdruk gebruikt een lokale toepassing op het persoonlijke apparaat. Vercel bevat alleen onderzoeksaggregaten en documentatie; geen credentials, orderwebhooks, signal relay of broker-endpoints. Begin zonder orders in log-only modus. API-entitlement, accountfase en toepasselijke voorwaarden moeten afzonderlijk geregeld zijn voordat een uitvoeringsadapter kan worden ingeschakeld.

1. Lokale kalender/contractresolver bepaalt de juiste concrete MNQ-expiry. Controleer `tickSize=0,25`, tickwaarde $0,50 en de accounttoegestane hoeveelheid. Geen hardcoded voorbeeldcontract-ID gebruiken.
2. De lokale data-adapter verwerkt gesloten 1m-bars en maakt bevestigde 5m-bars. Indicatorstate gebruikt alleen reeds beschikbare data. Bewaar bron, bar-startconventie, UTC-tijd en `known_at` naast NY-handelsdag.
3. De lokale eventengine onderhoudt bias, sweepstatus, eerste FVG, pending order, fills, stop/target, uiterste annuleer-/flatten-tijden en accountbuffer. Een apart accountslot voorkomt overlap/overmatige sizing.
4. De lokale ProjectX-adapter authenticeert, zoekt accounts en beschikbare contracten en vraagt orderstatus/posities op. De officiële API documenteert onder andere `POST /api/Account/search`, `/api/Contract/available` en `/api/Order/place`. De exacte actuele order- en bracketvelden worden bij implementatie uit de actuele schema's gehaald; dit document levert geen kant-en-klare productieorderpayload.
5. Alleen na bevestigde orderacceptatie en fill wordt de juiste beschermingshoeveelheid gekoppeld. Verwerk partial fills, rejects, cancel/fill-races en OCO-sibling-cancel expliciet. Bij een timeout eerst order/positie reconciliëren; nooit blind opnieuw dezelfde order sturen.
6. Herverbinding en tokens verlopen via de actuele API-specificatie. Bij datastagnatie, onbekende positie of lokale klokafwijking: geen nieuwe orders; bestaande bescherming en flattenproces blijven bewaakt. Een handmatige noodroute is noodzakelijk.

Documentatie: [ProjectX intro](https://gateway.docs.projectx.com/docs/intro/), [eerste order en contractselectie](https://gateway.docs.projectx.com/docs/getting-started/placing-your-first-order/). Dit is een ontwerp, geen reeds gebouwde of geteste brokerintegratie. Geen remote server kan lokale uptime of stopuitvoering garanderen.

## 7. MFFU: alerts en menselijke uitvoering

Gebruik een bevestigde TradingView-alert op het concrete contract, met exacte NY-tijdzone en alleen gesloten 5m-bars. Een alert kan een lokale/persoonlijke melding leveren; de handelaar controleert richting, entry, stop, target, expiry en accountbuffer en voert de order in Tradovate in. TradingView kan via de MFFU/Tradovate-koppeling werken. [Platformverbindingen](https://help.myfundedfutures.com/en/articles/8528337-connecting-to-different-platforms-at-mffu).

Voor Judas en selectieve S1-nachtpositie wordt de vereiste stop gekoppeld; Judas heeft ook het +2 stopR-target en OCO-annulering. Voor de brede S2-nachtpositie bestaat bewust geen strategie-stop: een extra protective stop maakt een nieuw model. Een firma-DLL of handmatig accountnoodstop kan de positie beëindigen; dit is dan een gelogde uitvoeringsafwijking, niet dezelfde historische trade.

Menselijke vertraging kan de eerste FVG-retest missen of een andere prijs geven. Een gemiste order blijft gemist. Log alerttijd, gelezen tijd, submit/ack/fill, echte prijs, hoeveelheid, bracketbevestiging en reden van overslaan/uitstap. Claim geen 100% backtestreplicatie. De sessiegrensguard en nieuws-/inactiviteitsvoorwaarden gelden ook bij handmatige uitvoering; de guard mag niet door een alert worden omzeild.

## 8. Exact gegevenscontract en dagelijkse toestandsmachine

| Moment NY | Benodigde, reeds bekende gegevens | Actie / beslismoment |
|---|---|---|
| Vóór 09:30 | Contract/expiry, kalender, Panama-spreads bekend vóór toepassing, ATR14_prior, twintig eerdere closes/SMA20, 08:30-open | Bevries bias/A, controleer bestaande nachtpositie en accountbuffer |
| 09:30 | Concrete RTH-open; werkelijke nacht-exitfill | Sluit A in hetzelfde contract; initialiseer Judas-ankers |
| Iedere voltooide 5m-bar vanaf 09:35 | OHLCV, laatste drie complete bars, bestaande sweep en extrema, bias/A, 09:30/08:30-open | Detecteer causale sweep/FVG/reclaim; activeer uitsluitend eerste order na bevestiging |
| 10:15 | Tot dan bekende sweepketen | Geen nieuwe sweep met starttijd ≥10:15; bevestiging mag nog strikt vóór 10:30 |
| 10:30 | Pending-orderstatus en fills | Annuleer ongevulde Judas-order; geen nieuwe setup |
| 15:55 | Intradaypositie/stop/targetstatus, actuele accountvloer, kalender | Judas flat; voorlopige overnight-check, terminale close nog onbekend |
| Na sluiting 15:59 | Definitieve normale RTH-high/low/close, terminale SMA20, vaste A, volgende cashdatum, held-contractexpiry | Leg overnightkeuze en geplande 18:00-tijd vast; geen toekomstige contractvolumes |
| Vóór 16:08 / eerdere officiële grens | Orders/posities én platformstatus | Annuleer rests en bevestig flat vóór firmcutoff; geen positie door 16:10–18:00 |
| Geplande 18:00 | Vastgelegd signaal, juiste concrete expiry, actuele accountbuffer, nieuws-/faseprofiel, eerste echte fill | A-entry en eventueel vaste S1-stop; geen instap op achteraf bekende open |
| Volgende 09:30 | Werkelijke exitfill, order-/positie-reconciliatie | A sluiten; OCO-rest annuleren; accountboekhouding bijwerken |

Een veilige implementatie bewaart per gebeurtenis minimaal:

```json
{
  "schema": "quant-prop-paper-v1",
  "event_id": "deterministisch:versie-contract-sessiedatum-type-bevestiging",
  "strategy": "S1_J0830_18",
  "mode": "PAPER_LOG_ONLY",
  "signal_session": "YYYY-MM-DD",
  "known_at_utc": "ISO-8601",
  "bar_start_ny": "ISO-8601 met geldige offset",
  "contract": "concrete MNQ-expiratie via resolver",
  "calendar_version": "hash",
  "rule_profile": "exacte firma-fase-accountvariant",
  "atr14_prior": "vastgezette positieve waarde",
  "sma20_prior": "vooraf bekende waarde",
  "bias": "BULL of BEAR of NONE",
  "anchor_open": "08:30 of 09:30 exacte prijs",
  "sweep_known_at": "voltooide bargrens",
  "sweep_extreme": "tot bevestiging bekende prijs",
  "fvg_confirmed_at": "derde barclose",
  "entry_limit": "tickprijs",
  "initial_stop": "tickprijs of expliciet NONE voor S2-A",
  "target": "+2 stopR voor Judas of NONE voor A",
  "expires_at": "10:30 NY bij pending Judas",
  "planned_flat_at": "15:55 of 09:30 of eerdere kalendergrens",
  "quantity": "gecontroleerd geheel aantal",
  "risk_floor_remaining_usd": "actuele broker-/accountwaarde",
  "dll_remaining_usd": "waarde of expliciet NONE",
  "reconciliation_state": "NO_OPEN_OR_UNKNOWN_ORDERS"
}
```

Dit is een veldspecificatie, geen direct instuurbaar orderbericht. Geen authenticatietoken, account-ID of privéprijsarray komt in de publieke webhook-/dashboardbestanden. De lokale order-adapter gebruikt een apart geauthenticeerd schema en idempotency-log. De publieke site accepteert geen orders.

## 9. Wat de haalbaarheidsrun concludeert

De cijfers staan in `PROP_FIRM_FEASIBILITY_REPORT.md` en drie CSV's: alle 36 NQ-performancerijen, 108 MNQ-kostenscenario's en 936 accountchecks. De twee bronreconstructies produceren byte-identieke bestanden. De 16:00-herberekening reproduceert de eerdere Judas-vervanging exact.

De 18:00-selectieve A verliest historisch een aanzienlijk deel van de genormaliseerde winst; in 2019–2021 is A alleen netto negatief in ATR-R. S1-Judas-Bull0930 heeft gecombineerd een lagere ongeschaalde puntendrawdown dan S1-Judas-0830, maar in het oudere blok met $6,50 MNQ-kosten is de dollarwinst van Bull0930 negatief. Een lagere drawdown van een losse Judas-pijler maakt de gecombineerde rekening niet automatisch veiliger: bij 2–3 MNQ raakt Bull0930 in enkele oudere 50K/100K-profielen de MLL.

Bij brede S2-portefeuilles zijn DLL-triggers in meerdere recente Builder-scenario's zichtbaar; bij hogere sizing komen ook potentiële of geobserveerde MLL-hits voor. Een succesvolle evaluatieprefix vóór zo'n latere trigger bewijst geen duurzaam funded-overleven. MFFU-inactiviteit en Rapid-funded-nieuwsregels blijven aanvullende poorten. Er is daarom **geen algemene prop-goedkeuring voor 1–3 MNQ**, en geen wijziging van regels/sizing om deze achteraf passend te maken.

Reproductie: `.venv/bin/python -m scripts.prop_firm verify` controleert de locks en identieke uitkomsten. De eerste volledige `replay` bouwde tweemaal vanaf de geregistreerde bronnen; de bestaande voltooide replay wordt daarna niet stilzwijgend overschreven. Publicatie: `.venv/bin/python -m scripts.publish_prop_firm`. De releasebuilder exporteert uitsluitend gecommitteerde frontendbestanden, zonder ruwe CSV's, ledgers, omgevingsbestanden of uitvoeringscredentials.
