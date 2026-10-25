from dataclasses import replace
import json
import numpy as np
import pytest
from scripts.ict_study import core as c


def bar(i,op=100,hi=101,lo=99,cl=100):return dict(start=i,end=i+1,valid=True,open=op,high=hi,low=lo,close=cl,volume=10)


def prices(n=480):return {k:np.full(n,100.,float) if k!='volume' else np.full(n,10.,float) for k in c.FIELDS}


def order(**kw):
    return dict(boundary=2,expires=10,direction=1,entry=100.,stop=98.,risk=2.,target=104.,valid_target=True,**kw)


def test_catalog_exact_eighty_unique_fixed_variants():
    specs=c.catalog();assert len(specs)==80 and len({s.name for s in specs})==80
    assert {s.timeframe for s in specs}=={1,5}
    assert sum(s.family=='ICT1' for s in specs)==24
    assert sum(s.family=='ICT2' for s in specs)==32
    assert sum(s.family=='ICT3' for s in specs)==24


def test_fvg_requires_closed_thirdbar_and_both_displacement_conditions():
    bars=[bar(0,hi=101,lo=99),bar(1,op=100,hi=105,cl=104),bar(2,lo=104,hi=106,cl=105)]
    assert c.fvg(bars,2,100)['direction']==1
    assert c.fvg(bars[:2],1,100) is None
    bad=[dict(b) for b in bars];bad[1]['close']=102
    assert c.fvg(bad,2,100) is None
    bad=[dict(b) for b in bars];bad[2]['low']=103.75
    assert c.fvg(bad,2,100) is None


def test_bearish_gap_mirrors_directional_body():
    bars=[bar(0,hi=105,lo=104),bar(1,op=105,hi=105,lo=100,cl=100),bar(2,hi=101,lo=99)]
    assert c.fvg(bars,2,100)['direction']==-1
    bars[1]['open']=98
    assert c.fvg(bars,2,100) is None


def test_fractal_only_known_two_bars_after_center_and_no_ties():
    bars=[bar(i,hi=h) for i,h in enumerate([101,102,110,103,104])]
    assert c.confirmed(bars[:4],3)=={}
    assert c.confirmed(bars,4)=={'high':110}
    bars[4]['high']=110
    assert 'high' not in c.confirmed(bars,4)


def test_incomplete_signal_block_is_not_forward_filled():
    p=prices();p['close'][92]=np.nan
    assert c.aggregate(p,5)[18]['valid'] is False


def test_limit_cannot_fill_in_forming_or_preconfirmation_bar():
    p=prices();p['low'][:92]=90;p['low'][92:]=101;p['high'][92:]=102;p['open'][92:]=101;p['close'][92:]=101
    assert c.execute(p,order())[1]=='UNFILLED_FIRST_ORDER'


def test_touch_vs_one_tick_fill_sensitivity_and_no_reselection():
    p=prices();p['open'][90:]=101;p['high'][90:]=102;p['close'][90:]=101;p['low'][90:]=100
    a,status=c.execute(p,order(),True);assert status=='FILLED' and a['entry_bar']==2
    assert c.execute(p,order(),False)[1]=='UNFILLED_FIRST_ORDER'
    p['low'][95]=99.75
    assert c.execute(p,order(),False)[0]['entry_bar']==5


def test_same_minute_stop_target_conflict_is_stop_first():
    p=prices();p['open'][92]=101;p['low'][92]=97;p['high'][92]=105;p['close'][92]=104
    t,_=c.execute(p,order());assert t['reason']=='STOP' and t['net_points']==pytest.approx(-3.225)


def test_entry_intrabar_target_requires_proven_later_cross():
    p=prices();p['open'][92]=102;p['low'][92]=99;p['high'][92]=105;p['close'][92]=101
    t,_=c.execute(p,order());assert t['exit_bar']!=2
    p['close'][92]=104
    assert c.execute(p,order())[0]['reason']=='TARGET'


def test_adverse_gap_can_lose_more_than_one_stop_R_and_full_fee():
    p=prices();p['open'][92]=95;p['low'][92]=94;p['close'][92]=96;p['high'][92]=97
    t,_=c.execute(p,order());assert t['exit_price']==95 and t['net_stop_R']<-1
    assert t['net_points']==pytest.approx(t['gross_points']-1.225)


def test_short_execution_is_symmetric_and_does_not_turn_losses_into_longs():
    p=prices();p['open'][92]=99;p['high'][92]=103;p['low'][92]=95;p['close'][92]=96
    o=order();o.update(direction=-1,stop=102,target=96)
    t,_=c.execute(p,o);assert t['reason']=='STOP' and t['gross_points']==-2


def test_flat_time_uses_1555_open_not_its_later_highlowclose():
    p=prices();p['open'][475]=103;p['high'][475]=1000;p['low'][475]=1;p['close'][475]=999
    t,_=c.execute(p,order());assert t['reason']=='TIME_1555' and t['gross_points']==3


def test_invalid_opposite_liquidity_target_never_looks_for_later_better_setup():
    o=order();o['valid_target']=False
    assert c.execute(prices(),o)[1]=='INVALID_FIRST_TARGET_NO_RESELECT'


def test_judas_shorts_require_preknown_bear_regime_and_bull_only_is_subset():
    both=c.Spec('ICT3',1,'BOTH','OPEN0930','JUDAS','2R')
    assert c.allowed(both,{'bull':False,'bear':True},-1)
    assert not c.allowed(both,{'bull':True,'bear':False},-1)
    assert not c.allowed(replace(both,bias='BULL_LONG'),{'bull':False,'bear':True},-1)


def test_retarget_preserves_first_event_and_minimum_risk():
    o=order();spec=c.Spec('ICT1',5,'BOTH','ON','REVERSAL','3R')
    assert c.retarget(o,{},spec)['target']==106
    assert c.retarget(o,{},spec)['boundary']==2


def test_nonoverlapping_reference_clock_windows_are_exact():
    assert c.window(c.Spec('ICT2',5,'BOTH','AM','FADE','2R'))==(30,90)
    assert c.window(c.Spec('ICT2',5,'BOTH','PM','FADE','2R'))==(270,330)


def test_source_replay_preserves_entire_committed_benchmark_and_no_raw_export():
    from scripts.ict_study import __main__ as run
    run.verify();x=json.loads(run.RESULT.read_text())
    assert len(x['catalog'])==80 and x['bootstrap']['family_tests']==480
    assert x['future_cutoff_checks']>=1151*32
    assert sum(x['samples']['TOUCH'][b][run.NAMES[0]]['cash_days'] for b in ('2019_2021','2024_2026'))==1171
    assert json.loads(run.PROOF.read_text())['status']=='BYTE_IDENTICAL_ICT_SOURCE_REPLAYS'
    assert all(x['benchmarks'][b]['B']['N']==n for b,n in [('2019_2021',97),('2024_2026',52),('COMBINED',149)])


def causal_chain():
    p=prices();p['high'][87]=105  # 09:27 pivot, confirmed at09:30
    for i,values in [(90,(101,101.5,100.5,101)),(91,(101,107,101,106)),(92,(103,108,102.5,107))]:
        for key,value in zip(('open','high','low','close'),values):p[key][i]=value
    ctx=dict(atr=30,ON=(100.75,110),ONL=100.75,ONH=110,OPEN0930=101,bull=True,bear=False)
    spec=c.Spec('ICT1',1,'BOTH','ON','REVERSAL','2R')
    return p,ctx,spec


def test_real_sweep_mss_fvg_chain_and_minimum_stop_are_causal():
    p,ctx,spec=causal_chain();o=c.signal(p,ctx,spec)
    assert o is not None and o['boundary']==3 and o['sweep_boundary']==1 and o['mss_boundary']==2
    assert o['risk']==pytest.approx(3) and o['stop']==99.5
    prefix={k:v[:93] for k,v in p.items()}
    assert c.signal(prefix,ctx,spec)==o
    assert c.signal({k:v[:92] for k,v in p.items()},ctx,spec) is None
    poison={k:v.copy() for k,v in p.items()}
    for v in poison.values():v[93:]=1e8
    assert c.signal(poison,ctx,spec)==o


def test_sweep_and_displacement_middle_cannot_be_same_bar():
    p,ctx,spec=causal_chain();p['low'][90]=101;p['low'][91]=100.5
    assert c.signal({k:v[:93] for k,v in p.items()},ctx,spec) is None


def test_day_adapter_copies_readonly_pandas_arrays_before_masking():
    import pandas as pd
    from scripts.ict_study import __main__ as run
    day='2025-06-17';ix=pd.date_range(run.h.at(day,'08:00'),run.h.at(day,'16:00'),freq='min',inclusive='left')
    frame=pd.DataFrame({k:np.full(len(ix),100.) for k in c.FIELDS},index=ix);frame['usable']=True
    rth={k:np.full(390,100.) for k in c.FIELDS}
    features=dict(bull=True,prior_daily_close=101,sma_prior=100)
    p,ctx=run.day_input(dict(groups={day:frame},state={day:(rth,dict(atr=30,ONL=99,ONH=110))},features={day:features}),day)
    assert len(p['open'])==480 and ctx['OPEN0930']==100


def test_judas_minimum_015_atr_includes_exact_boundary():
    p=prices();ctx=dict(atr=30,OPEN0930=102.25,bull=True,bear=False)
    for i,values in [(90,(102.25,102.5,97.75,101)),(91,(102,110,101,108)),(92,(104,111,103.5,109))]:
        for key,value in zip(('open','high','low','close'),values):p[key][i]=value
    spec=c.Spec('ICT3',1,'BULL_LONG','OPEN0930','JUDAS','2R')
    assert c.signal(p,ctx,spec)['boundary']==3


def test_cached_aggregation_is_identical_to_independent_prefix_aggregation():
    p,ctx,spec=causal_chain()
    assert c.signal(p,ctx,spec,c.aggregate(p,1))==c.signal(p,ctx,spec)
    assert c.aggregate(p,5)[:19]==c.aggregate({k:v[:95] for k,v in p.items()},5)
