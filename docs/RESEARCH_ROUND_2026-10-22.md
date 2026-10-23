# Onderzoeksronde 22 oktober 2026

De voorbereidende controle is uitgevoerd én er zijn daadwerkelijk twee nieuwe, vaste backtests gestart en afgerond. Alles hieronder is lokaal. Geen aankoop, extra download, GitHub-push, dashboardwijziging of Vercel-uitrol uitgevoerd.

## 1. Nieuwe kandidaten: beide uitkomsten behouden

Regels, kosten, periode en benchmarks zijn vóór de eerste berekening gehasht. Dit is een vastgelegde verkennende ronde op de reeds verbruikte dataset, geen onafhankelijke preregistratie of holdout. Geen optimalisatielus, nieuwe filters, stops, targets of achteraf omgekeerde signalen. Geen hergebruik van de vier gearchiveerde basisschermen of van de gesloten ochtendherstel-verkenning.

| Vast model | Trades | Netto NQ-punten | Netto USD, één NQ | Winrate | Profit factor | Max gesloten-equity DD, pt |
|---|---:|---:|---:|---:|---:|---:|
| Ochtendrichting → slot-halfuur | 417 | −71,325 | −1.426,50 | 48,68% | 0,992 | 2.064,55 |
| Maandwisseling, alleen RTH long | 81 | +4.364,025 | +87.280,50 | 64,20% | 1,706 | 1.307,075 |

Beide resultaten zijn na 1,225 punt / $24,50 roundtripkosten. Dit zijn historische modelberekeningen, geen gerealiseerde of verwachte rekeningopbrengsten. Er is geen position-sizingmodel, intraday risicolimiet of onafhankelijk bewijs van de open-/closefills. Gesloten-equitydrawdown onderschat het mogelijke intratraderisico.

### Wat de regels precies doen

- **Ochtendrichting → slot:** teken van de beweging vanaf de vorige complete RTH-close tot 09:59 close. De vorige close is uitsluitend met vooraf bekende rollover-informatie naar het actieve contract vertaald. Signaal bekend om 10:00; entry 15:30 open, exit 15:59 close, long of short. Benchmark: altijd long op precies dezelfde dagen en in hetzelfde halfuur.
- **Maandwisseling:** long van 09:30 open tot 15:59 close op de laatste cash-beursdag van de maand en de eerste drie cash-beursdagen. Alleen volledige maanden januari 2025–september 2026. Kalenderposities tellen ook korte beursdagen; een ontbrekende/korte kwaliteitsdag wordt niet door een andere datum vervangen. Benchmark: overige volledige dagen binnen dezelfde maand, gestandaardiseerd naar het aantal maandwisseldagen.

De eerste kandidaat is geïnspireerd door de overnight-inclusieve definitie in [Gao e.a.](https://smallake.kr/wp-content/uploads/2015/01/SSRN-id2440866.pdf). De tweede volgt het vierdaagse kalendervenster van [McConnell en Xu](https://docs.lib.purdue.edu/ciberwp/43/), maar is uitdrukkelijk een RTH-only NQ-aanpassing van hun dagelijkse aandelenonderzoek. De literatuur bewijst deze NQ-resultaten niet en verklaart de oorzaak niet zelfstandig.

### Benchmark en onzekerheid

| Model | Gemiddeld netto pt/trade | Benchmark pt | Verschil pt | Nominaal 95%-interval verschil | Nominaal 95%-interval eigen gemiddelde |
|---|---:|---:|---:|---|---|
| Ochtendrichting → slot | −0,17 | +0,58 | −0,75 | [−12,87; +10,53] | [−6,85; +6,78] |
| Maandwisseling | +53,88 | −7,41 | +61,29 | [+1,51; +129,71] | [−0,11; +111,69] |

5.000 vooraf vastgelegde resamples van hele kalendermaanden; 22 maandclusters voor de ochtendregel en 21 voor maandwisseling. Dit zijn nominale, niet simultaan gecorrigeerde intervallen op ontdekkingsdata. Er zijn twee modelclaims en twee benchmarkclaims mogelijk. Geen confirmatoire p-waarde, geen `HOLDOUT_PASSED`, geen universele dekkingsgarantie. Het positieve benchmarkverschil mag niet worden verwisseld met bewezen positieve nettoverwachting: het interval van de eigen nettotrade bevat nul.

### Kwartaalstabiliteit in netto punten

| Kwartaal | Ochtendrichting → slot | Maandwisseling |
|---|---:|---:|
| 2024 Q4, slechts twee kalenderdagen | −89,975 | vooraf uitgesloten |
| 2025 Q1 | −12,075 | +814,550 |
| 2025 Q2 | −928,250 | +1.225,800 |
| 2025 Q3 | +300,525 | −254,975 |
| 2025 Q4 | −303,500 | −59,725 |
| 2026 Q1 | −480,075 | +437,025 |
| 2026 Q2 | +913,725 | +1.759,550 |
| 2026 Q3 | +528,300 | +441,800 |

Maandwisseling: 12 van 21 maanden en 5 van 7 kwartalen positief. De drie beste trades leveren 37,81% van de totale nettowinst. Grootste verliesdag −583,975 punten / −$11.679,50. Mediane MAE 102,25 punten; P75 234,75 en P90 364 punten. Max gesloten-equitydrawdown circa $26.141,50. Bij twee extra ticks per kant bovenop de basiskosten resteert +4.283,025 punten, gemiddeld +52,88 punten. Dit is uitsluitend een frictiescenario, geen bewijs dat werkelijk zulke fills haalbaar waren.

**Beoordeling:** de ochtend-naar-slot-regel ondersteunt geen voordeel na kosten en wordt in deze ronde niet gered met extra voorwaarden. Maandwisseling blijft één interessante verkennende kandidaat, niet een gevalideerd winstmodel. Geen uitbreiding of selectie van maanddagen na deze inzage. Vóór een onafhankelijke toets moeten regels en beoordelingscriteria voor die afzonderlijke kandidaat vastliggen. Het al voor 15:00 gereserveerde historische venster wordt hiervoor niet stil opnieuw gebruikt.

## 2. Meetlat: foutdiagnose en één conservatief vervolg

De oude mislukte methoderonde blijft ongewijzigd. Van de 18 toen falende simultane Monte-Carlo-bovengrenzen hebben twee ook een simultane ondergrens boven de nominale 5%; de overige zestien bewijzen op zichzelf geen verhoogde werkelijke foutkans. Daarnaast toont de analytische AR(0,95)-controle concrete restafhankelijkheid: ware variantie / verwachte groeps-SE² tot 1,2029.

Eén nieuw voorstel is vóór verse seeds vastgelegd: dezelfde acht blokken, twintig-weekdag-gaps, informatiepoort en Holm2, met vaste variantievermenigvuldiger 1,25. Dat is SE × sqrt(1,25), geen wijziging van marktregels, kosten, horizons of alpha. De marge is modelgemotiveerd, geen stelling voor willekeurige afhankelijkheid.

Resultaat: **720.000 nieuwe synthetische panels; 0 van 396 gelijktijdige bovengrenzen boven 6%; maximum 5,26%.** De 6% blijft een numerieke screentolerantie, niet een nieuwe nominale alpha. De niet-mengende gemeenschappelijke-factorcontrole blijft buiten de aannamen en wordt zichtbaar gehouden. Power daalt: bij +4 netto punten uitsluitend op de 2-minutenhorizon, 783 weekdagposities en iid-ruis van ontdekkingsschaal van 89,79% naar 83,46%; bij sterke AR(0,95)-afhankelijkheid van 13,59% naar 9,55%.

Status: `CALIBRATION_SCREEN_PASSED_LIMITED_SCOPE_NOT_MARKET_VALIDATION`. Kandidaat v2 en de actieve methodereferentie zijn niet vervangen. Een expliciet inferentie-addendum is nodig vóór gebruik in een onafhankelijke markttest. De nieuwe kandidaatbacktests lenen geen formele certificering van deze andere tweehorizonsimulatie.

## 3. Zes historische bestanden: kwaliteit, geen uitkomstentest

Alle **64.622 bronbars** slagen voor schema/footer, eindige coherente OHLCV, 0,25-puntticks en positief geheel vendorvolume. Hashes behouden; geen 20.000-regelafkapping of overlapduplicaten binnen contracten.

- NQZ18: 21 volledige standaard-RTH-dagen, geen ontbrekende RTH-minuten op die standaarddagen.
- NQH19: 18 volledige standaard-RTH-dagen. Acht vroege, nog niet actieve dagen missen 177, 69, 71, 58, 7, 3, 2 en 1 RTH-minuten. Niet voorwaarts gevuld of als compleet voorgesteld.
- Volume-switch vastgesteld op de voltooide sessie 14 december 2018; activatie 17 december. Oude/nieuwe vendorvolumes 297.045 / 431.734. De causale pre-roll spread is 22,75 punten; toekomst-afknipcontrole geslaagd.
- De bestaande doorlopende ATR-module maakt **8 van 8** aanwezige complete RTH-dagen van 2–11 januari 2019 technisch ATR14-ready. Contract-only opwarming zou onnodig dagen missen. Geen UP-cohort of uitkomsten berekend.
- CME-rouwsluiting op 5 december en expiratie op 21 december zijn apart behandeld. De kalender is niet volledig exchange-gecertificeerd: met name de exacte 23-november-early-close blijft voorlopige reconstructie. Deze uitzonderingsdag is niet trade-eligible verklaard. Geen empirische DST-overgang in deze batch; alleen synthetische IANA-conversietests.

De volledige historische reeks is nog niet binnen. Geen uitspraak over het aantal uiteindelijke events of strategierendementen. Vendorvolume, licentie en fills zijn niet onafhankelijk gevalideerd. De spreadsheet-richtlijnen zijn gebruikt voor bronbehoud, expliciete hiaten en afzonderlijke kwaliteitsuitvoer; ruwe CSV’s zijn niet herschreven.

## 4. Verificatie en opslag

- Volledige suite op deze stand: **491 tests geslaagd**, waaronder 17 nieuwe tests voor de conservatieve toets, informatiepoort, causale signaalprefix, barankers, cashkalender, kosten, DST, kwaliteitsuitvoer en hashes.
- Tweede afzonderlijke run vanaf **69 bron-CSV’s**: resultaten, benchmark-/tradeledgers en modelrapport byte-identiek. Dit is een bronherlaad-reproductie op dezelfde machine/code, niet een onafhankelijk geschreven tweede engine. Een runtimecontrole blokkeert de historische 2019–2021-bronnen in deze runner.
- De 73 bevroren onderzoeksbestanden zijn byte-identiek; kandidaat v2, v1-archief en 115 beschermde kandidaat-archiefbestanden gecontroleerd. De 400 eerder gevolgde repositorybestanden zijn door de oude methodeslotcontrole behouden.
- Private ledgers: `artifacts/new-candidates-round01/`, Gitignored. Aggregate rapporten en registers: `docs/` en `research/`. Alles staat daadwerkelijk lokaal op schijf; niets is gepubliceerd.

Reproduceerbare opdrachten vanuit de projectmap:

```sh
.venv/bin/python -m scripts.afternoon_inference_round2 verify
.venv/bin/python -m scripts.afternoon_inference_round2 run
.venv/bin/python -m scripts.historical_batch01_quality
.venv/bin/python -m scripts.new_candidates_round01 verify
.venv/bin/python -m scripts.new_candidates_round01 run
.venv/bin/python -m scripts.verify_new_candidates_round01
.venv/bin/python -m pytest -q
```

De slotbestanden zijn al aangemaakt. Niet opnieuw initialiseren, parameters wijzigen of de historische kandidaatuitkomsten bekijken om een beter resultaat te zoeken.
