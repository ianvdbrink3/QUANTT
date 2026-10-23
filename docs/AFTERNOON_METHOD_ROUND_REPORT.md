# Methoderonde en vastlegging van het testvenster

22 oktober 2026. Alleen stappen 1 en 2 uitgevoerd. Geen nieuwe marktuitkomsten, cohortselectie, backtest, downloads, aankoop, GitHub-push of Vercel-publicatie. Baseline v0.9, vNext, kandidaat v2 en eerdere rapporten zijn ongewijzigd.

## Besluit

**CALIBRATION_FAILED_NO_METHOD_SWITCH**. De vooraf gekozen alternatieve meetlat haalt de vastgelegde vrijgave-eis niet. Stap 1 is als methoderonde uitgevoerd, maar het onderliggende betrouwbaarheidsprobleem is **niet opgelost**. Er is geen vervangende methode goedgekeurd of als actuele kandidaat ingesteld.

Het venster **2019-01-02 t/m 2021-12-31** en de bronacquisitie zijn vóór inzage van marktuitkomsten vergrendeld. Dit is historische replicatie, geen bewezen volledig onaangeraakte forwardproef. De lijst bevat **103 CSV’s / 14 contracten**, inclusief opwarming. **Nog niet de hele lijst verzamelen en geen eindtoets draaien** zolang de meetlat niet is vrijgegeven.

## 1. Wat vóór de simulatie vastlag

- Eén alternatieve methode: acht even lange chronologische kalenderblokken met telkens twintig weekdagposities tussenruimte. Geen zoektocht over laglengtes, groepen, gaps, rendementen of strategieparameters.
- Twee tweezijdige horizons, dezelfde selectie en kosten, dezelfde Holm2-familie met alpha 0,05. Geen primaire/secundaire inhoudelijke gate. De nieuwe steekproefpartitionering is een expliciet voorstel voor een afzonderlijk inferentie-addendum, geen stille wijziging van v2.
- Per blok de nulmoment-score A=sum(I×netto punten)/bloklengte. Niet-geselecteerde kalenderposities leveren een nul aan de invloedsscore, geen verzonnen geselecteerde nultrade. De getoonde conditionele gemiddelde punten blijven sum(I×netto punten)/sum(I), niet een achteraf dag- of blokgewogen gemiddelde.
- De p-waarde gebruikt t op de acht nulmoment-scores, met zeven vrijheidsgraden. De intervalfunctie inverteert de scoretoets via A−mu×B en geeft onbegrensde/disjuncte sets als zodanig terug. Geen kunstmatig eindige intervallen.
- Minstens acht geselecteerde dagen per blok en 120 totaal. Onvoldoende informatie geeft beide p-waarden 1 en DATA_INSUFFICIENT; kalender niet comprimeren of verlengen.
- Elf nulmodellen: iid normaal, t5, positieve/negatieve scheefheid, MA(19), AR(0,6/0,9/0,95), volatiliteitsregimes, persistente selectie en MA(19) met persistente selectie. Daarnaast één expliciete niet-mengende negatieve controle buiten de geldigheidsaannamen.
- Twee vooraf gekozen seeds, 10.000 panels per model/kalenderlengte/seed. Drie lengtes: 500, 783 en 1.000 weekdagposities. Gezamenlijke nul én twee deel-nullen: een horizon met +4 hypothetische netto punten, de andere werkelijk nul.
- Alle echte-nulverwerpingen tellen mee, beide tekens. Zowel onvoorwaardelijk als onder panels die de informatiepoort halen. Gelijktijdige eenzijdige Clopper–Pearson-bovengrenzen over alle 396 toetscellen: totale Monte-Carlo-foutkans 0,05 via Bonferroni. Elke bovengrens moest hoogstens 6% zijn. Die 6% was een vooraf vastgelegde numerieke screentolerantie, géén wijziging van de nominale alpha van 5%.

Protocol en implementatie zijn vóór de eerste simulatie gehasht. Totaal **720,000 synthetische panels**. Invoer: uitsluitend al bestaande samenvattingsgetallen voor selectiefrequentie, SD en correlatie; geen ruwe CSV of nieuwe eventledger numeriek gelezen. Een tweede seed is een afzonderlijke Monte-Carlo-controle, niet een externe onafhankelijke onderzoeker of een byte-identieke volledige reproductierun.

De methode is geïnspireerd door [Ibragimov en Müller (2010)](https://www.princeton.edu/~umueller/tstat.pdf). Hun groepsbenadering vereist voldoende onafhankelijke, ongeveer Gaussische groepsinformatie. Dat vereist aannamen over de gegevens; twintig dagen tussenruimte bewijzen die onafhankelijkheid niet. De hier gebruikte nulmoment-implementatie is een eigen toepassing, geen universele eindige-steekproefgarantie uit het artikel.

## 2. Resultaat van de vooraf vastgelegde vrijgavepoort

**18 van de 396 bovengrenzen overschrijden 6%.** Grootste bovengrens: **7.65%**. Dat is een onzekerheidsbovengrens, niet de gemeten foutkans zelf. Sommige afwijzingen van de screeneis komen ook door onvoldoende Monte-Carlo-precisie in de kleine evaluabele subgroep, niet alleen door een verhoogde puntschatting.

| Seedfase | Model | Kalender | Nulscenario | Populatie panels | Gemeten fout % | Gelijktijdige bovenkant % |
|---|---|---:|---|---|---:|---:|
| 1 | AR095 | 500 | BOTH_ZERO | evaluable_only (8273/10000 evaluabel) | 6.60 | 7.65 |
| 2 | AR095 | 500 | BOTH_ZERO | evaluable_only (8306/10000 evaluabel) | 6.53 | 7.57 |
| 2 | PERSISTENT_SELECTION | 500 | BOTH_ZERO | evaluable_only (1648/10000 evaluabel) | 4.85 | 7.08 |
| 2 | PERSISTENT_SELECTION | 500 | 2M_PLUS4_15M_ZERO | evaluable_only (1648/10000 evaluabel) | 4.67 | 6.87 |
| 1 | AR095 | 1000 | BOTH_ZERO | unconditional (10000/10000 evaluabel) | 5.79 | 6.69 |
| 1 | AR095 | 1000 | BOTH_ZERO | evaluable_only (10000/10000 evaluabel) | 5.79 | 6.69 |
| 1 | AR095 | 783 | BOTH_ZERO | unconditional (10000/10000 evaluabel) | 5.60 | 6.49 |
| 1 | AR095 | 783 | BOTH_ZERO | evaluable_only (10000/10000 evaluabel) | 5.60 | 6.49 |
| 2 | AR095 | 783 | BOTH_ZERO | unconditional (10000/10000 evaluabel) | 5.49 | 6.37 |
| 2 | AR095 | 783 | BOTH_ZERO | evaluable_only (10000/10000 evaluabel) | 5.49 | 6.37 |
| 1 | AR095 | 500 | BOTH_ZERO | unconditional (8273/10000 evaluabel) | 5.46 | 6.34 |
| 2 | AR095 | 500 | BOTH_ZERO | unconditional (8306/10000 evaluabel) | 5.42 | 6.30 |

Ook de vooraf gekozen lengte van 783 weekdagposities haalt de eis niet. Daarom wordt niet achteraf de falende 500-dagencontrole weggelaten, een langere gap gekozen of de tolerantie verruimd. Het resultaat bewijst niet dat iedere bloktoets fout is of dat de marktobservatie afwezig is. Het bewijst dat dit concrete voorstel onder de vooraf gekozen meetlat niet is goedgekeurd.

### Vergelijking bij het geplande driejaarsvenster

Hieronder de gezamenlijke nul, onvoorwaardelijke familieverwerping in enige richting. Beide seeds staan apart. De oude HAC5 staat alleen als referentie op precies dezelfde gescoorde kalender, niet als gunstiger alternatief om te kiezen.

| Model | Fase 1: nieuw % | Fase 2: nieuw % | Fase 1: HAC5 % | Fase 2: HAC5 % |
|---|---:|---:|---:|---:|
| GAUSSIAN_IID | 4.46 | 4.62 | 4.53 | 4.76 |
| T5_IID | 4.69 | 4.56 | 4.81 | 4.79 |
| NEGATIVE_SKEW_IID | 4.77 | 4.59 | 5.25 | 4.86 |
| POSITIVE_SKEW_IID | 4.62 | 4.52 | 5.16 | 5.24 |
| MA19 | 4.44 | 4.50 | 32.29 | 33.05 |
| AR06 | 4.92 | 4.50 | 9.16 | 8.15 |
| AR09 | 4.52 | 4.77 | 32.28 | 31.10 |
| AR095 | 5.60 | 5.49 | 50.27 | 50.31 |
| VOLATILITY_REGIMES | 4.32 | 4.58 | 4.49 | 4.50 |
| PERSISTENT_SELECTION | 3.28 | 3.60 | 3.89 | 3.79 |
| MA19_PERSISTENT_SELECTION | 2.79 | 2.99 | 21.79 | 22.67 |

### Waarom de AR-stresstest nog restafhankelijkheid heeft

Voor het vooraf gekozen Gaussische AR(0,95)-model is de populatiecovariantie van de vaste scoreblokken analytisch uit te rekenen. Dit is geen geschatte NQ-autocorrelatie. De twintig-dagen-gap maakt naburige blokken hier niet onafhankelijk.

| Kalender | Bloklengte | Correlatie naburige scores | Ware variantie / verwachte groeps-SE² |
|---:|---:|---:|---:|
| 500 | 45 | 0.0959 | 1.2029 |
| 783 | 80 | 0.0524 | 1.1066 |
| 1000 | 107 | 0.0374 | 1.0757 |

Deze verhouding is geen exacte verklaring van de eindige t-verwerpingskans of de selectie-informatiepoort. Ze toont wel een concrete onderschattingsroute in het model. Geen nieuwe gap of groepsaantal is op dit resultaat uitgeprobeerd.

### Negatieve controle: gedeelde factor over het hele panel

| Kalender | Fase 1: fout % | Fase 2: fout % |
|---:|---:|---:|
| 500 | 81.47 | 81.48 |
| 783 | 99.33 | 99.35 |
| 1000 | 99.41 | 99.48 |

Deze expliciet niet-mengende controle valt buiten de aannamen. Ze laat zien waarom een geslaagde beperkte simulatiesuite nooit universele bescherming tegen elke gezamenlijke marktfactor zou bewijzen.

## 3. Power: alleen hypothetische planning

Alle onderstaande effecten zijn al netto na het bevroren kostenmodel. De p-waarden zijn niet op nieuwe marktgegevens berekend. Omdat de kalibratie faalt, zijn dit slechts simulatie-uitkomsten van het afgekeurde voorstel, geen gecertificeerde onderscheidingskansen.

| Nulruismodel | SD-factor | Effect 2m | Effect 15m | Positief familiesucces % |
|---|---:|---:|---:|---:|
| GAUSSIAN_IID | 1.0 | 4 | 0 | 90.61 |
| GAUSSIAN_IID | 1.5 | 4 | 0 | 56.54 |
| GAUSSIAN_IID | 1.0 | 0 | 4 | 20.13 |
| GAUSSIAN_IID | 1.5 | 0 | 4 | 10.08 |
| GAUSSIAN_IID | 1.0 | 4 | 4 | 90.62 |
| GAUSSIAN_IID | 1.5 | 4 | 4 | 57.38 |
| MA19 | 1.0 | 4 | 0 | 19.42 |
| MA19 | 1.5 | 4 | 0 | 9.78 |
| MA19 | 1.0 | 0 | 4 | 5.04 |
| MA19 | 1.5 | 0 | 4 | 3.75 |
| MA19 | 1.0 | 4 | 4 | 20.84 |
| MA19 | 1.5 | 4 | 4 | 10.94 |
| AR095 | 1.0 | 4 | 0 | 14.26 |
| AR095 | 1.5 | 4 | 0 | 8.10 |
| AR095 | 1.0 | 0 | 4 | 4.96 |
| AR095 | 1.5 | 0 | 4 | 3.95 |
| AR095 | 1.0 | 4 | 4 | 15.46 |
| AR095 | 1.5 | 4 | 4 | 8.92 |

Alle +2/+4/+6-scenario’s, beide SD-factoren, nullen, deel-nullen en evaluabele fracties staan onverkort in JSON. Een driejaarskalender geeft niet onder elke afhankelijkheid 80% power. Er is geen venster verlengd om een mooier powergetal te halen.

## 4. Wat nu wel vaststaat en welke bestanden nodig zijn

- Vast historisch venster: **2 januari 2019–31 december 2021**, alleen voor een later afzonderlijk vrijgegeven replicatie. Opwarming **19 november 2018–1 januari 2019**. Geen overlap met de 435 ontdekkingsdagen of de NQH24-pilot.
- Eerdere aangetroffen intradaylabels beginnen pas in 2022; de eerdere minuutreeks eind-2022. Dag/week/maanddata van oudere jaren waren al bekeken. Daarom geen claim van absoluut nul eerdere inzage of prospectieve onafhankelijkheid. Bron-/toegangscontrole blijft een vrijgavevoorwaarde.
- 783 weekdagposities zijn geen 783 CME-sessies of eligible dagen. De nieuwe kandidaatmeetlat zou 640 weekdagposities scoren en 143 als tussenruimte/staart reserveren. Echte kwaliteits- en eventaantallen zijn nog onbekend.
- Bronacquisitie: **103 onbewerkte 1m-contractexports**, over **14 contracten**. De volledige lijst staat in [NQ_HISTORICAL_DOWNLOAD_LIST.md](NQ_HISTORICAL_DOWNLOAD_LIST.md). Geen Nearby, geen back-adjusted export, geen total-volume-aggregatie. Zondagen zijn bewust in de blokken opgenomen.
- Contracten: NQZ18 (opwarming); NQH19/M19/U19/Z19; NQH20/M20/U20/Z20; NQH21/M21/U21/Z21; NQH22 uitsluitend voor de december-2021-rollover tot 31 december 2021.
- **Mijn huidige advies: nog geen bulkdownload.** De lijst is een vastgelegde latere behoefte, geen verzoek om nu 103 downloads af te werken. Er is in deze ronde geen goedgekeurde nieuwe meetlat ontstaan.
- Geen nieuwe strategie, filters, stop/target, order, betaalde bron, accountwijziging of automatische verlenging. De empirische uitvoerbaarheid blijft onbewezen.

## Verificatie en reproduceerbaarheid

`python -m scripts.afternoon_inference_round prepare` heeft de methodestand vóór simulatie vergrendeld. `python -m scripts.afternoon_inference_round run` reproduceert uitsluitend de synthetische ronde. `python -m scripts.register_historical_replication_window --verify` controleert de datum-/downloadlock. Geen van deze opdrachten voert de nieuwe markthypothese uit.

407 bestaande bestanden blijven byte-identiek ten opzichte van de vóór deze ronde vastgelegde hashes. Nieuwe bestanden staan alleen lokaal; de huidige kandidaatpointer blijft v2 en `independent_test_released=false`. De test-/eindverificatie staat in `research/afternoon-method-round-verification.json`.
