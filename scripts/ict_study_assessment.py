"""Descriptive fixed comparisons. No extra signals, weighting or parameter search."""
import csv
import json
from scripts.ict_study import __main__ as run

ROOT=run.ROOT
CRITERIA=dict(
    candidate='Positive net ATR-R in BOTH eras with touch AND one-tick trade-through; combinedN>=30 reported as descriptive sample-size label, not tuned exclusion.',
    dominates_B='For each era: greater total net ATR-R AND higher trade PF_ATR_R AND higher daily Sharpe_ATR_R than frozen B. DD is reported as a separate tradeoff; no claim of general dominance if worse DD.',
    portfolio='For BOTH eras and BOTH S1/S2 baselines: equal0.5/0.5 separate sleeves improve daily Sharpe and do not increase DAILY close DD, plus positive standalone in both eras under bothfill assumptions. Diagnostic only; no third-pillar promotion.',
    significance='All Holm480 tests remain reported. Already-consumed development pool and selection cannot provide independent validation, even when p passes.')


def assess():
    run.verify();x=json.loads(run.RESULT.read_text());stats=x['samples']['TOUCH'];strict=x['samples']['TRADE_THROUGH']
    records=[]
    for name in run.NAMES:
        eras=run.PERIODS[:2]
        stable=all(stats[b][name]['net_ATR_R']>0 and strict[b][name]['net_ATR_R']>0 for b in eras)
        dominates=all(stats[b][name]['net_ATR_R']>x['benchmarks'][b]['B']['net_R'] and
                      stats[b][name]['PF_ATR_R'] is not None and stats[b][name]['PF_ATR_R']>x['benchmarks'][b]['B']['trade_PF_R'] and
                      stats[b][name]['sharpe_ATR_R'] is not None and stats[b][name]['sharpe_ATR_R']>x['benchmarks'][b]['B']['sharpe_daily_R'] for b in eras)
        portfolio=stable and all(
            x['portfolio'][b][name][base]['daily_sharpe'] is not None and
            x['portfolio'][b][name][base]['daily_sharpe']>x['portfolio'][b][name][base]['baseline_daily_sharpe'] and
            x['portfolio'][b][name][base]['daily_close_drawdown_ATR_R']<=x['portfolio'][b][name][base]['baseline_daily_close_drawdown_ATR_R']
            for b in eras for base in ('S1','S2'))
        significant=all(x['inference'][b][name]['MINUS_B']['p_holm480']<.05 and x['inference'][b][name]['MINUS_B']['mean_ci95'][0]>0 for b in run.PERIODS)
        records.append(dict(model=name,positive_both_eras_both_fills=stable,touch_exceeds_B_return_PF_sharpe_both_eras=dominates,
                            descriptive_portfolio_condition=portfolio,incremental_holm480_all_periods=significant,
                            combined_N=stats['COMBINED'][name]['N'],combined_ATR_R=stats['COMBINED'][name]['net_ATR_R']))
    result=dict(status=run.METHOD['status'],criteria=CRITERIA,records=records,
                counts={key:sum(r[key] for r in records) for key in ('positive_both_eras_both_fills','touch_exceeds_B_return_PF_sharpe_both_eras','descriptive_portfolio_condition','incremental_holm480_all_periods')})
    run.h.dump(ROOT/'research/ict-study-assessment.json',result)
    lines=['# ICT versus B, S1 en S2 — vaste beschrijvende vergelijking','',run.METHOD['status'],'']
    lines += [f'- {k}: {v}' for k,v in CRITERIA.items()]
    lines += ['', '## Aantallen','']+[f'- {k}: {v}/80' for k,v in result['counts'].items()]
    lines += ['', '## Alle varianten','', '| Variant | N | Netto ATR-R | Positief beide perioden en fills | B hoger rendement/PF/Sharpe beide perioden | Portefeuilleconditie beide baselines/perioden | Holm480 meerwaarde alle perioden |','|---|---:|---:|---|---|---|---|']
    for r in records:
        lines.append('| '+r['model']+f" | {r['combined_N']} | {r['combined_ATR_R']:.6f} | "+' | '.join(str(r[k]) for k in ('positive_both_eras_both_fills','touch_exceeds_B_return_PF_sharpe_both_eras','descriptive_portfolio_condition','incremental_holm480_all_periods'))+' |')
    lines += ['', 'Geen van deze beschrijvende labels is een onafhankelijke goedkeuring. Lagere handelsfrequentie, kortere stopafstand en een andere risiconoemer kunnen PF/stopR fraaier laten lijken zonder S1/S2 op vergelijkbare blootstelling te overtreffen.','']
    (ROOT/'docs/ICT_COMPARISON_WITH_BENCHMARKS.md').write_text('\n'.join(lines))
    return result


if __name__=='__main__':print(json.dumps(assess()['counts'],indent=2))
