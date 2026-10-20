# QUANT 0.9 — Productie-audit, 20 oktober 2026

**Status:** historische, exploratieve NQ-studie. Geen gevalideerde edge. De gepubliceerde afgeleide JSON-bestanden zijn de bron voor deze audit; originele Barchart CSV-bestanden ontbreken in GitHub.

## Data, herkomst en kwaliteit

- 106.678 1m bars van 30 december 2024 t/m 17 april 2025; 78 handelsdagen.
- NQH25 / NQM25; geen ES in de gepubliceerde studie.
- 67 schone dagen; 11 gemarkeerd (8 met missing minutes, 3 met special sessions).
- Totaal 32 ontbrekende minuten in de onderzochte sessies. De aparte raw importer vermeldt 85 contractgaten; dit is een andere, niet kalendergecorrigeerde definitie.
- ATR-ready 47 dagen; eligible 42 dagen.
- Roll op 19 maart 2025 volgens rapport. Onafhankelijke CME-kalender, roll-beslisgegevens, vendorlicentie en oorspronkelijke CSV-hashes niet geverifieerd.
- Publieke research09.json en nq-overnight.json tellen beide 106.678 bars en delen dezelfde run-ID.

## Strategieën (hypothetisch; een NQ-contract, $20/punt, $24,50 roundtrip)

| Screen | Trades | Netto punten | Netto USD | Profit factor | Nominale p | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| London sweep | 18 | +236,20 | +4.724 | 1,224 | 0,722 | 1,000 |
| ORB5 | 38 | +34,20 | +684 | 1,016 | 0,962 | 1,000 |
| ORB15 | 37 | +919,43 | +18.389 | 1,558 | 0,188 | 0,752 |
| VWAP Extreme | 19 | +82,98 | +1.660 | 1,128 | 0,836 | 1,000 |

**ORB15:** kandidaat voor verder onderzoek, geen edge. Eerste helft +183,95 punten, tweede +735,48; dubbele slippage +882,43; zonder beste trade +542,90; zonder drie beste trades slechts +49,10. De bootstrapinterval over eligible days [-8,10; +55,13] kruist nul. Gepaard directioneel controle-p ~0,152.

**London sweep:** eerste helft +406,95, tweede -170,75; zonder beste trade -35,33. **ORB5:** dubbele slippage verandert +34,20 naar -3,80; zonder beste trade -342,33. **VWAP extreme:** eerste helft -183,03, tweede +266,00; zonder beste trade -131,05. Geen van deze methoden toont robuuste, onafhankelijke positieve expectancy aan.

### Aanvullende marktinzichten

- Onvoorwaardelijke NQ 09:30 ET long baseline (n=77): gemiddeld -6,48/-5,61/-16,86/-26,86 netto punten over 15m/30m/60m/tot noon. Descriptief, geen onafhankelijk gerandomiseerde baseline.
- Overnight range t.o.v. ATR, 60m: broad n=3, +145,36 punten, 66,7% positief; middle n=21, -22,75; narrow n=18, -35,64. Broad n=3 is niet geschikt voor betrouwbare gevolgtrekkingen.
- Release09 descriptieve forward evenementen (geen dezelfde strategie-exits): London high sweep n=67: +8,11/+2,39/+1,66 punten; NY ORB n=58: +4,45/+15,72/+21,62; VWAP fade n=117/116/116: -4,17/-4,62/-7,03 (15/30/60m). Niet met de gesimuleerde netto-strategie-P&L verwarren.
- Geen onafhankelijke sealed holdout, geen broker fills en geen onafhankelijke CME-source attestation; 42 geschikte handelsdagen zijn een kleine evaluatiesteekproef.

## Synchronisatie tussen Git en productie

De productie-deployment dpl_4Bjx4cou4Um8qci876pCwua48wMt is gebouwd via een lokale Vercel CLI-bron (dpl_BMCG4wUf4YwsgcchBBzhwdqazLnw); deze kwam niet overeen met de GitHub default branch. De synchronisatie brengt twee **reeds publiek beschikbare afgeleide** JSON-rapporten en de bijbehorende NQ-weergave naar Git bovenop PR #11. Geen ruwe Barchart-futuresminuten of private CSV/Parquet, uitvoeringstrades of credentials gaan Git in.

Een nieuwe offline guard in scripts/verify_observed_snapshots.py controleert run-ID, aantallen, flags, hypothetische USD/punt-P&L, deelperiodes en expliciete edge=false / source=unverified. CI voert deze controle uit. Vergelijk na een productiebuild de exacte publieke bestandsbytes:

    python scripts/verify_observed_snapshots.py --base-url https://quantt-eight.vercel.app

De originele generator van het grote overnightstrategierapport is **nog niet** volledig vanuit Git reproduceerbaar. Daarvoor is de oorspronkelijke Work-code plus ruwe brondata nodig. De release creëert broncodepariteit voor de frontend en gecommitte snapshots, geen ongefundeerde wetenschappelijke certificering. Gebruik voortaan bij voorkeur alleen gereviewde Git main-commits voor productie in plaats van niet-herleidbare lokale Vercel CLI-overrides.
