"""Separate reproducible volume-continuity experiment; no baseline publications."""
import argparse
import json
from pathlib import Path
import pandas as pd
from . import engine,holdout,holdout_data
from .next_engine import Activation,prepare_with_overlap
from .continuous import continuous_daily,apply_indicators
from .volume_path import active_volume_history,trade_paths,summarize_paths

ROOT=holdout_data.REPO


def report(result):
    lines=['# vNext — volumecontinuïteit en post-entry paden', '',
           'Periode: 30 december 2024–30 september 2025. Uitsluitend beschrijvend op reeds bekeken data. Baseline v0.9 én de eerdere continuous-export blijven ongewijzigd.', '',
           '## Volumehistorie', '',
           'Ongewijzigd: mediaan van maximaal 20 eerdere observaties van dezelfde NY-minuut, minimum 10; signaalvolume >1,5× referentie. Alleen de historie gebruikt nu de chronologische actieve contractstroom. Geen inactief volume toegevoegd, geen huidige/toekomstige sessie in de referentie. De aparte context-RVOL14 is niet de ORB-signaalfilter en is niet aangepast.', '',
           'Alle vier strategieën hebben exact dezelfde 159 eligible datums. Dagen zonder trade blijven eligible. Overige kwaliteitsfilters, entry/exitregels, ATR, stops/targets en $24,50 roundtripkosten zijn gelijk aan de vorige continuous-variant.', '',
           '## Uitkomsten bij gelijkgetrokken datums', '',
           '| Strategie | Volumehistorie / datums | Dagen | Trades | Netto punten | PF | Winrate |', '|---|---|---:|---:|---:|---:|---:|']
    for strategy,views in result['comparison'].items():
        for label,m in views.items():
            pf='—' if m['profit_factor'] is None else f"{m['profit_factor']:.3f}"
            win='—' if m['win_rate'] is None else f"{m['win_rate']:.1%}"
            lines.append(f"| {strategy} | {label} | {m['eligible_days']} | {m['trades']} | {m['net_points']:.3f} | {pf} | {win} |")
    lines += ['', 'De eerste twee regels per strategie gebruiken dezelfde 148 dagen: verschil is uitsluitend de volumereferentie. De derde regel gebruikt alle 159 dagen; de vierde uitsluitend de 11 toegevoegde dagen. Dit is geen opgeteld portfolio.', '',
              '## Grenzen van de meting', '',result['measurement'], '',
              '## Bereikt R-niveau en uiteindelijk netto resultaat', '',
              '| Strategie | Niveau | Alle trades | Zeker bereikt | Mogelijk incl. zeker | Percentage [onder–boven] | Zekere hits: verlies / winst / vlak | Extra onzekere hits: verlies / winst / vlak |', '|---|---:|---:|---:|---:|---:|---|---|']
    for s,v in result['paths'].items():
        for t in v['thresholds']:
            signs=t['by_final_net_sign'];certain=[signs[k]['certain'] for k in ['negative','positive','flat']]
            uncertain=[signs[k]['possible_including_certain']-signs[k]['certain'] for k in ['negative','positive','flat']]
            lines.append(f"| {s} | +{t['R']:.1f}R | {t['all_trades']} | {t['certain_hits']} | {t['possible_hits_including_certain']} | {100*t['hit_fraction_lower']:.1f}–{100*t['hit_fraction_upper']:.1f}% | {' / '.join(map(str,certain))} | {' / '.join(map(str,uncertain))} |")
    lines += ['', 'Zeker en extra onzeker zijn disjunct; de netto-P&L-tekens zijn bekend. De bovengrenzen respecteren het gesimuleerde target en de stop (of bekende slechtere gapfill). Bij een sessie-exit op de laatste minuutclose is de volledige exitbar doorlopen en dus bekend. De JSON bevat daarnaast grenzen voor het conditionele verlies-/winstpercentage onder de trades die het niveau bereiken. De percentages zijn geen betrouwbaarheidsintervallen maar conservatieve intrabar-identificatiegrenzen.', '',
              '## Tijd tot eerste minuutextreem', '',
              '| Strategie | MFE mediaan [P25–P75] min | MAE mediaan [P25–P75] min | MFE in exitbar | MAE in exitbar |', '|---|---|---|---:|---:|']
    def fmt(q):
        return '—' if q['median'] is None else f"{q['median']:.2f} [{q['p25']:.2f}–{q['p75']:.2f}] (n={q['n']})"
    for s,v in result['paths'].items():
        lines.append(f"| {s} | {fmt(v['MFE_first_bar_minutes'])} | {fmt(v['MAE_first_bar_minutes'])} | {v['MFE_extreme_in_exit_bar']}/{v['trades']} | {v['MAE_extreme_in_exit_bar']}/{v['trades']} |")
    lines += ['', 'Tijd is het begin van de eerste minuutbar met het uiterste (eerste bij gelijke extremen). Bij nul positieve/negatieve excursie is het extremum al op entry bereikt: tijd 0, niet weggelaten. Minuut k betekent [k,k+1), niet een exact transactietijdstip. Deze volledige-bar-extremen kunnen in de exitminuut ná de fill vallen. Voor alleen volledig doorlopen minuten vóór de exitbar:', '',
              '| Strategie | MFE prefix mediaan [P25–P75] min | MAE prefix mediaan [P25–P75] min |', '|---|---|---|']
    for s,v in result['paths'].items():
        lines.append(f"| {s} | {fmt(v['MFE_completed_prefix_minutes'])} | {fmt(v['MAE_completed_prefix_minutes'])} |")
    lines += ['', 'De prefix is niet de volledige trade: de exitminuut ontbreekt en trades zonder positieve/negatieve excursie in die prefix hebben geen extremumtijd. Exacte timing van de werkelijke trade-MFE/MAE is niet identificeerbaar uit deze bron.', '',
              '## Netto resultaat per uitstapreden', '',
              '| Strategie | Reden | Trades | Aandeel | Netto punten | Netto USD | Mediaan netto R [P25–P75] |', '|---|---|---:|---:|---:|---:|---|']
    for s,v in result['paths'].items():
        for e in v['exits']:
            lines.append(f"| {s} | {e['reason']} | {e['trades']} | {e['share']:.1%} | {e['net_points']:.3f} | {e['net_usd']:.2f} | {fmt(e['net_R'])} |")
    lines += ['', 'Stop bevat stop_both: de ongewijzigde simulator neemt bij stop én target in dezelfde minuut de stop eerst. Netto R gebruikt kosten gedeeld door het initiële prijsrisico; 1R zelf is uitsluitend de afstand entry–initiële stop.', '',
              '## Statistische toetsen', '', 'Geen inferentiële toetsen uitgevoerd. Alleen gemeten aantallen, percentages, kwantielen en intrabar-grenzen; daarom geen p-waarden of multipliciteitscorrectie nodig. Geen aanbevelingen, selectie van filters of parameterwijzigingen.', '',
              '## Reproduceerbaarheid', '',
              'Vanaf de 30 originele CSV-hashes: `.venv/bin/python -m scripts.reproduce_research.run_volume_path`. Private trades, eligibility en padgegevens blijven in `artifacts/volume-path-vnext/`. De JSON bevat bron-/codehashes en bewijs dat eerdere exports tijdens de run gelijk bleven.']
    return '\n'.join(lines)+'\n'


def run(output):
    frozen_names=['public/data/nq-overnight.json','public/data/research09.json','public/data/research-holdout.json',
                  'research/holdout-reference.json','research/holdout-protocol.json','public/data/research-continuous.json']
    frozen_hash={n:holdout_data.sha(ROOT/n) for n in frozen_names}
    protocol=json.loads((ROOT/'research/holdout-protocol.json').read_text())
    holdout.preflight(ROOT/'data/raw',protocol)
    full,_=holdout_data.load_all(ROOT/'data/raw',protocol['sources'])
    rolls=holdout_data.rollovers(full);assert rolls==protocol['rollovers']
    schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]+[Activation(r['to'],r['effective_session']) for r in rolls]
    print('1/4 Rebuild raw contract features and continuous indicators',flush=True)
    prepared=prepare_with_overlap(full,schedule,calendar_grid=holdout_data.grid,require_day1_atr=False)
    daily,_=continuous_daily(full,schedule);old_master=apply_indicators(prepared.master,daily)
    old_trades,old_e=engine.hypotheses(old_master)
    previous=json.loads((ROOT/'public/data/research-continuous.json').read_text())
    old_summary=holdout.summarize(old_trades,old_e,daily,'2024-12-30','2025-09-30')
    for s in holdout.STRATEGIES:
        for key in ['eligible_days','trades','net_points','profit_factor']:
            assert abs(old_summary[s]['all'][key]-previous['continuous_combined'][s]['all'][key])<1e-8
    print('2/4 Active same-clock volume history; fixed strategy replay',flush=True)
    master=active_volume_history(old_master)
    unchanged=[c for c in old_master.columns if c!='prior_same_minute_median_volume']
    pd.testing.assert_frame_equal(master[unchanged],old_master[unchanged])
    trades,e=engine.hypotheses(master);holdout.verify_trades(master,trades)
    dates={s:set(e.loc[e.strategy.eq(s)&e.eligible,'trade_date']) for s in holdout.STRATEGIES}
    assert all(d==dates['B_ORB15'] for d in dates.values())
    common=set(old_e.loc[old_e.strategy.eq('B_ORB15')&old_e.eligible,'trade_date'])
    all_dates=dates['B_ORB15'];added=all_dates-common
    assert len(common)==148 and len(all_dates)==159 and len(added)==11
    # Mean-reversion does not consume the changed volume column.
    for s in ['A_London_sweep','C_VWAP_extreme']:
        pd.testing.assert_frame_equal(trades[trades.strategy.eq(s)].reset_index(drop=True),old_trades[old_trades.strategy.eq(s)].reset_index(drop=True))
    comparison={}
    for s in holdout.STRATEGIES:
        comparison[s]={}
        for name,t,ds in [('old_reference_common148',old_trades,common),('active_reference_common148',trades,common),
                          ('active_reference_full159',trades,all_dates),('active_reference_added11',trades,added)]:
            selected=t[t.strategy.eq(s)&t.trade_date.isin(ds)].sort_values('entry_utc')
            m=engine.metrics(selected,sorted(ds))
            comparison[s][name]={k:m[k] for k in ['eligible_days','trades','net_points','net_usd','profit_factor','win_rate','mean_net_points']}
    print('3/4 Measured post-entry paths, risk units and exit reconciliation',flush=True)
    paths=trade_paths(master,trades);stats=summarize_paths(paths)
    for s,v in stats.items():
        expected=comparison[s]['active_reference_full159']
        assert sum(x['trades'] for x in v['exits'])==expected['trades']
        assert abs(sum(x['net_points'] for x in v['exits'])-expected['net_points'])<1e-8
    assert frozen_hash=={n:holdout_data.sha(ROOT/n) for n in frozen_names}
    result={'classification':'DESCRIPTIVE_NO_NEW_HOLDOUT_NO_OPTIMIZATION','period':['2024-12-30','2025-09-30'],
            'eligible_days':159,'previous_ORB_eligible':148,'additional_dates':sorted(added),
            'comparison':comparison,'paths':stats,'frozen_exports_unchanged_sha256':frozen_hash,
            'source_sha256':{x['filename']:x['sha256'] for x in protocol['sources']},
            'code_sha256':{n:holdout_data.sha(Path(__file__).parent/n) for n in ['volume_path.py','run_volume_path.py','continuous.py','next_engine.py','engine.py']},
            'measurement':'1R = absolute raw entry-to-initial-stop distance, before costs. Completed pre-exit bars plus the modeled exit price give a conservative lower excursion bound. Whole-exit-bar extremes give upper bounds, capped by the target for MFE and by the stop or known worse gapfill for MAE under the frozen execution model. At session-close exit the entire final bar is observed. Reached-R percentages are conservative intrabar identification intervals, not confidence intervals or exact tick-order percentages. Bounds include the execution endpoint. Timing of whole-bar extrema can include post-exit prices and is separate from completed-prefix timing. Model fills, not observed broker executions.',
            'inferential_tests':0}
    result=engine.clean(result)
    output.mkdir(parents=True,exist_ok=True)
    for name,frame in [('trades',trades),('eligibility',e),('trade-paths',paths)]:frame.to_csv(output/(name+'.csv'),index=False)
    (output/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (output/'REPORT.md').write_text(report(result))
    print('4/4 Outputs verified:',output,flush=True)
    print(json.dumps(comparison,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/volume-path-vnext')
    run(parser.parse_args().output)
