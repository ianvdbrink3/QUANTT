"""Render closed descriptive tables, no new outcomes, tests or public export."""
import json

import pandas as pd

from scripts.morning_recovery_anatomy import ROOT,OUT,dump,verify
from scripts.oos_preparation.adapter import sha

LABELS = dict(NEGATIVE='Negatief / doorzakkend', POSITIVE='Positief / opverend', FLAT='Vlak',
    GAP_ONLY='Alleen Gap-Down (achteraf)', ONL_ONLY='Alleen ONL (achteraf)', BOTH='Beide (achteraf)',
    GAP_ONLY_KNOWN_0945='Gap-Down, nog geen ONL om09:45',
    ONL_ONLY_KNOWN_0945='ONL bekend09:45, geen Gap-Down', BOTH_KNOWN_0945='Beide bekend09:45')


def f(x):
    return '—' if x is None else f'{x:.3f}'.replace('.',',')


def table(rows):
    lines = ['| Groep | N | Gem. pt | P10 | P25 | Mediaan | P75 | P90 | Opwaarts % | Gem. log-bp |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        p = r['following_points']
        cells = [LABELS[r['group']], str(r['days']), *[f(p[k]) for k in ('mean','p10','p25','median','p75','p90')],
            f(100*r['positive_fraction']) if r['positive_fraction'] is not None else '—', f(r['following_logbps']['mean'])]
        lines.append('| '+' | '.join(cells)+' |')
    return lines


def main():
    verification = verify()
    summary = json.loads((OUT/'summary.json').read_text())
    dump(ROOT/'research/morning-recovery-anatomy-results.json', summary)
    flat = []
    for r in summary['tables']:
        flat.append({k:r[k] for k in ('view','group','days','positive_fraction')} |
            {metric+'_'+stat:value for metric in ('following_points','following_logbps') for stat,value in r[metric].items()})
    pd.DataFrame(flat).to_csv(ROOT/'research/morning-recovery-anatomy-tables.csv',index=False,float_format='%.17g')
    pd.DataFrame(summary['timing']).to_csv(ROOT/'research/morning-recovery-anatomy-timing.csv',index=False)
    pd.DataFrame(summary['descriptive_differences']).to_csv(ROOT/'research/morning-recovery-anatomy-differences.csv',index=False,float_format='%.17g')
    lines = ['# Ochtendherstel: strikt gescheiden eerste kwartier en vervolgvenster', '',
        'Beschrijvende metingen op de bestaande data, geen handelsmodel of nieuwe significantietoets. De afzonderlijke15:00-kandidaatregistratie is vóór deze uitkomsten bevroren; er zijn geen nieuwe15:00-rendementen berekend.', '',
        '## Vensters', '',
        '| Onderdeel | Definitie |', '|---|---|',
        '| Tijdzone | America/New_York, bestaande DST-bewuste parser |',
        '| Indeling eerste kwartier | 09:30 Open → 09:44 Close; strikt negatief, positief of exact vlak |',
        '| Uitsluitend gerapporteerd vervolgrendement | 09:45 Open → 10:29 Close,45 minuten, opwaarts positief |',
        '| Geen tijdsoverlap | Geen bar09:30–09:44 of close/open-gap op09:45 in het vervolgresultaat |',
        '| Prijzen | Ruwe actieve contractprijzen; geen contract- of dagovergang in beide vensters |',
        '| Selectie | Bestaande69 Gap-Down- en101 A_ONL_ACCEPT/60m-dagen;21 overlap;149 unieke dagen |',
        '| Interpretatie | Bruto prijsverdeling, geen winstpercentage van een uitvoerbare strategie. Tijdstipcausaliteit onder BAR_START_SUPPORTED_INTERNAL_ONLY, geen bewezen economische oorzaak |', '',
        '## A.69 Gap-Down-dagen naar het eerste kwartier', '',
        *table([r for r in summary['tables'] if r['view']=='GAP_OPENING_SIGN']), '',
        'Alle getoonde rendementen horen uitsluitend bij09:45–10:30. Vlakke dagen blijven een aparte rij, ook wanneer N=0. Kwantielen gebruiken lineaire interpolatie.', '',
        '## B. Gevraagde149 dagen: retrospectieve groepsindeling', '',
        '**De48/80/21-indeling is niet volledig point-in-time om09:45.** Bij55 van101 ONL-dagen is de eerste bevestigingsclose pas later bekend, waarvan29 na10:30. Ook het label alleen-Gap-Down gebruikt achteraf de afwezigheid van een ONL-event in de vaste dagset. Deze tabel is uitsluitend een beschrijving achteraf, geen causale voorspelling vanaf09:45.', '',
        *table([r for r in summary['tables'] if r['view']=='RETROSPECTIVE_149']), '',
        '### Beschikbaarheid van ONL op het meetmoment', '',
        '| Retrospectieve groep | N | ONL bekend uiterlijk09:45 | ONL later t/m10:30 | ONL na10:30 |',
        '|---|---:|---:|---:|---:|']
    for r in summary['timing']:
        lines.append('| '+' | '.join([LABELS[r['group']],str(r['days']),str(r['known_by0945']),str(r['later_through1030']),str(r['after1030'])])+' |')
    lines += ['', '## C. Afzonderlijke point-in-time vergelijking:101 dagen', '',
        'Om09:45 zijn69 Gap-Down- en46 ONL-dagen bekend, met14 overlap:101 unieke dagen. De groepen zijn55/32/14. De7 Gap-Down-dagen met pas latere ONL schuiven naar Gap-Down, nog geen ONL bekend. De48 niet-Gap-Down-dagen met pas latere ONL selecteren dit meetmoment niet. Dit is geen uitkomstgestuurde uitsluiting of vervanging van de gevraagde149-tabel.', '',
        *table([r for r in summary['tables'] if r['view']=='KNOWN_AT_0945']), '',
        '## Beschrijvende verschillen tussen groepen', '',
        'Verschillen zijn groepA minus groepB. Geen p-waarden, interval, significantieclaim of geselecteerde winnaar.', '',
        '| Indeling | Vergelijking | Verschil gemiddelde pt | Verschil mediaan pt |',
        '|---|---|---:|---:|']
    for r in summary['descriptive_differences']:
        a,b = r['comparison'].split(' minus ')
        lines.append('| '+' | '.join([r['view'],LABELS[a]+' minus '+LABELS[b],f(r['mean_difference_points']),f(r['median_difference_points'])])+' |')
    lines += ['', '## Afzonderlijk bevroren15:00-specificatie', '',
        'Zie `AFTERNOON_CANDIDATE_PREREGISTRATION.md` en `research/afternoon-candidate-v1.json`. Primaire horizon15:00-open→15:14-close; secundair15:00-open→15:01-close; één tweezijdige Holm2-familie. Status CANDIDATE_SPEC_FROZEN_INDEPENDENT_TEST_NOT_RELEASED. Geen toekomstige toets zonder afzonderlijk vooraf vastgelegd datavenster/stopregel.', '',
        '## Verificatie', '',
        f"69 bronbestanden op hashes gecontroleerd; {verification['first_quarter_prefix_checks']} prefix- en evenveel toekomstmutatiecontroles; verse bronreplay byte-identiek; {verification['protected_archive_files']} beschermde archiefbestanden ongewijzigd. Geen nieuwe strategie-runs,15:00-runs of p-waarden. Ruwe prijsarrays en meetregels blijven in de genegeerde artifacts-map. Geen GitHub/Vercel-publicatie in deze opdracht.", '',
        f"Protocol SHA-256: `{summary['protocol_sha256']}`.",
        f"Afzonderlijke kandidaat-lock SHA-256: `{summary['candidate_lock_sha256']}`.", '']
    report = ROOT/'docs/MORNING_RECOVERY_ANATOMY.md'
    report.write_text('\n'.join(lines))
    files = [report, ROOT/'scripts/report_morning_recovery_anatomy.py',
        *[ROOT/'research'/('morning-recovery-anatomy-'+stem+suffix) for stem,suffix in
            [('results','.json'),('tables','.csv'),('timing','.csv'),('differences','.csv')]]]
    dump(ROOT/'research/morning-recovery-anatomy-report-manifest.json',dict(
        verification=verification, files_sha256={str(p.relative_to(ROOT)):sha(p) for p in files}))
    print(json.dumps(dict(report=str(report),files=len(files),new_tests=0,new_strategy_runs=0),indent=2))


if __name__ == '__main__':
    main()
