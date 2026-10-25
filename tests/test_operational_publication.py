import csv
import json
import subprocess
from pathlib import Path

import pytest

from scripts import publish_operational_playbook as p
from scripts import build_operational_frontend as release

NODE=Path('/Users/ianvandenbrink/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')


def test_public_aggregates_exactly_match_frozen_results():
    public=json.loads(p.PUBLIC.read_text());raw=json.loads(p.source.RESULT.read_text())
    for sample in p.source.SAMPLES:
        for period in p.BLOCKS:
            for model in p.MODELS:
                row=public['samples'][sample][period][model]
                original=raw['samples'][sample][period][model]
                assert set(row)==set(p.SCALARS)|{'inference','quarterly'}
                for key in p.SCALARS:assert row[key]==original[key]
                assert row['quarterly']==original['quarterly']
                assert row['inference']=={k:v for k,v in original['inference'].items() if k in p.INFERENCE}


def test_no_private_series_or_ledger_exported():
    public=json.loads(p.PUBLIC.read_text())
    forbidden={'trades','ledger','marks','path_points','daily','net_R_matrix','open','high','low','close','volume','timestamps','entry_price','exit_price','source_verification'}
    def check(value):
        if isinstance(value,dict):
            assert not forbidden&set(value)
            for v in value.values():check(v)
        elif isinstance(value,list):
            for v in value:check(v)
    check(public)
    assert public['raw_data_published'] is False
    assert public['live_trading_approved'] is False
    assert public['continuous_five_year_record'] is False


def test_complete_original_report_and_playbook_byte_identical():
    for name in ('OPERATIONAL_TRADING_PLAYBOOK.md','REGIME_CONSOLIDATION_STATISTICS.md'):
        assert (p.ROOT/'docs'/name).read_bytes()==(p.ROOT/'public/reports'/name).read_bytes()
    assert (p.source.archive.OUT/'run1/performance-inference.csv').read_bytes()==(p.ROOT/'public/reports/REGIME_CONSOLIDATION_PERFORMANCE.csv').read_bytes()


def test_public_manifest_and_all_prior_freezes_verified():
    manifest=json.loads(p.MANIFEST.read_text())
    for name,digest in {**manifest['files_sha256'],**manifest['source_files_sha256']}.items():
        assert p.source.h.sha(p.ROOT/name)==digest
    p.source.verify()


def test_all_nineteen_focus_quarters_and_totals_present():
    public=json.loads(p.PUBLIC.read_text())
    rows=list(csv.DictReader((p.ROOT/'public/reports/SAME_CONTRACT_QUARTERS.csv').open()))
    for model in ('S1_SELECTIVE','S2_BROAD_NO_STOP'):
        x=public['samples']['OBSERVED_PATH']['COMBINED'][model]
        q=[r for r in rows if r['sample']=='OBSERVED_PATH' and r['period']=='COMBINED' and r['model']==model]
        assert len(q)==19
        assert sum(int(r['N']) for r in q)==x['N']
        assert sum(float(r['net_R']) for r in q)==pytest.approx(x['net_R'])
        assert sum(float(r['net_points']) for r in q)==pytest.approx(x['net_points'])


def test_playbook_explains_actual_indicator_and_execution_limits():
    text=p.PLAYBOOK.read_text()
    for term in ('geen Wilder-ATR','SMA20_prior','SMA20_terminal','15:55-open','16:00-minuutopen',
                 'q_ATR = floor(K / (2 * A))','q_stop = floor(K / (2*d + c_MNQ))',
                 'Voor S2-overnight is q_stop niet gedefinieerd','PREOPEN_ROUTE_SAME_CONTRACT_TO_NEXT_CASH_OPEN',
                 'geen aaneengesloten vijfjarige trackrecord','MNQM25','geen achteraf-uitsluiting'):
        assert term in text


def test_new_navigation_leaves_existing_layout_byte_identical():
    original=subprocess.check_output(['git','show','3f9e768a312dd260c77054d95659606bd72c5beb:app/research/layout.tsx'],cwd=p.ROOT)
    assert (p.ROOT/'app/research/layout.tsx').read_bytes()==original
    assert '/research/operational' in (p.ROOT/'app/research/template.tsx').read_text()


def sizing(values,leg=None):
    code="import {calculateSizing,calculateForLeg} from './lib/operational-sizing.mjs';\n"
    code+=f'const input={json.dumps(values)};\n'
    code+=f'console.log(JSON.stringify(calculateSizing(input)));' if leg is None else f'console.log(JSON.stringify(calculateForLeg(input,{json.dumps(leg)})));'
    return json.loads(subprocess.check_output([str(NODE),'--input-type=module','-e',code],cwd=p.ROOT))


def inputs(**updates):
    return dict(equity=100000,percent=1,atr=200,cost=6.5,stopDistance=100,**updates) if not updates else {**inputs(),**updates}


def test_budget_and_broker_cost_included_without_minimum_one():
    x=sizing(inputs())
    assert x['budget']==1000 and x['atrQuantity']==2 and x['stopQuantity']==4
    x=sizing(inputs(equity=1000,percent=1))
    assert x['atrQuantity']==0 and x['stopQuantity']==0


def test_unknown_cost_and_margin_stay_unknown():
    x=sizing(inputs(cost=None))
    assert x['stopQuantity'] is None and x['marginCap'] is None and x['cappedStop'] is None
    assert x['atrQuantity']==2


def test_margin_cap_and_zero_budget_respected():
    x=sizing(inputs(freeMargin=2500,marginPerContract=1000))
    assert x['marginCap']==2 and x['cappedStop']==2
    x=sizing(inputs(freeMargin=0,marginPerContract=1000))
    assert x['cappedAtr']==0 and x['cappedStop']==0


@pytest.mark.parametrize('values',[inputs(equity=None),inputs(atr=0),inputs(percent=-1),inputs(percent=101)])
def test_invalid_sizing_inputs_not_executable(values):
    assert sizing(values) is None


def test_unstopped_s2_never_gets_fabricated_stop_risk():
    x=sizing(inputs(stopDistance=100),'S2')
    assert x['stopQuantity'] is None and x['plannedStopDistance'] is None


def test_s1_fixed_stop_rounds_toward_entry():
    x=sizing(inputs(atr=200.3),'S1')
    assert x['plannedStopDistance']==100 and x['stopQuantity']==4


def test_B_requires_tick_valid_actual_distance_at_least_minimum():
    assert sizing(inputs(stopDistance=69.75),'B')['stopQuantity'] is None
    assert sizing(inputs(stopDistance=70.1),'B')['stopQuantity'] is None
    assert sizing(inputs(stopDistance=70),'B')['stopQuantity']==6


def test_no_unconfirmed_default_cost_or_risk_recommendation_in_ui():
    text=(p.ROOT/'components/OperationalSizing.tsx').read_text()
    assert "const [cost,setCost]=useState('')" in text
    assert "const [percent,setPercent]=useState('')" in text
    assert "const [leg,setLeg]=useState('S2')" in text


@pytest.mark.parametrize('name',['data/raw/nqh.csv','data/curated/a.parquet','artifacts/trades.json','private/foo.json',
                               '.env.production','public/data/raw/a.csv','public/data/NQ_in_1_minute.csv',
                               'public/../artifacts/foo.json','public/data/market.parquet'])
def test_clean_release_excludes_private_payloads(name):
    assert not release.allowed(name)


def test_clean_release_allows_frontend_and_aggregate_reports():
    for name in ['app/research/operational/page.tsx','components/OperationalSizing.tsx',
                 'lib/operational-sizing.mjs','public/data/operational-consolidation.json',
                 'public/reports/REGIME_CONSOLIDATION_PERFORMANCE.csv','package.json','vercel.json']:
        assert release.allowed(name)


def test_previous_publication_archive_matches_previous_commit_exactly():
    for old,new in [('docs/OPERATIONAL_TRADING_PLAYBOOK.md','docs/OPERATIONAL_TRADING_PLAYBOOK_PRE_CAUSAL_ARCHIVE.md'),('public/data/operational-consolidation.json','public/data/operational-consolidation-archive.json')]:
        prior=subprocess.check_output(['git','show','426d8a91ddc60d0650d83231a62e809c61b05d66:'+old],cwd=p.ROOT)
        assert (p.ROOT/new).read_bytes()==prior


def test_new_public_causal_report_and_performance_copy_exact():
    assert p.source.REPORT.read_bytes()==(p.ROOT/'public/reports/SAME_CONTRACT_CAUSAL_EXECUTION.md').read_bytes()
    assert (p.source.OUT/'run1/performance-inference.csv').read_bytes()==(p.ROOT/'public/reports/SAME_CONTRACT_PERFORMANCE.csv').read_bytes()
    data=json.loads(p.PUBLIC.read_text())
    assert data['rollover_timing_status']=='PREOPEN_ROUTE_SAME_CONTRACT_TO_NEXT_CASH_OPEN'
    assert len(data['comparison'])==15
