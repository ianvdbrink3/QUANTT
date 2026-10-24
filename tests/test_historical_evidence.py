"""Quality-only evidence tests; never score the registered remainder."""
import ast
import inspect
import json

import numpy as np
import pandas as pd
import pytest

from scripts import audit_historical_evidence as e
from scripts import prepare_historical_contracts as h


def bars(ix,volume=10.):
    return pd.DataFrame(dict(open=100.,high=101.,low=99.,close=100.,
        volume=volume,usable=True),index=ix)


def test_closed_day_overlay_isolated_and_source_supported():
    old=h.HistoricalCalendar();new=e.EvidenceCalendar()
    assert len(old.grid('2021-04-02'))==0
    ix=new.grid('2021-04-02')
    assert len(ix)==915
    assert ix.max()==h.at('2021-04-02','09:14')
    assert h.at('2021-04-02','09:15') not in ix
    assert len(h.HistoricalCalendar().grid('2021-04-02'))==0
    for day in pd.bdate_range('2018-11-19','2021-12-31').strftime('%Y-%m-%d'):
        if day!='2021-04-02':assert old.grid(day).equals(new.grid(day))


@pytest.mark.parametrize('day,minutes', [('2021-06-25',1365),('2021-06-28',1380),
    ('2019-11-28',1140),('2019-11-29',1155),('2021-12-25',0)])
def test_overlay_does_not_change_other_calendar_cases(day,minutes):
    assert len(e.EvidenceCalendar().grid(day))==minutes


def test_interior_gap_never_implies_zero_volume():
    day='2019-06-14';c=h.HistoricalCalendar();ix=c.grid(day)
    r=e.comparison(bars(ix.delete(100)),bars(ix,11),day,c)
    assert r['endpoint_rule_pass'] and r['candidate_qualifying']
    assert not r['both_grids_complete']
    assert r['old']['missing']==1
    assert r['missing_volume_bound'] is None


def test_full_grid_is_distinct_from_release_certification():
    c=h.HistoricalCalendar();day='2021-03-15';ix=c.grid(day)
    r=e.comparison(bars(ix),bars(ix,11),day,c)
    assert r['both_grids_complete']
    assert 'release_approved' not in r


def test_endpoint_rejection_does_not_discard_from_audit():
    day='2019-06-14';c=h.HistoricalCalendar();ix=c.grid(day)
    r=e.comparison(bars(ix[1:]),bars(ix,100),day,c)
    assert not r['endpoint_rule_pass']
    assert r['observed_new_minus_old']>0
    assert not r['candidate_qualifying']


@pytest.mark.parametrize('bad', ['duplicate','wrong_contract','bad_volume','wrong_schema','bad_footer'])
def test_daily_csv_strict_contract_and_format(tmp_path,bad):
    p=tmp_path/'nqm19_daily_example.csv'
    columns=h.SCHEMA+['Open Int']
    rows=[['2019-06-14',100,101,99,100,0,'0%',254822,1000]]
    if bad=='duplicate':rows*=2
    if bad=='bad_volume':rows[0][7]=-1
    g=pd.DataFrame(rows,columns=columns)
    if bad=='wrong_schema':g=g.drop(columns='Open Int')
    import csv
    with p.open('w',newline='') as f:
        g.to_csv(f,index=False)
        w=csv.writer(f);w.writerow(['bad footer' if bad=='bad_footer' else 'Downloaded from Barchart.com as of example'])
    with pytest.raises(ValueError):e.daily_csv(p,'NQU19' if bad=='wrong_contract' else 'NQM19')


def test_no_outcome_calls_or_old_report_writes():
    tree=ast.parse(inspect.getsource(e))
    calls={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
    calls|={n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
    assert not calls & {'select','fill','old_discovery_parity','simulate','score','backtest'}
    assert e.RESULT!=h.RESULT and e.REPORT!=h.REPORT and e.PUBLIC!=h.PUBLIC


def test_evidence_protocol_stays_quality_only():
    p=json.loads(e.PROTOCOL.read_text())
    assert p['outcomes_authorized'] is False
    assert p['replace_roll_rule_with_daily_volume'] is False
    assert p['missing_minutes_are_zero'] is False
    assert len(p['daily_checks'])==4
    assert p['calendar_overlay_only']=={'2021-04-02':'09:15'}


def test_real_audit_output_remains_blocked_and_reports_contradiction():
    if not e.RESULT.exists():pytest.skip('Quality audit output not built')
    r=json.loads(e.RESULT.read_text())
    assert not r['release_approved'] and not r['signals_computed'] and not r['holdout_executed']
    assert r['original_sources_hash_verified']==105
    assert len(r['volume_rollovers'])==13
    assert r['independently_certified_rollovers']==0
    june=next(x for x in r['volume_rollovers'] if x['old']=='NQM19')
    assert june['decision_observed_margin']==2055
    assert june['daily_crosscheck']['decision_day']['difference']==-1653
    assert june['daily_crosscheck']['same_decision_sign'] is False
    march=next(x for x in r['volume_rollovers'] if x['old']=='NQH20')
    assert march['daily_crosscheck']['same_decision_sign'] is True
    assert all(x['active_bars_at_or_after_expiry_open']==0 for x in r['expiry_checks'])
    assert len(r['verified_CME_calendar_cells'])==3
    assert r['calendar_context_impact']['april5_prefix_test']


def test_new_public_export_has_no_price_arrays():
    if not e.PUBLIC.exists():pytest.skip('Audit not built')
    x=json.loads(e.PUBLIC.read_text())
    banned={'open','high','low','close','atr14_prior','PDH','PDL','net_points','gross_points','trades','prices'}
    def walk(v):
        if isinstance(v,dict):
            assert not banned & v.keys()
            for z in v.values():walk(z)
        if isinstance(v,list):
            for z in v:walk(z)
    walk(x)
