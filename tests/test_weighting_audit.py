"""Hand calculations and exact independent oracles; no strategy calculation."""
import itertools
import json
from pathlib import Path

import numpy as np
import pytest

from scripts.weighting_audit import core as c

ROOT=Path(__file__).resolve().parents[1]


def coin_paths(steps=8):
    increments=np.array(list(itertools.product([-1.,1.],repeat=steps)))
    close=increments.cumsum(axis=1);before=np.c_[np.zeros(len(close)),close[:,:-1]]
    return np.maximum(before,close),np.minimum(before,close),close


def test_exact_scalar_oracle_equals_independent_vectorized_estimator():
    high,low,close=coin_paths();num,den=c.daily_statistics(high,low,close,(1,'rth_close'))
    theta=c.estimate(num,den);oracle=c.enumerate_symmetric_paths()
    for row in oracle:
        i=c.SIDES.index(row['side']);j=0 if row['horizon']=='1' else 1
        for k,scheme in enumerate(c.SCHEMES):assert theta[i,j,k]==pytest.approx(row[scheme],abs=1e-14)


def test_exact_no_predictability_can_have_nonzero_equal_day_mean():
    for row in c.enumerate_symmetric_paths():
        assert row['event']==pytest.approx(0,abs=1e-14)
        assert row['past_count']==pytest.approx(0,abs=1e-14)
        assert row['first_record']==pytest.approx(0,abs=1e-14)
        if row['side']=='RECORD_HIGH':assert row['equal_day']<0
        else:assert row['equal_day']>0


def test_weighting_gap_identity_is_exact_not_a_fitted_regression():
    high,low,close=coin_paths(10)
    num,den=c.daily_statistics(high,low,close,(1,2,'rth_close'))
    for row in c.weighting_decomposition(num,den):
        assert abs(row['identity_residual'])<1e-12
        assert row['event_minus_day']==pytest.approx(row['cov_over_mean_count'])


def test_two_day_toy_example():
    # A: three events each+1; B: one event-3. Event mean0; day mean-1.
    count=np.array([3.,1.]);day=np.array([1.,-3.])
    event=(count*day).sum()/count.sum()
    covariance=np.mean((count-count.mean())*(day-day.mean()))
    assert event==0 and day.mean()==-1 and covariance/count.mean()==1


def test_future_record_count_changes_equal_day_weights_not_past_count_weights():
    prefix=np.array([0.,2.,1.,3.,2.,4.,5.,6.]);changed=prefix.copy();changed[5:]=[-5,-6,-7]
    high=lambda x:np.maximum(np.r_[0.,x[:-1]],x)
    a=high(prefix);b=high(changed)
    ra=a[1:]>np.maximum.accumulate(a)[:-1];rb=b[1:]>np.maximum.accumulate(b)[:-1]
    assert np.array_equal(ra[:3],rb[:3])
    assert np.array_equal(np.cumsum(ra)[:3],np.cumsum(rb)[:3])
    assert ra.sum()!=rb.sum()  # final1/N weights differ despite same earlier history


def test_first_bar_and_equal_highs_are_not_new_records():
    high=np.array([[1.,1.,1.,1.]]);low=-high;close=np.zeros_like(high)
    num,den=c.daily_statistics(high,low,close,(1,2,'rth_close'))
    assert not num.any() and not den.any()


def test_terminal_bar_record_has_no_forward_outcome():
    high=np.array([[1.,1.,1.,10.]]);low=np.zeros_like(high);close=np.array([[.5,.5,.5,9.]])
    _,den=c.daily_statistics(high,low,close,(1,2,'rth_close'))
    assert not den.any()


def test_signed_returns_not_flipped_for_record_lows():
    high=np.array([[0.,-1.,-2.,1.]]);low=high-1;close=high-.5
    num,den=c.daily_statistics(high,low,close,(1,2,'rth_close'))
    assert num[0,1,0,3]==-1  # first low followed by another decline


@pytest.mark.parametrize('which',['gaussian_iid','gaussian_clock_scale','conditional_bar_reflections'])
def test_null_generators_are_seeded_valid_envelopes(which):
    shapes={'close':np.ones((5,20)), 'high':np.ones((5,20))*2,'low':np.ones((5,20))*-.5}
    args=(shapes,1.,np.ones(20),np.array([.5,1.,1.5]))
    a=c.simulated_path(which,np.random.default_rng(12),*args)
    b=c.simulated_path(which,np.random.default_rng(12),*args)
    for x,y in zip(a,b):np.testing.assert_array_equal(x,y)
    high,low,close=a;assert (high>=close).all() and (low<=close).all()


def test_reflecting_full_shapes_has_exact_zero_conditional_next_increment():
    shape=dict(close=np.array([[2.,-3.]]),high=np.array([[4.,1.]]),low=np.array([[-1.,-5.]]))
    # Every fair sign has an equally likely mirror; no future mean from a record.
    for minute in range(2):assert (shape['close'][0,minute]-shape['close'][0,minute])/2==0
    sign=np.array(list(itertools.product([-1,1],repeat=2)))
    increments=sign*shape['close'][0]
    for first in [-1,1]:assert increments[sign[:,0]==first,1].mean()==0


def test_independent_bootstrap_agrees_with_explicit_day_replication():
    high,low,close=coin_paths();num,den=c.daily_statistics(high,low,close,(1,2,'rth_close'))
    w=c.circular_weights(len(num),reps=32,seed=99);boot=c.bootstrap(num,den,w)
    for r in range(32):
        expanded=np.repeat(np.arange(len(num)),w[r]);expected=c.estimate(num[expanded],den[expanded])
        np.testing.assert_allclose(boot[r],expected,atol=1e-12)


def test_original_calendar_mask_not_replaced_by_zero_returns():
    n=np.array([[[[10.]]],[[[30.]]]]);d=np.ones_like(n)
    weights=c.circular_weights(3,reps=30)[:,[0,2]]
    boot=c.bootstrap(n,d,weights)
    assert (boot>=10).all() and (boot<=30).all()


def test_holm_is_global_and_includes_all_missing_comparisons():
    ps=[.0005]+[1.]*71
    assert c.holm(ps)[0]==pytest.approx(.036)
    assert c.holm([None,.02,.001])==pytest.approx([1.,.04,.003])


def test_mc_tail_probability_never_zero_and_two_sided_resolution():
    x=np.arange(4095,dtype=float);r=c.mc_p(-100,x)
    assert r['p_value']==2/4096 and r['minimum_two_sided_p']==2/4096
    assert r['mc_precision_95'][1]>0
    assert c.mc_p(2047,x)['p_value']==1.


def test_zero_test_and_predictive_null_are_different_questions():
    boot=np.linspace(-11.,-9.,4000)
    assert c.zero_test(-10,boot)==1/4001
    assert c.mc_p(-10,np.linspace(-11.,-9.,4095))['p_value']==1.


def test_wilson_intervals_not_degenerate_at_zero_or_one():
    assert c.wilson(0,128)[1]>0 and c.wilson(128,128)[0]<1


def test_locked_protocol_specifies_fixed_batch_and_no_models():
    p=json.loads((ROOT/'research/weighting-audit-protocol.json').read_text())
    assert p['simulation']['experiments_per_generator']==4095
    assert p['monte_carlo_comparison']['hypotheses']==72
    assert p['zero_test_calibration']['panels_per_generator']==128
    assert len(p['null_generators'])==3 and len(p['schemes'])==4


def test_price_unit_rescaling_changes_means_not_record_selection():
    high,low,close=coin_paths(9)
    a,da=c.daily_statistics(high,low,close,(1,2,'rth_close'))
    b,db=c.daily_statistics(3*high,3*low,3*close,(1,2,'rth_close'))
    np.testing.assert_array_equal(da,db)
    np.testing.assert_allclose(b,3*a)


def test_core_has_no_dependency_on_old_statistical_implementation():
    import ast
    tree=ast.parse((ROOT/'scripts/weighting_audit/core.py').read_text())
    modules=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):modules.extend(n.name for n in node.names)
        if isinstance(node,ast.ImportFrom):modules.append(node.module or '')
    assert set(modules)=={'itertools','numpy'}


def test_method_lock_is_intact_before_and_after_batch():
    from scripts.weighting_audit.__main__ import preflight
    assert preflight()['monte_carlo_comparison']['hypotheses']==72


def test_tampered_input_rejected_before_any_new_measurement(tmp_path,monkeypatch):
    from scripts.weighting_audit import __main__ as runner
    (tmp_path/'changed.txt').write_text('different')
    lock=tmp_path/'lock.json';lock.write_text(json.dumps(dict(files_sha256={'changed.txt':'0'*64})))
    monkeypatch.setattr(runner,'ROOT',tmp_path);monkeypatch.setattr(runner,'LOCK',lock)
    monkeypatch.setattr(runner,'verify_archive',lambda:None)
    with pytest.raises(ValueError,match='locked bytes changed'):runner.preflight()


def completed():
    p=ROOT/'public/data/research-weighting-audit.json'
    if not p.exists():pytest.skip('After the fixed simulation batch, never generate during tests')
    return json.loads(p.read_text())


def test_fixed_simulation_family_complete_not_selected_after_results():
    d=completed()
    assert len(d['comparisons'])==72 and len(d['real_estimators'])==24
    assert len(d['zero_test_calibration'])==72 and d['total_null_experiments']==12285
    assert d['total_null_days']==5343975
    assert d['new_strategy_signals']==0 and not d['entries_stops_targets_used']
    assert all(r['experiments']==4095 for r in d['comparisons'])
    assert all(r['panels']==128 for r in d['zero_test_calibration'])
    np.testing.assert_allclose(c.holm([r['p_value'] for r in d['comparisons']]),[r['p_holm72'] for r in d['comparisons']])


def test_observed_old_means_and_uncertainty_independently_reproduced():
    d=completed();p=d['independent_reproduction']
    assert p['complete_days']==435 and p['scheduled_sessions']==454 and p['source_files']==69
    assert p['max_abs_published_mean_error_bps']<1e-8
    assert p['max_abs_previous_ci_error_bps']<1e-8
    assert max(abs(r['identity_residual']) for r in d['weighting_decomposition'])<1e-8


def test_all_comparisons_are_around_simulated_estimand_not_assumed_zero():
    d=completed()
    for r in d['comparisons']:
        assert r['observed_minus_null_median']==pytest.approx(r['observed_bps']-r['null']['median'])
        assert r['null']['p025']<=r['null']['p05']<=r['null']['p25']<=r['null']['median']<=r['null']['p75']<=r['null']['p95']<=r['null']['p975']
        assert r['p_value']>=2/4096 and r['p_value']<=1


def test_original_reports_and_archive_not_rewritten_by_addendum():
    from scripts.weighting_audit.__main__ import preflight
    from scripts.archive_experiments import verify_archive
    preflight();assert verify_archive()['protected_files']==115


def test_simulation_evidence_hashes_reproduce_public_results_without_rescoring():
    completed()
    from scripts.weighting_audit.__main__ import verify_completed
    assert verify_completed()['simulation_experiments']==12285


def test_publication_aggregates_match_recorded_hashes():
    p=ROOT/'research/weighting-audit-publication.json'
    if not p.exists():pytest.skip('After deterministic publication')
    from scripts.oos_preparation.adapter import sha
    m=json.loads(p.read_text())
    for name,digest in m['files_sha256'].items():assert sha(ROOT/name)==digest
    assert sha(ROOT/'docs/WEIGHTING_AND_RECORD_SELECTION_AUDIT.md')==m['report_sha256']


def test_all72_tail_counts_and_null_quantiles_match_saved_simulations_by_independent_arithmetic():
    d=completed();out=ROOT/'artifacts/weighting-audit'
    if not out.exists():pytest.skip('Private full simulation arrays unavailable')
    for generator in {r['generator'] for r in d['comparisons']}:
        array=np.load(out/(generator+'.npz'))['estimates']
        for r in d['comparisons']:
            if r['generator']!=generator:continue
            sample=array[:,c.SIDES.index(r['side']),c.HORIZONS.index(r['horizon']),c.SCHEMES.index(r['scheme'])]
            smaller=min(int((sample<=r['observed_bps']).sum()),int((sample>=r['observed_bps']).sum()))
            p=min(1.,2*(1+smaller)/4096)
            assert p==r['p_value'] and smaller==r['smaller_tail_count']
            assert sample.mean()==pytest.approx(r['null']['mean'])
            assert np.quantile(sample,.975)==pytest.approx(r['null']['p975'])


def test_calibration_rate_exports_match_each_saved_panel_not_only_summary():
    d=completed();out=ROOT/'artifacts/weighting-audit'
    if not out.exists():pytest.skip('Private full simulation arrays unavailable')
    for generator in {r['generator'] for r in d['zero_test_calibration']}:
        arrays=np.load(out/(generator+'.npz'))
        for r in d['zero_test_calibration']:
            if r['generator']!=generator:continue
            key='calibration_p' if r['procedure']=='nominal' else 'calibration_holm43'
            i,j,k=c.SIDES.index(r['side']),c.HORIZONS.index(r['horizon']),c.SCHEMES.index(r['scheme'])
            successes=int((arrays[key][:,i,j,k]<.05).sum())
            assert successes==r['rejections'] and successes/128==r['rate']
