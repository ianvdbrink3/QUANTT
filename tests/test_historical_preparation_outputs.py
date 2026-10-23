import json
from scripts import prepare_historical_contracts as h


def data():return json.loads(h.RESULT.read_text())
def review():return json.loads((h.ROOT/'research/historical-preparation-review.json').read_text())


def test_complete_numeric_receipt():
    r=data()
    assert r['source_files']==105 and r['plan_blocks']==103 and r['contracts']==14
    assert r['source_bars']==1286673
    assert r['unique_contract_bars']+r['duplicate_rows_removed']==r['source_bars']
    assert r['conflicting_keys']==0 and not any(r['numeric_errors'].values())


def test_technical_days_not_trades():
    r=data()['groups']
    assert r['FULL_2019_2021']['cash_sessions']==757
    assert r['REGISTERED_REMAINDER']['cash_sessions']==749
    assert r['REGISTERED_REMAINDER']['technical_by_model']==dict(TOM_RTH=733,COMPRESSED_BREAK5=706,SWEEP_REV_1200=619)
    assert r['FULL_2019_2021']['clean_full_RTH']==741


def test_new_outcomes_remain_locked():
    assert data()['signals_computed'] is False and data()['holdout_executed'] is False
    assert review()['signals_on_registered_remainder'] is False
    assert review()['holdout_executed'] is False


def test_roll_prefix_evidence():
    r=data()['rollovers']
    assert len(r)==13 and all(z['future_cutoff_verified'] for z in r)
    assert r[0]['effective_session']=='2018-12-17'
    assert sum(z['complete_observed_minute_coverage'] for z in r)==3
    assert all(z['spread_available_utc']<z['effective_utc'] for z in r)
    assert len(review()['actual_roll_open_prefix_tests'])==13
    assert all(x['passed'] and x['prior_ATR14_ready'] for x in review()['actual_roll_open_prefix_tests'])


def test_real_DST_boundaries_present():
    t=data()['DST_transitions']
    assert len(t)==6 and all(s['open_bar_present'] for r in t for s in r['sessions'])


def test_no_private_prices_published():
    assert h.RESULT.read_bytes()==h.PUBLIC.read_bytes()
    for path in (h.PUBLIC,h.ROOT/'public/data/historical-preparation-review.json'):
        text=path.read_text()
        assert 'entry_price' not in text and '/Users/' not in text and '"open":' not in text
    assert h.ignored(h.OUT/'contract-bars.parquet') and h.ignored(h.OUT/'active-bars.parquet')


def test_original_file_integrity_and_replay():
    assert h.verify()['protected_files']==550
    r=json.loads((h.ROOT/'research/historical-preparation-verification.json').read_text())
    assert r['status']=='BYTE_IDENTICAL_QUALITY_ONLY_REPLAY'
    # Review appends an additional PRIVATE audit, without altering the9 replayed outputs.
    for name,digest in r['files_sha256'].items():assert h.sha(h.ROOT/name)==digest


def test_old_consumed_discovery_only_parity():
    r=review()['old_discovery_parity']
    assert r['days']==435 and not r['new_2019_2021_signals_computed']
    assert r['trade_counts']==dict(TOM_RTH=81,COMPRESSED_BREAK5=109,SWEEP_REV_1200=63)


def test_boundary_missing_is_not_hidden():
    x=next(r for r in review()['active_anomalies'] if r['day']=='2020-03-13')
    assert x['missing_RTH']==[] and x['boundary_0929_missing']
    assert x['classification']=='MISSING_0929_BOUNDARY_ONLY'
