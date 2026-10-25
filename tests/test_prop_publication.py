import csv
import json
from scripts import publish_prop_firm as pub
from scripts.prop_firm import __main__ as run
from scripts.build_prop_frontend import allowed


def test_exact_aggregate_export_and_portfolio_quarters():
    public=json.loads(pub.PUBLIC.read_text());source=json.loads(run.RESULT.read_text())
    for b,rows in public['performance'].items():
        for m,r in rows.items():
            assert all(r[k]==source['performance'][b][m][k] for k in pub.FIELDS)
    assert public['dollar_stress']==source['dollar_stress']
    assert public['account_checks']==source['account_checks']
    assert public['full_compliance_certified'] is False
    assert public['independent_validation'] is False


def test_public_data_has_no_individual_trade_or_price_paths():
    forbidden={'entry_price','exit_price','entry_time','exit_time','path_points','daily_panels','daily-dollar-panels',
               'open','high','low','close','volume','ledgers','adverse_gross_points','source_verification'}
    def visit(v):
        if isinstance(v,dict):
            assert not forbidden&set(v)
            for child in v.values():visit(child)
        elif isinstance(v,list):
            for child in v:visit(child)
    visit(json.loads(pub.PUBLIC.read_text()))


def test_csv_row_counts_and_byte_exact_copies():
    for name,count in [('PROP_PORTFOLIO_PERFORMANCE.csv',36),('PROP_MNQ_STRESS.csv',108),('PROP_ACCOUNT_CHECKS.csv',936)]:
        assert len(list(csv.DictReader((run.ROOT/'public/reports'/name).open())))==count
    for name in ['PROP_FIRM_FEASIBILITY_REPORT.md','PROP_FIRM_AND_AUTOMATION_GUIDE.md','OPERATIONAL_TRADING_PLAYBOOK_V3.md']:
        assert (run.ROOT/'docs'/name).read_bytes()==(run.ROOT/'public/reports'/name).read_bytes()


def test_versioned_playbook_retains_exact_frozen_original_and_current_limits():
    doc=pub.PLAYBOOK.read_bytes();old=(run.ROOT/'docs/OPERATIONAL_TRADING_PLAYBOOK.md').read_bytes()
    assert old in doc
    guide=pub.GUIDE.read_text()
    for phrase in ['geen VPS','Live Funded','30%','55%','15:55','18:00','09:30','0,03','0,10','0,15','geen accountbreuk','geen algemene prop-goedkeuring']:
        assert phrase.lower() in guide.lower()
    assert 'brokerintegratie' in guide


def test_release_allowlist_includes_proxy_without_private_data():
    assert allowed('proxy.ts') and allowed('public/data/prop-firm.json')
    for name in ['artifacts/prop-firm/run1/ledgers.json','data/raw/nqh19.csv','.env.local',
                 'public/data/private/foo.json','public/data/bar.parquet','public/reports/nqh19_intraday-1min.csv',
                 '../proxy.ts','/proxy.ts','scripts/prop_firm/core.py']:
        assert not allowed(name)
    proxy=(run.ROOT/'proxy.ts').read_text()
    assert "matcher: ['/', '/research']" in proxy
    assert "'/research/prop-firm'" in proxy and '307' in proxy
    assert 'fetch(' not in proxy


def test_registry_connects_entire_research_round_and_hashes_match():
    register=json.loads((run.ROOT/'public/data/ict-prop-research-register.json').read_text())
    assert len(register['entries'])==5
    assert any(e.get('performance_rows')==480 for e in register['entries'])
    assert any(e.get('selected_variants')==7 for e in register['entries'])
    for name,digest in json.loads(pub.MANIFEST.read_text())['files_sha256'].items():
        assert run.h.sha(run.ROOT/name)==digest
    run.verify()
