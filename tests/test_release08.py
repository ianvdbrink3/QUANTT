"""Research Command Center bundle tests: reproducibility, provenance, execution & governance."""
import json
from pathlib import Path
import pytest
from quantlab.release08 import research_bundle,export_reference

def config(symbol='NQ',bars=1700):
    return {'schema_version':1,'dataset':{'source_kind':'synthetic_fixture','bars':bars},
            'instrument':symbol,'seed':41,'code_ref':'release08-test',
            'event_spacing_minutes':60}

def test_bundle_has_real_pipeline_outputs():
    b=research_bundle(config())
    assert b['schema_version']=='0.8'
    assert b['provenance']=='SYNTHETIC SANDBOX (DETERMINISTIC)'
    assert b['feature_quality']['opening_ranges']>=1
    assert b['feature_quality']['london_complete_segments']>0
    assert set(b['execution'])=={'base_pessimistic','stress_pessimistic',
                                  'base_optimistic','stress_optimistic'}
    assert not b['edge_validated']
    assert b['governance']['holdout_sealed']
    assert not b['governance']['holdout_scored']
    assert b['governance']['trials_registered']<=b['governance']['trial_budget']
    for scenario in b['forward'].values():
        for horizon in scenario.values():
            assert horizon['p_value'] is None
            assert horizon['fdr_adjusted_p'] is None

def test_same_seed_same_output():
    assert research_bundle(config())==research_bundle(config())

def test_es_has_correct_contract():
    b=research_bundle(config('ES'))
    assert b['instrument']=='ES'
    assert b['quality']['contract_ids']==['ESZ26']
    assert not b['edge_validated']

def test_reject_observed_input():
    c=config(); c['dataset']['source_kind']='observed_future'
    with pytest.raises(ValueError,match='verified source adapter'):
        research_bundle(c)

def test_reject_overlapping_event_spacing():
    c=config();c['event_spacing_minutes']=15
    with pytest.raises(ValueError,match='spacing'):
        research_bundle(c)

def test_export_keeps_cfd_separate_and_deterministic(tmp_path):
    output=tmp_path/'research08.json'
    a=export_reference([config(),config('ES')],output)
    assert a==json.loads(output.read_text())
    assert len(a['runs'])==2
    assert a['sources'][0]['market_type']=='index_cfd'
    assert a['sources'][1]['observed_bars']==0
    assert all(not r['edge_validated'] for r in a['runs'])
    first=output.read_bytes()
    export_reference([config(),config('ES')],output)
    assert first==output.read_bytes()

def test_sealed_holdout_never_emits_forward_labels_or_execution(tmp_path):
    from quantlab.research_pipeline import fixture_frame
    import pandas as pd
    c=config('NQ',2400)
    b=research_bundle(c)
    horizon=pd.Timedelta(minutes=60)
    index=fixture_frame(c['seed'],c['dataset']['bars']).index
    withheld=index[int(len(index)*.8)]
    embargo=pd.Timedelta(minutes=b['governance']['embargo_minutes'])
    assert all(pd.Timestamp(e['signal_utc'])+horizon<withheld-embargo for e in b['events'])
    assert b['governance']['holdout_events_evaluated']==0
    assert b['governance']['forward_evaluated_events']==len(b['events'])
    assert b['governance']['holdout_sealed'] and not b['governance']['holdout_scored']
    assert b['governance']['holdout_count_sealed']>=0
    assert all(v['trades']<=len(b['events']) for v in b['execution'].values())

def test_matched_control_counts_never_exceed_visible_event_counts():
    r=research_bundle(config('NQ',2400))
    for family in r['forward'].values():
        for outcome in family.values():
            assert outcome['matched_events']+outcome['unmatched_events']==outcome['n']
            assert outcome['matching_dimensions']==['hour_et','volatility_regime_prior20']
            assert outcome['p_value'] is None
            assert outcome['fdr_adjusted_p'] is None

def test_asia_point_in_time_levels_require_complete_window():
    from quantlab.release08 import asia_context
    from quantlab.research_pipeline import fixture_frame
    import pandas as pd
    frame=fixture_frame(41,2400)
    asia=asia_context(frame)
    first=pd.Timestamp('2026-10-19T22:00:00Z')
    after=first+pd.Timedelta(minutes=1)
    assert pd.isna(asia.loc[first,'asia_high'])
    assert asia.loc[after,'asia_high']==frame.loc[first,'high']
    missing=frame.drop(first+pd.Timedelta(minutes=10))
    broken=asia_context(missing)
    midnight=pd.Timestamp('2026-10-20T04:00:00Z')
    assert pd.isna(broken.loc[midnight,'asia_high'])
