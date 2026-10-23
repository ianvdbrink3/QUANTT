# Historische contractreeks: ontvangst compleet

23 oktober2026. **Alle103vaste planblokken zijn ontvangen. Er ontbreken geen downloads meer.**

Er staan 105 fysieke CSV-bestanden in de ontvangstregisters:103unieke planblokken en2reeds bekende dubbele downloads. Die dubbele bestanden blijven bewaard, maar tellen niet opnieuw mee. Tijdens de hervatte ronde zijn de72destijds resterende blokken ontvangen.

| Contract | Unieke planblokken |
|---|---:|
| NQZ18 | 3 |
| NQH19 | 8 |
| NQM19 | 9 |
| NQU19 | 8 |
| NQZ19 | 8 |
| NQH20 | 8 |
| NQM20 | 8 |
| NQU20 | 8 |
| NQZ20 | 8 |
| NQH21 | 8 |
| NQM21 | 8 |
| NQU21 | 8 |
| NQZ21 | 8 |
| NQH22 | 3 |

## Gecontroleerd

- SHA-256 van alle oorspronkelijke Downloads-bestanden vergeleken met hun geregistreerde hashes.
- Alle privé-kopieën byte-identiek en perbestand op Gitignore gecontroleerd.
- Alle103bloknummers uit de oorspronkelijke downloadlijst aanwezig. Contract, bronbereik, schema, footer, volgorde, dubbele labels en de20.000-recordgrens metadata-only gecontroleerd. Geen metadatawaarschuwingen.
- 1,286,673 bronbars inclusief contractoverlap en dubbele downloads. Dit is nadrukkelijk niet het aantal unieke minuten van één actieve reeks.
- Geen aankoop, account, abonnementswijziging, Git-push of Vercel-uitrol.

## Nog niet vastgesteld

Een complete ontvangst is geen volledige datakwaliteits- of importgoedkeuring. Numerieke prijzen/volumes, alle RTH-minuten, CMEfeestdagen/haltes, definitieve volume-rollovers, causaliteit van opwarming en licentiegeschiktheid moeten nog afzonderlijk worden beoordeeld. Nieuwe2019–2021-prijzen zijn tijdens deze intake niet numeriek geanalyseerd. Geen signalen, rendementen of onafhankelijke backtest berekend.

## Lokale opslag en reproduceerbaarheid

Originelen blijven in Downloads. De privé-kopieën staan in data/raw/historical-replication-2019-2021/. Het volledige bronregister met hashes staat in research/historical-2019-2021-complete-source-register.json. De eerdere batchregisters en oorspronkelijke downloadlijst blijven behouden.

De spreadsheetvaardigheid is alleen gebruikt voor herleidbare bronregistratie en structuurcontrole; geen bron-CSV herschreven, prijzen aangevuld of onderzoeksuitkomsten berekend.
