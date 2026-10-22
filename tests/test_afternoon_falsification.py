import numpy as np
import pandas as pd
import pytest

from scripts.afternoon_falsification import measure,calculate,concentration,audit_bars as legacy_audit,transition_summary
from scripts.falsification_time_audit import audit_bars
from scripts.oos_preparation.adapter import at


def prices():
    c=100+np.arange(390)*.01
    return dict(open=np.r_[100.,c[:-1]],close=c,high=c+.1,low=c-.1,volume=np.ones(390))


def state(n=24):
    d=pd.bdate_range('2025-03-03',periods=n).strftime('%Y-%m-%d').tolist();s={}
    for i,day in enumerate(d):
        p=prices()
        if i%2:
            p={**p,'open':200-p['open'],'close':200-p['close'],'high':200-p['low'],'low':200-p['high']}
        s[day]=(p,dict(atr=5.))
    return s,d


def test_fixed_membership_not_reselected_after1430():
    s,days=state(2);p=s[days[0]][0]
    # Direction flips after14:30, but the fixed cohort must retain the day.
    p['close'][329]=90
    frame,trans,_=measure(s,days)
    fixed=frame[frame.scheme.eq('fixed')&frame.group.eq('UP')&frame.clock.eq('15:00')]
    assert set(fixed.day)=={days[0]}
    assert not len(frame[frame.scheme.eq('dynamic')&frame.group.eq('UP')&frame.clock.eq('15:00')])


def test_minute_split_retains_both_price_gaps():
    s,days=state(1);p=s[days[0]][0]
    p['open'][330]+=1;p['open'][331]+=2
    frame,_,_=measure(s,days)
    g=frame[frame.scheme.eq('fixed')&frame.clock.eq('15:00')].set_index('part')
    assert g.at['FULL','points']==pytest.approx(g.at['FIRST','points']+g.at['REST','points']+g.at['FULL','gap_before']+g.at['FULL','gap_between'])
    assert g.at['FIRST','points']==p['close'][330]-p['open'][330]
    assert g.at['REST','points']==p['close'][344]-p['open'][331]


def test_future_rewrite_cannot_change_fixed_cohort():
    s,days=state(2);before,_,_=measure(s,days)
    for day in days:
        p=s[day][0]
        for key in ('open','high','low','close'):p[key][300:]*=2
    after,_,_=measure(s,days)
    def memberships(f):return set(zip(f[f.scheme.eq('fixed')].day,f[f.scheme.eq('fixed')].group))
    assert memberships(before)==memberships(after)


def test_fixed_dynamic1430_same_and_only24_tests():
    s,days=state();frame,_,_=measure(s,days);rows,tests=calculate(frame,days)
    assert len(rows)==36 and len(tests)==24
    for group in ('UP','DOWN'):
        a=frame[frame.scheme.eq('fixed')&frame.group.eq(group)&frame.clock.eq('14:30')]
        b=frame[frame.scheme.eq('dynamic')&frame.group.eq(group)&frame.clock.eq('14:30')]
        assert np.array_equal(a.points,b.points)
    assert all('p_raw' not in r['points'] for r in tests)


def test_leave_out_extremes_match_bruteforce():
    records=[];values=[1.,2.,3.,4.,-1.,10.]
    for scheme in ('fixed','dynamic'):
        for i,x in enumerate(values):
            records.append(dict(scheme=scheme,group='UP',clock='15:00',part='FULL',day=f'd{i}',quarter='2025Q1' if i<3 else '2025Q2',points=x))
    summaries,q,private=concentration(pd.DataFrame(records))
    expected=[np.mean(values[:i]+values[i+1:]) for i in range(len(values))]
    for r in summaries:
        assert r['day_out_min_mean']==pytest.approx(min(expected))
        assert r['day_out_max_mean']==pytest.approx(max(expected))
        assert r['quarter_out_min']['remaining_mean']==pytest.approx(2.)
        assert not r['any_day_sign_flip']
    assert len(private)==12 and len(q)==4


def test_status_matrix_keeps_every_day_and_exposes_range_exits():
    frame=pd.DataFrame([dict(day='a',at1430='UP',at1500='RANGE_ABOVE_MID'),dict(day='b',at1430='DOWN',at1500='UP'),dict(day='c',at1430='ATR_MISSING',at1500='ATR_MISSING')])
    result=transition_summary(frame)
    assert sum(r['days'] for r in result['matrix'])==3
    assert result['coarse_changed_days']==2
    assert any(r['at1500']=='RANGE_ABOVE_MID' for r in result['detailed'])


def test_price_gap_is_not_a_timestamp_gap():
    days=['2025-03-07','2025-03-10'];frames=[]
    for day in days:
        ix=pd.DatetimeIndex([at(day,c) for c in ('14:59','15:00','15:01')])
        g=pd.DataFrame(dict(open=[100,101,102],high=[101,102,103],low=[99,100,101],close=[100,101,102],contract='NQH25',trade_date=day),index=ix)
        frames.append(g)
    result,rows=audit_bars(pd.concat(frames),days)
    assert result['flagged_days']==0 and result['missing']==0
    assert result['price_gaps'][0]['nonzero_days']==2
    assert not result['second_source_verified']


def test_missing_bar_is_flagged_not_filled():
    days=['2025-03-07','2025-03-10'];frames=[]
    for day in days:
        ix=pd.DatetimeIndex([at(day,c) for c in ('14:59','15:00','15:01')])
        g=pd.DataFrame(dict(open=100.,high=101.,low=99.,close=100.,contract='NQH25',trade_date=day),index=ix)
        frames.append(g.iloc[:2] if day==days[0] else g)
    result,_=audit_bars(pd.concat(frames),days)
    assert result['missing']==1 and result['flagged_days']==1


@pytest.mark.parametrize('unit',['us','ns'])
def test_timestamp_spacing_independent_of_datetime_resolution(unit):
    day='2025-03-10';ix=pd.DatetimeIndex([at(day,c) for c in ('14:59','15:00','15:01')]).as_unit(unit)
    g=pd.DataFrame(dict(open=100.,high=101.,low=99.,close=100.,contract='NQH25',trade_date=day),index=ix)
    result,_=audit_bars(g,[day])
    assert result['flagged_days']==0
    old,_=legacy_audit(g,[day])
    assert old['flagged_days']==(1 if unit=='us' else 0)
