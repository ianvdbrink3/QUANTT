"""Export registered precision results without resampling or recalculating paths."""
import json

import pandas as pd

from scripts.morning_recovery_precision import ROOT,OUT,verify,dump
from scripts.oos_preparation.adapter import sha


def f(value):
    return '—' if value is None else f'{value:.2f}'.replace('.',',')


def main():
    verification=verify()
    data=json.loads((OUT/'summary.json').read_text())
    bootstrap=data['block_bootstrap']
    intervals=[]
    for r,key in zip(data['intervals'],('mean_negative_ci95','difference_ci95')):
        intervals.append(dict(id=r['id'],estimate=r['estimate'],
            hac95_low=r['ci95'][0],hac95_high=r['ci95'][1],
            bootstrap95_low=bootstrap[key][0],bootstrap95_high=bootstrap[key][1],
            se_HAC5=r['se_HAC5'],se_CR1=r['se_CR1'],df=r['df'],event_days=r['event_days']))
    distribution=[dict(measure=name,**values) for name,values in data['excursions'].items()]
    dump(ROOT/'research/morning-recovery-precision-results.json',data)
    for name,rows in [('intervals',intervals),('quarters',data['quarters']),('excursions',distribution)]:
        pd.DataFrame(rows).to_csv(ROOT/f'research/morning-recovery-precision-{name}.csv',index=False,float_format='%.17g')
    labels={'MEAN_NEGATIVE29':'Gemiddelde29 doorzakkende Gap-Down-dagen',
        'NEGATIVE29_MINUS_POSITIVE40':'Verschil29 doorzakkend minus40 opverend'}
    lines=['# Precisie ochtendherstel:29 versus40 Gap-Down-dagen','',
        'Dit is een vooraf afzonderlijk vastgelegde precisie-uitbreiding op bestaande ontdekkingsdata, geen onafhankelijke validatie of nieuw handelsmodel. Alleen09:45 Open→10:29 Close wordt gemeten, bruto en opwaarts positief. De indeling gebruikt09:30 Open→09:44 Close. Geen eerste-kwartierbar of09:44close/open-gap zit in de uitkomst.','',
        '## 1. Twee gevraagde betrouwbaarheidsintervallen','',
        '| Grootheid | Schatting pt | HAC(5) nominaal95%-BI pt | Block-bootstrap nominaal95%-BI pt |',
        '|---|---:|---|---|']
    for r in intervals:
        lines.append('| '+' | '.join([labels[r['id']],f(r['estimate']),
            '['+f(r['hac95_low'])+'; '+f(r['hac95_high'])+']',
            '['+f(r['bootstrap95_low'])+'; '+f(r['bootstrap95_high'])+']'])+' |')
    lines += ['',
        'Het gemiddelde van de40 opverende dagen blijft +5,325 pt. Alle69 eerder berekende vervolgrendementen en de29/40-indeling zijn ongewijzigd.','',
        'Hoofdmethode: één invloedsscore per oorspronkelijke geplande handelsdag op de454-dagenkalender. Niet-geselecteerde dagen hebben nulinvloed, geen fictief nulrendement. Bartlett-HAC met lags1–5; geselecteerde-dagen-correctie29/28 voor het gemiddelde en69/68 voor het contrast; t-vrijheidsgraden28 voor beide. Contrastscores worden op dezelfde dagkalender afgetrokken om temporele covariantie te behouden. CR1-sensitiviteits-SE staat in JSON/CSV.','',
        'Gevoeligheidscontrole:20.000 circular moving-block bootstrapreplicaties van vijf geplande sessies, seed20261022. Hele dagrecords en groepsmaskers worden samen geresampled; beide conditionele gemiddelden worden per replicatie opnieuw berekend. Alle20.000 replicaties hebben beide groepen. De intervallen zijn percentielintervallen, geen studentized of simultane intervallen.','',
        '**Beide95%-intervallen zijn puntsgewijs en verkennend, niet gecorrigeerd voor de eerdere zoektocht of voor gezamenlijke dekking.** Kleine aantallen en regimestructuur kunnen de dekking beperken. Het contrastinterval bevat nul bij beide methoden. Voor het29-dagengemiddelde ligt de bootstrapondergrens net boven nul terwijl de HAC-ondergrens eronder ligt: geen methode-onafhankelijke conclusie van positieve verwachting. Er zijn geen nieuwe p-waarden berekend.','',
        '## 2. Alle kalenderkwartalen','',
        '| Kwartaal | N doorzakkend | Gem. pt | Mediaan pt | N opverend | Gem. pt | Mediaan pt | Mediane MFE doorzakkend | Mediane MAE doorzakkend |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    lookup={(r['quarter'],r['group']):r for r in data['quarters']}
    for quarter in sorted({r['quarter'] for r in data['quarters']}):
        a,b=lookup[quarter,'NEGATIVE'],lookup[quarter,'POSITIVE']
        lines.append('| '+' | '.join([quarter,str(a['days']),f(a['mean_points']),f(a['median_points']),
            str(b['days']),f(b['mean_points']),f(b['median_points']),f(a['median_mfe_points']),f(a['median_mae_points'])])+' |')
    lines += ['',
        'De29 doorzakkende dagen hebben in vijf van zeven niet-lege kwartalen een positief gemiddelde.2025Q1 en2026Q1 zijn negatief. Kwartaalgroepen bevatten slechts2–6 doorzakkende dagen;2024Q4 bevat geen Gap-Down-dagen. Geen kwartalen geselecteerd of weggelaten.','',
        '## 3. MFE/MAE van de29 doorzakkende dagen','',
        'Onderzoeksanker=09:45 Open. MFE=max(High van09:45 t/m10:29)−anker; MAE=anker−min(Low in hetzelfde venster). Beide zijn positieve afstanden in NQ-punten, geen uitvoerbare target/stop of bekende intraminuutvolgorde. De eerste en laatste45-minutenbar tellen mee; geen prijzen uit09:30–09:44 of vanaf10:30.','',
        '| Maat | N | Gemiddeld | Minimum | P10 | P25 | Mediaan | P75 | P90 | Maximum |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in distribution:
        lines.append('| '+' | '.join([r['measure'],str(r['days']),*[f(r[k]) for k in ('mean','min','p10','p25','median','p75','p90','max')]])+' |')
    paths=pd.read_csv(OUT/'excursions.csv',float_precision='round_trip')
    largest=paths.loc[paths.mfe_points.idxmax()]
    lines += ['',f"De maximale waargenomen MFE is {f(largest.mfe_points)} punten op {largest.day}. Deze bronwaarneming is behouden en niet afgeknipt; de grote maximale excursie trekt het MFE-gemiddelde omhoog ten opzichte van de mediaan. Dit is geen onafhankelijke vendor- of tickcertificatie.",'',
        '## Afzonderlijke15:00-specificatie v2','',
        'Zie AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md en research/afternoon-candidate-v2.json. Twee parallelle primaire netto-puntentoetsen, één Holm2-familie, geen inhoudelijke horizon-gate. V1 blijft als historisch beslisspoor bewaard. Geen nieuwe15:00-uitkomsten op de435 dagen. De toekomstige onafhankelijke toets blijft geblokkeerd totdat het steekproef-/stopplan vooraf is vastgelegd.','',
        '## Verificatie','',
        f"{verification['source_files']} bronbestanden gehasht;29 excursiepaden opnieuw uit de bron geladen met byte-identieke replay; bestaande69 vervolgrendementen ongewijzigd;115 beschermde archiefbestanden en eerdere rapporten ongewijzigd. Geen nieuwe strategie, p-waarden of15:00-run. Ruwe prijzen en dagpaden blijven in de genegeerde artifacts-map. Geen GitHub/Vercel-publicatie in deze opdracht.",'',
        f"Protocol SHA-256: `{data['protocol_sha256']}`.",'']
    report=ROOT/'docs/MORNING_RECOVERY_PRECISION.md'
    report.write_text('\n'.join(lines))
    files=[report,ROOT/'scripts/report_morning_recovery_precision.py',ROOT/'research/morning-recovery-precision-results.json']
    files.extend(ROOT/f'research/morning-recovery-precision-{name}.csv' for name in ('intervals','quarters','excursions'))
    dump(ROOT/'research/morning-recovery-precision-report-manifest.json',dict(
        verification=verification,files_sha256={str(p.relative_to(ROOT)):sha(p) for p in files}))
    print(json.dumps(dict(report=str(report),files=len(files),new_afternoon_runs=0),indent=2))


if __name__=='__main__':
    main()
