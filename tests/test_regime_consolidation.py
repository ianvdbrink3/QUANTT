import json

import numpy as np
import pytest

from scripts.regime_consolidation import core as c
from scripts.regime_consolidation import inference as i
from scripts.regime_consolidation import __main__ as r


def t(day='2020-01-02',value=.1,ratio=.5):
    return dict(day=day,exit_day=day,net_R=value,range_atr=ratio)


def test_five_unique_objects_and_bull_stop_alias_counted_once():
    assert len(c.MODELS)==5 and i.FAMILY==15
    models=c.assemble([t('2020-01-01')],[t('2020-01-03')],[t()],[t()])
    assert models['S3_BASE_1X']==[t()]
    assert len(models['S2_BROAD_STOP'])==2
    assert len(models['S1_SELECTIVE'])==2


def test_strong_day_is_never_added_as_second_s3_position():
    a=t();a['strong_day']=True
    models=c.assemble([a],[],[t()],[t()])
    assert len(models['S3_BASE_1X'])==1
    assert sum(x['net_R'] for x in models['S3_BASE_1X'])==.1


def test_nonhot_threshold_is_exact_complement_of_strict_greater_than():
    no=[t('2020-01-02',ratio=.85),t('2020-01-03',ratio=.850001),t('2020-01-06',ratio=.8)]
    models=c.assemble([],[],no,no)
    assert [x['day'] for x in models['S3_NONHOT_1X']]==['2020-01-02','2020-01-06']


def test_nonhot_excludes_large_range_even_without_strong_close():
    a=t(ratio=1.0);a['strong_day']=False
    assert c.assemble([],[],[a],[a])['S3_NONHOT_1X']==[]


def test_stop_must_not_change_entry_dates_and_duplicates_rejected():
    with pytest.raises(ValueError,match='membership'):
        c.assemble([],[],[t()],[])
    with pytest.raises(ValueError,match='Duplicate'):
        c.assemble([],[],[t(),t()],[t(),t()])


def test_daily_panel_preserves_zero_dates_and_adds_same_cash_day_legs():
    models={m:[t(value=.1),t('2020-01-03',value=.2),dict(t(value=.3),day='2020-01-01')] for m in c.MODELS}
    x=c.panel(models,['2020-01-02','2020-01-03','2020-01-06'])
    np.testing.assert_allclose(x[:,0],[.4,.2,0])
    assert x.shape==(3,5)


def test_missing_daily_boundary_is_not_silently_dropped():
    with pytest.raises(ValueError,match='boundary'):
        c.panel({m:[t()] for m in c.MODELS},['2020-01-03'])


def dates():
    return ['2020-01-02','2020-01-03','2020-02-03','2020-02-04',
            '2020-03-02','2020-03-03','2020-04-01','2020-04-02']


def test_joint_resampling_keeps_exact_cross_model_dependence():
    a=np.arange(8,dtype=float)
    x=np.column_stack([a,2*a,np.zeros(8),-a,a+1])
    samples,meta=i.sample_means(dates(),x,reps=300)
    np.testing.assert_allclose(samples[:,1],2*samples[:,0])
    np.testing.assert_allclose(samples[:,3],-samples[:,0])
    np.testing.assert_allclose(samples[:,4],samples[:,0]+1)
    assert meta['block_months']==2


def test_null_constant_has_zero_interval_and_p_one():
    x=np.zeros((100,5))
    result=i.describe(np.zeros(5),x,8)
    for row in result:
        assert row['mean_ci95']==[0,0] and row['p_raw_two_sided']==1
        assert not row['nominal_ci_strictly_positive']


def test_constant_positive_has_positive_interval_and_plus_one_p():
    result=i.describe(np.ones(5),np.ones((100,5)),8)
    assert result[0]['mean_ci95']==[1,1]
    assert result[0]['p_raw_two_sided']==2/101
    assert result[0]['expected_total_R_ci95']==[8,8]


def test_basic_interval_uses_centered_error_and_reverses_quantile_order():
    samples=np.tile(np.array([8,9,10,11,12])[:,None],(1,5))
    row=i.describe(np.full(5,10.),samples,10)[0]
    assert row['mean_ci95']==pytest.approx([8.1,11.9])


def test_sign_flip_mirrors_interval_and_preserves_two_sided_p():
    samples=np.random.default_rng(1).normal(.05,.2,(1000,5));mu=np.full(5,.05)
    a=i.describe(mu,samples,8);b=i.describe(-mu,-samples,8)
    for x,y in zip(a,b):
        assert x['mean_ci95']==pytest.approx([-y['mean_ci95'][1],-y['mean_ci95'][0]])
        assert x['p_raw_two_sided']==y['p_raw_two_sided']


def test_positive_scaling_changes_effects_but_not_p_values():
    samples=np.random.default_rng(2).normal(.05,.2,(1000,5));mu=np.full(5,.05)
    a=i.describe(mu,samples,8);b=i.describe(mu*2,samples*2,8)
    for x,y in zip(a,b):
        np.testing.assert_allclose(np.array(x['mean_ci95'])*2,y['mean_ci95'])
        assert x['p_raw_two_sided']==y['p_raw_two_sided']


def test_holm_known_values_and_permutation_invariance():
    np.testing.assert_allclose(i.holm([.001,.01,.04]),[.003,.02,.04])
    np.testing.assert_allclose(i.holm([.04,.001,.01]),[.04,.003,.02])


def test_combined_stratified_era_weights_and_no_gap_blocks():
    a=np.tile(np.arange(8)[:,None]/100,(1,5));b=a+1
    result,meta=i.joint([('OLD',dates(),a),('NEW',[d.replace('2020','2025') for d in dates()],b)],reps=200)
    assert meta['fixed_era_weights']==[.5,.5]
    assert meta['combined_blocks_cross_era_gap'] is False
    assert result['COMBINED'][0]['mean_net_R_per_cash_day']==pytest.approx(.535)
    for block in result:
        for row in result[block]:
            assert row['p_holm15']>=row['p_raw_two_sided']-1e-12


def test_simultaneous_interval_contains_nominal_interval():
    samples=np.random.default_rng(3).normal(.05,.2,(2000,5))
    for row in i.describe(np.full(5,.05),samples,8):
        lo,hi=row['mean_ci95'];flo,fhi=row['mean_familywise95_bonf15']
        assert flo<=lo<=hi<=fhi


def test_no_nonfinite_or_one_month_bootstrap():
    with pytest.raises(ValueError,match='two calendar months'):
        i.sample_means(['2020-01-02'],np.ones((1,5)))
    with pytest.raises(ValueError,match='Invalid'):
        i.sample_means(dates(),np.full((8,5),np.nan))


def test_five_columns_are_required_for_fixed_fifteen_test_family():
    with pytest.raises(ValueError,match='five unique'):
        i.joint([('OLD',dates(),np.ones((8,4))),('NEW',dates(),np.ones((8,4)))],reps=20)


def test_reproducible_fixed_draws():
    x=np.arange(40).reshape(8,5)
    a,ma=i.sample_means(dates(),x,reps=200)
    b,mb=i.sample_means(dates(),x,reps=200)
    np.testing.assert_array_equal(a,b)
    assert ma==mb


def test_final_results_aliases_and_primary_sample_integrity():
    if not r.RESULT.exists():pytest.skip('Consolidation not yet computed')
    x=json.loads(r.RESULT.read_text())
    s=x['samples']['OBSERVED_PATH']
    assert s['COMBINED']['S1_SELECTIVE']['N']==249
    assert s['COMBINED']['S2_BROAD_NO_STOP']['N']==872
    assert s['COMBINED']['S2_BROAD_STOP']['N']==872
    assert s['COMBINED']['S3_BASE_1X']['N']==723
    for b in r.BLOCKS:
        for field in ('net_R','net_points','N'):
            # The extra B pillar is identical regardless overnight stop.
            assert s[b]['S2_BROAD_STOP'][field]-s[b]['S3_BASE_1X'][field]==pytest.approx(
                json.loads(r.tp.RESULT.read_text())['portfolio'][b]['B'][field])
        for m in c.MODELS:
            p=s[b][m]['inference']
            assert 0<=p['p_raw_two_sided']<=p['p_holm15']<=1
            assert 'p_holm15' not in x['samples']['COMPLETE_DAY_SENSITIVITY'][b][m]['inference']
    r.verify()
