# NQ-inventarisatie na september 2025 — 21 oktober 2026

Alleen kolomnamen, timestamps, aantallen en bestandshashes gelezen. Geen OHLCV-analyse, featureberekening, signalen of backtest. 95 NQ-genaamde CSV-bestanden gevonden in Downloads (recursief) en de lokale QUANT-datamappen van deze projectworkspace. Geen fouten; geen volledige schijfdoorzoeking. Bronbestanden niet gewijzigd, gekopieerd of naar Git gepusht. Privé volledig padenoverzicht: `artifacts/nq-post-september-inventory.json`; openbaar geaggregeerd overzicht: `public/data/research-freeze.json`.

## Afzonderlijk Barchart-contract NQZ25 in Downloads

Gemeenschappelijke bestandsstam: `nqz25_intraday-1min_historical-data-10-19-2026`. Onderstaande tijden zijn bronklok volgens de bestaande Chicago-importconventie. De datum in de bestandsnaam is niet het datumbereik.

| Suffix | Eerste timestamp | Laatste timestamp | Beoordeling |
|---|---|---|---|
| `.csv` | 6 okt 2025 00:00 | 10 okt 2025 15:59 | Overlapt grotere exports |
| `-2.csv` | 21 sep 2025 17:00 | 3 okt 2025 15:59 | Bevat start oktober |
| `-3.csv` | 3 okt 2025 00:00 | 17 okt 2025 15:59 | Oktoberdeel |
| `-4.csv` | 17 okt 2025 00:00 | 31 okt 2025 15:59 | Oktoberdeel |
| `-5.csv` | 31 okt 2025 00:00 | 14 nov 2025 15:59 | Novemberdeel |
| `-6.csv` | 14 nov 2025 00:00 | 28 nov 2025 12:14 | Vroege sluiting mogelijk; niet getoetst |
| `-7.csv` | 28 nov 2025 07:30 | 12 dec 2025 15:59 | Decemberdeel |

Dit toont bereik, **geen bewezen volledigheid, correcte tijdzone, contractauthenticiteit, licentie of onafhankelijkheid**. Overlap moet later op OHLCV-conflicten en minute coverage worden gecontroleerd, vóór enig resultaat. De genummerde bestanden `-8` en `-12` bevatten geen parsebare bars; `-9`, `-10`, `-11`, `-13` bevatten januari–maart 2025 en zijn dus geen vervolgdataset. Niet uit de nummering concluderen dat ze op `-7` aansluiten.

De lokaal gestagede `10-20-2026-2.csv` eindigt 30 september 23:59 Chicago. Vanaf 17:00 Chicago / 18:00 NY behoort die avond al tot civiele sessie 1 oktober: een gedeeltelijke overnight-prefix, **geen complete oktoberdag**. Deze bars zijn door de historische pipeline buiten het septemberonderzoek gehouden.

## Andere aanwezige bronnen, niet uitwisselbaar

| Bestanden | Bereik na september | Limiet |
|---|---|---|
| `Dataset_NQ_1min_2022_2025.csv` | 70.460 timestamps vanaf 1 okt t/m 11 dec 2025 20:52, label ET | Geen afzonderlijk contract uit naam, herkomst/rolls/licentie niet gevalideerd; niet bij Barchart mengen |
| `archive/NQ_in_1_minute.csv` | 5 okt 2025 22:00–10 okt 2025 15:15; 6.554 rijen | Continue reeks; tijdzone/rolls onbevestigd |
| `archive/NQ_in_3_minute.csv`, `NQ_in_5_minute.csv`, `NQ_in_15_minute.csv`, `NQ_in_30_minute.csv`, `NQ_in_45_minute.csv`, 1/2/3/4-hour, daily, weekly | Sommige timestamps t/m 10 okt 2025 | Geen vervanging voor ruwe afzonderlijke 1m-contractbars |
| `frd_sample_futures_NQ/NQ_1min_sample.csv` en vier andere timeframes | 1–16 oktober **2026**; 16.200 minuutrijen | Buiten gekozen testvenster t/m sep 2026; sample, contract/roll/tijdzone onbevestigd |

## Wat ontbreekt voor 1 oktober 2025–30 september 2026

- De aanwezige NQZ25-exports lopen tot 12 december 2025; nog geen gevalideerd volledig kalender-/minutenoverzicht. Niet opnieuw heel oktober/november downloaden voordat dit veilig is vastgesteld.
- Geen NQH26-, NQM26- of NQU26-contract-CSV's aangetroffen. Nodig: volledige actieve sessies, met voldoende gezamenlijke pre-roll volumehistorie en gezamenlijke 15:59 NY-close voor de december-, maart- en juni-overgangen. Contracten mogen niet op vooraf geraden kalenderdagen aan elkaar worden geplakt.
- Ook NQZ26-overlap en actieve septemberdagen tot 30 september ontbreken in de geïnspecteerde bestanden. NQZ25-data na 12 december kan nodig zijn om de december-volumeswitch objectief te bewijzen; de exacte benodigde einddatum volgt pas uit de overlap, niet uit rendementen.
- Historie tot 30 september 2025 blijft ongescoorde ATR-/volume-prefix. Nieuwe kalender/feestdaguren, leverancierstijdzone/DST en gebruiksrechten moeten vooraf vastliggen.
- Onafhankelijkheid is niet door bestandsaanwezigheid bewezen. De eerdere Downloads-bestanden waren al bekend; sluit eerdere strategie-uitkomsten over oktober en later uit vóór een claim van nieuwe OOS. Vandaag zijn uitsluitend timestamps geïnventariseerd.

**Besluit:** vervolgmateriaal voor oktober–begin december 2025 is al aanwezig; voor het volledige vaste jaar ontbreekt nog het grootste deel van de afzonderlijke 2026-contractdata. Geen toekomstige test gestart.
