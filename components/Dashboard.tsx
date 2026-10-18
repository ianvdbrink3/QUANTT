"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowDownToLine,
  ArrowUpRight,
  BarChart3,
  Check,
  ChevronRight,
  CircleDot,
  Database,
  FlaskConical,
  GitBranch,
  Layers3,
  Menu,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Waves,
  X,
} from "lucide-react";
import type {
  Analytics,
  Bar,
  Experiment,
  LabData,
  Metrics,
  Profile,
} from "@/lib/types";
const Chart = dynamic(() => import("./Charts"), {
  ssr: false,
  loading: () => (
    <div className="chart-empty" style={{ height: 280 }}>
      Loading chart…
    </div>
  ),
});
type View = "explorer" | "quality" | "sessions" | "experiments";
const nav = [
  { id: "explorer", href: "/", label: "Market explorer", icon: BarChart3 },
  { id: "quality", href: "/quality", label: "Data quality", icon: ShieldCheck },
  {
    id: "sessions",
    href: "/sessions",
    label: "Session analytics",
    icon: Waves,
  },
  {
    id: "experiments",
    href: "/experiments",
    label: "Experiments",
    icon: FlaskConical,
  },
];
const fmt = (v: number | null | undefined, d = 2) =>
  v == null
    ? "—"
    : v.toLocaleString("en-US", {
        maximumFractionDigits: d,
        minimumFractionDigits: d,
      });
const count = (v: number) => v.toLocaleString("en-US");
function Stat({
  label,
  value,
  note,
  accent = false,
}: {
  label: string;
  value: string;
  note: string;
  accent?: boolean;
}) {
  return (
    <div className="stat">
      <div className="eyebrow">{label}</div>
      <div className={`stat-value ${accent ? "blue" : ""}`}>{value}</div>
      <div className="stat-note">{note}</div>
    </div>
  );
}
function Panel({
  title,
  sub,
  action,
  children,
  className = "",
}: {
  title: string;
  sub?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-head">
        <div>
          <h2>{title}</h2>
          {sub && <p>{sub}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
function Badge({
  children,
  warn = false,
}: {
  children: React.ReactNode;
  warn?: boolean;
}) {
  return (
    <span className={`badge ${warn ? "amber" : ""}`}>
      <span className="status-dot" />
      {children}
    </span>
  );
}

export default function Dashboard({
  view,
  data,
}: {
  view: View;
  data: LabData;
}) {
  const [mobile, setMobile] = useState(false);
  const q = data.quality;
  const active = nav.find((n) => n.id === view)!;
  return (
    <div className="workspace">
      <a className="skip" href="#main">
        Skip to content
      </a>
      <aside className={`sidebar ${mobile ? "open" : ""}`}>
        <Link className="brand" href="/">
          <span className="brand-icon">
            <Activity size={22} />
          </span>
          QUANTT<span className="brand-small">LAB</span>
        </Link>
        <div className="workspace-label">RESEARCH WORKSPACE</div>
        <nav aria-label="Main navigation">
          {nav.map((n) => (
            <Link
              onClick={() => setMobile(false)}
              aria-current={view === n.id ? "page" : undefined}
              className={`nav-item ${view === n.id ? "active" : ""}`}
              href={n.href}
              key={n.id}
            >
              <n.icon size={18} />
              {n.label}
              {view === n.id && <span className="nav-indicator" />}
            </Link>
          ))}
        </nav>
        <div className="sidebar-section">
          <div className="workspace-label">DATA UNIVERSE</div>
          <div className="universe">
            <span className="instrument-icon">N</span>
            <div>
              <strong>US 100 Tech</strong>
              <small>USATECHIDXUSD · CFD</small>
            </div>
            <CircleDot size={13} className="blue" />
          </div>
          <div className="universe disabled">
            <span className="instrument-icon">S</span>
            <div>
              <strong>S&P 500</strong>
              <small>ES · Not ingested</small>
            </div>
          </div>
        </div>
        <div className="sidebar-bottom">
          <div className="source-card">
            <Database size={16} />
            <span>
              Dukascopy<small>BID · 1-minute source</small>
            </span>
            <Badge warn={q.ingestion_status !== "complete_downloads"}>
              {q.ingestion_status === "complete_downloads"
                ? "Fetched"
                : "Partial"}
            </Badge>
          </div>
          <a
            className="repo-link"
            href="https://github.com/ianvdbrink3/QUANTT"
            target="_blank"
            rel="noreferrer"
          >
            <GitBranch size={15} />
            Research repository
            <ArrowUpRight size={14} />
          </a>
          <div className="profile">
            <span>IQ</span>
            <div>
              Quant Research<small>Independent workspace</small>
            </div>
            <span className="profile-dot" />
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              onClick={() => setMobile(!mobile)}
              aria-label="Toggle navigation"
            >
              {mobile ? <X size={18} /> : <Menu size={18} />}
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>{active.label}</strong>
          </div>
          <div className="topbar-right">
            <span className="offline-dot" />
            Historical research
            <span className="top-separator" />
            <span className="mono">v0.1</span>
          </div>
        </header>
        <main id="main">
          <div className="page-header">
            <div>
              <div className="eyebrow blue">
                MULTI-MARKET QUANT RESEARCH LAB
              </div>
              <h1>{active.label}</h1>
              <p>
                {view === "explorer"
                  ? "Explore price behavior. Understand the structure behind the moves."
                  : view === "quality"
                    ? "Every observation accounted for. Every gap made visible."
                    : view === "sessions"
                      ? "Find the rhythm of the market, across sessions and time zones."
                      : "From a research question to a reproducible statistical test."}
              </p>
            </div>
            <a
              className="button secondary"
              href={
                view === "quality"
                  ? "/data/quality.json"
                  : view === "experiments"
                    ? "/data/experiments.json"
                    : view === "sessions"
                      ? "/data/analytics.json"
                      : "/data/index.json"
              }
              download
            >
              <ArrowDownToLine size={15} />
              Export {view === "explorer" ? "manifest" : "report"}
            </a>
          </div>
          {q.ingestion_status !== "complete_downloads" && (
            <div className="notice" role="status">
              <span className="notice-icon">!</span>
              <div>
                <strong>Historical coverage is incomplete</strong>
                <span>
                  {count(q.observed_days)} observed UTC day
                  {q.observed_days === 1 ? "" : "s"} · Target{" "}
                  {q.requested_start} → {q.requested_end_exclusive} (exclusive).
                  Source access blocked; results only describe downloaded
                  observations.
                </span>
              </div>
              <Link href="/quality">
                View coverage
                <ArrowUpRight size={14} />
              </Link>
            </div>
          )}
          {view === "explorer" ? (
            <Explorer data={data} />
          ) : view === "quality" ? (
            <Quality data={data} />
          ) : view === "sessions" ? (
            <Sessions analytics={data.analytics} />
          ) : (
            <Experiments experiments={data.experiments} />
          )}
          <footer>
            <span>
              <span className="status-dot" />
              Real observations · Auditable research
            </span>
            <span>
              Dukascopy index CFD · No validated trading edge ·{" "}
              <a href="/data/index.json">
                Dataset {q.data_version.slice(0, 8)}
              </a>
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}

function Explorer({ data }: { data: LabData }) {
  const q = data.quality;
  const [tf, setTf] = useState("1h");
  const [bars, setBars] = useState<Bar[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [from, setFrom] = useState(q.actual_first.slice(0, 10));
  const [to, setTo] = useState(q.actual_last.slice(0, 10));
  const [zone, setZone] = useState("UTC");
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    setBars([]);
    Promise.all(
      data.index.exports
        .filter((f) => f.timeframe === tf)
        .map(async (f) => {
          const res = await fetch(`/data/${f.file}`, {
            signal: controller.signal,
          });
          if (!res.ok) throw new Error(`Unable to load ${f.file}`);
          return res.json() as Promise<(number | null)[][]>;
        }),
    )
      .then((parts) => {
        if (controller.signal.aborted) return;
        setBars(
          parts
            .flat()
            .map((r) => ({
              time: r[0]!,
              open: r[1]!,
              high: r[2]!,
              low: r[3]!,
              close: r[4]!,
              volume: r[5]!,
              minute_count: r[6]!,
              drawdown_pct: r[7]!,
              rolling_volatility_bps: r[8],
            }))
            .sort((a, b) => a.time - b.time),
        );
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [tf, data.index.exports]);
  const selected = useMemo(
    () =>
      bars.filter(
        (b) =>
          b.time >= Date.parse(from + "T00:00:00Z") / 1000 &&
          b.time < Date.parse(to + "T00:00:00Z") / 1000 + 86400,
      ),
    [bars, from, to],
  );
  const step = Math.max(1, Math.ceil(selected.length / 1400));
  const plot = selected.filter(
    (_, i) => i % step === 0 || i === selected.length - 1,
  );
  const first = selected[0];
  const last = selected.at(-1);
  const change =
    first && last ? (last.close / first.open - 1) * 100 : undefined;
  const maxdd = selected.length
    ? Math.min(...selected.map((b) => b.drawdown_pct))
    : null;
  const dates = useMemo(
    () => data.index.exports.filter((f) => f.timeframe === tf),
    [tf, data.index.exports],
  );
  const preset = (year: string) => {
    if (year === "ALL") {
      setFrom(q.actual_first.slice(0, 10));
      setTo(q.actual_last.slice(0, 10));
    } else {
      setFrom(`${year}-01-01`);
      setTo(`${year}-12-31`);
    }
  };
  return (
    <>
      <div className="stats-grid">
        <Stat
          label="Last observed price"
          value={fmt(last?.close)}
          note={
            last
              ? new Date(last.time * 1000).toLocaleString("en-GB", {
                  timeZone: zone,
                  hour12: false,
                }) + ` ${zone === "UTC" ? "UTC" : "ET"}`
              : "No observations selected"
          }
          accent
        />
        <Stat
          label="Range price change"
          value={
            change == null ? "—" : `${change >= 0 ? "+" : ""}${fmt(change)}%`
          }
          note="First open to final close · price only"
        />
        <Stat
          label="Close drawdown"
          value={maxdd == null ? "—" : `${fmt(maxdd)}%`}
          note="Largest decline vs dataset running close peak"
        />
        <Stat
          label="Validated minute bars"
          value={count(q.validated_bars)}
          note={`${count(q.flat_bars_filtered)} closed-market flats excluded`}
        />
      </div>
      <Panel
        title="US 100 Technical Index"
        sub="USATECHIDXUSD · Dukascopy BID"
        action={
          <div className="chart-head-actions">
            <Badge>Observed data</Badge>
            <div className="segmented" aria-label="Timeframe">
              {["15m", "1h", "1d"].map((t) => (
                <button
                  key={t}
                  aria-pressed={tf === t}
                  className={tf === t ? "selected" : ""}
                  onClick={() => setTf(t)}
                >
                  {t === "1d" ? "1D" : t}
                </button>
              ))}
            </div>
          </div>
        }
      >
        <div className="chart-toolbar">
          <div className="range-buttons">
            {["2024", "2025", "2026", "ALL"].map((y) => (
              <button key={y} onClick={() => preset(y)}>
                {y}
              </button>
            ))}
          </div>
          <div className="date-controls">
            <label>
              From{" "}
              <input
                aria-label="Start date"
                type="date"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
              />
            </label>
            <label>
              To{" "}
              <input
                aria-label="End date"
                type="date"
                value={to}
                onChange={(e) => setTo(e.target.value)}
              />
            </label>
            <select
              aria-label="Display time zone"
              value={zone}
              onChange={(e) => setZone(e.target.value)}
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">New York</option>
            </select>
          </div>
        </div>
        {from > to ? (
          <div className="chart-empty">
            Choose an end date on or after the start date.
          </div>
        ) : error ? (
          <div className="chart-empty" role="alert">
            {error}
            <button
              className="button secondary"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </div>
        ) : loading ? (
          <div className="chart-empty">Loading observed prices…</div>
        ) : (
          <>
            <div className="price-strip">
              <strong>{fmt(last?.close)}</strong>
              <span className={change != null && change < 0 ? "red" : "green"}>
                {change == null
                  ? "—"
                  : `${change >= 0 ? "+" : ""}${fmt(change)}%`}
              </span>
              {last && (
                <span className="ohlc mono">
                  O {fmt(last.open)} <span>H {fmt(last.high)}</span>{" "}
                  <span>L {fmt(last.low)}</span>{" "}
                  <span>C {fmt(last.close)}</span>
                </span>
              )}
            </div>
            <Chart
              data={plot}
              x="time"
              y="close"
              format="time"
              height={330}
              brush
            />
            <div className="chart-caption">
              <span>
                <span className="legend-dot" />
                Close price · {count(selected.length)} OHLC bars
                {step > 1 ? ` · chart displays every ${step}th close` : ""}
              </span>
              <span>
                Chart timestamps in UTC · Missing minutes remain gaps in source
              </span>
            </div>
          </>
        )}
      </Panel>
      <div className="two-column">
        <Panel
          title="Drawdown profile"
          sub="Close-to-peak drawdown · full observed history"
        >
          <Chart
            data={plot}
            x="time"
            y="drawdown_pct"
            color="#ef7d88"
            format="time"
            height={190}
          />
        </Panel>
        <Panel
          title="Rolling volatility"
          sub="20 consecutive complete-bar log returns · basis points"
        >
          <Chart
            data={plot}
            x="time"
            y="rolling_volatility_bps"
            color="#a78bfa"
            format="time"
            height={190}
          />
        </Panel>
      </div>
      <div className="two-column lower-grid">
        <Panel
          title="Data provenance"
          sub="Trace every chart back to its source"
        >
          <div className="detail-rows">
            <div>
              <span>Instrument</span>
              <strong>USATECHIDXUSD · index CFD</strong>
            </div>
            <div>
              <span>Actual coverage</span>
              <strong>
                {q.actual_first.slice(0, 10)} — {q.actual_last.slice(0, 10)}
              </strong>
            </div>
            <div>
              <span>Source frequency</span>
              <strong>1 minute · BID quotes · UTC</strong>
            </div>
            <div>
              <span>Quality</span>
              <Badge warn={q.ingestion_status !== "complete_downloads"}>
                {q.ingestion_status === "complete_downloads"
                  ? "Fetched"
                  : "Incomplete history"}
              </Badge>
            </div>
          </div>
        </Panel>
        <Panel
          title="Research-ready exports"
          sub="Full-resolution OHLC, activity and diagnostics"
        >
          <div className="export-list">
            {dates.map((f) => (
              <a href={`/data/${f.file}`} key={f.file} download>
                <span className="file-icon">
                  <Layers3 size={17} />
                </span>
                <span>
                  <strong>
                    {tf.toUpperCase()} · {f.year}
                  </strong>
                  <small>
                    {count(f.rows)} bars · {fmt(f.bytes / 1024, 1)} KB · JSON
                  </small>
                </span>
                <ArrowDownToLine size={16} />
              </a>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}

function Quality({ data }: { data: LabData }) {
  const q = data.quality;
  const [year, setYear] = useState("2025");
  const [month, setMonth] = useState("");
  const chosen = q.coverage.filter((c) => c.month.startsWith(year));
  const detail = q.coverage.find((c) => c.month === month);
  return (
    <>
      <div className="stats-grid">
        <Stat
          label="Source minute records"
          value={count(q.total_bars)}
          note={`${count(q.observed_days)} observed UTC days`}
        />
        <Stat
          label="Validated market bars"
          value={count(q.validated_bars)}
          note="Used by statistical analysis"
          accent
        />
        <Stat
          label="Filtered flat bars"
          value={count(q.flat_bars_filtered)}
          note="Zero activity and identical OHLC"
        />
        <Stat
          label="Price anomalies"
          value={count(q.price_anomalies)}
          note={`Divisor ${count(q.price_divisor)} · ${count(q.duplicate_bars)} duplicate timestamps`}
        />
      </div>
      <Panel
        title="Historical coverage"
        sub="Observed weekdays / requested weekdays · holidays have not been reconciled"
        action={
          <div className="segmented">
            {["2024", "2025", "2026"].map((y) => (
              <button
                key={y}
                className={year === y ? "selected" : ""}
                onClick={() => {
                  setYear(y);
                  setMonth("");
                }}
              >
                {y}
              </button>
            ))}
          </div>
        }
      >
        <div className="coverage-grid">
          {chosen.map((c) => (
            <button
              key={c.month}
              onClick={() => setMonth(c.month)}
              className={`month-cell ${c.bars ? "has-data" : ""} ${month === c.month ? "focused" : ""}`}
              aria-label={`${c.month}: ${fmt(c.weekday_coverage_pct, 1)} percent weekday coverage`}
            >
              <span>
                {new Date(c.month + "-01T00:00Z").toLocaleDateString("en", {
                  month: "short",
                  timeZone: "UTC",
                })}
              </span>
              <strong>
                {fmt(c.weekday_coverage_pct, 1)}
                <small>%</small>
              </strong>
              <div className="coverage-track">
                <i style={{ width: `${c.weekday_coverage_pct}%` }} />
              </div>
              <small>
                {c.observed_weekdays}/{c.weekday_days} weekdays
              </small>
            </button>
          ))}
        </div>
        {detail && (
          <div className="month-detail">
            {detail.month}: {count(detail.bars)} validated bars ·{" "}
            {count(detail.flat_bars)} flats · {detail.download_failures}{" "}
            failed/source-blocked days · {detail.unattempted_days} days not
            attempted
          </div>
        )}
        <div className="chart-caption">
          <span>Click a month to inspect ingestion details</span>
          <span>
            <span className="legend-dot" />
            Observed coverage <span className="legend-dot muted-dot" />
            No observations
          </span>
        </div>
      </Panel>
      <div className="two-column">
        <Panel
          title="Ingestion manifest"
          sub="Latest outcome per UTC day, including unsuccessful attempts"
        >
          <div className="detail-rows">
            <div>
              <span>Dates attempted</span>
              <strong>{count(q.manifest.days)}</strong>
            </div>
            {Object.entries(q.manifest.statuses).map(([s, n]) => (
              <div key={s}>
                <span className="capitalize">{s.replaceAll("_", " ")}</span>
                <strong>{count(n)}</strong>
              </div>
            ))}
            <div>
              <span>Recorded latest attempts</span>
              <strong>{count(q.manifest.total_attempts)}</strong>
            </div>
            <div>
              <span>Successful source payloads</span>
              <strong>{fmt(q.manifest.downloaded_bytes / 1024, 1)} KB</strong>
            </div>
            <div>
              <span>Days not attempted</span>
              <strong className="amber-text">
                {count(q.unattempted_days.length)}
              </strong>
            </div>
          </div>
        </Panel>
        <Panel
          title="Quality rules"
          sub="Conservative exclusions, retained for audit"
        >
          <div className="rule-list">
            <div>
              <Check size={16} />
              <span>
                <strong>Closed-market flat bars</strong>
                <p>{q.flat_rule}</p>
              </span>
            </div>
            <div>
              <Check size={16} />
              <span>
                <strong>Price validation</strong>
                <p>
                  Finite values, nonnegative activity, coherent OHLC and
                  5,000–100,000 index-point bounds.
                </p>
              </span>
            </div>
            <div>
              <Check size={16} />
              <span>
                <strong>Gap-safe returns</strong>
                <p>
                  Returns require exact elapsed time. Incomplete intraday bars
                  are excluded from distribution tests.
                </p>
              </span>
            </div>
            <div>
              <CircleDot size={16} />
              <span>
                <strong>Calendar limitation</strong>
                <p>{q.calendar_note}</p>
              </span>
            </div>
          </div>
        </Panel>
      </div>
      <Panel
        title="Coverage by year"
        sub="Observed records; no extrapolation into missing periods"
      >
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th>Validated bars</th>
                <th>Flat bars</th>
                <th>Observed days</th>
                <th>Missing weekdays*</th>
                <th>First / last observation</th>
              </tr>
            </thead>
            <tbody>
              {q.years.map((y) => (
                <tr key={y.year}>
                  <td className="strong">{y.year}</td>
                  <td>{count(y.bars)}</td>
                  <td>{count(y.flat_bars)}</td>
                  <td>{y.observed_days}</td>
                  <td className="amber-text">{y.missing_weekdays}</td>
                  <td>
                    {y.first
                      ? `${y.first.slice(0, 10)} / ${y.last?.slice(0, 10)}`
                      : "No data"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="panel-note">
          * Diagnostic candidates include holidays; this is not a count of
          confirmed missing trading sessions.
        </p>
      </Panel>
      <Panel
        title="March 2025 · DST validation"
        sub="Time-zone conversion checks and source availability are reported separately"
      >
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>NY 09:30 → UTC</th>
                <th>London 08:00 → UTC</th>
                <th>Observed NY / London bars</th>
              </tr>
            </thead>
            <tbody>
              {q.dst_checks.map((d) => (
                <tr key={d.date}>
                  <td>{d.date}</td>
                  <td>{d.ny_open_utc.slice(11, 16)}</td>
                  <td>{d.london_open_utc.slice(11, 16)}</td>
                  <td
                    className={
                      d.observed_ny_open && d.observed_london_open
                        ? "green"
                        : "amber-text"
                    }
                  >
                    {d.observed_ny_open ? "Yes" : "Missing"} /{" "}
                    {d.observed_london_open ? "Yes" : "Missing"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="panel-note">
          US daylight saving starts March 9; UK/EU starts March 30. Unit checks
          verify offsets; observed-data checks need the full month.
        </p>
      </Panel>
      <details className="panel details">
        <summary>
          Inspect missing weekday candidates ({q.missing_weekdays.length})
        </summary>
        <div className="date-cloud">
          {q.missing_weekdays.map((d) => (
            <code key={d}>{d}</code>
          ))}
        </div>
      </details>
    </>
  );
}

function Sessions({ analytics: a }: { analytics: Analytics }) {
  const [zone, setZone] = useState("America/New_York");
  const [metric, setMetric] = useState("volatility_bps");
  const [tf, setTf] = useState("1min");
  const profile = a.hourly[zone];
  const dist = a.distributions.find((d) => d.timeframe === tf);
  const metrics = [
    ["volatility_bps", "Return volatility (bps)"],
    ["mean_range_points", "Average range (points)"],
    ["mean_return_bps", "Mean return (bps)"],
    ["mean_activity", "Vendor activity"],
  ];
  return (
    <>
      <div className="section-note">
        <Activity size={16} />
        <span>
          Profiles describe observed bars only. Session definitions use local
          IANA time zones; London and New York switch DST independently.
        </span>
      </div>
      <Panel
        title="The intraday volatility clock"
        sub="Average market behavior by hour · independent UTC and New York grouping"
        action={
          <select
            aria-label="Profile timezone"
            value={zone}
            onChange={(e) => setZone(e.target.value)}
          >
            <option value="America/New_York">New York · ET</option>
            <option value="UTC">UTC</option>
          </select>
        }
      >
        <div className="metric-tabs">
          {metrics.map(([m, l]) => (
            <button
              key={m}
              className={metric === m ? "selected" : ""}
              onClick={() => setMetric(m)}
            >
              {l}
            </button>
          ))}
        </div>
        <Chart
          data={profile.map((p) => ({ ...p }))}
          x="hour"
          y={metric}
          kind="bar"
          height={300}
        />
        <div className="chart-caption">
          <span>Hour in {zone} · Half-open hourly buckets</span>
          <span>Log returns exclude time gaps</span>
        </div>
      </Panel>
      <div className="two-column">
        <Panel
          title="Session comparison"
          sub="Mean 1-minute return volatility in basis points"
        >
          <Chart
            data={a.sessions.map((s, i) => ({
              session: i,
              volatility_bps: s.volatility_bps,
            }))}
            x="session"
            y="volatility_bps"
            kind="bar"
            color="#a78bfa"
            height={220}
          />
          <div className="session-key">
            {a.sessions.map((s, i) => (
              <span key={s.name}>
                {i} · {s.name}
              </span>
            ))}
          </div>
        </Panel>
        <Panel
          title="Serial dependence"
          sub="Contiguous M1 returns · descriptive Pearson correlations"
        >
          <Chart
            data={a.autocorrelation.map((r) => ({ ...r }))}
            x="lag"
            y="return_acf"
            second="absolute_return_acf"
            kind="line"
            height={220}
          />
          <div className="chart-caption">
            <span>
              <span className="legend-dot" />
              Returns
            </span>
            <span>
              <span className="legend-dot purple-dot" />
              Absolute returns · volatility clustering
            </span>
          </div>
        </Panel>
      </div>
      <Panel
        title="Session detail"
        sub="Research windows may overlap; activity is not exchange volume"
      >
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Session</th>
                <th>Local window</th>
                <th>Time zone</th>
                <th>Bars</th>
                <th>Mean return (bps)</th>
                <th>Volatility (bps)</th>
                <th>Mean range (pts)</th>
              </tr>
            </thead>
            <tbody>
              {a.sessions.map((s) => (
                <tr key={s.name}>
                  <td className="strong">{s.name}</td>
                  <td>
                    {s.start}–{s.end}
                  </td>
                  <td>{s.timezone}</td>
                  <td>{count(s.bars)}</td>
                  <td>{fmt(s.mean_return_bps, 3)}</td>
                  <td>{fmt(s.volatility_bps, 3)}</td>
                  <td>{fmt(s.mean_range_points, 3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Panel
        title="Return distribution"
        sub="Complete bars only · central 99% histogram; tails remain in statistics"
        action={
          <select
            aria-label="Distribution timeframe"
            value={tf}
            onChange={(e) => setTf(e.target.value)}
          >
            {a.distributions.map((d) => (
              <option key={d.timeframe} value={d.timeframe}>
                {d.timeframe}
              </option>
            ))}
          </select>
        }
      >
        {dist ? (
          <>
            <div className="distribution-stats">
              <div>
                <span>Observations</span>
                <strong>{count(dist.n)}</strong>
              </div>
              <div>
                <span>Skewness</span>
                <strong>{fmt(dist.skewness, 3)}</strong>
              </div>
              <div>
                <span>Excess kurtosis</span>
                <strong>{fmt(dist.excess_kurtosis, 3)}</strong>
              </div>
              <div>
                <span>Beyond 3σ</span>
                <strong>{fmt(dist.tail_3sigma_fraction * 100)}%</strong>
              </div>
            </div>
            <Chart
              data={dist.histogram}
              x="return_bps"
              y="count"
              kind="bar"
              height={230}
            />
            <p className="panel-note">
              {dist.histogram_tail_count} tail observations outside the
              displayed histogram. Return quantiles: 1% {fmt(dist.q01_bps)} bps
              · 99% {fmt(dist.q99_bps)} bps. No normal-distribution assumption.
            </p>
          </>
        ) : (
          <p className="panel-note">
            Insufficient complete bars for this timeframe.
          </p>
        )}
      </Panel>
      <Panel
        title="Point-in-time volatility regimes"
        sub="A descriptive label, with no automatic strategy selection"
      >
        <p className="panel-note">
          {a.regime_rule}.{" "}
          {a.regimes.length
            ? `${a.regimes.length} day labels generated.`
            : "Insufficient historical days for the 20-day warmup."}
        </p>
      </Panel>
    </>
  );
}

function MetricTable({ rows }: { rows: Record<string, Metrics> }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Sample</th>
            <th>Trades</th>
            <th>Net points</th>
            <th>Mean net points</th>
            <th>Sharpe*</th>
            <th>95% mean CI (pts)</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(rows).map(([name, m]) => (
            <tr key={name}>
              <td className="capitalize strong">
                {name}
                <small className="cell-small">
                  {m.start && `${m.start} → ${m.end}`}
                </small>
              </td>
              <td>{m.trades}</td>
              <td>{fmt(m.net_points)}</td>
              <td>{fmt(m.mean_net_points)}</td>
              <td>{fmt(m.sharpe_daily_trade)}</td>
              <td>
                {m.ci_low == null
                  ? "Insufficient sample"
                  : `${fmt(m.ci_low)} / ${fmt(m.ci_high)}`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function Experiments({ experiments }: { experiments: Experiment[] }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [selected, setSelected] = useState(experiments[0]?.id ?? "");
  const [cost, setCost] = useState("base");
  const filtered = experiments.filter(
    (e) =>
      (status === "all" || e.status === status) &&
      `${e.id} ${e.name}`.toLowerCase().includes(query.toLowerCase()),
  );
  const exp = experiments.find((e) => e.id === selected);
  const m = exp?.cost_scenarios[cost];
  return (
    <>
      <div className="stats-grid">
        <Stat
          label="Registered hypotheses"
          value={count(experiments.length)}
          note="Fixed rules · no parameter optimization"
          accent
        />
        <Stat
          label="Screened"
          value={count(
            experiments.filter((e) => e.status === "SCREENED").length,
          )}
          note="At least 100 available independent day trades"
        />
        <Stat
          label="Need more data"
          value={count(
            experiments.filter((e) => e.status === "REQUIRES_MORE_DATA").length,
          )}
          note="No validation claim permitted"
        />
        <Stat
          label="Validated edges"
          value="0"
          note="Execution and independent replication pending"
        />
      </div>
      <Panel
        title="Hypothesis registry"
        sub="All planned tests are retained, including negative and incomplete results"
        action={<span className="pill">{experiments.length} hypotheses</span>}
      >
        <div className="experiment-filters">
          <label className="search-field">
            <Search size={16} />
            <input
              aria-label="Search hypotheses"
              placeholder="Search hypotheses…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
          <label className="filter-field">
            <SlidersHorizontal size={15} />
            <select
              aria-label="Filter experiment status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="all">All statuses</option>
              <option value="SCREENED">Screened</option>
              <option value="REQUIRES_MORE_DATA">Requires more data</option>
            </select>
          </label>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Hypothesis</th>
                <th>Status</th>
                <th>Trades</th>
                <th>Mean net (pts)</th>
                <th>p-value</th>
                <th>FDR q-value</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtered.map((e) => (
                <tr
                  key={e.id}
                  className={selected === e.id ? "selected-row" : ""}
                >
                  <td>
                    <button
                      className="hypothesis-button"
                      onClick={() => setSelected(e.id)}
                    >
                      <small className="mono blue">{e.id}</small>
                      <strong>{e.name}</strong>
                    </button>
                  </td>
                  <td>
                    <span
                      className={`pill ${e.status === "REQUIRES_MORE_DATA" ? "amber-text" : ""}`}
                    >
                      {e.status.replaceAll("_", " ").toLowerCase()}
                    </span>
                  </td>
                  <td>{e.metrics.trades}</td>
                  <td>{fmt(e.metrics.mean_net_points)}</td>
                  <td>{fmt(e.metrics.p_value, 4)}</td>
                  <td>{e.metrics.p_value == null ? "—" : fmt(e.q_value, 4)}</td>
                  <td>
                    <button
                      className="icon-button"
                      aria-label={`Inspect ${e.name}`}
                      onClick={() => setSelected(e.id)}
                    >
                      <ChevronRight size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!filtered.length && (
            <div className="chart-empty">No hypotheses match your filters.</div>
          )}
        </div>
      </Panel>
      {exp && (
        <Panel
          title={exp.name}
          sub={`${exp.id} · ${exp.entry} ${exp.timezone} · ${exp.horizon_minutes}-minute horizon`}
          action={
            <Badge warn={exp.status === "REQUIRES_MORE_DATA"}>
              {exp.status.replaceAll("_", " ").toLowerCase()}
            </Badge>
          }
        >
          <div className="hypothesis-question">{exp.question}</div>
          <div className="experiment-detail-grid">
            <div>
              <h3>Execution rule</h3>
              <p>
                Enter at the opening price of the signal minute. Exit at the
                last close in a complete {exp.horizon_minutes}-minute window.{" "}
                {exp.direction === "reverse_prior_hour"
                  ? "Direction opposes the preceding complete hour, known before entry."
                  : "Long direction is fixed in advance."}
              </p>
              <h3>Statistical protocol</h3>
              <p>
                Chronological 60/20/20 split. Circular five-day block bootstrap
                with 2,000 samples. Benjamini–Hochberg correction across all
                three planned tests.
              </p>
            </div>
            <div className="cost-card">
              <div className="flex-between">
                <h3>Cost scenario</h3>
                <select
                  aria-label="Cost scenario"
                  value={cost}
                  onChange={(e) => setCost(e.target.value)}
                >
                  <option value="base">Base</option>
                  <option value="stress">Stress</option>
                </select>
              </div>
              <div className="cost-number">
                {fmt(m?.round_trip_points)}
                <small>pts / round trip</small>
              </div>
              <p>
                Assumed spread + slippage on both sides. Illustrative CFD costs;
                observed ASK quotes and broker fees are unavailable.
              </p>
            </div>
          </div>
          <div className="detail-stats">
            <div>
              <span>Net points</span>
              <strong>{fmt(m?.net_points)}</strong>
            </div>
            <div>
              <span>Mean net points</span>
              <strong>{fmt(m?.mean_net_points)}</strong>
            </div>
            <div>
              <span>Win rate</span>
              <strong>
                {m?.win_rate == null ? "—" : fmt(m.win_rate * 100) + "%"}
              </strong>
            </div>
            <div>
              <span>Max drawdown (pts)</span>
              <strong>{fmt(m?.max_drawdown_points)}</strong>
            </div>
          </div>
          <h3 className="subheading">
            Chronological samples · base cost scenario
          </h3>
          <MetricTable rows={exp.splits} />
          <h3 className="subheading">Yearly results · base cost scenario</h3>
          <MetricTable rows={exp.yearly} />
          <div className="panel-note">
            * Annualized daily-trade return / volatility × √252; descriptive and
            unstable for small samples. CIs and p-values are withheld below 20
            day trades.
          </div>
          <h3 className="subheading">Cumulative net points · base scenario</h3>
          <Chart
            data={exp.equity.map((e) => ({
              time: Date.parse(e.date + "T00:00:00Z") / 1000,
              net_points: e.net_points,
            }))}
            x="time"
            y="net_points"
            format="time"
            height={200}
          />
          <div className="method-note">
            <FlaskConical size={18} />
            <p>{exp.limitations}</p>
          </div>
          <div className="run-line mono">
            RUN {exp.run_id} · DATA {exp.data_version.slice(0, 12)} · CONFIG{" "}
            {exp.config_version.slice(0, 12)}
          </div>
        </Panel>
      )}
    </>
  );
}
