import json
from pathlib import Path
from scripts.reproduce_research import holdout_data

ROOT=Path(__file__).resolve().parents[1]


def test_baseline_overview_is_only_a_view_of_immutable_reference():
    view=json.loads((ROOT/'public/data/research-baseline09.json').read_text())
    frozen=json.loads((ROOT/'research/holdout-reference.json').read_text())
    assert view['source_sha256']==holdout_data.sha(ROOT/'research/holdout-reference.json')
    for screen in view['screens']:
        expected=frozen['holdout'][screen['id']]['all']
        assert all(screen[k]==v for k,v in expected.items())
        assert screen['net_points']<0 and screen['profit_factor']<1


def test_continuous_export_adds_days_without_replacing_baseline():
    d=json.loads((ROOT/'public/data/research-continuous.json').read_text())
    assert d['label']=='vNext PIT Panama — EXPLORATORY_NOT_NEW_HOLDOUT'
    assert sum(x['eligible'] for x in d['coverage'])==148
    assert sum(x['baseline_eligible'] for x in d['coverage'])==123
    assert sum(x['additional'] for x in d['coverage'])==25
    assert next(x for x in d['coverage'] if x['contract']=='NQZ25')['eligible']==6
    assert all(x['ATR_missing']==0 for x in d['coverage'] if x['contract']!='NQH25')
    assert d['continuous_apr_sep_already_observed']['B_ORB15']['all']['eligible_days']==98
    assert d['continuous_apr_sep_already_observed']['B_ORB15']['all']['net_points']==-619.2
    for x in d['impact_decomposition'].values():assert x['lost_days']==0
    for name,digest in d['code_sha256'].items():
        assert holdout_data.sha(ROOT/'scripts/reproduce_research'/name)==digest


def test_global_multiple_testing_and_missing_tick_disclosure():
    d=json.loads((ROOT/'public/data/research-continuous.json').read_text())
    m=d['feature_matrix']
    assert len(m['tests'])==m['multiplicity_family_size']==40
    assert all(x['p_holm_global']>=x['p_raw'] for x in m['tests'])
    assert 'UNAVAILABLE' in d['availability']['ticks']
