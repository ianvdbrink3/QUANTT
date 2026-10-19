# Release 0.8 — Research Pipeline 2.0 / Command Center

The source of all numerical synthetic research results is `src/quantlab/release08.py`, which invokes the existing universal canonical contract, structural quality gate, point-in-time London session levels and VWAP, opening range, exact 15/30/60-minute MFE/MAE/forward outcome engine, 0.6 bidirectional execution simulator, and 0.7 purging/embargo/experiment-family governance.

Generate the public, **non-licensed synthetic-only** data:

```bash
python scripts/export_research08.py --out public/data/research08.json --bars 1700
python -m pytest -q
npm run build
```

Data includes synthetic NQ/ES runs and separate **metadata only** for March 19, 2025 Dukascopy index CFD. The CFD sample is *not* combined with synthetic executions; the CME futures adapter has no observed data yet. Synthetic events cannot prove a trading edge, and the experimental holdout remains sealed/unscored. P-values are intentionally null, not fabricated from artificial price paths. Session coverage and event counts can be zero if not enough observed minutes; the UI must show this transparently.

The static public reference is a reproducible **snapshot**, not a live computation engine. A protected release workflow regenerates it with Python and makes a Git commit for Vercel. Real licensed historical data remains private; never place it under `public/` or Git.
