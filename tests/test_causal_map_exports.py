import json
import subprocess

import numpy as np
import pandas as pd

from scripts.causal_map.__main__ import ROOT, LOCK, preflight
from scripts.causal_map.core import holm
from scripts.oos_preparation.adapter import sha


def test_archive_and_locked_method_unchanged():
    assert preflight()['protected_files']==115


def test_all_cells_and_both_p_families_published_without_selection():
    data=json.loads((ROOT/'public/data/research-causal-map.json').read_text())
    ranking=pd.read_csv(ROOT/'public/data/research-causal-map.ranking.csv')
    assert len(data['rows'])==len(ranking)==128
    assert ranking['rank'].nunique()==128
    assert sum(r['inference_bps']['status']=='OK' for r in data['rows'])==100
    p=[]
    for r in data['rows']:p.extend([r['inference_bps']['p'],r['inference_bps']['hac_p']])
    adjusted=holm(p)
    for i,r in enumerate(data['rows']):
        assert r['p_holm256']==adjusted[2*i]
        assert r['hac_p_holm256']==adjusted[2*i+1]


def test_quarters_keep_all_eight_including_empty_cells():
    quarters=pd.read_csv(ROOT/'public/data/research-causal-map.quarters.csv')
    assert len(quarters)==128*8
    assert set(quarters.quarter)=={'2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2','2026Q3'}
    assert quarters.events.sum()==24093
    assert quarters.loc[quarters.events.eq(0),'mean_points'].isna().all()


def test_no_private_ledger_or_raw_prices_in_publication():
    publication=json.loads((ROOT/'research/causal-map-publication.json').read_text())
    for name,digest in publication['files_sha256'].items():
        assert name.startswith('public/data/research-causal-map')
        assert sha(ROOT/name)==digest
    public=json.loads((ROOT/'public/data/research-causal-map.json').read_text())
    assert 'event_log' not in public and 'records' not in public
    assert public['verification']['protected_archive_files']==115


def test_explicit_text_erratum_does_not_rewrite_original_protocol():
    public=json.loads((ROOT/'public/data/research-causal-map.json').read_text())
    assert 'one-day2024Q4' in public['protocol']['quarters']
    assert public['publication_clarification']['selection_thresholds_horizons_statistics_changed'] is False
    quality=json.loads((ROOT/'artifacts/raw-market/quality.json').read_text())
    assert [r['day'] for r in quality if r['included'] and r['day'].startswith('2024')]==['2024-12-30','2024-12-31']


def test_every_private_evidence_hash_and_replay_match():
    done=json.loads((ROOT/'artifacts/causal-map/COMPLETED.json').read_text())
    for name,digest in done['files_sha256'].items():assert sha(ROOT/name)==digest
    assert sha(ROOT/'artifacts/causal-map/events-horizons.csv')==sha(ROOT/'artifacts/causal-map/events-horizons-replay.csv')


def test_export_is_deterministic_without_rescanning():
    publication=ROOT/'research/causal-map-publication.json'
    before=publication.read_bytes()
    subprocess.run([str(ROOT/'.venv/bin/python'),'-B','-m','scripts.publish_causal_map'],cwd=ROOT,check=True,capture_output=True)
    assert publication.read_bytes()==before
