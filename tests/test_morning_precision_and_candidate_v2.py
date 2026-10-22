import numpy as np
import pandas as pd
import pytest
from scipy.stats import t

from scripts.register_afternoon_candidate_v2 import parallel_decisions,verify
from scripts.morning_recovery_precision import hac_interval,bootstrap_means,excursion


def test_two_minute_not_blocked_by_failed_fifteen_minute():
    result=parallel_decisions([.8,.01],[1.,2.])
    assert result['p_holm2']==pytest.approx([.8,.02])
    assert result['positive_support']==[False,True]


def test_holm_second_uses_point05_not_fixed_bonferroni():
    result=parallel_decisions([.01,.04],[1.,2.])
    assert result['p_holm2']==pytest.approx([.02,.04])
    assert result['positive_support']==[True,True]


def test_positive_net_mean_required_for_own_horizon_only():
    result=parallel_decisions([.01,.03],[-1.,2.])
    assert result['positive_support']==[False,True]
    assert parallel_decisions([.04,.9],[2.,2.])['positive_support']==[False,False]


def test_no_extra_horizon_or_missing_test_bypass():
    with pytest.raises(ValueError):
        parallel_decisions([.001],[2.])
    result=parallel_decisions([None,.01],[None,2.])
    assert result['positive_support']==[False,True]


def test_v2_preserves_v1_and_no_independent_run():
    result=verify()
    assert result['v1_preserved'] and result['active_version']==2
    assert result['new_afternoon_runs']==0


def test_hac_interval_matches_scalar_bartlett_sum():
    scores=np.array([.3,-.1,.4,-.2,0,.1,.2,-.3])
    variance=sum(float(x*x) for x in scores)
    for lag in range(1,6):
        variance+=2*(1-lag/6)*sum(float(scores[i]*scores[i+lag]) for i in range(len(scores)-lag))
    expected=(max(0,variance)*8/7)**.5
    result=hac_interval(2.,scores,8,7)
    assert result['se_HAC5']==pytest.approx(expected)
    assert result['ci95']==pytest.approx([2-t.ppf(.975,7)*expected,2+t.ppf(.975,7)*expected])


def test_block_bootstrap_does_not_turn_absent_event_into_zero_return():
    calendar=pd.bdate_range('2025-01-02',periods=40).strftime('%Y-%m-%d').tolist()
    frame=pd.DataFrame([dict(day=d,first_quarter_status='NEGATIVE' if i%2 else 'POSITIVE',following_points=10. if i%2 else 3.) for i,d in enumerate(calendar) if i%3])
    result=bootstrap_means(frame,calendar,reps=1000,seed=123,block=5)
    assert result['mean_negative_ci95']==pytest.approx([10.,10.])
    assert result['difference_ci95']==pytest.approx([7.,7.])
    assert result==bootstrap_means(frame,calendar,reps=1000,seed=123,block=5)


def test_excursion_uses_45_bars_not_end_return():
    prices=dict(high=np.full(45,101.),low=np.full(45,99.))
    prices['high'][20]=110.;prices['low'][44]=95.
    assert excursion(prices,100.)==dict(mfe_points=10.,mae_points=5.)
    with pytest.raises(ValueError):
        excursion({k:v[:44] for k,v in prices.items()},100.)
