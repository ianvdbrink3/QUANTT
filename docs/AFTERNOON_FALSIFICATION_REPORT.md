# 15:00-falsificatie — vaste cohorten, minuutisolatie en integriteit

## Uitkomst

**INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED**. De positieve gemiddelde impuls verdwijnt niet bij cohortbevriezing om 14:30 en wisselt niet van teken na enige dag- of kwartaalweglating. De aantoonbare afwijking zit vooral in de eerste minuut: het restant is positief gemeten, maar niet overtuigend na de vooraf vastgelegde Holm-correctie. Geen gevalideerde edge of bewijs van uitvoerbaarheid.

Dit is uitsluitend een falsificatie op reeds gebruikte data, geen nieuwe holdout. Geen strategie, fills, kostenmodel, stops, targets of parameters zijn toegevoegd. Geen GitHub/Vercel-publicatie in deze ronde.

## Meetdefinities en onzekerheid

- Universum: dezelfde 435 volledige RTH-dagen; 69 geregistreerde bronbestanden. 17 dagen zonder vooraf bekende ATR blijven buiten UP/DOWN, maar binnen de integriteitscontrole.
- Vast: selectie uitsluitend met voltooide 14:29-bar, richting t.o.v. 09:30-open en opgebouwde range / vooraf bekende ATR14 in [0,5; 1,2). Dynamisch: identieke selectie opnieuw op elk meetmoment.
- FULL: close vóór start tot close van minuut start+14. Het venster 15:00–15:15 eindigt dus op de voltooide 15:14-bar, bekend om 15:15; niet op de close van de 15:15-bar.
- FIRST: open tot close van startminuut. REST: open start+1 tot close start+14. FULL omvat daarnaast beide close/open-prijsverschillen. Mediane componenten zijn niet optelbaar.
- UP is positief bij stijging; DOWN is positief bij daling. DOWN-cijfers zijn dus geen ruwe opwaartse prijsbeweging.
- Precies 24 tweezijdige toetsen, één Holm-familie. Primaire p-waarden op log-basispunten; dag-invloedscores met HAC(5), inclusief covariantie van overlappende cohorten, t-intervallen. Getoonde puntenintervallen zijn nominale 95%-intervallen, niet simultaan gecorrigeerd. CR1-sensitiviteits-SE staat in CSV/JSON.
- Deze correctie dekt alleen deze ronde, niet de eerdere projectbrede selectie. Niet-significant is geen bewijs dat het effect nul is. Point-in-time betekent geen geïdentificeerde institutionele oorzaak.

## 1. Vaste versus dynamische cohorten

| Cohort | Richting | Start | N | Gem. pt | Mediaan pt | Aandeel >0 |
| --- | --- | --- | --- | --- | --- | --- |
| fixed | UP | 14:30 | 162 | 0.8549 | 0.875 | 0.5309 |
| fixed | UP | 14:45 | 162 | -5.06 | -0.625 | 0.4938 |
| fixed | UP | 15:00 | 162 | 8.005 | 5.125 | 0.5802 |
| fixed | DOWN | 14:30 | 131 | 0.9179 | -0.5 | 0.4885 |
| fixed | DOWN | 14:45 | 131 | 5.956 | -1.25 | 0.4809 |
| fixed | DOWN | 15:00 | 131 | 4.485 | 2.75 | 0.5344 |
| dynamic | UP | 14:30 | 162 | 0.8549 | 0.875 | 0.5309 |
| dynamic | UP | 14:45 | 165 | -4.958 | -0.75 | 0.4909 |
| dynamic | UP | 15:00 | 167 | 7.54 | 4 | 0.5689 |
| dynamic | DOWN | 14:30 | 131 | 0.9179 | -0.5 | 0.4885 |
| dynamic | DOWN | 14:45 | 133 | 5.15 | -1 | 0.4812 |
| dynamic | DOWN | 15:00 | 131 | 3.666 | 2.5 | 0.5267 |

Van de oorspronkelijke +7,5404 pt blijft op het vaste UP-cohort +8,0046 pt over: +0,4642 pt verschil tussen twee verschillende groepen. Geen causale schatting van de invloed van selectie.

### Statusovergangen 14:30 → 15:00

| 14:30 | 15:00 | Dagen |
| --- | --- | --- |
| UP | UP | 155 |
| UP | DOWN | 6 |
| UP | OTHER | 1 |
| DOWN | UP | 7 |
| DOWN | DOWN | 121 |
| DOWN | OTHER | 3 |
| OTHER | UP | 5 |
| OTHER | DOWN | 4 |
| OTHER | OTHER | 133 |

26 dagen veranderen tussen de eindpunten van grove status (UP/DOWN/OTHER); 30 veranderen op minstens één van de drie kwartiermeetpunten. Van 162 vaste UP-dagen blijven 155 UP, gaan 6 naar DOWN en 1 boven de rangegrens; 12 nieuwe UP-dagen komen erbij. Van 131 vaste DOWN-dagen blijven 121 DOWN, gaan 7 naar UP en 3 boven de rangegrens; 10 nieuwe DOWN-dagen komen erbij. OTHER betekent geen bruikbare UP/DOWN-selectie, niet automatisch corrupte data.

## 2. Eerste minuut en resterende 14 minuten

| Cohort | Richting | Start | Deel | N | Gem. pt | Mediaan pt | Aandeel >0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed | UP | 14:30 | FIRST | 162 | 0.9444 | 1.5 | 0.5988 |
| fixed | UP | 14:30 | REST | 162 | -0.2052 | -0.75 | 0.4753 |
| fixed | UP | 14:45 | FIRST | 162 | -0.7284 | -0.375 | 0.4568 |
| fixed | UP | 14:45 | REST | 162 | -4.418 | 0.75 | 0.5185 |
| fixed | UP | 15:00 | FIRST | 162 | 3.491 | 2.625 | 0.6605 |
| fixed | UP | 15:00 | REST | 162 | 4.338 | 2 | 0.5432 |
| fixed | DOWN | 14:30 | FIRST | 131 | -0.04008 | 0 | 0.4885 |
| fixed | DOWN | 14:30 | REST | 131 | 1.048 | 3 | 0.5344 |
| fixed | DOWN | 14:45 | FIRST | 131 | 1.59 | 0 | 0.4962 |
| fixed | DOWN | 14:45 | REST | 131 | 4.475 | -1 | 0.4962 |
| fixed | DOWN | 15:00 | FIRST | 131 | -0.5744 | -0.75 | 0.4656 |
| fixed | DOWN | 15:00 | REST | 131 | 5.065 | 1.5 | 0.5496 |
| dynamic | UP | 14:30 | FIRST | 162 | 0.9444 | 1.5 | 0.5988 |
| dynamic | UP | 14:30 | REST | 162 | -0.2052 | -0.75 | 0.4753 |
| dynamic | UP | 14:45 | FIRST | 165 | -0.6152 | -0.5 | 0.4545 |
| dynamic | UP | 14:45 | REST | 165 | -4.439 | 0.75 | 0.5212 |
| dynamic | UP | 15:00 | FIRST | 167 | 3.455 | 2.75 | 0.6647 |
| dynamic | UP | 15:00 | REST | 167 | 3.937 | 1.25 | 0.5269 |
| dynamic | DOWN | 14:30 | FIRST | 131 | -0.04008 | 0 | 0.4885 |
| dynamic | DOWN | 14:30 | REST | 131 | 1.048 | 3 | 0.5344 |
| dynamic | DOWN | 14:45 | FIRST | 133 | 1.359 | 0.25 | 0.5038 |
| dynamic | DOWN | 14:45 | REST | 133 | 3.904 | -1 | 0.4962 |
| dynamic | DOWN | 15:00 | FIRST | 131 | -0.4179 | -0.25 | 0.4809 |
| dynamic | DOWN | 15:00 | REST | 131 | 4.101 | 1.5 | 0.542 |

### Alle vooraf vastgelegde toetsen

| Cohort | Richting | Deel | Vergelijking | Verschil pt | 95%-BI pt | p ruw (log-bp) | p Holm24 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed | UP | FIRST | 15:00 mean vs0 | 3.491 | [1.685; 5.297] | 0.0003359 | 0.007053 |
| fixed | UP | FIRST | 15:00 minus 14:30 | 2.546 | [0.283; 4.810] | 0.03537 | 0.6013 |
| fixed | UP | FIRST | 15:00 minus 14:45 | 4.219 | [2.074; 6.364] | 0.0002941 | 0.006765 |
| fixed | UP | REST | 15:00 mean vs0 | 4.338 | [-0.878; 9.553] | 0.07282 | 1 |
| fixed | UP | REST | 15:00 minus 14:30 | 4.543 | [-1.527; 10.613] | 0.1701 | 1 |
| fixed | UP | REST | 15:00 minus 14:45 | 8.756 | [1.862; 15.651] | 0.01369 | 0.2737 |
| fixed | DOWN | FIRST | 15:00 mean vs0 | -0.5744 | [-3.066; 1.917] | 0.5795 | 1 |
| fixed | DOWN | FIRST | 15:00 minus 14:30 | -0.5344 | [-3.774; 2.706] | 0.7202 | 1 |
| fixed | DOWN | FIRST | 15:00 minus 14:45 | -2.164 | [-5.713; 1.385] | 0.2392 | 1 |
| fixed | DOWN | REST | 15:00 mean vs0 | 5.065 | [-1.104; 11.234] | 0.08342 | 1 |
| fixed | DOWN | REST | 15:00 minus 14:30 | 4.017 | [-5.958; 13.993] | 0.3316 | 1 |
| fixed | DOWN | REST | 15:00 minus 14:45 | 0.5897 | [-9.252; 10.432] | 0.8434 | 1 |
| dynamic | UP | FIRST | 15:00 mean vs0 | 3.455 | [1.844; 5.066] | 5.922e-05 | 0.001421 |
| dynamic | UP | FIRST | 15:00 minus 14:30 | 2.511 | [0.456; 4.565] | 0.01989 | 0.378 |
| dynamic | UP | FIRST | 15:00 minus 14:45 | 4.07 | [1.965; 6.175] | 0.0003177 | 0.00699 |
| dynamic | UP | REST | 15:00 mean vs0 | 3.937 | [-0.498; 8.373] | 0.07433 | 1 |
| dynamic | UP | REST | 15:00 minus 14:30 | 4.142 | [-1.217; 9.502] | 0.196 | 1 |
| dynamic | UP | REST | 15:00 minus 14:45 | 8.377 | [1.316; 15.437] | 0.0206 | 0.378 |
| dynamic | DOWN | FIRST | 15:00 mean vs0 | -0.4179 | [-3.027; 2.191] | 0.7201 | 1 |
| dynamic | DOWN | FIRST | 15:00 minus 14:30 | -0.3779 | [-3.695; 2.939] | 0.8332 | 1 |
| dynamic | DOWN | FIRST | 15:00 minus 14:45 | -1.777 | [-5.443; 1.889] | 0.3441 | 1 |
| dynamic | DOWN | REST | 15:00 mean vs0 | 4.101 | [-2.268; 10.470] | 0.1997 | 1 |
| dynamic | DOWN | REST | 15:00 minus 14:30 | 3.053 | [-6.654; 12.761] | 0.4555 | 1 |
| dynamic | DOWN | REST | 15:00 minus 14:45 | 0.197 | [-9.574; 9.968] | 0.9587 | 1 |

UP FIRST is positief versus nul (vast Holm p=0,00705; dynamisch p=0,00142) en wijkt af van de eerste minuut om 14:45 (p=0,00676 / 0,00699), niet overtuigend van 14:30 (p=0,601 / 0,378). UP REST is gemiddeld +4,338 / +3,937 pt; de nulvergelijkingen hebben Holm p=1, en ook beide vergelijkingen met eerdere kwartieren blijven boven 0,05. Dit bewijst niet dat uitsluitend minuut 1 de beweging bevat: het meet wel waar in deze ronde het statistische bewijs overblijft.

De vaste UP-decompositie om 15:00 is 0,0833 + 3,4907 + 0,0926 + 4,3380 = 8,0046 pt. Dynamisch is dit 0,0734 + 3,4551 + 0,0749 + 3,9371 = 7,5404 pt. De eerste minuut zelf is circa 43,6% / 45,8% van het volledige gemiddelde; geen uitspraak over de eerste seconde mogelijk.

## 3. Concentratie en alle weglatingen

| Cohort | Orig. gem. | LODO min | LODO max | Min: dag eruit | Max: dag eruit | LOQO min | LOQO max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed | 8.005 | 7.135 | 8.769 | 2026-03-19 | 2026-03-02 | 5.081 | 10.13 |
| dynamic | 7.54 | 6.694 | 8.279 | 2026-03-19 | 2026-03-02 | 5.203 | 9.312 |

De minimumgemiddelden na dagweglating ontstaan zonder 19 maart 2026 (+148 pt); de maxima zonder 2 maart 2026 (−115 pt). Geen tekenomslag. Dit is richtingrobuustheid, geen bewijs van voldoende effectgrootte of significantie na weglating.

### Elke kwartaalweglating

| Cohort | Kwartaal eruit | N eruit | Gem. eruit pt | N over | Gem. over pt |
| --- | --- | --- | --- | --- | --- |
| fixed | 2025Q1 | 17 | 10.01 | 145 | 7.769 |
| fixed | 2025Q2 | 21 | 11.75 | 141 | 7.447 |
| fixed | 2025Q3 | 29 | -1.759 | 133 | 10.13 |
| fixed | 2025Q4 | 16 | 12.19 | 146 | 7.546 |
| fixed | 2026Q1 | 24 | 4.688 | 138 | 8.582 |
| fixed | 2026Q2 | 35 | 18.61 | 127 | 5.081 |
| fixed | 2026Q3 | 20 | -1.413 | 142 | 9.331 |
| dynamic | 2025Q1 | 19 | 13.78 | 148 | 6.74 |
| dynamic | 2025Q2 | 22 | 3.83 | 145 | 8.103 |
| dynamic | 2025Q3 | 27 | -1.648 | 140 | 9.312 |
| dynamic | 2025Q4 | 20 | 10.6 | 147 | 7.124 |
| dynamic | 2026Q1 | 25 | 3.71 | 142 | 8.215 |
| dynamic | 2026Q2 | 33 | 17.03 | 134 | 5.203 |
| dynamic | 2026Q3 | 21 | 4.333 | 146 | 8.002 |

Zonder 2026Q2 is het gemiddelde het laagst: +5,081 / +5,203 pt. Zonder 2025Q3 het hoogst: +10,133 / +9,313 pt. Afzonderlijke kwartalen hoeven niet positief te zijn: het vaste UP-cohort is in 2025Q3 én 2026Q3 gemiddeld negatief.

## 4. Bar-aansluiting en expliciete correctie

| Dagen | Verwacht | Aanwezig | Ontbrekend | Dubbel | Afgekeurde dagen |
| --- | --- | --- | --- | --- | --- |
| 435 | 1305 | 1305 | 0 | 0 | 0 |

| Overgang | Niet-nul dagen | Gem. pt | Mediaan | Min | Max |
| --- | --- | --- | --- | --- | --- |
| gap1500 | 352 | 0.05575 | 0 | -2 | 2.5 |
| gap1501 | 364 | 0.05862 | 0 | -2.75 | 4 |

Alle gecontroleerde bars hebben 60-secondenafstand, coherente OHLC op het 0,25-tickraster en één contract/handelsdatum per dag. Een close/open-prijsverschil is niet hetzelfde als een ontbrekende tijdstempel.

**Technisch erratum:** unit tests vonden vóór interpretatie van de nieuwe statistische tabellen een eenheidsfout in de eerste integriteitscontrole: microseconden werden vergeleken met een vaste nanosecondentelling. Daardoor werden onterecht alle 435 dagen gemarkeerd. De run was toen al afgerond. De originele code, uitvoer en hashes zijn behouden; een afzonderlijke timedelta-controle corrigeert uitsluitend de afstandstest naar 0 afgekeurde dagen. Alle overige auditkolommen zijn exact gelijk en geen statistische tabel of p-waarde is gewijzigd. De correctie is afzonderlijk gehasht en geregistreerd.

Dit sluit tijdstempelgaten in de gecontroleerde bron uit, maar geen systematische vendor-labelverschuiving. Onafhankelijke tweede-bronbevestiging en subminuut-/uitvoerbaarheidsbewijs ontbreken.

## Beslisboom en verificatie

1. Vast UP-gemiddelde ≤0? **Nee**, +8,0046 pt.
2. Enige dag-/kwartaalweglating met gemiddelde ≤0? **Nee**, beide cohortvarianten blijven positief.
3. Integriteitsfout of geen onafhankelijke bronbevestiging? **Geen resterende gridfout, wél ontbrekende onafhankelijke bronbevestiging.**
4. Eindstatus: **INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED**. Deze controles falsificeren de positieve gemiddelde impuls niet; ze valideren geen handelsedge. Het sterkste statistische bewijs blijft geconcentreerd in de eerste minuut.

Bronreplay: byte-identieke meetledgers; eerdere dynamische cohortresultaten exact gereproduceerd; 1.305 toekomst-afknipcontroles; 24 toetsen; 0 strategie-runs; 115 beschermde archiefbestanden ongewijzigd. Volledige aggregaten en testuitvoer staan naast dit rapport in research/afternoon-falsification-*.csv en results.json.
