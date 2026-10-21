import json
from pathlib import Path
from scripts.reproduce_research.holdout_data import sha

ROOT=Path(__file__).resolve().parents[1]


def public():
    return json.loads((ROOT/'public/data/research-volume-path.json').read_text())


def test_volume_publication_preserves_all_previous_exports_and_code():
    d=public()
    for name,digest in d['frozen_exports_unchanged_sha256'].items():
        assert sha(ROOT/name)==digest
    for name,digest in d['code_sha256'].items():
        assert sha(ROOT/'scripts/reproduce_research'/name)==digest
    assert (ROOT/'public/data/research-volume-path.md').read_bytes()==(ROOT/'docs/VOLUME_PATH_RESEARCH.md').read_bytes()


def test_public_volume_totals_and_exit_reconciliation():
    d=public()
    assert d['eligible_days']==159 and d['previous_ORB_eligible']==148
    assert d['inferential_tests']==0 and 'NO_NEW_HOLDOUT' in d['classification']
    for s,v in d['comparison'].items():
        m=v['active_reference_full159'];common=v['active_reference_common148'];extra=v['active_reference_added11']
        assert (m['eligible_days'],common['eligible_days'],extra['eligible_days'])==(159,148,11)
        assert m['trades']==common['trades']+extra['trades']==d['paths'][s]['trades']
        assert abs(m['net_points']-common['net_points']-extra['net_points'])<1e-8
        exits=d['paths'][s]['exits']
        assert sum(e['trades'] for e in exits)==m['trades']
        assert abs(sum(e['net_points'] for e in exits)-m['net_points'])<1e-8
        assert d['paths'][s]['MFE_first_bar_minutes']['n']==m['trades']
        assert d['paths'][s]['MAE_first_bar_minutes']['n']==m['trades']


def test_publication_contains_only_aggregates_and_consistent_thresholds():
    d=public();text=json.dumps(d)
    assert all(k not in text for k in ['entry_price','exit_price','signal_utc','entry_utc','exit_bar_utc'])
    assert 'source_sha256' not in d  # Do not duplicate the private source inventory.
    for v in d['paths'].values():
        for t in v['thresholds']:
            assert t['certain_hits']==t['possible_hits_including_certain']
            assert sum(x['certain'] for x in t['by_final_net_sign'].values())==t['certain_hits']
            assert t['all_trades']==v['trades']
            assert abs(t['hit_fraction_lower']-t['certain_hits']/v['trades'])<1e-12
