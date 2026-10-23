"""Synthetic technical tests. Never call a strategy on the locked remainder."""
import ast
import inspect
import json
import numpy as np
import pandas as pd
import pytest

from scripts import prepare_historical_contracts as h
from scripts.edge_marathon.features import calendar_context
from scripts.oos_preparation.adapter import at


def frame(ix,contract='NQH19',price=100.):
    f=pd.DataFrame(dict(open=price,high=price+.25,low=price-.25,close=price,
        volume=10.,contract=contract),index=ix)
    f['trade_date']=h.session_dates(ix)
    f['numeric_valid']=True;f['usable']=True;f['conflicting_duplicate']=False
    return f


def test_same_contract_identical_only_dedup():
    ix=pd.date_range(at('2019-01-14','09:30'),periods=2,freq='min')
    a=frame(ix);b=a.copy()
    full,r=h.reconcile([a,b])
    assert len(full)==2 and r['duplicate_rows_removed']==2 and r['conflicting_keys']==0
    assert full.usable.all()


def test_cross_contract_minutes_not_dedup():
    ix=pd.date_range(at('2019-01-14','09:30'),periods=2,freq='min')
    full,r=h.reconcile([frame(ix),frame(ix,'NQM19')])
    assert len(full)==4 and not r['duplicate_rows_removed']


def test_conflict_quarantined_not_selected_for_use():
    ix=pd.date_range(at('2019-01-14','09:30'),periods=2,freq='min')
    a=frame(ix);b=a.copy();b.loc[ix[0],'volume']=11
    full,r=h.reconcile([a,b])
    assert r['conflicting_keys']==1
    assert not full.loc[ix[0],'usable']
    assert full.loc[ix[1],'usable']


@pytest.mark.parametrize('column,value,flag',[
    ('close',100.1,'off_tick'),('volume',0,'invalid_volume'),
    ('volume',1.5,'invalid_volume'),('open',0,'nonpositive_price'),
    ('high',99,'incoherent'),('close',np.nan,'nonfinite')])
def test_numeric_diagnostics(column,value,flag):
    g=frame(pd.DatetimeIndex([at('2019-01-14','09:30')]))
    g.loc[g.index[0],column]=value
    assert h.numeric_flags(g)[flag].iloc[0]


def test_cash_calendar_and_year_end():
    assert len(h.cash_dates('2019-01-01','2019-12-31'))==252
    assert len(h.cash_dates('2020-01-01','2020-12-31'))==253
    assert len(h.cash_dates('2021-01-01','2021-12-31'))==252
    assert '2021-12-31' in h.cash_dates('2021-12-01','2021-12-31')
    assert h.cash_context('2021-12-31')['tom_position']=='T-1'
    assert h.cash_context('2021-01-01')['tom'] is False


def test_calendar_old_supported_year_parity():
    for a,b in [('2018-11-01','2019-12-31'),('2022-12-01','2026-12-31')]:
        for d in pd.bdate_range(a,b).strftime('%Y-%m-%d'):
            assert h.cash_context(d)==calendar_context(d),d


def test_pause_removed_on_20210628():
    c=h.HistoricalCalendar()
    assert len(c.grid('2021-06-25'))==1365
    assert at('2021-06-25','16:20') not in c.grid('2021-06-25')
    assert len(c.grid('2021-06-28'))==1380
    assert at('2021-06-28','16:20') in c.grid('2021-06-28')


@pytest.mark.parametrize('before,after,delta',[
    ('2019-03-08','2019-03-11',-1),('2019-11-01','2019-11-04',1),
    ('2020-03-06','2020-03-09',-1),('2020-10-30','2020-11-02',1),
    ('2021-03-12','2021-03-15',-1),('2021-11-05','2021-11-08',1)])
def test_DST_Chicago_NY_UTC(before,after,delta):
    x,y=at(before,'09:30'),at(after,'09:30')
    assert y.hour-x.hour==delta
    for t in (x,y):assert t.tz_convert('America/Chicago').strftime('%H:%M')=='08:30'


def test_half_session_not_corruption_or_full_eligible():
    day='2020-11-27';c=h.HistoricalCalendar()
    g=frame(c.grid(day),'NQZ20')
    row=h.assess_day(g,day,'NQZ20',c)
    assert row['cash_half'] and not row['clean_full_RTH']
    assert row['gap_classification']=='SCHEDULED_CASH_EXCEPTION_OR_EXPIRY'


def test_halt_not_imputed_or_eligible():
    day='2020-03-09';c=h.HistoricalCalendar()
    ix=c.grid(day);ix=ix[(ix<at(day,'09:35'))|(ix>=at(day,'09:49'))]
    row=h.assess_day(frame(ix,'NQH20'),day,'NQH20',c)
    assert row['known_circuit_breaker_date'] and row['rth_missing']==14
    assert not row['clean_full_RTH']


def test_expiry_not_calendar_roll():
    assert h.expiry('NQH19')=='2019-03-15'
    assert h.expiry('NQM20')=='2020-06-19'
    c=h.HistoricalCalendar();g=frame(c.grid('2019-03-15'))
    row=h.assess_day(g,'2019-03-15','NQH19',c)
    assert row['expiry_or_later']
    assert row['unexpected_session_minutes']>0


def test_future_cutoff_volume_roll_and_ATR_context():
    c=h.HistoricalCalendar();parts=[]
    days=pd.bdate_range('2018-11-19','2018-12-20').strftime('%Y-%m-%d').tolist()
    for day in days:
        ix=c.grid(day)
        if len(ix):
            for contract in ('NQZ18','NQH19'):
                g=frame(ix,contract,100 if contract=='NQZ18' else 110)
                g.volume=20 if contract=='NQZ18' else 10 if day<'2018-12-17' else 30
                parts.append(g)
    full=pd.concat(parts).sort_index()
    schedule,rolls,failure=h.roll_route(full,['NQZ18','NQH19'],c)
    assert failure is None and rolls[0]['effective_session']=='2018-12-18'
    assert rolls[0]['future_cutoff_verified']
    active=h.select_active(full,schedule)
    causal=h.roll_spreads(full,schedule)
    scheduled=[d for d in days if len(c.grid(d))]
    state=h.contexts(active,scheduled,c,causal)
    cutoff='2018-12-18'
    short=h.contexts(active[active.trade_date.le(cutoff)],[d for d in scheduled if d<=cutoff],c,causal)
    for key,value in state[cutoff][1].items():
        np.testing.assert_equal(value,short[cutoff][1][key])
    assert state[cutoff][1]['PDH']==110.25
    assert state[cutoff][1]['atr']==.5
    # Raw new contract was not back-adjusted.
    assert active[active.trade_date.eq(cutoff)].open.eq(110).all()


def test_unproven_roll_stops_no_fallback():
    c=h.HistoricalCalendar();ix=c.grid('2018-12-13')
    f=pd.concat([frame(ix,'NQZ18'),frame(ix,'NQH19')]).sort_index()
    schedule,rolls,failure=h.roll_route(f,['NQZ18','NQH19'],c)
    assert failure and not rolls and len(schedule)==1


def test_scoring_functions_absent_from_quality_route():
    tree=ast.parse(inspect.getsource(h))
    called={n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
    named={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
    assert not (called|named)&{'select','fill','hypotheses','outcome','replay_sample'}
    assert json.loads(h.PROTOCOL.read_text())['release'] is False
