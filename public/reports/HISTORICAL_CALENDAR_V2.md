# Historische kalender v2 — afzonderlijke technische voorbereiding

CALENDAR_V2_COMPLETE_CONDITIONAL_NOT_RELEASED

23 oktober 2026. Geen signalen, cohortselectie, trades, forward returns of P&L berekend. Geen Git-push of productie-uitrol. De oude voorbereiding en rapporten blijven byte-identiek.

## Besluit

De kalendercorrectie is apart geïmplementeerd en reproduceerbaar doorgerekend. Dit is géén definitieve goedkeuring van de onafhankelijke test: volume-/vendorvragen en een deel van de primaire bronherkomst blijven open. Een volledig uitgevoerde audit is niet hetzelfde als een volledig gecertificeerde bron.

## Wat is echt gewijzigd?

Alleen 2 april 2021: futures open tot 08:15 Chicago = 09:15 New York (13:15 UTC), ondanks gesloten cashmarkt. De verwachte sessie heeft 915 minuten; er zijn 910 vendorbars tot 09:14. Vijf ontbrekende minuten blijven onbekend, niet nul. De andere 37 uitzonderingsgrids zijn niet aangepast. Expiraties, 13 rollovers, joint-close spreads en alle ruwe OHLCV blijven gelijk.

De oude contextfunctie wordt exact hergebruikt: ATR is het gemiddelde van 14 eerdere geldige true ranges. Een korte/onvolledige geplande sessie wist de vorige-RTH-context. De eerstvolgende volledige sessie produceert dan geen true range zonder vorige volledige RTH; er wordt geen dagrange als vervanging ingevoerd. Dit is expliciet de bevroren architectuur, niet een nieuw geoptimaliseerd ATR-beleid.

## Bronsterkte, zonder schijnzekerheid

| Bewijsklasse | Uitzonderingen |
|---|---:|
| CME_LABELED_PRESERVED | 25 |
| CROPPED_ATTRIBUTED | 9 |
| DIRECT_CME_XLS_VERIFIED | 3 |
| PREVIOUSLY_REVIEWED_PRIMARY_NOTICE | 1 |

Alle 38 uitzonderingen zijn afzonderlijk beoordeeld. Een gedateerde, CME-gelabelde afbeelding op een brokerwebsite ondersteunt de getranscribeerde Equity-uren, maar is niet cryptografisch geauthenticeerd door CME. Bijgesneden tabellen missen de volledige titel/jaarcontext en blijven voorlopig. De 3 directe CME-XLS-cellen uit de eerdere audit zijn opnieuw tegen de tabelaflezing gecontroleerd. De rouwdag blijft op het eerder beoordeelde primaire CME-bericht gebaseerd; geen nieuwe lokale PDF-hash geclaimd.

Nog voorlopig wegens bijgesneden bron: 2018-11-22, 2018-11-23, 2019-01-21, 2019-02-18, 2020-01-20, 2020-02-17, 2020-04-10, 2021-01-18, 2021-02-15.
Cashsessiedatum, kalenderdatum en exchange clearing trade date zijn verschillende begrippen. Meerdere vakantiesessies kunnen één clearingdatum delen. Deze ronde verandert de volume-aggregatie niet en bewijst geen officiële volume-crossover.

## Technische beschikbaarheid vóór → na

| Periode | Cashsessies | Schoon 390+09:29 | ATR-context | Compressie-context | Sweep-context |
|---|---:|---:|---:|---:|---:|
| FULL_2019_2021 | 757 | 741 | 741 → 741 | 714 → 713 | 627 → 627 |
| REGISTERED_REMAINDER | 749 | 733 | 733 → 733 | 706 → 705 | 619 → 619 |

Alleen technische context, geen aantal signalen of handelsmogelijkheden. FULL bevat 8 eerder bekeken januaridagen; REGISTERED_REMAINDER begint 14 januari 2019. De 6 halve cashdagen blijven niet eligible voor volledige-RTH-modellen. Geen haltdag of ontbrekende boundary is synthetisch gerepareerd.

ATR/PD-context verandert op 15 datums. De beschikbaarheid van PDH/PDL vervalt op 5 april 2021, waardoor één compressie-contextdag afvalt. De overige verschillen betreffen de daaropvolgende ATR-historie. Nachtcontext en actieve prijsbars worden niet aangepast.

| Datum | Gewijzigde vooraf bekende contextvelden |
|---|---|
| 2021-04-05 | PDH, PDL |
| 2021-04-06 | atr14_prior |
| 2021-04-07 | atr14_prior |
| 2021-04-08 | atr14_prior |
| 2021-04-09 | atr14_prior |
| 2021-04-12 | atr14_prior |
| 2021-04-13 | atr14_prior |
| 2021-04-14 | atr14_prior |
| 2021-04-15 | atr14_prior |
| 2021-04-16 | atr14_prior |
| 2021-04-19 | atr14_prior |
| 2021-04-20 | atr14_prior |
| 2021-04-21 | atr14_prior |
| 2021-04-22 | atr14_prior |
| 2021-04-23 | atr14_prior |

## Elke kalenderuitzondering en de aanwezige bars

| Datum | Grens NY | Verwacht | Aanwezig | Ontbreekt | Buiten grid | Bewijs |
|---|---|---:|---:|---:|---:|---|
| 2018-11-22 | 13:00 | 1140 | 1140 | 0 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/US%20Holiday%20Trading%20Hours%20-%20Thanksgiving%20-%202018.png) |
| 2018-11-23 | 13:15 | 1155 | 1152 | 3 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/US%20Holiday%20Trading%20Hours%20-%20Thanksgiving%20-%202018.png) |
| 2018-12-05 | 09:30 | 930 | 930 | 0 | 0 | [PREVIOUSLY_REVIEWED_PRIMARY_NOTICE](https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2018/12/SER-8289.pdf) |
| 2018-12-24 | 13:15 | 1155 | 1155 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20-%20Holiday%20Trading%20Schedule%20-%20Christmas%202018.png) |
| 2018-12-25 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20-%20Holiday%20Trading%20Schedule%20-%20Christmas%202018.png) |
| 2019-01-01 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hs-fs/hubfs/CME%20Group%20Holiday%20Trading%20Schedule%20-%20New%20Years%20December%2031%2c%202018%20-%20January%202%2c%202019.png?width=1186&name=CME%20Group%20Holiday%20Trading%20Schedule%20-%20New%20Years%20December%2031%2c%202018%20-%20January%202%2c%202019.png) |
| 2019-01-21 | 13:00 | 1140 | 1140 | 0 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/CME%20Group%20-%20Martin%20Luther%20King%20Holiday%20Schedule%20-%202019.png) |
| 2019-02-18 | 13:00 | 1140 | 1140 | 0 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20%7C%20Presidents%20Day%20Holiday%20Trading%20Schedule%20-%20February%2015%20-%2019%2c%202019.png) |
| 2019-04-19 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.cannontrading.com/tools/support-resistance-levels/wp-content/uploads/2019/04/goodFriday2019.gif) |
| 2019-05-27 | 13:00 | 1140 | 1139 | 1 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/US%20Memorial%20Day%20Holiday%20Trading%20Hours%20-%202019.png) |
| 2019-07-03 | 13:15 | 1155 | 1155 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/US%20Independence%20Day%20on%204th%20July%20-%20Holiday%20Trading%20Schedule%20-%202019.png) |
| 2019-07-04 | 13:00 | 1140 | 1138 | 2 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/US%20Independence%20Day%20on%204th%20July%20-%20Holiday%20Trading%20Schedule%20-%202019.png) |
| 2019-09-02 | 13:00 | 1140 | 1140 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20Labor%20Day%20Holiday%20Schedule%20-%202019.png) |
| 2019-11-28 | 13:00 | 1140 | 1139 | 1 | 0 | [DIRECT_CME_XLS_VERIFIED](https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-thanksgiving-schedule.xls) |
| 2019-11-29 | 13:15 | 1155 | 1155 | 0 | 0 | [DIRECT_CME_XLS_VERIFIED](https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-thanksgiving-schedule.xls) |
| 2019-12-24 | 13:15 | 1155 | 1151 | 4 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/Christmas%20-%20Holiday%20Trading%20Schedule%20-%202019.png) |
| 2019-12-25 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/Christmas%20-%20Holiday%20Trading%20Schedule%20-%202019.png) |
| 2020-01-01 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/New%20Year%20-%20Holiday%20Trading%20Schedule%20-%20CME%20-%202019-2020.png) |
| 2020-01-20 | 13:00 | 1140 | 1134 | 6 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/CME%20Group%20-%20Martin%20Luther%20King%20Day%20Holiday%20Schedule%20-%202020.png) |
| 2020-02-17 | 13:00 | 1140 | 1139 | 1 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20Presidents%20Day%20Holiday%20Schedule%20-%202020.png) |
| 2020-04-10 | gesloten | 0 | 0 | 0 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20Good%20Friday%20Holiday%20Schedule%20-%20April%209%2c2020%20to%20April%2013%2c%202020.png) |
| 2020-05-25 | 13:00 | 1140 | 1140 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20-Memorial%20Day%20Holiday%20Schedule%20May%2024-26%2c%202020.png) |
| 2020-07-03 | 13:00 | 1140 | 1140 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20Independence%20Day%20Holiday%20Schedule%20-%20July%202%20to%20July%206%2c%202020.png) |
| 2020-09-07 | 13:00 | 1140 | 1140 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20Labor%20Day%20Holiday%20Schedule%20-%20September%202020.png) |
| 2020-11-26 | 13:00 | 1140 | 1140 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Thanksgiving%20Holiday%20Schedule%20-%20%20November%202020.png) |
| 2020-11-27 | 13:15 | 1155 | 1155 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Thanksgiving%20Holiday%20Schedule%20-%20%20November%202020.png) |
| 2020-12-24 | 13:15 | 1155 | 1155 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Christmas%20Holiday%20Schedule%20December%2024%20-%2028%2c%202020.png) |
| 2020-12-25 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Christmas%20Holiday%20Schedule%20December%2024%20-%2028%2c%202020.png) |
| 2021-01-01 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20New%20Years%20Holiday%20Schedule%20-%20December%2031%2c%202020%20-%20January%204%2c%202021.png) |
| 2021-01-18 | 13:00 | 1140 | 1140 | 0 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/CME%20Group%20-%20Martin%20Luther%20King%20Day%20Holiday%20Schedule%20-%20January%2015%20-%2019%2c%202021.png) |
| 2021-02-15 | 13:00 | 1140 | 1139 | 1 | 0 | [CROPPED_ATTRIBUTED](https://www.ampfutures.com/hubfs/CME%20Group%20-%20Martin%20Luther%20King%20Day%20Holiday%20Schedule%20January%2015%20-%2019%2c%202021.png) |
| 2021-04-02 | 09:15 | 915 | 910 | 5 | 0 | [DIRECT_CME_XLS_VERIFIED](https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-holiday-schedule.xls) |
| 2021-05-31 | 13:00 | 1140 | 1136 | 4 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20Memorial%20Day%20Holiday%20Schedule%20-%20May%2028%2c%202021%20-%20June%201st%2c%202021-1.png) |
| 2021-07-05 | 13:00 | 1140 | 1140 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hs-fs/hubfs/CME%20-%20Independence%20Day%20Holiday%20Schedule%20-%20July%202%20-%206%2c%202021.png?width=683&name=CME%20-%20Independence%20Day%20Holiday%20Schedule%20-%20July%202%20-%206%2c%202021.png) |
| 2021-09-06 | 13:00 | 1140 | 1136 | 4 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20Labor%20Day%20Holiday%20Schedule%20-%20September%205%20-%207%2c%202021.png) |
| 2021-11-25 | 13:00 | 1140 | 1140 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hs-fs/hubfs/CME%20Group%20-%20Thanksgiving%20Holiday%20Schedule%20-%20November%2024%20-%2026%2c%202021.png?width=740&name=CME%20Group%20-%20Thanksgiving%20Holiday%20Schedule%20-%20November%2024%20-%2026%2c%202021.png) |
| 2021-11-26 | 13:15 | 1155 | 1155 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hs-fs/hubfs/CME%20Group%20-%20Thanksgiving%20Holiday%20Schedule%20-%20November%2024%20-%2026%2c%202021.png?width=740&name=CME%20Group%20-%20Thanksgiving%20Holiday%20Schedule%20-%20November%2024%20-%2026%2c%202021.png) |
| 2021-12-24 | gesloten | 0 | 0 | 0 | 0 | [CME_LABELED_PRESERVED](https://www.ampfutures.com/hubfs/CME%20Group%20-%20Christmas%20Holiday%20Trading%20Schedule%20-%20December%2023%20-%2027%2c%202021.png) |

Verwacht/ontbreekt is een nominaal bar-start-grid, geen bewijs van werkelijk continu handelen of feedcompleetheid. De vijf ontbrekende minuten op 2 april zijn niet automatisch corrupt. De kalender ondersteunt 31 december 2021 als normale Equity-sessie; die dag wordt niet wegens een clearingbericht gesloten verklaard. Bronhashes en precieze rij-/kolomverwijzingen staan in historical-calendar-v2-sources.json en de uitzonderingen-CSV.

## Causaliteit, DST en bronbehoud

105 ruwe CSV’s opnieuw geparseerd en SHA-256 gecontroleerd bij origineel én privé-kopie. De ontdubbelde bars zijn exact gelijk aan de oorspronkelijke Parquet. Alle 585 bestaande bestanden en 13 private audit-/voorbereidingsbestanden blijven byte-identiek.
Toekomst-afkniptest op 43 verschillende openingen: alle 13 rollovers, gewijzigde contextdagen, zes DST-weekenden en de vier haltdagen. Alleen gegevens vóór 09:30 beschikbaar; ATR/PD/nachtcontext exact gelijk. Chicago/NY-conversie gebruikt de echte IANA-zones, geen vaste UTC-offset.

## Nog niet vrijgeven

- CROPPED_TABLES_REQUIRE_FULL_PRIMARY_PROVENANCE
- NQ_HALT_SECONDS_NOT_INDEPENDENTLY_CERTIFIED
- VENDOR_MISSING_MINUTE_SEMANTICS_AND_VOLUME_UNIVERSE_UNRESOLVED
- EARLIEST_TRUE_VOLUME_CROSSOVER_NOT_CERTIFIED
- LICENSE_AND_TICK_FILL_VALIDATION_UNCONFIRMED
- EXPLICIT_OUTCOME_RELEASE_REQUIRED

Barchart heeft de eerder gestelde ondersteuningsvraag ontvangen. Deze ronde leest geen inbox en claimt geen ontvangen inhoudelijk antwoord. Ontbrekende minuten worden niet als nulvolume geïnterpreteerd; dagvolume vervangt nooit stilzwijgend het minuutvolume. Geen aankoop, accountaanmaak, nieuwe externe berichten of wijziging van kandidaatregels.

## Reproductie en bestanden

`python -m scripts.historical_calendar_v2 verify` controleert de beschermde staat. `run` voert alleen kalender-/contextcontrole uit; `replay` doet twee onafhankelijke bronherberekeningen en vergelijkt uitvoerbytes. Gebruik de bestaande onderzoeksomgeving; geen nieuw strategiecommando. De aparte broncollector downloadt alleen werkelijk aangetroffen openbare links en geeft zelf nooit bewijsgoedkeuring.

Lokaal dashboard: /research/historical-calendar-v2. Publieke-safe JSON/Markdown bevatten tellingen, bronverwijzingen en kwaliteitsvlaggen, geen prijs-, ATR- of minuutarrays. Alle ruwe tabellen/CSV’s en numerieke context blijven Gitignored. De spreadsheetwerkwijze is gevolgd voor ongewijzigde bronbytes, expliciete missings en traceerbare aflezingen.
