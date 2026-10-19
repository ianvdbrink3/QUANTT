# CME futures contract-native CSV intake (experimental)

This is an **additional safety gate**, not an assertion that QUANTT already has historical NQ data, a completed NQ backtest, or a licensed datafeed. Existing Dukascopy CFD observations remain segregated.

Expected CSV columns:
```csv
timestamp_utc,contract_id,open,high,low,close,volume
2026-10-19T13:30:00Z,NQZ26,20000.00,20001.00,19999.75,20000.25,125
```

Run:
```bash
PYTHONPATH=src python -c "from quantlab.futures_csv import validate_contract_csv; import json; print(json.dumps(validate_contract_csv('path/to/NQ.csv'),indent=2))"
python -m pytest -q tests/test_futures_csv.py
```

Strict UTC bar-open timestamps, actual per-contract IDs, CME tick alignment, positive ordered OHLC, nonnegative integer volume and strictly increasing timestamps **within each contract** are required. Gaps are reported but not filled or automatically called exchange closures. No roll adjustment is assumed. This validator does not attest whether a vendor supplies genuine exchange volume, correct NQ trading contracts or license rights.

**Next integration gate:** once licensed contract-native NQ minute exports are available, add source fingerprinting, authoritative CME holiday and halt schedule, explicit contract-month/roll policy, immutable per-contract Parquet partitions, acceptance snapshots, then wire into the point-in-time session research pipeline. The current Next.js dashboard still reads its existing CFD research exports; this gate does not relabel them as futures.

Local isolated regression run prior to publication: 8 tests passed using Python standard library. Full repository CI and Vercel are not yet asserted for this branch.
