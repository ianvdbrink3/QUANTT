"""Describe existing challenge candidates; never generate signals or resize trades.

Run: .venv/bin/python -m scripts.audit_prop_components
Private inputs remain in artifacts/. Only aggregate statistics are exported.
"""
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ('J0830', 'JBULL0930', 'J1M_TIME', 'PULLBACK', 'ICT1', 'SB_AM', 'SB_PM')
COSTS = (3.22, 6.50)  # MNQ roundtrip assumptions, not verified broker quotes
SOURCES = {
    'Topstep evaluation': 'https://help.topstep.com/en/articles/8284197-trading-combine-parameters',
    'Topstep payouts': 'https://help.topstep.com/en/articles/8284233-topstep-payout-policy',
    'MFFU Builder': 'https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide',
}


def profit_factor(values):
    gain = sum(max(0, v) for v in values)
    loss = -sum(min(0, v) for v in values)
    return gain / loss if loss else None


def aggregate(trades, calendar, component, cost):
    selected = [t for t in trades if t['component'] == component and t['filled']]
    if any(t.get('unknown') or not t.get('risk') or t['risk'] <= 0 for t in selected):
        raise ValueError('RTH component must have a resolved path and positive initial stop')
    if any(t['day'] not in calendar for t in selected):
        raise ValueError('Trade outside source calendar')
    dollars = [2 * t['gross'] - cost for t in selected]
    risk_r = [p / (2 * t['risk']) for p, t in zip(dollars, selected)]
    duration = [t['release'] - int(datetime.fromisoformat(t['entry_time']).timestamp() // 60)
                for t in selected]
    return dict(component=component, cash_days=len(calendar), trades=len(selected),
                trades_per_21_sessions=len(selected) * 21 / len(calendar),
                assumed_MNQ_RT_USD=cost, mean_net_USD_1MNQ=mean(dollars) if dollars else None,
                profit_factor_USD=profit_factor(dollars),
                mean_net_initial_stop_R=mean(risk_r) if risk_r else None,
                profit_factor_initial_stop_R=profit_factor(risk_r),
                winrate=mean(p > 0 for p in dollars) if dollars else None,
                median_holding_minutes=median(duration) if duration else None)


def render(rows, hashes):
    text = '''# Prop-firm geschiktheid: bouwstenenaudit — 25 oktober 2026

Status: ONTWIKKELINGSONDERZOEK; GEEN GEVALIDEERD PROP-MODEL.

Deze audit hergroepeert uitsluitend bestaande, gevulde intraday-kandidaten uit de
gepubliceerde challenge-run. Geen nieuwe signalen, parameters, stops of targets.
De eerdere challenge-resultaten en de S1/S2-benchmarks blijven ongewijzigd.

## Gemeten bouwstenen

Eén MNQ wordt benaderd met NQ-prijzen, $2 per punt. $3,22 roundtrip omvat het
bestaande commissie-/slippage-rekenmodel; $6,50 is een kostenscenario. Geen van beide
is een gecontroleerde persoonlijke brokerquote. Initial-stop-R = netto dollars /
(oorspronkelijke stopafstand in punten × $2). Dit is geen uitgevoerde position-sizing
met gehele contracten en geen garantie dat een stop tegen de stopprijs wordt gevuld.

Elke rij is zelfstandig gemeten: overlappende kandidaten kunnen niet zomaar worden
opgeteld. Handelsfrequentie is een gemiddelde per 21 cashsessies, geen maandgarantie.
De eerste periode bevat 749 cashsessies; de tweede 422 (feitelijk vanaf 27 januari
2025, ondanks de bestaande bronlabelnaam 2024_2026). De gecombineerde pool is al
bekeken en geselecteerd; positieve cijfers vormen geen onafhankelijke bevestiging.

| Bouwsteen | Periode | N | Trades/21 | Gem. netto $/MNQ | PF $ | Gem. netto stop-R | PF stop-R | Mediaan duur (min) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
'''
    for r in rows:
        if r['assumed_MNQ_RT_USD'] != 3.22:
            continue
        text += (f"| {r['component']} | {r['era']} | {r['trades']} | {r['trades_per_21_sessions']:.2f} "
                 f"| {r['mean_net_USD_1MNQ']:.2f} | {r['profit_factor_USD']:.3f} "
                 f"| {r['mean_net_initial_stop_R']:.3f} | {r['profit_factor_initial_stop_R']:.3f} "
                 f"| {r['median_holding_minutes']:.1f} |\n")
    text += '''
## Kostengevoeligheid: gemiddeld netto dollarresultaat per 1 MNQ

| Bouwsteen | Periode | Bij $3,22 RT | Bij $6,50 RT |
|---|---|---:|---:|
'''
    for r in rows:
        if r['assumed_MNQ_RT_USD'] != 3.22:
            continue
        stress = next(s for s in rows if s['component'] == r['component'] and
                      s['era'] == r['era'] and s['assumed_MNQ_RT_USD'] == 6.50)
        text += (f"| {r['component']} | {r['era']} | {r['mean_net_USD_1MNQ']:.2f} "
                 f"| {stress['mean_net_USD_1MNQ']:.2f} |\n")
    text += '''
## Wat dit betekent

1. De na-10:15 Pullback is in beide perioden netto negatief. De late ICT1 is in
   dollars licht positief, maar negatief in initial-stop-R in beide perioden.
   Ze leveren dus geen aangetoonde risicogenormaliseerde verbetering door ze aan
   Judas toe te voegen. Dit verandert de oorspronkelijke, onbeperkte Pullback niet.
2. Judas heeft circa 1–2 trades per 21 sessies per variant. De gehouden posities
   duren mediaan meerdere uren. Een ochtend-entry betekent geen vrijgevallen
   account voor een tweede ochtend-/middagstrategie. Variantentellingen optellen
   overschat uitvoerbaar volume.
3. SB_PM houdt korter vast, maar heeft circa 2–3 trades per 21 sessies en een kleine
   opbrengst per micro. Het is geen aangetoonde oplossing voor een maandchallenge.
4. De bestaande rolling-studie vond geen combinatie met minstens 10% bekende
   21-sessies-pass-rate in beide perioden. Die grens was een onderzoeksscreen,
   geen bewijscriterium voor toekomstige winst. Ontbrekende overnight-paden en
   achteraf geselecteerde combinaties begrenzen de uitspraken verder.

## Juiste doel: van evaluatie tot uitbetaling

Regels gecontroleerd op 25 oktober 2026; exacte plan en accountfase moeten steeds
apart worden vastgelegd. De eerdere MFFU-simulatie betreft Rapid EOD, niet Builder.

- Topstep Combine 50K: 55% consistency en maximaal 50 micros; de evaluatiewinst
  gaat niet mee naar Express Funded. Automatisering is onder voorwaarden toegestaan.
- Topstep Express: Standard vereist vijf winstdagen van minstens $150 voor payout;
  Consistency drie handelsdagen en 40% consistency. Na een uitbetaling staat de
  verliesvloer permanent op nul. Daarom is pass-rate alleen geen passend einddoel.
- MFFU Builder Default 50K: $3.000 target, $2.000 EOD-verliesvloer, $1.000 dagelijkse
  soft pause en geen consistency in de evaluatie. Sim Funded heeft wél 7 kalenderdagen
  inactiviteitslimiet en 50% payout-consistency. Voor de eerste payout is minimaal
  $2.600 nodig: $2.100 buffer plus $500. De eerdere Rapid EOD-pass-rates mogen niet
  als Builder-resultaten worden gepresenteerd.

Een doel van $3.000 vereist rekenkundig gemiddeld $150 netto bij 20 trades, of $100
bij 30 trades. Dat zijn schaalreferenties, geen vereiste of voorspelling per trade:
variantie, volgorde, trailing floor en consistency bepalen de feitelijke slaagkans.
Meer contracten verhogen zowel opbrengst als het verliesrisico.

## Afgebakend vervolgonderzoek

Onderzoek één intraday-kandidaat met volledige bronpaden en begrensd initiëel risico,
met vooraf vastgelegde regels en een bekende economische reden voor de entry.
Geen nieuwe brede combinatie-/sizingzoektocht en geen verplichte trades voor volume
of inactiviteit. Kies niet achteraf een stop op basis van de beste challenge-score.

Voeg eerst een plan-specifieke levenscyclus toe aan de bestaande meetlat: evaluatie,
nieuw funded beginsaldo, payout-eisen, uitbetaling, resterende verliesbuffer en
overleving daarna. Rapporteer kans op eerste én tweede payout vóór breach, dagen
tot payout en netto ontvangen dollars na evaluatie-, reset- en activatiekosten.
Gebruik geen andere regels om oude resultaten gunstiger te labelen.

Een definitieve kandidaat moet daarna op ongebruikte data of forward paper worden
gemeten met vooraf vastgelegde looptijd/steekproef en faalcriteria. Schijnbaar
gunstige resultaten op deze ontwikkelingspool zijn onvoldoende voor aankoop of
livehandel. Er is in deze audit geen nieuw model gevalideerd en geen account gekocht.

## Bronnen en reproduceerbaarheid

Uitvoeren: `.venv/bin/python -m scripts.audit_prop_components`.
Private kandidaat- en kalenderbestanden worden niet naar publieke output gekopieerd.
De CSV bevat uitsluitend aggregaten. Geen nieuw inferentieel bewijs of p-waarde
uit een achteraf geselecteerde groep; dit is een beschrijvende audit.

'''
    for label, url in SOURCES.items():
        text += f'- [{label}]({url})\n'
    text += '\nBronhashes SHA-256:\n\n'
    for name, sha in hashes.items():
        text += f'- `{name}`: `{sha}`\n'
    return text


def main():
    from scripts.prop_challenge.__main__ import verify
    proof = verify()
    inputs = [ROOT / 'artifacts/prop-challenge/run1' / f for f in
              ('candidates.json', 'cash-calendar.json')]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    candidates, calendar = [json.loads(p.read_text()) for p in inputs]
    rows = []
    for era, days in calendar.items():
        trades = [t for day in candidates[era].values() for t in day]
        for component in COMPONENTS:
            for cost in COSTS:
                rows.append(dict(era=era, **aggregate(trades, days, component, cost)))
    out = ROOT / 'artifacts/prop-component-audit'
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'aggregates.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / 'docs/PROP_MODEL_SUITABILITY_AUDIT_2026-10-25.md').write_text(render(rows, hashes))
    (out / 'verification.json').write_text(json.dumps(dict(
        status='EXISTING_CANDIDATES_DESCRIPTIVE_AUDIT_ONLY', sources=hashes,
        frozen_verification=proof, aggregate_rows=len(rows)), sort_keys=True, indent=2) + '\n')
    print(json.dumps(dict(status='AUDIT_WRITTEN', rows=len(rows), frozen=proof)))


if __name__ == '__main__':
    main()
