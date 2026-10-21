"""Synthetic preparation tests: no holdout strategy evaluation."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.oos_preparation.adapter import Calendar,at,session_dates,combine,determine_roll,sha
from scripts.oos_preparation.route import (indicator_state,technical_eligibility,
    historical_features,replay_historical,STRATEGIES)
from scripts.oos_preparation.year import forbid_scoring,load_registered
from scripts.reproduce_research import engine
from scripts.reproduce_research.next_engine import Activation
from scripts.verify_research_freeze import verify

ROOT=Path(__file__).resolve().parents[1]


def calendar():
    return Calendar(json.loads((ROOT/'research/oos-year-calendar.json').read_text()))


def bars(day,contract='NQU26',price=100.,volume=100):
    ix=calendar().grid(day)
    return pd.DataFrame(dict(contract=contract,trade_date=day,open=price,high=price+1,
        low=price-1,close=price,volume=volume),index=ix)


@pytest.mark.parametrize('day,count',[('2025-12-24',1155),('2025-12-25',0),
    ('2026-01-01',0),('2026-01-19',1140),('2026-02-16',1140),
    ('2026-04-03',915),('2026-05-25',1140),('2026-06-19',1140),
    ('2026-07-03',1140),('2026-09-07',1140)])
def test_year_product_calendar(day,count):
    assert len(calendar().grid(day))==count


@pytest.mark.parametrize('before,after,hours',[('2025-10-31','2025-11-03',(13,14)),
    ('2026-03-06','2026-03-09',(14,13))])
def test_both_dst_changes(before,after,hours):
    assert (at(before,'09:30').hour,at(after,'09:30').hour)==hours
    assert len(calendar().grid(before))==len(calendar().grid(after))==1380
    for d in [before,after]:assert set(session_dates(calendar().grid(d)))=={d}


def test_unknown_future_calendar_refused():
    with pytest.raises(ValueError,match='CALENDAR_UNVERIFIED'):calendar().grid('2026-10-01')


@pytest.mark.parametrize('hm,eligible',[('02:00',False),('09:45',False),('12:37',True)])
def test_exact_prefix_not_relaxed_for_missing_bars(hm,eligible):
    day='2026-08-03';f=bars(day).assign(atr14_prior=2.,prior_same_minute_median_volume=100.)
    f=f.drop(at(day,hm));e=technical_eligibility(f,calendar(),day,day)
    assert e.eligible.tolist()==[eligible]*4


def test_volume_readiness_affects_only_orb():
    day='2026-08-03';f=bars(day).assign(atr14_prior=2.,prior_same_minute_median_volume=np.nan)
    e=technical_eligibility(f,calendar(),day,day).set_index('strategy')
    assert e.eligible.to_dict()==dict(A_London_sweep=True,B_ORB5=False,B_ORB15=False,C_VWAP_extreme=True)


def test_outage_attribution_never_supplies_prefix():
    day='2025-11-28';f=bars(day).assign(atr14_prior=2.,prior_same_minute_median_volume=100.)
    f=f.loc[calendar().grid(day,remove_observed_outage=True)]
    assert not technical_eligibility(f,calendar(),day,day).eligible.any()


@pytest.mark.parametrize('function',[historical_features,replay_historical])
def test_future_scoring_rejected_before_any_feature_call(function,monkeypatch):
    monkeypatch.setattr(engine,'build_features',lambda *_:pytest.fail('Feature call on future data'))
    monkeypatch.setattr(engine,'hypotheses',lambda *_:pytest.fail('Signal call on future data'))
    with pytest.raises(PermissionError,match='HOLDOUT_LOCKED'):
        function(bars('2026-08-03'),[Activation('NQU26','2026-08-03')],calendar())


def test_runtime_scoring_tripwire_restores_originals():
    old=engine.hypotheses
    with forbid_scoring():
        with pytest.raises(PermissionError,match='HOLDOUT_LOCKED'):engine.hypotheses(None)
    assert engine.hypotheses is old


def synthetic_roll():
    days=pd.bdate_range('2026-08-03',periods=20).strftime('%Y-%m-%d')
    full=pd.concat([bars(d,'OLD') for d in days[:-1]]+
        [bars(days[-2],'NEW',150),bars(days[-1],'NEW',150)]).sort_index()
    schedule=[Activation('OLD',days[0]),Activation('NEW',days[-1])]
    return full,schedule,days[-1]


def test_atr_volume_both_ready_on_roll_day_without_signal_calls():
    full,schedule,day=synthetic_roll()
    with forbid_scoring():
        state,_,_=indicator_state(full,schedule)
        e=technical_eligibility(state,calendar(),day,day)
    assert e.eligible.all()
    assert state[state.trade_date.eq(day)].atr14_prior.eq(2).all()
    assert state[state.trade_date.eq(day)].prior_same_minute_median_volume.eq(100).all()
    assert state[state.trade_date.eq(day)].open.eq(150).all()
    assert not any(c.startswith('vwap') for c in state.columns)


def test_future_mutation_cannot_change_current_prerequisites():
    full,schedule,day=synthetic_roll();before,_,_=indicator_state(full,schedule)
    changed=full.copy();changed.loc[changed.trade_date.ge(day),['open','high','low','close','volume']]*=10
    after,_,_=indicator_state(changed,schedule)
    pd.testing.assert_frame_equal(before[['atr14_prior','prior_same_minute_median_volume']],
                                  after[['atr14_prior','prior_same_minute_median_volume']])


def test_real_frozen_73_files_unchanged():
    assert verify()['files']==73


def test_changed_source_fails_before_indicators(tmp_path):
    (tmp_path/'research').mkdir()
    (tmp_path/'data/raw/oos').mkdir(parents=True)
    p=tmp_path/'data/raw/oos/changed.csv';p.write_text('changed source')
    (tmp_path/'research/oos-year-sources.json').write_text(json.dumps(dict(warmup_sources=[],
        sources=[dict(filename='changed.csv',relative_private_path='data/raw/oos/changed.csv',
            contract='NQU26',sha256='0'*64)])))
    with pytest.raises(ValueError,match='Source hash mismatch'):load_registered(tmp_path)


def test_missing_source_has_no_downloads_fallback(tmp_path):
    (tmp_path/'research').mkdir()
    (tmp_path/'research/oos-year-sources.json').write_text(json.dumps(dict(warmup_sources=[],
        sources=[dict(filename='missing.csv',relative_private_path='data/raw/oos/missing.csv',
            contract='NQU26',sha256='0'*64)])))
    with pytest.raises(FileNotFoundError):load_registered(tmp_path)


def test_preparation_publication_contains_no_future_outcomes():
    p=ROOT/'public/data/research-oos-year-readiness.json'
    if not p.exists():pytest.skip('Generated after private-source run')
    d=json.loads(p.read_text())
    assert not d['signals_computed'] and not d['future_PnL_computed'] and not d['scoring_authorized']
    assert set(d['technical_eligible_days'])==set(STRATEGIES)
    assert len(d['rollovers'])==4 and all(r['future_truncation_verified'] for r in d['rollovers'])
    assert not d['missing_full_sessions']


def test_historical_replay_evidence_is_exact_and_bounded():
    p=ROOT/'research/oos-year-historical-parity.json'
    if not p.exists():pytest.skip('Requires explicit private historical regression command')
    d=json.loads(p.read_text())
    assert d['future_source_files_opened']==0 and not d['future_signals_computed']
    assert d['period']==['2024-12-30','2025-09-30']
    assert all(x['byte_identical'] for x in d['historical_results'].values())
    assert set(d['technical_eligible_days'].values())=={159}
    assert all(sha(ROOT/name)==digest for name,digest in d['implementation_sha256'].items())
