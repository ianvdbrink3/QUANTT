# QUANTT · Quant Research Lab

A reproducible Python market-data pipeline and a dark Next.js research dashboard. The web app serves versioned static data directly from Git; it needs no external database, credentials, or Python runtime on Vercel.

## Actual delivery status — 18 October 2026

**Historical ingestion is incomplete because source access is blocked.** The repository was empty when work began; no v0.2 implementation, existing hypotheses, cost profiles, or historical dataset was present. This implementation and its three hypotheses were created from scratch.

The real Dukascopy BID file for **19 March 2025** was obtained and decoded: **1,440 source records, 1,329 validated minute bars, 111 zero-activity flat bars excluded, zero price anomalies**. The target interval is **2024-01-01 through 2026-10-18 exclusive** (1,021 UTC days). No synthetic market history or fabricated backtest results are published. The dashboard prominently displays the coverage shortfall.

The old datafeed returns HTTP 429 with a link to the [official bulk export guide](https://www.dukascopy.com/wiki/en/development/data-export/). The newer public API returned an AWS WAF browser challenge. The documented bulk route is an AWS Requester Pays S3 bucket, requiring the user's own AWS access and billing. No AWS profile was available. Credentials are never stored in this repository. A browser export was also attempted; no usable historical dataset was obtained through that route.

**This instrument is a Dukascopy Nasdaq-related index CFD, not CME NQ futures.** Source activity is not exchange-traded contract volume. Futures rolls, CME session calendars, contract multipliers, and actual broker execution costs must not be inferred from it. ES is displayed as not ingested.

## Local use

Node 22+ and Python 3.11+ are required. The verified environment used Python 3.14 and Node 22. Dependencies are locked in `package-lock.json` and `requirements-lock.txt`.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
npm ci
npm run build
npm run start
```

Open the Local URL printed by Next.js. Development mode: `npm run dev`. Production builds use the supported Webpack backend because this desktop sandbox restricts Turbopack's child-process port binding. The browser bundle contains no raw minute history.

## Resume ingestion

The one-command runner first downloads and checks March 2025, then processes the full requested interval. It returns nonzero when coverage is incomplete.

```sh
.venv/bin/python scripts/run_pipeline.py --start 2024-01-01 --end 2026-10-18 --workers 4
```

Individual stages, useful for resuming a specific batch after source access is restored:

```sh
.venv/bin/python scripts/dukascopy_ingest.py --start 2025-03-01 --end 2025-04-01 --workers 4
.venv/bin/python scripts/dukascopy_ingest.py --start 2024-01-01 --end 2025-01-01 --workers 4
.venv/bin/python scripts/dukascopy_ingest.py --start 2025-01-01 --end 2026-01-01 --workers 4
.venv/bin/python scripts/dukascopy_ingest.py --start 2026-01-01 --end 2026-10-18 --workers 4
.venv/bin/python scripts/build_research.py --start 2024-01-01 --end 2026-10-18
.venv/bin/python scripts/verify_artifacts.py
```

`--end` is an exclusive UTC date. Its default is the current UTC day, excluding an incomplete day. The downloader supports `--transport curl` (default) or `--transport requests`, bounded concurrency, exponential backoff with jitter, atomic cache writes, re-download of corrupt cache files, and a bulk circuit breaker on rate limiting/challenge responses. A 404 is unavailable data, never silently declared a closed market. Source failures and every attempted day are retained in `data/download_manifest.jsonl`; successful cached days can be reprocessed without a network request. Imported cache files must use the documented **daily M1 candle** layout, not hourly or daily tick `.bi5` formats.

The March gate checks all 31 UTC day partitions, observed 09:30 New York/08:00 London bars on both sides of each DST transition, and price anomalies. Weekends are downloaded and audited rather than blindly discarded; Sunday evening may contain real CFD activity. `march_validation.json` distinguishes tested time-zone arithmetic from missing real-data observations.

## Pipeline and audit model

```text
Dukascopy daily BID M1 → validated .bi5 cache → flagged daily Parquet partitions
    → curated minute Parquet + data quality report
    → session / distribution / autocorrelation / fixed hypothesis screens
    → compact annual JSON shards + immutable experiment registry
    → Next.js pages / interactive charts → Vercel Git deployment
```

- Binary record: big-endian unsigned seconds, open, close, low, high, float32 volume (`>5If`). Month directory is zero-based. Raw integer prices are divided by 1,000 for this instrument. Timestamps identify UTC bar opens. Initial scale check: raw 19,495,332 → 19,495.332 index points on 19 March 2025.
- Normalization validates finite prices/activity, price bounds, OHLC ordering, and strictly increasing unique minute offsets. The curated Parquet retains excluded bars with `is_market_open=False`, `is_flat_closed`, and `is_price_anomaly`.
- Closed flat rule: `volume == 0 AND open == high == low == close`. A zero-activity moving bar or an active flat-price bar is retained. No forward filling.
- Quality JSON includes observed span, annual/monthly coverage, missing weekday candidates, failures, unattempted days, anomalies, duplicates, source hashes, and DST probes. Weekday coverage is a diagnostic, **not a validated exchange calendar**; holidays are explicitly unreconciled.
- Intraday returns require exact elapsed time. Multi-minute distribution bars need complete M1 coverage on both sides of the return. Partial bars remain visible with `minute_count` in explorer exports. Daily bars use UTC calendar days and do not represent official vendor sessions.
- Hourly profiles use UTC and `America/New_York`. London windows use `Europe/London` independently of US DST. Local research windows are in `configs/sessions.yaml` and can overlap.
- Histograms display the central 99%, disclose excluded tail counts, and compute all moments on the full eligible sample. Return and absolute-return autocorrelations require contiguous underlying minutes.
- Regime labels use previous-day volatility and an expanding median of prior days, with a 20-day warmup; they do not select trades.
- Dataset SHA-256, configuration/code fingerprints, a fixed bootstrap seed, and idempotent run IDs allow audit and repeatability. `experiments/registry.jsonl` is append-only; previous and failed/incomplete research is retained.

## Hypotheses and statistical limits

Three rules were specified before the first analysis: NY opening long drift, London opening long drift, and fading the preceding complete hour at NY open. Each trade requires every minute in its fixed 60-minute holding window. Entry is at the next available **known opening price at the specified clock minute**, never at the opening of a bar whose close is needed to form the signal. Missing bars cause trade exclusion, never delayed entry/exit.

`configs/costs.yaml` contains illustrative CFD scenarios: 2 points base and 4 points stress per round trip. These include assumed spread and slippage on both sides; they are **not observed or broker-verified costs**. Results include net point P&L, win rate, daily-trade Sharpe, profit factor, initial-zero-equity maximum drawdown, yearly metrics, and chronological 60/20/20 samples. The final sample has been opened for this fixed descriptive run and is no longer sealed for future tuning.

Uncertainty uses a deterministic 2,000-sample circular five-day moving-block bootstrap of trading-day results. Two-sided mean tests are corrected across all three planned hypotheses with Benjamini–Hochberg. Below 20 day trades, CIs and p-values are withheld. Annualized Sharpe and single-day results are descriptive and unstable. All current hypotheses require more data. No execution validation or independent replication has established a tradable edge.

## Dashboard

- `/`: Market explorer with 15m, 1h, 1D switching, UTC date bounds, year presets, price chart/brush, full-history close drawdown, rolling volatility, and full-resolution JSON downloads. Large ranges sample at most about 1,400 closes for rendering only; exported OHLC stays complete. Chart timestamps are UTC; the latest-observation display can switch to New York time.
- `/quality`: monthly coverage heatmap, year summary, manifest outcomes, explicit missing weekday candidates, exclusions, and March DST probes.
- `/sessions`: hourly volatility/range/return/activity, local session comparison, distributions at four frequencies, return/absolute-return ACF, and causal regime warmup status.
- `/experiments`: searchable/filterable registry, fixed rule details, base/stress costs, chronological/yearly tables, statistical limits, and cumulative net points.

The frontend loads only the selected timeframe's annual JSON shards, never raw `.bi5` or minute Parquet. Heavy chart code is dynamically loaded. Annual files include row counts and SHA-256 checksums in `public/data/index.json`. No ingestion runs in a Vercel request or build.

## Verification

```sh
.venv/bin/python -m pytest -q
.venv/bin/python scripts/verify_artifacts.py
npm run typecheck
npm run build
```

Python tests cover binary decoding, scale rejection, flat filtering, malformed data, DST mismatches, gap-safe returns, causal trade direction, incomplete windows, costs, drawdown, bootstrap reproducibility, multiplicity, registry idempotency, retry backoff, corrupt downloads, and source-block circuit behavior. Artifact verification recomputes every exported OHLC row against the curated source and verifies all SHA-256 hashes. CI runs these checks plus the production build on pushes and pull requests without fetching external market data. See `docs/VERIFICATION.md` for actual run evidence and remaining blockers.

## Vercel

**Live deployment verified on 19 October 2026:** [quantt-eight.vercel.app](https://quantt-eight.vercel.app). The user imported the GitHub repository into Vercel. All four dashboard routes and seven data exports returned HTTP 200; live data matched the locally verified files and shard hashes. The 15m timeframe switch rendered 89 observed bars and the browser reported no warnings/errors. The original connector project-creation restriction no longer prevents serving the app; historical ingestion is still incomplete.

The live project imports [ianvdbrink3/QUANTT](https://github.com/ianvdbrink3/QUANTT) as a Next.js project, repository root, production branch `main`. `vercel.json` uses `npm ci` and `npm run build`. No environment variables or database are required. Git integration then redeploys exported data and source changes on every push to `main`. No raw `.bi5` files, virtual environments, dependencies, tokens, or build directories are committed.

The deployment does not make ingestion complete: the visible coverage warning stays until source data is actually obtained and exports are regenerated. To replace the CFD with NQ/ES futures, add a contract-native licensed source adapter, exchange holiday/half-day calendar and explicit rollover/cost models before transferring research conclusions.
