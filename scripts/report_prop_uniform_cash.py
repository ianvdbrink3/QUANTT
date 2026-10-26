"""Export existing aggregate cash receipts and fees; no strategy/account replay."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=ROOT/'artifacts/prop-uniform/run1/summary.json'
    rows=json.loads(p.read_text())
    text='''# Ontvangen payouts en netto cash — 26 oktober 2026

Alle bedragen zijn gemiddelden per gestart account, na winstdeling waar het om
ontvangen cash gaat. Geen onopgenomen equity als inkomen. Dezelfde 669 overlappende
jaarvensters (498 oud, 171 recent). Geen onafhankelijke validatie. De officiële
Builder Sim-fase kent maximaal vijf payouts: ONBEKEND betekent dat verdere Live-
kasstromen niet zijn ingevuld. De aparte CONTINUED_SIM_COUNTERFACTUAL is hypothetisch.

| Route | Model | Profiel | Periode | Ontvangen $ eerste 2 | Ontvangen $ heel venster | Betaalde accountkosten $ | Netto $ eerste 2 | Netto $ jaar | Livefase onbekend |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
'''
    for r in rows:
        assert abs(r['mean_received_first_two_USD']-r['mean_fees_accrued_USD']-r['mean_net_first_two_USD'])<1e-7
        assert abs(r['mean_received_full_window_observed_USD']-r['mean_fees_accrued_USD']-r['mean_net_cash_accrued_until_known_stop_USD'])<1e-7
        n=r['mean_net_full_window_USD']
        text+=(f"| {r['firm']} | {r['model']} | {r['profile']} | {r['era']} "
           f"| {r['mean_received_first_two_USD']:.2f} | {r['mean_received_full_window_observed_USD']:.2f} "
           f"| {r['mean_fees_accrued_USD']:.2f} | {r['mean_net_first_two_USD']:.2f} "
           f"| {'ONBEKEND' if n is None else f'{n:.2f}'} | {r['live_transition_unmodeled']} |\n")
    text+='\nAccountkosten omvatten aankoop, evaluatie-abonnementen en activatie; handelsfrictie is al in het accountsaldo verwerkt. Geen dubbele aftrek, resets, belastingen, FX-, API- of transferkosten.\n'
    text+='\nBron-SHA-256: `'+hashlib.sha256(p.read_bytes()).hexdigest()+'`.\n'
    for name in ('docs/PROP_UNIFORM_CASH_DETAILS_2026-10-26.md','public/reports/PROP_UNIFORM_CASH_DETAILS_2026-10-26.md'):
        (ROOT/name).write_text(text)
    print('Uniform cash receipts reconciled and exported')


if __name__=='__main__':main()
