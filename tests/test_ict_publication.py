import csv
import json
from pathlib import Path
import numpy as np
import pytest
from scripts.ict_study import __main__ as run
from scripts import publish_ict_study as pub


def test_all_480_performance_rows_match_verified_source():
    x=json.loads(pub.PUBLIC.read_text());raw=json.loads(run.RESULT.read_text())
    assert len(x['rows'])==480 and len({(r['fill'],r['period'],r['model']) for r in x['rows']})==480
    for row in x['rows']:
        original=raw['samples'][row['fill']][row['period']][row['model']]
        for key in pub.SCALARS:assert row[key]==original[key]
        if row['fill']=='TRADE_THROUGH':assert row['inference'] is None
    csvrows=list(csv.DictReader((run.ROOT/'public/reports/ICT_PERFORMANCE.csv').open()))
    assert len(csvrows)==480


def test_append_only_export_contains_no_raw_bars_or_ledgers():
    x=json.loads(pub.PUBLIC.read_text())
    banned={'entry_price','exit_price','entry_time','exit_time','path_points','entry_bar','exit_bar','open','high','low','close','volume','timestamps','daily_panels','source_verification'}
    def visit(v):
        if isinstance(v,dict):
            assert not banned&set(v)
            for w in v.values():visit(w)
        elif isinstance(v,list):
            for w in v:visit(w)
    visit(x)
    assert x['raw_data_published'] is False and x['independent_validation'] is False


def test_ict_publication_files_and_previous_benchmarks_unchanged():
    manifest=json.loads(pub.MANIFEST.read_text())
    for name,digest in manifest['files_sha256'].items():assert run.h.sha(run.ROOT/name)==digest
    run.verify()
    assert (run.ROOT/'docs/ICT_CAUSAL_DEVELOPMENT_STUDY.md').read_bytes()==(run.ROOT/'public/reports/ICT_CAUSAL_DEVELOPMENT_STUDY.md').read_bytes()
    assert (run.OUT/'run1/performance.csv').read_bytes()==(run.ROOT/'public/reports/ICT_PERFORMANCE.csv').read_bytes()


def test_quarter_totals_reconcile_every_primary_and_sensitivity_model():
    x=json.loads(pub.PUBLIC.read_text())
    for row in x['rows']:
        assert sum(q['N'] for q in row['quarterly'])==row['N']
        assert sum(q['net_R'] for q in row['quarterly'])==pytest.approx(row['net_ATR_R'])
        assert sum(q['net_points'] for q in row['quarterly'])==pytest.approx(row['net_points'])
        assert row['net_points']==pytest.approx(row['gross_points']-row['N']*1.225)


def test_independent_replay_matches_numeric_checkpoint_before_display_repair():
    amendment=json.loads((run.ROOT/'research/ict-study-registration-export-amendment.json').read_text())
    for name,digest in amendment['checkpoint_before_report_fix'].items():
        assert run.h.sha(run.OUT/'run1'/name)==digest


def test_daily_zero_ledger_is_not_mistaken_for_positive_evidence():
    dates=['2020-01-02','2020-02-03'];panels=[('2019_2021',dates,np.zeros((2,80))),('2024_2026',['2025-01-02','2025-02-03'],np.zeros((2,80)))]
    B={k:np.zeros(2) for k,_,_ in panels}
    result,meta=run.inference(panels,B)
    assert meta['family_tests']==480
    for period in run.PERIODS:
        for name in run.NAMES:
            for contrast in ('ZERO','MINUS_B'):
                x=result[period][name][contrast]
                assert x['mean_ci95']==[0.,0.] and x['p_raw_two_sided']==1 and x['p_holm480']==1


def test_future_prices_after_closed_trade_do_not_change_fill_or_pnl():
    from scripts.ict_study import core as c
    p={k:np.full(480,100.,float) if k!='volume' else np.full(480,10.,float) for k in c.FIELDS}
    p['open'][92]=101;p['high'][92]=105;p['low'][92]=97;p['close'][92]=104
    o=dict(boundary=2,expires=10,direction=1,entry=100.,stop=98.,risk=2.,target=104.,valid_target=True)
    original=c.execute(p,o)
    for v in p.values():v[93:]=1e9
    assert c.execute(p,o)==original
