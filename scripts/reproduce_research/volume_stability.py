"""Fixed-rule retrospective stability audit; no raw prices published or rules tuned."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from . import engine,holdout_data

ROOT=holdout_data.REPO
PROTOCOL=ROOT/'research/volume-stability-protocol.json'
OLD=ROOT/'artifacts/continuous-vnext'
NEW=ROOT/'artifacts/volume-path-vnext'
PERIODS={'full':('2024-12-30','2025-09-30'),'discovery':('2024-12-30','2025-04-17'),
         'observed_apr_sep':('2025-04-18','2025-09-30')}
STRATEGIES=['A_London_sweep','B_ORB5','B_ORB15','C_VWAP_extreme']
FROZEN=['public/data/nq-overnight.json','public/data/research09.json','public/data/research-holdout.json',
        'public/data/research-continuous.json','public/data/research-volume-path.json',
        'research/holdout-reference.json','research/holdout-protocol.json']


def register():
    sources=[OLD/'trades.csv',OLD/'eligibility.csv',NEW/'trades.csv',NEW/'eligibility.csv']
    plan={'classification':'RETROSPECTIVE_AUDIT_OF_ALREADY_OBSERVED_DATA',
          'not_prospective_preregistration':True,'periods':PERIODS,
          'roll_window':'First 20 observed active civil-session dates starting at each fixed roll, including incomplete/holiday observed sessions. Last window truncated at dataset end. Check changed trades outside, do not assume references become identical.',
          'roll_dates':['2025-03-19','2025-06-17','2025-09-17'],
          'inference':'One global Holm family of 16 two-sided centered circular 5-eligible-session bootstrap tests: four strategies x three period mean returns plus four paired common148 improvements. Existing engine bootstrap: 2000 replicates, seed 20261020. Eligible zero-trade days included; calendar gaps not filled. Nominal 95% CIs are not simultaneous. Monthly/direction/roll groups and sensitivities descriptive only.',
          'costs_rt_usd':[24.5,44.5,64.5],
          'cost_definition':'2,4,6 ticks per side at .25 points; fixed $4.50 RT commission; unchanged trade fills and stops. Extra cost only, no new signal simulation.',
          'outliers':'Remove exactly three highest-net trades per strategy/period, tie break by date; no threshold search.',
          'source_sha256':{str(p.relative_to(ROOT)):holdout_data.sha(p) for p in sources},
          'frozen_sha256':{p:holdout_data.sha(ROOT/p) for p in FROZEN}}
    plan=json.loads(json.dumps(plan))
    if PROTOCOL.exists():
        assert json.loads(PROTOCOL.read_text())==plan,'Do not silently change audit definitions or sources'
    else:PROTOCOL.write_text(json.dumps(plan,indent=2)+'\n')
    print('Audit definitions and source hashes locked before new breakdowns.')


def dates_for(eligibility,strategy):
    return sorted(eligibility.loc[eligibility.strategy.eq(strategy)&eligibility.eligible,'trade_date'].unique())


def simple_metrics(t,days):
    x=t.sort_values(['entry_utc','trade_date']).net_points.to_numpy(float)
    wins=float(x[x>0].sum());losses=float(-x[x<0].sum())
    eq=np.r_[0,np.cumsum(x)]
    return {'eligible_days':len(days),'trades':len(t),'net_points':float(x.sum()),'net_usd':float(x.sum()*20),
            'win_rate':float((x>0).mean()) if len(x) else None,'profit_factor':wins/losses if losses else None,
            'mean_trade_points':float(x.mean()) if len(x) else None,
            'mean_eligible_day_points':float(x.sum()/len(days)) if len(days) else None,
            'realized_max_drawdown_points':float((np.maximum.accumulate(eq)-eq).max())}


def roll_windows(observed,starts):
    windows=[];all_dates=set()
    for start in starts:
        chosen=[d for d in observed if d>=start][:20]
        windows.append({'start':start,'end':chosen[-1] if chosen else None,'observed_sessions':len(chosen)})
        all_dates.update(chosen)
    return all_dates,windows


def attribution(old,new,common,all_dates,strategy):
    a=old[old.strategy.eq(strategy)].set_index('trade_date')
    b=new[new.strategy.eq(strategy)].set_index('trade_date')
    if not a.index.is_unique or not b.index.is_unique:raise ValueError('One trade per strategy/day required')
    rows=[]
    compare=['signal_utc','entry_utc','exit_bar_utc','entry_price','exit_price','direction','stop','target','exit_reason','net_points']
    for day in sorted(all_dates):
        x=a.loc[day] if day in common and day in a.index else None
        y=b.loc[day] if day in b.index else None
        if day not in common:category='extra_dates_outside_common148' if y is not None else 'extra_dates_no_trade'
        elif x is None and y is None:category='no_trade_both'
        elif x is None:category='added_common'
        elif y is None:category='removed_common'
        elif all(x[k]==y[k] for k in compare):category='unchanged'
        elif x.direction!=y.direction:category='direction_changed'
        elif x.entry_utc!=y.entry_utc:category='entry_time_changed'
        else:category='same_entry_changed_outcome'
        old_net=float(x.net_points) if x is not None else 0.
        new_net=float(y.net_points) if y is not None else 0.
        rows.append({'strategy':strategy,'trade_date':day,'category':category,
                     'old_trade':x is not None,'new_trade':y is not None,
                     'old_entry_utc':x.entry_utc if x is not None else None,
                     'new_entry_utc':y.entry_utc if y is not None else None,
                     'old_direction':int(x.direction) if x is not None else None,
                     'new_direction':int(y.direction) if y is not None else None,
                     'old_net_points':old_net,'new_net_points':new_net,'delta_points':new_net-old_net})
    detail=pd.DataFrame(rows)
    categories=[]
    for category,g in detail.groupby('category',sort=True):
        categories.append({'category':category,'days':len(g),'old_trades':int(g.old_trade.sum()),
                           'new_trades':int(g.new_trade.sum()),'old_net_points':float(g.old_net_points.sum()),
                           'new_net_points':float(g.new_net_points.sum()),'delta_points':float(g.delta_points.sum())})
    return detail,categories


def sensitivities(t,dates):
    ordered=t.sort_values(['net_points','trade_date'],ascending=[False,True])
    best=ordered.head(3)
    reduced=t.drop(best.index)
    net=float(t.net_points.sum());top=float(best.net_points.sum())
    costs=[]
    for cost in [24.5,44.5,64.5]:
        adjusted=t.copy();adjusted['net_points']=t.net_points-(cost-24.5)/20
        costs.append({'cost_rt_usd':cost,**simple_metrics(adjusted,dates)})
    return {'best3_net_points':top,'best3_share_net_profit_pct':100*top/net if net>0 else None,
            'without_best3':simple_metrics(reduced,dates),'cost_scenarios':costs}


def audit(output,publish=False):
    if not PROTOCOL.exists():raise ValueError('First run --register; no outcome breakdown before definitions')
    plan=json.loads(PROTOCOL.read_text())
    for name,digest in {**plan['source_sha256'],**plan['frozen_sha256']}.items():
        assert holdout_data.sha(ROOT/name)==digest,name
    previous=json.loads((ROOT/'research/continuous-verification-evidence.json').read_text())
    for name in ['trades.csv','eligibility.csv']:
        assert holdout_data.sha(OLD/name)==previous['private_output_sha256'][name]
    old,oe,new,ne=[pd.read_csv(p) for p in [OLD/'trades.csv',OLD/'eligibility.csv',NEW/'trades.csv',NEW/'eligibility.csv']]
    for frame in [old,new]:
        assert not frame.duplicated(['strategy','trade_date']).any()
        assert np.allclose(frame.net_points,frame.direction*(frame.exit_price-frame.entry_price)-engine.COST,atol=1e-9)
        assert np.allclose(frame.net_usd,20*frame.net_points,atol=1e-8)
    for s in ['A_London_sweep','C_VWAP_extreme']:
        pd.testing.assert_frame_equal(old[old.strategy.eq(s)].reset_index(drop=True),new[new.strategy.eq(s)].reset_index(drop=True))
    pub=json.loads((ROOT/'public/data/research-volume-path.json').read_text())
    oldpub=json.loads((ROOT/'public/data/research-continuous.json').read_text())
    common=set(dates_for(oe,'B_ORB15'));full_dates=dates_for(ne,'B_ORB15')
    assert len(common)==148 and len(full_dates)==159 and common.issubset(full_dates)
    assert all(dates_for(ne,s)==full_dates for s in STRATEGIES)
    window_dates,windows=roll_windows(sorted(ne.trade_date.unique()),plan['roll_dates'])
    strategies={};tests=[];details=[]
    for s in STRATEGIES:
        a=old[old.strategy.eq(s)];b=new[new.strategy.eq(s)]
        for key in ['trades','net_points','profit_factor']:
            actual=simple_metrics(b,full_dates)[key]
            assert np.isclose(actual,pub['comparison'][s]['active_reference_full159'][key])
            assert np.isclose(simple_metrics(a,dates_for(oe,s))[key],oldpub['continuous_combined'][s]['all'][key])
        detail,categories=attribution(old,new,common,full_dates,s)
        assert not detail.category.eq('same_entry_changed_outcome').any(), 'Volume-only change altered an identical entry outcome'
        details.append(detail)
        changed=detail[detail.category.isin(['added_common','removed_common','direction_changed','entry_time_changed','same_entry_changed_outcome'])]
        periods={};slices=[]
        for period,(start,end) in PERIODS.items():
            dates=[d for d in full_dates if start<=d<=end]
            t=b[b.trade_date.isin(dates)]
            daily=t.groupby('trade_date').net_points.sum().reindex(dates,fill_value=0)
            index=len(tests)
            tests.append({'strategy':s,'test':period+'_mean_daily_profit','eligible_days':len(dates),
                          'estimate_mean_daily_points':float(daily.mean()),**engine.bootstrap(daily)})
            periods[period]={'metrics':simple_metrics(t,dates),'sensitivity':sensitivities(t,dates),'test_index':index}
            for side,label in [(1,'long'),(-1,'short')]:
                slices.append({'period':period,'dimension':'direction','group':label,
                               **simple_metrics(t[t.direction.eq(side)],dates)})
            for inside,label in [(True,'first20_after_roll'),(False,'outside_roll_window')]:
                ds=[d for d in dates if (d in window_dates)==inside]
                core=sorted(set(ds)&common)
                old_t=a[a.trade_date.isin(core)];new_t=b[b.trade_date.isin(core)]
                slices.append({'period':period,'dimension':'roll_window','group':label,
                               **simple_metrics(t[t.trade_date.isin(ds)],ds),
                               'common148_old_net_points':float(old_t.net_points.sum()),
                               'common148_new_net_points':float(new_t.net_points.sum()),
                               'common148_delta_points':float(new_t.net_points.sum()-old_t.net_points.sum()),
                               'changed_common_days':int(changed.trade_date.isin(core).sum())})
        for month in sorted({d[:7] for d in full_dates}):
            ds=[d for d in full_dates if d.startswith(month)]
            slices.append({'period':'full','dimension':'month','group':month,**simple_metrics(b[b.trade_date.isin(ds)],ds)})
        common_sorted=sorted(common)
        paired=b[b.trade_date.isin(common)].groupby('trade_date').net_points.sum().reindex(common_sorted,fill_value=0)-a[a.trade_date.isin(common)].groupby('trade_date').net_points.sum().reindex(common_sorted,fill_value=0)
        index=len(tests)
        tests.append({'strategy':s,'test':'paired_common148_improvement','eligible_days':148,
                      'estimate_mean_daily_points':float(paired.mean()),**engine.bootstrap(paired)})
        strategies[s]={'periods':periods,'attribution':categories,'paired_test_index':index,'slices':slices,
                       'changed_common_days':len(changed),
                       'changed_common_days_outside_roll_window':int((~changed.trade_date.isin(window_dates)).sum())}
        assert abs(sum(g['new_net_points'] for g in categories)-b.net_points.sum())<1e-8
        assert abs(sum(g['old_net_points'] for g in categories)-a.loc[a.trade_date.isin(common),'net_points'].sum())<1e-8
        assert len(detail)==159
    assert len(tests)==16
    for row,p in zip(tests,engine.holm([t['p_value'] for t in tests])):row['p_holm_global']=float(p)
    result={'classification':'RETROSPECTIVE_DESCRIPTIVE_STABILITY_AUDIT_NOT_NEW_HOLDOUT',
            'period':PERIODS['full'],'protocol':plan,'protocol_sha256':holdout_data.sha(PROTOCOL),
            'code_sha256':{n:holdout_data.sha(Path(__file__).parent/n) for n in ['volume_stability.py','engine.py','volume_stability_report.py']},
            'roll_windows':windows,'eligible_days':159,'common_days':148,'tests':tests,'global_test_family_size':16,
            'strategies':strategies,
            'limits':['Entire dataset already observed; no independent validation or causal claim.',
                      'Holm applies to the 16 listed tests; subgroup and cost/outlier tables are descriptive, not additional p-value searches.',
                      'Bootstrap intervals nominal 95%, not simultaneous; 2000 draws and few regimes limit precision.',
                      'Higher-cost scenarios alter only costs on identical fills; no market-impact or order-book execution simulation.',
                      'Rollover-window concentration also reflects where the reference construction differs; it is not independent evidence of a tradable rollover effect.',
                      'Closed-trade drawdown only; strategies not combined as a portfolio.']}
    result=engine.clean(result)
    from .volume_stability_report import report
    output.mkdir(parents=True,exist_ok=True)
    pd.concat(details).to_csv(output/'trade-attribution.csv',index=False)
    (output/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (output/'REPORT.md').write_text(report(result))
    assert all(holdout_data.sha(ROOT/p)==h for p,h in plan['frozen_sha256'].items())
    if publish:
        (ROOT/'public/data/research-volume-stability.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        (ROOT/'public/data/research-volume-stability.md').write_text(report(result))
        (ROOT/'docs/VOLUME_STABILITY_AUDIT.md').write_text(report(result))
    print(json.dumps({'status':'PASS','tests':16,'output':str(output),
                      'periods':{s:{p:v['metrics']['net_points'] for p,v in d['periods'].items()} for s,d in strategies.items()}},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--register',action='store_true')
    parser.add_argument('--publish',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/volume-stability')
    args=parser.parse_args()
    if args.register:register()
    else:audit(args.output,args.publish)
