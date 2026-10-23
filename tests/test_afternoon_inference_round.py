import ast
import json
from datetime import date, timedelta

import numpy as np
import pytest
from scipy.stats import t

from scripts.afternoon_inference_round import (ROOT, LOCK, PROTOCOL, group_test,
    partition, score_interval, generate, hac_comparator, finalize_counter, verify_lock)
from scripts.register_historical_replication_window import chunks, downloads, verify, WINDOW, PLAN
from scripts.register_afternoon_candidate_v2 import parallel_decisions


def synthetic(seed=12, length=783):
    return generate(np.random.default_rng(seed),'GAUSSIAN_IID',20,length,.36,[14.,36.],.59)


def test_partition_equal_lengths_fixed_gaps_and_unused_tail():
    blocks, indexes, width=partition(783)
    assert width == 80 and len(indexes) == 640
    assert indexes[-1] == 779
    assert all(blocks[j+1][0]-blocks[j][-1]-1==20 for j in range(7))
    assert len(np.unique(indexes)) == 640


def test_calendar_too_short_is_not_silently_repartitioned():
    with pytest.raises(ValueError): partition(150)


def test_group_statistic_matches_scalar_formula():
    panel, mask=synthetic()
    estimate=group_test(panel,mask)
    blocks,indexes,width=partition(783)
    for i in range(len(panel)):
        a=np.array([panel[i,b].sum(axis=0)/width for b in blocks])
        raw=2*t.sf(abs(a.mean(axis=0)/(a.std(axis=0,ddof=1)/np.sqrt(8))),7)
        assert estimate['p'][i] == pytest.approx(raw,abs=1e-12)
        assert estimate['mean'][i] == pytest.approx(panel[i,indexes].sum(axis=0)/mask[i,indexes].sum())


def test_guard_and_tail_returns_cannot_change_result():
    panel, mask=synthetic()
    original=group_test(panel,mask)
    keep=np.zeros(783,bool);keep[original['scored_indexes']]=True
    panel[:,~keep] += 100000*mask[:,~keep,None]
    changed=group_test(panel,mask)
    assert np.array_equal(original['p'],changed['p'])
    assert np.array_equal(original['mean'],changed['mean'])


def test_future_appending_cannot_redefine_a_fixed_existing_partition():
    # Candidate input is the fixed pre-registered date slice, not a growing file.
    panel,mask=synthetic()
    extended=np.concatenate([panel,np.ones((20,50,2))*999],axis=1)
    extended_mask=np.concatenate([mask,np.ones((20,50),bool)],axis=1)
    a=group_test(panel,mask)
    b=group_test(extended[:,:783],extended_mask[:,:783])
    assert np.array_equal(a['p'],b['p'])


def test_insufficient_single_group_keeps_both_tests_in_family():
    panel,mask=synthetic()
    block=partition(783)[0][3]
    panel[:,block]=0;mask[:,block]=False
    estimate=group_test(panel,mask)
    assert not estimate['valid'].any()
    assert np.all(estimate['p']==1)


def test_unselected_scores_are_not_fabricated_observed_returns():
    panel,mask=synthetic()
    panel[~mask]=1
    with pytest.raises(ValueError): group_test(panel,mask)


def test_pooled_event_mean_not_equal_weighted_block_event_mean():
    length=783
    blocks,indexes,width=partition(length)
    panel=np.zeros((1,length,2));mask=np.zeros((1,length),bool)
    for j,block in enumerate(blocks):
        n=8+3*j
        chosen=block[:n];mask[0,chosen]=True;panel[0,chosen]=j+1
    r=group_test(panel,mask)
    pooled=panel[0,indexes,0].sum()/mask[0,indexes].sum()
    assert r['valid'][0]
    assert r['mean'][0,0] == pytest.approx(pooled)
    assert r['mean'][0,0] != pytest.approx(4.5)


def test_inverted_interval_matches_score_test_at_zero():
    rng=np.random.default_rng(321)
    for _ in range(30):
        a=rng.normal(.5,.3,8);b=rng.uniform(.25,.5,8)
        ci=score_interval(a,b)
        assert ci['kind']=='BOUNDED'
        p=2*t.sf(abs(a.mean()/(a.std(ddof=1)/np.sqrt(8))),7)
        assert (ci['interval'][0] > 0 or ci['interval'][1] < 0) == (p < .05)


def test_unbounded_interval_is_reported_not_forced_finite():
    interval=score_interval(np.arange(8.),np.array([0,0,0,0,0,0,0,1.]))
    assert interval['kind']=='UNBOUNDED_OR_DISJOINT'
    assert interval['interval'] is None


@pytest.mark.parametrize('model',['GAUSSIAN_IID','T5_IID','NEGATIVE_SKEW_IID',
    'POSITIVE_SKEW_IID','MA19','AR06','AR09','AR095','VOLATILITY_REGIMES',
    'PERSISTENT_SELECTION','MA19_PERSISTENT_SELECTION','NONMIXING_COMMON_FACTOR'])
def test_synthetic_generators_are_finite_reproducible_and_sparse(model):
    args=(model,10,783,.36,[14.,36.],.59)
    a,mask=generate(np.random.default_rng(42),*args)
    b,mask2=generate(np.random.default_rng(42),*args)
    assert np.array_equal(a,b) and np.array_equal(mask,mask2)
    assert np.isfinite(a).all() and np.all(a[~mask]==0)


def test_comparator_keeps_gap_slots_and_has_no_alternative_alpha():
    panel,mask=synthetic()
    result=group_test(panel,mask)
    p=hac_comparator(panel,mask,result['valid'],result['scored_indexes'])
    assert p.shape==(20,2) and np.all((p>=0)&(p<=1))
    assert not np.allclose(p,result['p'])


def test_holm_two_parallel_horizons_remain_unchanged():
    r=parallel_decisions([.9,.01],[-10,4])
    assert r['positive_support']==[False,True]


def test_mc_upper_bound_handles_empty_evaluable_and_zero_counts():
    r=finalize_counter(dict(total=10000,evaluable=0,rejected=0,positive=0,rejected_evaluable=0),.001)
    assert r['evaluable_only']['simultaneous_upper']==1
    assert r['unconditional']['simultaneous_upper']>0


def test_acquisition_chunks_include_sunday_without_within_contract_overlap():
    plan=downloads()
    assert len(plan)==103 and len({r['contract'] for r in plan})==14
    assert plan[0]['start_mmddyyyy']=='11/19/2018'
    assert plan[0]['end_mmddyyyy']=='12/02/2018'
    for contract in {r['contract'] for r in plan}:
        rows=[r for r in plan if r['contract']==contract]
        for j,row in enumerate(rows):
            a,b=date.fromisoformat(row['start_iso']),date.fromisoformat(row['end_iso'])
            assert (b-a).days < 14
            if j: assert a==date.fromisoformat(rows[j-1]['end_iso'])+timedelta(days=1)
    assert plan[-1]['end_iso']=='2021-12-31'
    assert all(not r['nearby'] and not r['total_volume_and_open_interest'] for r in plan)


def test_window_and_source_method_hashes_frozen_and_no_test_release():
    verify_lock();verify()
    window=json.loads(WINDOW.read_text())
    assert window['calendar_weekdays']==783 and window['scored_weekdays']==640
    assert window['complete_rth_days'] is None and window['selected_event_days'] is None
    assert not window['candidate_test_released']
    assert not window['independence_evidence']['absolute_non_exposure_proven']
    assert window['independence_evidence']['earliest_prior_intraday_source_label'].startswith('2022')


def test_method_module_has_no_market_runner_or_csv_parser_import():
    tree=ast.parse((ROOT/'scripts/afternoon_inference_round.py').read_text())
    imports=[node.module or '' for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
    assert not any('causal_map' in x or 'year_holdout' in x or 'afternoon_feasibility' in x for x in imports)
    assert 'read_csv' not in (ROOT/'scripts/afternoon_inference_round.py').read_text()
    assert 'read_csv' not in (ROOT/'scripts/register_historical_replication_window.py').read_text()
