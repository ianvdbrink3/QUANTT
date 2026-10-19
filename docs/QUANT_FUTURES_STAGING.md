# Contract-native 1-minute futures CSV staging

A safe preparatory adapter for later licensed NQ/ES futures exports. It accepts exactly:
`timestamp_utc,contract_id,open,high,low,close,volume`.

Example (run only for data you have the rights to use):

```bash
python scripts/stage_futures_csv.py --input ./private/NQZ26.csv --instrument NQ --source my-verified-provider --out ./private/staged/NQZ26.parquet
```

Outputs a canonical Parquet file and `.quality.json` sidecar with source hash, per-contract counts, observed gap list, structural checks and **UNVERIFIED** source trust labels. Raw vendor data should remain outside public Git and Next.js `public/`.

This staging adapter **cannot** validate the legal license, real CME provenance, exchange holiday/halts, rollover policy or vendor timing conventions. It does not automatically attach data to research or claim to have solved access to 2024–2026 futures history. Future provider-specific adapters must independently certify those properties before statistical results can be published.

Run `python -m pytest -q tests/test_futures_import.py`.
