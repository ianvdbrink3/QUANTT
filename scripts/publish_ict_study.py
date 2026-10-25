"""Append-only local dashboard export. No Git push or production deployment."""
import csv
import json
from scripts.ict_study import __main__ as run
from scripts import ict_study_assessment as assessment

ROOT=run.ROOT
PUBLIC=ROOT/'public/data/ict-study.json'
MANIFEST=ROOT/'research/ict-study-publication-manifest.json'
SCALARS=('N','net_ATR_R','net_stop_R','net_points','gross_points','winrate','PF_ATR_R','PF_stop_R',
         'sharpe_ATR_R','sharpe_stop_R','max_marked_drawdown_ATR_R','max_marked_drawdown_stop_R',
         'max_marked_drawdown_points','positive_quarters_ATR_R','positive_quarters_stop_R','traded_quarters','cash_days')


def publish():
    run.verify();summary=json.loads(run.RESULT.read_text());compare=assessment.assess()
    rows=[]
    for fill in ('TOUCH','TRADE_THROUGH'):
        for period in run.PERIODS:
            for spec in run.SPECS:
                x=summary['samples'][fill][period][spec.name]
                rows.append(dict(fill=fill,period=period,model=spec.name,**spec.__dict__,**{k:x[k] for k in SCALARS},
                    calendar_quarters=len(x['quarterly']),quarterly=x['quarterly'],direction=x['direction'],
                    inference=summary['inference'][period][spec.name] if fill=='TOUCH' else None,
                    portfolio=summary['portfolio'][period][spec.name] if fill=='TOUCH' else None))
    benches={p:{name:{k:x[k] for k in ('N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R','max_marked_drawdown_points','positive_quarters_R','traded_quarters')} for name,x in summary['benchmarks'][p].items()} for p in run.PERIODS}
    data=dict(status=run.METHOD['status'],benchmark_commit=run.METHOD['benchmark_commit'],cash_sessions=1171,ATR_ready_sessions=1151,variants=80,
              source_replays='BYTE_IDENTICAL_ICT_SOURCE_REPLAYS',future_cutoff_checks=summary['future_cutoff_checks'],
              inference_tests=480,rows=rows,coverage=summary['coverage'],benchmarks=benches,assessment=compare,
              method=run.METHOD,raw_data_published=False,independent_validation=False,
              reports=dict(findings='/reports/ICT_STUDY_FINDINGS.md',full='/reports/ICT_CAUSAL_DEVELOPMENT_STUDY.md',comparison='/reports/ICT_COMPARISON_WITH_BENCHMARKS.md',
                           performance='/reports/ICT_PERFORMANCE.csv',quarters='/reports/ICT_QUARTERS.csv'))
    run.h.dump(PUBLIC,data)
    folder=ROOT/'public/reports';folder.mkdir(parents=True,exist_ok=True)
    copies={ROOT/'docs/ICT_STUDY_FINDINGS.md':folder/'ICT_STUDY_FINDINGS.md',run.REPORT:folder/run.REPORT.name,ROOT/'docs/ICT_COMPARISON_WITH_BENCHMARKS.md':folder/'ICT_COMPARISON_WITH_BENCHMARKS.md',run.OUT/'run1/performance.csv':folder/'ICT_PERFORMANCE.csv'}
    for src,dst in copies.items():dst.write_bytes(src.read_bytes())
    qfile=folder/'ICT_QUARTERS.csv'
    with qfile.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['fill','period','model','quarter','N','net_ATR_R','net_points']);writer.writeheader()
        for row in rows:
            for q in row['quarterly']:
                writer.writerow(dict(fill=row['fill'],period=row['period'],model=row['model'],quarter=q['quarter'],N=q['N'],net_ATR_R=q['net_R'],net_points=q['net_points']))
    files=[PUBLIC,*copies.values(),qfile,ROOT/'research/ict-study-assessment.json',ROOT/'docs/ICT_COMPARISON_WITH_BENCHMARKS.md',ROOT/'scripts/publish_ict_study.py',ROOT/'app/research/ict/page.tsx',ROOT/'components/ICTStudyTable.tsx']
    run.h.dump(MANIFEST,dict(status='LOCAL_ICT_DASHBOARD_EXPORT_READY_BENCHMARK_UNCHANGED',files_sha256={str(p.relative_to(ROOT)):run.h.sha(p) for p in files},source_verification_sha256=run.h.sha(run.PROOF),raw_data_published=False))
    run.verify();return dict(status='LOCAL_DASHBOARD_READY',rows=len(rows),public_data_bytes=PUBLIC.stat().st_size,raw_data_published=False)


if __name__=='__main__':print(json.dumps(publish(),indent=2))
