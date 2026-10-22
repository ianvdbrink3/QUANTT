"""Export verified fixed-round aggregates, without computing new returns/tests."""
import json

import pandas as pd

from scripts.afternoon_falsification import ROOT, OUT, dump, verify
from scripts.oos_preparation.adapter import sha


def corrected_result():
    verification = verify()
    s = json.loads((OUT / 'summary.json').read_text())
    c = json.loads((OUT / 'time-audit-correction.json').read_text())
    checks = [
        (OUT / 'COMPLETED.json', c['old_completed_sha256']),
        (OUT / 'bar-audit-corrected.csv', c['corrected_csv_sha256']),
        (ROOT / 'scripts/falsification_time_audit.py', c['correction_source_sha256']),
    ]
    for path, digest in checks:
        if sha(path) != digest:
            raise ValueError('Correction evidence changed: ' + str(path))
    if json.loads((ROOT / 'research/afternoon-falsification-time-audit-correction.json').read_text()) != c:
        raise ValueError('Correction copies differ')
    if c['statistical_tables_or_pvalues_changed']:
        raise ValueError('Statistics cannot change in timestamp correction')
    s['legacy_integrity'] = s['integrity']
    s['integrity'] = c['corrected_integrity']
    s['time_audit_correction'] = c
    fixed = next(r for r in s['concentration'] if r['scheme'] == 'fixed')
    if fixed['original_mean'] <= 0:
        decision = 'DISAPPEARS_WITH_FIXED_COHORT'
    elif any(r['any_day_sign_flip'] or r['any_quarter_sign_flip'] for r in s['concentration']):
        decision = 'SIGN_FRAGILE_TO_LEAVE_OUT'
    elif s['integrity']['flagged_days'] or not s['integrity']['second_source_verified']:
        decision = 'INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED'
    else:
        decision = 'STRONGER_RESEARCH_HYPOTHESIS_NOT_VALIDATED_EDGE'
    s['decision_after_time_audit_correction'] = decision
    return s, verification


def fmt(x):
    if isinstance(x, float):
        return f'{x:.4g}'
    return str(x)


def table(rows, columns):
    return '\n'.join([
        '| ' + ' | '.join(label for key, label in columns) + ' |',
        '| ' + ' | '.join('---' for _ in columns) + ' |',
        *['| ' + ' | '.join(fmt(r[key]) for key, label in columns) + ' |' for r in rows],
    ])


def run():
    s, verification = corrected_result()
    research = ROOT / 'research'
    dump(research / 'afternoon-falsification-results.json', s)
    pd.DataFrame(s['tables']).to_csv(research / 'afternoon-falsification-rows.csv', index=False, float_format='%.17g')
    tests = []
    for r in s['tests']:
        tests.append({k: v for k, v in r.items() if k not in ('points', 'bps')} | dict(
            delta_points=r['points']['delta'], ci95_points_low=r['points']['ci95'][0],
            ci95_points_high=r['points']['ci95'][1], delta_logbps=r['bps']['delta'],
            se_HAC5_logbps=r['bps']['se_HAC5'], se_CR1_logbps=r['bps']['se_CR1'],
            ci95_logbps_low=r['bps']['ci95'][0], ci95_logbps_high=r['bps']['ci95'][1],
            p_raw=r['bps']['p_raw']))
    pd.DataFrame(tests).to_csv(research / 'afternoon-falsification-tests.csv', index=False, float_format='%.17g')
    pd.DataFrame(s['leave_quarters']).to_csv(research / 'afternoon-falsification-leave-quarters.csv', index=False, float_format='%.17g')
    pd.DataFrame(s['transitions']['detailed']).to_csv(research / 'afternoon-falsification-transitions.csv', index=False)

    base = [('scheme', 'Cohort'), ('group', 'Richting'), ('clock', 'Start'), ('days', 'N'),
            ('mean_points', 'Gem. pt'), ('median_points', 'Mediaan pt'), ('positive_fraction', 'Aandeel >0')]
    full = [r for r in s['tables'] if r['part'] == 'FULL']
    parts = [r for r in s['tables'] if r['part'] != 'FULL']
    trows = [dict(scheme=r['scheme'], group=r['group'], part=r['part'], comparison=r['comparison'],
                  delta=r['points']['delta'], ci=f"[{r['points']['ci95'][0]:.3f}; {r['points']['ci95'][1]:.3f}]",
                  p=r['bps']['p_raw'], holm=r['p_Holm24']) for r in s['tests']]
    concentration = [dict(scheme=r['scheme'], mean=r['original_mean'],
        day_min=r['day_out_min_mean'], day_max=r['day_out_max_mean'],
        min_day=r['day_out_min_omitted'], max_day=r['day_out_max_omitted'],
        quarter_min=r['quarter_out_min']['remaining_mean'], quarter_max=r['quarter_out_max']['remaining_mean'])
        for r in s['concentration']]
    lines = [
        '# 15:00-falsificatie — vaste cohorten, minuutisolatie en integriteit', '',
        '## Uitkomst', '',
        '**INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED**. De positieve gemiddelde impuls verdwijnt niet bij cohortbevriezing om 14:30 en wisselt niet van teken na enige dag- of kwartaalweglating. De aantoonbare afwijking zit vooral in de eerste minuut: het restant is positief gemeten, maar niet overtuigend na de vooraf vastgelegde Holm-correctie. Geen gevalideerde edge of bewijs van uitvoerbaarheid.', '',
        'Dit is uitsluitend een falsificatie op reeds gebruikte data, geen nieuwe holdout. Geen strategie, fills, kostenmodel, stops, targets of parameters zijn toegevoegd. Geen GitHub/Vercel-publicatie in deze ronde.', '',
        '## Meetdefinities en onzekerheid', '',
        '- Universum: dezelfde 435 volledige RTH-dagen; 69 geregistreerde bronbestanden. 17 dagen zonder vooraf bekende ATR blijven buiten UP/DOWN, maar binnen de integriteitscontrole.',
        '- Vast: selectie uitsluitend met voltooide 14:29-bar, richting t.o.v. 09:30-open en opgebouwde range / vooraf bekende ATR14 in [0,5; 1,2). Dynamisch: identieke selectie opnieuw op elk meetmoment.',
        '- FULL: close vóór start tot close van minuut start+14. Het venster 15:00–15:15 eindigt dus op de voltooide 15:14-bar, bekend om 15:15; niet op de close van de 15:15-bar.',
        '- FIRST: open tot close van startminuut. REST: open start+1 tot close start+14. FULL omvat daarnaast beide close/open-prijsverschillen. Mediane componenten zijn niet optelbaar.',
        '- UP is positief bij stijging; DOWN is positief bij daling. DOWN-cijfers zijn dus geen ruwe opwaartse prijsbeweging.',
        '- Precies 24 tweezijdige toetsen, één Holm-familie. Primaire p-waarden op log-basispunten; dag-invloedscores met HAC(5), inclusief covariantie van overlappende cohorten, t-intervallen. Getoonde puntenintervallen zijn nominale 95%-intervallen, niet simultaan gecorrigeerd. CR1-sensitiviteits-SE staat in CSV/JSON.',
        '- Deze correctie dekt alleen deze ronde, niet de eerdere projectbrede selectie. Niet-significant is geen bewijs dat het effect nul is. Point-in-time betekent geen geïdentificeerde institutionele oorzaak.', '',
        '## 1. Vaste versus dynamische cohorten', '', table(full, base), '',
        'Van de oorspronkelijke +7,5404 pt blijft op het vaste UP-cohort +8,0046 pt over: +0,4642 pt verschil tussen twee verschillende groepen. Geen causale schatting van de invloed van selectie.', '',
        '### Statusovergangen 14:30 → 15:00', '',
        table(s['transitions']['matrix'], [('at1430','14:30'),('at1500','15:00'),('days','Dagen')]), '',
        '26 dagen veranderen tussen de eindpunten van grove status (UP/DOWN/OTHER); 30 veranderen op minstens één van de drie kwartiermeetpunten. Van 162 vaste UP-dagen blijven 155 UP, gaan 6 naar DOWN en 1 boven de rangegrens; 12 nieuwe UP-dagen komen erbij. Van 131 vaste DOWN-dagen blijven 121 DOWN, gaan 7 naar UP en 3 boven de rangegrens; 10 nieuwe DOWN-dagen komen erbij. OTHER betekent geen bruikbare UP/DOWN-selectie, niet automatisch corrupte data.', '',
        '## 2. Eerste minuut en resterende 14 minuten', '',
        table(parts, base[:3] + [('part','Deel')] + base[3:]), '',
        '### Alle vooraf vastgelegde toetsen', '',
        table(trows, [('scheme','Cohort'),('group','Richting'),('part','Deel'),('comparison','Vergelijking'),
            ('delta','Verschil pt'),('ci','95%-BI pt'),('p','p ruw (log-bp)'),('holm','p Holm24')]), '',
        'UP FIRST is positief versus nul (vast Holm p=0,00705; dynamisch p=0,00142) en wijkt af van de eerste minuut om 14:45 (p=0,00676 / 0,00699), niet overtuigend van 14:30 (p=0,601 / 0,378). UP REST is gemiddeld +4,338 / +3,937 pt; de nulvergelijkingen hebben Holm p=1, en ook beide vergelijkingen met eerdere kwartieren blijven boven 0,05. Dit bewijst niet dat uitsluitend minuut 1 de beweging bevat: het meet wel waar in deze ronde het statistische bewijs overblijft.', '',
        'De vaste UP-decompositie om 15:00 is 0,0833 + 3,4907 + 0,0926 + 4,3380 = 8,0046 pt. Dynamisch is dit 0,0734 + 3,4551 + 0,0749 + 3,9371 = 7,5404 pt. De eerste minuut zelf is circa 43,6% / 45,8% van het volledige gemiddelde; geen uitspraak over de eerste seconde mogelijk.', '',
        '## 3. Concentratie en alle weglatingen', '',
        table(concentration, [('scheme','Cohort'),('mean','Orig. gem.'),('day_min','LODO min'),('day_max','LODO max'),
            ('min_day','Min: dag eruit'),('max_day','Max: dag eruit'),('quarter_min','LOQO min'),('quarter_max','LOQO max')]), '',
        'De minimumgemiddelden na dagweglating ontstaan zonder 19 maart 2026 (+148 pt); de maxima zonder 2 maart 2026 (−115 pt). Geen tekenomslag. Dit is richtingrobuustheid, geen bewijs van voldoende effectgrootte of significantie na weglating.', '',
        '### Elke kwartaalweglating', '',
        table(s['leave_quarters'], [('scheme','Cohort'),('omitted_quarter','Kwartaal eruit'),('omitted_days','N eruit'),
            ('omitted_mean','Gem. eruit pt'),('remaining_days','N over'),('remaining_mean','Gem. over pt')]), '',
        'Zonder 2026Q2 is het gemiddelde het laagst: +5,081 / +5,203 pt. Zonder 2025Q3 het hoogst: +10,133 / +9,313 pt. Afzonderlijke kwartalen hoeven niet positief te zijn: het vaste UP-cohort is in 2025Q3 én 2026Q3 gemiddeld negatief.', '',
        '## 4. Bar-aansluiting en expliciete correctie', '',
        table([s['integrity']], [('days','Dagen'),('expected_bars','Verwacht'),('observed_bars','Aanwezig'),('missing','Ontbrekend'),('duplicates','Dubbel'),('flagged_days','Afgekeurde dagen')]), '',
        table(s['integrity']['price_gaps'], [('pair','Overgang'),('nonzero_days','Niet-nul dagen'),('mean_points','Gem. pt'),
            ('median_points','Mediaan'),('min_points','Min'),('max_points','Max')]), '',
        'Alle gecontroleerde bars hebben 60-secondenafstand, coherente OHLC op het 0,25-tickraster en één contract/handelsdatum per dag. Een close/open-prijsverschil is niet hetzelfde als een ontbrekende tijdstempel.', '',
        '**Technisch erratum:** unit tests vonden vóór interpretatie van de nieuwe statistische tabellen een eenheidsfout in de eerste integriteitscontrole: microseconden werden vergeleken met een vaste nanosecondentelling. Daardoor werden onterecht alle 435 dagen gemarkeerd. De run was toen al afgerond. De originele code, uitvoer en hashes zijn behouden; een afzonderlijke timedelta-controle corrigeert uitsluitend de afstandstest naar 0 afgekeurde dagen. Alle overige auditkolommen zijn exact gelijk en geen statistische tabel of p-waarde is gewijzigd. De correctie is afzonderlijk gehasht en geregistreerd.', '',
        'Dit sluit tijdstempelgaten in de gecontroleerde bron uit, maar geen systematische vendor-labelverschuiving. Onafhankelijke tweede-bronbevestiging en subminuut-/uitvoerbaarheidsbewijs ontbreken.', '',
        '## Beslisboom en verificatie', '',
        '1. Vast UP-gemiddelde ≤0? **Nee**, +8,0046 pt.',
        '2. Enige dag-/kwartaalweglating met gemiddelde ≤0? **Nee**, beide cohortvarianten blijven positief.',
        '3. Integriteitsfout of geen onafhankelijke bronbevestiging? **Geen resterende gridfout, wél ontbrekende onafhankelijke bronbevestiging.**',
        '4. Eindstatus: **INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED**. Deze controles falsificeren de positieve gemiddelde impuls niet; ze valideren geen handelsedge. Het sterkste statistische bewijs blijft geconcentreerd in de eerste minuut.', '',
        'Bronreplay: byte-identieke meetledgers; eerdere dynamische cohortresultaten exact gereproduceerd; 1.305 toekomst-afknipcontroles; 24 toetsen; 0 strategie-runs; 115 beschermde archiefbestanden ongewijzigd. Volledige aggregaten en testuitvoer staan naast dit rapport in research/afternoon-falsification-*.csv en results.json.', '',
    ]
    report = ROOT / 'docs/AFTERNOON_FALSIFICATION_REPORT.md'
    report.write_text('\n'.join(lines))
    paths = [report, research / 'afternoon-falsification-results.json',
        *[research / ('afternoon-falsification-' + name + '.csv') for name in ('rows','tests','leave-quarters','transitions')],
        ROOT / 'scripts/report_afternoon_falsification.py', ROOT / 'scripts/falsification_time_audit.py',
        research / 'afternoon-falsification-time-audit-correction.json']
    dump(research / 'afternoon-falsification-report-manifest.json', dict(
        decision=s['decision_after_time_audit_correction'], verification=verification,
        files_sha256={str(p.relative_to(ROOT)): sha(p) for p in paths}))
    print(json.dumps(dict(report=str(report), decision=s['decision_after_time_audit_correction'], output_files=len(paths)), indent=2))


if __name__ == '__main__':
    run()
