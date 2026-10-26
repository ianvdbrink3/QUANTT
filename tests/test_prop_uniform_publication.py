import gzip
import hashlib
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public/data/prop-uniform/summary.json'


@pytest.mark.skipif(not PUBLIC.exists(),reason='Needs local uniform-risk replay')
def test_all_profiles_all_periods_full_year_cash_and_hard_risk_caps():
    x=json.loads(PUBLIC.read_text());assert len(x['rows'])==171
    for r in x['rows']:
        assert r['starts']=={'2019_2021':498,'2024_2026':171,'COMBINED':669}[r['era']]
        if r['budget_USD'] is not None:
            cap=1.25*r['budget_USD']
            assert r['max_initial_overnight_risk_USD']<=cap+1e-8
            assert r['max_initial_judas_risk_USD']<=cap+1e-8
        if r['mean_net_full_window_USD'] is not None:
            assert r['mean_net_full_window_USD']>=r['mean_net_first_two_USD']-1e-8
            assert r['mean_net_full_window_USD']-r['mean_net_first_two_USD']==pytest.approx(r['mean_additional_cash_after_second_USD'])
        else:
            assert r['live_transition_unmodeled']>0
        assert r['payout5_all_starts']<=r['payout3_all_starts']<=r['payout2_all_starts']<=r['payout1_all_starts']
    for era in ('2019_2021','2024_2026','COMBINED'):
        for model in ('S1-Judas-Bull0930','S1-Judas-0830','S2-Judas-STOP050','S2-Judas-STOP075'):
            for firm in ('TOPSTEP_STANDARD','TOPSTEP_CONSISTENCY','MFFU_BUILDER'):
                assert len([r for r in x['rows'] if r['era']==era and r['model']==model and r['firm']==firm and r['profile'] in ('UNIFORM_300','UNIFORM_350','UNIFORM_400')])==3


@pytest.mark.skipif(not PUBLIC.exists(),reason='Needs local uniform-risk replay')
def test_source_and_code_lock_double_replay_and_no_private_public_arrays():
    lock=json.loads((ROOT/'research/prop-uniform-registration.json').read_text())
    for key in ('protected','code_sha256'):
        for name,digest in lock[key].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    for name in ('summary.json','summary.csv','accounts.json.gz'):
        assert (ROOT/'artifacts/prop-uniform/run1'/name).read_bytes()==(ROOT/'artifacts/prop-uniform/run2'/name).read_bytes()
    accounts=json.loads(gzip.decompress((ROOT/'artifacts/prop-uniform/run1/accounts.json.gz').read_bytes()))
    assert len(accounts)==38133
    for a in accounts:
        assert a['received_first_two_USD']==pytest.approx(sum(p['received'] for p in a['payouts'][:2]))
        assert a['received_USD']==pytest.approx(sum(p['received'] for p in a['payouts']))
        assert a['cash_net_accrued_USD']==pytest.approx(a['received_USD']-a['fees_USD'])
    def check(x):
        if isinstance(x,dict):
            assert not set(x)&{'records','entry_price','entry_time','accounts','negative_record_lows'}
            for v in x.values():check(v)
        elif isinstance(x,list):
            for v in x:check(v)
    check(json.loads(PUBLIC.read_text()))
