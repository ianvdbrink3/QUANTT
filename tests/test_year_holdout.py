"""Released scoring tests on synthetic data only; no extra year signal run."""
import json
from pathlib import Path

import pandas as pd
import pytest

from scripts import year_holdout as y
from scripts.oos_preparation.adapter import Calendar,at
from scripts.oos_preparation.route import historical_features
from scripts.reproduce_research import engine,holdout
from scripts.reproduce_research.next_engine import Activation
from scripts.verify_research_freeze import verify

ROOT=Path(__file__).resolve().parents[1]


def trades(values):
    return pd.DataFrame(dict(trade_date=[f'2026-01-{i+2:02}' for i in range(len(values))],
        entry_utc=pd.date_range('2026-01-02T15:00Z',periods=len(values),freq='D'),
        net_points=values,entry_price=100.,both_hit_bar=False))


def test_frozen_preparation_stays_valid():
    y.check_preparation();assert verify()['files']==73


def test_descriptive_pnl_drawdown_concentration_and_zero_days():
    t=trades([10.,-20.,5.]);dates=t.trade_date.tolist()+['2026-01-05']
    m=y.descriptive(t,dates)
    assert m['net_points']==-5 and m['net_usd']==-100
    assert m['max_drawdown_points']==20 and m['max_drawdown_usd']==400
    assert m['worst_day_points']==-20
    assert m['best3_share_net_profit_pct'] is None
    assert m['eligible_days']==4 and m['mean_eligible_day_points']==-1.25


def test_concentration_can_exceed100_without_clipping():
    m=y.descriptive(trades([10.,8.,6.,-20.]),['2026-01-02','2026-01-03','2026-01-04','2026-01-05'])
    assert m['net_points']==4 and m['best3_share_net_profit_pct']==600
    assert m['net_points_without_best3']==-20


@pytest.mark.parametrize('key,value',[('net_points',0),('profit_factor',1),('p_value',.05),('ci_low',0),('eligible_days',19)])
def test_each_strict_primary_criterion_can_fail(key,value):
    p=json.loads((ROOT/'research/vnext-future-oos-protocol.json').read_text())
    m=dict(net_points=10.,profit_factor=2.,p_value=.01,ci_low=1.,eligible_days=249)
    assert holdout.verdict(m,p)[0]=='HOLDOUT_PASSED'
    m[key]=value
    assert holdout.verdict(m,p)[0]=='HOLDOUT_FAILED'


def test_generic_released_feature_orchestration_matches_sealed_historical_route(monkeypatch):
    monkeypatch.setattr(y,'preflight',lambda:None)
    day='2025-08-04';c=Calendar(dict(reviewed_ranges=[[day,day]],closes_ny={},observed_outages=[]))
    ix=c.grid(day)
    f=pd.DataFrame(dict(open=100.,high=101.,low=99.,close=100.,volume=100,contract='NQU25',trade_date=day),index=ix)
    schedule=[Activation('NQU25',day)]
    pd.testing.assert_frame_equal(y.released_features(f,schedule,c),historical_features(f,schedule,c),check_exact=True)


def test_released_bounds_cannot_be_extended(monkeypatch):
    monkeypatch.setattr(y,'preflight',lambda:None)
    f=pd.DataFrame(dict(trade_date=['2026-10-01']))
    with pytest.raises(ValueError,match='Outside released bounds'):y.released_features(f,[],None)


def test_compare_outputs_uses_full_bytes_not_only_summary(tmp_path,monkeypatch):
    release=tmp_path/'release.json';release.write_text('{}')
    monkeypatch.setattr(y,'RELEASE',release)
    a,b=tmp_path/'a',tmp_path/'b';a.mkdir();b.mkdir()
    for folder in [a,b]:
        (folder/'summary.json').write_text('{}');(folder/'trades.csv').write_text('same\n')
    assert y.compare_runs(a,b)['status']=='PASS_TWO_FRESH_SOURCE_REPLAYS_BYTE_IDENTICAL'
    (b/'trades.csv').write_text('different\n')
    with pytest.raises(ValueError,match='Byte mismatch'):y.compare_runs(a,b)


def test_nonmatching_output_sets_fail(tmp_path):
    a,b=tmp_path/'a',tmp_path/'b';a.mkdir();b.mkdir()
    (a/'summary.json').write_text('{}')
    with pytest.raises(ValueError,match='file-set'):y.compare_runs(a,b)


def test_no_overwrite_of_consumed_run(tmp_path,monkeypatch):
    monkeypatch.setattr(y,'preflight',lambda:{})
    monkeypatch.setattr(y,'OUTPUT',tmp_path)
    (tmp_path/'first').mkdir()
    with pytest.raises(ValueError,match='already exists'):y.score('first')


def test_bootstrap_reuses_frozen_seed_block_and_zero_sessions():
    daily=[0.,1.,-1.,2.,0.]*10
    assert engine.bootstrap(daily)==engine.bootstrap(daily)
    p=json.loads((ROOT/'research/vnext-future-oos-protocol.json').read_text())
    assert p['inference']['replicates']==2000 and p['inference']['circular_block_length_eligible_sessions']==5
    assert p['inference']['seed']==engine.SEED==20261020


def test_primary_inference_is_not_corrected_with_references():
    p=ROOT/'research/year-holdout-release.json'
    if not p.exists():pytest.skip('Release not yet registered')
    r=json.loads(p.read_text())
    assert 'year:B_ORB15' not in r['nonprimary_family']
    assert len(r['nonprimary_family'])==8
    assert 'year:B_ORB15:clean' in r['nonprimary_family']


def published():
    path=ROOT/'public/data/research-year-holdout.json'
    if not path.exists():pytest.skip('Only after two authorized source runs')
    return json.loads(path.read_text())


def test_published_eligible_costs_breakdowns_and_nominal_inference_reconcile():
    d=published()
    for period,models in d['results'].items():
        for model,r in models.items():
            m=r['metrics'];expected=249 if period=='year' else 408
            assert m['eligible_days']==expected
            assert sum(x['trades'] for x in r['monthly'])==m['trades']
            assert sum(x['eligible_days'] for x in r['monthly'])==expected
            assert sum(x['net_points'] for x in r['monthly'])==pytest.approx(m['net_points'])
            assert sum(x['net_points'] for x in r['direction'].values())==pytest.approx(m['net_points'])
            assert m['net_usd']==pytest.approx(m['net_points']*20)
            assert r['cost_sensitivity'][0]['net_points']==pytest.approx(m['net_points'])
            assert r['cost_sensitivity'][1]['net_points']==pytest.approx(m['net_points']-m['trades'])
            assert r['cost_sensitivity'][2]['net_points']==pytest.approx(m['net_points']-2*m['trades'])
            for stem in ['MFE','MAE']:
                lower=r['excursions'][stem+'_points_lower'];upper=r['excursions'][stem+'_points_bar_upper']
                assert lower['n']==upper['n']==m['trades']
                assert lower['median']<=upper['median']
            assert 0<m['p_value']<=1


def test_published_verdict_uses_only_primary_year_all_view():
    d=published();p=json.loads((ROOT/'research/vnext-future-oos-protocol.json').read_text())
    status,checks=holdout.verdict(d['results']['year']['B_ORB15']['metrics'],p)
    assert d['status']==status and d['primary_checks']==checks
    assert d['historical_ledgers_byte_identical'] and d['future_scoring_completed']


def test_verification_hashes_cover_both_private_and_publication_output_sets():
    path=ROOT/'research/year-holdout-verification.json'
    if not path.exists():pytest.skip('After authorized reproduction')
    v=json.loads(path.read_text())
    assert len(v['files_sha256'])==6 and len(v['publication_files_sha256'])==8
    assert v['fresh_processes']==2 and v['scoring_engine_invocations']==2
    assert v['parameter_changes']==0 and not v['independent_engine_implementation']
    from scripts.oos_preparation.adapter import sha
    if (y.OUTPUT/'first').exists():
        for name,digest in v['files_sha256'].items():
            assert sha(y.OUTPUT/'first'/name)==sha(y.OUTPUT/'reproduction'/name)==digest
