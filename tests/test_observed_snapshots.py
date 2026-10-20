"""Regressions for snapshot invariants, without vendor-proprietary minute data."""
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from verify_observed_snapshots import check

def reports():
    return [json.loads((ROOT/"public"/"data"/x).read_text()) for x in ("nq-overnight.json","research09.json")]

def test_integrity_gate():
    a,b=reports()
    result=check(a,b)
    assert result["rows"]>100000 and result["edge_validated"] is False

def test_fake_edge_is_rejected():
    a,b=reports()
    a["edge_validated"]=True
    with pytest.raises(AssertionError,match="validated edge"):
        check(a,b)

def test_run_disagreement_is_rejected():
    a,b=reports()
    b["run_id"]="bad"
    with pytest.raises(AssertionError,match="Research run"):
        check(a,b)

def test_false_source_attestation_rejected():
    a,b=reports()
    a["import_gate"]["source_authenticated"]=True
    with pytest.raises(AssertionError,match="Source or calendar"):
        check(a,b)

def test_split_mismatch_rejected():
    a,b=reports()
    a["strategies"][2]["splits"]["first"]["net_points"]+=1
    with pytest.raises(AssertionError,match="half-split"):
        check(a,b)
