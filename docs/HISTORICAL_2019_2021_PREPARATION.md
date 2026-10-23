# Historische NQ-contractreeks 2019–2021: kwaliteitscontrole en import

QUALITY_AUDITED_CONDITIONAL_READINESS_NOT_RELEASED

Geen strategie-signalen, toekomstig rendement, trades of P&L berekend. De onafhankelijke toets is niet vrijgegeven. Bron-CSV’s, bestaande regels en oude rapporten blijven ongewijzigd.

105 fysieke CSV’s / 103 planblokken / 14 contracten. 1,286,673 bronbars → 1,263,677 unieke contractminuten. 22,996 identieke overlaprecords verwijderd; 0 conflicterende sleutels. Actieve voorlopige reeks: 1,092,525 bars.

## Technische beschikbaarheid, geen signalentelling

| Periode | Cashsessies incl. halve dagen | Normaal | Schoon 390 +09:29 | ATR-ready | Compressie-context | Sweep-context |
|---|---:|---:|---:|---:|---:|---:|
| FULL_2019_2021 | 757 | 751 | 741 | 741 | 714 | 627 |
| REGISTERED_REMAINDER | 749 | 743 | 733 | 733 | 706 | 619 |

TOM-kolom telt uitsluitend ATR-ready evaluatiedagen, niet maandwissels. Compressie telt beschikbare ATR/PDH/PDL, niet de compressiedrempel of uitbraken. Sweep telt volledige nachtcontext, niet sweep-events. De 8 reeds geïnspecteerde januaridagen tellen niet mee in REGISTERED_REMAINDER. De tellingen zijn voorwaardelijk zolang kalender-/rolloverpunten openstaan.

## Prijzen, tijd en volume

Numerieke fouten per categorie: `{'nonfinite': 0, 'incoherent': 0, 'off_tick': 0, 'nonpositive_price': 0, 'invalid_volume': 0}`. Afkappingswaarschuwingen: 0. Bronhashes van originelen en privé-kopieën opnieuw gecontroleerd. Ontbrekende minuten nooit gevuld, tegenstrijdige records nooit stilzwijgend gekozen.

Chicago-bronlabels worden met IANA-DST naar UTC en New York geconverteerd. Alle zes DST-weekenden hebben expliciete controle op de omringende cash-open labels. Dit valideert de conversie, niet onafhankelijk de vendor-timestampconventie. Volume is positief geheel vendorvolume, niet tegen officiële CME-dagtotalen bevestigd. CSV bevat geen ticks, bid/ask of intern contract-ID.

## Causale volume-overgangen

| Van | Naar | Beslissessie | Actief vanaf | Oude volume | Nieuwe volume | Ontbrekende minuten oud/nieuw |
|---|---|---|---|---:|---:|---|
| NQZ18 | NQH19 | 2018-12-14 | 2018-12-17 | 297,045 | 431,734 | 0 / 1 |
| NQH19 | NQM19 | 2019-03-08 | 2019-03-11 | 258,239 | 326,619 | 1 / 2 |
| NQM19 | NQU19 | 2019-06-14 | 2019-06-17 | 205,819 | 207,874 | 1 / 9 |
| NQU19 | NQZ19 | 2019-09-13 | 2019-09-16 | 190,052 | 264,713 | 3 / 0 |
| NQZ19 | NQH20 | 2019-12-13 | 2019-12-16 | 267,146 | 377,305 | 4 / 0 |
| NQH20 | NQM20 | 2020-03-16 | 2020-03-17 | 216,004 | 338,800 | 776 / 804 |
| NQM20 | NQU20 | 2020-06-15 | 2020-06-16 | 235,811 | 340,396 | 0 / 2 |
| NQU20 | NQZ20 | 2020-09-14 | 2020-09-15 | 204,571 | 437,507 | 0 / 0 |
| NQZ20 | NQH21 | 2020-12-14 | 2020-12-15 | 207,824 | 339,461 | 0 / 6 |
| NQH21 | NQM21 | 2021-03-15 | 2021-03-16 | 220,114 | 311,534 | 0 / 0 |
| NQM21 | NQU21 | 2021-06-14 | 2021-06-15 | 142,596 | 292,920 | 8 / 2 |
| NQU21 | NQZ21 | 2021-09-13 | 2021-09-14 | 263,718 | 473,089 | 0 / 0 |
| NQZ21 | NQH22 | 2021-12-10 | 2021-12-13 | 332,436 | 360,583 | 1 / 1 |

Alle getoonde overgangen zijn opnieuw uitsluitend uit een afgekapt bestand t/m de beslissessie gereproduceerd. Activering volgende sessie, spread laatste gemeenschappelijke voltooide15:59-bar vóór activering. Actieve ruwe OHLCV blijft onverschoven. Geen kalenderfallback of selectie op strategie-uitkomst. De bestaande60-minuten-endpointtolerantie certificeert geen ontbrekende interne vendorvolume-minuten.

## Kalender en afwijkende dagen

Officiële cashkalender:27 feestdagen en6 vroege sluitingen in2019–2021. Cashdagen zijn niet gelijk aan CME clearing trade dates. De dagelijkse16:15–16:30NY-pauze geldt uitsluitend vóór28juni2021. Expiratie is apart gemarkeerd, geen rollovertrigger. Voor alle datum-specifieke futuresfeestdagen is nog geen volledige primaire urenmatrix teruggevonden. De kalender blijft daarom deels voorlopig.

9,12,16en18maart2020 zijn gedocumenteerde circuit-breakerdagen. Ontbrekende minuten op die datums worden als halt-geassocieerd gemarkeerd, maar niet zonder exact NQ-bewijs uit de verwachte RTH-grid geschrapt. Deze dagen worden niet kunstmatig390-minuten-eligible gemaakt. Ook geen prijs-fills om een complete simulatie te construeren.

| Normale datum met onvoldoende RTH/boundary | Ontbrekende RTH-minuten | Classificatie |
|---|---:|---|
| 2020-03-09 | 14 | DOCUMENTED_CASH_HALT_DATE_EXACT_FUTURES_MINUTES_UNCERTIFIED |
| 2020-03-12 | 13 | DOCUMENTED_CASH_HALT_DATE_EXACT_FUTURES_MINUTES_UNCERTIFIED |
| 2020-03-13 | 0 | COMPLETE |
| 2020-03-16 | 14 | DOCUMENTED_CASH_HALT_DATE_EXACT_FUTURES_MINUTES_UNCERTIFIED |
| 2020-03-18 | 13 | DOCUMENTED_CASH_HALT_DATE_EXACT_FUTURES_MINUTES_UNCERTIFIED |
| 2020-06-16 | 1 | UNEXPLAINED_MISSING_MINUTES_NOT_AUTOMATICALLY_CORRUPT |
| 2020-07-31 | 1 | UNEXPLAINED_MISSING_MINUTES_NOT_AUTOMATICALLY_CORRUPT |
| 2020-09-03 | 1 | UNEXPLAINED_MISSING_MINUTES_NOT_AUTOMATICALLY_CORRUPT |
| 2020-09-08 | 1 | UNEXPLAINED_MISSING_MINUTES_NOT_AUTOMATICALLY_CORRUPT |
| 2021-05-06 | 4 | UNEXPLAINED_MISSING_MINUTES_NOT_AUTOMATICALLY_CORRUPT |

## Openstaande vrijgavevoorwaarden

- EXPLICIT_OUTCOME_RELEASE_REQUIRED
- DATE_SPECIFIC_CME_HOLIDAY_AND_HALT_GRID_NOT_FULLY_CERTIFIED
- NEW_FULL_WINDOW_ROUTE_OUTCOME_PARITY_NOT_EXECUTED
- LICENSE_AND_INDEPENDENT_VENDOR_VALIDATION_UNCONFIRMED
- ROLL_VOLUME_INTERIOR_MINUTE_GAPS

Geen oordeel over winstgevendheid of onafhankelijke bevestiging. Geen Git-push of productie-uitrol. Licentie/redistributie en onafhankelijke volume-/tickvalidatie ontbreken. Kleine ontbrekende-volume-intervallen mogen no-trade-minuten zijn; zij bewijzen op zichzelf geen corrupte bron.

## Lokale reproduceerbaarheid

`python -m scripts.prepare_historical_contracts verify` controleert de freeze. `python -m scripts.prepare_historical_contracts run` maakt uitsluitend kwaliteits- en importuitvoer. `python -m scripts.prepare_historical_contracts replay` controleert byte-identieke dubbele import. Geen optie voor strategie-uitkomsten aanwezig.

Privé: artifacts/historical-preparation/contract-bars.parquet, active-bars.parquet, prior-context.json en volledige dag-/bronkwaliteitsregisters. Publiek geschikt: alleen research/historical-preparation-quality.json en public/data/historical-preparation.json met tellingen/vlaggen, geen minuutarrays. De spreadsheetrichtlijnen sturen bronbehoud en expliciete missing-values; geen brondata gerepareerd.

## Primaire bronnen

- [cash_calendar](https://ir.theice.com/press/news-details/2018/NYSE-Group-Announces-2019-2020-and-2021-Holiday-and-Early-Closings-Calendar/default.aspx)
- [pause_removal](https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2021/06/SER-8788.pdf)
- [mourning](https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2018/12/SER-8289.pdf)
- [halt_dates](https://www.nyse.com/article/assessing-nyse-model-performance)
- [halt_coordination](https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2020-14)
- [year_end_processing_not_trading_hours](https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-new-years-advisory.pdf)
- [expiry_rule_historical](https://www.cmegroup.com/market-regulation/files/16-081R_EXHA.pdf)
