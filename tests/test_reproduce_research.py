"""Fast negative controls; real raw replay is the separate verify:research command."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import pytest
from scripts.reproduce_research.cli import preflight, compare, semantic_payload, verify_targets, trade_ledger_sha256

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs(tmp_path):
    raw=tmp_path/'raw';public=tmp_path/'public'
    raw.mkdir();public.mkdir()
    sources=[]
    for i in range(11):
        p=raw/f'source-{i}.csv';p.write_text(f'source-{i}\n')
        sources.append({'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    reports={'nq-overnight.json':{'source_csv_hashes':[s['sha256'] for s in sources]},'research09.json':{'sources':[]}}
    hashes={}
    for name,obj in reports.items():
        p=public/name;p.write_text(json.dumps(obj))
        hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    return raw,public,{'sources':sources,'reference_files':hashes}


def test_preflight_success(inputs):
    raw,public,manifest=inputs
    assert len(preflight(raw,manifest,public))==2


def test_raw_tampering_is_fatal(inputs):
    raw,public,manifest=inputs
    (raw/'source-0.csv').write_text('changed')
    with pytest.raises(ValueError,match='SHA256 MISMATCH'):
        preflight(raw,manifest,public)


def test_missing_raw_is_fatal(inputs):
    raw,public,manifest=inputs
    (raw/'source-0.csv').unlink()
    with pytest.raises(ValueError,match='MISSING'):
        preflight(raw,manifest,public)


def test_changed_public_reference_is_fatal(inputs):
    raw,public,manifest=inputs
    (public/'research09.json').write_text('{}')
    with pytest.raises(ValueError,match='PUBLISHED REPORT MISMATCH'):
        preflight(raw,manifest,public)


def test_manifest_must_match_published_source_hashes(inputs):
    raw,public,manifest=inputs
    manifest['sources'].reverse()
    with pytest.raises(ValueError,match='do not match'):
        preflight(raw,manifest,public)


def test_unsafe_source_path_is_fatal(inputs):
    raw,public,manifest=inputs
    manifest['sources'][0]['filename']='../secret.csv'
    with pytest.raises(ValueError,match='unsafe'):
        preflight(raw,manifest,public)


def test_payload_comparison_checks_all_results():
    compare({'n':37,'p':919.425},{'n':37,'p':919.42500000001})
    with pytest.raises(ValueError):
        compare({'n':37},{'n':37.0})
    with pytest.raises(ValueError):
        compare({'p':919.425},{'p':919.426})
    with pytest.raises(ValueError):
        compare({'trades':[1,2]},{'trades':[1]})


def test_metadata_exclusions_never_remove_source_or_result_fingerprints():
    actual=semantic_payload('nq-overnight.json',{'generated_at':'new','dataset_sha256':'bytes','source_csv_hashes':['a'],'trades':37})
    assert actual=={'source_csv_hashes':['a'],'trades':37}
    actual=semantic_payload('research09.json',{'sources':[{'staged_sha256':'bytes','dataset_fingerprint':'logical','input_sha256':'raw'}]})
    assert actual['sources']==[{'dataset_fingerprint':'logical','input_sha256':'raw'}]


def test_targets_use_decimal_half_up_and_underlying_trade_list():
    manifest={'expected':{'bars':106678,'eligible_days':42,'orb15_trades':37,'orb15_net_points':919.425,'orb15_display_points':'919.43'}}
    experiments=[{'name':'B_ORB15','quality_view':'all','metrics':{'trades':37,'eligible_days':42,'net_points':919.425}}]
    trades=[{'strategy':'B_ORB15','gross_points':964.75}]+[{'strategy':'B_ORB15','gross_points':0}]*36
    manifest['expected']['orb15_trade_ledger_sha256']=trade_ledger_sha256(trades)
    assert verify_targets(manifest,{'bars':106678},experiments,trades)['orb15_display_points']=='919.43'
    with pytest.raises(ValueError,match='trade-list'):
        verify_targets(manifest,{'bars':106678},experiments,trades[:-1])
    experiments[0]['metrics']['eligible_days']=41
    with pytest.raises(ValueError,match='eligible_days'):
        verify_targets(manifest,{'bars':106678},experiments,trades)


def test_same_total_but_different_individual_trades_are_rejected():
    one=[{'strategy':'B_ORB15','entry_utc':'09:46','gross_points':1},{'strategy':'B_ORB15','entry_utc':'10:00','gross_points':2}]
    two=[{'strategy':'B_ORB15','entry_utc':'09:46','gross_points':2},{'strategy':'B_ORB15','entry_utc':'10:00','gross_points':1}]
    assert sum(x['gross_points'] for x in one)==sum(x['gross_points'] for x in two)
    assert trade_ledger_sha256(one)!=trade_ledger_sha256(two)


def test_optimized_python_cannot_disable_assertions():
    r=subprocess.run([sys.executable,'-O','-m','scripts.reproduce_research.cli','--hashes-only'],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode!=0 and 'Do not run with Python -O' in r.stderr


def test_raw_entire_directory_and_private_outputs_are_gitignored():
    r=subprocess.run(['git','check-ignore','data/raw/example.csv','data/raw/nested/example.txt','artifacts/reproduction/output.json'],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0
    assert len(r.stdout.splitlines())==3


def test_npm_launcher_fails_closed_without_private_data(tmp_path):
    r=subprocess.run(['node','scripts/reproduce-research','--raw-dir',str(tmp_path),'--hashes-only'],cwd=ROOT,capture_output=True,text=True,env={**__import__('os').environ,'PYTHON':sys.executable})
    assert r.returncode!=0 and 'MISSING' in r.stderr
