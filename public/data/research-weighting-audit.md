# Wegingsaudit: dagextremen, eventaantallen en schijnbare voorspelbaarheid

## Kernuitkomst en afbakening

Een eventgewogen en een daggewogen gemiddelde meten verschillende grootheden. Het delen door het uiteindelijke aantal events kan in een koersproces met onvoorspelbare toekomstige log-rendementen toch een niet-nul daggemiddelde opleveren. Dat is geen tegenstrijdigheid en op zichzelf geen fout in de optelling. Het is wel een probleem wanneer zo’n daggemiddelde als bewijs voor voorspelbaarheid wordt gebruikt.

De nieuwe audit controleert dit met alle256 korte muntworpkoerspaden, een onafhankelijke bronherberekening en **12,285 nul-experimenten**, samen 5,343,975 gesimuleerde handelsdagen. Vier meetwijzen, twee recordsides en drie horizonten staan volledig in de publicatie. De drie nulscenario’s zijn illustratief, geen bewezen NQ-marktmodellen.

**Geen nieuw handelsmodel.** De vier basisschermen blijven ARCHIVED_NOT_VALIDATED. Geen entries, stops, targets, koersdoelen, filters voor toekomstige trading, parameterzoektocht of nieuwe holdout. De oorspronkelijke ruwe-marktmetingen en p-waarden zijn niet overschreven.

### Concrete uitkomst van deze batch

- Iedere afzonderlijke daggewogen record/horizontoets verwerpt gemiddelde0 na Holm43 in 128–128 van128 panelen, in alle drie nulscenario’s. De echte toekomstige richtingsinnovaties blijven daarin onvoorspelbaar.
- Van alle72 NQ-versus-nulmodelvergelijkingen haalt 1 de Holm72-grens. Voor de36 vergelijkingen van de twee meetcontroles1/k en eerste record zijn dat 0.
- De overblijvende afwijking betreft RECORD_LOW, 15m, Iedere eventdag gelijk tegenover Gaussian i.i.d.: NQ 11,140 bp versus nulmediaan 5,654, Holm72 p=0,035156. Dezelfde meetwijze tegenover de andere scenario’s: Gaussian met klok- en dagschaal: Holm72 p=0,102539; Spiegelingen echte barvormen: Holm72 p=0,664062. Dit is een nulmodelafwijking, geen gevalideerde edge; de Monte-Carlo-resolutiegrens wordt hieronder expliciet behandeld.

Het kernprobleem is dus niet dat de eerder gepubliceerde daggemiddelden verkeerd waren opgeteld. Hun gebruik als argument voor voorspelbare omkeer is niet gerechtvaardigd: hetzelfde soort effect is aantoonbaar verenigbaar met processen zonder voorspelbare vervolgrendementen. De audit bewijst niet dat iedere mogelijke marktvoorspelling onmogelijk is.

## 1. Wat wordt precies gemiddeld?

Voor dag d: N_d = aantal horizon-eligible records, Y_dk = getekend vervolgrendement van record k, S_d = som van Y_dk. D+ telt alleen dagen met minstens één dergelijk record. Alle rendementen zijn log-basispunten; lows krijgen géén omgekeerd teken.

| Meting | Formule | Wat is bekend op het eventmoment? |
|---|---|---|
| Ieder event gelijk | Σ_d S_d / Σ_d N_d | Het huidige record en de verstreken geschiedenis; het totale aantal events nog niet. De teller is een som van causaal gekozen event-outcomes. |
| Iedere eventdag gelijk | gemiddelde_d(S_d/N_d), alleen N_d>0 | Het uiteindelijke N_d is pas aan het einde van het eventvenster bekend. Elk vroeg event krijgt daardoor een achteraf bepaald gewicht. |
| Gepoold1/k | Σ_dk(Y_dk/k) / Σ_dk(1/k) | k is de rang van het huidige record, bekend op het eventmoment. Er volgt géén per-dag renormalisatie. De eindige globale ratio is niet gegarandeerd exact onvertekend. |
| Eerste record | Gemiddelde uitkomst van het eerste record per eventdag | Het optreden van het eerste record is een begrensde stopping time. Dit is een meetcontrole, geen voorgestelde entry of filter. |

Onder een martingaal voor log-prijzen is het verwachte toekomstige log-rendement na een causaal vastgesteld record nul. Een gewicht dat van latere records afhangt hoeft echter niet onafhankelijk te zijn van dat vervolgrendement. Een beschrijvend daggemiddelde kan dus echt niet-nul zijn in een markt zonder deze voorspelbaarheid.

### Exacte identiteit

`eventgemiddelde − daggemiddelde = Cov_pop(N_d, S_d/N_d) / gemiddelde(N_d)`

Deze identiteit geldt exact over dezelfde eventdagen, zonder regressie of geschatte parameters. Zij verklaart rekenkundig het volledige verschil tussen de twee gemiddelden, maar identificeert géén causaal percentage van een trading edge.

Een eenvoudig voorbeeld: dag A heeft drie outcomes van +1, dag B één van −3. Het eventgemiddelde is0, het daggemiddelde −1. Geen fout: de weging veranderde. Dit voorbeeld alleen bewijst geen onvoorspelbaar proces; daarvoor volgt de exacte muntworpcontrole.

### NQ: exacte ontbinding

| Record | Horizon | Events | Eventdagen | Eventgem. bp | Daggem. bp | Verschil | 95%CI gepaard verschil | Cov(N,daggem.) / gem.N | Numeriek restverschil |
|---|---|---|---|---|---|---|---|---|---|
| RECORD_HIGH | 15m | 7699 | 388 | 0,352 | -7,323 | 7,675 | [6,165; 9,251] | 7,675 | -0,000000000000 |
| RECORD_HIGH | 60m | 7326 | 384 | -0,032 | -17,348 | 17,315 | [14,451; 20,360] | 17,315 | 0,000000000000 |
| RECORD_HIGH | rth_close | 7940 | 389 | 0,633 | -33,157 | 33,790 | [27,229; 40,905] | 33,790 | -0,000000000000 |
| RECORD_LOW | 15m | 6247 | 400 | 0,460 | 11,140 | -10,680 | [-12,302; -9,134] | -10,680 | 0,000000000000 |
| RECORD_LOW | 60m | 5887 | 400 | -0,793 | 22,545 | -23,338 | [-26,933; -19,982] | -23,338 | 0,000000000000 |
| RECORD_LOW | rth_close | 6360 | 400 | -1,348 | 37,357 | -38,705 | [-48,238; -30,504] | -38,705 | 0,000000000000 |

### Spreiding van het eventaantal per eventdag

| Record | Horizon | Minimum N | Mediaan N | P95 N | Maximum N |
|---|---|---|---|---|---|
| RECORD_HIGH | 15m | 1 | 17,0 | 49,9 | 116 |
| RECORD_HIGH | 60m | 1 | 16,0 | 48,0 | 102 |
| RECORD_HIGH | rth_close | 1 | 17,0 | 51,6 | 116 |
| RECORD_LOW | 15m | 1 | 12,0 | 43,0 | 98 |
| RECORD_LOW | 60m | 1 | 11,0 | 40,0 | 89 |
| RECORD_LOW | rth_close | 1 | 12,0 | 45,0 | 98 |

## 2. Exact tegenvoorbeeld: alle256 muntworpkoerspaden

Acht onafhankelijke symmetrische log-prijsstappen van +1/−1; alle256 paden even waarschijnlijk. Elke bar omvat open en close. De eerste bar vormt alleen het initiële high/low. Records en censoring worden zonder enige marktdata bepaald. Geen drift of voorspelbare volgende stap. De scalar referentie en vectorberekening zijn afzonderlijk geschreven en getest.

| Record | Horizon | Paden | Eventdagen | Eventgemiddelde | Daggemiddelde | Gepoold1/k | Eerste record |
|---|---|---|---|---|---|---|---|
| RECORD_HIGH | 1 | 256 | 146 | 0,000000 | -0,282192 | 0,000000 | 0,000000 |
| RECORD_HIGH | rth_close | 256 | 146 | 0,000000 | -0,541096 | 0,000000 | 0,000000 |
| RECORD_LOW | 1 | 256 | 146 | 0,000000 | 0,282192 | -0,000000 | 0,000000 |
| RECORD_LOW | rth_close | 256 | 146 | 0,000000 | 0,541096 | -0,000000 | 0,000000 |

De waarden hebben hier de eenheid van de muntworp-logprijsstap, niet een gekalibreerde NQ-puntwaarde. Dit exacte tegenvoorbeeld toont dat een niet-nul daggewogen recordgemiddelde geen voldoende bewijs voor voorspelbare toekomstige rendementen is. Het zegt niet welk percentage van elk waargenomen NQ-effect door hetzelfde mechanisme ontstaat.

## 3. Onafhankelijke bron- en formulecontrole

69 bronbestanden opnieuw op SHA-256 gecontroleerd; dezelfde435 complete RTH-dagen en454 geplande sessierijen als eerder. 41459 record/horizonregels onafhankelijk opnieuw geïdentificeerd. Datums, eventlabels, bar-tijden, puntsverschillen en log-rendementen komen overeen met de vorige private eventregels.

Maximaal absoluut verschil met een gepubliceerd gemiddelde: 0,000000000000 bp. Maximaal verschil met eerdere 95%-bootstrapgrenzen: 0,000000000000 bp. Maximaal p-verschil van de eerdere gecentreerde nulwaardetoets: 0,000000000000.

De nieuwe rekenkern importeert geen eerdere eventextractor, gemiddelden-, bootstrap- of Holm-functie. De bestaande import-/kalender-/contractregisters worden wel hergebruikt: de audit mag de dataset of rolloverkeuze niet veranderen. Runtimeblokkades verhinderen het aanroepen van strategiefuncties tijdens de bronextractie.

### Alle vier gemeten NQ-estimators

Nominale 95%-intervallen uit een onafhankelijk geïmplementeerde circular moving-block bootstrap:4.000 replicaties, blokken van vijf geplande sessies, seed20261022. De19 uitgesloten sessies blijven als ontbrekende maskers in de kalender; geen fictieve nulrendementen. Intervallen zijn niet simultaan. Er worden hier geen nieuwe nulwaardep-waarden op de extra meetcontroles geplakt.

| Record | Horizon | Meetwijze | Eventdagen | Events | Gemiddelde bp | Nominaal95%CI |
|---|---|---|---|---|---|---|
| RECORD_HIGH | 15m | Ieder event gelijk | 388 | 7699 | 0,352 | [-0,554; 1,249] |
| RECORD_HIGH | 15m | Iedere eventdag gelijk | 388 | 7699 | -7,323 | [-9,225; -5,591] |
| RECORD_HIGH | 15m | Gepoold gewicht1/k | 388 | 7699 | 1,483 | [-0,023; 2,996] |
| RECORD_HIGH | 15m | Eerste record per dag | 388 | 7699 | 1,882 | [-0,843; 4,498] |
| RECORD_HIGH | 60m | Ieder event gelijk | 384 | 7326 | -0,032 | [-2,734; 2,359] |
| RECORD_HIGH | 60m | Iedere eventdag gelijk | 384 | 7326 | -17,348 | [-21,232; -13,588] |
| RECORD_HIGH | 60m | Gepoold gewicht1/k | 384 | 7326 | 2,054 | [-1,813; 5,736] |
| RECORD_HIGH | 60m | Eerste record per dag | 384 | 7326 | 3,912 | [-0,822; 8,664] |
| RECORD_HIGH | rth_close | Ieder event gelijk | 389 | 7940 | 0,633 | [-5,511; 6,675] |
| RECORD_HIGH | rth_close | Iedere eventdag gelijk | 389 | 7940 | -33,157 | [-41,829; -25,498] |
| RECORD_HIGH | rth_close | Gepoold gewicht1/k | 389 | 7940 | 2,222 | [-5,422; 9,703] |
| RECORD_HIGH | rth_close | Eerste record per dag | 389 | 7940 | 2,275 | [-6,888; 11,070] |
| RECORD_LOW | 15m | Ieder event gelijk | 400 | 6247 | 0,460 | [-1,266; 2,197] |
| RECORD_LOW | 15m | Iedere eventdag gelijk | 400 | 6247 | 11,140 | [9,012; 13,338] |
| RECORD_LOW | 15m | Gepoold gewicht1/k | 400 | 6247 | 0,990 | [-1,299; 3,285] |
| RECORD_LOW | 15m | Eerste record per dag | 400 | 6247 | 2,109 | [-1,062; 5,247] |
| RECORD_LOW | 60m | Ieder event gelijk | 400 | 5887 | -0,793 | [-4,808; 3,344] |
| RECORD_LOW | 60m | Iedere eventdag gelijk | 400 | 5887 | 22,545 | [18,756; 26,320] |
| RECORD_LOW | 60m | Gepoold gewicht1/k | 400 | 5887 | 0,510 | [-3,855; 4,566] |
| RECORD_LOW | 60m | Eerste record per dag | 400 | 5887 | 2,973 | [-2,626; 8,358] |
| RECORD_LOW | rth_close | Ieder event gelijk | 400 | 6360 | -1,348 | [-11,812; 8,620] |
| RECORD_LOW | rth_close | Iedere eventdag gelijk | 400 | 6360 | 37,357 | [31,205; 43,472] |
| RECORD_LOW | rth_close | Gepoold gewicht1/k | 400 | 6360 | -0,825 | [-9,538; 7,780] |
| RECORD_LOW | rth_close | Eerste record per dag | 400 | 6360 | 1,885 | [-7,155; 10,342] |

## 4. Drie nulscenario’s zonder voorspelbare toekomstige log-rendementen

Per scenario4.095 onafhankelijke experimenten van435 dagen en390 minuten. Masterseed20261023; per scenario een vooraf afgeleide eigen random stream. Geen gekozen gunstige seed, tussentijdse p-inspectie, uitbreiding of optional stopping. De Gaussian scenario’s gebruiken acht substeps per minuut om OHLC-records te construeren.

- **Gaussian i.i.d.**: Independent zero-mean Gaussian log increments,8 independent substeps/minute and390 minutes/day. Constant minute variance equals observed pooled RTH realized variance/390. No drift; conditional expected future log return is0.
- **Gaussian met klok- en dagschaal**: Same zero-mean independent Gaussian substeps;13 fixed halfhour variance factors calibrated from real squared close increments, plus independent empirical daily RV-scale draws normalized to unit second moment. Volatility varies, conditional mean remains0.
- **Spiegelingen echte barvormen**: For every observed bar, reflect its full open/high/low/close log-offset shape around previous close by an independent fair sign. Concatenate reflected close increments. Actual magnitude/wick/time/day patterns fixed, directions randomized. Conditional simulated future close increments have mean0. No assertion this is an exact NQ data-generating process.

De Gaussian modellen zijn onafhankelijk in toekomstige richtingsinnovaties. Variabele volatiliteit kan voorspelbaar zijn zonder dat het conditionele gemiddelde van toekomstige log-rendementen van nul afwijkt. Het spiegelingsmodel houdt de echte barvormen/absolute bewegingen vast maar trekt onafhankelijke richtingsspiegelingen. Die vaste volledige templates zijn een conditioneel nulmodel, geen informatie die als handelsinput wordt gebruikt.

Het eerste scenario benadert geen ticks, spread of prijsrooster. Het tweede bewaart geen volledige regime-afhankelijkheid. Het derde veronderstelt spiegelingssymmetrie en is geen bewezen invariantie van NQ. De drie scenario’s worden allemaal gerapporteerd; er wordt geen best passend model uitgekozen.

### Uitsluitend volatiliteitskalibratie, geen fit op vervolgrendement

Gepoolde minuut-SD: 5,369 bp. Dagvolatiliteitsschalen hebben tweede moment 1,000000. De13 klokfactoren volgen uit gemiddelde gekwadrateerde minuutrendementen per halfuur; geen optimalisatie op de record-outcomes.

### Alle72 NQ-versus-nulmodelvergelijkingen

P2,5/P97,5 hieronder vormen een **nulmodel-predictie-interval voor een experiment van435 dagen**, geen betrouwbaarheidsinterval van het echte effect. Daarnaast staan nulmediaan, gemiddelde en Monte-Carlo-standaardfout van het nulgemiddelde.

Tweezijdige vergelijkingswaarde: `min(1, 2×min((1+#null≤observed)/4096, (1+#null≥observed)/4096))`. Eén globale Holm-correctie over3×2×3×4=72 vergelijkingen. De minimale ruwe tweezijdige p is2/4096. Deze waarden zijn modelafhankelijke controles, geen nieuwe onafhankelijke of exacte confirmatoire bewijzen: Gaussian kalibratie gebruikt eerder bekeken NQ-data en spiegelingsvaliditeit vereist de genoemde invariantie.

| Nulmodel | Record | Horizon | Meetwijze | NQ bp | Nulgem. | MC-SE nulgem. | Nulmediaan | NulP2,5 | NulP97,5 | NQ−nulmediaan | p modelcheck | p Holm72 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Gaussian i.i.d. | RECORD_HIGH | 15m | Ieder event gelijk | 0,352 | -0,005 | 0,008 | -0,005 | -0,971 | 0,941 | 0,356 | 0,453125 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | 15m | Iedere eventdag gelijk | -7,323 | -5,626 | 0,010 | -5,615 | -6,864 | -4,467 | -1,709 | 0,006348 | 0,437988 |
| Gaussian i.i.d. | RECORD_HIGH | 15m | Gepoold gewicht1/k | 1,483 | 0,002 | 0,010 | 0,013 | -1,223 | 1,189 | 1,470 | 0,013672 | 0,916016 |
| Gaussian i.i.d. | RECORD_HIGH | 15m | Eerste record per dag | 1,882 | 0,004 | 0,016 | 0,023 | -1,973 | 1,918 | 1,860 | 0,055664 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | 60m | Ieder event gelijk | -0,032 | -0,026 | 0,023 | -0,040 | -2,836 | 2,797 | 0,007 | 0,997559 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | 60m | Iedere eventdag gelijk | -17,348 | -16,404 | 0,023 | -16,442 | -19,210 | -13,516 | -0,905 | 0,523926 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | 60m | Gepoold gewicht1/k | 2,054 | 0,004 | 0,024 | -0,022 | -3,111 | 3,032 | 2,075 | 0,193359 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | 60m | Eerste record per dag | 3,912 | 0,028 | 0,032 | 0,030 | -4,048 | 4,122 | 3,882 | 0,062500 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | rth_close | Ieder event gelijk | 0,633 | -0,091 | 0,070 | -0,011 | -8,797 | 8,632 | 0,644 | 0,880859 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | rth_close | Iedere eventdag gelijk | -33,157 | -39,666 | 0,062 | -39,610 | -47,349 | -31,949 | 6,453 | 0,098145 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | rth_close | Gepoold gewicht1/k | 2,222 | 0,009 | 0,073 | -0,025 | -9,200 | 9,293 | 2,248 | 0,630371 | 1,000000 |
| Gaussian i.i.d. | RECORD_HIGH | rth_close | Eerste record per dag | 2,275 | 0,076 | 0,080 | 0,043 | -9,995 | 10,163 | 2,233 | 0,670410 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | 15m | Ieder event gelijk | 0,460 | 0,003 | 0,008 | 0,006 | -0,940 | 0,968 | 0,454 | 0,344238 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | 15m | Iedere eventdag gelijk | 11,140 | 5,646 | 0,010 | 5,654 | 4,452 | 6,872 | 5,486 | 0,000488 | 0,035156 |
| Gaussian i.i.d. | RECORD_LOW | 15m | Gepoold gewicht1/k | 0,990 | 0,011 | 0,010 | 0,014 | -1,227 | 1,267 | 0,976 | 0,117188 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | 15m | Eerste record per dag | 2,109 | 0,025 | 0,016 | 0,042 | -2,014 | 2,032 | 2,067 | 0,043457 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | 60m | Ieder event gelijk | -0,793 | 0,030 | 0,023 | 0,017 | -2,904 | 3,039 | -0,810 | 0,581055 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | 60m | Iedere eventdag gelijk | 22,545 | 16,426 | 0,023 | 16,429 | 13,549 | 19,353 | 6,117 | 0,000977 | 0,069336 |
| Gaussian i.i.d. | RECORD_LOW | 60m | Gepoold gewicht1/k | 0,510 | 0,010 | 0,025 | -0,019 | -2,988 | 3,084 | 0,528 | 0,744629 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | 60m | Eerste record per dag | 2,973 | 0,025 | 0,032 | 0,008 | -3,978 | 4,050 | 2,966 | 0,152344 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | rth_close | Ieder event gelijk | -1,348 | 0,209 | 0,070 | 0,167 | -8,479 | 8,968 | -1,515 | 0,717285 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | rth_close | Iedere eventdag gelijk | 37,357 | 39,817 | 0,062 | 39,752 | 32,207 | 47,712 | -2,395 | 0,544434 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | rth_close | Gepoold gewicht1/k | -0,825 | 0,141 | 0,074 | 0,104 | -8,842 | 9,513 | -0,930 | 0,844727 | 1,000000 |
| Gaussian i.i.d. | RECORD_LOW | rth_close | Eerste record per dag | 1,885 | 0,129 | 0,080 | 0,079 | -9,759 | 10,336 | 1,807 | 0,741699 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 15m | Ieder event gelijk | 0,352 | -0,021 | 0,009 | -0,018 | -1,177 | 1,183 | 0,370 | 0,524902 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 15m | Iedere eventdag gelijk | -7,323 | -7,766 | 0,015 | -7,741 | -9,725 | -6,000 | 0,418 | 0,634277 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 15m | Gepoold gewicht1/k | 1,483 | -0,017 | 0,015 | -0,016 | -1,862 | 1,813 | 1,499 | 0,115234 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 15m | Eerste record per dag | 1,882 | -0,026 | 0,024 | -0,014 | -3,018 | 2,910 | 1,896 | 0,210938 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 60m | Ieder event gelijk | -0,032 | -0,083 | 0,026 | -0,065 | -3,434 | 3,200 | 0,033 | 0,985840 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 60m | Iedere eventdag gelijk | -17,348 | -20,218 | 0,033 | -20,174 | -24,440 | -16,261 | 2,826 | 0,159668 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 60m | Gepoold gewicht1/k | 2,054 | -0,040 | 0,034 | -0,003 | -4,357 | 4,298 | 2,057 | 0,331055 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 60m | Eerste record per dag | 3,912 | -0,020 | 0,045 | -0,055 | -5,841 | 5,725 | 3,967 | 0,169922 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | rth_close | Ieder event gelijk | 0,633 | -0,218 | 0,065 | -0,287 | -8,382 | 8,000 | 0,920 | 0,838867 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | rth_close | Iedere eventdag gelijk | -33,157 | -36,852 | 0,062 | -36,802 | -44,856 | -29,259 | 3,645 | 0,347656 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | rth_close | Gepoold gewicht1/k | 2,222 | -0,155 | 0,071 | -0,193 | -8,922 | 8,763 | 2,415 | 0,600098 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_HIGH | rth_close | Eerste record per dag | 2,275 | -0,109 | 0,080 | -0,102 | -10,039 | 10,028 | 2,377 | 0,648438 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 15m | Ieder event gelijk | 0,460 | 0,018 | 0,010 | 0,008 | -1,180 | 1,228 | 0,452 | 0,461426 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 15m | Iedere eventdag gelijk | 11,140 | 7,779 | 0,015 | 7,753 | 6,015 | 9,679 | 3,387 | 0,001465 | 0,102539 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 15m | Gepoold gewicht1/k | 0,990 | 0,022 | 0,015 | 0,021 | -1,868 | 1,910 | 0,969 | 0,308594 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 15m | Eerste record per dag | 2,109 | 0,035 | 0,024 | 0,026 | -2,929 | 2,920 | 2,083 | 0,177734 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 60m | Ieder event gelijk | -0,793 | 0,075 | 0,027 | 0,098 | -3,261 | 3,312 | -0,891 | 0,590820 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 60m | Iedere eventdag gelijk | 22,545 | 20,244 | 0,032 | 20,198 | 16,339 | 24,471 | 2,347 | 0,264648 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 60m | Gepoold gewicht1/k | 0,510 | 0,063 | 0,034 | 0,083 | -4,309 | 4,472 | 0,426 | 0,849609 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | 60m | Eerste record per dag | 2,973 | 0,049 | 0,045 | 0,040 | -5,553 | 5,671 | 2,934 | 0,314453 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | rth_close | Ieder event gelijk | -1,348 | 0,088 | 0,066 | 0,058 | -8,107 | 8,247 | -1,406 | 0,735840 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | rth_close | Iedere eventdag gelijk | 37,357 | 36,753 | 0,061 | 36,670 | 29,301 | 44,749 | 0,687 | 0,868164 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | rth_close | Gepoold gewicht1/k | -0,825 | 0,033 | 0,072 | -0,038 | -8,896 | 8,804 | -0,787 | 0,862305 | 1,000000 |
| Gaussian met klok- en dagschaal | RECORD_LOW | rth_close | Eerste record per dag | 1,885 | -0,020 | 0,080 | -0,004 | -10,041 | 9,978 | 1,889 | 0,696777 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 15m | Ieder event gelijk | 0,352 | -0,021 | 0,011 | -0,027 | -1,369 | 1,365 | 0,378 | 0,583008 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 15m | Iedere eventdag gelijk | -7,323 | -8,508 | 0,016 | -8,501 | -10,489 | -6,592 | 1,177 | 0,227539 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 15m | Gepoold gewicht1/k | 1,483 | -0,018 | 0,016 | -0,016 | -1,981 | 1,977 | 1,499 | 0,135742 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 15m | Eerste record per dag | 1,882 | -0,011 | 0,024 | -0,013 | -3,030 | 3,089 | 1,895 | 0,226074 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 60m | Ieder event gelijk | -0,032 | -0,066 | 0,030 | -0,083 | -3,729 | 3,853 | 0,050 | 0,981934 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 60m | Iedere eventdag gelijk | -17,348 | -20,247 | 0,033 | -20,230 | -24,318 | -16,250 | 2,882 | 0,167480 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 60m | Gepoold gewicht1/k | 2,054 | -0,001 | 0,036 | -0,031 | -4,525 | 4,607 | 2,085 | 0,389648 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | 60m | Eerste record per dag | 3,912 | 0,059 | 0,046 | 0,090 | -5,658 | 5,836 | 3,822 | 0,192871 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | rth_close | Ieder event gelijk | 0,633 | -0,192 | 0,073 | -0,250 | -9,116 | 9,311 | 0,883 | 0,855957 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | rth_close | Iedere eventdag gelijk | -33,157 | -35,720 | 0,061 | -35,690 | -43,561 | -27,978 | 2,533 | 0,512695 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | rth_close | Gepoold gewicht1/k | 2,222 | -0,113 | 0,075 | -0,199 | -9,351 | 9,479 | 2,422 | 0,622070 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_HIGH | rth_close | Eerste record per dag | 2,275 | -0,056 | 0,082 | -0,061 | -10,212 | 10,221 | 2,337 | 0,642090 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | 15m | Ieder event gelijk | 0,460 | 0,018 | 0,011 | 0,020 | -1,326 | 1,311 | 0,440 | 0,494141 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | 15m | Iedere eventdag gelijk | 11,140 | 8,494 | 0,015 | 8,488 | 6,612 | 10,438 | 2,653 | 0,009766 | 0,664062 |
| Spiegelingen echte barvormen | RECORD_LOW | 15m | Gepoold gewicht1/k | 0,990 | 0,004 | 0,015 | 0,004 | -1,906 | 1,893 | 0,986 | 0,314941 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | 15m | Eerste record per dag | 2,109 | -0,017 | 0,024 | 0,009 | -3,177 | 2,959 | 2,100 | 0,172363 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | 60m | Ieder event gelijk | -0,793 | 0,079 | 0,030 | 0,145 | -3,702 | 3,694 | -0,938 | 0,642578 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | 60m | Iedere eventdag gelijk | 22,545 | 20,281 | 0,032 | 20,265 | 16,316 | 24,355 | 2,281 | 0,269531 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | 60m | Gepoold gewicht1/k | 0,510 | 0,050 | 0,036 | 0,053 | -4,416 | 4,537 | 0,457 | 0,839355 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | 60m | Eerste record per dag | 2,973 | 0,014 | 0,046 | 0,068 | -5,687 | 5,663 | 2,905 | 0,304688 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | rth_close | Ieder event gelijk | -1,348 | 0,075 | 0,072 | 0,255 | -9,369 | 8,965 | -1,603 | 0,728516 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | rth_close | Iedere eventdag gelijk | 37,357 | 35,667 | 0,061 | 35,681 | 28,026 | 43,388 | 1,676 | 0,658203 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | rth_close | Gepoold gewicht1/k | -0,825 | 0,038 | 0,075 | 0,121 | -9,650 | 9,309 | -0,946 | 0,847168 | 1,000000 |
| Spiegelingen echte barvormen | RECORD_LOW | rth_close | Eerste record per dag | 1,885 | -0,016 | 0,081 | -0,000 | -10,289 | 10,265 | 1,885 | 0,713867 | 1,000000 |

Aantal modelcheck-vergelijkingen onder0,05 na Holm72: **1/72**. Een afwijking verwerpt hoogstens een aspect van dat specifieke nulmodel; zij valideert geen handelsregel. Niet-verwerpen bewijst omgekeerd niet dat NQ exact uit het nulmodel komt.

Volledige P05/P25/P50/P75/P95, null-eventaantallen en indicatieve Monte-Carlo-tailprecisie staan in JSON/CSV. Tailprecisie is onzekerheid door het eindige aantal simulaties, niet onzekerheid over de juistheid van het marktmodel.

### Expliciet: resultaten op de Monte-Carlo-resolutiegrens

| Nulmodel | Record | Horizon | Meetwijze | Kleinere tailcount | Ruwe p | Holm72 | Indicatieve95%-MC-tailprecisie (ruwe p) |
|---|---|---|---|---|---|---|---|
| Gaussian i.i.d. | RECORD_LOW | 15m | Iedere eventdag gelijk | 0 | 0,000488 | 0,035156 | [0,000000; 0,001874] |

Bij nul extremere trekkingen is de p-waarde begrensd door de vooraf gekozen simulatieresolutie. De tailprecisie is een indicatief, naar tweezijdig geschaald Wilsoninterval voor de kleinere gesimuleerde staart, geen exact gezamenlijk p-interval en geen zekerheid over het overschrijden van de Holm-grens. Er zijn geen extra trekkingen gedaan om een gewenste beslissing te krijgen.

## 5. Wat doet de oorspronkelijke nulwaardetoets op onvoorspelbare paden?

De eerste128 experimenten per scenario worden behandeld als afzonderlijke datasets. Elk krijgt dezelfde4.000 vijf-sessie bootstrapreplicaties als het vorige onderzoek. Twaalf recordtoetsen (twee sides×drie horizonten×twee meetwijzen) worden aangevuld met31 placeholders p=1, zodat de oorspronkelijke Holm43-familiegrootte behouden blijft. Dit is conservatief voor die niet-gesimuleerde toetsen; het reproduceert niet de gezamenlijke verdeling van alle oorspronkelijke43 markttoetsen.

**Dit heet bewust geen type-I-fout voor het daggemiddelde.** Onder een onvoorspelbaar koersproces kan het echte daggewogen gemiddelde niet-nul zijn. Een correcte toets op gemiddelde0 kan dan terecht verwerpen, terwijl de interpretatie “dus voorspelbare marktbeweging” onjuist is. We meten de frequentie van nulwaardeverwerpingen onder een generator zonder voorspelbaarheid.

| Nulmodel | Record | Horizon | Meetwijze | Panelen | Nominale verwerpingen | Fractie | 95%Wilson | Holm43 verwerpingen | Fractie | 95%Wilson |
|---|---|---|---|---|---|---|---|---|---|---|
| Gaussian i.i.d. | RECORD_HIGH | 15m | Ieder event gelijk | 128 | 7 | 0,055 | [0,027; 0,109] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian i.i.d. | RECORD_HIGH | 15m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian i.i.d. | RECORD_HIGH | 60m | Ieder event gelijk | 128 | 10 | 0,078 | [0,043; 0,138] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian i.i.d. | RECORD_HIGH | 60m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian i.i.d. | RECORD_HIGH | rth_close | Ieder event gelijk | 128 | 10 | 0,078 | [0,043; 0,138] | 1 | 0,008 | [0,001; 0,043] |
| Gaussian i.i.d. | RECORD_HIGH | rth_close | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian i.i.d. | RECORD_LOW | 15m | Ieder event gelijk | 128 | 8 | 0,062 | [0,032; 0,118] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian i.i.d. | RECORD_LOW | 15m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian i.i.d. | RECORD_LOW | 60m | Ieder event gelijk | 128 | 6 | 0,047 | [0,022; 0,098] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian i.i.d. | RECORD_LOW | 60m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian i.i.d. | RECORD_LOW | rth_close | Ieder event gelijk | 128 | 4 | 0,031 | [0,012; 0,078] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian i.i.d. | RECORD_LOW | rth_close | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 15m | Ieder event gelijk | 128 | 6 | 0,047 | [0,022; 0,098] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 15m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 60m | Ieder event gelijk | 128 | 5 | 0,039 | [0,017; 0,088] | 1 | 0,008 | [0,001; 0,043] |
| Gaussian met klok- en dagschaal | RECORD_HIGH | 60m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | RECORD_HIGH | rth_close | Ieder event gelijk | 128 | 9 | 0,070 | [0,037; 0,128] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian met klok- en dagschaal | RECORD_HIGH | rth_close | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | RECORD_LOW | 15m | Ieder event gelijk | 128 | 6 | 0,047 | [0,022; 0,098] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian met klok- en dagschaal | RECORD_LOW | 15m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | RECORD_LOW | 60m | Ieder event gelijk | 128 | 9 | 0,070 | [0,037; 0,128] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian met klok- en dagschaal | RECORD_LOW | 60m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | RECORD_LOW | rth_close | Ieder event gelijk | 128 | 8 | 0,062 | [0,032; 0,118] | 0 | 0,000 | [0,000; 0,029] |
| Gaussian met klok- en dagschaal | RECORD_LOW | rth_close | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | RECORD_HIGH | 15m | Ieder event gelijk | 128 | 3 | 0,023 | [0,008; 0,067] | 1 | 0,008 | [0,001; 0,043] |
| Spiegelingen echte barvormen | RECORD_HIGH | 15m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | RECORD_HIGH | 60m | Ieder event gelijk | 128 | 8 | 0,062 | [0,032; 0,118] | 0 | 0,000 | [0,000; 0,029] |
| Spiegelingen echte barvormen | RECORD_HIGH | 60m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | RECORD_HIGH | rth_close | Ieder event gelijk | 128 | 11 | 0,086 | [0,049; 0,147] | 1 | 0,008 | [0,001; 0,043] |
| Spiegelingen echte barvormen | RECORD_HIGH | rth_close | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | RECORD_LOW | 15m | Ieder event gelijk | 128 | 4 | 0,031 | [0,012; 0,078] | 0 | 0,000 | [0,000; 0,029] |
| Spiegelingen echte barvormen | RECORD_LOW | 15m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | RECORD_LOW | 60m | Ieder event gelijk | 128 | 7 | 0,055 | [0,027; 0,109] | 0 | 0,000 | [0,000; 0,029] |
| Spiegelingen echte barvormen | RECORD_LOW | 60m | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | RECORD_LOW | rth_close | Ieder event gelijk | 128 | 10 | 0,078 | [0,043; 0,138] | 0 | 0,000 | [0,000; 0,029] |
| Spiegelingen echte barvormen | RECORD_LOW | rth_close | Iedere eventdag gelijk | 128 | 128 | 1,000 | [0,971; 1,000] | 128 | 1,000 | [0,971; 1,000] |

Wilson-intervallen beschrijven de Monte-Carlo-onzekerheid over de gemeten fractie uit128 panelen; niet het onzekerheidsinterval van een NQ-effect.

### Panelen met minstens één record-verwerping

| Nulmodel | Procedure | Panelen met ≥1 | Totaal | Fractie | 95%Wilson |
|---|---|---|---|---|---|
| Gaussian i.i.d. | nominal | 128 | 128 | 1,000 | [0,971; 1,000] |
| Gaussian i.i.d. | holm43 | 128 | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | nominal | 128 | 128 | 1,000 | [0,971; 1,000] |
| Gaussian met klok- en dagschaal | holm43 | 128 | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | nominal | 128 | 128 | 1,000 | [0,971; 1,000] |
| Spiegelingen echte barvormen | holm43 | 128 | 128 | 1,000 | [0,971; 1,000] |

## 6. Wat mogen we hier wel en niet uit concluderen?

- Het verschil tussen event- en dagweging is exact aan de count/outcome-covariantie gekoppeld. Dat is een verandering van estimand, niet automatisch een programmeerfout.
- Het exacte muntworpvoorbeeld toont dat een niet-nul daggewogen recordeffect kan bestaan zonder voorspelbare toekomstige log-rendementen.
- De nulscenario’s kwantificeren hoe groot dat verschijnsel binnen elk vooraf vastgelegd model kan worden. Zij identificeren geen universeel causaal percentage van een NQ-effect.
- Een block-bootstrap bewaart afhankelijkheid binnen dagen; hij verwijdert geen toekomstafhankelijkheid uit een eindedagsgewicht. Holm corrigeert multipliciteit, niet een verkeerd geïnterpreteerde onderzoeksvraag.
- De meetcontroles1/k en eerste record zijn geen nieuwe handelsvoorstellen. Geen kosten, brokerfills, uitvoerbaarheid of zelfstandige edge zijn getest.
- De oorspronkelijke tabellen blijven geldig als beschrijvende schattingen van hun expliciet gedefinieerde gemiddelden. De significante daggemiddelden mogen niet als bewijs van een vooraf uitvoerbare mean-reversion-edge worden gelezen.
- Alle435 dagen zijn al verbruikt. Deze audit levert geen nieuwe out-of-sample validatie op en heropent geen van de vier gearchiveerde modellen.

## 7. Methodologische bronnen en reikwijdte

Het algemene onderscheid tussen een gemiddelde over waarnemingen en een gemiddelde over clusters, wanneer clustergrootte met uitkomsten samenhangt, is behandeld door [Kahan et al., Estimands in cluster-randomized trials](https://academic.oup.com/ije/article/52/1/107/6644521). Die studie betreft klinische trials; de toepassing op eventdagen en de martingaalcontrole hierboven zijn eigen berekeningen, geen claim van die auteurs over NQ.

Voor eindige randomisatie-/Monte-Carlo-p-waarden en het vermijden van exact nul: [Phipson & Smyth](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf). De+1-regel maakt een verkeerd gespecificeerd of achteraf gekalibreerd nulmodel niet automatisch exact geldig.

## 8. Reproductie en bewijsbestanden

- Methode, code en inputhashes: `research/weighting-audit-lock.json`; definities: `research/weighting-audit-protocol.json`.
- Uitvoering: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m scripts.weighting_audit`.
- Afgeronde batch wordt niet overschreven. Alleen volledig afgeronde scenario-checkpoints met dezelfde methode-/codehash worden bij een onderbreking hergebruikt.
- Verificatie zonder nieuwe simulaties of strategieën: `.venv/bin/python -B -m scripts.weighting_audit --verify`.
- Publicatietabellen opnieuw opbouwen: `.venv/bin/python -B -m scripts.publish_weighting_audit`.
- Tests: `.venv/bin/python -m pytest -q`; dashboard: `npm run typecheck` en `npm run build`.
- De volledige experimentarrays en reële eventregels blijven privé. Alleen geaggregeerde verdelingen en controlegetallen worden gepubliceerd.

Definities SHA-256: `028151863460a6b995371c3ef73902a098906268b6f42a8d80f69cf58d1eb806`.
Methode-/inputslot SHA-256: `7476f40d0d6ebe968b38727f74c040ddb141e8b694cf8bdc40bbce30b8ab6d42`.
Runtime: Python3.14.3, NumPy2.5.4, pandas3.0.6. Alle115 beschermde experimentbestanden ongewijzigd.
