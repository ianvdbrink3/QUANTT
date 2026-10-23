import json
from pathlib import Path

import pytest

from scripts.edge_marathon.stats import holm
from scripts.month_turn_audit import verify

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT/'research/month-turn-audit-results.json'
pytestmark = pytest.mark.skipif(not PATH.exists(), reason='Audit outputs not generated yet')


def data():
    return json.loads(PATH.read_text())


def test_original_tom_baselines_reproduced_not_redefined():
    samples = data()['samples']
    assert samples['DISCOVERY']['replay']['trades'] == 81
    assert samples['DISCOVERY']['tom']['net_points'] == pytest.approx(4364.025)
    assert samples['CONTINUOUS_2022_2024_UNVERIFIED']['replay']['trades'] == 90
    assert samples['CONTINUOUS_2022_2024_UNVERIFIED']['tom']['net_points'] == pytest.approx(1440.25)


def test_complementary_benchmarks_reconcile_exact_exposure():
    for s in data()['samples'].values():
        a, b, c = (s[k] for k in ('tom', 'non_tom', 'all_rth_long'))
        assert a['days']+b['days'] == c['days'] == s['complete_days']
        assert a['net_points']+b['net_points'] == pytest.approx(c['net_points'])
        assert (a['mean_net']*a['days']+b['mean_net']*b['days'])/c['days'] == pytest.approx(c['mean_net'])


def test_all_four_exploratory_contrasts_remain_in_holm_family():
    d = data()
    rows = [s[f] for s in d['samples'].values() for f in ('raw_contrast', 'normalized_contrast')]
    assert d['multiplicity']['new_contrasts'] == len(rows) == 4
    assert [r['p_holm4'] for r in rows] == pytest.approx(holm([r['p_raw'] for r in rows]))
    assert all(r['bootstrap_valid_replications'] == 10000 for r in rows)


def test_missing_atr_only_changes_descriptive_common_sample():
    for s in data()['samples'].values():
        n = s['normalization']
        assert n['groups']['tom']['days']+n['tom_missing_atr'] == s['tom']['days']
        assert n['groups']['non_tom']['days']+n['non_tom_missing_atr'] == s['non_tom']['days']
        assert not n['original_model_exclusions_changed']


def test_all9_execution_scenarios_keep_same_days_and_fixed_cost_math():
    for s in data()['samples'].values():
        rows = s['execution_sensitivity']
        assert len(rows) == 9
        assert {(r['entry_delay_minutes'], r['roundtrip_cost_usd']) for r in rows} == {
            (delay, cost) for delay in (0, 1, 5) for cost in (24.5, 34.5, 44.5)
        }
        assert all(r['days'] == s['tom']['days'] for r in rows)
        for delay in (0, 1, 5):
            a, b, c = [r for r in rows if r['entry_delay_minutes'] == delay]
            assert a['net_points']-b['net_points'] == pytest.approx(.5*s['tom']['days'])
            assert a['net_points']-c['net_points'] == pytest.approx(s['tom']['days'])


def test_minute_marked_drawdown_and_concentration_reconcile():
    for s in data()['samples'].values():
        r = s['risk']
        assert r['minute_close_equity_drawdown'] >= s['tom']['closed_trade_drawdown']-1e-8
        assert r['without_top3']['net_points']+r['top3_net_points'] == pytest.approx(s['tom']['net_points'])
        assert r['mae']['median'] <= r['mae']['p95'] <= r['mae']['max']


def test_public_outputs_are_aggregate_only_and_match_local_report():
    public = ROOT/'public/data/month-turn-audit.json'
    assert public.read_bytes() == PATH.read_bytes()
    assert (ROOT/'public/reports/MONTH_TURN_AUDIT.md').read_bytes() == (ROOT/'docs/MONTH_TURN_AUDIT.md').read_bytes()
    text = public.read_text()
    for forbidden in ('/Users/', 'entry_price', 'exit_price', 'open_prices', 'close_prices', 'daily_ledger'):
        assert forbidden not in text
    assert not data()['independent_validation']
    assert not data()['new_candidate_preregistration']
    assert not data()['external_publication']


def test_all_prior_files_and_private_baselines_still_byte_identical():
    assert len(verify()['protected_files']) == data()['protected_files']
