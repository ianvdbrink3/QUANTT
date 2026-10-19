# QUANT 0.4 — Fifteen source-neutral research gates

Implementation lives in `src/quantlab/research_validation.py` and regression tests in `tests/test_research_validation.py`.

1. Market-specific contract value and tick validation.
2. Canonical UTC minute-index validation.
3. Observed, per-contract gap accounting.
4. New York calendar-date projection, explicitly **not** the CME trade date.
5. Configurable New York same-day session window selection.
6. Fully observed opening-range calculations, with explicit `known_at_utc`.
7. Prior-bar VWAP estimates without current-bar leakage.
8. Threshold event timestamps on completed observations.
9. Regime/time-matched comparison with a baseline.
10. Chronological train/validation/holdout partition with observation-count embargo.
11. Reproducible block bootstrap of outcomes.
12. Benjamini-Hochberg false-discovery-rate adjustment.
13. Explicit, configurable cost scenarios.
14. Stable provenance/parameter manifest and instrument definition.
15. Automated deterministic regression testing and CI gating.

**Important limits:** These primitives do not yet constitute a complete contract-native production data adapter, an official CME calendar, sealed holdout governance, purged event-based cross-validation, realistic live broker fills, a short-selling backtester, or statistically validated edge discovery. A chronological holdout is marked sealed in metadata only; enforcement belongs in a later immutable run registry. The opening range currently requires complete minute bars for its opening interval, but relies on upstream source-integrity validation.

Run `python -m pytest -q`, `python scripts/verify_artifacts.py`, and `npm ci && npm run build`. No real NQ statistics are claimed here. The existing Dukascopy CFD dashboard remains segregated.
