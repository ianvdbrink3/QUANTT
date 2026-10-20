"""Audit, stress-test and publish only derived NQ aggregates to local preview sources."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from . import engine as batch

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'artifacts/reproduction'
APP=ROOT
sys.path.insert(0,str(REPO/'src'))
from quantlab.futures_import import stage_futures_csv
from quantlab.observed_release09 import export_observed


def main():
    dashboard=ROOT/'dashboard'
    manifest=json.loads((dashboard/'manifest.json').read_text())
    for item in manifest['exports']:
        assert batch.hashfile(ROOT/item['path'])==item['sha256'],item['path']
    master=pd.read_parquet(ROOT/'data/overnight_nq/NQ_point_in_time_1min.parquet')
    trades=pd.read_csv(dashboard/'strategy_trades.csv',parse_dates=['signal_utc','entry_utc','exit_bar_utc'])
    experiments=json.loads((dashboard/'experiments.json').read_text())
    quality=json.loads((dashboard/'quality.json').read_text())
    daily=pd.read_csv(dashboard/'daily_features.csv')
    # Use the 0.9 gate on canonical contract-native OHLCV, privately. No altered backtest definitions.
    private=APP/'artifacts/nq-overnight'
    private.mkdir(parents=True,exist_ok=True)
    canonical=master[['contract',*batch.source.FIELDS]].rename(columns={'contract':'contract_id'})
    csv=private/'NQ.csv'
    canonical.to_csv(csv,date_format='%Y-%m-%dT%H:%M:%SZ')
    staged=private/'NQ.parquet'
    imported=stage_futures_csv(csv,staged,instrument='NQ',source='Barchart user-supplied individual contract exports')
    staged.with_suffix('.quality.json').write_text(json.dumps(imported,indent=2,default=str)+'\n')
    observed=export_observed([staged],private/'descriptive09.json')
    assert observed['row_count']==len(master)==106678
    controls=[]
    for _,r in trades.iterrows():
        g=master.loc[master.trade_date.eq(r.trade_date)]
        stopdist=abs(r.entry_price-r.stop); targetdist=abs(r.target-r.entry_price)
        mirror=batch.simulate(g,r.signal_utc,-int(r.direction),stopdist,targetdist=targetdist)
        replay=batch.simulate(g,r.signal_utc,int(r.direction),stopdist,targetdist=targetdist)
        assert mirror is not None and replay is not None
        assert np.isclose(replay['net_points'],r.net_points),r.strategy
        controls.append({'strategy':r.strategy,'trade_date':r.trade_date,'actual_net_points':r.net_points,
                         'opposite_net_points':mirror['net_points'],
                         'coinflip_expected_points':(r.net_points+mirror['net_points'])/2,
                         'paired_excess_points':(r.net_points-mirror['net_points'])/2})
    controls=pd.DataFrame(controls)
    controls.to_csv(private/'direction_controls.csv',index=False)
    summary=[]
    for r in experiments:
        if r['quality_view']!='all':
            continue
        t=trades.loc[trades.strategy.eq(r['name'])].sort_values('trade_date')
        c=controls.loc[controls.strategy.eq(r['name'])]
        eligible=pd.read_csv(dashboard/'strategy_eligibility.csv')
        dates=eligible.loc[eligible.strategy.eq(r['name']) & eligible.eligible,'trade_date'].tolist()
        delta=c.set_index('trade_date').paired_excess_points.reindex(dates,fill_value=0)
        ranked=t.net_points.sort_values(ascending=False)
        best_removed={str(n):float(ranked.iloc[n:].sum()) for n in [1,3]}
        loo=[float(t.net_points.sum()-x) for x in t.net_points]
        monthly=[{'month':month,'trades':len(g),'net_points':float(g.net_points.sum())}
                 for month,g in t.groupby(t.trade_date.str[:7])]
        summary.append({'id':r['name'],'metrics':r['metrics'],'splits':r['splits'],
                        'cost_scenarios':r['cost_scenarios'],'holm_original':r['holm_adjusted_p'],
                        'monthly':monthly,'net_points_without_best':best_removed,
                        'leave_one_trade_out_net_points_min':min(loo) if loo else None,
                        'coinflip_expected_net_points':float(c.coinflip_expected_points.sum()),
                        'paired_excess_total_points':float(c.paired_excess_points.sum()),
                        'paired_daily_inference':batch.bootstrap(delta),
                        'candidate':r['positive_both_halves_min10_trades'],'edge_validated':False,
                        'equity':r['equity']})
    # Correct across both profitability and directional-excess screens, not only favorable results.
    ps=[r['metrics']['p_value'] for r in summary]+[r['paired_daily_inference']['p_value'] for r in summary]
    adjusted=batch.holm(ps)
    for i,r in enumerate(summary):
        r['holm_joint_profit_p']=float(adjusted[i])
        r['holm_joint_direction_p']=float(adjusted[i+len(summary)])
    daily_public=daily[['trade_date','contract','data_quality_flag','missing_minutes','atr_history_count']].to_dict('records')
    condition=pd.read_csv(dashboard/'conditional_distributions.csv')
    regime=condition.loc[condition.quality_view.eq('all')&condition.half.eq('all')&condition.entry_ny.eq('09:30')&condition.horizon.eq('60m')&condition.direction.eq(1)]
    bundle={'schema_version':'nq-overnight-1','classification':'OBSERVED NQ — SOURCE UNVERIFIED',
            'status':'EXPLORATORY_NO_VALIDATED_EDGE','generated_at':pd.Timestamp.now(tz='UTC'),
            'period':['2024-12-30','2025-04-17'],'row_count':len(master),'trade_dates':quality['trade_dates'],
            'clean_days':quality['clean_days'],'flagged_days':quality['flagged_days'],'missing_minutes':quality['missing_minutes'],
            'atr_ready_days':quality['atr_ready_days'],'eligible_days':next(r['metrics']['eligible_days'] for r in experiments if r['name']=='B_ORB15' and r['quality_view']=='all'),
            'cost_rt_usd':24.5,'roll_trade_date':'2025-03-19','edge_validated':False,
            'dataset_sha256':batch.hashfile(ROOT/'data/overnight_nq/NQ_point_in_time_1min.parquet'),
            'source_csv_hashes':[x['sha256'] for x in quality['source_hashes']],
            'import_gate':{'passed':True,'rows':observed['row_count'],'run_id':observed['run_id'],
                           'synthetic_input':False,'calendar_certified':False,'source_authenticated':False},
            'strategies':summary,'day_quality':daily_public,'overnight_regimes':regime.to_dict('records'),
            'baseline':pd.read_csv(dashboard/'baseline_distributions.csv').loc[lambda x:x.quality_view.eq('all')&x.half.eq('all')&x.entry_ny.eq('09:30')&x.direction.eq(1)].to_dict('records'),
            'methodology':json.loads((dashboard/'methodology.json').read_text()),
            'checks':json.loads((dashboard/'verification.json').read_text()),
            'limitations':['Historical Dec2024–Apr2025 only, not current market signals.',
                           'No independent holdout; additional robustness probes viewed after original results.',
                           'Direction control uses same selected entries/risk distances, not a randomized independent experiment.',
                           'Cost estimates and OHLC fill model, not broker-verified execution.',
                           'HLC3 VWAP proxy; raw data, local paths and trade-level prices not published.',
                           'Strategy equities are independent screens, not an additive investment portfolio.',
                           'Broad overnight regime has only three observations; no reliable edge conclusion.',
                           'Vendor redistribution rights are not certified; only derived aggregate research exported.']}
    public=APP/'public/data/nq-overnight.json'
    public.write_text(json.dumps(batch.clean(bundle),indent=2,allow_nan=False)+'\n')
    # Existing route receives actual staged source aggregates, not a fictional AWAITING_INPUT placeholder.
    export_observed([staged],APP/'public/data/research09.json',publication_approved=True)
    local=ROOT/'dashboard/EDGE_ROBUSTNESS_2026-10-20.json'
    local.write_text(json.dumps(batch.clean(summary),indent=2,allow_nan=False)+'\n')
    lines=['# NQ edge-robuustheid — 20 oktober 2026','',
           'Vaste hypothesen uit de nachtbatch, geen parameteroptimalisatie. Dit is aanvullend exploratief onderzoek op reeds bekeken data, geen nieuwe holdout.','',
           '| Test | n | Netto punten | PF | Zonder beste trade | Zonder beste 3 | Omgekeerde richting: verwachte coinflip punten | Gezamenlijke Holm p (winst) |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in summary:
        lines.append(f"| {r['id']} | {r['metrics']['trades']} | {r['metrics']['net_points']:.2f} | {r['metrics']['profit_factor']:.2f} | {r['net_points_without_best']['1']:.2f} | {r['net_points_without_best']['3']:.2f} | {r['coinflip_expected_net_points']:.2f} | {r['holm_joint_profit_p']:.3f} |")
    lines += ['','ORB15 is een onderzoekskandidaat, geen statistisch bevestigde edge. Vergelijk de twee helften, hogere slippage en uitbijtergevoeligheid. De directionele controle is geconditioneerd op dezelfde signalen en instaptijden en bewijst geen onafhankelijke alpha.','',
              'De 0.9-importgate heeft alle 106.678 echte aangeleverde NQ-bars privé verwerkt. De oude 0.9-events en onze kostenbacktests blijven afzonderlijk gelabeld: andere regels geven andere uitkomsten. Raw CSV/Parquet en uitvoeringsprijzen blijven buiten de deployment.']
    (ROOT/'dashboard/EDGE_ROBUSTNESS_2026-10-20.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'staged_rows':observed['row_count'],'public_bytes':public.stat().st_size,
                       'strategies':[{k:r[k] for k in ['id','net_points_without_best','holm_joint_profit_p','holm_joint_direction_p']} for r in summary]},indent=2))


if __name__=='__main__':
    main()
