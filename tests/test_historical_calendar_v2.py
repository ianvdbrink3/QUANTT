"""Calendar/context-only tests. No strategy outcomes on the new window."""
import ast
import inspect
import json

import numpy as np
import pandas as pd
import pytest

from scripts import historical_calendar_v2 as v
from scripts import prepare_historical_contracts as h


@pytest.mark.parametrize('day,stem,ct,grade',v.TABLES)
def test_every_transcribed_exception_uses_its_own_dated_equity_source(day,stem,ct,grade):
    cat=json.loads(v.CATALOG.read_text())
    row=next(r for r in cat['exceptions'] if r['day']==day)
    assert row['date_scope']==day and row['product']=='Equity'
    assert row['close_ct']==ct
    assert row['close_ny']==v.CalendarV2().registry['closes_ny'][day]
    assert row['grade'] in {'DIRECT_CME_XLS_VERIFIED','CME_LABELED_PRESERVED','CROPPED_ATTRIBUTED'}
    if grade=='CROPPED_ATTRIBUTED':
        assert row['grade']=='CROPPED_ATTRIBUTED' and not row['year_visible_in_table']
    assert len(row['source_sha256'])==64
    assert h.sha(v.ROOT/row['private_source'])==row['source_sha256']


def test_only_source_proven_good_friday_grid_changes():
    old=h.HistoricalCalendar();new=v.CalendarV2();changed=[]
    for day in pd.bdate_range('2018-11-19','2021-12-31').strftime('%Y-%m-%d'):
        if not old.grid(day).equals(new.grid(day)):changed.append(day)
    assert changed==['2021-04-02']
    assert len(old.grid('2021-04-02'))==0
    assert len(new.grid('2021-04-02'))==915
    assert new.grid('2021-04-02')[-1]==h.at('2021-04-02','09:14')
    assert h.at('2021-04-02','09:15') not in new.grid('2021-04-02')


@pytest.mark.parametrize('day,minutes',[
    ('2019-04-19',0),('2020-04-10',0),('2021-04-02',915),
    ('2019-11-28',1140),('2019-11-29',1155),
    ('2021-06-25',1365),('2021-06-28',1380),('2021-12-31',1380),
    ('2021-12-24',0),('2018-12-05',930),('2021-07-04',0),
])
def test_closed_halted_early_close_and_pause_are_distinct(day,minutes):
    assert len(v.CalendarV2().grid(day))==minutes


@pytest.mark.parametrize('day,utc_hour',[
    ('2019-03-08',14),('2019-03-11',13),('2019-11-01',13),('2019-11-04',14),
    ('2020-03-06',14),('2020-03-09',13),('2020-10-30',13),('2020-11-02',14),
    ('2021-03-12',14),('2021-03-15',13),('2021-11-05',13),('2021-11-08',14),
])
def test_real_iana_dst_conversion(day,utc_hour):
    t=h.at(day,'09:30')
    assert t.hour==utc_hour and t.minute==30
    assert t.tz_convert('America/Chicago').strftime('%H:%M')=='08:30'


def synthetic_history():
    calendar=v.CalendarV2();parts=[];dates=[]
    for i,day in enumerate(pd.bdate_range('2021-03-01','2021-04-30').strftime('%Y-%m-%d')):
        ix=calendar.grid(day)
        if not len(ix):continue
        dates.append(day)
        parts.append(pd.DataFrame(dict(open=1000.+i,high=1002.+i*2,low=999.-i,
            close=1000.+i,volume=10.,usable=True,trade_date=day),index=ix))
    return pd.concat(parts),dates,calendar


def test_short_session_resets_pd_and_preserves_frozen_true_range_policy():
    bars,days,c=synthetic_history()
    new=h.contexts(bars,days,c,[])
    old=h.contexts(bars,[d for d in days if d!='2021-04-02'],h.HistoricalCalendar(),[])
    assert np.isfinite(new['2021-04-01'][1]['atr'])
    assert np.isnan(new['2021-04-05'][1]['PDH'])
    assert np.isfinite(old['2021-04-05'][1]['PDH'])
    assert new['2021-04-05'][1]['atr']==old['2021-04-05'][1]['atr']
    # No range-only fallback: the first complete day after a partial session
    # does not append a TR. The following morning ATR is unchanged.
    assert new['2021-04-06'][1]['atr']==new['2021-04-05'][1]['atr']
    assert np.isfinite(new['2021-04-06'][1]['PDH'])


def test_future_cutoff_and_poisoned_future_cannot_change_prior_context():
    bars,days,c=synthetic_history();state=h.contexts(bars,days,c,[])
    cutoff=h.at('2021-04-05','09:30')
    altered=bars.copy()
    altered.loc[altered.index>=cutoff,['open','high','low','close','volume']]=999999.
    other=h.contexts(altered,days,c,[])
    for key in (*v.KEYS.values(),'prior_close'):
        np.testing.assert_equal(state['2021-04-05'][1][key],other['2021-04-05'][1][key])
    check=v.cutoff_checks(bars,days,state,c,[],['2021-04-05'])
    assert check[0]['context_identical']


def test_hash_mismatch_is_a_hard_error(tmp_path):
    p=tmp_path/'source.txt';p.write_text('not the locked original')
    with pytest.raises(ValueError,match='Changed protected/source bytes'):
        v.check_hashes({str(p):'0'*64})


def test_method_and_publication_scope_cannot_open_outcomes():
    assert not v.METHOD['outcome_release'] and not v.METHOD['missing_minutes_are_zero']
    assert v.METHOD['publication']=='LOCAL_ONLY_NO_PUSH_NO_DEPLOY'
    assert set(v.METHOD['changes'])=={'2021-04-02'}
    tree=ast.parse(inspect.getsource(v))
    calls={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
    calls|={n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
    assert not calls & {'select','fill','simulate','score','backtest','select_events','outcome','old_discovery_parity'}
    assert v.RESULT!=h.RESULT and v.REPORT!=h.REPORT and v.PUBLIC!=h.PUBLIC


def test_original_state_including_untracked_audit_is_still_identical():
    r=v.verify()
    assert r['protected_files']==585 and r['private_inputs']==13
    assert r['prior_freeze']['protected_files']==550
    locked=json.loads(v.LOCK.read_text())['protected_files']
    assert 'scripts/audit_historical_evidence.py' in locked
    assert 'docs/HISTORICAL_VOLUME_CALENDAR_EVIDENCE.md' in locked


def test_real_output_counts_context_and_release_status():
    if not v.RESULT.exists():pytest.skip('Calendar v2 not built yet')
    r=json.loads(v.RESULT.read_text())
    assert r['calendar_cases']==38 and len(r['remaining_provisional_dates'])==9
    assert r['source_files_verified']==105 and r['active_bars_unchanged']
    assert len(r['context_changed'])==15
    assert r['groups_after']['FULL_2019_2021']['technical_by_model']==dict(TOM_RTH=741,COMPRESSED_BREAK5=713,SWEEP_REV_1200=627)
    assert r['groups_after']['REGISTERED_REMAINDER']['technical_by_model']==dict(TOM_RTH=733,COMPRESSED_BREAK5=705,SWEEP_REV_1200=619)
    assert not r['release_approved'] and not r['signals_computed'] and not r['holdout_executed']
    assert r['rollovers_unchanged']==13
    dates={x['day'] for x in r['cutoff_checks']}
    for day in ('2020-03-09','2020-03-12','2020-03-16','2020-03-18','2021-04-05','2021-04-23','2021-12-13'):
        assert day in dates


def test_public_export_contains_no_price_or_trade_arrays():
    if not v.PUBLIC.exists():pytest.skip('Calendar v2 not built yet')
    banned={'open','high','low','close','volume','prices','trades','net_points','atr14_prior','PDH','PDL','ONH','ONL'}
    def walk(x):
        if isinstance(x,dict):
            assert not (banned & x.keys())
            for value in x.values():walk(value)
        if isinstance(x,list):
            for value in x:walk(value)
    walk(json.loads(v.PUBLIC.read_text()))


def test_reproduction_record_covers_all_output_bytes():
    if not v.VERIFICATION.exists():pytest.skip('Two-run check not built yet')
    r=json.loads(v.VERIFICATION.read_text())
    assert r['status']=='BYTE_IDENTICAL_CALENDAR_V2_REPLAY'
    assert len(r['files_sha256'])==8
    v.check_hashes(r['files_sha256'])
