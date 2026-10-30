"use client";
import { useEffect, useMemo, useState } from "react";
import type { Profile } from "@/lib/portfolio-os-types";
import type { ProfileBenchmark } from "@/lib/profile-benchmark-types";
import { dutchDate, growthPoints } from "@/lib/portfolio-friendly.mjs";

const selectedModel: Record<Profile, string> = {
  defensive: "defensive_off",
  balanced: "balanced_off",
  offensive: "offensive",
};
const colors: Record<string, string> = {
  defensive_off: "#60a5fa",
  balanced_off: "#a78bfa",
  offensive: "#fb923c",
  qqq_trend200: "#2dd4bf",
  qqq_buyhold: "#cbd5e1",
  tqqq_trend200: "#f472b6",
};
const money = (v: number, currency: string) =>
  new Intl.NumberFormat("nl-NL", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(v);
const number = (v: number | null, digits = 2) =>
  v === null
    ? "—"
    : new Intl.NumberFormat("nl-NL", {
        maximumFractionDigits: digits,
        minimumFractionDigits: digits,
      }).format(v);
let request: Promise<ProfileBenchmark> | undefined;
function load() {
  return (request ??= fetch("/data/portfolio-os/profile-benchmark.json")
    .then((r) => {
      if (!r.ok)
        throw Error("De historische vergelijking kon niet worden geladen.");
      return r.json();
    })
    .catch((e) => {
      request = undefined;
      throw e;
    }));
}

export default function PerformanceComparison({
  profile,
}: {
  profile: Profile;
}) {
  const [data, setData] = useState<ProfileBenchmark | null>(null),
    [error, setError] = useState("");
  const [mode, setMode] = useState<"history" | "pure" | "future">("history");
  const [currency, setCurrency] = useState<"EUR" | "USD">("EUR"),
    [bp, setBp] = useState(2),
    [period, setPeriod] = useState("FULL");
  const [all, setAll] = useState(true),
    [hover, setHover] = useState<number | null>(null),
    [annual, setAnnual] = useState(0);
  useEffect(() => {
    let active = true;
    load()
      .then((d) => {
        if (active) setData(d);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, []);
  const model = selectedModel[profile],
    monthly = mode === "pure" ? 0 : 100;
  const indices = useMemo(
    () =>
      data?.days
        .map((_, i) => i)
        .filter((i) => period !== "2022" || data.days[i].startsWith("2022-")) ??
      [],
    [data, period],
  );
  const pureRows =
    data?.rows.filter(
      (r) =>
        r.currency === currency &&
        r.RT_bp === bp &&
        r.monthly === 0 &&
        r.period === period,
    ) ?? [];
  const chosen = pureRows.find((r) => r.model === model),
    bh = pureRows.find((r) => r.model === "qqq_buyhold"),
    trend = pureRows.find((r) => r.model === "qqq_trend200"),
    ttrend = pureRows.find((r) => r.model === "tqqq_trend200");
  const models = all
    ? Object.keys(colors)
    : [model, "qqq_trend200", "qqq_buyhold"];
  const curves = models.map((key) => ({
    key,
    label: data?.models[key] ?? key,
    values: indices.map(
      (i) => data?.curves[`${currency}|${bp}|${monthly}|${key}`]?.[i] ?? 0,
    ),
  }));
  const deposits = indices.map(
    (i) => 1000 + (monthly ? 100 * monthNumber(data!.days[i]) : 0),
  );
  const max =
    Math.max(1000, ...curves.flatMap((c) => c.values), ...deposits) * 1.08;
  const W = 1000,
    H = 325,
    L = 16,
    R = 90,
    T = 12,
    B = 35;
  const x = (i: number) =>
      L + ((W - L - R) * i) / Math.max(1, indices.length - 1),
    y = (v: number) => H - B - ((H - T - B) * v) / max;
  const path = (v: number[]) =>
    v
      .map((n, i) => `${i ? "L" : "M"}${x(i).toFixed(2)},${y(n).toFixed(2)}`)
      .join(" ");
  const inspect = Math.max(
    0,
    Math.min(hover ?? indices.length - 1, indices.length - 1),
  );
  const future = growthPoints(1000, 100, 10, annual / 100),
    futureLast = future.at(-1)!;
  return (
    <section
      className="human-panel human-performance"
      aria-label="Werkelijke historische prestatievergelijker"
    >
      <header className="human-panel-heading">
        <div>
          <span className="human-eyebrow">
            WAT LEVERDEN DE REGELS HISTORISCH OP?
          </span>
          <h2>Profielen naast eenvoudig beleggen</h2>
          <p>
            Gemeten ETF-koersen en een historische uitvoering-simulatie. Geen
            voorspelling of onafhankelijk winstbewijs.
          </p>
        </div>
      </header>
      <div
        className="performance-modes"
        role="group"
        aria-label="Weergave prestaties"
      >
        <button
          aria-pressed={mode === "history"}
          onClick={() => {
            setMode("history");
            setHover(null);
          }}
        >
          Echte historie: €1.000 + €100/mnd (2019–2026)
        </button>
        <button
          aria-pressed={mode === "pure"}
          onClick={() => {
            setMode("pure");
            setHover(null);
          }}
        >
          Pure groei: eenmalig €1.000 (2019–2026)
        </button>
        <button
          aria-pressed={mode === "future"}
          onClick={() => setMode("future")}
        >
          Toekomst-simulator · eigen %
        </button>
      </div>
      {mode === "future" ? (
        <div className="performance-body">
          <h3>Rekensimulatie — jij kiest de aanname</h3>
          <p>
            Geen profielrendement. Dit percentage is niet uit onze backtest
            afgeleid.
          </p>
          <label>
            Zelfgekozen rendement per jaar: <strong>{annual}%</strong>
            <input
              type="range"
              aria-label="Zelfgekozen jaarlijks rendement"
              min={-10}
              max={30}
              step={1}
              value={annual}
              onChange={(e) => setAnnual(Number(e.target.value))}
            />
          </label>
          <div className="performance-kpis">
            <div>
              Eigen inleg na 10 jaar<strong>€13.000</strong>
            </div>
            <div>
              Uitkomst bij jouw {annual}%
              <strong>{money(futureLast.value, "EUR")}</strong>
            </div>
          </div>
          <svg
            viewBox="0 0 1000 230"
            role="img"
            aria-label={`Rekensimulatie tien jaar met ${annual}% per jaar`}
          >
            <path
              d={future
                .map(
                  (p, i) =>
                    `${i ? "L" : "M"}${16 + (i / 120) * 900},${205 - (p.value / Math.max(13000, futureLast.value)) * 185}`,
                )
                .join(" ")}
              fill="none"
              stroke="#60a5fa"
              strokeWidth="3"
            />
            <path
              d={future
                .map(
                  (p, i) =>
                    `${i ? "L" : "M"}${16 + (i / 120) * 900},${205 - (p.contributions / Math.max(13000, futureLast.value)) * 185}`,
                )
                .join(" ")}
              fill="none"
              stroke="#94a3b8"
              strokeDasharray="5 5"
            />
          </svg>
          <p>
            Start €1.000, daarna €100 per maand. Belastingen, inflatie en
            wisselkoersen zijn hier niet inbegrepen. De stippellijn is je eigen
            inleg; er bestaat geen gemeten toekomstige Buy & Hold-lijn.
          </p>
        </div>
      ) : error ? (
        <p role="alert" className="performance-body">
          {error}
        </p>
      ) : !data ? (
        <p className="performance-body">Historische vergelijking laden…</p>
      ) : (
        <>
          <div className="performance-controls">
            <label>
              Valuta
              <select
                aria-label="Valuta historische prestaties"
                value={currency}
                onChange={(e) => setCurrency(e.target.value as "EUR" | "USD")}
              >
                <option value="EUR">Euro · ECB-referentiewaardering</option>
                <option value="USD">USD · vergelijkbaar met oude studie</option>
              </select>
            </label>
            <label>
              Kosten
              <select
                aria-label="Historische roundtripkosten"
                value={bp}
                onChange={(e) => setBp(Number(e.target.value))}
              >
                <option value="2">2 bp heen + terug</option>
                <option value="10">10 bp gevoeligheidscheck</option>
              </select>
            </label>
            <label>
              Periode
              <select
                aria-label="Periode historische prestaties"
                value={period}
                onChange={(e) => {
                  setPeriod(e.target.value);
                  setHover(null);
                }}
              >
                <option value="FULL">2019–2026 doorlopend</option>
                <option value="2022">
                  2022 berenmarkt · uit dezelfde replay
                </option>
              </select>
            </label>
            <label>
              <input
                type="checkbox"
                checked={all}
                onChange={(e) => setAll(e.target.checked)}
              />{" "}
              Alle profielen + TQQQ-referentie
            </label>
          </div>
          <div className="performance-kpis">
            <div>
              Eigen inleg
              <strong>{money(deposits.at(-1) ?? 1000, currency)}</strong>
            </div>
            <div>
              {data.models[model]}
              <strong>
                {money(
                  curves.find((c) => c.key === model)?.values.at(-1) ?? 0,
                  currency,
                )}
              </strong>
            </div>
            <div>
              {mode === "history"
                ? "Winst boven eigen inleg"
                : "Zuivere samengestelde groei"}
              <strong>
                {mode === "history"
                  ? money(
                      (curves.find((c) => c.key === model)?.values.at(-1) ??
                        0) - (deposits.at(-1) ?? 1000),
                      currency,
                    )
                  : `${number(chosen?.CAGR_pct ?? null)}% per jaar`}
              </strong>
            </div>
          </div>
          <div className="performance-chart">
            <svg
              viewBox={`0 0 ${W} ${H}`}
              role="img"
              tabIndex={0}
              aria-label={`Historische vermogensvergelijking ${mode}, ${period}, ${currency}. Gebruik de pijltjestoetsen om dagen te inspecteren.`}
              onKeyDown={(e) => {
                if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
                  e.preventDefault();
                  setHover(
                    Math.max(
                      0,
                      Math.min(
                        indices.length - 1,
                        inspect + (e.key === "ArrowLeft" ? -1 : 1),
                      ),
                    ),
                  );
                }
              }}
              onPointerMove={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                setHover(
                  Math.max(
                    0,
                    Math.min(
                      indices.length - 1,
                      Math.round(
                        ((((e.clientX - rect.left) / rect.width) * W - L) /
                          (W - L - R)) *
                          (indices.length - 1),
                      ),
                    ),
                  ),
                );
              }}
              onPointerLeave={() => setHover(null)}
            >
              {[0, 1, 2, 3].map((i) => (
                <g key={i}>
                  <line
                    x1={L}
                    x2={W - R}
                    y1={y((max * i) / 3)}
                    y2={y((max * i) / 3)}
                    className="chart-grid"
                  />
                  <text
                    x={W - R + 9}
                    y={y((max * i) / 3) + 4}
                    className="chart-axis"
                  >
                    {money((max * i) / 3, currency)}
                  </text>
                </g>
              ))}
              {period === "FULL" && (
                <rect
                  x={x(
                    indices.findIndex((i) => data.days[i].startsWith("2022-")),
                  )}
                  width={
                    x(
                      indices.findIndex((i) =>
                        data.days[i].startsWith("2023-"),
                      ),
                    ) -
                    x(
                      indices.findIndex((i) =>
                        data.days[i].startsWith("2022-"),
                      ),
                    )
                  }
                  y={T}
                  height={H - T - B}
                  fill="#ef4444"
                  opacity=".07"
                />
              )}
              <path
                d={path(deposits)}
                fill="none"
                stroke="#94a3b8"
                strokeWidth="2"
                strokeDasharray="3 5"
              />
              {curves.map((c) => (
                <path
                  key={c.key}
                  d={path(c.values)}
                  fill="none"
                  stroke={colors[c.key]}
                  strokeWidth={c.key === model ? 3 : 1.8}
                  strokeDasharray={c.key === "qqq_buyhold" ? "7 5" : undefined}
                />
              ))}
              {[0, Math.floor(indices.length / 2), indices.length - 1].map(
                (i) => (
                  <text
                    key={i}
                    x={x(i)}
                    y={H - 8}
                    className="chart-axis"
                    textAnchor={
                      i === 0
                        ? "start"
                        : i === indices.length - 1
                          ? "end"
                          : "middle"
                    }
                  >
                    {data.days[indices[i]]}
                  </text>
                ),
              )}
              {hover !== null && (
                <line
                  x1={x(inspect)}
                  x2={x(inspect)}
                  y1={T}
                  y2={H - B}
                  stroke="#a5b4fc"
                  strokeDasharray="3 4"
                />
              )}
            </svg>
            <div className="performance-legend">
              {curves.map((c) => (
                <span key={c.key}>
                  <i style={{ background: colors[c.key] }} />
                  {c.label}
                  {c.key === "qqq_buyhold" ? " · stippellijn" : ""}
                </span>
              ))}
              <span>┄ Eigen inleg</span>
            </div>
            <div className="performance-inspect">
              {dutchDate(data.days[indices[inspect]])} ·{" "}
              {curves
                .map((c) => `${c.label}: ${money(c.values[inspect], currency)}`)
                .join(" · ")}
            </div>
          </div>
          {period === "2022" && (
            <p className="human-note">
              2022 is uitgesneden uit de doorlopende portefeuille. Posities en
              vermogen uit 2021 blijven bestaan. De tabel toont het
              flow-gecorrigeerde jaarresultaat; de grafiek toont het werkelijk
              gesimuleerde vermogensniveau.
            </p>
          )}
          <div className="performance-verdict" role="status">
            <strong>De meerwaarde, zonder mooipraterij</strong>
            {chosen && bh && trend && ttrend && (
              <p>
                {data.models[model]} heeft bij {bp} bp{" "}
                {period === "FULL"
                  ? chosen.ending > bh.ending
                    ? "meer eindvermogen"
                    : "minder eindvermogen"
                  : chosen.total_growth_pct > bh.total_growth_pct
                    ? "een beter jaarrendement"
                    : "een slechter jaarrendement"}{" "}
                dan QQQ Buy & Hold en{" "}
                {period === "FULL"
                  ? chosen.ending > trend.ending
                    ? "meer eindvermogen"
                    : "minder eindvermogen"
                  : chosen.total_growth_pct > trend.total_growth_pct
                    ? "een beter jaarrendement"
                    : "een slechter jaarrendement"}{" "}
                dan QQQ TREND200. De maximale terugval is{" "}
                {number(chosen.max_DD_pct)}%, tegenover {number(bh.max_DD_pct)}%
                en {number(trend.max_DD_pct)}%. Dit profiel haalt{" "}
                {number(chosen.CAGR_pct)}% per jaar versus{" "}
                {number(ttrend.CAGR_pct)}% voor de eenvoudige TQQQ
                TREND200-referentie
                {chosen.CAGR_pct < ttrend.CAGR_pct
                  ? " — de complexere regels leveren hier dus minder groei op"
                  : ""}
                .
              </p>
            )}
          </div>
          <div className="performance-table">
            <table>
              <caption>
                Alle regels · {period === "FULL" ? "volledige periode" : "2022"}{" "}
                · {bp} bp · {currency}
              </caption>
              <thead>
                <tr>
                  <th>Regel</th>
                  <th>Vermogen zonder bijstorten</th>
                  <th>CAGR</th>
                  <th>Groei</th>
                  <th>Max terugval</th>
                  <th>Sharpe</th>
                  <th>Herstel / onderwater</th>
                  <th>Met maandinleg →</th>
                  <th>Winst boven inleg</th>
                </tr>
              </thead>
              <tbody>
                {pureRows.map((r) => {
                  const wealth = data.rows.find(
                    (w) =>
                      w.model === r.model &&
                      w.currency === currency &&
                      w.RT_bp === bp &&
                      w.monthly === 100 &&
                      w.period === period,
                  )!;
                  return (
                    <tr key={r.model}>
                      <th>{data.models[r.model]}</th>
                      <td>{money(r.ending, currency)}</td>
                      <td>{number(r.CAGR_pct)}%</td>
                      <td>{number(r.total_growth_pct)}%</td>
                      <td>{number(r.max_DD_pct)}%</td>
                      <td>{number(r.Sharpe)}</td>
                      <td>
                        {r.max_underwater_sessions} beursdagen /{" "}
                        {r.max_underwater_calendar_days} kalenderdagen
                        {r.last_drawdown_unrecovered
                          ? " · laatste dip niet hersteld"
                          : ""}
                      </td>
                      <td>{money(wealth.ending, currency)}</td>
                      <td>{money(wealth.profit, currency)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <aside className="performance-warning">
            <strong>
              Profielen mét S1: volledige historische prestatie onbekend.
            </strong>
            <p>
              {data.s1.required} vereiste nachten; {data.s1.anchors} met exacte
              ankers, maar slechts {data.s1.complete_stop_paths} volledig
              geobserveerde stoppaden. Voorzichtig en Gebalanceerd worden
              hierboven daarom expliciet met S1-reserve in cash getoond.
              Ontbrekende nachten zijn geen bewezen nulrendement.
            </p>
          </aside>
          <p className="human-note">
            {data.first} t/m {data.last}. 2020 en 2022 zijn volledig opgenomen.
            Dividenden eenmaal verwerkt; prijzen split-gecorrigeerd. Dagbar-open
            is een uitvoeringsreferentie, geen bewezen brokerfill.{" "}
            {currency === "EUR"
              ? "Eurocash met historische ECB-referentiewisselkoersen, geen geobserveerde FX-fills of conversiefees."
              : "USD-referentie; geen werkelijk eurorendement."}{" "}
            Kosten zijn aannames; belastingen en cashrente ontbreken. Maandgeld
            komt na de eerste opening binnen en wordt vanaf de volgende opening
            belegd. Historische simulatie op eerder onderzochte data; geen
            voorspelling.
          </p>
          <a
            className="performance-report"
            href="/reports/PROFILE_BENCHMARK_VERDICT_2026-10-30.md"
            target="_blank"
            rel="noopener noreferrer"
          >
            Lees de volledige meetlat en het oordeel →
          </a>
        </>
      )}
    </section>
  );
}

function monthNumber(day: string) {
  return (Number(day.slice(0, 4)) - 2019) * 12 + Number(day.slice(5, 7)) - 1;
}
