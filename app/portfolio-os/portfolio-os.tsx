"use client";

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { LockKeyhole, RefreshCw, Search } from "lucide-react";
import type { OSState, Profile } from "@/lib/portfolio-os-types";
import {
  terminalNumber as num,
  terminalDays,
  terminalShortcut,
  terminalSleeves,
  terminalCostRows,
} from "@/lib/portfolio-terminal.mjs";

import {
  publicCostRoutes,
  terminalClockContext,
} from "@/lib/portfolio-public.mjs";

const tabs = [
  "Terminal Cockpit",
  "60D Audit Ledger",
  "Cost & Broker Matrix",
  "Dagbrief Inspector",
];
const profiles: Record<Profile, string> = {
  defensive: "Defensive 50/0/25/25",
  balanced: "Balanced 60/30/10/0",
  offensive: "Offensive 0/100/0/0",
};
const planNames: Record<Profile, string> = {
  defensive: "Defensief",
  balanced: "Gebalanceerd",
  offensive: "Offensief",
};
const brokerNames: Record<string, string> = {
  trading212: "T212 EUR",
  ibkr: "IBKR TIER",
  degiro: "DEGIRO",
  alpaca: "ALPACA P",
};
const variants = [
  ["naked", "NAKED"],
  ["schmitt", "SCHMITT .5%"],
  ["confirm2", "2D CONFIRM"],
] as const;
const euro = (value: number | null | undefined) =>
  value == null ? "—" : `€${num(value)}`;

function useDebounced(value: number) {
  const [result, setResult] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setResult(value), 180);
    return () => clearTimeout(timer);
  }, [value]);
  return result;
}

function Clocks() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
  const time = (zone: string) =>
    now
      ? new Intl.DateTimeFormat("en-GB", {
          timeZone: zone,
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }).format(now)
      : "--:--:--";
  const context = now ? terminalClockContext(now) : null;
  return (
    <div className="qt-clocks">
      <span>
        NYC <b>{time("America/New_York")}</b> {context?.ny_label ?? "—"}
      </span>
      <span>
        AMS <b>{time("Europe/Amsterdam")}</b> {context?.nl_label ?? "—"}
      </span>
      <span>
        DST_DELTA:<b>{context?.offset_hours ?? "—"}H</b>
      </span>
    </div>
  );
}

function BarTitle({
  title,
  detail,
  children,
}: {
  title: string;
  detail?: string;
  children?: ReactNode;
}) {
  return (
    <div className="qt-bar-title">
      <h2>{title}</h2>
      {detail ? <span>{detail}</span> : null}
      {children}
    </div>
  );
}

function SignalMatrix({ state }: { state: OSState }) {
  return (
    <section className="qt-signal qt-cell" aria-label="Signaalmatrix">
      <BarTitle
        title="01 / SIGNAL & REGIME MATRIX"
        detail={`ASOF ${state.market_asof} · USD`}
      />
      <div className="qt-table-wrap">
        <table className="qt-matrix">
          <thead>
            <tr>
              <th>ASSET</th>
              <th>CLOSE</th>
              <th>SMA20</th>
              <th>Δ20 %</th>
              <th>SMA200</th>
              <th>Δ200 %</th>
              <th>ATR14_PRE</th>
              <th>IBS</th>
              <th>VOL / P90</th>
            </tr>
          </thead>
          <tbody>
            {(["QQQ", "TQQQ"] as const).map((key) => {
              const d = state.telemetry[key];
              return (
                <tr key={key}>
                  <th>
                    {key}
                    <small>{key === "QQQ" ? "1X" : "3X DAILY"}</small>
                  </th>
                  <td>{num(d.close)}</td>
                  <td>{num(d.sma20)}</td>
                  <td
                    className={
                      d.distance_sma20_pct >= 0 ? "qt-positive" : "qt-negative"
                    }
                  >
                    {num(d.distance_sma20_pct)}%
                  </td>
                  <td>{num(d.sma200)}</td>
                  <td
                    className={
                      d.distance_sma200_pct >= 0 ? "qt-positive" : "qt-negative"
                    }
                  >
                    {num(d.distance_sma200_pct)}%
                    <span className="qt-distance-track">
                      <i
                        style={{
                          width: `${Math.min(100, Math.max(2, 50 + d.distance_sma200_pct * 2))}%`,
                        }}
                      />
                    </span>
                  </td>
                  <td>{num(d.atr14_pre)}</td>
                  <td>{num(d.ibs, 3)}</td>
                  <td>
                    {num(d.vol_ratio * 100)} / {num(d.vol_p90_pre * 100)}%
                    <small className={d.high_vol ? "qt-warning" : "qt-muted"}>
                      {d.high_vol == null
                        ? "UNKNOWN"
                        : d.high_vol
                          ? "HIGH_VOL"
                          : "NORMAL"}
                    </small>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="qt-inline-strip">
        <span>Δ$_20 QQQ {num(state.telemetry.QQQ.distance_sma20_dollars)}</span>
        <span>
          Δ$_200 QQQ {num(state.telemetry.QQQ.distance_sma200_dollars)}
        </span>
        <span>
          TQQQ {num(state.telemetry.TQQQ.distance_sma20_dollars)} /{" "}
          {num(state.telemetry.TQQQ.distance_sma200_dollars)}
        </span>
        <span className="qt-muted">SNAPSHOT</span>
      </div>
    </section>
  );
}

function Diagnostics({ state }: { state: OSState }) {
  const q = state.telemetry.QQQ;
  const rows = [
    ["C > SMA20", num(q.sma20), num(q.close)],
    ["IBS >= 0.85", "0,850", num(q.ibs, 3)],
    ["RANGE > .85*ATR", num(0.85 * q.atr14_pre), num(q.high - q.low)],
    ["STATE == 2", "2", String(state.regime.state_code)],
  ];
  return (
    <div className="qt-diagnostics">
      <section className="qt-cell">
        <BarTitle title="02 / WHIPSAW & TIMING" />
        <table>
          <thead>
            <tr>
              <th>RULE / BASIS</th>
              <th>QQQ</th>
              <th>TQQQ</th>
            </tr>
          </thead>
          <tbody>
            {variants.map(([key, label]) => (
              <tr key={key}>
                <th>{label}</th>
                {(["QQQ", "TQQQ"] as const).map((asset) => (
                  <td
                    key={asset}
                    className={
                      state.telemetry[asset].anti_whipsaw[key]
                        ? "qt-positive"
                        : "qt-muted"
                    }
                  >
                    {state.telemetry[asset].anti_whipsaw[key] ? "LONG" : "CASH"}
                  </td>
                ))}
              </tr>
            ))}
            <tr>
              <th>09:30 DAILY OPEN</th>
              <td>2469/2469</td>
              <td>2469/2469</td>
            </tr>
            <tr>
              <th>09:31 MINUTE</th>
              <td colSpan={2}>
                {state.replay.execution_timing === "NEXT_DAILY_OPEN"
                  ? "NOT_SELECTED"
                  : `${state.replay.days - state.replay.missing_minute_quote_days}/${state.replay.days} DAYS · BOTH`}
              </td>
            </tr>
          </tbody>
        </table>
        <div className="qt-rule-note">MODE {state.replay.execution_timing}</div>
      </section>
      <section className="qt-cell">
        <BarTitle title="03 / S1 GATEKEEPER" detail="EXEC: LOCKED" />
        <table>
          <thead>
            <tr>
              <th>RULE</th>
              <th>LIMIT</th>
              <th>OBSERVED</th>
              <th>RESULT</th>
            </tr>
          </thead>
          <tbody>
            {state.s1.conditions.map((c, i) => (
              <tr key={c.key}>
                <th>{rows[i][0]}</th>
                <td>{rows[i][1]}</td>
                <td>{rows[i][2]}</td>
                <td className={c.passed ? "qt-positive" : "qt-negative"}>
                  {c.passed == null ? "N/A" : c.passed ? "PASS" : "FAIL"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="qt-rule-note">
          <LockKeyhole size={11} strokeWidth={1} />
          S1_ORDER_GATE: UNVERIFIED_ROUTE
        </div>
      </section>
    </div>
  );
}

function Equity({ state }: { state: OSState }) {
  const points = state.audit.days.map((d) =>
    Number(d.unit_nav ?? Number(d.nav_reference) / 1000),
  );
  const lo = Math.min(...points) - 0.001,
    hi = Math.max(...points) + 0.001;
  const line = points
    .map(
      (v, i) =>
        `${((i / Math.max(1, points.length - 1)) * 560).toFixed(2)},${(76 - ((v - lo) / Math.max(0.0001, hi - lo)) * 68).toFixed(2)}`,
    )
    .join(" ");
  return (
    <div className="qt-equity" aria-label="Flow-adjusted Unit-NAV">
      <div className="qt-chart-axis">
        <span>{num(hi, 4)}</span>
        <span>{num(lo, 4)}</span>
      </div>
      <svg
        viewBox="0 0 560 86"
        preserveAspectRatio="none"
        role="img"
        aria-label="Unit-NAV over geselecteerde auditperiode"
      >
        {[15, 43, 72].map((y) => (
          <line
            key={y}
            x1="0"
            x2="560"
            y1={y}
            y2={y}
            stroke="#27272a"
            strokeWidth="1"
          />
        ))}
        <polyline
          points={line}
          fill="none"
          stroke="#a1a1aa"
          strokeWidth="1"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
      <div className="qt-chart-dates">
        <span>{state.replay.first}</span>
        <span>{state.replay.last}</span>
      </div>
    </div>
  );
}

function Portfolio({
  state,
  profile,
  setProfile,
  deposit,
  setDeposit,
}: {
  state: OSState;
  profile: Profile;
  setProfile: (value: Profile) => void;
  deposit: number;
  setDeposit: (value: number) => void;
}) {
  const last = state.audit.days.at(-1)!,
    nav = Number(last.nav_reference),
    dd = Number(last.drawdown) * 100;
  const limit = state.profiles[state.active_profile].dd_limit_pct,
    preview = profile !== state.active_profile;
  const scenarios = state.scenarios.filter(
    (s) =>
      s.profile === planNames[profile] && Number(s.monthly_eur) === deposit,
  );
  return (
    <section className="qt-portfolio qt-cell">
      <BarTitle
        title="04 / CAPITAL & RISK"
        detail={preview ? "VIEW: PREVIEW" : "VIEW: ACTIVE"}
      />
      <div className="qt-controls qt-profile-controls">
        <select
          aria-label="Profielpreview"
          value={profile}
          onChange={(e) => setProfile(e.target.value as Profile)}
        >
          {Object.entries(profiles).map(([key, label]) => (
            <option value={key} key={key}>
              {label}
            </option>
          ))}
        </select>
        <select
          aria-label="Scenario maandinleg"
          value={deposit}
          onChange={(e) => setDeposit(Number(e.target.value))}
        >
          <option value={100}>€100/M</option>
          <option value={250}>€250/M</option>
        </select>
      </div>
      <table className="qt-sleeves">
        <thead>
          <tr>
            <th>SLEEVE</th>
            <th>WEIGHT</th>
            <th>{preview ? "TARGET_REF €" : "BALANCE_REF €"}</th>
          </tr>
        </thead>
        <tbody>
          {terminalSleeves(state, profile).map((s) => (
            <tr key={s.sleeve}>
              <th>
                {s.sleeve.toUpperCase()}
                {s.sleeve === "s1" ? " [OFF]" : ""}
              </th>
              <td>{num(s.weight * 100, 0)}%</td>
              <td>{num(s.value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="qt-capital-stats">
        <span>
          NAV_REF <b>{num(nav)}</b>
        </span>
        <span>
          UNIT <b>{num(Number(last.unit_nav ?? nav / 1000), 4)}</b>
        </span>
        <span>
          DD <b className="qt-warning">{num(dd)}%</b> / {limit}%
        </span>
      </div>
      <Equity state={state} />
      <div className="qt-dd-track">
        <i style={{ width: `${Math.min(100, (dd / limit) * 100)}%` }} />
      </div>
      <div className="qt-inline-strip">
        <span>POLICY_ACTIVE: {state.active_profile.toUpperCase()}</span>
        <span className={state.audit.meta.halt ? "qt-negative" : "qt-muted"}>
          {state.audit.meta.halt ? "BREAKER: HALT" : "BREAKER: READY"}
        </span>
      </div>
      <table className="qt-projections">
        <thead>
          <tr>
            <th>PLAN / NOT_FORECAST</th>
            <th>5Y</th>
            <th>10Y</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>
              €{deposit}/M ·{" "}
              {profile === "defensive"
                ? "6"
                : profile === "balanced"
                  ? "8"
                  : "10"}
              %/Y
            </th>
            {[5, 10].map((y) => (
              <td key={y}>
                {euro(
                  Number(
                    scenarios.find((s) => Number(s.years) === y)
                      ?.planning_central_eur ?? 0,
                  ),
                )}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
      <div className="qt-rule-note">
        FX=1 REF · PRE-TAX · VIEW ≠ POLICY_CHANGE
      </div>
    </section>
  );
}

type CostsProps = {
  state: OSState;
  amount: number;
  setAmount: (n: number) => void;
  spread: number;
  setSpread: (n: number) => void;
  gate: string;
  setGate: (v: string) => void;
  broker: string;
  setBroker: (v: string) => void;
};
function Friction({
  state,
  amount,
  setAmount,
  spread,
  setSpread,
  gate,
  setGate,
  broker,
  setBroker,
}: CostsProps) {
  const routes = terminalCostRows(state.costs, gate),
    selected = routes.find((c) => c.key === broker)!;
  return (
    <section className="qt-friction qt-cell">
      <BarTitle
        title="05 / FRICTION & ACCUMULATOR"
        detail="ROUTES: UNVERIFIED"
      />
      <div className="qt-controls">
        <label>
          NOTIONAL €
          <input
            aria-label="Orderbudget in euro"
            type="number"
            min={1}
            max={1000000}
            value={amount}
            onChange={(e) =>
              setAmount(
                Math.max(1, Math.min(1000000, Number(e.target.value) || 1)),
              )
            }
          />
        </label>
        <label>
          SPREAD BP
          <input
            aria-label="Volledige spread in basispunten"
            type="number"
            min={0}
            max={100}
            step={0.5}
            value={spread}
            onChange={(e) =>
              setSpread(Math.max(0, Math.min(100, Number(e.target.value) || 0)))
            }
          />
        </label>
        <select
          aria-label="Frictiepoort"
          value={gate}
          onChange={(e) => setGate(e.target.value)}
        >
          <option value="5">GATE 5 BP</option>
          <option value="10">GATE 10 BP</option>
        </select>
      </div>
      <div className="qt-table-wrap">
        <table className="qt-fees">
          <thead>
            <tr>
              <th>BROKER</th>
              <th>NOTIONAL</th>
              <th>RT FEE €</th>
              <th>SPRD</th>
              <th>RT BP</th>
              <th>MIN €</th>
            </tr>
          </thead>
          <tbody>
            {routes.map((c) => (
              <tr key={c.key} className={broker === c.key ? "qt-selected" : ""}>
                <th>
                  <button
                    aria-label={`Broker ${c.label}`}
                    onClick={() => setBroker(c.key)}
                  >
                    {brokerNames[c.key]}
                  </button>
                </th>
                <td>{num(c.amount_eur, 0)}</td>
                <td>{num(c.fee_eur)}</td>
                <td>{num(c.spread_bp, 1)}</td>
                <td
                  className={
                    c.math_status === "MATH_PASS" ? "qt-positive" : "qt-warning"
                  }
                >
                  {c.roundtrip_bp == null ? "≥" : ""}
                  {num(c.roundtrip_bp ?? c.lower_bound_bp)}
                </td>
                <td>
                  {c.key === "alpaca"
                    ? "?"
                    : c.gate.minimum_eur == null
                      ? "∞"
                      : num(c.gate.minimum_eur)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="qt-accumulator">
        <div>
          <span>
            {brokerNames[selected.key]} :: {selected.math_status}
          </span>
          <span>
            EXTRA €{" "}
            {selected.key === "alpaca" ? "?" : num(selected.gate.extra_eur)}
          </span>
        </div>
        <div className="qt-savings-track">
          <i style={{ width: `${selected.gate.progress_pct}%` }} />
        </div>
        <div>
          <span>
            €100/M →{" "}
            {selected.gate.months == null
              ? "NO_FINITE_THRESHOLD"
              : `${selected.gate.months} MONTHS`}
          </span>
          <span>
            APPROVED_INTENT: <b className="qt-negative">LOCKED</b>
          </span>
        </div>
      </div>
      <div className="qt-rule-note">
        SLIP_ASSUMED: +1 BP · MATH_PASS ≠ ROUTE_VERIFIED
      </div>
    </section>
  );
}

type AuditProps = {
  state: OSState;
  query: string;
  setQuery: (v: string) => void;
  filter: string;
  setFilter: (v: string) => void;
  selectedDay: string;
  setDay: (v: string) => void;
};
function Audit({
  state,
  query,
  setQuery,
  filter,
  setFilter,
  selectedDay,
  setDay,
}: AuditProps) {
  const rows = useMemo(
    () => terminalDays(state.audit.days, query, filter),
    [state.audit.days, query, filter],
  );
  return (
    <section className="qt-audit qt-cell">
      <BarTitle
        title="06 / 60D AUDIT LEDGER"
        detail={`${rows.length}/${state.audit.days.length} ROWS`}
      />
      <div className="qt-controls qt-audit-controls">
        <label className="qt-search">
          <Search size={12} strokeWidth={1} />
          <input
            aria-label="Zoek in audit"
            placeholder="DATE / STATE / REASON"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <select
          aria-label="Auditfilter"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">ALL</option>
          <option value="fills">FILLS ONLY</option>
          <option value="cost">COST-BLOCKED</option>
          <option value="data">DATA-SKIPS</option>
        </select>
      </div>
      <div className="qt-audit-scroll">
        <table>
          <thead>
            <tr>
              <th>DATE</th>
              <th>STATE</th>
              <th>RESULT</th>
              <th>FILLS</th>
              <th>DD %</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr
                key={d.day}
                className={d.day === selectedDay ? "qt-selected" : ""}
              >
                <th>
                  <button
                    aria-label={`Inspecteer ${d.day}`}
                    onClick={() => setDay(d.day)}
                  >
                    {d.day}
                  </button>
                </th>
                <td>{d.advisor.state}</td>
                <td
                  className={
                    d.has_data_skip || d.has_cost_block
                      ? "qt-warning"
                      : d.fills
                        ? "qt-positive"
                        : "qt-muted"
                  }
                >
                  {d.has_data_skip
                    ? "DATA_SKIP"
                    : d.has_cost_block
                      ? "COST_BLOCK"
                      : d.fills
                        ? "FILLED"
                        : "HOLD"}
                </td>
                <td>{d.fills}</td>
                <td>{num(Number(d.drawdown) * 100)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!rows.length ? (
          <div className="qt-empty">NO_MATCHING_RECORDS</div>
        ) : null}
      </div>
    </section>
  );
}

function Inspector({
  state,
  day,
  setDay,
  mode,
  setMode,
}: {
  state: OSState;
  day: string;
  setDay: (value: string) => void;
  mode: string;
  setMode: (value: string) => void;
}) {
  const brief = state.briefs.find((b) => b.day === day) ?? state.briefs.at(-1)!,
    intents = state.audit.intents.filter((i) => i.day === brief.day);
  return (
    <section className="qt-inspector qt-cell">
      <BarTitle title="07 / DAY & INTENT INSPECTOR">
        <select
          aria-label="Selecteer dagbrief"
          value={brief.day}
          onChange={(e) => setDay(e.target.value)}
        >
          {state.briefs
            .slice()
            .reverse()
            .map((b) => (
              <option key={b.day}>{b.day}</option>
            ))}
        </select>
      </BarTitle>
      <div className="qt-inspector-tabs">
        <button
          className={mode === "brief" ? "is-active" : ""}
          onClick={() => setMode("brief")}
        >
          DAGBRIEF
        </button>
        <button
          className={mode === "intents" ? "is-active" : ""}
          onClick={() => setMode("intents")}
        >
          {state.public_summary ? "ORDERMETADATA" : "ORDERINTENTS"} [
          {intents.length}]
        </button>
      </div>
      {mode === "brief" ? (
        <pre className="qt-brief-text">{brief.markdown}</pre>
      ) : (
        <div className="qt-intent-details">
          {intents.length ? (
            intents.map((i) => (
              <article key={i.id}>
                <div className="qt-intent-state">
                  {i.side} {i.key} · {i.status}
                </div>
                <dl>
                  <dt>INTENT_SHA256</dt>
                  <dd>{i.id}</dd>
                  <dt>POLICY_SHA256</dt>
                  <dd>{i.policy_hash}</dd>
                  <dt>REASON</dt>
                  <dd>{i.reason}</dd>
                  <dt>APPROVAL_HMAC</dt>
                  <dd>PROCESS_LOCAL / NOT_RETAINED</dd>
                </dl>
                <pre>{JSON.stringify(i, null, 2)}</pre>
              </article>
            ))
          ) : (
            <div className="qt-empty">NO_ORDERINTENTS_ON_SELECTED_DAY</div>
          )}
        </div>
      )}
    </section>
  );
}

function BrokerNotes({ state, gate }: { state: OSState; gate: string }) {
  return (
    <section className="qt-cell qt-route-notes">
      <BarTitle title="ROUTE / MODEL LIMITS" detail={`GATE ${gate} BP`} />
      <table>
        <thead>
          <tr>
            <th>ROUTE</th>
            <th>ASSUMPTIONS / EVIDENCE</th>
          </tr>
        </thead>
        <tbody>
          {state.costs.map((c) => (
            <tr key={c.key}>
              <th>{brokerNames[c.key]}</th>
              <td>
                {c.note}
                <small>EXECUTION_PERMISSION: UNVERIFIED</small>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="qt-rule-note">
        BUDGET: SCENARIO INPUT · SPREAD: ASSUMED · NO ORDER ENDPOINT
      </div>
    </section>
  );
}

export default function PortfolioOS() {
  const [state, setState] = useState<OSState | null>(null),
    [error, setError] = useState("");
  const [activeTab, setTab] = useState(1),
    [dataset, setDataset] = useState("current");
  const [profile, setProfile] = useState<Profile>("defensive"),
    [deposit, setDeposit] = useState(100);
  const [amount, setAmount] = useState(100),
    [spread, setSpread] = useState(3),
    [gate, setGate] = useState("5"),
    [broker, setBroker] = useState("trading212");
  const [query, setQuery] = useState(""),
    [filter, setFilter] = useState("all"),
    [selectedDay, setDay] = useState(""),
    [inspectorMode, setInspectorMode] = useState("brief"),
    [refresh, setRefresh] = useState(0);
  const budget = useDebounced(amount),
    quoteSpread = useDebounced(spread),
    tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  useEffect(() => {
    let mounted = true;
    let controller = new AbortController();
    const load = async () => {
      controller.abort();
      controller = new AbortController();
      try {
        const local =
          process.env.NODE_ENV !== "production" &&
          ["localhost", "127.0.0.1", "[::1]"].includes(
            window.location.hostname,
          );
        const response = await fetch(
          local
            ? `/api/portfolio-os?dataset=${dataset}&amount=${budget}&spread=${quoteSpread}`
            : `/data/portfolio-os/${dataset}.json`,
          { signal: controller.signal, cache: "no-store" },
        );
        const body = await response.json();
        if (!response.ok) throw new Error(body.error || "STATE_UNAVAILABLE");
        if (!local) body.costs = publicCostRoutes(budget, quoteSpread);
        if (mounted) {
          setState(body);
          setError("");
        }
      } catch (e) {
        if (mounted && e instanceof Error && e.name !== "AbortError")
          setError(e.message);
      }
    };
    void load();
    const timer = setInterval(() => void load(), 15000);
    return () => {
      mounted = false;
      controller.abort();
      clearInterval(timer);
    };
  }, [dataset, budget, quoteSpread, refresh]);
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const typing =
        event.target instanceof Element &&
        !!event.target.closest(
          'input,textarea,select,[contenteditable="true"]',
        );
      const tab = terminalShortcut(
        event.key,
        typing,
        event.metaKey || event.ctrlKey || event.altKey,
      );
      if (tab) {
        event.preventDefault();
        setTab(tab);
        tabRefs.current[tab - 1]?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  if (!state)
    return (
      <main lang="nl" className="qt-terminal qt-boot">
        <div>QUANT-OS // PORTFOLIO-AGENT</div>
        <pre>{error ? `STATE_ERROR :: ${error}` : "READING LOCAL AUDIT…"}</pre>
        {error ? (
          <button onClick={() => setRefresh((v) => v + 1)}>RETRY</button>
        ) : null}
      </main>
    );
  const day = state.briefs.some((b) => b.day === selectedDay)
    ? selectedDay
    : state.briefs.at(-1)!.day;
  const policyOk = state.policy_hash === state.audit.meta.policy_hash;
  const regime =
    state.regime.state_code === 2
      ? "STATE_2 :: CONFIRMED_BULL"
      : state.regime.state_code === 1
        ? "STATE_1 :: PULLBACK"
        : state.regime.state_code === 0
          ? "STATE_0 :: BEAR_LOCKDOWN"
          : "DATA_HALT";
  const capital = (
    <Portfolio
      state={state}
      profile={profile}
      setProfile={setProfile}
      deposit={deposit}
      setDeposit={setDeposit}
    />
  );
  const friction = (
    <Friction
      state={state}
      amount={amount}
      setAmount={setAmount}
      spread={spread}
      setSpread={setSpread}
      gate={gate}
      setGate={setGate}
      broker={broker}
      setBroker={setBroker}
    />
  );
  const audit = (
    <Audit
      state={state}
      query={query}
      setQuery={setQuery}
      filter={filter}
      setFilter={setFilter}
      selectedDay={day}
      setDay={setDay}
    />
  );
  const inspector = (
    <Inspector
      state={state}
      day={day}
      setDay={setDay}
      mode={inspectorMode}
      setMode={setInspectorMode}
    />
  );
  return (
    <div lang="nl" className="qt-terminal">
      <header className="qt-commandbar">
        <div className="qt-system">
          <strong>
            QUANT-OS <span>// PORTFOLIO-AGENT</span>
          </strong>
          <span className="qt-muted">
            <LockKeyhole size={11} strokeWidth={1} />
            SHADOW_ONLY
          </span>
          <code
            className={policyOk ? "" : "qt-negative"}
            title={state.policy_hash}
          >
            {policyOk ? "POLICY_OK" : "HASH_FAIL"}:
            {state.policy_hash.slice(0, 10)}
          </code>
        </div>
        <div className="qt-header-state">
          <div>
            <span className={`qt-state-dot state-${state.regime.state_code}`} />
            <b>{regime}</b>
          </div>
          <small>SHADOW_OK:REPLAY · ROUTE:NO · EVIDENCE:NO</small>
        </div>
        <Clocks />
      </header>
      <nav className="qt-tabrail" aria-label="Terminal werkbladen">
        <div role="tablist" aria-label="Werkbladen">
          {tabs.map((label, i) => (
            <button
              key={label}
              ref={(el) => {
                tabRefs.current[i] = el;
              }}
              id={`qt-tab-${i + 1}`}
              role="tab"
              aria-selected={activeTab === i + 1}
              aria-controls="qt-workspace"
              className={activeTab === i + 1 ? "is-active" : ""}
              onClick={() => setTab(i + 1)}
            >
              [{i + 1}] {label}
            </button>
          ))}
        </div>
        <div className="qt-dataset-control">
          <label htmlFor="qt-dataset">DATASET</label>
          <select
            id="qt-dataset"
            value={dataset}
            onChange={(e) => {
              setDataset(e.target.value);
              setDay("");
            }}
          >
            {state.datasets.map((d) => (
              <option value={d.key} key={d.key}>
                {d.key === "current"
                  ? state.public_summary
                    ? "PUBLISHED EXPORT"
                    : "CURRENT EXPORT"
                  : d.key === "60d_recent"
                    ? "60D RECENT / 09:31"
                    : d.key === "60d_complete"
                      ? "60D COMPLETE / 09:31"
                      : "60D DAILY OPEN"}
              </option>
            ))}
          </select>
          <button
            aria-label="State vernieuwen"
            title="State vernieuwen"
            onClick={() => setRefresh((v) => v + 1)}
          >
            <RefreshCw size={12} strokeWidth={1} />
          </button>
        </div>
      </nav>
      <main
        id="qt-workspace"
        className={`qt-workspace tab-${activeTab}`}
        role="tabpanel"
        aria-labelledby={`qt-tab-${activeTab}`}
      >
        {activeTab === 1 ? (
          <>
            <div className="qt-left-top">
              <SignalMatrix state={state} />
              <Diagnostics state={state} />
            </div>
            {capital}
            <div className="qt-audit-pair">
              {audit}
              {inspector}
            </div>
            {friction}
          </>
        ) : activeTab === 2 ? (
          <div className="qt-full-split">
            {audit}
            {inspector}
          </div>
        ) : activeTab === 3 ? (
          <div className="qt-full-split qt-cost-workspace">
            {friction}
            <BrokerNotes state={state} gate={gate} />
          </div>
        ) : (
          <div className="qt-full-split qt-reader-workspace">
            {audit}
            {inspector}
          </div>
        )}
      </main>
      <footer className="qt-statusbar">
        <span title="Geen onafhankelijke 60-sessie forwardfase">
          SHADOW_OK:<b className="qt-warning">REPLAY_ONLY</b>
        </span>
        <span>
          ROUTE_VERIFIED:<b className="qt-negative">NO</b>
        </span>
        <span>
          STRATEGY_EVIDENCE:<b className="qt-warning">INSUFFICIENT</b>
        </span>
        <span className="qt-footer-data">
          ASOF {state.market_asof} · {state.replay.execution_timing} · ANCHORS{" "}
          {state.replay.days - state.replay.missing_minute_quote_days}/
          {state.replay.days} · FILLS {state.replay.fills}
        </span>
        <span className={error ? "qt-negative" : "qt-muted"}>
          {error ||
            (state.public_summary
              ? "PUBLIC_SNAPSHOT / LIVE_LOCKED"
              : "DB_READ_ONLY / LIVE_LOCKED")}
        </span>
      </footer>
    </div>
  );
}
