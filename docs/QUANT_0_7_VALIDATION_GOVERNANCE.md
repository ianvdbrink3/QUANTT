# QUANT 0.7 — Validation and deterministic orchestration protocol

Adds:
- Predeclared research family and a maximum trial count.
- Event-interval purging and evaluation embargo in UTC.
- Immutable, identity-specific sealed holdout metadata.
- Simple outlier/tail fragility screen with conservative conclusions.
- Seven distinct logical research/audit roles with no autonomous LLM or broker order execution.

This is an **experimental governance layer**, not a production implementation of an independently sealed holdout or regulator-grade research audit. The lock prevents accidental overwriting of identity but a user with filesystem write permissions could deliberately delete it. Purging is for event intervals explicitly supplied by the research runner; observation-based chronological splits remain separate. No synthetic results may demonstrate a real market edge.

Run `python -m pytest -q tests/test_validation_governance.py`.
