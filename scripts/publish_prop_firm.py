"""Append verified aggregate research, guides and an explicit public registry."""
import json
from scripts.prop_firm import __main__ as run

ROOT=run.ROOT
PUBLIC=ROOT/'public/data/prop-firm.json'
MANIFEST=ROOT/'research/prop-firm-publication.json'
GUIDE=ROOT/'docs/PROP_FIRM_AND_AUTOMATION_GUIDE.md'
PLAYBOOK=ROOT/'docs/OPERATIONAL_TRADING_PLAYBOOK_V3.md'
FIELDS=('N','net_R','net_points','trade_PF_R','sharpe_daily_R','max_marked_drawdown_R',
        'max_marked_drawdown_points','positive_quarters_R','cash_days','quarterly')


def publish():
    run.verify();x=json.loads(run.RESULT.read_text())
    # The old playbook is protected by nested freeze manifests. Publish a version
    # that embeds those exact original bytes, then adds the new research appendix.
    original=(ROOT/'docs/OPERATIONAL_TRADING_PLAYBOOK.md').read_bytes()
    intro=('# QUANT — Operationeel playbook V3: referentie en prop-uren\n\n'
           'De onderstaande oorspronkelijke specificatie blijft ongewijzigd. '
           'S1/S2 met B zijn de vaste referentie; Judas-vervanging en 18:00 zijn '
           'afzonderlijke ontwikkelingsvarianten, niet onafhankelijk gevalideerd. '
           'De nieuwe uitvoeringsgids staat in het aanhangsel.\n\n'
           '[Alle ICT-varianten](/research/ict) · [Zeven Judas-varianten](/research/judas-replacement) · '
           '[Prop-uren en risico](/research/prop-firm)\n\n---\n\n').encode()
    PLAYBOOK.write_bytes(intro+original+b'\n\n---\n\n'+GUIDE.read_bytes())
    reports=dict(full='/reports/PROP_FIRM_FEASIBILITY_REPORT.md',guide='/reports/PROP_FIRM_AND_AUTOMATION_GUIDE.md',
                 playbook='/reports/OPERATIONAL_TRADING_PLAYBOOK_V3.md',performance='/reports/PROP_PORTFOLIO_PERFORMANCE.csv',
                 mnq='/reports/PROP_MNQ_STRESS.csv',accounts='/reports/PROP_ACCOUNT_CHECKS.csv',registry='/data/ict-prop-research-register.json')
    data=dict(status=x['status'],baseline_commit='2ec3a07',cash_sessions=1171,
              performance={b:{m:{**{k:r[k] for k in FIELDS},'winrate':r['points']['winrate']} for m,r in rows.items()} for b,rows in x['performance'].items()},
              dollar_stress=x['dollar_stress'],account_checks=x['account_checks'],rules=x['rules'],method=x['method'],
              coverage=x['coverage'],paired_timing=x['paired_timing'],reports=reports,
              raw_data_published=False,independent_validation=False,full_compliance_certified=False,
              verification_status=json.loads(run.PROOF.read_text())['status'])
    run.h.dump(PUBLIC,data)
    dest=ROOT/'public/reports';dest.mkdir(parents=True,exist_ok=True)
    copies={run.REPORT:dest/run.REPORT.name,GUIDE:dest/GUIDE.name,PLAYBOOK:dest/PLAYBOOK.name,
            run.OUT/'run1/portfolio-performance.csv':dest/'PROP_PORTFOLIO_PERFORMANCE.csv',
            run.OUT/'run1/mnq-stress.csv':dest/'PROP_MNQ_STRESS.csv',
            run.OUT/'run1/account-checks.csv':dest/'PROP_ACCOUNT_CHECKS.csv'}
    for a,b in copies.items():b.write_bytes(a.read_bytes())
    register=ROOT/'public/data/ict-prop-research-register.json'
    entries=[dict(id='baseline-2ec3a07',status='FROZEN_DEVELOPMENT_REFERENCE',page='/research/operational',report='/reports/OPERATIONAL_TRADING_PLAYBOOK.md'),
             dict(id='ict-80',status='EXPLORATORY_SELECTED_ON_DEVELOPMENT_POOL',page='/research/ict',report='/reports/ICT_CAUSAL_DEVELOPMENT_STUDY.md',performance_rows=480),
             dict(id='judas-seven-and-replacement',status='EXPLORATORY_NOT_INDEPENDENTLY_VALIDATED',page='/research/judas-replacement',report='/reports/JUDAS_ONE_FOR_ONE_REPLACEMENT.md',selected_variants=7),
             dict(id='prop-hours-feasibility',status=x['status'],page='/research/prop-firm',report=reports['full'],performance_rows=36,MNQ_stress_rows=108,account_checks=936),
             dict(id='playbook-v3',status='DESIGN_ONLY_NO_BROKER_INTEGRATION_ACTIVE',report=reports['playbook'],guide=reports['guide'])]
    run.h.dump(register,dict(baseline_commit='2ec3a07',entries=entries,private_market_data_published=False))
    files=[PUBLIC,register,*copies.values(),GUIDE,PLAYBOOK,ROOT/'scripts/publish_prop_firm.py',
           ROOT/'app/research/prop-firm/page.tsx',ROOT/'proxy.ts',ROOT/'scripts/build_prop_frontend.py',ROOT/'tests/test_prop_publication.py']
    run.h.dump(MANIFEST,dict(status='VERIFIED_AGGREGATE_PUBLICATION_READY',files_sha256={str(p.relative_to(ROOT)):run.h.sha(p) for p in files},
                           verification_sha256=run.h.sha(run.PROOF),baseline_preserved=True,raw_data_published=False))
    run.verify()
    return dict(status='PUBLICATION_READY',performance_rows=36,MNQ_stress_rows=108,account_checks=936)


if __name__=='__main__':print(json.dumps(publish(),indent=2))
