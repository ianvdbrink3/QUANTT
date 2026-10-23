# Preregistratie drie signalen en vaste ATR-portefeuille — 22 oktober 2026

Status: REGISTERED_NOT_RELEASED. Nog geen berekening op nieuwe2019–2021-uitkomsten. Dit document is een aanvulling, geen vervanging van de bestaande afternoon-v2-registratie.

## Afbakening en toegangsgeschiedenis

Volledig historisch beschrijvend venster:2019-01-02–2021-12-31. Opwarming vanaf2018-11-19. Uitkomsten van2019-01-02,03,04,07,08,09,10,11 zijn al tijdens de marathon bekeken, ook voor de nieuwe kandidaten. Deze8dagen zijn geen verse bevestiging. De nieuwe beslissende deelsteekproef loopt daarom vast van2019-01-14 tot2021-12-31; die keuze volgt uit de toegangslog, niet de uitkomsten. De8dagen blijven toegestaan als vooraf bekende indicatorhistorie. Eerdere grovere bestanden kunnen deze jaren bestrijken; absolute onbekendheid van alle marktinformatie is niet aantoonbaar. De435en493sessies zijn beide gebruikte selectiedata. De493zijn bovendien een onbevestigde generieke bron, geen contract-gevalideerde onafhankelijke bevestiging.

Geen optioneel eindpunt, verlenging, tussentijds resultaat, horizonwisseling of vervanging bij falen. Geen2019–2021-backtest nu. Eerst complete metadata-, numerieke kwaliteit-, kalender-, rollover- en codeversielock, daarna afzonderlijke expliciete vrijgave. De ontvangen CSV's blijven privé. Geen tick- of brokerfill-certificatie door deze registratie.

## Exact drie ongewijzigde signaalregels

Tijdzone America/New_York met kalender-DST. Barlabels volgen de bestaande Barchart-contractadapter. Alle beslissingen gebruiken alleen voltooide bevestigingsbars; entry op volgende minuutopen. Ongewijzigde regels in `scripts/edge_marathon/core.py` en kalenderdefinitie in `features.py`, beide gehasht in de nieuwe lock.

1. **TOM_RTH:** laatste cashhandelsdag van de maand en eerste3cashhandelsdagen. Long09:30minuutopen, exitclose15:59. Maandpositie wordt vooraf uit officiële kalender bepaald, niet uit alleen aanwezige data. Geen trendfilter, ATR-drempel of stop.
2. **COMPRESSED_BREAK5:** vorige RTH high−low strikt kleiner dan0,65×vooraf bekende ATR14. Zoek de eerste voltooide5-minutenclose buiten PDH/PDL: erbovenlong, erondershort. Beslismomenten09:35tot15:55 in5-minutenstappen. Entryvolgendeminuuropen, exit15:59close. Maximaal1trade perdag, geen stop of target.
3. **SWEEP_REV_1200:** eerste30RTH-minuten raken strikt boven ONH of onder ONL maar niet beide. Close09:59 strikt terugbinnen ONL/ONH en hoger dan09:30open na lage sweep (long), respectievelijk lager na hoge sweep (short). Entry10:00open, exit11:59close. Geen latere sweep of middagexit. De informele naam “Vroege Sweep → Middag” betekent hier exact deze bestaande12:00-uitstap, niet16:00.

Geen nieuwe filters. PDH/PDL, overnightankers, ATR en sessiekwaliteit volgen de bevroren point-in-time adapter, geen achteraf geoptimaliseerde grens. PriorATR is exact de reeds gebruikte14-sessiemaatstaf; geen nieuwe ATR-formule onder dezelfde naam. De toekomstige jaarkalenderadapter moet de oude jaren bit-identiek reconstrueren vóór vrijgave.

## Schaling en frictie

Primaire uitkomst per sessie: `(richting×(exit−entry)−1,225)/vooraf_bekende_ATR14`, met1,225NQpunt=$24,50RT. Dit is ATR-schaling, geen1ATRstop of maximaal toegestaan verlies. Ontbrekende/niet-positieve ATR geeft bekende grootte nul en wordt apart geteld, niet aangevuld uit toekomstige data.

Vier vooraf vastgelegde objecten: de drie afzonderlijke signalen en hun vaste gelijke1/3-combinatie. Iedere sleeve krijgt1/3van het ATR-budget; geen herweging, compensatie, herverdeling van ongebruikt budget of korting op overlappende orderkosten. Off-signal dagen blijven nul, alle technisch geldige sessies blijven in de dagelijkse steekproef. Geen compounding.

Secundaire uitvoerbaarheidsberekening, geen extra signaalhypothese: vast illustratief dollar-ATRbudgetB=$1.000. MNQwaarde$2/punt, tick0,25punt=$0,50. Ideaal q=B/(2×ATR), portfolio q=B/(3×2×ATR) per sleeve. Integerfloor vóór entry, mag nul worden. Nooit minimum1contract afdwingen of B verhogen na inzage. MNQRT-aanname$6,50=$4,50commissie/fees+$2slippage(2ticks per kant). De gebruiker kent zijn brokerkosten niet; dit is geen offerte. Geen mechanische$24,50/10. Bewaar kostensom per echt berekend contract. Deelbare contracten zijn theoretisch, NQbars zijn geen MNQfillbewijs. Vóór6mei2019bestond MNQ niet: daar alleen hypothetisch dollar-equivalent, geen werkelijk MNQ-handelsresultaat.

## Kalender, rollover en kwaliteitsblokkades

Cashsluitingen volgens de vooraf gepubliceerde NYSEkalender van4december2018:

| Jaar | Gesloten cashdatums | Cashhalfdag tot13:00NY |
|---|---|---|
|2019|01-01,01-21,02-18,04-19,05-27,07-04,09-02,11-28,12-25|07-03,11-29,12-24|
|2020|01-01,01-20,02-17,04-10,05-25,07-03,09-07,11-26,12-25|11-27,12-24|
|2021|01-01,01-18,02-15,04-02,05-31,07-05,09-06,11-25,12-24|11-26|

Juneteenth2020/2021is geen NYSEsluitingsdag;31december2021is open. Cashkalender is niet hetzelfde als complete CMEfutures-haltkalender. Officiële CMEholiday-,expiry- en2020circuitbreaker/haltinformatie moeten nog vóór testvrijgave aan technische kwaliteit worden gekoppeld. Geen aannames dat elke ontbrekende minuut corrupt is, en geen outcome-afhankelijke uitzonderingen. Halfdagen worden als officiële halfdag gelabeld en blijven buiten het volledige390-minutensample. Geen prijzen doorvullen.

Volume-rollover: bestaande vaste objectieve regel, nieuwecontractvolume groter dan oude over een volledig afgelopen handelssessie, activering pas volgende handelssessie. Geen resultaatvergelijking tussen rollerdatums. Spread uit laatste gezamenlijke RTHclose vóór activering; causale indicatoradjustment gebruikt alleen op dat moment bekende spreads. Indicatorhistorie loopt door, entries/exits blijven op actieve ruwe contractprijzen. Ontbrekende vergelijking → DATA_INSUFFICIENT, geen willekeurige kalenderfallback. Geen open posities over de contractwissel.

## Beslisprotocol vóór vrijgave

Dagelijkse netRgemiddelden, alle nul-dagen inbegrepen. Vier **co-primaire** tweezijdige toetsen, één per signaal en één voor de vaste combinatie; alpha0,05, Holm4, positieve nettoverwachting noodzakelijk. Geen primaire/secondaire reddingsconstructie. Gezamenlijke moving-blockbootstrap van2opeenvolgende kalendermaanden,10.000herhalingen, vaste seed20261022311,95%nominale percentileCI, gecentreerde benaderende tweezijdige p. Resample exact dezelfde maandblokken voor alle modellen, behoud dagclusters en kruis-correlatie. Geen trade-IIDbootstrap. Rapporteer ook alle ruwe p, PF, Sharpe, dagelijkse en minuutgemarkeerde DD, staarten, kwartaalconcentratie en volledige vaste eindperiode, ongeacht resultaat.

Bij toetsing van de bestaande2afternoon-v2-horizons op hetzelfde resterende venster blijven hun oorspronkelijke resultaten/Holm2apart reproduceerbaar. Een projectbrede bevestigingsclaim vergt daarnaast gezamenlijkeHolm6over deze4+die2; niet-uitgevoerde hypothesen krijgenp=1. Geen opsplitsing van dezelfde nieuwe data in handige families om promotie af te dwingen. Deze nieuwe registratie verandert oude v2bytes niet.

Informatievloer voor een formeel oordeel: minimaal24bruikbare kalendermaanden en30ATR-readytrades per afzonderlijk signaal; daaronder INCONCLUSIVE, geen verlenging. Dit zijn vaste operationele minima, geen bewijs van80%power. Einde vast31december2021. Een positieve significante uitkomst heet STATISTICAL_SUPPORT_ON_REGISTERED_REMAINDER, niet “bewezen winstgevend” of vrijgave voor echt geld. Kosten, bronkwaliteit, fills, drawdownacceptatie, margin en toekomstig regime blijven afzonderlijke vereisten. De resterende toegangsgeschiedenis en onzekere effectieve steekproef beperken bewijskracht.

## Bronnen

- [NYSE2019–2021voorafkalender](https://ir.theice.com/press/news-details/2018/NYSE-Group-Announces-2019-2020-and-2021-Holiday-and-Early-Closings-Calendar/default.aspx)
- [CME MNQcontract](https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html)
- [CME MicroE-mini FAQ en lancering6mei2019](https://www.cmegroup.com/articles/faqs/frequently-asked-questions-micro-e-mini-equity-index-futures.html)
