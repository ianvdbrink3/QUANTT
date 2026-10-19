# QUANT 0.6 — bidirectional OHLC execution prototype

Supports long/short stop-loss and take-profit, conservative gap-through-stop fills, explicit uncertain stop/target collisions, execution cost scenarios, hard contract caps, commissions, and equity drawdown. All calculations are performed on synthetic fixtures in tests.

**Not live-grade:** No real order-book, exchange queue, limit-fill priority, latency, partial fills, margin model, position concurrency, trading-calendar checks, observed bid/ask or contract-native licensed historical data. Spread/slippage are explicit assumptions. No broker order routing exists.

Run `python -m pytest -q tests/test_futures_execution.py`. This module is available for future connection to the research orchestration pipeline after policy tests and an explicit architecture review.
