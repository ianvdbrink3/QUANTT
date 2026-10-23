# Aanvullende technische beoordeling 2019–2021

TECHNICAL_REVIEW_NOT_OUTCOME_RELEASE

Geen signalen of resultaten op de geregistreerde2019–2021-restperiode. De enige signaalreplay hieronder betreft de reeds verbruikte435 ontdekkingsdagen, uitsluitend als regressiecontrole.

Oude ontdekkingsreeks: exact435 dagen, alle8 contextvelden, OHLCV-arrays en de oorspronkelijke 253 trades exact gereproduceerd ({'TOM_RTH': 81, 'COMPRESSED_BREAK5': 109, 'SWEEP_REV_1200': 63}). Geen nieuwe P&L-tabellen gepubliceerd.

Alle13 echte rollover-openingen opnieuw berekend met de actuele RTH volledig afgeknipt op09:30. De vooraf bekende ATR, PDH/PDL en nachtankers blijven gelijk. Alle13 hebben ATR14 beschikbaar op dag1 van het nieuwe contract. De eerste overgang is17december2018, gelijk aan de legacy-fragmentroute.

## De tien uitgesloten normale cashdagen

| Datum | Contract | Ontbrekende RTH-minuten NY | 09:29 ontbreekt |
|---|---|---|---|
| 2020-03-09 | NQH20 | 09:33, 09:36, 09:37, 09:38, 09:39, 09:40, 09:41, 09:42, 09:43, 09:44, 09:45, 09:46, 09:47, 09:48 | True |
| 2020-03-12 | NQH20 | 09:37, 09:38, 09:39, 09:40, 09:41, 09:42, 09:43, 09:44, 09:45, 09:46, 09:47, 09:48, 09:49 | True |
| 2020-03-13 | NQH20 | geen | True |
| 2020-03-16 | NQH20 | 09:31, 09:32, 09:33, 09:34, 09:35, 09:36, 09:37, 09:38, 09:39, 09:40, 09:41, 09:42, 09:43, 09:44 | True |
| 2020-03-18 | NQM20 | 12:58, 12:59, 13:00, 13:01, 13:02, 13:03, 13:04, 13:05, 13:06, 13:07, 13:08, 13:09, 13:10 | True |
| 2020-06-16 | NQU20 | 10:56 | False |
| 2020-07-31 | NQU20 | 15:02 | False |
| 2020-09-03 | NQU20 | 11:24 | False |
| 2020-09-08 | NQU20 | 09:44 | False |
| 2021-05-06 | NQM21 | 09:34, 09:35, 11:25, 11:26 | False |

2020-03-13 has390RTH bars but lacks09:29. Root COMPLETE labels its RTH-only gap classification, not full eligibility. This supplement explicitly corrects the presentation, not any exclusion or count.

## Volume-overgangen: resterende onzekerheid

3van13 beslissessies hebben beide contracten volledig op de gereconstrueerde minuutgrid. De overige10 hebben ontbrekende interne minuten. Veel daarvan liggen in de dunne nacht. Geen ontbrekende minuut is als nulvolume ingevuld. De verwachte grid is geen bewijs dat er in elke minuut werkelijk transacties hadden moeten zijn.

De kleinste waargenomen volumemarge is2.055contracten op14juni2019 (switch17juni). De oude NQM19 mist01:32NY en het nieuwe NQU19 mist9 nachtminuten. Zonder onafhankelijke totalen/no-trade-definitie is de tekenvastheid van de werkelijke volumevergelijking niet bewezen. Op16maart2020 ontbreken776/804minuten tegenover de normalegrid, deels in een limit-/haltregime. Het register bevat beide feitelijke aantallen zonder ze als bewezen broncorruptie aan te merken.

## Wat nu nog nodig is, zonder strategie-uitkomsten te openen

- Datum-specifieke historische NQ-futuresuren en limit-/haltvensters onderbouwen waar ze de voorafgaande indicatorhistorie of rolloverbeslissing raken. Cash- en CME-kalender niet verwarren.
- Vendorbetekenis van ontbrekende volume-minuten of onafhankelijke dagtotalen voor de beslissessies vaststellen. Vooral14juni2019 en16maart2020. Geen rolloverdatum aanpassen op P&L.
- Licentie/gebruik en eventuele distributierechten blijven afzonderlijk onbevestigd. De Barchartvoorwaarden waren via de documentopvraag niet leesbaar door een verificatiescherm. Geen omzeiling geprobeerd.
- Daarna de nieuwe runner/codeversie definitief vastleggen en afzonderlijk de uitkomsttoets vrijgeven. Nog geen120 gescoorde waarnemingen claimen: dit rapport telt technische dagen, geen signalen of trades.

Geen aankoop, nieuwe account, externe upload, Git-push of productie-uitrol. Ruwe data blijft privé.
