import copy
import numpy as np
import pandas as pd
import pytest
from scripts.edge_marathon.core import catalog,select,fill
from scripts.edge_marathon.features import calendar_context,enrich
from scripts.edge_marathon.stats import holm,inference,metrics
from scripts.edge_marathon.runner import collect
from scripts.oos_preparation.adapter import at


def prices():
    close=np.linspace(100,110,390)
    return dict(open=close.copy(),close=close.copy(),high=close+1,low=close-1,volume=np.ones(390)*100)


def ctx():
    return dict(tom=True,atr=12.,atr_p90=15.,atr_regime='MID',PDH=103.,PDL=97.,ONH=120.,ONL=90.,
        prior_close=100.,overnight_complete=True,overnight_open=101.,overnight_high=121.,overnight_low=89.,
        on_close=100.,week_open=99.,friday=True,inventory_condition=True,overnight_direction=1)


def test_fixed25_family_no_grid():
    assert len(catalog())==25 and len(set(catalog()))==25


def test_tom_calendar_closed_and_short_sessions_not_replaced():
    assert calendar_context('2025-01-02')['tom_position']=='T+1'
    assert calendar_context('2025-01-06')['tom_position']=='T+3'
    assert not calendar_context('2025-01-07')['tom']
    assert not calendar_context('2025-01-01')['tom']
    assert calendar_context('2025-11-28')['tom_position']=='T-1'
    assert not calendar_context('2025-11-26')['tom']


@pytest.mark.parametrize('boundary',[1,5,30,60,240,300,330,385])
def test_prefix_and_mutation_before_any_real_outcomes(boundary):
    p=prices();c=ctx();full=select(p,c)
    expected=[e for e in full if e['decision']<=boundary]
    assert select({k:v[:boundary] for k,v in p.items()},c)==expected
    other={k:v.copy() for k,v in p.items()}
    for field in ('open','high','low','close'):other[field][boundary:]+=100000
    assert [e for e in select(other,c) if e['decision']<=boundary]==expected


def test_overnight_signal_known_without_future_rth_or_overnight_quality():
    c=ctx();p={k:v[:0] for k,v in prices().items()}
    a=select(p,c)
    c.update(overnight_complete=False,overnight_open=np.nan,ONH=np.nan,ONL=np.nan,atr=np.nan)
    assert a==select(p,c)
    assert a==[dict(model='TOM_OVERNIGHT_1030',decision=-930,entry=-930,end=60,direction=1)]


def test_trend_filter_uses_only_confirming_close():
    p=prices();c=ctx();p['close'][29]=99.
    assert not any(e['model']=='TOM_TREND_1000' for e in select(p,c))
    p['close'][29]=101.
    e=next(e for e in select(p,c) if e['model']=='TOM_TREND_1000')
    assert e['decision']==e['entry']==30


def test_missing_atr_history_never_uses_full_sample_percentile():
    c=ctx();c['atr_p90']=np.nan
    assert not any(e['model']=='TOM_ATR_CAP' for e in select(prices(),c))


def test_compression_first_closed5bar_next_open():
    p=prices();c=ctx();p['close'][:5]=100;p['close'][4]=104
    e=next(e for e in select(p,c) if e['model']=='COMPRESSED_BREAK5')
    assert e['decision']==e['entry']==5
    assert e['direction']==1
    p['open'][5]=105;p['close'][-1]=107
    r=fill(e,p,c)
    assert r['entry_price']==105 and r['net_points']==2-1.225


def test_sweep_both_sides_excluded_and_reversal_confirmed():
    p=prices();c=ctx();p['low'][0]=89;p['close'][29]=102
    e=[e for e in select(p,c) if e['model'].startswith('SWEEP')]
    assert len(e)==2 and all(x['direction']==1 for x in e)
    p['high'][5]=121
    assert not any(e['model'].startswith('SWEEP') for e in select(p,c))


def test_afternoon_frozen_upper_bound_exclusive():
    p=prices();c=ctx();p['high'][:300]=111;p['low'][:300]=99;c['atr']=10
    assert not any(e['model'].startswith('AFTERNOON') for e in select(p,c))
    p['high'][:300]=110.9
    rows=[e for e in select(p,c) if e['model'].startswith('AFTERNOON')]
    assert {e['entry'] for e in rows}=={330}
    assert {e['end'] for e in rows}=={332,345}
    assert {e['decision'] for e in rows}=={300}


def test_overnight_excursion_and_missing_future_quality():
    e=dict(model='X',decision=-930,entry=-930,end=60,direction=1)
    p=prices();c=ctx();r=fill(e,p,c)
    assert r['entry_price']==101.
    assert r['mfe_points']==20 and r['mae_points']==12
    c['overnight_complete']=False
    with pytest.raises(ValueError):fill(e,p,c)


def test_outcome_truncation_no_shortened_horizon():
    e=dict(model='X',decision=30,entry=30,end=390,direction=1)
    with pytest.raises(ValueError):fill(e,{k:v[:60] for k,v in prices().items()},ctx())


def test_holm_includes_unavailable_cells_and_monotonicity():
    assert holm([.01,.04,1.])==pytest.approx([.03,.08,1.])
    assert holm([1.]*25)==[1.]*25


def test_sparse_fragment_information_gate_and_exact_signflip():
    calendar=list(pd.bdate_range('2019-01-02',periods=8).strftime('%Y-%m-%d'))
    rows=[dict(day=d,net_points=2.) for d in calendar]
    result=inference(rows,calendar,reps=50)
    assert result['signflip_p']==2/256
    assert result['conservative_p']==1.
    assert result['conservative_status']=='DATA_INSUFFICIENT'
    assert 'EXACT_ENUMERATION' in result['signflip_method']


def test_risk_metrics_initial_zero_and_no_fake_infinite_pf():
    calendar=list(pd.bdate_range('2025-01-02',periods=4).strftime('%Y-%m-%d'))
    rows=[dict(day=d,net_points=x,gross_points=x+1.225,mae_points=10.,mfe_points=20.,atr=100.,direction=1)
          for d,x in zip(calendar,[-10.,-20.,40.,-5.])]
    m=metrics(rows,calendar)
    assert m['drawdown']==30.
    assert m['max_consecutive_losses']==2
    assert m['net_points']==5.
    assert m['slippage'][-1]['net_points']==1.
    assert m['daily_sharpe'] is not None


def test_enrichment_percentiles_use_only_previous_days():
    days=list(pd.bdate_range('2024-01-02',periods=62).strftime('%Y-%m-%d'))
    state={d:(prices(),dict(ctx(),atr=float(j+1))) for j,d in enumerate(days)}
    empty=pd.DataFrame(columns=['trade_date','open','high','low','close','volume'])
    empty.index=pd.DatetimeIndex([],tz='UTC')
    enriched=enrich(state,days,empty,[])
    assert np.isnan(enriched[days[59]][1]['atr_p90'])
    assert enriched[days[60]][1]['atr_p90']==pytest.approx(np.quantile(np.arange(1,61),.9))
    altered=copy.deepcopy(state);altered[days[61]][1]['atr']=1e12
    again=enrich(altered,days,empty,[])
    assert again[days[60]][1]['atr_p90']==enriched[days[60]][1]['atr_p90']
