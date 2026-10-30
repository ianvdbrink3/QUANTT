"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Maximize2,
  Moon,
  ZoomIn,
} from "lucide-react";
import type { OSState } from "@/lib/portfolio-os-types";
import type { ChartData, ChartRow } from "@/lib/portfolio-chart-types";
import {
  chartPeriod,
  dutchDate,
  executedMarkers,
  marketCopy,
} from "@/lib/portfolio-friendly.mjs";
import { terminalNumber as num } from "@/lib/portfolio-terminal.mjs";

function TradingView({ asset }: { asset: "QQQ" | "TQQQ" }) {
  const container = useRef<HTMLDivElement>(null),
    [failed, setFailed] = useState(false);
  useEffect(() => {
    const host = container.current;
    if (!host) return;
    setFailed(false);
    host.replaceChildren();
    const widget = document.createElement("div");
    widget.className = "tradingview-widget-container__widget";
    widget.style.height = "100%";
    const script = document.createElement("script");
    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.async = true;
    script.onerror = () => setFailed(true);
    script.textContent = JSON.stringify({
      autosize: true,
      symbol: `NASDAQ:${asset}`,
      interval: "D",
      timezone: "America/New_York",
      theme: "dark",
      style: "3",
      locale: "nl",
      allow_symbol_change: false,
      withdateranges: true,
      hide_side_toolbar: false,
      save_image: false,
      calendar: false,
      support_host: "https://www.tradingview.com",
      studies: [
        { id: "MASimple@tv-basicstudies", inputs: { length: 20 } },
        { id: "MASimple@tv-basicstudies", inputs: { length: 200 } },
      ],
    });
    // Defer insertion so React StrictMode can cancel its preliminary mount.
    const frame = requestAnimationFrame(() => {
      host.appendChild(widget);
      host.appendChild(script);
    });
    return () => {
      cancelAnimationFrame(frame);
      script.onerror = null;
      host.replaceChildren();
    };
  }, [asset]);
  return (
    <div className="human-tv">
      <div ref={container} className="human-tv-frame" />
      {failed && (
        <div className="human-chart-error">
          TradingView kon niet laden. Controleer je internetverbinding.
        </div>
      )}
      <div className="human-chart-caption">
        <span>
          Externe koersweergave · kan vertraagd zijn of ontbreken · los van onze signalen
        </span>
        <a
          href={`https://www.tradingview.com/symbols/NASDAQ-${asset}/`}
          target="_blank"
          rel="noopener noreferrer"
        >
          {asset} op TradingView <ExternalLink size={12} />
        </a>
      </div>
    </div>
  );
}

export default function PortfolioChart({
  state,
  expanded = false,
}: {
  state: OSState;
  expanded?: boolean;
}) {
  const [data, setData] = useState<ChartData | null>(null),
    [error, setError] = useState(""),
    [asset, setAsset] = useState<"QQQ" | "TQQQ">("QQQ");
  const [mode, setMode] = useState(
      process.env.NODE_ENV === "production" ? "live" : "strategy",
    ),
    [period, setPeriod] = useState("3m"),
    [hover, setHover] = useState<number | null>(null);
  const [zoom, setZoom] = useState(100),
    [pan, setPan] = useState(100),
    [s1, setS1] = useState(true),
    [averages, setAverages] = useState(true);
  useEffect(() => {
    if (
      process.env.NODE_ENV === "production" ||
      !["localhost", "127.0.0.1", "[::1]"].includes(window.location.hostname)
    ) {
      setError(
        "De volledige lokale koershistorie wordt niet openbaar meegestuurd. Bekijk die op je Mac, of gebruik TradingView.",
      );
      return;
    }
    const abort = new AbortController();
    fetch("/api/portfolio-chart", { signal: abort.signal, cache: "no-store" })
      .then(async (r) => {
        if (!r.ok)
          throw Error(
            "De lokale koershistorie is hier niet beschikbaar. Gebruik de externe koersgrafiek.",
          );
        return r.json();
      })
      .then(setData)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => abort.abort();
  }, []);
  const base = useMemo(
    () => chartPeriod(data?.assets[asset] ?? [], period, state.market_asof),
    [data, asset, period, state.market_asof],
  );
  const count = Math.max(10, Math.ceil((base.length * zoom) / 100)),
    offset = Math.max(0, Math.round(((base.length - count) * pan) / 100));
  const rows = base.slice(offset, offset + count),
    markers = executedMarkers(state, asset).filter((m) =>
      rows.some((r) => r.day === m.day),
    );
  const width = 1000,
    height = 340,
    left = 18,
    right = 74,
    top = 22,
    bottom = 33,
    pw = width - left - right,
    ph = height - top - bottom;
  const values = rows
    .flatMap((r) => [r.close, ...(averages ? [r.sma20, r.sma200] : [])])
    .concat(markers.map((m) => m.price))
    .filter((v): v is number => v !== null && Number.isFinite(v));
  const low = values.length ? Math.min(...values) : 0,
    high = values.length ? Math.max(...values) : 1,
    pad = Math.max((high - low) * 0.1, 1),
    min = low - pad,
    max = high + pad;
  const x = (i: number) => left + (i / Math.max(1, rows.length - 1)) * pw,
    y = (v: number) => top + ((max - v) / (max - min)) * ph;
  const path = (key: "close" | "sma20" | "sma200", subset = rows, start = 0) =>
    subset
      .map((r, i) =>
        r[key] === null
          ? ""
          : `${i === 0 || subset[i - 1][key] === null ? "M" : "L"}${x(i + start).toFixed(2)},${y(r[key]!).toFixed(2)}`,
      )
      .join(" ");
  const segments: { start: number; end: number; state: number }[] = [];
  rows.forEach((r, i) => {
    const last = segments.at(-1);
    if (!last || last.state !== r.state)
      segments.push({ start: i, end: i, state: r.state });
    else last.end = i;
  });
  const selected = rows[Math.min(hover ?? rows.length - 1, rows.length - 1)],
    last = rows.at(-1),
    first = rows[0],
    change = first && last ? (last.close / first.close - 1) * 100 : 0;
  const activate = (i: number) =>
    setHover(Math.max(0, Math.min(rows.length - 1, i)));
  return (
    <section
      className={`human-panel human-chart-panel ${expanded ? "is-expanded" : ""}`}
      aria-label="Interactieve koersgrafiek"
    >
      <div className="human-panel-heading">
        <div>
          <span className="human-eyebrow">ZIE WAT DE MARKT DOET</span>
          <h2>De koers, onze lijnen en de signalen</h2>
        </div>
        <div className="human-segment" aria-label="Kies fonds">
          {(["QQQ", "TQQQ"] as const).map((a) => (
            <button
              key={a}
              aria-pressed={asset === a}
              className={asset === a ? "selected" : ""}
              onClick={() => {
                setAsset(a);
                setHover(null);
              }}
            >
              {a} <small>{a === "QQQ" ? "Kern · 1×" : "Turbo · 3×"}</small>
            </button>
          ))}
        </div>
      </div>
      <div className="human-chart-tabs" role="tablist" aria-label="Grafiekbron">
        <button
          role="tab"
          aria-selected={mode === "strategy"}
          onClick={() => setMode("strategy")}
        >
          Onze data & signalen
        </button>
        <button
          role="tab"
          aria-selected={mode === "live"}
          onClick={() => setMode("live")}
        >
          Live beurskoers{" "}
          <span>
            TradingView <ExternalLink size={11} />
          </span>
        </button>
      </div>
      {mode === "live" ? (
        <TradingView asset={asset} />
      ) : (
        <>
          <div className="human-chart-toolbar">
            <div className="human-periods">
              {[
                ["3m", "3 maanden"],
                ["year", "1 jaar"],
                ["2022", "2022 crash-test"],
                ["all", "Alles 2019–2026"],
              ].map(([k, label]) => (
                <button
                  key={k}
                  className={period === k ? "selected" : ""}
                  aria-pressed={period === k}
                  onClick={() => {
                    setPeriod(k);
                    setZoom(100);
                    setPan(100);
                    setHover(null);
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
            <span className="human-small">
              Dagsloten · dollars · peildatum {dutchDate(state.market_asof)}
            </span>
          </div>
          <div className="human-chart-quote" aria-live="polite">
            <strong>${num(selected?.close)}</strong>
            <span className={change >= 0 ? "text-green" : "text-red"}>
              {change >= 0 ? "+" : ""}
              {num(change)}% <small>in dit venster</small>
            </span>
            <span className="human-hover-date">
              {selected ? dutchDate(selected.day) : "Koersen laden…"}
            </span>
          </div>
          <div className="human-chart-legend">
            <span>
              <i className="legend-price" />
              Koers {asset}
            </span>
            <button
              aria-pressed={averages}
              onClick={() => setAverages((v) => !v)}
            >
              <i className="legend-short" />
              20 dagen{" "}
              {selected?.sma20 != null ? `$${num(selected.sma20)}` : ""}
              <i className="legend-long" />
              200 dagen{" "}
              {selected?.sma200 != null ? `$${num(selected.sma200)}` : ""}
            </button>
            <button aria-pressed={s1} onClick={() => setS1((v) => !v)}>
              <Moon size={12} /> Nachtkansen (signaal)
            </button>
          </div>
          {error && !data ? (
            <div className="human-chart-error">
              {error}
              <button onClick={() => setMode("live")}>
                Open TradingView <ExternalLink size={14} />
              </button>
            </div>
          ) : (
            <div className="human-chart-canvas">
              <svg
                viewBox={`0 0 ${width} ${height}`}
                role="img"
                tabIndex={0}
                aria-label={`Koersgrafiek ${asset}, ${rows.length} beursdagen. Gebruik de pijltjestoetsen om een dag te bekijken.`}
                onPointerMove={(e) => {
                  const box = e.currentTarget.getBoundingClientRect();
                  activate(
                    Math.round(
                      ((((e.clientX - box.left) / box.width) * width - left) /
                        pw) *
                        (rows.length - 1),
                    ),
                  );
                }}
                onPointerLeave={() => setHover(null)}
                onKeyDown={(e) => {
                  if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
                    e.preventDefault();
                    activate(
                      (hover ?? rows.length - 1) +
                        (e.key === "ArrowLeft" ? -1 : 1),
                    );
                  }
                }}
              >
                <defs>
                  <clipPath id={`price-clip-${asset}`}>
                    <rect x={left} y={top} width={pw} height={ph} />
                  </clipPath>
                </defs>
                {[0, 1, 2, 3, 4].map((i) => {
                  const val = min + ((max - min) * i) / 4;
                  return (
                    <g key={i}>
                      <line
                        x1={left}
                        x2={width - right}
                        y1={y(val)}
                        y2={y(val)}
                        className="chart-grid"
                      />
                      <text
                        x={width - right + 13}
                        y={y(val) + 4}
                        className="chart-axis"
                      >
                        ${num(val, 0)}
                      </text>
                    </g>
                  );
                })}
                <g clipPath={`url(#price-clip-${asset})`}>
                  {segments.map((s, i) => (
                    <rect
                      key={i}
                      x={x(s.start) - pw / Math.max(1, rows.length - 1) / 2}
                      width={Math.max(
                        1,
                        x(s.end) -
                          x(s.start) +
                          pw / Math.max(1, rows.length - 1),
                      )}
                      y={top}
                      height={ph}
                      fill={
                        s.state === 0
                          ? "#f43f5e"
                          : s.state === 2
                            ? "#10b981"
                            : "#f59e0b"
                      }
                      opacity={s.state === 0 ? 0.08 : 0.045}
                    />
                  ))}
                  {averages && (
                    <>
                      <path d={path("sma20")} className="chart-sma20" />
                      {segments.map((s, i) => (
                        <path
                          key={i}
                          d={path(
                            "sma200",
                            rows.slice(
                              s.start,
                              Math.min(rows.length, s.end + 2),
                            ),
                            s.start,
                          )}
                          className={
                            s.state === 0 ? "chart-sma200 red" : "chart-sma200"
                          }
                        />
                      ))}
                    </>
                  )}
                  <path
                    d={path("close")}
                    className={`chart-price ${asset === "TQQQ" ? "purple" : ""}`}
                  />
                  {s1 &&
                    rows.map((r, i) =>
                      r.s1_candidate ? (
                        <path
                          key={r.day}
                          d={`M${x(i)},${y(r.close) - 12}l-4,-6l4,-6l4,6Z`}
                          className="chart-candidate"
                        >
                          <title>
                            {dutchDate(r.day)} · Nachtkans bij dagslot, geen
                            order
                          </title>
                        </path>
                      ) : null,
                    )}
                  {markers.map((m) => {
                    const i = rows.findIndex((r) => r.day === m.day);
                    return (
                      <g
                        key={m.id}
                        transform={`translate(${x(i)},${y(m.price)})`}
                      >
                        <circle
                          r="6"
                          className={
                            m.side === "BUY"
                              ? "chart-fill buy"
                              : "chart-fill sell"
                          }
                        />
                        <path
                          d={
                            m.side === "BUY"
                              ? "M-3,1L0,-2L3,1"
                              : "M-3,-1L0,2L3,-1"
                          }
                          stroke="white"
                          fill="none"
                          strokeWidth="1.3"
                        />
                        <title>
                          {dutchDate(m.day)} · {m.label} · ${num(m.price, 4)}
                        </title>
                      </g>
                    );
                  })}
                  {selected && hover !== null && (
                    <>
                      <line
                        x1={x(hover)}
                        x2={x(hover)}
                        y1={top}
                        y2={height - bottom}
                        className="chart-crosshair"
                      />
                      <circle
                        cx={x(hover)}
                        cy={y(selected.close)}
                        r="4"
                        className="chart-hover-dot"
                      />
                    </>
                  )}
                </g>
                {[0, 0.25, 0.5, 0.75, 1].map((f) => {
                  const i = Math.round(f * Math.max(0, rows.length - 1));
                  return rows[i] ? (
                    <text
                      key={f}
                      x={x(i)}
                      y={height - 10}
                      textAnchor={
                        f === 0 ? "start" : f === 1 ? "end" : "middle"
                      }
                      className="chart-axis"
                    >
                      {new Intl.DateTimeFormat("nl-NL", {
                        month: "short",
                        year: period === "3m" ? undefined : "2-digit",
                        day: period === "3m" ? "numeric" : undefined,
                      }).format(new Date(`${rows[i].day}T12:00:00Z`))}
                    </text>
                  ) : null;
                })}
              </svg>
            </div>
          )}
          <div className="human-chart-navigation">
            <label>
              <ZoomIn size={14} />
              Zoom
              <input
                aria-label="Zoom koersgrafiek"
                type="range"
                min="10"
                max="100"
                step="5"
                value={zoom}
                onChange={(e) => {
                  setZoom(Number(e.target.value));
                  setHover(null);
                }}
              />
            </label>
            {zoom < 100 && (
              <label>
                Periode verschuiven
                <input
                  aria-label="Verschuif koersperiode"
                  type="range"
                  min="0"
                  max="100"
                  value={pan}
                  onChange={(e) => {
                    setPan(Number(e.target.value));
                    setHover(null);
                  }}
                />
              </label>
            )}
            <button
              onClick={() => {
                setZoom(100);
                setPan(100);
                setHover(null);
              }}
            >
              <Maximize2 size={13} />
              Hele venster
            </button>
          </div>
          <div className="human-chart-caption">
            <span>
              <i className="zone-green" />
              Groeistand <i className="zone-amber" />
              Voorzichtig <i className="zone-red" />
              Cashsignaal · QQQ-model bij dagslot
            </span>
            <span>
              <ArrowUp size={12} /> <ArrowDown size={12} />
              {markers.length} gelogde simulatie-fills
            </span>
          </div>
          <p className="human-chart-disclaimer">
            Achtergrond = berekende modelstand, geen bewezen rekeningpositie.
            Ruitjes = S1-kans, geen uitvoering. Alleen de gekleurde pijlen zijn
            gelogde simulatie-fills. Split-gecorrigeerde prijzen; geen
            dividendrendement.
          </p>
        </>
      )}
    </section>
  );
}
