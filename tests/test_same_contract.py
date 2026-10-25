import json
import numpy as np
import pandas as pd
import pytest
from scripts.same_contract.core import choose,path,successor
from scripts.same_contract import __main__ as run
from scripts.two_pillar.core import night
h=run.h


def roll(day='2025-06-17',decision='2025-06-16'):
    return dict(to='NQU25',decision_session=decision,effective_session=day,effective_utc=h.at('2025-06-16','18:00').isoformat())


def test_current_completed_volume_or_tomorrow_route_cannot_change_16_contract():
    # June16's volume can only affect June17, never the already selected June16.
    a=choose('2025-06-16','2025-06-17','NQM25',[])
    b=choose('2025-06-16','2025-06-17','NQM25',[roll()])
    assert a==b and a['contract']=='NQM25'
    assert choose('2025-06-17','2025-06-18','NQM25',[roll()])['contract']=='NQU25'


def test_future_cutoff_removes_future_volume_routes_without_changing_choice():
    rows=[roll(),dict(to='NQZ25',decision_session='2025-09-16',effective_session='2025-09-17',effective_utc=h.at('2025-09-16','18:00').isoformat())]
    assert choose('2025-06-18','2025-06-20','NQM25',rows)==choose('2025-06-18','2025-06-20','NQM25',rows[:1])


def test_expiry_guard_moves_contract_before_thursday_entry_not_after_friday_price():
    c=choose('2025-06-19','2025-06-20','NQM25',[])
    assert c['contract']=='NQU25' and c['expiry_guard']
    assert pd.Timestamp(c['selected_at_utc'])==h.at('2025-06-19','09:30')
    assert choose('2025-06-18','2025-06-19','NQM25',[])['contract']=='NQM25'
    assert successor('NQZ25')=='NQH26'


def test_impossible_effective_future_volume_record_rejected():
    r=roll();r['decision_session']='2025-06-17'
    with pytest.raises(ValueError,match='Future volume'):choose('2025-06-17','2025-06-18','NQM25',[r])


def bars(contract,entry=100,exit=105):
    ix=pd.DatetimeIndex([h.at('2025-06-16','16:00'),h.at('2025-06-17','09:30')])
    p=np.array([entry,exit],float)
    return pd.DataFrame(dict(open=p,high=p+1,low=p-1,close=p,volume=[10,10],contract=contract,usable=True),index=ix)


class Calendar:
    def grid(self,day):return pd.DatetimeIndex([h.at(day,'16:00')])


def test_same_contract_no_roll_jump_and_no_next_active_dependency():
    selected=bars('NQM25');other=bars('NQU25',entry=200,exit=205)
    holding,code=path(selected,'2025-06-16','2025-06-17',Calendar())
    times,prices,missing=holding
    t=night('2025-06-16','2025-06-17',times,prices,10,missing)
    assert code=='FILLED' and t['gross_points']==5 and t['net_points']==pytest.approx(3.775)
    other.loc[:,'open']=100000  # tomorrow's new active price cannot enter held path
    assert path(selected,'2025-06-16','2025-06-17',Calendar())[1]=='FILLED'


def test_missing_old_contract_exit_never_substitutes_available_new_contract():
    one=bars('NQM25').iloc[:1]
    assert path(one,'2025-06-16','2025-06-17',Calendar())==(None,'MISSING_SAME_CONTRACT_ENDPOINT')


def test_mixed_contract_bar_path_rejected():
    b=bars('NQM25');b.iloc[-1,b.columns.get_loc('contract')]='NQU25'
    with pytest.raises(ValueError,match='Mixed'):path(b,'2025-06-16','2025-06-17',Calendar())


def test_dst_selection_uses_ny_zone_not_fixed_utc():
    a=choose('2025-03-07','2025-03-10','NQH25',[])
    b=choose('2025-03-10','2025-03-11','NQH25',[])
    assert pd.Timestamp(a['selected_at_utc']).hour==14
    assert pd.Timestamp(b['selected_at_utc']).hour==13


def test_replay_bytes_archives_and_fixed_B_verified():
    run.verify()
    result=json.loads(run.RESULT.read_text())
    assert result['contract_selection']['future_route_not_used']
    assert result['contract_selection']['expiry_guard_sessions']==0
    proof=json.loads(run.PROOF.read_text())
    assert proof['status']=='BYTE_IDENTICAL_SAME_CONTRACT_REPLAYS'
    # All pre-existing rows reproduce; new executions alone explain the delta.
    for model in run.MODELS:
        old=json.loads((run.archive.OUT/'run1'/(model+'-trades.json')).read_text())
        new=json.loads((run.OUT/'run1'/(model+'-trades.json')).read_text())
        index={(t['entry_time'],t['exit_day']):t for t in new}
        assert len(new)>=len(old)
        for t in old:
            assert index[(t['entry_time'],t['exit_day'])]['net_points']==pytest.approx(t['net_points'])
        overnight=[t for t in new if t.get('contract')]
        assert all(t['contract']==choose(t['day'],t['exit_day'],t['contract'],[])['contract'] for t in overnight)
    for era in ('2019_2021','2024_2026'):
        assert result['coverage'][era]['rejections'].get('CONTRACT_SWITCH',0)==0
