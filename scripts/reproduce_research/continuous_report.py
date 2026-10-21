"""Human-readable companion to the aggregate vNext JSON."""
def report(d):
    lines=['# Continuous indicator research — vNext', '',
           '**EXPLORATORY_NOT_NEW_HOLDOUT**. Baseline v0.9 blijft ongewijzigd. Periode 30 december 2024–30 september 2025; niet tien volledige maanden.', '',
           '## Methode', '',
           'Point-in-time additieve Panama-aanpassing. Intern raw minus de cumulatieve reeds bekende spread; historische PDH/PDL worden naar de huidige contractbasis vertaald. ATR gebruikt 14 eerder afgesloten geldige RTH true ranges. Intraday OHLCV, VWAP, signalen en fills blijven op het actieve ruwe contract. De vaste strategiecode en $24,50 RT blijven gelijk. Een nieuwe ATR verandert wel stops/targets op bestaande dagen: dit is niet uitsluitend het toevoegen van verloren trades.', '',
           '| Roll | Laatste gezamenlijke RTH-closebar UTC | Spread (nieuw−oud) |', '|---|---|---:|']
    for r in d['spreads']:lines.append(f"| {r['session']} | {r['close_bar_utc']} | {r['spread_points']:.2f} |")
    lines += ['', 'De spread is pas bekend na voltooiing van de minuutbar. Dit zijn vendor-last-closes, geen officiële settlements. Geen latere rollspread herberekent een eerdere beslissing.', '',
              '## Dekking ORB15', '', '| Contract | Sessies | Baseline eligible | vNext eligible | Extra | ATR ontbreekt |', '|---|---:|---:|---:|---:|---:|']
    for r in d['coverage']:lines.append(f"| {r['contract']} | {r['sessions']} | {r['baseline_eligible']} | {r['eligible']} | {r['additional']} | {r['ATR_missing']} |")
    lines += ['', 'Alle rollover-ATR-gaten verdwijnen, maar niet alle eligibility-gaten: contracteigen same-clock volume-opwarming en complete vereiste minuten blijven verplicht. Ook de initiële H25-opwarming blijft bestaan.', '',
              '## Vaste regels, nieuwe indicatorhistorie', '',
              '| Strategie | Periode | Eligible | Trades | Netto pt | PF | Winrate |', '|---|---|---:|---:|---:|---:|---:|']
    for period,key in [('Dec–sep','continuous_combined'),('Apr–sep reeds bekeken','continuous_apr_sep_already_observed')]:
        for s,v in d[key].items():
            m=v['all'];lines.append(f"| {s} | {period} | {m['eligible_days']} | {m['trades']} | {m['net_points']:.3f} | {m['profit_factor']:.3f} | {m['win_rate']:.1%} |")
    lines += ['', '### Effect ontleed', '', '| Strategie | Extra dagen | Extra-dag trades | Extra-dag netto pt | Gemeenschappelijke dagen: vNext pt | Gemeenschappelijke dagen: baseline pt |', '|---|---:|---:|---:|---:|---:|']
    for s,v in d['impact_decomposition'].items():
        lines.append(f"| {s} | {v['additional_days']} | {v['new_days_trades']} | {v['new_days_net_points']:.3f} | {v['common_days_vnext_net_points']:.3f} | {v['common_days_baseline_net_points']:.3f} |")
    lines += ['', '## Featurebeschikbaarheid', '']+[f'- {k}: {v}' for k,v in d['availability'].items()]
    lines += ['', 'RVOL is het openingsvolume gedeeld door het gemiddelde van de vorige 14 actieve sessies, niet het gemiddelde van achteraf geselecteerde geschikte dagen. Een incompleet historisch openingsvenster maakt deze RVOL tijdelijk onbekend. Voor London-trades vóór 09:30 zijn de volledige overnight-range en openingslocatie onbekend; voor elke entry vóór 09:45 is de volledige 15m-RVOL onbekend. Deze rijen worden niet met toekomstige waarden aangevuld. PDH/PDL na een onvolledige vorige RTH blijven onbekend.', '',
              '## Beschrijvende feature-matrix', '',
              '| Strategie | Feature | Groep | n | Gemiddeld netto pt | Mediane MFE pt |', '|---|---|---|---:|---:|---:|']
    for r in d['feature_matrix']['groups']:
        mean=r['mean_net_points'];mfe=r['median_MFE_points']
        lines.append(f"| {r['strategy']} | {r['feature']} | {r['group']} | {r['trades']} | {mean:.3f} | {mfe:.3f} |" if mean is not None and mfe is not None else f"| {r['strategy']} | {r['feature']} | {r['group']} | 0 | — | — |")
    lines += ['', 'De groepsrijen kunnen door ontbrekende of nog onbekende features minder trades bevatten dan de strategietotalen. Geen optelling tussen verschillende features of strategieën.', '',
              '## Correctie voor meervoudig toetsen', '',d['feature_matrix']['method'], '',d['feature_matrix']['selection'], '',
              '| Strategie | Feature / contrast | Uitkomst | n | Effect | Ruwe p | Globale Holm p |', '|---|---|---|---:|---:|---:|---:|']
    for r in d['feature_matrix']['tests']:
        label=r['feature']+(f" {r['left']} minus {r['right']}" if r['left'] else '')
        effect='—' if r['estimate'] is None else f"{r['estimate']:.4f}"
        lines.append(f"| {r['strategy']} | {label} | {r['outcome']} | {r['complete_cases']} | {effect} | {r['p_raw']:.4f} | {r['p_holm_global']:.4f} |")
    lines += ['', 'Niet-testbare kleine/constante groepen tellen mee met p=1. Ruwe CI’s in JSON zijn niet multipliciteitsgecorrigeerd. Observatieverbanden, geen causale verklaringen, geen nieuwe filters of parameteroptimalisatie. Er is geen onafhankelijke holdout meer voor deze variant.', '', '## Beperkingen', '']+['- '+x for x in d['limitations']]
    return '\n'.join(lines)+'\n'
