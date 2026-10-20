"""Offline public release guard. No proprietary raw data is required by CI."""
import hashlib
import json
from pathlib import Path
from verify_observed_snapshots import check

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    read = lambda p:json.loads((root/p).read_text())
    sha = lambda p:hashlib.sha256((root/p).read_bytes()).hexdigest()
    a,b = [read('public/data/'+n) for n in ['nq-overnight.json','research09.json']]
    check(a,b)
    frozen = read('research/reproduction-manifest.json')
    for name,digest in frozen['reference_files'].items():
        assert sha('public/data/'+name)==digest, 'Frozen in-sample export changed'
    h = read('public/data/research-holdout.json')
    assert h==read('research/holdout-reference.json'), 'Frozen holdout export changed'
    protocol = read('research/holdout-protocol.json')
    assert sha('scripts/reproduce_research/engine.py')==protocol['frozen_engine_sha256']
    assert sha('research/holdout-protocol.json')==h['protocol_sha256']
    assert h['status']=='HOLDOUT_FAILED' and h['promotion_checks']['net_profit'] is False
    assert a['period']==['2024-12-30','2025-04-17']
    assert h['period']=={'start':'2025-04-18','end':'2025-09-30'}
    assert a['period'][1]<h['period']['start']
    m=h['holdout']['B_ORB15']['all']
    assert m['trades']==76 and m['eligible_days']==81 and abs(m['net_points']+627.6)<1e-9
    p=read('public/data/research-postmortem.json')
    assert p['classification']=='DESCRIPTIVE_POST_HOC_NOT_NEW_HOLDOUT'
    for key,expected_n,expected_t,expected_pnl in [('in_sample',42,37,919.425),('out_of_sample',81,76,-627.6)]:
        s=p[key]
        assert (s['eligible_days'],s['trades'])==(expected_n,expected_t)
        assert abs(sum(r['net_points'] for r in s['long_short'].values())-expected_pnl)<1e-9
        assert sum(r['trades'] for r in s['long_short'].values())==expected_t
        for r in s['return_inside_range_after_entry'].values():
            assert 0<=r['returned_inside']<=r['trades_with_complete_window']==expected_t
            assert abs(r['fraction']-r['returned_inside']/expected_t)<1e-12
    assert all(not r['zero_lost_sessions_possible_under_frozen_rules'] for r in p['warmup'])
    return {'status':'PASS','in_sample_points':919.425,'holdout_points':m['net_points'],
            'holdout_status':h['status'],'raw_required_for_this_offline_guard':False}


if __name__=='__main__':
    print(json.dumps(verify(),sort_keys=True))
