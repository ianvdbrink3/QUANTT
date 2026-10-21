# OOS voorbereiden zonder strategie-uitkomsten

De bevroren Baseline v0.9 en vNext159 blijven byte-identiek. Het jaar 1 oktober 2025–30 september 2026 blijft ongescoord: geen kwartaaltest, interim-P&L of nieuwe signalen. Nieuwe code staat afzonderlijk in `scripts/oos_preparation`.

## Uitgevoerd

- Zes bestaande NQZ25-blokken zijn ongewijzigd naar de genegeerde lokale map `data/raw/oos/` gekopieerd. Een bestaande afwijkende kopie wordt nooit overschreven. Bronhashes, datumbereiken, eerdere toegang en kalenderhash zijn geregistreerd in `research/oos-source-register.json`. Ruwe OHLCV en individuele trades blijven privé.
- De quality-only adapter valideert schema, footer, contractnaam, OHLC, ticks, volume, tijdzone en conflicterende overlap. Gebruik van verschillende contracten wordt niet door timestamp-ontdubbeling vermengd. Geen minuten worden geïmputeerd.
- Kalender en bronverwijzingen zijn vastgelegd in `research/oos-calendar-register.json`: Thanksgiving, de gedocumenteerde storing en twee resterende minuten. De waargenomen storingsgrenzen zijn niet als officieel minuutcertificaat gepresenteerd. Datums ná 12 december worden geweigerd totdat NQ-specifieke uren zijn geverifieerd. Clearing-/settlement-/cashmarkturen zijn geen vervanging.
- Dezelfde brondata levert 72.028 unieke bars, 53 sessiedatums, 51 schone normale dagen en 52 volledige overnight–12:00-prefixen. Thanksgiving past bij het ongewijzigde all-filter, 28 november niet. Dit is géén actieve-contracttelling: zonder H26 kan de decemberroll niet worden bevestigd.
- Historische data-pariteit: alle 30 oorspronkelijke bronbestanden geven exact dezelfde OHLCV en sessiedatums als de bevroren importer; 301.299 ontdubbelde contractbars, nog vóór actieve selectie. Juni- en septembervolumeswitch en laatste gezamenlijke pre-roll RTH-close sluiten aan. Geen strategie of feature-engine is hiervoor uitgevoerd.
- Synthetische tests behandelen DST, kalenderblokkering, nachtelijke storing versus prefix-eis, identieke/conflicterende overlap, contractisolatie, immutable staging, volume-ties en toekomstige-mutatie-isolatie van rollbeslissingen.

De adapter bereidt uitsluitend brondata, datums, kalender en volume-roll-ledgers voor. De toekomstige strategie-integratie is bewust NIET vrijgegeven: geen evaluate/backtest-opdracht, geen toekomstige ATR/VWAP/entryberekening. Synthetische/gegevenspariteit is geen bewijs van volledige toekomstige strategiepariteit of correcte brokeruitvoering.

## Eerdere toegang en sluiting van de holdout

De bestanden waren niet ongezien: lokale consolidatie en kwaliteitsinspectie op 19 oktober 2026, daarna inventarisatie en quality-only controles. De zes hashes en bestaande consolidatie zijn gelijk gebleven. De onderzochte runners zijn begrensd tot 30 september; geen okt–dec strategie-ledger aangetroffen. Beschikbare lokale uitvoeringssporen zijn echter niet volledig: er is geen absolute verklaring van niet-gebruik afgegeven.

Deze scheiding is een programmatische veiligheidsgrens, geen versleuteling, OS-toegangsverbod of certificering van menselijke blindheid. De status blijft DATA_INSUFFICIENT, niet HOLDOUT_PASSED. Toekomstige scoring vereist apart expliciet besluit nadat bronnen, roll-ledgers, volledige kalender en onafhankelijkheid zijn beoordeeld. Geen alsnog gekozen gunstige deelperiode.

## Powerplanning op uitsluitend verbruikte data

De planning leest uitsluitend de op SHA-256 verankerde vNext159 trade- en eligibility-ledgers uit dec 2024–sep 2025. Eerst worden de datums gecontroleerd, daarna pas de historische P&L-kolom. Eligible nultrade-dagen blijven nul. Geen nieuwe strategie berekend; geen toekomstige P&L gelezen.

Vaste aannames: één tweezijdige 5%-toets, doelpower 80%, hypothetisch netto daggemiddelde 2,5 / 5 / 10 / 20 NQ-punten per eligible dag. Varianten voor de variantie-inflatie: 1 / 1,5 / 2. Deze scenariowaarden veranderen geen entry-, exit-, kosten- of slaagparameter. Daggemiddelde/spreiding en een vaste lag-4 Bartlett-HAC-diagnostiek komen alleen uit de reeds verbruikte historie. HAC selecteert niet de gunstigste scenarioruimte.

De historische dagspreiding is circa **94,035 punten**. Onder de eenvoudige onafhankelijkheidsbenadering:

| Veronderstelde werkelijke netto edge per eligible dag | Power bij 52 dagen | Power bij 240 dagen | Dagen voor circa 80% power |
|---|---:|---:|---:|
| 5 punten | 6,7% | 13,1% | 2777 |
| 10 punten | 12,0% | 37,7% | 695 |
| 20 punten | 33,5% | 90,9% | 174 |

Dit zijn normale benaderingen voor een gemiddelde, NIET de gemeten power van het bevroren gezamenlijke bootstrap-/CI-/PF-slaagcriterium. Staarten, regimeverandering en seriële afhankelijkheid kunnen de betrouwbaarheid verminderen. Ook een heel jaar geeft geen garantie op voldoende onderscheidend vermogen voor een bescheiden edge. Geen significante uitkomst kan dus gebrek aan bewijs betekenen; het protocol blijft desondanks ongewijzigd, en een onvoldoende resultaat mag geen promotie krijgen.

De bestaande vaste jaarhorizon wordt niet op basis van deze tabel verlengd of ingekort. Geen optioneel stoppen, nieuwe optimalisatie of gewijzigde criteria. Voor een latere onderzoeksgeneratie kan economische relevantie en steekproefomvang vooraf opnieuw worden ontworpen op werkelijk ongebruikte data.

Methodische bron: [NIST sample-size/power-formule](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm). Volledige scenariomatrix staat in de geaggregeerde dashboarddownload.

## Nog geblokkeerd

De ontbrekende H26/M26/U26/Z26-bestanden zijn NIET opgehaald. Safari-toegang liep vast; de publieke Barchart-route toont JS/robotverificatie. Er zijn geen wachtwoorden/cookies geëxtraheerd, geen verificaties omzeild en geen abonnement of API gekocht. Het concrete contract-/overlapplan staat in `research/oos-download-plan.json`. Hiervoor is een bestuurbare aangemelde browsersessie met downloadrechten of aanlevering van CSV's nodig.

Ook de volledige NQ-specifieke kalender na 12 december, leverancierlicentie/publicatievintages en onafhankelijke niet-gebruikbevestiging blijven open. Deze ontbrekende voorwaarden worden niet als afgerond gepresenteerd.

## Herhaalbare controles

- `npm run prepare:oos -- --stage-existing`: ongewijzigde lokale staging, kwaliteit en historische powerplanning. Geen signalen.
- `npm run verify:oos-data-parity`: uitsluitend historische importer-/roll-pariteit, lokale originele bronnen vereist.
- `python -m scripts.oos_preparation.export`: alleen geaggregeerde voorbereidingsstatus publiceren.
- `npm run verify:freeze`: alle 73 bevroren bestanden blijven gelijk.
- `python -m pytest -q`: bestaande tests plus nieuwe voorbereidende regressietests. CI heeft geen privédata nodig.
