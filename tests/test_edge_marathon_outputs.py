import json
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.edge_marathon.core import catalog
from scripts.edge_marathon.runner import ROOT,OUT,verify
from scripts.edge_marathon.stats import holm
from scripts.afternoon_inference_round import sha


def read(path):return json.loads(path.read_text())


def test_marathon_protocol_implementation_and_prior_research_locked():
    lock=verify()
    assert lock['models']==catalog()
    assert len(lock['models'])==25
    assert lock['status']=='LOCKED_BEFORE_MARATHON_OUTCOMES'


def test_all25_rows_empty_cells_retained_in_correction():
    d=read(OUT/'discovery.json')
    assert set(d['models'])==set(catalog())
    q=holm([d['models'][n]['inference']['signflip_p'] for n in catalog()])
    for n,p in zip(catalog(),q):assert d['models'][n]['inference']['signflip_holm25']==p
    for n in ['ON_INVENTORY_CONT','ON_INVENTORY_REVERT']:
        assert d['models'][n]['metrics']['trades']==0
        assert d['models'][n]['inference']['signflip_p']==1
        assert d['models'][n]['inference']['conservative_p']==1


def test_discovery_parity_and_causal_checks_all435_days():
    d=read(OUT/'discovery.json')
    assert d['complete_days']==435
    assert d['models']['TOM_RTH']['metrics']['trades']==81
    np.testing.assert_allclose(d['models']['TOM_RTH']['metrics']['net_points'],4364.025)
    for horizon in [2,15]:assert d['models'][f'AFTERNOON_V2_{horizon}']['metrics']['trades']==162
    assert d['checks']['prefix_truncation_checks']==435*11
    assert d['checks']['future_mutation_checks']==435*11


def test_no_same_close_entry_and_fixed_cost_every_trade():
    df=pd.read_csv(OUT/'discovery-trades.csv')
    assert (df.entry>=df.decision).all()
    assert (df.end>df.entry).all()
    assert not df.duplicated(['model','day']).any()
    np.testing.assert_allclose(df.gross_points-df.net_points,1.225)
    assert df.fill_status.eq('BAR_PROXY_NOT_TICK_CERTIFIED').all()
    assert df.exit_reason.eq('FIXED_TIME').all()


def test_anatomy_reconciles_and_no_cherry_picked_days():
    df=pd.read_csv(OUT/'tom-paths.csv')
    assert len(df)==81
    np.testing.assert_allclose(df[['morning','midday','afternoon','bridge1100','bridge1400']].sum(axis=1),df.rth_points)
    assert set(df.position)=={'T-1','T+1','T+2','T+3'}


def test_cap_does_not_credit_missing_history_to_vol_filter():
    d=read(OUT/'discovery.json');c=d['cap_comparable_control']
    assert c['comparable_known_history_days']==66
    assert len(c['missing60history_tom_dates'])==15
    assert c['matched_baseline']['trades']==66
    assert c['cap']['trades']==61
    assert c['cap']['net_points']<c['matched_baseline']['net_points']


def test_historical_winner_selection_locked_before_and_mechanically_reproducible():
    d=read(OUT/'discovery.json');release=read(OUT/'historical-release.json')
    assert release['discovery_sha256']==sha(OUT/'discovery.json')
    variants=[n for n in ['TOM_TREND_1000','TOM_OVERNIGHT_1030','TOM_ATR_CAP']
              if d['models'][n]['metrics']['net_points']>0 and (d['models'][n]['metrics']['profit_factor'] or 0)>1.3]
    best=sorted(variants,key=lambda n:(-d['models'][n]['metrics']['profit_factor'],-d['models'][n]['metrics']['mean_net'],n))[0]
    assert release['best_tom_variant']==best=='TOM_ATR_CAP'
    assert {'AFTERNOON_V2_2','AFTERNOON_V2_15','TOM_RTH'}<=set(release['selected'])


def test_historical_sources_separate_and_global_holm_all125_rows():
    h=read(OUT/'historical.json')
    assert h['historical_family_size']==125
    pairs=[(s,n) for s,r in h['samples'].items() if 'models' in r for n in catalog()]
    adjusted=holm([h['samples'][s]['models'][n]['inference']['signflip_p'] for s,n in pairs])
    for (s,n),q in zip(pairs,adjusted):
        r=h['samples'][s]
        assert r['source_certified'] is False
        assert r['models'][n]['inference']['signflip_holm_all_historical_sources']==q
        if n not in r['selected_model_ids']:assert r['models'][n]['metrics']['trades']==0


def test_eight_january_days_not_treated_as_three_year_holdout():
    h=read(OUT/'historical.json');r=h['samples']['CONTRACT_2019_FRAGMENT']
    assert r['complete_days']==8
    assert r['period']==['2019-01-02','2019-01-11']
    assert 'NOT_FIXED_END_TEST' in r['exposure']
    for n in ['AFTERNOON_V2_2','AFTERNOON_V2_15']:
        assert r['models'][n]['metrics']['trades']==4
        assert r['models'][n]['inference']['conservative_p']==1.


def test_no_borrowed_atr60_history_for_contract_fragments():
    h=read(OUT/'historical.json')
    for s in ['CONTRACT_2018_WARMUP','CONTRACT_2019_FRAGMENT','CONTRACT_PILOT_2024','VENDOR_SAMPLE_OCT2026']:
        assert h['samples'][s]['models']['TOM_ATR_CAP']['metrics']['trades']==0


def test_independent_promotion_never_claimed_from_unverified_or_small_samples():
    r=read(ROOT/'research/edge-marathon-results.json')
    assert r['independent_validation_passes']==0
    assert all(not x['independently_validated'] for x in r['scorecard'])
    assert r['additional_unique_calendar_dates']==539
    assert r['additional_source_session_counts_not_independent']==558


def test_public_export_has_no_raw_arrays_private_paths_or_price_records():
    r=read(ROOT/'public/data/edge-marathon.json')
    forbidden={'entry_price','exit_price','open','high','low','close','volume','paths','private_copy','ledger_hashes'}
    def walk(value):
        if isinstance(value,dict):
            assert not set(value)&forbidden
            for v in value.values():walk(v)
        elif isinstance(value,list):
            for v in value:walk(v)
        elif isinstance(value,str):
            assert '/Users/' not in value
            assert 'data/raw/' not in value
    walk(r)


def test_signflip_support_not_misreported_as_conservative_information_pass():
    d=read(OUT/'discovery.json');r=d['models']['AFTERNOON_V2_2']
    assert r['inference']['signflip_holm25']<.05
    assert sum(r['inference']['conservative_group_counts'])==109
    assert r['inference']['conservative_status']=='DATA_INSUFFICIENT'
    assert r['inference']['conservative_holm25']==1.


def test_overlap_check_fixed_convention_no_clock_search():
    r=read(OUT/'source-overlap-parity.json')
    assert r['common_rth_minutes']>90000
    assert r['fifteen00_two_minute_move_exact_fraction']>.9
    assert 'No shift search' in r['caveat']


def test_inventory_zero_events_is_inconclusive_not_rejection():
    r=read(OUT/'inventory-feasibility.json')
    assert r['counts']['all_three_conditions']==0
    assert 'not evidence' in r['interpretation']


def test_no_loss_completeness_amendment_preserves_original_and_family():
    h=read(OUT/'historical.json');a=h['completeness_addendum']
    assert a['additional_models']==['AFTERNOON_TOM_YES_HIGH_2']
    assert a['registered_family_size']==25
    assert a['original_history_sha256']==sha(OUT/'historical-before-zero-loss-completion.json')
    assert a['original_release_sha256']==sha(OUT/'historical-release.json')
    assert 'AFTERNOON_TOM_YES_HIGH_2' not in read(OUT/'historical-release.json')['selected']
    assert h['samples']['CONTINUOUS_2022_2024_UNVERIFIED']['models']['AFTERNOON_TOM_YES_HIGH_2']['metrics']['trades']>0


def test_independent_selector_and_fill_reference_matches_all_events():
    result=read(ROOT/'research/edge-marathon-reference-parity.json')
    assert result['status']=='INDEPENDENT_SELECTOR_FILL_REFERENCE_PARITY_PASSED'
    assert sum(x['events'] for x in result['samples'])==2436
    assert all(x['maximum_absolute_difference']<1e-8 for x in result['samples'])
    assert result['reference_code_sha256']==sha(ROOT/'scripts/reference_edge_marathon.py')
