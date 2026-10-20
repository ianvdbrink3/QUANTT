"""Independent output reconciliations and final report/manifest refresh."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
from . import engine as batch

def main():
    root=batch.ROOT
    out=root/'dashboard'
    master=pd.read_parquet(root/'data/overnight_nq/NQ_point_in_time_1min.parquet')
    daily=pd.read_csv(out/'daily_features.csv')
    base=pd.read_csv(out/'baseline_paths.csv')
    trades=pd.read_csv(out/'strategy_trades.csv')
    results=json.loads((out/'experiments.json').read_text())
    q=json.loads((out/'quality.json').read_text())
    checks=json.loads((out/'verification.json').read_text())
    assert all(checks.values())
    assert len(master)==106678 and len(daily)==78
    assert daily.missing_minutes.sum()==32
    assert daily.data_quality_flag.eq('ok').sum()==67
    assert master.contract.nunique()==2
    assert master.groupby('trade_date').contract.nunique().eq(1).all()
    assert master.contract.eq('NQH25').equals(master.trade_date.le('2025-03-18'))
    # Paired long/short baselines reconcile algebraically before and after costs.
    paired=base.groupby(['trade_date','entry_ny','horizon']).agg(n=('direction','size'),gross=('gross_points','sum'),net=('net_points','sum'))
    assert paired.n.eq(2).all() and np.allclose(paired.gross,0)
    assert np.allclose(paired.net,-2*batch.COST)
    assert (base[['mfe_points','mae_points']]>=0).all().all()
    for r in results:
        t=trades.loc[trades.strategy.eq(r['name'])]
        if r['quality_view']=='clean':
            t=t.loc[t.data_quality_flag.eq('ok')]
        assert len(t)==r['metrics']['trades']
        assert np.isclose(t.net_points.sum(),r['metrics']['net_points'])
        assert np.isclose(t.net_usd.sum(),r['metrics']['net_usd'])
        assert all(not x for x in [r['validated_edge'],r['significant_holm_005']])
        for half,met in r['splits'].items():
            assert np.isclose(t.loc[t.half.eq(half),'net_points'].sum(),met['net_points'])
    # Confirm M25 PDH on roll day is really the prior M25 RTH, not H25.
    m=batch.load_contract('NQM25',['','-2','-3'])
    prior=m.loc[(m.trade_date=='2025-03-18') & (m.index>=batch.time_at('2025-03-18','09:30')) & (m.index<batch.time_at('2025-03-18','16:00'))]
    rolled=master.loc[master.trade_date=='2025-03-19']
    assert np.isclose(rolled.pdh.iloc[0],prior.high.max())
    assert np.isclose(rolled.pdl.iloc[0],prior.low.min())
    checks.update(independent_pnl_reconciliation=True,baseline_long_short_cost_identity=True,
                  same_contract_previous_rth_at_roll=True,independent_day_quality_counts=True)
    (out/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
    batch.report(q,results,daily,json.loads((out/'analytics.json').read_text())['conditional_distributions'],checks,pd.read_csv(out/'baseline_distributions.csv'))
    manifest=json.loads((out/'manifest.json').read_text())
    manifest['exports']=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(list(out.glob('*'))+list((root/'data/overnight_nq').glob('*')))
                         if p.is_file() and p.name!='manifest.json']
    manifest['code_version']=batch.hashfile(Path(batch.__file__))
    manifest['verification_code_version']=batch.hashfile(Path(__file__))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for row in manifest['exports']:
        p=root/row['path']
        assert p.is_file() and p.stat().st_size==row['bytes'] and batch.hashfile(p)==row['sha256']
    assert (root/'OVERNIGHT_RESEARCH_REPORT_2026-10-20.md').read_bytes()==(out/'OVERNIGHT_RESEARCH_REPORT_2026-10-20.md').read_bytes()
    print(json.dumps({'files_verified':len(manifest['exports']),'baseline_paths':len(base),'strategy_trades':len(trades),'verification':checks},indent=2))
