"""New local aggregate dashboard; no modifications to old research or production."""
import json
from scripts.judas_replacement import __main__ as run

ROOT=run.ROOT
PUBLIC=ROOT/'public/data/judas-replacement.json'
MANIFEST=ROOT/'research/judas-replacement-publication.json'
WIN=('model','fill','period','N','net_ATR_R','net_stop_R','net_points','winrate','PF_ATR_R','PF_stop_R','sharpe_ATR_R','sharpe_stop_R','max_marked_drawdown_ATR_R','max_marked_drawdown_stop_R','positive_quarters_ATR_R')
PORT=('N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R','max_marked_drawdown_points','positive_quarters_R','cash_days')


def publish():
    run.verify();x=json.loads(run.RESULT.read_text())
    performance={b:{m:{**{k:r[k] for k in PORT},'winrate':r['points']['winrate'],'calendar_quarters':len(r['quarterly']),'quarterly':r['quarterly']} for m,r in rows.items()} for b,rows in x['performance'].items()}
    data=dict(status=x['status'],baseline_commit=run.METHOD['baseline_commit'],cash_sessions=1171,
        selected_Judas=run.JUDAS,winner_names=x['winner_names'],winner_rows=[{k:r[k] for k in WIN} for r in x['winner_rows']],
        performance=performance,inference=x['inference'],bootstrap=x['bootstrap'],overlap=x['overlap'],quality=x['quality'],method=run.METHOD,
        reports=dict(full='/reports/JUDAS_ONE_FOR_ONE_REPLACEMENT.md',portfolios='/reports/JUDAS_PORTFOLIO_PERFORMANCE.csv',winners='/reports/SEVEN_ICT_VARIANTS.csv',inference='/reports/JUDAS_REPLACEMENT_INFERENCE.csv'),
        raw_data_published=False,independent_validation=False)
    run.h.dump(PUBLIC,data)
    folder=ROOT/'public/reports';folder.mkdir(parents=True,exist_ok=True)
    copies={run.REPORT:folder/run.REPORT.name,run.OUT/'run1/portfolio-performance.csv':folder/'JUDAS_PORTFOLIO_PERFORMANCE.csv',run.OUT/'run1/seven-variants.csv':folder/'SEVEN_ICT_VARIANTS.csv',run.OUT/'run1/inference.csv':folder/'JUDAS_REPLACEMENT_INFERENCE.csv'}
    for a,b in copies.items():b.write_bytes(a.read_bytes())
    files=[PUBLIC,*copies.values(),ROOT/'scripts/publish_judas_replacement.py',ROOT/'app/research/judas-replacement/page.tsx']
    run.h.dump(MANIFEST,dict(status='LOCAL_APPEND_ONLY_JUDAS_COMPARISON_READY',files_sha256={str(p.relative_to(ROOT)):run.h.sha(p) for p in files},source_verification_sha256=run.h.sha(run.PROOF),prior_files_unchanged=True))
    run.verify();return dict(status='LOCAL_DASHBOARD_READY',winner_rows=len(data['winner_rows']),raw_data_published=False)


if __name__=='__main__':print(json.dumps(publish(),indent=2))
