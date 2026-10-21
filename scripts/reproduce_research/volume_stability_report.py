"""Aggregate, retrospective stability audit report; no individual trades published."""
LABELS={'A_London_sweep':'London Sweep','B_ORB5':'ORB 5m','B_ORB15':'ORB 15m','C_VWAP_extreme':'VWAP Extreme'}
PERIODS={'full':'Dec–sep','discovery':'Dec–17 apr','observed_apr_sep':'18 apr–sep (reeds bekeken)'}


def f(v):return '—' if v is None else f'{v:.3f}'


def report(d):
    lines=['# Stabiliteitsaudit vNext — doorlopende volumehistorie', '',
           '**Beschrijvend, retrospectief, geen nieuwe holdout.** Geen handelsregel of parameter aangepast. Baseline v0.9 en beide eerdere vNext-exports blijven ongewijzigd. Periode 30 december 2024–30 september 2025; geen tien volledige maanden.', '',
           '## Analyseplan en herleidbaarheid', '',
           'Definities en bronhashes zijn vastgelegd vóór deze nieuwe uitsplitsingen. De oorspronkelijke trades en geaggregeerde uitkomsten waren al bekeken: dit is dus geen prospectieve preregistratie. Eerder geverifieerde private tradebestanden worden op hash, totale P&L en kosten gereconcilieerd; strategieën hoeven niet opnieuw gesimuleerd te worden.', '',
           d['protocol']['roll_window'], '',
           '| Rollstart | Laatste sessie venster | Geobserveerde sessies |', '|---|---|---:|']
    for r in d['roll_windows']:lines.append(f"| {r['start']} | {r['end']} | {r['observed_sessions']} |")
    lines += ['', '## Periode-uitkomsten en onzekerheid', '',
              'Vier strategieën × drie perioden + vier gepaarde common148-verbeteringen = één globale Holm-familie van 16 toetsen. Tweezijdige gecentreerde circular block-bootstrap: 2000 replicaties, bloklengte 5 eligible sessies, seed 20261020. Eligible dagen zonder trade tellen als nul. Kalendergaten zijn geen fictieve nul-handelsdagen. CI’s hieronder zijn nominale 95%-intervallen per toets, niet gelijktijdige intervallen.', '',
              '| Strategie | Periode | Dagen | Trades | Netto pt | PF | Winrate | Gem. pt/eligible dag | 95% CI daggemiddelde | Holm p |', '|---|---|---:|---:|---:|---:|---:|---:|---|---:|']
    for s,v in d['strategies'].items():
        for period,p in v['periods'].items():
            m=p['metrics'];t=d['tests'][p['test_index']]
            win='—' if m['win_rate'] is None else f"{m['win_rate']:.1%}"
            lines.append(f"| {LABELS[s]} | {PERIODS[period]} | {m['eligible_days']} | {m['trades']} | {f(m['net_points'])} | {f(m['profit_factor'])} | {win} | {f(m['mean_eligible_day_points'])} | [{f(t['ci_low'])}; {f(t['ci_high'])}] | {f(t['p_holm_global'])} |")
    lines += ['', 'Percentiel-CI en gecentreerde tweezijdige bootstrap-p zijn bij een scheve verdeling niet exacte inversen van elkaar. De nominale CI is geen vervanging voor de globale Holm-toets. Alle conclusies blijven retrospectief.', '', '## Tradeverschillen op dezelfde 148 dagen', '',
              'Oud = ATR-continuous met contractgebonden volume; nieuw = dezelfde ATR met actieve doorlopende volumehistorie. Per dag maximaal één trade per strategie. Toegevoegd/verwijderd betreft hier een gewijzigde trade op een al eligible common148-dag. De categorie extra_dates betreft de 11 datums buiten common148; die waren voor London/VWAP al eligible, dus hun extra-datumresultaat is géén winst door een gewijzigde volumefilter.', '',
              '| Strategie | Categorie | Dagen | Oude trades | Nieuwe trades | Oud netto pt | Nieuw netto pt | Verschil pt |', '|---|---|---:|---:|---:|---:|---:|---:|']
    for s,v in d['strategies'].items():
        for r in v['attribution']:
            lines.append(f"| {LABELS[s]} | {r['category']} | {r['days']} | {r['old_trades']} | {r['new_trades']} | {f(r['old_net_points'])} | {f(r['new_net_points'])} | {f(r['delta_points'])} |")
    lines += ['', '### Gepaard verschil binnen common148', '',
              '| Strategie | Veranderde common-dagen | Daarvan buiten rollvenster | Gem. verschil pt/dag | 95% CI | Ruwe p | Globale Holm p |', '|---|---:|---:|---:|---|---:|---:|']
    for s,v in d['strategies'].items():
        t=d['tests'][v['paired_test_index']]
        lines.append(f"| {LABELS[s]} | {v['changed_common_days']} | {v['changed_common_days_outside_roll_window']} | {f(t['estimate_mean_daily_points'])} | [{f(t['ci_low'])}; {f(t['ci_high'])}] | {f(t['p_value'])} | {f(t['p_holm_global'])} |")
    lines += ['', '## Maanden en richting', '',
              'Alle onderstaande uitsplitsingen zijn beschrijvend: geen extra p-waarden, geen selectie van de beste maand of richting.', '',
              '| Strategie | Periode | Uitsplitsing | Groep | Eligible dagen | Trades | Netto pt | PF | Winrate |', '|---|---|---|---|---:|---:|---:|---:|---:|']
    for s,v in d['strategies'].items():
        for r in v['slices']:
            if r['dimension']=='roll_window':continue
            win='—' if r['win_rate'] is None else f"{r['win_rate']:.1%}"
            lines.append(f"| {LABELS[s]} | {PERIODS[r['period']]} | {r['dimension']} | {r['group']} | {r['eligible_days']} | {r['trades']} | {f(r['net_points'])} | {f(r['profit_factor'])} | {win} |")
    lines += ['', '## Rollovervensters versus overige dagen', '',
              '| Strategie | Periode | Venster | Dagen | Nieuwe trades | Nieuw netto pt | Common148 oud pt | Common148 nieuw pt | Common148 verschil pt | Veranderde common-dagen |', '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for s,v in d['strategies'].items():
        for r in v['slices']:
            if r['dimension']!='roll_window':continue
            lines.append(f"| {LABELS[s]} | {PERIODS[r['period']]} | {r['group']} | {r['eligible_days']} | {r['trades']} | {f(r['net_points'])} | {f(r['common148_old_net_points'])} | {f(r['common148_new_net_points'])} | {f(r['common148_delta_points'])} | {r['changed_common_days']} |")
    lines += ['', '## Uitbijters en kosten', '',
              'Verwijder exact de drie hoogste netto trades per strategie/periode. Geen aangepaste entry/exit of parameterselectie. Bij netto verlies is top3/nettowinst niet gedefinieerd. De kostenscenario’s veranderen alleen de kosten op dezelfde fills: 2/4/6 ticks per kant plus $4,50 RT commissie = $24,50/$44,50/$64,50 per roundtrip.', '',
              '| Strategie | Periode | Basis pt | Beste 3 pt | Beste 3 / nettowinst | Zonder beste 3 pt | $44,50 RT pt | $64,50 RT pt | Gerealiseerde max. DD pt |', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for s,v in d['strategies'].items():
        for period,p in v['periods'].items():
            a=p['sensitivity'];m=p['metrics'];share='—' if a['best3_share_net_profit_pct'] is None else f"{a['best3_share_net_profit_pct']:.1f}%"
            lines.append(f"| {LABELS[s]} | {PERIODS[period]} | {f(m['net_points'])} | {f(a['best3_net_points'])} | {share} | {f(a['without_best3']['net_points'])} | {f(a['cost_scenarios'][1]['net_points'])} | {f(a['cost_scenarios'][2]['net_points'])} | {f(m['realized_max_drawdown_points'])} |")
    lines += ['', '## Grenzen', '']+['- '+s for s in d['limits']]
    lines += ['', 'Geen causale verklaring, geen strategiepromotie, geen nieuwe filters of geoptimaliseerde stops/targets. Dit rapport beschrijft alleen de reeds berekende vaste-regels-variant.', '',
              'Reproductie met de geverifieerde private bestanden: `npm run research:volume-stability`. Publiceren van uitsluitend aggregaten: voeg `-- --publish` toe. Private tradeverschillen blijven in `artifacts/volume-stability/trade-attribution.csv`.']
    return '\n'.join(lines)+'\n'
