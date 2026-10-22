import numpy as np
import pandas as pd
import pytest

from scripts.afternoon_specificity import context_at,measurements,calculate,WINDOWS


def prices():
    c=100+np.arange(390)*.01
    return dict(open=np.r_[100,c[:-1]],close=c,high=c+.1,low=c-.1,volume=np.ones(390))


@pytest.mark.parametrize('k',[300,315,330])
def test_context_uses_only_completed_prefix(k):
    p=prices();group=context_at(p,5.,k)
    assert group=='UP'
    q={z:v.copy() for z,v in p.items()}
    for z in ('open','high','low','close'):q[z][k:]=1e6
    assert context_at(q,5.,k)==group
    assert context_at({z:v[:k] for z,v in p.items()},5.,k)==group


@pytest.mark.parametrize('ratio,expected',[(.49,None),(.5,'UP'),(1.199,'UP'),(1.2,None)])
def test_exact_original_range_bounds(ratio,expected):
    p=prices();p['high'][:330]=102;p['low'][:330]=100
    assert context_at(p,2/ratio,330)==expected


def test_missing_atr_excludes_context_not_unconditional():
    frame,_,_=measurements({'2025-01-02':(prices(),dict(atr=np.nan))},['2025-01-02'])
    assert len(frame)==3 and frame.group.eq('ALL').all()


def test_clock_anchors_not_first_future_bar():
    p=prices();frame,_,_=measurements({'2025-01-02':(p,dict(atr=5.))},['2025-01-02'])
    for clock,k in WINDOWS.items():
        r=frame[(frame.clock==clock)&frame.group.eq('ALL')].iloc[0]
        assert r.anchor==p['close'][k-1] and r.endpoint==p['close'][k+14]
        assert r.points==p['close'][k+14]-p['close'][k-1]


def synthetic_frame():
    rows=[];days=[f'd{i}' for i in range(100)]
    for j,clock in enumerate(WINDOWS):
        for i,d in enumerate(days):
            y=np.sin(i)+j*.3
            for group in ['ALL','UP' if i%2 else 'DOWN']:
                direction=-1 if group=='DOWN' else 1
                rows.append(dict(day=d,clock=clock,group=group,points=direction*y,bps=direction*y))
    return pd.DataFrame(rows),days


def test_family_and_constant_friction_cancels_in_premium():
    frame,days=synthetic_frame();rows,contrasts=calculate(frame,days)
    assert len(rows)==9 and len(contrasts)==10
    for r in rows:
        assert r['mean_gross_points']-r['mean_cost_only_points']==pytest.approx(1.225)
    assert all('p_raw' not in r['points'] for r in contrasts)


def test_same_day_overlap_covariance_not_ignored():
    frame,days=synthetic_frame();rows,contrasts=calculate(frame,days)
    # Shared noise cancels exactly when subtracting clocks on the same days.
    for r in contrasts:
        assert r['bps']['se_HAC5']<1e-12
        if r['kind']=='context_premium':assert abs(r['bps']['delta'])<1e-12


def test_directional_down_benchmark_has_same_sign():
    frame,days=synthetic_frame();rows,_=calculate(frame,days)
    for clock in WINDOWS:
        blind=next(r for r in rows if r['clock']==clock and r['group']=='ALL')
        down=next(r for r in rows if r['clock']==clock and r['group']=='DOWN')
        assert down['same_direction_blind_mean_points']==-blind['mean_gross_points']
        assert down['premium_points']==pytest.approx(down['mean_gross_points']+blind['mean_gross_points'])
