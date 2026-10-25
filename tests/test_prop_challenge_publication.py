import csv
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
import pytest
from scripts.prop_challenge import __main__ as run
from scripts.prop_challenge.read_outcomes import read


def test_private_binary_ledger_roundtrip_preserves_exact_net_values(tmp_path):
    path=tmp_path/'test.bin.gz'
    row=(1,3,4,123.456789123,49,49,2,3,9)
    a=np.array([row],dtype=run.OUTCOME_DTYPE)
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as f:
            f.write(b'QUANT_CHALLENGE_V1\n')
            f.write(json.dumps(['TEST','FIXED_1','TOPSTEP','2019_2021',21,1]).encode()+b'\n')
            f.write(a.tobytes())
    header,result=next(read(path))
    assert header[-1]==1 and result['net'][0]==row[3]
    assert result.tobytes()==a.tobytes()


def test_private_binary_reader_rejects_truncated_account_evidence(tmp_path):
    p=tmp_path/'broken.gz'
    with gzip.open(p,'wb') as f:f.write(b'QUANT_CHALLENGE_V1\n["T","F","T","E",21,1]\nX')
    with pytest.raises(ValueError,match='Truncated'):list(read(p))


def test_engine_code_hashes_match_declared_storage_only_amendment():
    proof=json.loads((run.ROOT/'research/prop-challenge-code-lock.json').read_text())
    for path,sha in proof['files'].items():assert run.digest(run.ROOT/path)==sha


def test_completed_research_preserves_all_original_files_and_double_replay():
    if not run.PROOF.exists():pytest.skip('Full research still running')
    assert run.verify()['protected_files']==744
    assert json.loads(run.PROOF.read_text())['status']=='BYTE_IDENTICAL_DOUBLE_RAW_RECONSTRUCTION'


def test_public_rankings_cover_every_valid_cell_without_private_paths():
    root=run.ROOT/'public/data/prop-challenge'
    if not (root/'register.json').exists():pytest.skip('Public export still pending')
    register=json.loads((root/'register.json').read_text())
    assert register['universe']['valid_cells']==2487
    for firm in ('topstep','mffu_eod'):
        for horizon in (21,42,63):
            t=json.loads((root/f'{firm}-{horizon}.json').read_text())
            assert len(t['rows'])==2487 and len(set(tuple(r[:2]) for r in t['rows']))==2487
            assert all(len(r)==len(t['columns']) for r in t['rows'])
            assert not set(t['columns'])&{'entry_time','exit_time','entry_price','path_points','raw','bars','trades_ledger'}


def test_outcome_partition_and_horizon_denominators():
    if not run.RESULT.exists():pytest.skip('Full research still running')
    result=json.loads(run.RESULT.read_text())
    assert len(result['results'])==14922
    for r in result['results']:
        for era,stats in r['eras'].items():
            assert stats['starts']==result['calendar'][era]['sessions']-r['horizon']+1
            assert stats['starts']==stats['passed']+stats['failed']+stats['unknown']+stats['unfinished']
            assert stats['pass_rate']<=stats['pass_upper_source_unknown']<=1
            if stats['unknown'] or not stats['passed']:assert stats['cost_per_pass_proxy_USD'] is None


def test_csv_includes_failure_causes_and_billing_sensitivities():
    path=run.ROOT/'public/reports/PROP_CHALLENGE_FULL_RANKING.csv'
    if not path.exists():pytest.skip('Public export still pending')
    with path.open() as f:
        reader=csv.DictReader(f);fields=set(reader.fieldnames)
        assert {'outcome_FAILED_OBSERVED_FLOOR','outcome_FAILED_OHLC_FLOOR_BOUND','outcome_FAILED_INACTIVITY_CONSERVATIVE',
                'mean_calendar_billed_fee_USD','cost_reset99_USD','nonoverlap_pass_rate'}<=fields
        assert sum(1 for _ in reader)==44766


def test_publication_file_hashes_and_frontend_privacy_allowlist():
    p=run.ROOT/'research/prop-challenge-publication.json'
    if not p.exists():pytest.skip('Public export still pending')
    proof=json.loads(p.read_text());assert not proof['private_data_included']
    for name,sha in proof['files'].items():assert run.digest(run.ROOT/name)==sha
    from scripts.build_prop_frontend import allowed
    assert allowed('app/research/prop-challenge/page.tsx')
    assert allowed('public/data/prop-challenge/topstep-21.json')
    for n in ('bot/engine.py','artifacts/prop-challenge/run1/rolling-outcomes.bin.gz','data/raw/a.csv','research/prop-challenge-results.json'):
        assert not allowed(n)


def test_identical_start_cohorts_have_monotone_pass_counts_across_horizons():
    path=run.ROOT/'public/reports/PROP_CHALLENGE_COMMON_STARTS.csv'
    if not path.exists():pytest.skip('Public export still pending')
    groups={}
    with path.open() as f:
        for row in csv.DictReader(f):
            key=tuple(row[k] for k in ('combination','sizing','firm','era'))
            groups.setdefault(key,{})[int(row['horizon'])]=(int(row['same_starts']),int(row['passed']))
    assert len(groups)==2487*2*2
    for group in groups.values():
        assert group[21][0]==group[42][0]==group[63][0]
        assert group[21][1]<=group[42][1]<=group[63][1]
