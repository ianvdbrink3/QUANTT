"""Raw-to-vNext reproduction. No edits to Baseline v0.9 files."""
import argparse
import json
from pathlib import Path
import pandas as pd
from . import engine,holdout,holdout_data
from .next_engine import Activation,prepare_with_overlap
from .continuous import continuous_daily,apply_indicators
from .context import day_context,trade_context
from .feature_matrix import matrix
from .continuous_report import report

ROOT=holdout_data.REPO


def run(output, publish=False, verify=False):
    protocol=json.loads((ROOT/'research/holdout-protocol.json').read_text())
    holdout.preflight(ROOT/'data/raw',protocol)
    full,_=holdout_data.load_all(ROOT/'data/raw',protocol['sources'])
    rolls=holdout_data.rollovers(full)
    assert rolls==protocol['rollovers']
    schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]+[Activation(r['to'],r['effective_session']) for r in rolls]
    print('1/4 Features from all raw contract overlaps; frozen rules unchanged',flush=True)
    prepared=prepare_with_overlap(full,schedule,calendar_grid=holdout_data.grid,require_day1_atr=False)
    baseline,base_eligible=engine.hypotheses(prepared.master)
    frozen=json.loads((ROOT/'research/holdout-reference.json').read_text())
    baseline_summary=holdout.summarize(baseline,base_eligible,prepared.daily,'2024-12-30','2025-09-30')
    for key in holdout.STRATEGIES:
        for field in ['eligible_days','trades','net_points','profit_factor']:
            assert abs(baseline_summary[key]['all'][field]-frozen['combined'][key]['all'][field])<1e-8
    print('2/4 Point-in-time continuous ATR/PDH/PDL; raw execution',flush=True)
    daily,spreads=continuous_daily(full,schedule)
    master=apply_indicators(prepared.master,daily)
    assert master[['open','high','low','close','volume','vwap_close']].equals(prepared.master[['open','high','low','close','volume','vwap_close']])
    trades,eligible=engine.hypotheses(master)
    holdout.verify_trades(master,trades)
    contexts=day_context(master); tf=trade_context(master,trades,contexts)
    eligible_dates=set(eligible.loc[eligible.eligible,'trade_date'])
    contexts=contexts[contexts.trade_date.isin(eligible_dates)]
    summary=holdout.summarize(trades,eligible,daily,'2024-12-30','2025-09-30')
    historical=holdout.summarize(trades,eligible,daily,'2025-04-18','2025-09-30')
    decomposition={}
    for strategy in holdout.STRATEGIES:
        old_dates=set(base_eligible.loc[base_eligible.strategy.eq(strategy)&base_eligible.eligible,'trade_date'])
        new_dates=set(eligible.loc[eligible.strategy.eq(strategy)&eligible.eligible,'trade_date'])
        t=trades[trades.strategy.eq(strategy)]
        b=baseline[baseline.strategy.eq(strategy)]
        decomposition[strategy]={'additional_days':len(new_dates-old_dates),'lost_days':len(old_dates-new_dates),
                                 'new_days_trades':int(t.trade_date.isin(new_dates-old_dates).sum()),
                                 'new_days_net_points':float(t.loc[t.trade_date.isin(new_dates-old_dates),'net_points'].sum()),
                                 'common_days_vnext_net_points':float(t.loc[t.trade_date.isin(old_dates&new_dates),'net_points'].sum()),
                                 'common_days_baseline_net_points':float(b.loc[b.trade_date.isin(old_dates&new_dates),'net_points'].sum())}
    coverage=[]
    eligible_contract=eligible.assign(contract=eligible.trade_date.map(daily.set_index('trade_date').contract))
    for c,g in eligible_contract[eligible_contract.strategy.eq('B_ORB15')].groupby('contract'):
        old=base_eligible[base_eligible.strategy.eq('B_ORB15')&base_eligible.trade_date.isin(daily[daily.contract.eq(c)].trade_date)]
        coverage.append({'contract':c,'sessions':len(g),'eligible':int(g.eligible.sum()),
                         'baseline_eligible':int(old.eligible.sum()),'additional':int(g.eligible.sum()-old.eligible.sum()),
                         'ATR_missing':int(daily[daily.contract.eq(c)].atr14_continuous.isna().sum())})
    print('3/4 Context matrix; global Holm correction',flush=True)
    feature_matrix=matrix(tf,sorted(master.trade_date.unique()))
    result={'label':'vNext PIT Panama — EXPLORATORY_NOT_NEW_HOLDOUT',
            'period':['2024-12-30','2025-09-30'],'baseline_label':'Baseline v0.9 frozen',
            'source_protocol_sha256':holdout_data.sha(ROOT/'research/holdout-protocol.json'),
            'raw_source_hashes':{x['filename']:x['sha256'] for x in protocol['sources']},
            'code_sha256':{n:holdout_data.sha(Path(__file__).parent/n) for n in ['continuous.py','context.py','feature_matrix.py','run_continuous.py','next_engine.py','continuous_report.py']},
            'cost_rt_usd':24.5,'spreads':spreads,'coverage':coverage,
            'baseline_combined':baseline_summary,'continuous_combined':summary,
            'continuous_apr_sep_already_observed':historical,'impact_decomposition':decomposition,
            'feature_matrix':feature_matrix,
            'availability':{'ticks':'UNAVAILABLE: raw source contains OHLCV only; no trade count. All relative-ticks/intensity outputs null.',
                            'opening_context':'09:30 open is known at 09:30; masked for earlier/equal-time entries.',
                            'opening_volume':'First 15 completed 1m bars known at 09:45. RVOL uses previous 14 active sessions only; masked for earlier trades.',
                            'distance':'Signed distance from completed signal close to current-basis PDH/PDL, not unknown next-open entry price.',
                            'daily_export':'Timestamped feature snapshots, NOT a claim every field was known before every trade.'},
            'limitations':['No real ticks, order book or trade-level VWAP.',
                           'Panama changes ATR-based risk/targets even on existing eligible dates; this is not merely appending lost trades.',
                           'Same-clock signal-volume histories still contract-native; quality/prefix gates unchanged. Zero ATR loss is not a guarantee all calendar days become trade eligible.',
                           'Spreads use vendor 15:59 minute closes, not official settlement; identical-clock prices may be asynchronous last trades.',
                           'Entire dataset already observed: all vNext comparisons exploratory; no promotion or strategy selection.',
                           'Initial history and holiday/incomplete-session exclusions remain. Period is Dec30 plus Jan-Sep, not ten complete months.']}
    output.mkdir(parents=True,exist_ok=True)
    for name,frame in [('trades',trades),('eligibility',eligible),('daily-indicators',daily),('day-context',contexts),('trade-context',tf)]:
        frame.to_csv(output/(name+'.csv'),index=False)
    (output/'summary.json').write_text(json.dumps(engine.clean(result),indent=2,allow_nan=False)+'\n')
    (output/'REPORT.md').write_text(report(engine.clean(result)))
    if publish:
        (ROOT/'public/data/research-continuous.json').write_text(json.dumps(engine.clean(result),indent=2,allow_nan=False)+'\n')
        (ROOT/'docs/CONTINUOUS_CONTEXT_RESEARCH.md').write_text(report(engine.clean(result)))
    if verify:
        assert json.loads((output/'summary.json').read_text())==json.loads((ROOT/'public/data/research-continuous.json').read_text()), 'vNext reproduction mismatch'
    print('4/4 Verified output files:',output,flush=True)
    print(json.dumps(coverage,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/continuous-vnext')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--publish',action='store_true')
    mode.add_argument('--verify',action='store_true')
    args=parser.parse_args();run(args.output,args.publish,args.verify)
