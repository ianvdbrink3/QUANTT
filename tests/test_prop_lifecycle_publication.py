import gzip
import hashlib
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public/data/prop-lifecycle/summary.json'


@pytest.mark.skipif(not PUBLIC.exists(),reason='Requires local lifecycle research replay')
def test_aggregates_only_and_equal_followup_cash_accounting():
    x=json.loads(PUBLIC.read_text())
    forbidden={'records','negative_record_lows','entry_price','entry_time','source_rows','accounts'}
    def inspect(obj):
        if isinstance(obj,dict):
            assert not (set(obj)&forbidden)
            assert not isinstance(obj.get('payouts'), (list, dict))  # method prose is safe
            for v in obj.values(): inspect(v)
        elif isinstance(obj,list):
            for v in obj: inspect(v)
    inspect(x)
    assert len(x['rows'])==144
    for row in x['rows']:
        if row['horizon']=='252_SESSIONS':
            assert row['starts']=={'2019_2021':498,'2024_2026':171,'COMBINED':669}[row['era']]
        assert row['evaluation_pass_rate']>=row['payout1_all_starts']>=row['payout2_all_starts']
        assert row['failures']+row['unknown_rate']+row['censored']+row['payout2_all_starts']==pytest.approx(1.)
        if row['unknown_rate']:
            assert row['mean_net_cash_per_start_USD'] is None
        assert row['partial_identification_cash_bounds_USD'][0]<=row['partial_identification_cash_bounds_USD'][1]


@pytest.mark.skipif(not PUBLIC.exists(),reason='Requires local lifecycle research replay')
def test_private_replay_bytes_and_no_retained_equity_as_income():
    a=ROOT/'artifacts/prop-lifecycle/run1'
    b=ROOT/'artifacts/prop-lifecycle/run2'
    for name in ('accounts.json.gz','accounts.csv','summary.json','summary.csv'):
        assert hashlib.sha256((a/name).read_bytes()).digest()==hashlib.sha256((b/name).read_bytes()).digest()
    accounts=json.loads(gzip.decompress((a/'accounts.json.gz').read_bytes()))
    assert len(accounts)==44160
    for account in accounts:
        assert account['cash_net_accrued_USD']==pytest.approx(account['received_USD']-account['fees_USD'])
        assert account['credited_payouts']<=2
        if account['source_unknown']:
            assert account['net_cash_through_horizon_USD'] is None
