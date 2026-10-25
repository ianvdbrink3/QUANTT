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
