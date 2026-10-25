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
