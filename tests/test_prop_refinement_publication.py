import gzip
import hashlib
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public/data/prop-refinement/summary.json'


@pytest.mark.skipif(not PUBLIC.exists(),reason='Needs the local refinement replay')
def test_full_scenario_matrix_and_observed_paths_are_not_presented_as_missing():
    x=json.loads(PUBLIC.read_text());rows=x['rows']
    assert len(rows)==516
    old=json.loads((ROOT/'public/data/prop-lifecycle/summary.json').read_text())['rows']
    for r in rows:
        assert r['evaluation_pass_rate']>=r['payout1_all_starts']>=r['payout2_all_starts']
        assert r['failures']+r['censored']+r['unknown_rate']+r['payout2_all_starts']==pytest.approx(1.)
        if r['horizon']=='252_SESSIONS':
            assert r['starts']=={'2019_2021':498,'2024_2026':171,'COMBINED':669}[r['era']]
        if r['profile']=='FROZEN_STRICT':
            reference=next(a for a in old if all(a[k]==r[k] for k in ('era','firm','model','horizon')) and a['MNQ']==r['overnight_MNQ'])
            for key in ('evaluation_pass_rate','payout1_all_starts','payout2_all_starts','unknown_rate','mean_net_cash_per_start_USD'):
                assert r[key]==reference[key]
        else:
            assert r['unknown_rate']==0 and isinstance(r['mean_net_cash_per_start_USD'],float)
        if 'KEEPALIVE' not in r['profile']:
            assert r['mean_keep_alive_roundtrips']==0
    assert 'CONDITIONAL' in x['method']['status']
    assert 'NOTverified' in x['method']['maintenance']


@pytest.mark.skipif(not PUBLIC.exists(),reason='Needs the local refinement replay')
def test_frozen_bytes_private_replay_parity_and_public_payload_excludes_raw_records():
    lock=json.loads((ROOT/'research/prop-refinement-registration.json').read_text())
    for name,digest in lock['protected'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    for name in ('accounts.json.gz','summary.json','summary.csv'):
        assert (ROOT/'artifacts/prop-refinement/run1'/name).read_bytes()==(ROOT/'artifacts/prop-refinement/run2'/name).read_bytes()
    x=json.loads(PUBLIC.read_text())
    def walk(x):
        if isinstance(x,dict):
            assert not set(x)&{'entry_price','entry_time','records','negative_record_lows','accounts'}
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(x)
    path=ROOT/'artifacts/prop-refinement/run1/accounts.json.gz'
    accounts=json.loads(gzip.decompress(path.read_bytes()))
    assert len(accounts)==158240
    for a in accounts:
        assert a['cash_net_accrued_USD']==pytest.approx(a['received_USD']-a['fees_USD'])
        if 'KEEPALIVE' in a['profile']:
            cost=6.50 if 'KA650' in a['profile'] else 3.22
            assert a['keep_alive_cost_USD']==pytest.approx(cost*a['keep_alive_roundtrips'])
