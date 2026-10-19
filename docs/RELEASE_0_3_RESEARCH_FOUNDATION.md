# QUANT Release 0.3 — Research foundation (pre-data)

## Scope and status
This branch is a **provider-neutral research foundation**. It does not pretend synthetic fixtures are genuine NQ history. The live website continues to show its separate Dukascopy index CFD dataset. No automatic broker actions.

## Components
- `research_contract.validate_bars`: canonical source + venue + market type + contract identity + UTC timestamps + validated OHLCV; duplicate bar-key rejection.
- `research_contract.save_curated`: Parquet export with fingerprints and file SHA-256, no CFD/futures identity merge.
- `futures_csv.validate_contract_csv`: import safety gate for genuine per-contract NQ/ES CSV; source authenticity/license remains independently required.
- `futures_research.session_context`: point-in-time London 03:00–08:30 NY session levels; incomplete windows return unavailable levels.
- `futures_research.evaluate_forward`: exact next-minute-entry 15/30/60-minute returns, MFE/MAE, no gap or contract-roll crossing.
- `synthetic_scenarios.known_path`: deterministic engineered OHLC bar patterns, used *only* for testing.
- `sandbox_execution.simulate_long`: long-only, single-position prototype with costs, downside gap-fill and pessimistic/optimistic/unresolved same-bar stop/target bounds.
- `experiment_audit.record_experiment`: append-only JSONL with source provenance, status restrictions and stable run fingerprint.

## Acceptance gates
- Run `python -m pytest -q`, `python scripts/verify_artifacts.py`, `npm ci && npm run build`.
- Check no real futures history is claimed, no license assumed, no synthetic backtest promoted to a trading edge.
- Before evaluating real NQ data, add instrument-specific holidays, contract roll policy, data lineage, source-provided bar semantic mapping and official CME market-calendar verification.
- Before strategy validation, add separate order-side handling, latency/spread/cost scenarios, walk-forward/holdout protections, and statistical multiple-testing corrections. Current fill prototype is **not** a live-grade execution engine.

## Adapters to build after obtaining credentials
Provider-specific raw inputs -> strict canonical schema -> immutable dataset/version -> feature matrix -> event calculations -> simulation -> validation -> signed experiment report. Do not alter research core for one vendor.

## Safety
Generated fixtures have no market expectancy, and long-only simulation is a bounded unit-tested prototype. Never expose trade execution APIs or deploy research output as automated financial advice.
