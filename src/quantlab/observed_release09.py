"""QUANT 0.9: fail-closed, descriptive research on staged contract-native futures.

Never treats a valid CSV as proof of exchange origin, license, calendar accuracy,
broker fills, an independent holdout, or a statistically validated trading edge.
The synthetic 0.8 pipeline remains isolated from this observed-data path.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd

from quantlab.futures_research import evaluate_forward, session_context
from quantlab.research_contract import dataset_fingerprint, validate_bars
from quantlab.research_validation import opening_range, vwap_known_at

HORIZONS = (15, 30, 60)
FAMILIES = ("NY opening range breakout", "London high sweep", "VWAP mean reversion")
INSTRUMENTS = {"NQ", "ES", "MNQ", "MES"}


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for piece in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(piece)
    return digest.hexdigest()


def load_staged(path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Require the importer's exact audit sidecar and byte/content checksums."""
    staged = Path(path)
    if staged.suffix.lower() != ".parquet" or not staged.is_file():
        raise ValueError("Input must be an existing staged Parquet file")
    sidecar = staged.with_suffix(".quality.json")
    if not sidecar.is_file():
        raise ValueError("Missing audited .quality.json companion")
    quality = json.loads(sidecar.read_text(encoding="utf-8"))
    if quality.get("source_type") != "USER_SUPPLIED_CONTRACT_FUTURES":
        raise ValueError("Refusing non-futures, synthetic or unaudited source")
    if quality.get("trading_edge_validation_allowed") is not False:
        raise ValueError("Expected unverified futures staging status")
    structural = quality.get("structural_validation", {})
    instrument = structural.get("instrument")
    if instrument not in INSTRUMENTS or structural.get("bar_timestamp_convention") != "bar_open_utc":
        raise ValueError("Missing strict instrument/timestamp provenance")
    if structural.get("futures_source_authenticated") is not False:
        raise ValueError("Source attestation not independently audited")
    if _hash_file(staged) != quality.get("content_sha256"):
        raise ValueError("Parquet checksum mismatch")
    frame = validate_bars(pd.read_parquet(staged))
    if dataset_fingerprint(frame) != quality.get("dataset_fingerprint"):
        raise ValueError("Canonical dataset fingerprint mismatch")
    if len(frame) != quality.get("rows") or len(frame) != structural.get("rows"):
        raise ValueError("Data/sidecar row-count mismatch")
    if set(frame.instrument_id) != {instrument} or set(frame.market_type) != {"future"}:
        raise ValueError("Staging contains wrong instrument or market type")
    if set(frame.venue) != {"CME_UNVERIFIED"} or set(frame.source) != {quality.get("source_name")}:
        raise ValueError("Source/venue metadata tampered with")
    if frame.timestamp_utc.isna().any() or (frame.timestamp_utc.dt.second != 0).any():
        raise ValueError("Minute-aligned UTC bar-open timestamps required")
    actual_contracts = frame.groupby("contract_id").size().to_dict()
    if actual_contracts != structural.get("contracts"):
        raise ValueError("Contract counts differ from imported CSV")
    for contract, group in frame.groupby("contract_id"):
        ts = group.timestamp_utc.sort_values()
        if not ts.is_monotonic_increasing or ts.duplicated().any():
            raise ValueError(f"Duplicate contract timestamps: {contract}")
    return frame, quality


def _events(frame: pd.DataFrame) -> tuple[list[dict], dict]:
    """Descriptive event labels only; next-bar entry and exact complete paths."""
    result = []
    counts = {family: {"detected": 0, "complete_15m": 0, "complete_30m": 0, "complete_60m": 0}
              for family in FAMILIES}
    for contract, rows in frame.groupby("contract_id", sort=True):
        bars = rows.set_index("timestamp_utc").sort_index()
        context = session_context(bars)
        vwap = vwap_known_at(bars)
        oranges = opening_range(bars, minutes=15)
        local = bars.index.tz_convert("America/New_York")
        minutes = local.hour * 60 + local.minute
        day = pd.Index(local.date)
        flags = {family: pd.Series(False, index=bars.index) for family in FAMILIES}
        for r in oranges.itertuples():
            valid_day = day == pd.Timestamp(r.ny_calendar_date).date()
            in_window = (minutes >= 585) & (minutes < 720)  # 09:45–12:00 ET
            now_known = bars.index >= pd.Timestamp(r.known_at_utc)
            crossed = (bars.close > r.range_high) & (bars.close.shift(1) <= r.range_high)
            flags[FAMILIES[0]] |= pd.Series(valid_day & in_window & now_known & crossed, index=bars.index)
        in_ny_am = pd.Series((minutes >= 510) & (minutes < 720), index=bars.index)
        flags[FAMILIES[1]] = (in_ny_am & context.london_high.notna()
                              & (bars.high > context.london_high)
                              & (bars.close < context.london_high))
        flags[FAMILIES[2]] = (in_ny_am & vwap.vwap_prior.notna()
                              & (bars.close < vwap.vwap_prior)
                              & (bars.close.shift(1) >= vwap.vwap_prior.shift(1)))
        for family, mask in flags.items():
            last = None
            for signal in bars.index[mask.fillna(False)]:
                if last is not None and signal - last < pd.Timedelta(minutes=60):
                    continue
                last = signal
                counts[family]["detected"] += 1
                window = evaluate_forward(bars, pd.DatetimeIndex([signal]), horizons=HORIZONS)
                for row in window.itertuples():
                    if row.complete:
                        counts[family][f"complete_{row.horizon_min}m"] += 1
                        result.append({"family": family, "instrument": rows.instrument_id.iloc[0],
                                       "contract_id": contract, "horizon": int(row.horizon_min),
                                       "signal_utc": signal.isoformat(),
                                       "known_at_utc": (signal + pd.Timedelta(minutes=1)).isoformat(),
                                       "forward_points": float(row.forward_points),
                                       "mfe_points": float(row.mfe_points),
                                       "mae_points": float(row.mae_points)})
    return result, counts


def build_observed_bundle(staged_paths: list[str | Path]) -> dict:
    if not staged_paths:
        raise ValueError("No staged observed futures files provided")
    frames = []
    sources = []
    identities: set[tuple[str, str]] = set()
    for path in staged_paths:
        frame, quality = load_staged(path)
        symbol = quality["structural_validation"]["instrument"]
        for contract in frame.contract_id.unique():
            key = (symbol, str(contract))
            if key in identities:
                raise ValueError("Duplicate contract across source files; merge/audit upstream")
            identities.add(key)
        frames.append(frame)
        sources.append({"instrument": symbol, "source": quality["source_name"],
                        "input_sha256": quality["input_sha256"],
                        "staged_sha256": quality["content_sha256"],
                        "dataset_fingerprint": quality["dataset_fingerprint"],
                        "rows": len(frame), "contracts": sorted(frame.contract_id.unique().tolist()),
                        "observed_gaps": len(quality["structural_validation"].get("observed_gaps", [])),
                        "calendar_verified": False, "contract_provenance_verified": False})
    observed = pd.concat(frames, ignore_index=True)
    observed = validate_bars(observed)
    records, counters = _events(observed)
    metrics = {}
    for family in FAMILIES:
        metrics[family] = {}
        for h in HORIZONS:
            subset = [r for r in records if r["family"] == family and r["horizon"] == h]
            metrics[family][str(h)] = {
                "complete_events": len(subset),
                "mean_forward_points": sum(e["forward_points"] for e in subset) / len(subset) if subset else None,
                "mean_mfe_points": sum(e["mfe_points"] for e in subset) / len(subset) if subset else None,
                "mean_mae_points": sum(e["mae_points"] for e in subset) / len(subset) if subset else None,
                "inference": "WITHHELD — source provenance, calendar and holdout unverified",
            }
    dataset_id = dataset_fingerprint(observed)
    fingerprint = json.dumps({"dataset": dataset_id, "families": FAMILIES, "horizons": HORIZONS,
                              "algorithm": "observed-release09-v1"}, sort_keys=True)
    run_id = hashlib.sha256(fingerprint.encode()).hexdigest()
    return {"schema_version": "0.9", "classification": "OBSERVED FUTURES — UNVERIFIED SOURCE",
            "status": "STAGED_UNVERIFIED", "edge_validated": False,
            "data_is_synthetic": False, "run_id": run_id, "dataset_id": dataset_id,
            "row_count": len(observed), "sources": sources, "event_counts": counters,
            "descriptive_forward": metrics,
            "governance": {"holdout_scored": False, "holdout_validated": False,
                           "trading_edge_validation_allowed": False,
                           "execution_simulated": False},
            "limitations": [
                "Structurally valid user-supplied futures data is not CME provenance verification",
                "Trading calendar/maintenance windows and contract roll policies are not certified",
                "Raw gaps are not forward-filled; only complete single-contract horizons are measured",
                "Events are descriptive screens, not independent or multiple-testing-corrected samples",
                "No sealed holdout, broker-cost calibration or real fill validation was conducted",
            ]}


def export_observed(staged_paths: list[str | Path], output: str | Path,
                    *, publication_approved: bool = False) -> dict:
    destination = Path(output)
    if "public" in destination.parts and not publication_approved:
        raise ValueError("Public research export requires explicit --publication-approved")
    bundle = build_observed_bundle(staged_paths)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(json.dumps(bundle, allow_nan=False, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    os.replace(temporary, destination)
    return bundle



def append_registry(bundle: dict, destination: str | Path) -> bool:
    """Idempotent private experiment ledger; never silently reset corruption."""
    registry = Path(destination)
    if "public" in registry.parts:
        raise ValueError("Experiment registry must remain private")
    record = {"schema_version": "0.9", "run_id": bundle["run_id"],
              "dataset_id": bundle["dataset_id"], "status": bundle["status"],
              "edge_validated": False,
              "source_fingerprints": [x["dataset_fingerprint"] for x in bundle["sources"]]}
    if registry.exists():
        for line in registry.read_text(encoding="utf-8").splitlines():
            prior = json.loads(line)
            if not isinstance(prior, dict) or not prior.get("run_id") or not prior.get("dataset_id"):
                raise ValueError("Corrupt 0.9 experiment registry")
            if prior["run_id"] == record["run_id"]:
                if prior != record:
                    raise ValueError("Conflicting run ID in registry")
                return False
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return True
