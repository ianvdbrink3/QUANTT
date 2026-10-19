"""Deterministic tests for point-in-time session features and horizons."""
import pandas as pd
from quantlab.futures_research import session_context, evaluate_forward

def market(start='2026-10-19T07:00:00Z', count=400):
    times=pd.date_range(start,periods=count,freq='min',tz='UTC')
    return pd.DataFrame({'contract_id':'NQZ26','open':20000.0,
                         'high':20001.0,'low':19999.0,'close':20000.5},index=times)

def test_london_high_not_visible_during_its_own_bar():
    x=market()
    y=session_context(x)
    assert pd.isna(y.london_high.iloc[0])
    assert y.london_high.iloc[1]==20001.0
    assert y.known_at_utc.iloc[0]==x.index[1]

def test_future_horizon_requires_all_minutes():
    x=market(count=75)
    y=evaluate_forward(x,pd.DatetimeIndex([x.index[0]]))
    assert list(y.complete)==[True,True,True]
    assert list(y.forward_points)==[0.5,0.5,0.5]
    assert list(y.mfe_points)==[1.0,1.0,1.0]
    assert list(y.mae_points)==[1.0,1.0,1.0]
    broken=x.drop(x.index[10])
    z=evaluate_forward(broken,pd.DatetimeIndex([x.index[0]]))
    assert not z.complete.any()

def test_future_returns_do_not_cross_contract_roll():
    x=market(count=70)
    x.loc[x.index[10]:,'contract_id']='NQH27'
    y=evaluate_forward(x,pd.DatetimeIndex([x.index[0]]))
    assert not y.complete.any()

def test_london_cutoff_point_in_time():
    # October NY daylight saving = UTC-4. 08:30 ET = 12:30 UTC.
    x = market(start='2026-10-19T07:00:00Z', count=332)
    x.loc[pd.Timestamp('2026-10-19T12:29:00Z'), 'high'] = 20005
    y = session_context(x)
    before = pd.Timestamp('2026-10-19T12:29:00Z')
    cutoff = pd.Timestamp('2026-10-19T12:30:00Z')
    assert y.loc[before, 'london_high'] == 20001
    assert y.loc[cutoff, 'london_high'] == 20005

def test_missing_london_start_invalidates_levels():
    # Missing 03:00 ET bar must invalidate the entire day's London context.
    x = market(start='2026-10-19T07:01:00Z', count=400)
    y = session_context(x)
    assert y.london_high.isna().all()

def test_missing_internal_london_minute_invalidates_levels():
    x = market()
    x = x.drop(pd.Timestamp('2026-10-19T09:00:00Z'))
    y = session_context(x)
    assert y.london_low.isna().all()

def test_no_timezone_naive_data():
    x=market()
    x.index=x.index.tz_localize(None)
    try: session_context(x)
    except ValueError: pass
    else: raise AssertionError('Expected a timezone validation failure')
