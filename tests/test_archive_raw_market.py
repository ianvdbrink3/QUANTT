"""Independent hand-computed examples; no real-data strategy calculation."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts import raw_market as m
from scripts.archive_experiments import verify_archive
from scripts.execution_reality_audit import extra_stop_friction
from scripts.reproduce_research import engine
from scripts.oos_preparation.adapter import at,Calendar
from scripts.oos_preparation.year import forbid_scoring

ROOT=Path(__file__).resolve().parents[1]


def fixture_bars(start='09:59',end='12:00'):
    day='2026-08-03';ix=pd.date_range(at(day,start),at(day,end),freq='min',inclusive='left')
    return pd.DataFrame(dict(open=100.,high=101.,low=99.,close=100.,volume=10,
                             contract='NQU26',trade_date=day,data_quality_flag='ok'),index=ix)


def test_archive_rejects_changed_experiment(tmp_path):
    (tmp_path/'research').mkdir();(tmp_path/'engine.py').write_text('changed')
    (tmp_path/'research/archived-experiments.json').write_text(json.dumps(dict(status='ARCHIVED_NOT_VALIDATED',
        models={x:{} for x in ['B_ORB5','B_ORB15','A_London_sweep','C_VWAP_extreme']},files_sha256={'engine.py':'0'*64})))
    with pytest.raises(ValueError,match='Archived experiment bytes'):verify_archive(tmp_path)


def test_all_archived_bytes_remain_intact():
    assert verify_archive()['status']=='ARCHIVED_NOT_VALIDATED'


def test_signal_bar_cannot_fill_or_stop_the_trade():
    g=fixture_bars();g.loc[g.index[0],['open','high','low','close']]=[100,200,1,150]
    r=engine.simulate(g,g.index[0],1,10,20)
    assert r['entry_utc']==g.index[1] and r['entry_price']==100
    assert r['exit_reason']=='noon' and r['net_points']==-1.225


@pytest.mark.parametrize('direction',[1,-1])
def test_entry_bar_both_barriers_stop_first(direction):
    g=fixture_bars();g.loc[g.index[1],['high','low']]=[125,75]
    r=engine.simulate(g,g.index[0],direction,10,20)
    assert r['exit_bar_utc']==r['entry_utc'] and r['exit_reason']=='stop_both'
    assert r['gross_points']==-10 and r['net_usd']==pytest.approx(-224.5)


@pytest.mark.parametrize('direction,price',[ (1,80.),(-1,120.) ])
def test_adverse_stop_gap_worse_open(direction,price):
    g=fixture_bars();g.loc[g.index[2],['open','high','low','close']]=[price,price+1,price-1,price]
    r=engine.simulate(g,g.index[0],direction,10,20)
    assert r['exit_reason']=='stop' and r['exit_price']==price and r['gross_points']==-20


def test_target_gap_no_price_improvement():
    g=fixture_bars();g.loc[g.index[2],['open','high','low','close']]=[130,131,129,130]
    r=engine.simulate(g,g.index[0],1,10,20)
    assert r['exit_reason']=='target' and r['exit_price']==120


def test_invalid_vwap_target_not_a_limit_entry():
    g=fixture_bars();assert engine.simulate(g,g.index[0],1,10,target=90) is None


def test_timeout_last_minute_close_and_tick_rounding():
    g=fixture_bars();g.loc[g.index[-1],'close']=100.5
    r=engine.simulate(g,g.index[0],1,10.24,20.01)
    assert r['stop']==90 and r['target']==120.25
    assert r['exit_bar_utc']==at('2026-08-03','11:59') and r['exit_price']==100.5


def test_missing_next_minute_prevents_fill():
    g=fixture_bars();assert engine.simulate(g.drop(g.index[1]),g.index[0],1,10,20) is None


def test_vwap_proxy_reset_and_population_sd_by_hand(monkeypatch):
    g=fixture_bars('18:00','18:03');day='2026-08-03'
    # Small two-session synthetic samples; complete-session gates are irrelevant
    # to verifying the exact primitive formula and its availability time.
    g['trade_date']=day
    g.loc[g.index,['high','low','close']]=[[102,98,100],[108,102,105],[111,105,108]]
    g['open']=[100,105,108];g['volume']=[1,3,2]
    second=g.copy();second.index=second.index+pd.Timedelta(days=1);second['trade_date']='2026-08-04'
    full=pd.concat([g,second]);monkeypatch.setattr(engine,'expected_grid',lambda d:full[full.trade_date.eq(d)].index)
    enriched,*_=engine.build_features(full)
    # HLC3=[100,105,108], cumulative VWAP at second bar=(100+315)/4.
    assert enriched.loc[g.index[1],'vwap_close']==103.75
    assert enriched.loc[g.index[1],'vwap_sd_close']==pytest.approx(np.sqrt((10000+3*11025)/4-103.75**2))
    assert enriched.loc[second.index[0],'vwap_close']==100
    assert enriched.loc[g.index[1],'feature_available_at_utc']==g.index[1]+pd.Timedelta(minutes=1)


def test_extra_stop_cost_only_applies_to_stop_fills():
    t=pd.DataFrame(dict(exit_reason=['stop','stop_both','target','noon'],net_points=[-10.,-20.,30.,4.]))
    for ticks in [1,2]:
        r=extra_stop_friction(t,ticks)
        assert r['extra_cost_usd']==2*ticks*5
        assert r['net_points']==pytest.approx(4-2*ticks*.25)


def test_bootstrap_resamples_whole_days_with_fixed_row_totals():
    w=m.block_weights(29,reps=100);assert w.shape==(100,29) and (w.sum(axis=1)==29).all()
    np.testing.assert_array_equal(w,m.block_weights(29,reps=100))


def test_correlations_hand_calculated_and_constant_undefined():
    x=np.arange(25,dtype=float);w=m.block_weights(25,reps=100)
    assert m.correlation(x,2*x+3,np.arange(25),w)['coefficient']==pytest.approx(1)
    assert m.correlation(x,-x,np.arange(25),w)['coefficient']==pytest.approx(-1)
    assert m.correlation(x,np.ones(25),np.arange(25),w)['coefficient'] is None


def test_day_cluster_mean_and_median_match_observation_distribution():
    w=np.ones((100,25),dtype=int);x=np.arange(25,dtype=float)
    r=m.summarize(x,np.arange(25),w)
    assert r['mean']==r['mean_ci_low']==r['median_ci_low']==12
    assert r['days']==25 and r['n']==25


def test_pdh_gap_without_actual_observed_touch_is_excluded():
    g=fixture_bars('09:30','09:35')
    rows,c=m.event_rows('2026-08-03',g,pdh=90,pdl=110)
    assert c['PDH_TOUCH']==c['PDL_TOUCH']==0


def test_event_first_touch_and_future_endpoint_from_bar_close():
    g=fixture_bars('09:30','16:00');g['close']=100+np.arange(len(g))*.1;g['high']=g.close+1;g['low']=g.close-1
    rows,c=m.event_rows('2026-08-03',g,pdh=100,pdl=90)
    assert c['PDH_TOUCH']==1 and c['RECORD_HIGH']==389 and c['RECORD_LOW']==0
    a=next(r for r in rows if r['event']=='PDH_TOUCH' and r['horizon']=='15m')
    assert a['return_points']==pytest.approx(1.5)
    assert pd.Timestamp(a['event_known_utc'])==g.index[0]+pd.Timedelta(minutes=1)
    assert all(r['minutes_to_endpoint']>0 for r in rows)


def test_equal_record_prices_are_not_new_records():
    rows,c=m.event_rows('2026-08-03',fixture_bars('09:30','16:00'))
    assert c['RECORD_HIGH']==c['RECORD_LOW']==0 and not rows


def test_raw_measurement_full_session_sum_and_same_contract_previous_day():
    days=['2026-08-03','2026-08-04'];c=Calendar(dict(reviewed_ranges=[[days[0],days[1]]],closes_ny={}))
    parts=[]
    for day,contract,px in [(days[0],'OLD',100),(days[0],'NEW',200),(days[1],'NEW',200)]:
        ix=pd.date_range(at(day,'09:29'),at(day,'16:00'),freq='min',inclusive='left')
        parts.append(pd.DataFrame(dict(open=px,high=px+1,low=px-1,close=px,volume=10,contract=contract,trade_date=day),index=ix))
    from scripts.reproduce_research.next_engine import Activation
    with forbid_scoring():
        _,slots,_,daily,_,quality=m.measure(pd.concat(parts).sort_index(),[Activation('OLD',days[0]),Activation('NEW',days[1])],c,*days)
    assert slots.groupby('day').volume_share.sum().eq(1).all()
    assert daily.iloc[1].close_close_bps==daily.iloc[1].overnight_bps==0
    assert quality[1]['prior_same_contract_RTH_complete']


def test_no_strategy_calls_allowed_in_raw_route():
    with forbid_scoring():
        for name in ['build_features','hypotheses','simulate','baseline']:
            with pytest.raises(PermissionError):getattr(engine,name)(None)


def test_holm_global_family_includes_missing_tests():
    out=m.holm([.001,.04,None]);np.testing.assert_allclose(out,[.003,.08,1])


def test_registered_raw_protocol_fixed_family_no_new_validation():
    p=json.loads((ROOT/'research/raw-market-protocol.json').read_text())
    assert p['multiplicity']['hypotheses']==43 and p['no_new_holdout_claim']
    assert p['no_entries_stops_targets_or_parameter_search'] and p['uncertainty']['block_sessions']==5


def test_event_cluster_bootstrap_matches_explicit_replication():
    # Unequal numbers of events per day; exact brute-force oracle for every draw.
    di=np.r_[np.arange(25),0,0,1];x=np.r_[np.arange(25,dtype=float),100.,-50.,75.]
    w=m.block_weights(25,reps=100);r=m.summarize(x,di,w)
    expanded=[np.repeat(x,row[di]) for row in w]
    means=np.array([a.mean() for a in expanded]);medians=np.array([np.median(a) for a in expanded])
    assert r['mean_ci_low']==pytest.approx(np.quantile(means,.025))
    assert r['mean_ci_high']==pytest.approx(np.quantile(means,.975))
    assert r['median_ci_low']==pytest.approx(np.quantile(medians,.025))
    assert r['median_ci_high']==pytest.approx(np.quantile(medians,.975))


def test_future_prices_cannot_change_record_identification_in_past():
    g=fixture_bars('09:30','16:00');g['high']=101+np.arange(len(g))*.01
    a,_=m.event_rows('2026-08-03',g)
    changed=g.copy();changed.loc[changed.index[200]:,'high']+=1000
    b,_=m.event_rows('2026-08-03',changed)
    prefix=lambda rows:{(r['event'],r['bar_utc'],r['event_known_utc']) for r in rows if pd.Timestamp(r['bar_utc'])<g.index[200]}
    assert prefix(a)==prefix(b)


def test_measured_halves_and_events_reconcile_independently_from_private_rows():
    path=ROOT/'public/data/research-raw-market.json'
    if not path.exists():pytest.skip('Only after raw measurement, no scoring')
    d=json.loads(path.read_text());out=ROOT/'artifacts/raw-market'
    if not out.exists():pytest.skip('Private detailed observations unavailable')
    slots=pd.read_csv(out/'half-hours.csv');events=pd.read_csv(out/'events.csv')
    assert slots.groupby('day').volume_share.sum().to_numpy()==pytest.approx(np.ones(slots.day.nunique()))
    assert slots.day.nunique()==d['complete_RTH_and_boundary_days']
    assert len(d['half_hours'])==13 and len(d['correlations'])==6 and len(d['events'])==12
    for row in d['half_hours']:
        g=slots[slots.slot.eq(row['slot'])]
        assert row['return_bps']['mean']==pytest.approx(g.return_bps.mean())
        assert row['range_points']['median']==pytest.approx(g.range_points.median())
    for row in d['events']:
        g=events[events.event.eq(row['event'])&events.horizon.eq(row['horizon'])]
        assert row['event_weighted_bps']['mean']==pytest.approx(g.return_bps.mean())
        assert row['equal_event_day_mean_bps']['mean']==pytest.approx(g.groupby('day').return_bps.mean().mean())
    assert len(d['tests'])==43 and not d['strategy_signals_computed'] and not d['entries_stops_targets_used']
    adjusted=m.holm([r['p_value'] for r in d['tests']])
    np.testing.assert_allclose(adjusted,[r['p_holm_global43'] for r in d['tests']])


def test_published_archive_audit_and_market_hashes():
    path=ROOT/'research/market-review-verification.json'
    if not path.exists():pytest.skip('After publication')
    from scripts.oos_preparation.adapter import sha
    manifest=json.loads(path.read_text())
    for name,digest in manifest['files_sha256'].items():assert sha(ROOT/name)==digest
    assert sha(ROOT/'scripts/raw_market.py')==manifest['calculation_code_sha256']
    assert sha(ROOT/'research/raw-market-protocol.json')==manifest['definitions_sha256']
