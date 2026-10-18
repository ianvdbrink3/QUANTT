# Verification evidence

Run started 18 October 2026 (UTC), completed after local midnight in Europe/Amsterdam.

## Executed successfully

- Python unit suite: **31 passed**. Covers decoding, price scale, flat filtering, invalid records, US/EU DST divergence, missing bars, causal direction, costs, initial-zero-equity drawdown, bootstrap, multiple testing, registry idempotency, transient retries, corruption, rate-limit circuit breaking, and stopping after consecutive failed batches.
- `scripts/verify_artifacts.py`: **3 web shards verified**, every OHLC row reconciled to curated minute data, SHA-256 hashes checked, quality report equality checked.
- `npm run typecheck`: passed.
- `npm run build`: passed with Next.js 16.4.2 / Webpack, all four pages statically generated, no compilation warnings/errors. Turbopack could not bind a child-process port in this desktop sandbox; the project therefore uses the supported Webpack build option.
- Local production server: HTTP **200** for `/` and `/data/quality.json`.
- Browser: price chart rendered; 1h → 15m switch changed 23 to 89 observed OHLC bars. Coverage heatmap opened March detail: 1,329 validated bars, 111 flats. Session page rendered hourly/session metrics, distributions and autocorrelations. Experiment search narrowed to London; selecting it updated the rule details. Base → stress cost switch changed round-trip costs from 2 to 4 points and NY drift net points from 56.40 to 54.40. Small-sample p-values and CIs were withheld.

## Source and coverage evidence

Real file obtained:

`https://datafeed.dukascopy.com/datafeed/USATECHIDXUSD/2025/02/19/BID_candles_min_1.bi5`

Decoded 1,440 daily M1 records; 1,329 validated bars, 111 closed flat bars, zero price anomalies. Observed span: 2025-03-19 00:00–23:59 UTC. No synthetic price history is present.

The original March download using Python requests exhausted retries with connection/TLS handshake timeouts. Direct old-datafeed requests then returned **HTTP 429**, including:

```json
{"error":"Too Many Requests. For instructions, see: https://www.dukascopy.com/wiki/en/development/data-export/"}
```

The current public API returned **HTTP 202**, `x-amzn-waf-action: challenge`. Browser historical export was inspected and a day export attempted, but no usable additional dataset was obtained. No challenge was bypassed, no credentials were requested or saved, and no paid bulk download was initiated.

The official bulk guide requires AWS Requester Pays access. No configured AWS profile was available in this environment. Full-range ingest with the improved downloader stopped after the first blocked batch. The single-command March validation remains failed/incomplete. Its report distinguishes correct UTC offset arithmetic from absent real source observations.

Target interval: 2024-01-01 inclusive to 2026-10-18 exclusive, 1,021 UTC days. There are **729 missing weekday candidates** including unreconciled holidays. The complete dataset, observed-data DST validation across March, full-history analysis, and any trading-edge claims therefore remain **unfulfilled**. All three hypotheses are `REQUIRES_MORE_DATA`.

## Operational notes

- The repository was empty; v0.2 was not available. New hypotheses and illustrative CFD cost scenarios are disclosed in README/configs.
- These are Dukascopy index CFD BID quotes, not CME NQ contracts or exchange contract volume.
- Package locks, raw exclusion rules, code/config fingerprints, full manifest history, curated Parquet and versioned JSON exports are included.
- CI repeats tests, artifact verification, dependency installation and the Next.js production build without external data ingestion.
- The local Vercel CLI token was invalid. The connected Vercel integration is used for project/deployment setup where available. Never interpret a successful local build as proof of a live deployment.

## Publication evidence

- Published through the authenticated GitHub connector because the local Git/CLI keyring token was invalid. Remote source tree `823eefcdffe22ee8bee9285ae5260b7938564eb0` exactly matched the locally tested tree.
- Initial complete-source commit on `main`: `faa5fa546fd462d9c91c1d5194094dd85db16f69`. Local and remote file trees were compared with no differences.
- Vercel project creation for `quantt`, repository `ianvdbrink3/QUANTT`, team `team_9hWiWgRgntKUEwASNdTdpExK`, returned **403 forbidden: no permission to create the project**. The existing CLI token was invalid, and the browser was not signed in. No Vercel project or live deployment is claimed.
- Required external remediation: authorized Dukascopy historical-data access and Vercel project-creation/import access. No secrets should be pasted into the chat or committed.
