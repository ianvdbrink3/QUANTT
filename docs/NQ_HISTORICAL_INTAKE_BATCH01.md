# Ontvangst eerste zes historische NQ-bestanden

22 oktober 2026. De expliciet genoemde zes exports zijn via de bestaande Barchart-sessie gedownload. Geen nieuwe aankoop, account, abonnementswijziging of uitkomstberekening. De overige 97 bestanden zijn niet opgehaald.

| # | Contract | Gevraagde start | Gevraagd einde | Minuutbars | Metadatavlaggen |
|---:|---|---|---|---:|---|
| 1 | NQZ18 | 11/19/2018 | 12/02/2018 | 13212 | {} |
| 2 | NQZ18 | 12/03/2018 | 12/16/2018 | 13211 | {} |
| 3 | NQZ18 | 12/17/2018 | 12/21/2018 | 5592 | {} |
| 4 | NQH19 | 12/03/2018 | 12/16/2018 | 8247 | {} |
| 5 | NQH19 | 12/17/2018 | 12/30/2018 | 12075 | {} |
| 6 | NQH19 | 12/31/2018 | 01/13/2019 | 12285 | {} |

Totaal: **64622 bronbars**. Dit is niet het aantal unieke minuten van één actieve doorlopende reeks: NQZ18 en NQH19 overlappen bewust. Overlap binnen hetzelfde contract: **0** tijdstempels. Twee verschillende contracten op hetzelfde tijdstip zijn geen duplicaat dat verwijderd moet worden.

## Opslag en controle

- Originelen blijven in Downloads. Byte-identieke kopieën staan onder `data/raw/historical-replication-2019-2021/`. Gitignore is per bestand gecontroleerd. Niets naar GitHub of Vercel gestuurd.
- Het lokale register `research/afternoon-historical-intake-batch01.json` bevat per bestand SHA-256, bestandsgrootte, kolommen, bars, footer, UTC/Chicago/New York-bereik en metadatawaarschuwingen. De eerder vergrendelde downloadlijst en het testvenster zijn niet gewijzigd.
- Geen nieuwe OHLCV-waarden numeriek onderzocht. Alleen structuur en tijdstempels gecontroleerd; geen 15:00-waarden, cohort, rendement, volatiliteitsfeature, volumeroll of P&L berekend. De afgekeurde methoderonde blijft afgekeurd.
- Geen claim over complete CME-sessies of trade-eligible dagen. Feestdagen, vroege sluitingen, bijzondere haltes en de aflopende NQZ18-expiratie moeten nog officieel worden verzoend. Een dun bestand van een aflopend contract is niet automatisch een mislukte download.
- De zondagen zijn bewust inbegrepen. Eerste en laatste bronlabels zijn Chicago-civiele datums, niet noodzakelijk complete NY-handelsdagen. Het eerste maandagprefix begint om 00:00 Chicago, dus de voorafgaande zondagavond is daar niet compleet. Opwarming en uiteindelijke kwaliteit blijven afzonderlijke controles.
- Alle 400 gevolgde bestanden bleven byte-identiek. De bestaande methode-/vensterlocks zijn apart verifieerbaar; de kandidaat blijft niet vrijgegeven.

## Werkelijk ontvangen bronbereik (Chicago)

| # | Eerste label | Laatste label | Bytes |
|---:|---|---|---:|
| 1 | 2018-11-19T00:00:00-06:00 | 2018-12-02T23:59:00-06:00 | 818492 |
| 2 | 2018-12-03T00:00:00-06:00 | 2018-12-16T23:59:00-06:00 | 818868 |
| 3 | 2018-12-17T00:00:00-06:00 | 2018-12-21T08:29:00-06:00 | 340865 |
| 4 | 2018-12-03T00:08:00-06:00 | 2018-12-16T23:59:00-06:00 | 495761 |
| 5 | 2018-12-17T00:00:00-06:00 | 2018-12-30T23:59:00-06:00 | 750863 |
| 6 | 2018-12-31T00:00:00-06:00 | 2019-01-13T23:59:00-06:00 | 761149 |

De gebruikte spreadsheet-instructies beperken deze controle tot lezen en herleidbare bronregistratie. Er is geen werkblad herschreven, prijsserie aangevuld of CSV opnieuw geëxporteerd.
