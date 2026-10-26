"""Descriptive tables only; consume the locked, already-reproduced outcomes."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def main():
    path=ROOT/'artifacts/prop-lifecycle/run1/summary.json'
    rows=json.loads(path.read_text())
    text='''# Levenscyclus: netto cash en interpretatie — 26 oktober 2026

Deze tabellen horen bij PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md. Alle regels,
kosten, payout-beleid en de 252-sessiehorizon zijn vóór de accountreplay vastgelegd.
Geen nieuwe kandidaat is toegevoegd: Judas blijft de enige intraday-motor.

## Netto dollars per gestart account: beide perioden afzonderlijk

De band hieronder is een wiskundige identificatiegrens, GEEN 95%-interval en GEEN
geschatte waarschijnlijkheidsverdeling. Bekende paden gebruiken hun werkelijke cash
tot tweede payout/jaargrens/falen. Bij een onopgelost bronpad is de ondergrens:
reeds ontvangen cash minus maximaal mogelijke abonnementen/activatie binnen het
venster. De bovengrens voegt maximaal twee toegestane payouts toe minus al betaalde
fees. De bovengrens is nadrukkelijk geen aannemelijk best-case rendement.

Daarmee hoeft geen winst of verlies voor ontbrekende minuten te worden verzonnen.
Een positieve ondergrens geldt alleen voor deze historische jaarcohorten, dit
payout-beleid en de modelaannames; geen bewijs van toekomstige winstgevendheid.
De all-start puntverwachting is ONBEKEND zolang bronpaden onopgelost zijn. Het
gemiddelde van alleen opgeloste accounts is selectief en vervangt die niet.

| Route | Model | MNQ | Periode | Starts | Passes | Payout1 | Payout2 | Onbekende paden | Netto $/start: ondergrens | Bovengrens |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
'''
    for r in rows:
        if r['horizon']!='252_SESSIONS' or 'SENSITIVITY' in r['firm']:
            continue
        n=r['starts'];lo,hi=r['partial_identification_cash_bounds_USD']
        text+=(f"| {r['firm']} | {r['model']} | {r['MNQ']} | {r['era']} | {n} "
               f"| {r['known_evaluation_passes']} | {round(r['payout1_all_starts']*n)} "
               f"| {round(r['payout2_all_starts']*n)} | {round(r['unknown_rate']*n)} "
               f"| {lo:.2f} | {hi:.2f} |\n")
    text+='''
## Onderzoeksconclusie

De huidige bronnen rechtvaardigen geen algemeen winstgevend prop-model in beide
perioden. In de 252-sessievergelijking zijn er bij Topstep Standard wel eerste
payouts, maar geen tweede bekende payouts. De aparte Consistency-route kent bij
S1-Judas-0830 op 2 MNQ wel twee payouts; die starts liggen in het recente blok.
Deze route is vooraf als aparte vergelijking vastgelegd en vervangt Standard niet
achteraf als hoofdroute.

Het recente S1-blok op 2 MNQ heeft zelfs bij de conservatieve ontbrekende-padgrenzen
een positief cashresultaat voor Topstep Standard. Dat is een waargenomen plaatselijk
resultaat. Het oudere blok bevat te veel onopgeloste nachtpaden om dezelfde conclusie
te trekken. Een nul bekende evaluatiepasses daar is geen bewijs van nul werkelijke
slaagkans. Overlappende starts geven geen onafhankelijke replicaties.

Builder heeft voor de selectieve kernen geen bekende pass of payout. De meeste
bekende afsluitingen komen door de conservatief toegepaste zeven-kalenderdagenregel,
niet door verliesvloer. De aanvullende officiële policy zegt 'could be closed';
dit is een model van sluiting, geen zekerheid over discretionaire handhaving.
De los gerapporteerde variant zonder eval-inactiviteit helpt oorzaken scheiden,
maar verandert niets aan de officiële funded-inactiviteitslimiet.

Geen extra setup, contractopschaling of keep-alive is gebruikt om een gewenste
uitkomst af te dwingen. Een nieuw intraday-model is niet nodig om de conclusie
van deze afgebakende opdracht te beantwoorden. S1/S2 en eerdere studies blijven
als benchmarks intact; deze simulatie is geen live-handelvrijgave.

## Bestanden en controle

- Volledige regels/tabellen: `docs/PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md`.
- Alle 144 aggregaten: `public/data/prop-lifecycle/summary.csv` en `summary.json`.
- Iedere accountstart, tijd tot pass, fees en milestones: privé in
  `artifacts/prop-lifecycle/run1/accounts.csv` en `accounts.json.gz`.
- Hashbewijs dubbele accountreplay: `research/prop-lifecycle-verification.json`.
- Nieuwe dashboardroute: `/research/prop-lifecycle`; alleen aggregaten zijn publiek.

Gebruikte resultaat-SHA-256: `'''+hashlib.sha256(path.read_bytes()).hexdigest()+'`.\n'
    for p in (ROOT/'docs/PROP_ACCOUNT_LIFECYCLE_FINDINGS_2026-10-26.md',
              ROOT/'public/reports/PROP_ACCOUNT_LIFECYCLE_FINDINGS_2026-10-26.md'):
        p.write_text(text)
    print('CASH_IDENTIFICATION_TABLES_WRITTEN')


if __name__=='__main__':
    main()
