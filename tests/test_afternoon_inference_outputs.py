import json

import numpy as np

from scripts.afternoon_inference_round import ROOT,OUT,sha,verify_lock
from scripts.register_historical_replication_window import verify,WINDOW,PLAN
from scripts.report_inference_round import ar_diagnostic


def test_all_predeclared_null_and_partial_null_cells_present():
    r=json.loads(OUT.read_text())
    assert len(r['null_rows'])==66
    assert len(r['negative_control'])==6
    assert len(r['power_rows'])==54
    assert r['simultaneous_bounds']==396
    assert all(len(x['methods']['group_score_t'])==3 for x in r['null_rows'])


def test_failed_method_does_not_silently_replace_candidate_or_release_test():
    r=json.loads(OUT.read_text())
    bounds=[cell[scope]['simultaneous_upper'] for row in r['null_rows'] for cell in row['methods']['group_score_t'] for scope in ('unconditional','evaluable_only')]
    assert r['calibration_passed']==(max(bounds)<=.06)
    assert r['status']=='CALIBRATION_FAILED_NO_METHOD_SWITCH'
    assert not r['candidate_v2_changed'] and not r['independent_test_released']
    assert not r['new_market_outcomes_read'] and r['raw_market_files_read']==0
    assert r['max_simultaneous_upper']==max(bounds)


def test_method_and_window_inputs_match_locked_bytes():
    verify_lock();verify()
    r=json.loads(OUT.read_text())
    for path,digest in r['inputs'].items(): assert sha(ROOT/path)==digest
    current=json.loads((ROOT/'research/afternoon-candidate-current.json').read_text())
    assert current['active_id']=='NQ-1430-FIXED-UP-1500-V2'
    assert not current['independent_test_released']


def test_ar_diagnostic_exposes_cross_group_dependence_without_tuning():
    r=ar_diagnostic(783,.36)
    assert r['adjacent_score_correlation']>0
    assert r['true_to_expected_variance']>1
    assert r['phi']==.95 and r['block_weekdays']==80


def test_simulation_and_download_counts_agree_with_summary():
    summary=json.loads((ROOT/'research/afternoon-method-round-summary.json').read_text())
    plan=json.loads(PLAN.read_text());window=json.loads(WINDOW.read_text())
    assert summary['synthetic_panels']==720000
    assert summary['downloads']==len(plan['rows'])==103
    assert len({r['contract'] for r in plan['rows']})==14
    assert window['start']=='2019-01-02' and window['end']=='2021-12-31'
    assert summary['failed_simultaneous_bounds']>0


def test_simultaneous_bounds_are_not_misreported_as_point_estimates():
    r=json.loads(OUT.read_text())
    for row in r['null_rows']:
        for state in row['methods']['group_score_t']:
            for scope in ('unconditional','evaluable_only'):
                interval=state[scope]
                if interval['rate'] is not None:
                    assert interval['simultaneous_upper']>=interval['rate']
