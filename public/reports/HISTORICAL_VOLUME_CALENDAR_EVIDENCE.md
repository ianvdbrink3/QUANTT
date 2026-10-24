# Volume- en kalenderbewijsaudit — historische NQ-reeks

AUDIT_COMPLETE_RELEASE_NOT_APPROVED

23 oktober 2026. Alleen bronkwaliteit, kalender en vooraf bekende indicatorcontext. Geen signalen, trades, vervolgrendement of P&L op 2019–2021 berekend. Geen regels, bestaande rapporten, bronbars of rolloverdatums gewijzigd.

## Besluit

De audit is uitgevoerd, maar definitieve vrijgave is NIET verantwoord. Een echte volumedefinitie-tegenspraak en een aantoonbare kalenderfout zijn gevonden. Het keuringshek blijft gesloten; technische beschikbaarheid is geen onafhankelijke bevestiging.

## 1. Volume: dezelfde contracten, verschillende transactieverzamelingen

De hulptekst van de ingelogde Barchart-CSV-pagina bevestigt dat intraday bepaalde transactietypen uitsluit die wel in dagvolume kunnen voorkomen. Uitgeschakelde Total Volume and Open Interest levert contractvolume, geen totaal over alle expiraties. Dit bevestigt NIET dat een ontbrekende minuut nul transacties had. CME-bulletins onderscheiden eveneens Globex- en pit/block-volume; een willekeurig dagtotaal is geen uitwisselbare controle.

| Beslissessie | Contractpaar | Minuutvolume oud / nieuw | Minuutmarge nieuw−oud | Dagvolume oud / nieuw | Dagmarge | Zelfde rangorde? |
|---|---|---:|---:|---:|---:|---|
| 2019-06-14 | NQM19 → NQU19 | 205,819 / 207,874 | +2,055 | 254,822 / 253,169 | -1,653 | False |
| 2020-03-16 | NQH20 → NQM20 | 216,004 / 338,800 | +122,796 | 307,368 / 424,860 | +117,492 | True |

14 juni 2019 is dus NIET door de aparte dagbron bevestigd. Dit bewijst niet dat de minuutbestanden corrupt zijn; de filterdefinitie verschilt. Dagvolume wordt niet achteraf als vervangende rolloverregel ingevoerd. De finale publicatietijd van dagtotalen vóór de volgende activering is evenmin bewezen. CME meldt bovendien dat het eerste bulletin pas de volgende werkdag rond middernacht CT verschijnt en de finale versie rond 10:00 CT; dat is geen causale invoer voor een eerdere avondactivering.

### Alle 13 rollovers, inclusief eerdere overlapdagen

| Van → naar | Beslissessie | Actief vanaf | Minuutmarge | Ontbreekt oud/nieuw | Eerdere onvolledige vergelijkingen |
|---|---|---|---:|---:|---:|
| NQZ18 → NQH19 | 2018-12-14 | 2018-12-17 | +134,689 | 0 / 1 | 9 |
| NQH19 → NQM19 | 2019-03-08 | 2019-03-11 | +68,380 | 1 / 2 | 9 |
| NQM19 → NQU19 | 2019-06-14 | 2019-06-17 | +2,055 | 1 / 9 | 9 |
| NQU19 → NQZ19 | 2019-09-13 | 2019-09-16 | +74,661 | 3 / 0 | 9 |
| NQZ19 → NQH20 | 2019-12-13 | 2019-12-16 | +110,159 | 4 / 0 | 9 |
| NQH20 → NQM20 | 2020-03-16 | 2020-03-17 | +122,796 | 776 / 804 | 10 |
| NQM20 → NQU20 | 2020-06-15 | 2020-06-16 | +104,585 | 0 / 2 | 9 |
| NQU20 → NQZ20 | 2020-09-14 | 2020-09-15 | +232,936 | 0 / 0 | 10 |
| NQZ20 → NQH21 | 2020-12-14 | 2020-12-15 | +131,637 | 0 / 6 | 10 |
| NQH21 → NQM21 | 2021-03-15 | 2021-03-16 | +91,420 | 0 / 0 | 9 |
| NQM21 → NQU21 | 2021-06-14 | 2021-06-15 | +150,324 | 8 / 2 | 10 |
| NQU21 → NQZ21 | 2021-09-13 | 2021-09-14 | +209,371 | 0 / 0 | 10 |
| NQZ21 → NQH22 | 2021-12-10 | 2021-12-13 | +28,147 | 1 / 1 | 9 |

Alle 13 waargenomen beslissingen gereproduceerd vanaf de overlappende brondata t/m hun beslissessie. Alle 105 ruwe CSV’s opnieuw geparseerd en ontdubbeld: exact dezelfde contractbars als de bevroren privé-Parquet. Slechts 3 beslissessies hebben twee volledige nominale minuutgrids. Ook die zijn geen onafhankelijke certificering van de eerste werkelijke volumeswitch: eerdere vergelijkingen kunnen incompleet zijn en historie vóór de overlap is niet bewezen. Volledige grid ≠ volledige exchange feed. Ontbrekend volume blijft onbekend, zonder bovengrens of nul-imputatie.

## 2. Kalender: concrete correctie gevonden

| Datum | Origineel CME-bewijs | Correcte grens NY | Oude voorstelling |
|---|---|---|---|
| 2019-11-28 | Equity Products, Thanksgiving-rooster, Halt | 13:00 | klopt |
| 2019-11-29 | Equity Products, Thanksgiving-rooster, Close | 13:15 | klopt |
| 2021-04-02 | Equity Products, Good Friday-rooster, Close 08:15 CT | 09:15 | onterecht volledig gesloten |

Op Goede Vrijdag 2021 zijn 910 actieve vendorbars aanwezig tot 09:14 NY. Het oorspronkelijke CME-bestand bevestigt een korte futuresessie, ondanks gesloten cashmarkt. De eerdere kalender sloeg die dag geheel over. De geïsoleerde, brononderbouwde overlay corrigeert alleen dit gegeven; de bevroren uitvoeringsroute blijft onaangeroerd.

### Uitsluitend indicator-/eligibility-impact van deze overlay

| Periode | Model-context | Oude technische dagen | Overlay technische dagen |
|---|---|---:|---:|
| FULL_2019_2021 | TOM_RTH | 741 | 741 |
| FULL_2019_2021 | COMPRESSED_BREAK5 | 714 | 713 |
| FULL_2019_2021 | SWEEP_REV_1200 | 627 | 627 |
| REGISTERED_REMAINDER | TOM_RTH | 733 | 733 |
| REGISTERED_REMAINDER | COMPRESSED_BREAK5 | 706 | 705 |
| REGISTERED_REMAINDER | SWEEP_REV_1200 | 619 | 619 |

Vooraf bekende ATR/PD-context verschilt op 15 kalenderdagen. Details bevatten alleen datums/veldnamen, geen strategie-uitkomsten. De toekomst-afknipcontrole op 5 april vóór 09:30 slaagt. De vaste contracten en spreads blijven gelijk.

### Nog niet bewezen kalenderonderdelen

Het register beoordeelt elke cashfeestdag/halve dag in de warme en testhistorie apart. Een cashkalender bewijst geen CME-Globex-uren; een clearing- of settlementbericht evenmin. De twee opgehaalde CME-XLS-bestanden bewijzen drie specifieke daggrenzen, niet automatisch alle overige feestdagen in 2018–2021.

De officiële wijziging verwijdert de dagelijkse 16:15–16:30 NY-pauze vanaf 28 juni 2021. De rouwdag 5 december 2018 is afzonderlijk onderbouwd. De historische NQ-regel is hoofdstuk 359 (niet het grote S&P-contract): expiratie bij de reguliere Nasdaq-open op de vastgestelde derde vrijdag. Er zijn geen actieve bars na de nominale expiratie-open aangetroffen.

De SEC-werkgroep bevestigt de cash-halts op 9, 12, 16 en 18 maart 2020, maar beschrijft ook vertraging tussen cash-halt en CME-halt. Vanaf 12 oktober 2020 veranderden bovendien limieten en heropeningstijden. Cash-seconden mogen daarom niet zonder afzonderlijk bewijs naar NQ-minuten worden gekopieerd. Ontbrekende NQ-minuten blijven gemarkeerd; de vier haltdagen worden niet synthetisch compleet gemaakt.

### Datums waarvoor nog volledig futuresurenbewijs ontbreekt

Dit is geen lijst van ontbrekende CSV’s of bewezen corruptie. De bars kunnen met het voorlopige rooster overeenkomen; een overeenkomst bewijst het officiële rooster niet. Ook nul bars bewijst op zichzelf geen beurssluiting.

| Datum | Cash gesloten / half | Aanwezige bars | Laatste aanwezige bar NY |
|---|---|---:|---|
| 2018-11-22 | gesloten | 1140 | 2018-11-22T12:59:00-05:00 |
| 2018-11-23 | half | 1152 | 2018-11-23T13:14:00-05:00 |
| 2018-12-24 | half | 1155 | 2018-12-24T13:14:00-05:00 |
| 2018-12-25 | gesloten | 0 | geen |
| 2019-01-01 | gesloten | 0 | geen |
| 2019-01-21 | gesloten | 1140 | 2019-01-21T12:59:00-05:00 |
| 2019-02-18 | gesloten | 1140 | 2019-02-18T12:59:00-05:00 |
| 2019-04-19 | gesloten | 0 | geen |
| 2019-05-27 | gesloten | 1139 | 2019-05-27T12:59:00-04:00 |
| 2019-07-03 | half | 1155 | 2019-07-03T13:14:00-04:00 |
| 2019-07-04 | gesloten | 1138 | 2019-07-04T12:59:00-04:00 |
| 2019-09-02 | gesloten | 1140 | 2019-09-02T12:59:00-04:00 |
| 2019-12-24 | half | 1151 | 2019-12-24T13:14:00-05:00 |
| 2019-12-25 | gesloten | 0 | geen |
| 2020-01-01 | gesloten | 0 | geen |
| 2020-01-20 | gesloten | 1134 | 2020-01-20T12:59:00-05:00 |
| 2020-02-17 | gesloten | 1139 | 2020-02-17T12:59:00-05:00 |
| 2020-04-10 | gesloten | 0 | geen |
| 2020-05-25 | gesloten | 1140 | 2020-05-25T12:59:00-04:00 |
| 2020-07-03 | gesloten | 1140 | 2020-07-03T12:59:00-04:00 |
| 2020-09-07 | gesloten | 1140 | 2020-09-07T12:59:00-04:00 |
| 2020-11-26 | gesloten | 1140 | 2020-11-26T12:59:00-05:00 |
| 2020-11-27 | half | 1155 | 2020-11-27T13:14:00-05:00 |
| 2020-12-24 | half | 1155 | 2020-12-24T13:14:00-05:00 |
| 2020-12-25 | gesloten | 0 | geen |
| 2021-01-01 | gesloten | 0 | geen |
| 2021-01-18 | gesloten | 1140 | 2021-01-18T12:59:00-05:00 |
| 2021-02-15 | gesloten | 1139 | 2021-02-15T12:59:00-05:00 |
| 2021-05-31 | gesloten | 1136 | 2021-05-31T12:59:00-04:00 |
| 2021-07-05 | gesloten | 1140 | 2021-07-05T12:59:00-04:00 |
| 2021-09-06 | gesloten | 1136 | 2021-09-06T12:59:00-04:00 |
| 2021-11-25 | gesloten | 1140 | 2021-11-25T12:59:00-05:00 |
| 2021-11-26 | half | 1155 | 2021-11-26T13:14:00-05:00 |
| 2021-12-24 | gesloten | 0 | geen |

## Minimale ontbrekende bewijslast vóór vrijgave

1. Barchart-definitie van ontbrekende minuten én een controleerbare reconciliatie van het volume-universum rond de switches, minimaal 14 juni 2019 en 16 maart 2020 plus hun eerdere overlapdagen. Voor 2019 is nu een tegengestelde rangorde vastgesteld; een grotere marge is geen oplossing voor een ongedefinieerde meetgrootheid.
2. Ontbrekende gedateerde Equity Products/Globex-roosters 2018–2021 verzamelen of een onderbouwde, vooraf vastgelegde kalenderbeslissing nemen voor iedere context-rakende uitzondering. Het nieuwe uitzonderingenregister noemt de precieze datums.
3. Daarna de kalendercorrectie en expliciete volumedefinitie in een nieuwe vastgelegde voorbereidingsversie verwerken en alleen technische regressie/causaliteit opnieuw testen. Geen P&L gebruiken om tussen volumeregels te kiezen.
4. Los daarvan blijven gebruiksrechten, onafhankelijke tick/fill-validatie en expliciete uitkomstvrijgave aparte voorwaarden. Deze audit keurt geen winstgevend model goed.

## Borging en reproduceerbaarheid

Alle 105 oorspronkelijke CSV-hashes opnieuw geverifieerd. Alle 572 reeds bijgehouden bestanden en 7 private voorbereidingsbestanden byte-identiek. De aanvullende vier dag-CSV’s en twee CME-XLS-bestanden zijn apart privé gekopieerd en gehasht. De spreadsheetwerkwijze bewaart de originele bronnen en behandelt ontbreken niet als nul.

`python -m scripts.audit_historical_evidence verify` controleert de freeze; `run` voert alleen deze bewijsaudit uit; `replay` controleert byte-identieke uitvoer. Voor de originele .xls-bronnen is xlrd 2.0.2 nodig; de extra afhankelijkheid staat in requirements-historical-evidence.txt, naast de bestaande onderzoeksomgeving. Geen nieuw signaal- of P&L-commando aanwezig.

Lokaal opgeslagen: audit-JSON, rollover-CSV, dit rapport en publieke-safe kopieën. Niet gepusht of gedeployed; de bestaande productie blijft ongewijzigd. Geen ruwe arrays of extra vendor-CSV’s in publieke uitvoer.

## Bronnen

- [barchart_csv_help](https://www.barchart.com/futures/quotes/NQM19/historical-download)
- [cme_bulletin_definitions_and_availability](https://www.cmegroup.com/market-data/daily-bulletin.html)
- [cme_bulletin_volume_universe](https://www.cmegroup.com/daily_bulletin/current/Section11_Equity_And_Index_Futures.pdf)
- [cash_calendar](https://ir.theice.com/press/news-details/2018/NYSE-Group-Announces-2019-2020-and-2021-Holiday-and-Early-Closings-Calendar/default.aspx)
- [thanksgiving_2019](https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-thanksgiving-schedule.xls)
- [good_friday_2021](https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-holiday-schedule.xls)
- [pause_removal](https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2021/06/SER-8788.pdf)
- [mourning_2018](https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2018/12/SER-8289.pdf)
- [cash_halts_and_futures_coordination](https://www.sec.gov/files/rules/sro/nyse/2021/34-92428-ex3.pdf)
- [historical_NQ_expiry_chapter_359](https://www.cmegroup.com/market-regulation/files/16-081R_EXHA.pdf)
