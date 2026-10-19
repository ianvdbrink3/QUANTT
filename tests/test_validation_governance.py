import pandas as pd
import pytest
from quantlab.validation_governance import (ResearchFamily,purge_overlapping_events,
 holdout_lock,robustness_gate,orchestrator_protocol)

def events():
    return pd.DataFrame({
       'event_start_utc':['2026-01-05T14:00:00Z','2026-01-05T14:55:00Z',
                          '2026-01-05T15:01:00Z','2026-01-05T15:07:00Z'],
       'event_end_utc':['2026-01-05T14:10:00Z','2026-01-05T15:05:00Z',
                        '2026-01-05T15:04:00Z','2026-01-05T15:12:00Z']})
def test_purge_overlaps_and_embargo():
    r=purge_overlapping_events(events(),'2026-01-05T15:00:00Z',embargo_minutes=5)
    assert len(r['train'])==1
    assert len(r['evaluation'])==1
    assert r['purged_or_embargoed']==2
def test_invalid_interval_rejected():
    x=events();x.loc[0,'event_end_utc']='2026-01-05T13:00:00Z'
    with pytest.raises(ValueError,match='Invalid event'): purge_overlapping_events(x,'2026-01-05T15:00:00Z')
def test_naive_cutoff_rejected():
    with pytest.raises(ValueError,match='timezone-aware'):
        purge_overlapping_events(events(),'2026-01-05T15:00:00')
def test_family_budget_cannot_expand_without_new_spec():
    assert ResearchFamily('london-sweep',('a','b'),2).validate().max_trials==2
    with pytest.raises(ValueError,match='budget'):
        ResearchFamily('london-sweep',('a','b','c'),2).validate()
def test_holdout_lock_cannot_change(tmp_path):
    path=tmp_path/'holdout.json'
    lock=holdout_lock(path,data_hash='data1',configuration_hash='cfg1',family_id='fam1')
    assert not lock['unsealed']
    assert holdout_lock(path,data_hash='data1',configuration_hash='cfg1',family_id='fam1')==lock
    with pytest.raises(ValueError,match='different'):
        holdout_lock(path,data_hash='data2',configuration_hash='cfg1',family_id='fam1')
def test_small_sample_never_approved():
    assert robustness_gate([1.,2.,3.])['status']=='STATISTICALLY INCONCLUSIVE'
def test_tail_flip_flagged():
    r=robustness_gate([-1.0]*38+[50.0]*2,min_events=30)
    assert r['direction_flips_without_tails']
    assert r['status']=='STATISTICALLY INCONCLUSIVE'
def test_orchestrator_is_read_only():
    d=orchestrator_protocol()
    assert not d['live_trading_enabled'] and not d['llm_may_approve_edge']
    assert len(d['roles'])==7
