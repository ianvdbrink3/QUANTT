"""Publish allowlisted aggregates and byte-identical reports, never raw ledgers."""
import csv
import json
from pathlib import Path

from scripts.same_contract import __main__ as source

ROOT=source.ROOT
PUBLIC=ROOT/'public/data/operational-consolidation.json'
REGISTER=ROOT/'public/data/operational-research-register.json'
MANIFEST=ROOT/'research/operational-publication-manifest.json'
PLAYBOOK=ROOT/'docs/OPERATIONAL_TRADING_PLAYBOOK.md'
MODELS=source.MODELS
BLOCKS=source.BLOCKS
SCALARS=('N','net_R','net_points','trade_PF_R','sharpe_daily_R',
         'max_marked_drawdown_R','max_marked_drawdown_points','positive_quarters_R',
         'positive_quarters_points','traded_quarters','cash_days')
INFERENCE=('mean_net_R_per_cash_day','mean_ci95','expected_total_R_ci95',
           'mean_familywise95_bonf15','nominal_ci_strictly_positive',
           'simultaneous_ci_strictly_positive','p_raw_two_sided','p_holm15','scope')


def payload():
    source.verify()
    result=json.loads(source.RESULT.read_text())
    samples={}
    for sample in source.SAMPLES:
        samples[sample]={}
        for period in BLOCKS:
            samples[sample][period]={}
            for model in MODELS:
                original=result['samples'][sample][period][model]
                row={k:original[k] for k in SCALARS}
                row['inference']={k:original['inference'][k] for k in INFERENCE if k in original['inference']}
                row['quarterly']=[{k:q[k] for k in ('quarter','N','net_R','net_points')} for q in original['quarterly']]
                samples[sample][period][model]=row
    sections=[]
    for part in PLAYBOOK.read_text().split('\n## ')[1:]:
        title,body=part.split('\n',1)
        sections.append(dict(title=title,body=body.strip()))
    return dict(schema='QUANT_OPERATIONAL_PUBLIC_V2_SAME_CONTRACT',date='2026-10-25',
                status='EXPLORATORY_NOT_INDEPENDENTLY_VALIDATED',
                entry_sessions=1151,cash_sessions=1171,quarters=19,
                eras=['2019-2021','2024-2026'],continuous_five_year_record=False,
                live_trading_approved=False,raw_data_published=False,new_backtest_run=True,
                rollover_timing_status='PREOPEN_ROUTE_SAME_CONTRACT_TO_NEXT_CASH_OPEN',
                comparison=result['comparison'],contract_selection=result['contract_selection'],
                source_result_sha256=source.h.sha(source.RESULT),
                samples=samples,coverage=result['coverage'],criteria=result['criteria'],
                inference=dict(replications=20000,block_months=2,primary_tests=15,
                    type='Basic joint month-block bootstrap; nominal95%CI and two-sided p, Holm15',
                    expected_total_ci='Mean cash-day R interval times fixed daycount',
                    selection='Already consumed development data; correction only this round'),
                playbook=dict(report='/reports/OPERATIONAL_TRADING_PLAYBOOK.md',
                    sha256=source.h.sha(PLAYBOOK),sections=sections,
                    capital_risk_note='ATR-scaled exposure is not a maximum loss. S2 overnight has no stop-based loss bound.',
                    mnq_specification_source='https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html'),
                reports=dict(full='/reports/SAME_CONTRACT_CAUSAL_EXECUTION.md',archive='/reports/REGIME_CONSOLIDATION_STATISTICS.md',archive_data='/data/operational-consolidation-archive.json',
                    performance='/reports/SAME_CONTRACT_PERFORMANCE.csv',
                    quarters='/reports/SAME_CONTRACT_QUARTERS.csv'))


def publish():
    result=payload();source.h.dump(PUBLIC,result)
    folder=ROOT/'public/reports';folder.mkdir(parents=True,exist_ok=True)
    reports={PLAYBOOK:folder/PLAYBOOK.name,source.REPORT:folder/source.REPORT.name,
             ROOT/'docs/OPERATIONAL_TRADING_PLAYBOOK_PRE_CAUSAL_ARCHIVE.md':folder/'OPERATIONAL_TRADING_PLAYBOOK_PRE_CAUSAL_ARCHIVE.md',
             source.OUT/'run1/performance-inference.csv':folder/'SAME_CONTRACT_PERFORMANCE.csv'}
    for origin,target in reports.items():target.write_bytes(origin.read_bytes())
    quarterfile=folder/'SAME_CONTRACT_QUARTERS.csv'
    with quarterfile.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['sample','period','model','quarter','N','net_R','net_points'])
        writer.writeheader()
        for sample in source.SAMPLES:
            for period in BLOCKS:
                for model in MODELS:
                    for row in result['samples'][sample][period][model]['quarterly']:
                        writer.writerow(dict(sample=sample,period=period,model=model,**row))
    register=dict(status=result['status'],dashboard='/research/operational',
        entries=[dict(id='NQ-SAME-CONTRACT-20261025',title='Causale contractcorrectie en vergelijking met archief',status=result['status'],independent_validation=False,report=result['reports']['full'],data='/data/operational-consolidation.json'),
                 dict(id='NQ-S1-S2-CONSOLIDATION-ARCHIVE-20261025',title='S1 en S2: consolidatie, onzekerheid en alle kwartalen',
                      status=result['status'],independent_validation=False,report=result['reports']['archive'],data=result['reports']['archive_data']),
                 dict(id='NQ-OPERATIONAL-PLAYBOOK-20261025',title='Dagelijkse regels en MNQ-sizing-playbook',
                      status='RESEARCH_AND_PAPER_EXECUTION_SPECIFICATION',independent_validation=False,report=result['playbook']['report'])],
        previous_register='/data/research-register.json',raw_data_published=False)
    source.h.dump(REGISTER,register)
    paths=[PUBLIC,REGISTER,*reports.values(),quarterfile,ROOT/'public/data/operational-consolidation-archive.json']
    manifest=dict(status='PUBLIC_AGGREGATES_AND_RESEARCH_PLAYBOOK_READY',new_signals_computed=True,
        raw_data_published=False,source_report_sha256=source.h.sha(source.REPORT),
        source_verification_sha256=source.h.sha(source.PROOF),
        files_sha256={str(p.relative_to(ROOT)):source.h.sha(p) for p in paths},
        source_files_sha256={str(p.relative_to(ROOT)):source.h.sha(p) for p in (PLAYBOOK,source.RESULT,source.REPORT,source.PROOF)})
    source.h.dump(MANIFEST,manifest);source.verify()
    return dict(status=manifest['status'],public_files=len(paths),raw_data_published=False)


if __name__=='__main__':print(json.dumps(publish(),indent=2))
