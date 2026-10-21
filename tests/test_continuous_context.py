import numpy as np
import pandas as pd
import pytest
from scripts.reproduce_research import engine
from scripts.reproduce_research.continuous import continuous_daily,apply_indicators,roll_spreads
from scripts.reproduce_research.context import day_context,trade_context
from scripts.reproduce_research.next_engine import Activation
from scripts.reproduce_research.feature_matrix import matrix


def bars(contract,day,price,full=False):
    ix=engine.expected_grid(day) if full else pd.date_range(engine.time_at(day,'09:30'),engine.time_at(day,'16:00'),freq='min',inclusive='left')
    return pd.DataFrame(dict(contract=contract,trade_date=day,open=price,high=price+1,
                             low=price-1,close=price,volume=100),index=ix)


@pytest.fixture(params=['2025-06-17','2025-09-17'])
def roll_data(request):
    day=request.param
    dates=pd.bdate_range(end=day,periods=21).strftime('%Y-%m-%d')
    full=pd.concat([bars('OLD',d,100) for d in dates[:-1]]+
                   [bars('NEW',dates[-2],150),bars('NEW',day,150,True)]).sort_index()
    return full,[Activation('OLD',dates[0]),Activation('NEW',day)],day


def test_day1_eligible_after_panama_without_changing_raw_fills(roll_data):
    full,schedule,day=roll_data
    daily,spreads=continuous_daily(full,schedule)
    d=daily[daily.trade_date.eq(day)].iloc[0]
    assert d.atr14_continuous==2 and d.pdh_continuous==151 and d.pdl_continuous==149
    assert spreads[0]['spread_points']==50
    g=full[(full.contract=='NEW')&(full.trade_date==day)].copy()
    g['atr14_prior']=np.nan;g['prior_same_minute_median_volume']=100.
    g['data_quality_flag']='ok';g['vwap_close']=150.;g['vwap_z_close']=0.
    for n in [5,15,30]:g[f'orb{n}_high']=151.;g[f'orb{n}_low']=149.
    _,before=engine.hypotheses(g)
    adjusted=apply_indicators(g,daily)
    _,after=engine.hypotheses(adjusted)
    assert not before.eligible.any() and after.eligible.all()
    assert adjusted[['open','high','low','close','volume']].equals(g[['open','high','low','close','volume']])


def test_future_prices_do_not_revise_old_indicator_states(roll_data):
    full,schedule,day=roll_data
    original,spreads=continuous_daily(full,schedule)
    changed=full.copy()
    changed.loc[changed.trade_date.ge(day),['open','high','low','close']]+=1000
    revised,again=continuous_daily(changed,schedule)
    assert spreads==again
    cols=['trade_date','atr14_continuous','pdh_continuous','pdl_continuous','offset_points']
    pd.testing.assert_frame_equal(original[cols],revised[cols])
    assert spreads[0]['spread_available_utc']<spreads[0]['effective_utc']


def test_no_common_pre_roll_close_fails(roll_data):
    full,schedule,day=roll_data
    with pytest.raises(ValueError,match='No common'):
        roll_spreads(full[~((full.contract=='NEW')&(full.trade_date<day))],schedule)


def prepared_days():
    dates=pd.bdate_range('2025-07-07',periods=16).strftime('%Y-%m-%d')
    frames=[]
    for i,d in enumerate(dates):
        g=bars('NEW',d,100,True)
        g['volume']=i+1;g['atr14_prior']=10.;g['pdh']=105.;g['pdl']=95.
        frames.append(g)
    return pd.concat(frames),dates


def test_rvol_uses_exact_prior14_sessions_and_never_current_window():
    master,dates=prepared_days();days=day_context(master)
    row=days.iloc[14]
    assert row.opening_RVOL14==pytest.approx(15/7.5)
    assert pd.isna(days.iloc[13].opening_RVOL14)
    changed=master.copy();changed.loc[changed.trade_date.ge(dates[14]),'volume']*=10
    new=day_context(changed)
    assert new.iloc[14].prior14_opening_volume_mean==row.prior14_opening_volume_mean
    assert new.iloc[14].opening_RVOL14==pytest.approx(row.opening_RVOL14*10)
    assert days.opening_relative_ticks.isna().all() and days.opening_volume_per_tick.isna().all()


@pytest.mark.parametrize('hm,volume_known,overnight_known',[('08:45',False,False),('09:40',False,True),('09:45',True,True),('10:30',True,True)])
def test_context_masks_future_opening_windows(hm,volume_known,overnight_known):
    master,dates=prepared_days();day=dates[14];entry=engine.time_at(day,hm)
    trades=pd.DataFrame([dict(trade_date=day,entry_utc=entry,signal_utc=entry-pd.Timedelta(minutes=1),
                              strategy='TEST',net_points=0,mfe_bar_bound_points=0,mae_bar_bound_points=0)])
    row=trade_context(master,trades,day_context(master)).iloc[0]
    assert pd.notna(row.opening_RVOL14)==volume_known
    assert pd.notna(row.overnight_range_ATR)==overnight_known
    assert pd.notna(row.opening_location)==overnight_known
    assert row.breakout_reference_price==100
    assert row.distance_to_PDH_pct_ATR==50
    assert row.breakout_bar_volume_per_tick is None


def test_holm_family_contains_all_strategies_features_and_outcomes():
    dates=pd.bdate_range('2025-01-01',periods=20).strftime('%Y-%m-%d').tolist()
    rows=[dict(strategy=s,trade_date=d,opening_location='INSIDE_PRIOR_RANGE',overnight_regime='MIDDLE',
               opening_RVOL14=1.,overnight_range_ATR=.6,net_points=float(i),mfe_bar_bound_points=float(i+2))
          for s in ['A','B','C','D'] for i,d in enumerate(dates)]
    result=matrix(pd.DataFrame(rows),dates,reps=20)
    assert result['multiplicity_family_size']==40
    assert all(t['p_holm_global']==1 for t in result['tests'])


def test_future_ohlcv_mutation_cannot_change_pre_entry_trade_context():
    master,dates=prepared_days();day=dates[14];entry=engine.time_at(day,'09:40')
    trades=pd.DataFrame([dict(trade_date=day,entry_utc=entry,signal_utc=entry-pd.Timedelta(minutes=1),
                              strategy='TEST',net_points=0,mfe_bar_bound_points=0,mae_bar_bound_points=0)])
    old=trade_context(master,trades,day_context(master))
    altered=master.copy()
    altered.loc[altered.index>=entry,['open','high','low','close','volume']]*=10
    new=trade_context(altered,trades,day_context(altered))
    pd.testing.assert_frame_equal(old,new)
