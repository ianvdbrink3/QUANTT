"""QUANT 0.9 regression: observed-data segregation and provenance controls."""
import csv
import json
import pandas as pd
import pytest
from quantlab.futures_import import stage_futures_csv
from quantlab.observed_release09 import append_registry, build_observed_bundle, export_observed, load_staged


def _csv(tmp_path, symbol="NQ", gap=None):
    path = tmp_path / (symbol + ".csv")
    start = pd.Timestamp("2026-10-19T13:30:00Z")
    base = 20000 if symbol in {"NQ", "MNQ"} else 5000
    last = float(base)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("timestamp_utc", "contract_id", "open", "high", "low", "close", "volume"))
        for i in range(145):
            if i == gap:
                continue
            close = float(base + 0.5) if i >= 16 else float(base)
            writer.writerow(((start + pd.Timedelta(minutes=i)).isoformat(),
                             symbol + "Z26", last, max(last, close) + .25,
                             min(last, close) - .25, close, 10 + i))
            last = close
    return path


def _stage(tmp_path, symbol="NQ", gap=None):
    source = _csv(tmp_path, symbol, gap)
    dest = tmp_path / (symbol + ".parquet")
    report = stage_futures_csv(source, dest, instrument=symbol, source="UNIT_TEST_VENDOR_UNVERIFIED")
    dest.with_suffix(".quality.json").write_text(json.dumps(report), encoding="utf-8")
    return dest


def test_observed_pipeline_from_contract_shape(tmp_path):
    staged = _stage(tmp_path)
    result = build_observed_bundle([staged])
    assert result["status"] == "STAGED_UNVERIFIED"
    assert result["row_count"] == 145
    assert result["sources"][0]["contracts"] == ["NQZ26"]
    assert result["data_is_synthetic"] is False
    assert result["edge_validated"] is False
    assert result["governance"]["holdout_scored"] is False
    assert result["governance"]["execution_simulated"] is False
    assert result["event_counts"]["NY opening range breakout"]["detected"] == 1
    assert result["descriptive_forward"]["NY opening range breakout"]["60"]["complete_events"] == 1


def test_missing_minute_invalidates_exact_horizon(tmp_path):
    result = build_observed_bundle([_stage(tmp_path, gap=40)])
    assert result["sources"][0]["observed_gaps"] == 1
    assert result["descriptive_forward"]["NY opening range breakout"]["15"]["complete_events"] == 1
    assert result["descriptive_forward"]["NY opening range breakout"]["30"]["complete_events"] == 0
    assert result["descriptive_forward"]["NY opening range breakout"]["60"]["complete_events"] == 0


def test_file_tamper_rejected(tmp_path):
    staged = _stage(tmp_path)
    with staged.open("ab") as file:
        file.write(b"tampered")
    with pytest.raises(ValueError, match="checksum"):
        load_staged(staged)


def test_sidecar_fingerprint_tamper_rejected(tmp_path):
    staged = _stage(tmp_path)
    audit = staged.with_suffix(".quality.json")
    report = json.loads(audit.read_text())
    report["dataset_fingerprint"] = "0" * 64
    audit.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="fingerprint"):
        load_staged(staged)


def test_cfd_and_synthetic_sidecars_rejected(tmp_path):
    staged = _stage(tmp_path)
    audit = staged.with_suffix(".quality.json")
    report = json.loads(audit.read_text())
    for kind in ("synthetic_fixture", "CFD", None):
        report["source_type"] = kind
        audit.write_text(json.dumps(report))
        with pytest.raises(ValueError, match="non-futures"):
            load_staged(staged)


def test_multi_instrument_segregation(tmp_path):
    nq = _stage(tmp_path, "NQ")
    es = _stage(tmp_path, "ES")
    result = build_observed_bundle([nq, es])
    assert result["row_count"] == 290
    assert {s["instrument"] for s in result["sources"]} == {"NQ", "ES"}
    with pytest.raises(ValueError, match="Duplicate contract"):
        build_observed_bundle([nq, nq])


def test_publication_gate_and_determinism(tmp_path):
    staged = _stage(tmp_path)
    public = tmp_path / "public" / "data" / "research09.json"
    with pytest.raises(ValueError, match="publication-approved"):
        export_observed([staged], public)
    assert not public.exists()
    a = export_observed([staged], tmp_path / "private-a.json")
    b = export_observed([staged], tmp_path / "private-b.json")
    assert a == b and a["run_id"] == b["run_id"]
    published = export_observed([staged], public, publication_approved=True)
    assert published == a
    assert json.loads(public.read_text())["edge_validated"] is False


def test_no_data_has_no_synthetic_fallback(tmp_path):
    with pytest.raises(ValueError, match="No staged"):
        build_observed_bundle([])
    fake = tmp_path / "x.parquet"
    fake.write_bytes(b"not-a-market-file")
    with pytest.raises(ValueError, match="Missing audited"):
        build_observed_bundle([fake])



def test_registry_is_private_and_idempotent(tmp_path):
    bundle = build_observed_bundle([_stage(tmp_path)])
    ledger = tmp_path / "artifacts" / "registry.jsonl"
    assert append_registry(bundle, ledger) is True
    assert append_registry(bundle, ledger) is False
    assert len(ledger.read_text().splitlines()) == 1
    with pytest.raises(ValueError, match="private"):
        append_registry(bundle, tmp_path / "public" / "registry.jsonl")
    ledger.write_text('{"not_a_valid_registry":"entry"}\n')
    with pytest.raises(ValueError, match="Corrupt"):
        append_registry(bundle, ledger)


def test_continuous_contract_not_accepted(tmp_path):
    path = _csv(tmp_path)
    text = path.read_text()
    path.write_text(text.replace("NQZ26", "NQ1!"))
    with pytest.raises(ValueError, match="contract"):
        stage_futures_csv(path, tmp_path / "refused.parquet", instrument="NQ", source="licensed-broker")


def test_source_label_blocks_cfd_and_synthetic_synonyms(tmp_path):
    path = _csv(tmp_path)
    for source in ("SYNTHETIC data", "dukascopy export", "index-CFD", "Fixture Vendor"):
        with pytest.raises(ValueError, match="non-CFD"):
            stage_futures_csv(path, tmp_path / "out.parquet", instrument="NQ", source=source)



def test_cli_csv_stage_research_and_ledger(tmp_path):
    from scripts.export_research09 import main
    csv_path = _csv(tmp_path)
    stage_dir = tmp_path / "stage"
    out = tmp_path / "private" / "research09.json"
    ledger = tmp_path / "private" / "registry.jsonl"
    assert main(["--csv", "NQ=" + str(csv_path), "--source", "unit-test-vendor",
                 "--stage-dir", str(stage_dir), "--out", str(out),
                 "--registry", str(ledger)]) == 0
    assert json.loads(out.read_text())["row_count"] == 145
    assert (stage_dir / "NQ.parquet").exists()
    assert (stage_dir / "NQ.quality.json").exists()
    assert len(ledger.read_text().splitlines()) == 1
