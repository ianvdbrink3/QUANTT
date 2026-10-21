"""Explicitly released, fixed-window scoring. One first run plus one fresh replay.

The sealed preparation route and all frozen strategy files remain unmodified.
No optimizing, period selection or repeated inference until a preferred result.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.oos_preparation.adapter import Calendar,sha
from scripts.oos_preparation.seal import check as check_preparation
from scripts.oos_preparation.year import load_registered,schedule_for,dump
from scripts.oos_preparation.route import select_active,STRATEGIES
from scripts.reproduce_research import engine,holdout
from scripts.reproduce_research.continuous import continuous_daily,apply_indicators
from scripts.reproduce_research.volume_path import active_volume_history,trade_paths,summarize_paths,quantiles
from scripts.verify_research_freeze import verify

ROOT=Path(__file__).resolve().parents[1]
START,END='2025-10-01','2026-09-30'
RELEASE=ROOT/'research/year-holdout-release.json'
OUTPUT=ROOT/'artifacts/year-holdout'
PERIODS={'year':(START,END),'combined':('2024-12-30',END)}


def register_release():
    check_preparation()
    readiness=json.loads((ROOT/'public/data/research-oos-year-readiness.json').read_text())
    assert set(readiness['technical_eligible_days'].values())=={249}
    assert readiness['contamination_status']=='NO_FUTURE_TRADE_LEDGER_FOUND_LIMITED_EVIDENCE'
    plan=dict(classification='EXPLICIT_HUMAN_RELEASE_BEFORE_FIRST_SCORING',
        approved_preparation_commit='8d37b66b76ba7f0ea0b486b372c29582f08fab7f',
        authorization='User explicitly approves Step4 fixed full-year scoring, one independent source replay, Step5 publication to GitHub main and quantt production; accepts preparation limitations.',
        period=[START,END],primary_strategy='B_ORB15',primary_view='all',expected_eligible_per_model=249,
        cost_rt_usd=24.5,parameters_changed=False,maximum_full_scoring_runs_this_release=2,
        nonprimary_family=[f'{period}:{s}' for period in PERIODS for s in STRATEGIES if not(period=='year' and s=='B_ORB15')]+['year:B_ORB15:clean'],
        multiplicity='One confirmatory year ORB15 all-view, unchanged raw p. Eight other requested/clean sensitivity p-values in one globally Holm-adjusted family, fixed before scoring. References and combined statistics descriptive only, never promotion.',
        costs_stress_rt_usd=[24.5,44.5,64.5],subgroup_tests='None: month, direction and paths descriptive only',
        preparation_sha256=sha(ROOT/'research/oos-year-preregistration.json'),
        frozen_protocol_sha256=sha(ROOT/'research/vnext-future-oos-protocol.json'),
        scoring_code_sha256=sha(Path(__file__)),
        source_register_sha256=sha(ROOT/'research/oos-year-sources.json'),
        calibration='No future returns inspected before this file; user release is not an external prospective registration.',
        caveats=readiness['gates'])
    if RELEASE.exists():
        if json.loads(RELEASE.read_text())!=plan:raise ValueError('Release already locked; never silently replace')
    else:dump(RELEASE,plan)
    print('Explicit release locked before outcomes. No signals yet.')


def preflight():
    check_preparation();verify()
    p=json.loads(RELEASE.read_text())
    if p['scoring_code_sha256']!=sha(Path(__file__)):raise ValueError('Scoring code changed since release')
    for key,name in [('preparation_sha256','research/oos-year-preregistration.json'),
                     ('frozen_protocol_sha256','research/vnext-future-oos-protocol.json'),
                     ('source_register_sha256','research/oos-year-sources.json')]:
        if p[key]!=sha(ROOT/name):raise ValueError('Released input changed: '+name)
    if p['period']!=[START,END] or p['cost_rt_usd']!=engine.COST*20:raise ValueError('Period/cost drift')
    return p


def released_features(full,schedule,calendar):
    """Identical orchestration to sealed historical_features, release guard first.

    Intraday features are contract/session native. Only subsequent multi-day
    ATR/PDH/PDL and active volume history are continuous, as frozen previously.
    """
    preflight()
    if full.empty or not full.trade_date.between('2024-12-30',END).all():raise ValueError('Outside released bounds')
    old=engine.expected_grid
    try:
        engine.expected_grid=calendar.grid
        enriched,_,_,_=engine.build_features(full)
    finally:engine.expected_grid=old
    master=select_active(enriched,schedule)
    daily,_=continuous_daily(full,schedule)
    return active_volume_history(apply_indicators(master,daily))


def descriptive(t,dates):
    t=t.sort_values(['entry_utc','trade_date'])
    x=t.net_points.to_numpy(float)
    daily=t.groupby('trade_date').net_points.sum().reindex(dates,fill_value=0.)
    equity=np.r_[0.,np.cumsum(x)]
    loss=float(-x[x<0].sum());net=float(x.sum());best3=float(t.net_points.nlargest(3).sum())
    return dict(eligible_days=len(dates),trades=len(t),net_points=net,net_usd=net*20,
        win_rate=float((x>0).mean()) if len(x) else None,
        profit_factor=float(x[x>0].sum()/loss) if loss>0 else None,
        profit_factor_no_losses=bool(len(x)>0 and loss==0),
        mean_trade_points=float(x.mean()) if len(x) else None,
        mean_eligible_day_points=float(daily.mean()) if len(daily) else None,
        max_drawdown_points=float((np.maximum.accumulate(equity)-equity).max()),
        max_drawdown_usd=float((np.maximum.accumulate(equity)-equity).max())*20,
        worst_day=str(daily.idxmin()) if len(daily) else None,
        worst_day_points=float(daily.min()) if len(daily) else None,
        worst_day_usd=float(daily.min()*20) if len(daily) else None,
        best3_net_points=best3,best3_share_net_profit_pct=100*best3/net if net>0 else None,
        best3_share_note='Undefined when total net profit<=0; not a positive profit-concentration fraction',
        net_points_without_best3=net-best3,
        drawdown_definition='Realized closed-trade equity with initial zero; not mark-to-market',
        both_hit_bars=int(t.both_hit_bar.sum()) if len(t) else 0)


def aggregate(trades,eligibility,paths,plan):
    result={};daily_rows=[]
    for period,(start,end) in PERIODS.items():
        result[period]={}
        for s in STRATEGIES:
            e=eligibility[eligibility.strategy.eq(s)&eligibility.eligible&eligibility.trade_date.between(start,end)]
            dates=sorted(e.trade_date.unique())
            t=trades[trades.strategy.eq(s)&trades.trade_date.between(start,end)].sort_values(['entry_utc','trade_date'])
            if not t.trade_date.isin(dates).all():raise ValueError('Trade outside eligible days')
            m=descriptive(t,dates)
            daily=t.groupby('trade_date').net_points.sum().reindex(dates,fill_value=0.)
            m.update(engine.bootstrap(daily))
            m['bootstrap_unit']='Mean net points per eligible day, including no-trade zeros;95%nominal percentile CI'
            m['inferential_role']='Sole confirmatory hypothesis' if period=='year' and s=='B_ORB15' else 'Descriptive only; combined includes spent discovery data'
            months=[]
            for month in pd.period_range(start,end,freq='M').astype(str):
                ds=[d for d in dates if d.startswith(month)];mt=t[t.trade_date.str.startswith(month)]
                months.append(dict(month=month,**descriptive(mt,ds)))
            directions={label:descriptive(t[t.direction.eq(value)],dates) for label,value in [('long',1),('short',-1)]}
            stresses=[]
            for cost in plan['costs_stress_rt_usd']:
                st=t.copy();st['net_points']=st.gross_points-cost/20;st['net_usd']=st.net_points*20
                stresses.append(dict(cost_rt_usd=cost,**descriptive(st,dates)))
            pg=paths[paths.strategy.eq(s)&paths.trade_date.between(start,end)]
            distributions={c:quantiles(pg[c]) for c in ['MFE_R_lower','MFE_R_bar_upper','MAE_R_lower','MAE_R_bar_upper',
                'MFE_points_lower','MFE_points_bar_upper','MAE_points_lower','MAE_points_bar_upper',
                'MFE_first_bar_minute','MAE_first_bar_minute']}
            path_summary=summarize_paths(pg).get(s,{})
            clean_dates=sorted(e.loc[e.data_quality_flag.eq('ok'),'trade_date'].unique())
            ct=t[t.trade_date.isin(clean_dates)]
            clean=descriptive(ct,clean_dates)
            # Only primary year clean sensitivity has inference; other clean views descriptive.
            if period=='year' and s=='B_ORB15':
                cd=ct.groupby('trade_date').net_points.sum().reindex(clean_dates,fill_value=0.)
                clean.update(engine.bootstrap(cd))
            result[period][s]=dict(metrics=m,monthly=months,direction=directions,cost_sensitivity=stresses,
                excursions=distributions,path_summary=path_summary,clean_sensitivity=clean)
            eq=daily.cumsum();dd=eq.cummax().clip(lower=0)-eq
            for day,value in daily.items():daily_rows.append(dict(period=period,strategy=s,trade_date=day,
                net_points=float(value),cumulative_net_points=float(eq.at[day]),drawdown_points=float(dd.at[day])))
            # Only monthly cumulative equity is published; private daily per-strategy ledger retained.
            mseries=pd.Series(daily.to_numpy(),index=pd.to_datetime(dates))
            meq=mseries.resample('ME').sum().cumsum()
            result[period][s]['monthly_equity']=[dict(month=d.strftime('%Y-%m'),net_points=float(v)) for d,v in meq.items()]
    pvalues=[]
    for key in plan['nonprimary_family']:
        parts=key.split(':');m=result[parts[0]][parts[1]]['clean_sensitivity' if len(parts)==3 else 'metrics']
        pvalues.append(m['p_value'])
    adjusted=engine.holm(pvalues)
    for key,p in zip(plan['nonprimary_family'],adjusted):
        parts=key.split(':');m=result[parts[0]][parts[1]]['clean_sensitivity' if len(parts)==3 else 'metrics']
        m['p_holm_nonprimary_family8']=float(p)
    return result,pd.DataFrame(daily_rows)


def score(run_id):
    plan=preflight()
    if run_id not in ['first','reproduction']:raise ValueError('Only first and one reproduction allowed')
    out=OUTPUT/run_id
    if out.exists():raise ValueError('Run already exists; never overwrite a seen holdout run')
    if run_id=='reproduction' and not (OUTPUT/'first/summary.json').is_file():raise ValueError('Complete first run required')
    print('1/6 Fresh sourceCSV load; hashes and preregistration verified',flush=True)
    full,_,_=load_registered()
    calendar=Calendar(json.loads((ROOT/'research/oos-year-calendar.json').read_text()))
    schedule,rolls=schedule_for(full,calendar)
    approved=json.loads((ROOT/'research/oos-year-rollovers.json').read_text())['rollovers']
    current=[{k:v for k,v in r.items() if k not in ['old_volume','new_volume','spread_points']} for r in rolls]
    if current!=approved:raise ValueError('Rollover drift before scoring')
    print('2/6 Frozen contract-session features; continuous point-in-time prerequisites',flush=True)
    master=released_features(full,schedule,calendar)
    # Output directory is an exclusive consumption marker immediately before signals.
    out.mkdir(parents=True,exist_ok=False)
    (out/'EXECUTION_STARTED').write_text('Released year scoring started; do not overwrite or silently rerun.\n')
    print('3/6 One frozen hypothesis-engine invocation, fixed full period',flush=True)
    trades,eligibility=engine.hypotheses(master)
    historical=trades[trades.trade_date.le('2025-09-30')]
    hist_e=eligibility[eligibility.trade_date.le('2025-09-30')]
    refs=json.loads((ROOT/'research/volume-stability-protocol.json').read_text())['source_sha256']
    for name,frame in [('trades',historical),('eligibility',hist_e)]:
        path=ROOT/f'artifacts/volume-path-vnext/{name}.csv'
        if sha(path)!=refs[str(path.relative_to(ROOT))] or frame.to_csv(index=False)!=path.read_text():
            raise ValueError('Historical trade/eligibility drift')
    approved_e=pd.read_csv(ROOT/'artifacts/oos-year-readiness/eligibility.csv')
    actual_e=eligibility[eligibility.trade_date.between(START,END)]
    for s in STRATEGIES:
        ds=set(actual_e.loc[actual_e.strategy.eq(s)&actual_e.eligible,'trade_date'])
        expected=set(approved_e.loc[approved_e.strategy.eq(s)&approved_e.eligible,'trade_date'])
        if ds!=expected or len(ds)!=249:raise ValueError('Eligible-day drift: '+s)
    print('4/6 Fill/cost invariants and bounded post-entry paths',flush=True)
    holdout.verify_trades(master,trades)
    paths=trade_paths(master,trades)
    for stem in ['MFE','MAE']:
        paths[f'{stem}_points_lower']=paths[f'{stem}_R_lower']*paths.initial_R_points
        paths[f'{stem}_points_bar_upper']=paths[f'{stem}_R_bar_upper']*paths.initial_R_points
    print('5/6 Fixed bootstrap, descriptive breakdowns, no optimization',flush=True)
    results,daily=aggregate(trades,eligibility,paths,plan)
    protocol=json.loads((ROOT/'research/vnext-future-oos-protocol.json').read_text())
    status,checks=holdout.verdict(results['year']['B_ORB15']['metrics'],protocol)
    summary=dict(classification='FIXED_YEAR_HOLDOUT_CONSUMED',status=status,primary_checks=checks,
        future_scoring_completed=True,
        period=[START,END],combined_period=['2024-12-30',END],primary_strategy='B_ORB15',
        results=results,release_sha256=sha(RELEASE),preparation_sha256=plan['preparation_sha256'],
        source_register_sha256=plan['source_register_sha256'],cost_rt_usd=24.5,
        historical_ledgers_byte_identical=True,technical_eligible_per_model=249,
        multiplicity=plan['multiplicity'],nonprimary_family=plan['nonprimary_family'],
        methods=dict(bootstrap=protocol['inference'],drawdown='Closed-trade, not intratrade mark-to-market',
            MFE_MAE='Lower/upper intrabar identification bounds, not exact tick sequence. Quantiles in points and initial-risk R. Time labels are first minute-bar extrema, may occur after modeled exit within that minute.',
            stresses='Fixed fills, $24.50/$44.50/$64.50 roundtrip subtraction only; not new signals',
            independence='Second fresh-process reproduction of same implementation, not an independently authored engine or statistical replication',
            combined='Spent historical research plus new holdout; descriptive only, cannot rescue failed year'),
        limitations=plan['caveats'],freeze=verify())
    summary=engine.clean(summary)
    for name,frame in [('trades-combined',trades),('trades-year',trades[trades.trade_date.between(START,END)]),
                       ('eligibility',eligibility),('trade-paths',paths),('daily-equity',daily)]:
        frame.to_csv(out/(name+'.csv'),index=False)
    dump(out/'summary.json',summary)
    (out/'EXECUTION_STARTED').unlink()  # Successful completion; not part of result set.
    print('6/6 Complete deterministic output set written; no parameter changes',flush=True)
    return summary


def compare_runs(a=OUTPUT/'first',b=OUTPUT/'reproduction'):
    files_a=sorted(p.name for p in a.iterdir() if p.is_file())
    files_b=sorted(p.name for p in b.iterdir() if p.is_file())
    if files_a!=files_b or 'summary.json' not in files_a:raise ValueError('Output file-set mismatch')
    hashes={}
    for name in files_a:
        if (a/name).read_bytes()!=(b/name).read_bytes():raise ValueError('Byte mismatch: '+name)
        hashes[name]=sha(a/name)
    return dict(status='PASS_TWO_FRESH_SOURCE_REPLAYS_BYTE_IDENTICAL',files_sha256=hashes,
        fresh_processes=2,scoring_engine_invocations=2,parameter_changes=0,
        independent_engine_implementation=False,release_sha256=sha(RELEASE))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--register-release',action='store_true')
    parser.add_argument('--run',choices=['first','reproduction'])
    parser.add_argument('--compare',action='store_true')
    args=parser.parse_args()
    if args.register_release:register_release()
    if args.run:score(args.run)
    if args.compare:
        evidence=compare_runs();dump(ROOT/'research/year-holdout-verification.json',evidence)
        print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
