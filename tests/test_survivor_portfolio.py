import numpy as np
import pytest
from scripts.survivor_portfolio import scaled, marked_curve, bootstrap, MODELS
from scripts.edge_marathon.core import select


def test_NQ_ATR_cost():
    net,qty,cost=scaled(20,200)
    assert net==pytest.approx(18.775/200)
    assert cost==pytest.approx(1.225/200)


@pytest.mark.parametrize('atr',[float('nan'),0,-1])
def test_missing_prior_ATR_size0(atr):
    assert scaled(20,atr)==(0,0,0)


def test_MNQ_fee_not_NQ_divided_by10():
    net,q,cost=scaled(20,100,1,'MNQ_FRACTIONAL')
    assert q==5
    assert cost==.0325
    assert net==pytest.approx(5*(40-6.5)/1000)


def test_integer_zero_not_forced_one():
    assert scaled(100,200,1/3,'MNQ_INTEGER')==(0,0,0)


def test_no_idle_budget_reallocation():
    assert scaled(20,100,1/3)[0]==pytest.approx(scaled(20,100)[0]/3)
    assert scaled(20,100,1/3,'MNQ_INTEGER')[1]==1
    assert scaled(20,100,1,'MNQ_INTEGER')[1]==5


def test_marked_final_matches_daily():
    p=dict(close=np.arange(390,dtype=float)+100)
    trades=[dict(entry=0,end=390,direction=1,entry_price=100,atr=200),
            dict(entry=30,end=150,direction=-1,entry_price=130,atr=200)]
    for v in ('NQ_ATR','MNQ_FRACTIONAL','MNQ_INTEGER'):
        path=marked_curve(trades,p,[1/3,1/3],v)
        expected=scaled(389,200,1/3,v)[0]+scaled(-119,200,1/3,v)[0]
        assert path[-1]==pytest.approx(expected)
        assert path[0]<=0


def test_joint_bootstrap_preserves_equal_third():
    dates=[f'2025-{m:02d}-02' for m in range(1,13)]
    x=np.column_stack([np.arange(12),np.arange(12)*2,np.zeros(12)])
    x=np.column_stack([x,x.mean(axis=1)])
    a=bootstrap(dates,x,reps=200)
    b=bootstrap(dates,x,reps=200)
    assert a==b
    assert a[0]['mean_R_ci95'][0]<=x[:,0].mean()<=a[0]['mean_R_ci95'][1]


def test_future_truncation_signal_information():
    p=dict(open=np.full(390,100.),close=np.full(390,102.),high=np.full(390,103.),low=np.full(390,99.))
    ctx=dict(tom=True,atr=100.,PDH=101.,PDL=98.,ONH=104.,ONL=100.)
    full=[e for e in select(p,ctx) if e['model'] in MODELS]
    for event in full:
        boundary=max(1,event['decision'])
        prefix={k:v[:boundary] for k,v in p.items()}
        assert event in select(prefix,ctx)


def test_unknown_cost_variant_rejected():
    with pytest.raises(ValueError):scaled(1,100,variant='OTHER')
