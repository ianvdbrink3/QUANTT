import json

import numpy as np
import pandas as pd
import pytest

from scripts.price_volume import core as c
from scripts.price_volume import __main__ as r


def bars(n=390):
    return {k:np.full(n,v,dtype=float) for k,v in
            dict(open=1000,high=1001,low=999,close=1000,volume=10).items()}


def pullback_bars():
    p=bars();p['open'][0]=1060;p['high'][0]=1070;p['low'][0]=1059;p['close'][0]=1060
    p['volume'][10:15]=30;p['close'][14]=1010;p['high'][14]=1011
    return p


def climax_bars(start=5):
    p=bars();p['low'][start]=998;p['volume'][start:start+5]=100
    p['close'][start+9]=1001
    return p


def test_twenty_fixed_variants_no_optimized_combinations():
    assert len(c.MODELS)==20 and len(set(c.MODELS))==20
    assert len(c.G1)==3 and len(c.G2)==12 and len(c.G3)==5


def test_g1_prior_bull_and_prior_twenty_volumes_required():
    p=pullback_bars();ctx=dict(atr=100,bull=True)
    assert c.select_g1(p,ctx,[50]*20)['boundary']==15
    assert c.select_g1(p,dict(ctx,bull=False),[50]*20) is None
    assert c.select_g1(p,dict(ctx,bull=None),[50]*20) is None
    assert c.select_g1(p,ctx,[]) is None


def test_trigger_volume_not_in_own_reference():
    p=pullback_bars();p['volume'][10:15]=16
    ev=c.select_g1(p,dict(atr=100,bull=True),[50]*20)
    assert ev and ev['volume_reference']==50


def test_peak_minute_low_does_not_prove_pullback_order():
    p=bars();p['high'][9]=1100;p['low'][9]=900
    assert c.pullback(p,10) is None


def test_pullback_known_before_reversal_not_its_same_bar_wick():
    p=bars();p['low'][10]=900;p['volume'][10:15]=30;p['close'][14]=1010;p['high'][14]=1011
    assert c.select_g1(p,dict(atr=100,bull=True),[50]*20) is None


def test_g1_future_truncation_and_poisoning():
    p=pullback_bars();ctx=dict(atr=100,bull=True)
    event=c.select_g1(p,ctx,[50]*20)
    assert c.select_g1({k:v[:15] for k,v in p.items()},ctx,[50]*20)==event
    for v in p.values():v[15:]=999999
    assert c.select_g1(p,ctx,[50]*20)==event


def test_g2_confirm_then_next_open_not_climax_close():
    p=climax_bars();ctx=dict(atr=100,ONL=999,bull=True)
    ev=c.select_g2(p,ctx,'ONL')
    assert ev['boundary']==15 and ev['low']==997.75
    assert c.select_g2({k:v[:14] for k,v in p.items()},ctx,'ONL') is None
    p['open'][15]=1002
    t,code=c.execute(p,ctx,'G2_ONL_ALL_TIME',ev)
    assert code=='FILLED' and t['entry_price']==1002 and t['entry_bar']==15


def test_g2_missing_overnight_not_filled_from_rth_future():
    assert c.select_g2(climax_bars(),dict(atr=100,ONL=np.nan,bull=True),'ONL') is None


def test_first_hour_level_not_available_before_1030():
    p=climax_bars();ctx=dict(atr=100,bull=True)
    assert c.select_g2(p,ctx,'H1') is None
    p=climax_bars(60)
    assert c.select_g2(p,ctx,'H1')['boundary']==70


def test_g2_reference_excludes_climax_and_confirmation():
    p=climax_bars();p['volume'][10:15]=100000
    ev=c.select_g2(p,dict(atr=100,ONL=999),'ONL')
    assert ev['volume_reference']==50


def test_g2_bull_filter_does_not_affect_unconditional_signal():
    p=climax_bars();ctx=dict(atr=100,ONL=999,bull=False)
    assert c.select_g2(p,ctx,'ONL') is not None
    assert c.select_g2(p,ctx,'ONL',True) is None


def test_g2_future_truncation():
    p=climax_bars();ctx=dict(atr=100,ONL=999)
    ev=c.select_g2(p,ctx,'ONL')
    assert c.select_g2({k:v[:15] for k,v in p.items()},ctx,'ONL')==ev
    for v in p.values():v[15:]=999999
    assert c.select_g2(p,ctx,'ONL')==ev


def test_g1_stop_includes_minimum_distance_and_structural_low():
    p=bars();event=dict(boundary=15,low=990,high=1100)
    p['low'][15]=960
    t,_=c.execute(p,dict(atr=100),'G1_TIME',event)
    assert t['exit_price']==965
    event['low']=950;p['low'][15]=940
    t,_=c.execute(p,dict(atr=100),'G1_TIME',event)
    assert t['exit_price']==950


def test_entry_gap_invalidating_climax_stop_is_reported():
    t,status=c.execute(bars(),dict(atr=100),'G2_ONL_ALL_TIME',dict(boundary=15,low=1001))
    assert t is None and status=='STOP_NOT_BELOW_ENTRY'


def test_gap_stop_and_intrabar_stop_priority():
    p=bars();p['high'][16]=1100;p['low'][16]=900
    t,_=c.manage(p,15,1000,stop=950,target=1050)
    assert t['exit_price']==950 and t['reason']=='STOP'
    p['open'][16]=900
    t,_=c.manage(p,15,1000,stop=950,target=1050)
    assert t['exit_price']==900 and t['reason']=='STOP_GAP'


def test_live_target_at_open_precedes_later_intrabar_stop():
    p=bars();p['open'][16]=1060;p['high'][16]=1070;p['low'][16]=900
    t,_=c.manage(p,15,1000,stop=950,target=1050)
    assert t['exit_price']==1050 and t['reason']=='TARGET_OPEN'


def test_target_requires_trade_through():
    p=bars();p['high'][15]=1050
    t,_=c.manage(p,15,1000,target=1050)
    assert t['reason']=='TIME_1555'


def test_vwap_only_completed_minutes_not_current_bar():
    p=bars();v=c.vwap_before(p,15)
    p['high'][15:]=100000;p['volume'][15:]=100000
    assert c.vwap_before(p,15)==v


def test_marketable_vwap_is_zero_gross_not_filtered_win():
    t,status=c.manage(bars(),15,1001,vwap=True)
    assert status=='FILLED' and t['gross_points']==0 and t['net_points']==-1.225


def test_no_entry_bar_target_without_temporal_proof():
    p=bars();p['high'][10]=1100;p['low'][10]=990
    t,_=c.manage(p,10,995,target=1050,at_open=False)
    assert t['reason']=='TIME_1555'
    p['close'][10]=1051
    t,_=c.manage(p,10,995,target=1050,at_open=False)
    assert t['reason']=='TARGET' and t['exit_bar']==10


def test_1555_exit_does_not_see_1555_close():
    p=bars();p['open'][385]=1010;p['close'][385]=999999
    t,_=c.manage(p,15,1000)
    assert t['exit_bar']==385 and t['exit_price']==1010


def test_terminal_strong_day_not_known_before_final_close():
    p=bars();p['high'][0]=1100;p['close'][-1]=1090
    ctx=dict(atr=100,sma_today=1000)
    assert c.strong_day(p,ctx)
    assert not c.strong_day({k:v[:389] for k,v in p.items()},ctx)


def test_morning_dip_requires_trade_through_and_cancels_noon():
    p=bars();ctx=dict(atr=100)
    p['low'][10]=975
    assert c.dip_entry(p,ctx)[0] is None
    p['low'][150]=974
    assert c.dip_entry(p,ctx)[0] is None
    p['low'][149]=974
    t,_=c.dip_entry(p,ctx)
    assert t['entry_bar']==149 and t['entry_price']==975


def test_marks_and_summary_reconcile_after_costs():
    p=bars();p['open'][385]=1010
    t,_=c.manage(p,15,1000)
    x=r.attach(t,'2020-01-02','2019_2021','X',c.marks(t,p))
    s=r.describe([x])
    assert s['net_points']==8.775 and s['max_marked_drawdown']==1.225
    assert s['positive_quarters']==s['traded_quarters']==1


class Calendar:
    def grid(self, day):
        return pd.date_range(r.h.at(day,'09:30'),r.h.at(day,'16:00'),freq='min',inclusive='left')


def daily_data():
    days=pd.bdate_range('2020-01-02',periods=23).strftime('%Y-%m-%d').tolist()
    frames=[]
    for j,d in enumerate(days):
        g=pd.DataFrame({k:np.full(390,100+j if k!='volume' else 10) for k in c.FIELDS},index=Calendar().grid(d))
        g['trade_date']=d;g['contract']='NQH20';frames.append(g)
    return days,pd.concat(frames)


def test_sma_prior_twenty_does_not_use_today_close():
    days,a=daily_data()
    x=r.daily_features(a,days,Calendar(),[])
    assert x[days[19]]['bull'] is None
    assert x[days[20]]['sma_prior']==109.5 and x[days[20]]['bull'] is True
    a.loc[a.trade_date.eq(days[20]),'close']=999999
    y=r.daily_features(a,days,Calendar(),[])
    assert y[days[20]]['sma_prior']==x[days[20]]['sma_prior']


def test_panama_removes_daily_roll_gap_without_changing_raw_prices():
    days,a=daily_data();before=a.copy()
    roll=dict(session=days[20],spread_points=100.,spread_available_utc=r.h.at(days[19],'16:00').isoformat())
    a.loc[a.trade_date.ge(days[20]),['open','high','low','close']]+=100
    x=r.daily_features(a,days,Calendar(),[roll])
    assert x[days[21]]['prior_daily_close']==220
    assert x[days[21]]['sma_prior']==210.5
    assert a.loc[a.trade_date.eq(days[20]),'close'].iloc[-1]==220
    assert before.close.iloc[0]==100


def test_sma_missing_cash_day_is_not_skipped_or_forward_filled():
    days,a=daily_data();a=a.drop(Calendar().grid(days[10])[1])
    x=r.daily_features(a,days,Calendar(),[])
    assert x[days[20]]['bull'] is None


def test_future_roll_spread_rejected():
    days,a=daily_data()
    roll=dict(session=days[20],spread_points=100.,spread_available_utc=r.h.at(days[20],'10:00').isoformat())
    with pytest.raises(ValueError,match='Future rollover'):
        r.daily_features(a,days,Calendar(),[roll])


def test_final_outputs_preserve_universe_and_fees():
    if not r.RESULT.exists():pytest.skip('Fixed exploration not yet run')
    x=json.loads(r.RESULT.read_text())
    assert x['sessions']==1151 and len(x['performance']['COMBINED'])==20
    for m in c.MODELS:
        for b in r.BLOCKS:
            row=x['performance'][b][m]
            assert row['gross_points']-c.FEE*row['N']==pytest.approx(row['net_points'])
        assert x['performance']['COMBINED'][m]['N']==sum(x['performance'][b][m]['N'] for b in r.BLOCKS[1:])
    r.verify()
