"""End-to-end synthetic pipeline, immutable run identity, registry corruption and fail-closed gates."""
import json
import pytest
from quantlab.research_pipeline import run_research,write_bundle,main,fixture_frame,quality_gate

CONFIG={'schema_version':1,'dataset':{'source_kind':'synthetic_fixture','bars':500},
        'instrument':'NQ','seed':42,'code_ref':'test-revision',
        'feature':'close','threshold':19999,'side':'above',
        'event_spacing_minutes':60,'horizon_minutes':15}

def test_e2e_reproducible_and_nonvalidated(tmp_path):
    a=run_research(CONFIG);b=run_research(CONFIG)
    assert a==b
    assert a['run_id']==b['run_id'] and not a['edge_validated']
    assert a['quality']['status']=='PASS'
    assert a['provenance']=='SYNTHETIC_FIXTURE_ONLY'
    write_bundle(a,tmp_path)
    write_bundle(b,tmp_path)
    assert len((tmp_path/'registry.jsonl').read_text().splitlines())==1
    assert json.loads((tmp_path/'result.json').read_text())==a
    assert 'NO REAL MARKET EDGE' in (tmp_path/'report.md').read_text()

def test_quality_gate_rejects_missing_minute():
    x=fixture_frame(2,150).drop(fixture_frame(2,150).index[3])
    with pytest.raises(ValueError,match='missing minute'): quality_gate(x)

def test_quality_gate_rejects_ohlc():
    x=fixture_frame(2,150)
    x.loc[x.index[1],'high']=1
    with pytest.raises(ValueError,match='OHLC'): quality_gate(x)

def test_reject_observed_source_disguised_as_fixture():
    x={**CONFIG,'dataset':{'source_kind':'observed_future','bars':500}}
    with pytest.raises(ValueError,match='source adapter'): run_research(x)

def test_reject_short_horizon_spacing():
    x={**CONFIG,'horizon_minutes':30,'event_spacing_minutes':10}
    with pytest.raises(ValueError,match='spacing'): run_research(x)

def test_registry_corruption_never_overwritten(tmp_path):
    (tmp_path/'registry.jsonl').write_text('{"invalid":true}\n')
    with pytest.raises(ValueError,match='Corrupt'): write_bundle(run_research(CONFIG),tmp_path)

def test_cli_creates_and_repeats_bundle(tmp_path):
    cfg=tmp_path/'config.yaml'
    cfg.write_text('''schema_version: 1
dataset:
  source_kind: synthetic_fixture
  bars: 500
instrument: NQ
code_ref: cli-test
seed: 7
''')
    dest=tmp_path/'output'
    assert main(['--config',str(cfg),'--out',str(dest)])==0
    assert main(['--config',str(cfg),'--out',str(dest)])==0
    assert (dest/'report.md').exists()
    assert len((dest/'registry.jsonl').read_text().splitlines())==1

def test_cli_records_failures(tmp_path):
    cfg=tmp_path/'config.yaml'
    cfg.write_text('''schema_version: 1
dataset:
  source_kind: observed_future
  bars: 200
instrument: NQ
''')
    dest=tmp_path/'out'
    with pytest.raises(ValueError): main(['--config',str(cfg),'--out',str(dest)])
    assert json.loads((dest/'failures.jsonl').read_text().splitlines()[0])['status']=='FAILED'

def test_repository_shipped_demo_yaml_is_executable(tmp_path):
    """Exercise the actual committed CLI config, not just an inline imitation."""
    from pathlib import Path
    demo=Path(__file__).resolve().parents[1]/'configs'/'synthetic_research.yaml'
    assert demo.exists()
    out=tmp_path/'shipped-demo'
    assert main(['--config',str(demo),'--out',str(out)])==0
    a=json.loads((out/'result.json').read_text())
    assert a['provenance']=='SYNTHETIC_FIXTURE_ONLY'
    assert a['quality']['status']=='PASS'
    assert a['edge_validated'] is False
    assert a['manifest']['code_ref']=='synthetic-e2e-v1'
