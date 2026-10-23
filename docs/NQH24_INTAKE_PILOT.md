# NQH24 technische intakepilot

22 oktober 2026. Twee 1-minuutexports via bestaande Barchart-toegang. Geen nieuwe aankoop, signaal-, cohort- of rendementsberekening. Geen onafhankelijke toets vrijgegeven.

| Gevraagd blok | Bars | Volledige RTH-dagen | Ontbrekende RTH-minuten |
|---|---:|---:|---:|
| 2024-01-22 – 2024-02-02 | 13335 | 9 | 4 |
| 2024-02-05 – 2024-02-16 | 13372 | 10 | 0 |

Totaal: 26707 bars, 19 volledige RTH-dagen. Overlap tussen bestanden: 0 tijdstempels.

## Integriteit en beperkingen

- De bronbestanden zijn ongewijzigd gekopieerd naar `data/raw/independent-pilot/`, met byte-identieke SHA-256-controle en geverifieerde Gitignore. Downloads blijven intact.
- Het lokale register `research/nqh24-intake-pilot.json` bevat bronhashes, kolommen, UTC/Chicago/New York-grenzen, afzonderlijke kwaliteitsbevindingen en de RTH-minuutdekking per dag.
- RTH-dekking betekent uitsluitend 390 labels van 09:30 t/m 15:59 New York. Geen volledige Globex-kalendercertificering. Deze blokken bevatten geen DST-overgang of contractrollover. Geen bewijs van tick-level fills of onafhankelijk gevalideerde barconventie.
- Elke export begint op maandag om 00:00 Chicago (01:00 New York). Het eerste overnight-prefix vanaf zondag 18:00 New York is daardoor niet volledig opgenomen. RTH-dekking en volledige sessiedekking zijn niet hetzelfde.
- NQH24-identiteit berust op de geobserveerde contractpagina/exportkeuze en bestandsnaam. De CSV heeft geen contractkolom, bid/ask, ticks of orderfills. Volume omvat volgens de bronhulp alleen kwalificerende new-last-price trades, niet noodzakelijk alle CME-transactietypes.
- Dit is een technische beschikbaarheidsproef, geen volledige onafhankelijke steekproef, ATR-opwarmgarantie of bevestigend onderzoek. Geen 15:00-cohort of uitkomsten berekend. De eerdere inferentie- en uitvoeringsblokkades blijven gelden.
- Bestaande tijdelijke proeftoegang is geen permanent gratis abonnement. Exporttoegang is geen toestemming voor herpublicatie van ruwe marktdata. Geen accountwijziging, commit, push of deployment uitgevoerd.
- Alle 400 bestaande gevolgde bestanden bleven byte-identiek, inclusief de bevroren specificatie en archiefbestanden.

## Ontbrekende RTH-labels

Onderstaande gaten zijn onverklaard: deze intake stelt niet vast of sprake is van een officiële handelsstop, afwezige kwalificerende transacties of een bronprobleem. Geen forward-fill of uitsluiting op basis van rendement.

- 2024-01-23: 10:20, 10:21, 10:22, 10:23 New York. Status `RTH_GAP_UNEXPLAINED`.

## Feitelijke bestandscontroles

### nqh24_intraday-1min_historical-data-10-22-2026.csv

- SHA-256: `66441d492328528589ede1f690fba016ec32082eba2dfb254789095c162933e5`
- Chicago: 2024-01-22T00:00:00-06:00 t/m 2024-02-02T15:59:00-06:00.
- Kwaliteitsbevindingen (leeg = geen fout in de genoemde structurele controles): `{}`.

### nqh24_intraday-1min_historical-data-10-22-2026-2.csv

- SHA-256: `9ee92754ba8777635a37c6e8824619f798b45996b3d286ee3a4ede7621548514`
- Chicago: 2024-02-05T00:00:00-06:00 t/m 2024-02-16T15:59:00-06:00.
- Kwaliteitsbevindingen (leeg = geen fout in de genoemde structurele controles): `{}`.
