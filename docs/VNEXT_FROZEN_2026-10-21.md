# Bevroren onderzoeksstand VNEXT_159_2026-10-21

Deze stand bestaat naast de ongewijzigde **Baseline v0.9**. Historische codecommit: `1be0a10e0afd2713957b1a6e262524613cdc07fe`. Dec 2024–sep 2025 is volledig verbruikt onderzoeksdata, geen nieuwe holdout. Geen regels, fills, resultaten of historische tests aangepast.

## Wat ligt vast

- 159 gedeelde eligible dagen, doorlopende point-in-time ATR/PDH/PDL en actieve same-clock volumehistorie.
- Alle vier vaste strategieën, post-entry R-bounds/tijden en de retrospectieve stabiliteitsaudit.
- **207 bestaande tests**, niet 196. Vier nieuwe integriteitscontroles geven 211 tests in deze release. Het aantal tests is geen bewijs van een trading edge.
- SHA-256 per historische rekenmodule, test, bronmanifest, protocol en onderzoeksuitvoer in `research/vnext-freeze-manifest.json`. Ruwe bronhashes staan al in het bevroren holdout-protocol; raw CSV's en individuele trades blijven privé.
- `npm run verify:freeze` controleert offline exact dezelfde bytes, zonder backtest of raw data. CI voert deze controle en alle tests uit. Dit is een wijzigingsdetector, geen technisch onwijzigbare Git-branch of ondertekend archief; de historische commit blijft de onafhankelijke referentie. Nieuwe logica krijgt een nieuwe module/versie en aparte outputs, nooit een overschreven baseline.

| Model | Eligible | Trades | Netto punten |
|---|---:|---:|---:|
| London Sweep | 159 | 82 | +175,550 |
| ORB5 | 159 | 147 | −402,075 |
| ORB15 | 159 | 143 | +1083,575 |
| VWAP Extreme | 159 | 63 | +95,825 |

Dit zijn afzonderlijke modellen, geen portefeuille. ORB15 april–september blijft −272,550 punten in vNext. Geen onafhankelijke bevestiging. De v0.9 holdout blijft −627,600 en `HOLDOUT_FAILED`.

## Exacte definities en toekomstige test

De machineleesbare, vastgelegde definitie staat in `research/vnext-future-oos-protocol.json` en als download in het dashboard. Hierin staan signalvensters, grenzen, stops/targets, fills, kosten, eligibility, history, rollover, spreadbeschikbaarheid, rapportage en besluitvorming expliciet.

Kosten blijven **$24,50 per roundtrip** voor één NQ: 2 ticks slippage per kant plus $4,50 commissie, totaal 1,225 punt. Raw fill-P&L minus één vaste kostenpost, geen dubbele slippage.

Historische activaties: 19 maart, 17 juni en 17 september 2025. Nieuwe activaties volgen uitsluitend de eerste boundary-gekwalificeerde volumedominantie van het inkomende kwartaalcontract over het uitgaande, switch volgende verwachte open sessie om 18:00 NY. Bij onvoldoende overlap geen geraden roll. Laatste gezamenlijke voltooide 15:59 NY-close vóór activatie bepaalt Panama-spread. Alleen toen bekende offsets tellen; geen toekomstige revisies. Volumemediaan: maximaal 20 eerdere observaties op dezelfde NY-minuut, minimum 10, alleen actieve contracten. Openings-RVOL14 blijft een andere beschrijvende maatstaf.

Vast toekomstig testvenster: **1 oktober 2025–30 september 2026**. Nog niet getest. Datum-aanwezigheid of eerdere kwaliteitsinspectie bewijst geen onafhankelijkheid: vóór scoring moet eerdere strategie-analyse worden uitgesloten. Bij besmetting status `CONTAMINATED`; eerst een ander ongebruikt venster registreren, niet stilzwijgend dit venster als blind presenteren.

ORB15 is de enige primaire hypothese. Ongewijzigde numerieke criteria uit het eerdere holdout-protocol: minstens 20 eligible dagen, netto >0, PF >1, tweezijdige centered block-bootstrap p<0,05 én ondergrens van het 95%-daggemiddelde-interval >0. Alle voorwaarden moeten op de volledige nieuwe periode gelden. 20 dagen is slechts de rekenkundige ondergrens, geen steekproefgroottegarantie of reden om te stoppen zodra 20 gunstige dagen zijn bereikt. Er is geen nieuw achteraf gekozen drawdown- of concentratiecriterium toegevoegd.

Inferentie: 2000 circulaire replicaties, bloklengte 5 eligible dagen, seed 20261020, nultrade-dagen inbegrepen. Eén primaire toets; referenties en uitsplitsingen uitsluitend beschrijvend. Gecombineerde oude/nieuwe P&L mag een falende OOS niet redden. Geen interim P&L, optimalisatie, richtingfilter of exitwijzigingen. Regels blijven staan ook bij een negatief resultaat.

Eerst volledigheid, kalender, tijdzone/DST, overlap, licentie en contaminatie beoordelen, bron-/kalender-/roll-ledgers vastleggen; dan pas één vaste evaluatie. De huidige runners blijven bewust tot september 2025 begrensd. Een toekomstige datum-/contractadapter is nog nodig en moet hashbewaking en historische pariteit behouden. Deze release voert geen toekomstige backtest uit en claimt die adapter niet af te hebben.

## Herhalen

`npm run verify:freeze` — byte-integriteit, geen signalen.

`python -m pytest -q` — unit/regressietests, geen nieuwe holdout.

Historische reproductiecommando's (`verify:research`, `verify:holdout`, `verify:continuous`, `research:volume-path`, `research:volume-stability`) blijven beschikbaar met lokale privé-inputs. In deze freeze-run zijn onderzoeksresultaten niet opnieuw berekend of vervangen.
