# QUANT 0.5 — first integrated CLI pipeline

Run from repository root (after installing requirements):

```bash
python scripts/run_synthetic_research.py --config configs/synthetic_research.yaml --out ./research_runs/synthetic_demo
python -m pytest -q
python scripts/verify_artifacts.py
npm run build
```

Outputs under `research_runs/synthetic_demo/`: `result.json`, `report.md`, append-only/idempotent `registry.jsonl`. Failed runs write `failures.jsonl` and raise a nonzero process exit. The same seed, config and code_ref generate a reproducible **run_id**. Reports explicitly disclose synthetic provenance, incomplete external market data verification, and withholding of empirical edge claims.

This is an **integration foundation, not the complete releases 0.5–0.7**. The CLI deliberately only allows `synthetic_fixture` input. Futures adapters, authoritative CME calendars and roll policies, contract-native dataset quality certification, independent holdout enforcement, time-to-target, short accounting and multi-agent orchestration remain future work. Unreconciled gaps fail closed; deterministic fixture P&L is neither historical performance nor a real strategy expectation.
