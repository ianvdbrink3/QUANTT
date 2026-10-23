# Kwaliteit eerste zes historische NQ-bestanden

TECHNICAL_BATCH_AUDITED_NOT_FULL_HISTORICAL_RELEASE

**64,622 bronbars**. Alle zes slagen voor schema, footer, unieke oplopende timestamps, eindige OHLCV, coherente OHLC, 0,25-punt tick-grid en positief geheel vendorvolume. Geen afkapping op de 20.000-recordgrens. Originele hashes zijn gecontroleerd; bronbytes niet gewijzigd. Dit maakt de reeks nog niet volledig of model-eligible.

| Contract | Volledige 390-min RTH-dagen | Standaarddagen met ontbrekende RTH-minuten | Eerste ATR14-readiness |
|---|---:|---:|---|
| NQZ18 | 21 | 0 | 2018-12-17 |
| NQH19 | 18 | 8 | 2019-01-10 |

## Kalender en contractovergang

- 5 december 2018: CME bevestigt halt om 08:30 Chicago /09:30 New York. Geen RTH verwachten. NQZ18 eindigt op 21 december om08:30 Chicago: verenigbaar met expiratie aan de cash open, geen kunstmatige verlenging naar16:00.
- Thanksgiving 22 november13:00NY is broker-ondersteund; 23 november13:15NY blijft een voorlopige kalenderreconstructie. Christmas Eve13:15NY en Christmas Day gesloten zijn door TradeStation gedocumenteerd. New Year gesloten is kalenderreconstructie. Deze uitzonderingen worden niet als gewone corrupte390-minuten-sessies bestempeld en niet trade-eligible verklaard.
- Volledige sessiedekking buiten RTH gebruikt ook de historische16:15–16:30NY-pauze als reconstructie. De volledige kalender is niet als exchange-gecertificeerd vrijgegeven. Per dag staan zowel RTH- als nachtsessie-gaten in JSON.

Volumeregel op voltooide gezamenlijke sessies, activatie volgende sessie en laatste gemeenschappelijke RTH-close vóór activatie:

```json
{
  "from": "NQZ18",
  "to": "NQH19",
  "decision_session": "2018-12-14",
  "old_volume": 297045,
  "new_volume": 431734,
  "effective_session": "2018-12-17",
  "effective_utc": "2018-12-16T23:00:00+00:00",
  "close_bar_utc": "2018-12-14T20:59:00+00:00",
  "spread_available_utc": "2018-12-14T21:00:00+00:00",
  "spread_points": 22.75,
  "future_cutoff_verified": true,
  "status": "OBSERVED_VOLUME_RULE_WITH_CALENDAR_LIMITATIONS"
}
```

### Doorlopende ATR in plaats van contract-only opwarming

De contract-only telling hierboven is niet de vNext-vereiste. Met de ongewijzigde point-in-time continuous-module en Z18-historie zijn **8 van 8** aanwezige volledige RTH-dagen van2–11januari al ATR14-ready. Beide tellingen staan apart in JSON. Geen UP-cohort of vrijgegeven eindtoets.

## Ontbrekende standaard-RTH-minuten

NQZ18: geen
NQH19: 2018-12-03 (177), 2018-12-04 (69), 2018-12-06 (71), 2018-12-07 (58), 2018-12-10 (7), 2018-12-11 (3), 2018-12-12 (2), 2018-12-13 (1)

## Grenzen van dit oordeel

De beperkte batch stopt met volledige H19-RTH op11 januari2019; zondag13januariavond is geen volledige volgende handelsdag. Contract-only ATR reset de prior-close na een onvolledige/korte sessie, niet na een volledig gesloten dag. De aparte continuous-telling draagt vooraf bekende, causale Panama-historie mee, nooit onverschoven contractprijsverschillen. Readiness en volumetelling zijn technische checks, geen 15:00-cohort of kandidaatuitkomsten. Geen onafhankelijke toets vrijgegeven.

Timestamps zijn Chicago→UTC→New York geconverteerd. Er is in deze batch geen DST-overgang geobserveerd; tests van IANA-overgangen zijn geen empirische certificering. Volume is het volume van deze bron, niet onafhankelijk tegen CME-totalen gevalideerd. Geen Tick/BBO-kolommen of licentiegoedkeuring aanwezig. De spreadsheet-richtlijnen zijn toegepast voor bronbehoud en expliciete ontbrekende waarden; er is geen bron-CSV herschreven.

## Bronverwijzingen

- mourning_exchange: https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2018/12/SER-8289.pdf
- expiration_exchange: https://www.cmegroup.com/market-regulation/files/16-081R_EXHA.pdf
- christmas_broker: https://cdn.tradestation.com/uploads/Christmas-2018.pdf
- thanksgiving_broker: https://www.ampfutures.com/news/thanksgiving-holiday-trading-schedule-2018
- thanksgiving_friday_unconfirmed: 13:15NY provisional reconstruction; authoritative date-specific close not recovered. Exclude from eligibility regardless.
