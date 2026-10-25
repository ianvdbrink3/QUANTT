import json
import numpy as np
import pytest
from scripts.judas_replacement import core as c


def trade(day,start,end,block='old'):
    return dict(day=day,block=block,entry_time=f'{day}T{start}:00+00:00',exit_time=f'{day}T{end}:00+00:00',exit_day=day,net_R=1.)


def test_replacement_removes_exact_B_membership_without_scaling_A():
    a=trade('2020-01-02','21:00','22:00');b=trade('2020-01-03','15:00','16:00')
    assert c.split_baseline([a,b],[b])==[a]
    with pytest.raises(ValueError,match='exactly'):c.split_baseline([a],[b])


def test_overlap_accepts_adjacent_boundary_but_rejects_real_intersection():
    a=trade('2020-01-02','14:00','15:00');b=trade('2020-01-02','15:00','16:00')
    assert c.overlap([a],[b])==dict(overlap_pairs=0,overlap_minutes=0)
    b['entry_time']='2020-01-02T14:30:00+00:00'
    assert c.overlap([a],[b])==dict(overlap_pairs=1,overlap_minutes=30.)


def test_daily_attribution_uses_actual_cash_exit_day_and_retains_zeros():
    t=trade('2020-01-02','21:00','22:00');t['exit_day']='2020-01-03';t['net_R']=2
    np.testing.assert_array_equal(c.daily([t],['2020-01-02','2020-01-03','2020-01-06']),[0,2,0])


def test_joint_pairing_counts_one_delta_not_two_and_zero_difference_is_null():
    dates=['2020-01-02','2020-02-03'];other=['2025-01-02','2025-02-03']
    mat=np.array([[.1,.2,.1,.2],[.3,.4,.3,.4]])
    result,meta=c.inference([('2019_2021',dates,mat),('2024_2026',other,mat)])
    assert meta['unique_tests']==9 and meta['paired_differences_identical']
    for b in c.PERIODS:
        r=result[b]['JUDAS_MINUS_B']
        assert r['expected_total_ATR_R_ci95']==[0,0] and r['p_raw_two_sided']==1


def test_different_paired_deltas_are_rejected_not_silently_pooled():
    dates=['2020-01-02','2020-02-03'];mat=np.zeros((2,4));mat[0,2]=1
    with pytest.raises(AssertionError):c.inference([('2019_2021',dates,mat),('2024_2026',dates,mat)])


def test_seven_winners_rechecked_under_both_fills_and_both_eras():
    from scripts.judas_replacement import __main__ as run
    names,rows=run.winners();assert len(names)==7 and len(rows)==42 and run.JUDAS in names
    x=json.loads(run.ict.RESULT.read_text())
    for name in names:
        for fill in ('TOUCH','TRADE_THROUGH'):
            for b in c.PERIODS[:2]:
                own=x['samples'][fill][b][name];base=x['benchmarks'][b]['B']
                assert own['net_ATR_R']>base['net_R']
                assert own['PF_ATR_R']>base['trade_PF_R']
                assert own['sharpe_ATR_R']>base['sharpe_daily_R']


def test_completed_raw_replay_preserves_Benchmarks_and_full_size_sum_identity():
    from scripts.judas_replacement import __main__ as run
    run.verify();x=json.loads(run.RESULT.read_text())
    assert json.loads(run.PROOF.read_text())['status']=='BYTE_IDENTICAL_JUDAS_REPLACEMENT_REPLAYS'
    assert all(a['overlap_minutes']==0 for a in x['overlap'].values())
    source=json.loads(run.ict.RESULT.read_text())
    for b in c.PERIODS:
        J=source['samples']['TRADE_THROUGH'][b][run.JUDAS];B=source['benchmarks'][b]['B']
        for base in ('S1','S2'):
            old=x['performance'][b][base+'_ORIGINAL'];new=x['performance'][b][base+'_JUDAS']
            assert new['N']==old['N']-B['N']+J['N']
            assert new['net_R']==pytest.approx(old['net_R']-B['net_R']+J['net_ATR_R'])
            assert new['net_points']==pytest.approx(old['net_points']-B['net_points']+J['net_points'])
        delta=x['inference'][b]['JUDAS_MINUS_B'];reference=source['inference'][b][run.JUDAS]['MINUS_B']
        np.testing.assert_allclose(delta['expected_total_ATR_R_ci95'],reference['total_ci95'],atol=1e-10,rtol=0)
        assert delta['p_raw_two_sided']==reference['p_raw_two_sided']
