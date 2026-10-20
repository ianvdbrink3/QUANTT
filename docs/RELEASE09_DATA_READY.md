# QUANT 0.9 — Data-Ready Observed Futures

This release connects the existing strict futures CSV import to a separate
observed-data research path. The synthetic Release 0.8 path is unchanged.

## Import licensed user-provided contract-native futures data

Run from the repository root after installing requirements-lock.txt:

    python scripts/export_research09.py --csv NQ=/secure/NQZ26_minute.csv --csv ES=/secure/ESZ26_minute.csv --source vendor-name --stage-dir artifacts/observed-stage --out artifacts/research09.json

Or reuse already staged files and their quality sidecars:

    python scripts/export_research09.py --staged artifacts/observed-stage/NQ.parquet --staged artifacts/observed-stage/ES.parquet --out artifacts/research09.json

CSV fields: timestamp_utc (one-minute bar-open UTC), contract_id, open,
high, low, close and volume. Specify actual contract identifiers (e.g. NQZ26),
not a continuous or synthetic ticker. The existing importer checks ordering,
tick alignment, OHLC relationships, nonnegative integer volume and records
gaps; it does not fill gaps or authenticate an exchange license.

The observed runner verifies the staged Parquet SHA-256, dataset fingerprint,
source metadata, venue, row/contract counts and matching importer sidecar.
It refuses other market types, unaudited files and repeated contract IDs
across source files. The separate research JSON contains aggregates only;
raw minute history must not be uploaded to GitHub or Vercel.

## What the descriptive pipeline computes

- NY 09:30–09:45 ET opening-range breakout with full prior range
- London 03:00–08:30 ET high sweep in NY morning when full London range exists
- Lagged, prior-bar VWAP mean-reversion crosses in NY morning
- Exact next-bar-open forward return and MFE/MAE at 15, 30 and 60 minutes
- Only fully covered same-contract forward paths count

No broker fills, multiple-testing correction, walk-forward or independently
sealed holdout are claimed. All results explicitly remain
STAGED_UNVERIFIED with edge_validated=false; missing values stay null.
A structurally valid CSV is not proof of CME-origin authenticity.

## Publication and dashboard

Output defaults to private artifacts/research09.json. A publication action
is separate and requires an explicit flag:

    python scripts/export_research09.py --staged artifacts/observed-stage/NQ.parquet --out public/data/research09.json --publication-approved

Review your vendor license before publishing aggregates or provenance metadata.
Do not commit the raw CSV or Parquet. The /research/observed route initially
shows AWAITING_INPUT with zero observations, not synthetic fallback metrics.
Its content updates only after a reviewed aggregate report is published,
committed and deployed.

## Tests

    PYTHONPATH=src python -m pytest -q tests/test_observed_release09.py tests/test_futures_import.py

Tests use fabricated fixture prices exclusively and test controls for
checksum tampering, provenance spoofing, missing bars, multi-instrument
separation, deterministic results and publication consent. They provide
no historical market evidence. This PR makes no production changes.
