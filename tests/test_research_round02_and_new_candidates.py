import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scripts import afternoon_inference_round as old
from scripts.afternoon_inference_round2 import adjusted_test,verify as verify_round2
from scripts.new_candidates_round01 import cash_calendar,tom_dates,morning_direction,trade,metrics,verify
from scripts.historical_batch01_quality import expected_rth,HistoricalCalendar,SPECIAL
from scripts.oos_preparation.adapter import at

ROOT=Path(__file__).resolve().parents[1]


def test_conservative_test_preserves_estimand_mask_and_increases_p():
    rng=np.random.default_rng(9)
    panel,mask=old.generate(rng,'AR095',30,783,.36,[14.,36.],.59)
    a,b=old.group_test(panel,mask),adjusted_test(panel,mask)
    np.testing.assert_equal(a['valid'],b['valid'])
    np.testing.assert_allclose(a['mean'],b['mean'])
    assert (b['p']>=a['p']).all()


def test_insufficient_information_never_significant():
    selected=np.zeros((3,783),bool);selected[:,:20]=True
    values=np.ones((3,783,2))*selected[:,:,None]
    result=adjusted_test(values,selected)
    assert not result['valid'].any()
    assert (result['p']==1).all()


def test_round2_prelock_and_fresh_seeds():
    verify_round2()
    a=json.loads((ROOT/'research/afternoon-method-round-protocol.json').read_text())
    b=json.loads((ROOT/'research/afternoon-method-round2-protocol.json').read_text())
    assert not set(a['seeds']) & set(b['seeds'])
    assert b['bound_family']==396
    assert b['nominal_alpha']==.05
    assert b['variance_multiplier']==1.25


def test_cash_calendar_not_cme_partial_sessions():
    dates=cash_calendar()
    assert '2025-01-09' not in dates
    assert '2025-04-18' not in dates
    assert '2026-04-03' not in dates
    assert '2025-11-28' in dates  # Early close counts as a calendar session.
    assert '2025-12-24' in dates


def test_month_boundary_exante_not_ranked_by_quality_filter():
    chosen=tom_dates()
    assert {'2025-01-02','2025-01-03','2025-01-06','2025-01-31'}<=chosen
    assert '2025-01-07' not in chosen
    assert '2025-11-28' in chosen
    # Do not shift the last-day event to Nov26 when the short Nov28 is excluded.
    assert '2025-11-26' not in chosen


@pytest.mark.parametrize('move,expected',[(-2,-1),(0,0),(2,1)])
def test_direction_is_overnight_inclusive_and_causal(move,expected):
    prefix=np.ones(30)*100;prefix[-1]+=move
    assert morning_direction(prefix,100)==expected
    assert morning_direction(prefix,np.nan)==0
    future=np.r_[prefix,np.arange(360)+9000]
    a=morning_direction(future[:30],100)
    future[30:]*=-100
    assert morning_direction(future[:30],100)==a
    assert morning_direction(future[:30],100)==morning_direction(prefix,100)
    with pytest.raises(ValueError):morning_direction(future,100)


def test_entry_and_exit_bar_anchors_and_direction():
    prices={k:np.ones(390)*100 for k in ('open','high','low','close')}
    prices['open'][360]=102;prices['close'][389]=107
    prices['high'][360:390]=110;prices['low'][360:390]=99
    long=trade('2025-01-02',prices,360,390,1)
    short=trade('2025-01-02',prices,360,390,-1)
    assert long['gross_points']==5 and short['gross_points']==-5
    assert long['net_points']==5-1.225
    assert long['mfe_points']==8 and long['mae_points']==3
    assert short['mfe_points']==3 and short['mae_points']==8
    assert long['entry_minute']==360 and long['exit_minute']==389


def test_zero_initial_equity_drawdown_and_costs():
    rows=[]
    for x in [-10,20,-30]:
        rows.append(dict(net_points=x,gross_points=x+1.225,mfe_points=5,mae_points=4))
    result=metrics(pd.DataFrame(rows))
    assert result['net_points']==-20
    assert result['max_closed_equity_drawdown']==30
    assert result['cost_sensitivity'][1]['net_points']==-21.5
    assert result['cost_sensitivity'][2]['net_dollars']==-460


def test_historical_mourning_and_expiry_not_missing_rth():
    assert len(expected_rth('2018-12-05','NQZ18'))==0
    assert len(expected_rth('2018-12-21','NQZ18'))==0
    assert len(expected_rth('2018-12-21','NQH19'))==390
    assert len(expected_rth('2018-12-24','NQH19'))==225
    assert len(expected_rth('2018-12-25','NQH19'))==0


def test_historical_pause_is_outside_rth():
    calendar=HistoricalCalendar(dict(reviewed_ranges=[['2018-11-19','2019-01-14']],closes_ny=SPECIAL))
    ix=calendar.grid('2018-12-14')
    assert len(ix)==1365
    assert at('2018-12-14','16:15') not in ix
    assert at('2018-12-14','16:30') in ix
    assert len(expected_rth('2018-12-14','NQH19').difference(ix))==0


def test_timezone_dst_transition_synthetic_not_observed_certification():
    assert at('2019-03-08','09:30').hour==14
    assert at('2019-03-11','09:30').hour==13
    assert at('2019-11-01','09:30').hour==13
    assert at('2019-11-04','09:30').hour==14


def test_new_candidate_inputs_still_locked_and_not_historical():
    verify()
    p=json.loads((ROOT/'research/new-candidates-round01-protocol.json').read_text())
    assert len(p['candidates'])==2
    assert p['period']==['2024-12-30','2026-09-30']


def test_results_trade_counts_costs_and_private_hashes():
    result=json.loads((ROOT/'research/new-candidates-round01-results.json').read_text())
    assert not result['new_historical_sample_read']
    assert result['fixed_complete_days']==435
    for name,r in result['results'].items():
        ledger=pd.read_csv(ROOT/'artifacts/new-candidates-round01'/f'{name.lower()}-trades.csv')
        m=r['metrics']
        assert m['trades']==len(ledger)
        np.testing.assert_allclose(ledger.gross_points-ledger.net_points,1.225)
        np.testing.assert_allclose(ledger.net_points.sum(),m['net_points'])
        assert ledger.day.between('2024-12-30','2026-09-30').all()
        assert r['uncertainty']['confirmatory_p'] is None


def test_round2_finite_screen_not_universal_claim():
    r=json.loads((ROOT/'research/afternoon-method-round2-results.json').read_text())
    assert r['raw_market_files_read']==0 and not r['independent_test_released']
    assert r['tested_bounds']==396
    assert len(r['negative_control'])==6
    assert not r['candidate_v2_changed']


def test_historical_quality_sources_preserved_and_continuous_not_cohort():
    q=json.loads((ROOT/'research/historical-batch01-quality.json').read_text())
    assert q['source_bars']==64622
    assert not q['signal_or_horizon_returns_computed']
    assert not q['new_historical_outcomes_released']
    assert q['rollover']['future_cutoff_verified']
    assert q['continuous_atr_readiness']['january_atr14_ready_full_rth_days']==8
    for r in q['files']:assert old.sha(ROOT/'data/raw/historical-replication-2019-2021'/r['filename'])==r['sha256']
