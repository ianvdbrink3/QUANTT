"""Independent small examples and future-truncation regression checks."""
import json
import numpy as np
import pandas as pd
import pytest

from scripts.causal_map.core import (Event,catalog,select_events,outcome,volume_reference,
                                    cluster_inference,holm,size_bin)
from scripts.causal_map.__main__ import prepare, ROOT
from scripts.oos_preparation.adapter import Calendar,at


def prices(n=390):
    c=100+np.arange(n)*.01
    return dict(open=np.r_[100.,c[:-1]],close=c,high=c+.01,low=c-.01,volume=np.full(n,100.))


def ctx():
    return dict(opening=100.,atr=10.,PDH=102.,PDL=98.,prior_close=99.,ONH=101.,ONL=97.,on_open=98.,on_close=99.,
        volume_q95_1=np.full(390,150.),volume_mean_1=np.full(390,100.),
        volume_q95_5=np.full(78,750.),volume_mean_5=np.full(78,500.))


def test_catalog_and_family():
    c=catalog()
    assert len(c)==32 and len({x['id'] for x in c})==32
    assert [sum(x['category']==k for x in c) for k in 'ABCD']==[8,8,12,4]
    assert len(c)*4*2==256


def test_every_prefix_all_391_boundaries():
    p=prices();p['volume'][40:50]=200
    p['high'][44]=109;p['low'][44]=95
    full=select_events(p,ctx())
    for k in range(391):
        assert select_events({z:v[:k] for z,v in p.items()},ctx())==[e for e in full if e.boundary<=k]


def test_rewriting_all_future_data_does_not_rewrite_known_events():
    p=prices();a=select_events(p,ctx())
    q={z:v.copy() for z,v in p.items()}
    for z in ('open','close','high','low'):q[z][100:]*=2
    q['volume'][100:]*=1000
    b=select_events(q,ctx())
    assert [e for e in a if e.boundary<=100]==[e for e in b if e.boundary<=100]


@pytest.mark.parametrize('k,h,expected',[(0,15,14),(30,15,44),(1,30,30),(330,60,389),(330,'close',389)])
def test_exact_boundary_clock_horizon(k,h,expected):
    p=prices();e=Event('x',k,100.,1)
    o=outcome(p,e,h)
    assert o['endpoint_bar']==expected
    assert o['return_points']==p['close'][expected]-100
    assert o['minutes']==expected-k+1


def test_no_shortening_or_zero_length_at_close():
    p=prices()
    assert outcome(p,Event('x',380,100.,1),15) is None
    assert outcome(p,Event('x',390,100.,1),'close') is None
    assert outcome(p,Event('x',389,100.,1),'close')['minutes']==1


def test_confirmation_bar_wicks_excluded_from_excursions():
    p=prices();p['high'][19]=9999;p['low'][19]=.01
    o=outcome(p,Event('x',20,p['close'][19],1),15)
    assert o['mfe_points']<1 and o['mae_points']<1


def test_excursion_orientation_and_raw_returns():
    p=prices();p['high'][5]=110;p['low'][6]=90
    a=outcome(p,Event('x',0,100.,1),15);b=outcome(p,Event('x',0,100.,-1),15)
    assert a['return_points']==-b['return_points']
    assert a['raw_up_points']==b['raw_up_points']
    assert a['mfe_points']==b['mae_points']==10
    assert a['mae_points']==b['mfe_points']==10


def test_first_reach_not_hindsight_confirmation():
    p=prices();p['high'][10]=103;p['close'][10]=101.;p['close'][15]=104
    ev=[e for e in select_events(p,ctx()) if e.mechanism.startswith('A_PDH')]
    assert len(ev)==1 and ev[0].mechanism=='A_PDH_REJECT' and ev[0].boundary==11 and ev[0].direction==-1


def test_gap_over_is_reach_not_claimed_traded_touch():
    p=prices();x=ctx();x['PDH']=99
    ev=[e for e in select_events(p,x) if e.mechanism.startswith('A_PDH')]
    assert ev[0].boundary==1 and ev[0].mechanism=='A_PDH_ACCEPT'
    assert any(e.mechanism=='B_GAP_UP_0930' and e.boundary==0 for e in select_events({z:v[:0] for z,v in p.items()},x))


def test_final_bar_reach_logged_but_no_forward_outcome():
    p=prices();x=ctx();x['PDH']=200;p['high'][389]=201
    ev=[e for e in select_events(p,x) if e.mechanism.startswith('A_PDH')]
    assert len(ev)==1 and ev[0].boundary==390
    assert outcome(p,ev[0],'close') is None


def test_open_conditions_do_not_read_first_bar_close():
    p=prices();a=select_events({z:v[:0] for z,v in p.items()},ctx())
    p['close'][0]=1e6
    b=select_events({z:v[:0] for z,v in p.items()},ctx())
    assert a==b and any(e.mechanism.startswith('C_0930') for e in a)


def test_volume_reference_only_prior20_and_missing_not_zero():
    history=[np.full(390,float(k+1)) for k in range(21)]
    r=volume_reference(history)
    assert r['volume_mean_1'][0]==11.5
    assert r['volume_q95_1'][0]==np.quantile(np.arange(2,22),.95)
    history[-1][3]=np.nan;r=volume_reference(history)
    assert np.isnan(r['volume_q95_1'][3]) and np.isnan(r['volume_q95_5'][0])
    assert np.isfinite(r['volume_q95_1'][4])
    assert np.isnan(volume_reference(history[:19])['volume_q95_1']).all()


def test_volume_shock_requires_completed_block_and_preceding_extreme():
    p=prices();p['volume'][5:10]=1000
    a=select_events({z:v[:9] for z,v in p.items()},ctx())
    b=select_events({z:v[:10] for z,v in p.items()},ctx())
    assert not any(e.mechanism=='D_5m_HIGH' for e in a)
    assert any(e.mechanism=='D_5m_HIGH' and e.boundary==10 for e in b)


def test_duplication_inside_cluster_does_not_shrink_standard_error():
    x=np.tile([-2.,1.,3.,-1.,2.],20);ids=np.arange(100)
    a=cluster_inference(x,ids,100)
    b=cluster_inference(np.repeat(x,100),np.repeat(ids,100),100)
    assert b['se']==pytest.approx(a['se'],rel=1e-12)
    assert b['p']==pytest.approx(a['p'],rel=1e-12)
    assert b['hac_se']==pytest.approx(a['hac_se'],rel=1e-12)


def test_independent_scalar_sandwich():
    ids=np.repeat(np.arange(30),np.arange(1,31))
    x=np.sin(np.arange(len(ids)))+ids*.01
    avg=sum(x)/len(x)
    residuals=[sum(float(x[i])-avg for i in range(len(x)) if ids[i]==d) for d in range(30)]
    expected=(30/29*sum(z*z for z in residuals))**.5/len(x)
    assert cluster_inference(x,ids,30)['se']==pytest.approx(expected)


def test_sparse_cells_not_given_fake_pvalues():
    inf=cluster_inference(np.ones(100),np.repeat(np.arange(10),10),100)
    assert inf['p'] is None and inf['ci95'] is None


def test_holm_full_family_including_empty_cells():
    assert holm([.0001,None,.02])==pytest.approx([.0003,1.,.04])


@pytest.mark.parametrize('x,result',[(.499,'SMALL'),(.5,'MID'),(1.199,'MID'),(1.2,'LARGE')])
def test_size_boundaries(x,result):
    assert size_bin(x)==result


def test_context_ignores_same_and_future_day_close_prices():
    days=pd.bdate_range('2025-02-03',periods=24).strftime('%Y-%m-%d').tolist();parts=[]
    for j,d in enumerate(days):
        ix=pd.date_range(at(d,'09:30'),at(d,'16:00'),freq='min',inclusive='left')
        p=prices();g=pd.DataFrame(p,index=ix);g['trade_date']=d;g['contract']='TEST';parts.append(g)
    full=pd.concat(parts);cal=Calendar(json.loads((ROOT/'research/oos-year-calendar.json').read_text()))
    a=prepare(full,days,cal,[])
    cut=days[20];subset=days[:21]
    b=prepare(full[full.trade_date.le(cut)],subset,cal,[])
    for key in ('atr','PDH','PDL','prior_close','volume_q95_1'):
        assert np.allclose(a[cut][1][key],b[cut][1][key],equal_nan=True)
    changed=full.copy();changed.loc[changed.trade_date.ge(cut),['high','low','close']]*=2
    c=prepare(changed,days,cal,[])
    for key in ('atr','PDH','PDL','prior_close','volume_q95_1'):
        assert np.allclose(a[cut][1][key],c[cut][1][key],equal_nan=True)


def test_known_roll_translation_preserves_atr_and_maps_prior_levels():
    days=pd.bdate_range('2025-02-03',periods=24).strftime('%Y-%m-%d').tolist();parts=[]
    for j,d in enumerate(days):
        ix=pd.date_range(at(d,'09:30'),at(d,'16:00'),freq='min',inclusive='left')
        p=prices();g=pd.DataFrame(p,index=ix);g['trade_date']=d;g['contract']='OLD' if j<20 else 'NEW';parts.append(g)
    full=pd.concat(parts);cal=Calendar(json.loads((ROOT/'research/oos-year-calendar.json').read_text()))
    a=prepare(full,days,cal,[]);shifted=full.copy();mask=shifted.trade_date.ge(days[20])
    shifted.loc[mask,['open','high','low','close']]+=50
    rolls=[dict(session=days[20],spread_points=50.,spread_available_utc=at(days[19],'16:00'))]
    b=prepare(shifted,days,cal,rolls)
    assert b[days[21]][1]['atr']==pytest.approx(a[days[21]][1]['atr'])
    assert b[days[20]][1]['PDH']==pytest.approx(a[days[20]][1]['PDH']+50)
