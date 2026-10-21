import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scripts.reproduce_research.volume_stability import simple_metrics,sensitivities,roll_windows,attribution
from scripts.reproduce_research.holdout_data import sha

ROOT=Path(__file__).resolve().parents[1]


def trades(values):
    dates=pd.bdate_range('2025-01-06',periods=len(values)).strftime('%Y-%m-%d')
    return pd.DataFrame({'trade_date':dates,'entry_utc':[d+'T15:00:00Z' for d in dates],'net_points':values})


def test_metrics_drawdown_starts_at_zero_and_zero_trade_days_retained():
    t=trades([-5,2,-3]);m=simple_metrics(t,list(range(5)))
    assert m['realized_max_drawdown_points']==6
    assert m['mean_eligible_day_points']==-6/5 and m['eligible_days']==5
    assert m['profit_factor']==2/8
    empty=simple_metrics(t.iloc[:0],list(range(5)))
    assert empty['net_points']==0 and empty['profit_factor'] is None and empty['trades']==0


def test_fixed_cost_and_best_three_sensitivities():
    t=trades([10,-3,4,2]);s=sensitivities(t,t.trade_date.tolist())
    assert s['best3_net_points']==16
    assert s['best3_share_net_profit_pct']==pytest.approx(1600/13)
    assert s['without_best3']['net_points']==-3
    assert [x['net_points'] for x in s['cost_scenarios']]==[13,9,5]
    assert s['without_best3']['eligible_days']==4
    assert sensitivities(trades([-1,-2,-3,-4]),list(range(4)))['best3_share_net_profit_pct'] is None


def test_roll_window_is_first20_observed_sessions_not_price_outcome():
    dates=pd.bdate_range('2025-06-17',periods=25).strftime('%Y-%m-%d').tolist()
    window,rows=roll_windows(dates,['2025-06-17',dates[-2]])
    assert rows[0]['observed_sessions']==20 and rows[0]['end']==dates[19]
    assert rows[1]['observed_sessions']==2
    assert dates[20] not in window and dates[24] in window


def row(day,direction=1,hour='14:00',net=1.):
    return {'strategy':'S','trade_date':day,'signal_utc':day+'T13:59Z','entry_utc':day+'T'+hour+'Z',
            'exit_bar_utc':day+'T16:00Z','entry_price':100.,'exit_price':101.,'direction':direction,
            'stop':99.,'target':102.,'exit_reason':'noon','net_points':net}


def test_attribution_partitions_dates_and_reconciles_signed_delta():
    dates=pd.bdate_range('2025-01-06',periods=8).strftime('%Y-%m-%d').tolist()
    old=pd.DataFrame([row(dates[i],net=float(i+1)) for i in [0,1,2,3,4]])
    new=pd.DataFrame([row(dates[0],net=1),row(dates[1],hour='14:30',net=9),
                      row(dates[2],direction=-1,net=-2),row(dates[4],net=8),
                      row(dates[5],net=4),row(dates[7],net=2)])
    detail,categories=attribution(old,new,set(dates[:7]),dates,'S')
    expected={'unchanged','entry_time_changed','direction_changed','removed_common',
              'same_entry_changed_outcome','added_common','no_trade_both','extra_dates_outside_common148'}
    assert set(detail.category)==expected and len(detail)==8
    assert sum(x['old_trades'] for x in categories)==len(old)
    assert sum(x['new_trades'] for x in categories)==len(new)
    assert sum(x['delta_points'] for x in categories)==new.net_points.sum()-old.net_points.sum()


def test_duplicate_trade_dates_fail_attribution():
    a=pd.DataFrame([row('2025-01-06'),row('2025-01-06')])
    with pytest.raises(ValueError,match='One trade'):
        attribution(a,a,{'2025-01-06'},['2025-01-06'],'S')


def data():return json.loads((ROOT/'public/data/research-volume-stability.json').read_text())


def test_published_stability_preserves_prior_exports_and_research_code():
    d=data()
    for name,digest in d['protocol']['frozen_sha256'].items():assert sha(ROOT/name)==digest
    for name,digest in d['code_sha256'].items():assert sha(ROOT/'scripts/reproduce_research'/name)==digest
    assert sha(ROOT/'research/volume-stability-protocol.json')==d['protocol_sha256']
    assert (ROOT/'docs/VOLUME_STABILITY_AUDIT.md').read_bytes()==(ROOT/'public/data/research-volume-stability.md').read_bytes()


def test_global_family_periods_and_reconciliation():
    d=data();assert d['global_test_family_size']==len(d['tests'])==16
    assert all(t['p_holm_global']>=t['p_value'] for t in d['tests'])
    assert all(t['p_holm_global']>=.05 for t in d['tests'])
    for s,v in d['strategies'].items():
        p=v['periods'];full=p['full']['metrics']
        assert full['eligible_days']==159
        assert p['discovery']['metrics']['eligible_days']+p['observed_apr_sep']['metrics']['eligible_days']==159
        assert full['trades']==sum(p[x]['metrics']['trades'] for x in ['discovery','observed_apr_sep'])
        assert abs(full['net_points']-sum(p[x]['metrics']['net_points'] for x in ['discovery','observed_apr_sep']))<1e-8
        assert sum(x['days'] for x in v['attribution'])==159
        month=[x for x in v['slices'] if x['dimension']=='month']
        assert abs(sum(x['net_points'] for x in month)-full['net_points'])<1e-8
        assert abs(sum(x['new_net_points'] for x in v['attribution'])-full['net_points'])<1e-8


def test_orb15_key_diagnostics_and_mean_reversion_zero_delta():
    d=data();v=d['strategies']['B_ORB15'];p=v['periods']
    assert p['observed_apr_sep']['metrics']['net_points']==pytest.approx(-272.55)
    assert p['full']['sensitivity']['best3_share_net_profit_pct']==pytest.approx(80.41206192464757)
    assert v['changed_common_days']==14 and v['changed_common_days_outside_roll_window']==0
    assert d['tests'][v['paired_test_index']]['estimate_mean_daily_points']*148==pytest.approx(460.7)
    for s in ['A_London_sweep','C_VWAP_extreme']:
        t=d['tests'][d['strategies'][s]['paired_test_index']]
        assert t['estimate_mean_daily_points']==0 and t['p_holm_global']==1
    text=json.dumps(d)
    assert all(k not in text for k in ['old_entry_utc','new_entry_utc','entry_price','exit_price'])
