"""Deterministic aggregate publication from BOTH independently rebuilt outputs."""
import json
from pathlib import Path

import pandas as pd

from scripts.year_holdout import ROOT,OUTPUT,STRATEGIES,compare_runs,preflight
from scripts.oos_preparation.adapter import sha
from scripts.oos_preparation.year import dump
from scripts.verify_research_freeze import verify

LABELS={'B_ORB15':'ORB15 (primair)','B_ORB5':'ORB5 (referentie)',
        'A_London_sweep':'London Sweep (referentie)','C_VWAP_extreme':'VWAP Extreme (referentie)'}


def fmt(value,decimals=3):
    return 'n.v.t.' if value is None else f'{value:,.{decimals}f}'.replace(',','#').replace('.',',').replace('#','.')


def rate(value):
    return 'n.v.t.' if value is None else fmt(value*100,1)+'%'


def pf(metrics):
    return '∞ (geen verlies)' if metrics['profit_factor_no_losses'] else fmt(metrics['profit_factor'])


def render(summary):
    lines=['# Jaar-holdout ORB15 — vaste regels, één primaire hypothese','',
        f"**Formeel oordeel: {summary['status']}.** Alleen ORB15, all-view, over 1 oktober 2025–30 september 2026 bepaalt dit oordeel. Geen parameterwijzigingen. De jaar-holdout is nu verbruikt.",'',
        'Baseline v0.9 en de vNext159-onderzoeksstand blijven ongewijzigd. Gecombineerde historie en referenties zijn uitsluitend beschrijvend. Een positief resultaat is geen toestemming voor live handelen.','',
        '## Primaire vooraf vastgelegde criteria','',
        '| Criterium | Gehaald |','|---|---|']
    for name,value in summary['primary_checks'].items():lines.append(f"| {name} | {'Ja' if value else 'Nee'} |")
    lines += ['', 'Alle vijf criteria moeten slagen: ≥20 eligible dagen, netto >0, PF >1, tweezijdige block-bootstrap-p <0,05 en de ondergrens van het 95%-interval van het gemiddelde dagresultaat >0. Geen vervanging door gecombineerd resultaat of beste referentie.','']
    metric_rows=[('Eligible dagen','eligible_days'),('Trades','trades'),('Netto NQ-punten','net_points'),('Netto USD','net_usd'),
        ('Profit factor','profit_factor'),('Maximale gesloten-trade drawdown (punten)','max_drawdown_points'),
        ('Maximale gesloten-trade drawdown (USD)','max_drawdown_usd'),('Grootste verliesdag (punten)','worst_day_points'),
        ('Grootste verliesdag (USD)','worst_day_usd'),('Top3 netto punten','best3_net_points'),
        ('Top3 / totale netto winst (%)','best3_share_net_profit_pct'),('Netto zonder top3 (punten)','net_points_without_best3'),
        ('95%CI gemiddeld netto punten/eligible dag: laag','ci_low'),('95%CI gemiddeld netto punten/eligible dag: hoog','ci_high'),
        ('Tweezijdige p (nominaal)','p_value')]
    for period,title in [('year','Jaar-holdout: 1 oktober 2025–30 september 2026'),('combined','Gecombineerd: 30 december 2024–30 september 2026 (beschrijvend)')]:
        values=summary['results'][period]
        lines += ['## '+title,'','| Maatstaf | ORB15 primair | ORB5 referentie | London referentie | VWAP referentie |','|---|---:|---:|---:|---:|']
        order=['B_ORB15','B_ORB5','A_London_sweep','C_VWAP_extreme']
        for label,key in metric_rows:lines.append('| '+label+' | '+' | '.join(pf(values[s]['metrics']) if key=='profit_factor' else fmt(values[s]['metrics'][key],6 if key=='p_value' else 0 if key in ['eligible_days','trades'] else 3) for s in order)+' |')
        lines += ['| Winrate | '+' | '.join(rate(values[s]['metrics']['win_rate']) for s in order)+' |',
                  '| Datum grootste verliesdag | '+' | '.join(str(values[s]['metrics']['worst_day']) for s in order)+' |',
                  '| p na Holm, aanvullende familie8 | '+' | '.join(fmt(values[s]['metrics'].get('p_holm_nonprimary_family8'),6) for s in order)+' |','',
                  'Top3-aandeel is niet gedefinieerd bij nettoverlies of netto nul. Een aandeel boven100% wordt niet afgekapt. Grootste verliesdag is het minimum over alle eligible dagen inclusief nultrade-dagen. Drawdown gebruikt gerealiseerde gesloten trades met startwaarde0, niet intratrade mark-to-market.','',
                  '### Maandverdeling','',
                  '| Model | Maand | Eligible | Trades | Netto punten | Netto USD | Winrate | PF |','|---|---|---:|---:|---:|---:|---:|---:|']
        for s in order:
            for m in values[s]['monthly']:
                lines.append(f"| {LABELS[s]} | {m['month']} | {m['eligible_days']} | {m['trades']} | {fmt(m['net_points'])} | {fmt(m['net_usd'],2)} | {rate(m['win_rate'])} | {pf(m)} |")
        lines += ['', '### Long versus short','',
                  '| Model | Richting | Trades | Netto punten | Netto USD | Winrate | PF | Gemiddelde trade |','|---|---|---:|---:|---:|---:|---:|---:|']
        for s in order:
            for direction,m in values[s]['direction'].items():
                lines.append(f"| {LABELS[s]} | {direction} | {m['trades']} | {fmt(m['net_points'])} | {fmt(m['net_usd'],2)} | {rate(m['win_rate'])} | {pf(m)} | {fmt(m['mean_trade_points'])} |")
        lines += ['', '### MFE/MAE-verdelingen','',
                  '| Model | Maatstaf | n | P05 | P25 | Mediaan | P75 | P95 |','|---|---|---:|---:|---:|---:|---:|---:|']
        for s in order:
            for name,q in values[s]['excursions'].items():
                lines.append(f"| {LABELS[s]} | {name} | {q['n']} | "+' | '.join(fmt(q[k]) for k in ['p05','p25','median','p75','p95'])+' |')
        lines += ['', 'MFE/MAE zijn intrabar-identificatiegrenzen, geen exacte tickvolgorde. Lower gebruikt voltooide eerdere bars plus de fill; upper gebruikt de exitbar binnen de vaste stop-/targetbarrières. Bij tijdexit is de laatste volledige minuut bekend.1R=afstand entry tot initiële stop vóór kosten. Tijd tot eerste bar-extreem is in minuten en kan binnen de exitminuut na de fill liggen.','',
                  '### Kosten-gevoeligheid, onveranderde fills','',
                  '| Model | USD roundtrip | Netto punten | Netto USD | Winrate | PF | Max drawdown punten |','|---|---:|---:|---:|---:|---:|---:|']
        for s in order:
            for m in values[s]['cost_sensitivity']:
                lines.append(f"| {LABELS[s]} | {fmt(m['cost_rt_usd'],2)} | {fmt(m['net_points'])} | {fmt(m['net_usd'],2)} | {rate(m['win_rate'])} | {pf(m)} | {fmt(m['max_drawdown_points'])} |")
        lines += ['', '### Clean-sensitiviteit (niet beslissend)','',
                  '| Model | Eligible | Trades | Netto punten | PF |','|---|---:|---:|---:|---:|']
        for s in order:
            m=values[s]['clean_sensitivity']
            lines.append(f"| {LABELS[s]} | {m['eligible_days']} | {m['trades']} | {fmt(m['net_points'])} | {pf(m)} |")
        if period=='year':
            c=values['B_ORB15']['clean_sensitivity']
            lines += ['', f"ORB15 clean:95%CI gemiddeld dagresultaat [{fmt(c['ci_low'])},{fmt(c['ci_high'])}], nominaal p={fmt(c['p_value'],6)}, Holm8 p={fmt(c['p_holm_nonprimary_family8'],6)}. Dit vervangt de primaire all-view niet."]
        lines += ['']
    lines += ['## Inferentie en beperkingen','',
        'De vooraf vastgelegde2000 circular moving-block bootstrapreplicaties gebruiken blokken van5eligible sessies en seed20261020. Eligible dagen zonder trade tellen als0; niet-eligible kalenderdagen worden niet als fictieve0 toegevoegd. CI is nominaal95% voor gemiddelde netto punten per eligible dag. De p-waarde is tweezijdig, gecentreerd: (1+extreme replicaties)/2001. CI en p zijn niet noodzakelijk exacte inversen.','',
        summary['multiplicity'],'',
        'De acht aanvullende toetsen zijn vóór de eerste signaalrun in de vrijgave vastgelegd: drie jaarreferenties, vier gecombineerde reeksen en ORB15jaar-clean. Nominale intervallen zijn geen simultane intervallen. Maand-, richting-, kosten- en excursietabellen zijn beschrijvend, zonder nieuwe hypothesetoetsen.','',
        'Kosten:$24,50RT=2ticks per kant plus$4,50commissie. Stress:$44,50 en$64,50RT met identieke fills. Bij stop en target in dezelfde minuut geldt de stop; ongunstige gapstop wordt tegen de slechtere open uitgevoerd. Eén contract per model, geen samengevoegd portfolio of compounding.','',
        '## Reproductie en onveranderde historie','',
        'Twee afzonderlijke Python-processen laden alle69geregistreerde bronbestanden opnieuw. Geen gecachte features of tradeledger wordt gebruikt om signalen te genereren. De vooraf verankerde private historische ledger en eligibility-datums worden alleen als onafhankelijke controle gebruikt. Alle deterministische outputs worden byte voor byte vergeleken. Dit bewijst reproduceerbaarheid van dezelfde implementatie, niet een tweede onafhankelijk geschreven engine of nieuwe statistische replicatie.','',
        'De historische435trades en780eligibility-regels blijven byte-identiek; alle73bevroren bestanden en het volledige voorbereidingspakket blijven geldig. De onbekende leveranciersvintages, gebruiksrechten, beperkte eerdere-niet-gebruikbewijzen en gereconstrueerde kalender blijven als beperking bestaan. De gebruiker heeft uitvoering met deze vastgelegde beperkingen expliciet vrijgegeven.','',
        '### Commando’s','',
        '- Nieuwe gecontroleerde werkmap, na herstel van private geregistreerde bronnen en voorbereidingsledgers: `.venv/bin/python -B -m scripts.year_holdout --run first` en daarna `--run reproduction`.',
        '- Bestaande runs niet overschrijven: `.venv/bin/python -B -m scripts.year_holdout --compare`.',
        '- Alle69bronhashes, beide ledgers en publicatie opnieuw controleren zonder derde scoringrun: `node scripts/verify-year-holdout`.',
        '- Aggregaten uit beide runs reproduceren en vergelijken: `.venv/bin/python -B -m scripts.publish_year_holdout`.',
        '- `npm run verify:freeze`; `.venv/bin/python -B -m scripts.oos_preparation.seal --verify`; `.venv/bin/python -m pytest -q`.',
        '- Het vrijgavebestand staat in `research/year-holdout-release.json`; geen impliciete nieuwe vrijgave door een CLI-vlag. Eerste run en reproductie zijn per werkmap exclusief en worden niet overschreven.','',
        '**Deze jaarperiode is vanaf nu verbruikte onderzoeksdata. Geen nieuwe filters of parameters testen en dezelfde periode opnieuw als onafhankelijke holdout presenteren.**','']
    return '\n'.join(lines)


def export(summary,out):
    out.mkdir(parents=True,exist_ok=True)
    dump(out/'results.json',summary)
    (out/'REPORT.md').write_text(render(summary))
    tables={name:[] for name in ['metrics','monthly','direction','excursions','costs','monthly-equity']}
    for period,models in summary['results'].items():
        for s,r in models.items():
            base=dict(period=period,strategy=s)
            tables['metrics'].append(dict(base,**r['metrics']))
            for name,key in [('monthly','monthly'),('costs','cost_sensitivity'),('monthly-equity','monthly_equity')]:
                tables[name] += [dict(base,**row) for row in r[key]]
            tables['direction'] += [dict(base,direction=d,**row) for d,row in r['direction'].items()]
            tables['excursions'] += [dict(base,measure=m,**q) for m,q in r['excursions'].items()]
    for name,rows in tables.items():pd.DataFrame(rows).to_csv(out/(name+'.csv'),index=False)


def main():
    preflight()
    evidence=compare_runs()
    a,b=OUTPUT/'first',OUTPUT/'reproduction'
    first=json.loads((a/'summary.json').read_text());second=json.loads((b/'summary.json').read_text())
    export(first,a/'publication');export(second,b/'publication')
    names=sorted(p.name for p in (a/'publication').iterdir())
    evidence['publication_files_sha256']={}
    for name in names:
        if (a/'publication'/name).read_bytes()!=(b/'publication'/name).read_bytes():raise ValueError('Publication byte mismatch: '+name)
        evidence['publication_files_sha256'][name]=sha(a/'publication'/name)
    for name in names:
        suffix={'results.json':'json','REPORT.md':'md'}.get(name,name)
        target=ROOT/'public/data'/('research-year-holdout.'+suffix)
        target.write_bytes((a/'publication'/name).read_bytes())
    dump(ROOT/'research/year-holdout-verification.json',evidence)
    dump(ROOT/'public/data/research-year-holdout-verification.json',evidence)
    (ROOT/'docs/YEAR_HOLDOUT_2026-10-21.md').write_text(render(first))
    verify()
    print(json.dumps(dict(status=first['status'],byte_identical_private_files=len(evidence['files_sha256']),
        byte_identical_publication_files=len(evidence['publication_files_sha256'])),indent=2))


if __name__=='__main__':main()
