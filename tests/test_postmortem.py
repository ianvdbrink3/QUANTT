import pandas as pd
from scripts.reproduce_research import engine
from scripts.reproduce_research.postmortem import warmup_audit,trade_diagnostics


def test_inactive_history_already_makes_atr_ready_without_cross_contract_prices():
    frames=[]
    for day in pd.bdate_range('2025-05-20','2025-06-17'):
        day=day.strftime('%Y-%m-%d')
        if day=='2025-05-26':
            continue
        ix=pd.date_range(engine.time_at(day,'09:30'),engine.time_at(day,'16:00'),freq='min',inclusive='left')
        frames.append(pd.DataFrame({'open':100.,'high':102.,'low':99.,'close':100.,
                                    'volume':10,'contract':'NQU25','trade_date':day},index=ix))
    audit,summary=warmup_audit(pd.concat(frames),[{'to':'NQU25','effective_session':'2025-06-17'}])
    assert summary[0]['atr_ready_at_roll']
    assert summary[0]['valid_prior_tr_at_roll']>=14
    assert summary[0]['zero_lost_sessions_possible_under_frozen_rules']
    assert audit.iloc[-1].prior_atr14==3.


def test_one_missing_rth_minute_invalidates_today_and_next_true_range():
    frames=[]
    for day in ['2025-06-10','2025-06-11','2025-06-12']:
        ix=pd.date_range(engine.time_at(day,'09:30'),engine.time_at(day,'16:00'),freq='min',inclusive='left')
        if day=='2025-06-11':
            ix=ix.delete(30)
        frames.append(pd.DataFrame({'open':100.,'high':102.,'low':99.,'close':100.,
                                   'volume':10,'contract':'NQU25','trade_date':day},index=ix))
    audit,_=warmup_audit(pd.concat(frames),[])
    assert audit.valid_tr_today.sum()==0
    assert audit.rth_complete.tolist()==[True,False,True]


def test_return_to_range_is_fixed_post_entry_close_not_touch_or_optimized_exit():
    day='2025-07-14'; signal=engine.time_at(day,'09:45')
    ix=pd.date_range(signal,periods=16,freq='min')
    g=pd.DataFrame({'open':102.,'high':103.,'low':99.,'close':102.,'volume':10,
                    'trade_date':day,'contract':'NQU25','orb15_high':101.,'orb15_low':99.,'atr14_prior':10.},index=ix)
    g.loc[ix[3],'close']=100.  # Two minutes after entry, not first bar.
    t=pd.DataFrame([{'trade_date':day,'contract':'NQU25','signal_utc':signal,
                     'entry_utc':ix[1],'entry_price':102.,'direction':1,'net_points':-1.225,
                     'mfe_bar_bound_points':1.,'mae_bar_bound_points':3.}])
    r=trade_diagnostics(g,t).iloc[0]
    assert not r.return_inside_1m
    assert r.return_inside_5m and r.return_inside_15m
    assert r.forward15_mfe==1. and r.forward15_mae==3.
