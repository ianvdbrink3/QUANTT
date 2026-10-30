"use client";

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  Check,
  CheckCircle2,
  ChevronRight,
  Clock3,
  HelpCircle,
  Info,
  Landmark,
  LockKeyhole,
  Moon,
  RefreshCw,
  Search,
  ShieldCheck,
  Wallet,
  X,
} from "lucide-react";
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
import {
  dutchDate,
  growthPoints,
  marketCopy,
} from "@/lib/portfolio-friendly.mjs";
import PortfolioChart from "./portfolio-chart";

const tabs = [
  "Overzicht",
  "Koersen & signalen",
  "Kosten & brokers",
  "Dagboek & controle",
];
const profiles: Record<Profile, string> = {
  defensive: "Voorzichtig",
  balanced: "Gebalanceerd",
  offensive: "Aanvallend",
};
const planNames: Record<Profile, string> = {
  defensive: "Defensief",
  balanced: "Gebalanceerd",
  offensive: "Offensief",
};
const brokerNames: Record<string, string> = {
  trading212: "Trading 212",
  ibkr: "Interactive Brokers",
  degiro: "DEGIRO",
  alpaca: "Alpaca (testomgeving)",
};
const sleeveNames = [
  "Nasdaq-100 · QQQ",
  "Turbo · TQQQ",
  "Nachtkansen · reserve",
  "Vrije cash",
];
const eur = (v: number | null | undefined) =>
  v == null ? "Onbekend" : `€ ${num(v)}`;

function Help({ text }: { text: string }) {
  return (
    <span className="human-help" tabIndex={0} role="note" aria-label={text}>
      <HelpCircle size={14} />
      <span role="tooltip">{text}</span>
    </span>
  );
}
function Title({
  eyebrow,
  title,
  help,
  children,
}: {
  eyebrow?: string;
  title: string;
  help?: string;
  children?: ReactNode;
}) {
  return (
    <div className="human-panel-heading">
      <div>
        {eyebrow && <span className="human-eyebrow">{eyebrow}</span>}
        <h2>
          {title}
          {help && <Help text={help} />}
        </h2>
      </div>
      {children}
    </div>
  );
}
function Clocks() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  const c = now ? terminalClockContext(now) : null;
  const time = (zone: string) =>
    now
      ? new Intl.DateTimeFormat("nl-NL", {
          timeZone: zone,
          hour: "2-digit",
          minute: "2-digit",
        }).format(now)
      : "—";
  return (
    <div className="human-clocks">
      <Clock3 size={16} />
      <span>
        New York <b>{time("America/New_York")}</b>
      </span>
      <span>
        Nederland <b>{time("Europe/Amsterdam")}</b>
      </span>
      <small>{c?.offset_hours ?? "—"} uur verschil</small>
    </div>
  );
}

function Advice({
  state,
  broker,
  amount,
  deposit,
  onCosts,
}: {
  state: OSState;
  broker: string;
  amount: number;
  deposit: number;
  onCosts: () => void;
}) {
  const copy = marketCopy(state.regime.state_code),
    q = state.telemetry.QQQ,
    n = state.s1.conditions.slice(0, 3).filter((c) => c.passed).length;
  const costs = state.costs.find((c) => c.key === broker)!,
    fits = costs.roundtrip_bp != null && costs.gates["5"].mathematical_pass;
  const core = terminalSleeves(state, state.active_profile)[0];
  return (
    <section
      className={`human-advice tone-${copy.tone}`}
      aria-label="Advies bij de laatste meting"
    >
      <div className="human-advice-intro">
        <span className="human-status-icon">
          {state.regime.state_code === 2 ? (
            <ArrowUpRight size={24} />
          ) : state.regime.state_code === 1 ? (
            <Activity size={24} />
          ) : (
            <ShieldCheck size={24} />
          )}
        </span>
        <div>
          <div className="human-eyebrow">
            ADVIES BIJ DE LAATSTE METING · {dutchDate(state.market_asof)}
          </div>
          <h1>{copy.headline}</h1>
          <p>{copy.description}</p>
        </div>
        <span className={`human-badge ${copy.tone}`}>{copy.title}</span>
      </div>
      <div className="human-advice-grid">
        <div>
          <Wallet size={19} />
          <div>
            <h3>Waar staat je geld?</h3>
            <p>
              Je kern heeft <b>{eur(core.value)}</b> aan waarde in de simulatie.
              QQQ staat <b>{num(q.distance_sma200_pct)}%</b>{" "}
              {q.distance_sma200_pct >= 0 ? "boven" : "onder"} de lange
              veiligheidslijn.
            </p>
          </div>
        </div>
        <div>
          <Moon size={19} />
          <div>
            <h3>Is er een nachtkans?</h3>
            <p>
              <b>{n} van 3</b> voorwaarden gehaald.{" "}
              {state.s1.signal
                ? "Het model ziet een kans, maar nachtorders staan uit."
                : "Er is geen actief S1-signaal."}{" "}
              Er worden geen echte orders geplaatst.
            </p>
          </div>
        </div>
        <div>
          <Landmark size={19} />
          <div>
            <h3>En je maandelijkse {eur(deposit)}?</h3>
            <p>
              {fits
                ? `${brokerNames[broker]} past bij ${eur(amount)} binnen de kostenlimiet in dit rekenmodel.`
                : `Bij ${brokerNames[broker]} is doorsparen nodig, of de kostengrens is niet haalbaar.`}{" "}
              Dit is een rekensom, geen ingelegde cash.
            </p>
            <button className="human-text-button" onClick={onCosts}>
              Bekijk de kosten <ChevronRight size={13} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function Allocation({
  state,
  profile,
  setProfile,
  deposit,
  setDeposit,
}: {
  state: OSState;
  profile: Profile;
  setProfile: (p: Profile) => void;
  deposit: number;
  setDeposit: (v: number) => void;
}) {
  const rows = terminalSleeves(state, profile),
    preview = profile !== state.active_profile,
    last = state.audit.days.at(-1)!,
    nav = Number(last.nav_reference),
    dd = Number(last.drawdown) * 100,
    limit = state.profiles[state.active_profile].dd_limit_pct;
  return (
    <section className="human-panel human-allocation">
      <Title
        eyebrow="JOUW PORTEFEUILLE"
        title="Een verdeling die je begrijpt"
        help="De profielkeuze is een voorbeeld. De werkelijke simulatie, de actieve regels en je eerdere transacties veranderen niet."
      />
      <div className="human-profile-picker" aria-label="Profielpreview">
        {(Object.keys(profiles) as Profile[]).map((p) => (
          <button
            key={p}
            aria-pressed={profile === p}
            className={profile === p ? "selected" : ""}
            onClick={() => setProfile(p)}
          >
            {profiles[p]}
          </button>
        ))}
      </div>
      <div
        className="human-allocation-bar"
        aria-label="Verdeling per onderdeel"
      >
        {rows.map((r, i) => (
          <span
            key={r.sleeve}
            className={`sleeve-color-${i}`}
            style={{ width: `${r.weight * 100}%` }}
            title={`${sleeveNames[i]} ${num(r.weight * 100, 0)}%`}
          >
            {r.weight >= 0.2 ? `${num(r.weight * 100, 0)}%` : ""}
          </span>
        ))}
      </div>
      <div className="human-sleeve-list">
        {rows.map((r, i) => (
          <div key={r.sleeve}>
            <i className={`sleeve-color-${i}`} />
            <span>
              {sleeveNames[i]}
              {i === 2 && (
                <small>Nachtorders staan uit; dit deel blijft reserve</small>
              )}
            </span>
            <b>{num(r.weight * 100, 0)}%</b>
            <strong>{eur(r.value)}</strong>
          </div>
        ))}
      </div>
      <p className="human-preview-note">
        <Info size={14} />
        {preview
          ? `Je bekijkt ${profiles[profile].toLowerCase()}. Het actieve profiel blijft ${profiles[state.active_profile].toLowerCase()}.`
          : "Dit zijn de geaggregeerde bedragen van de actieve simulatie."}
      </p>
      <div className="human-capital-row">
        <div>
          <span>
            Totale waarde{" "}
            <Help text="Referentie-euro's met FX=1. Dit is geen werkelijk brokertegoed en geen bewezen EUR-rendement." />
          </span>
          <strong>{eur(nav)}</strong>
        </div>
        <div>
          <span>
            Onder de eerdere top{" "}
            <Help text="De terugval van de portefeuille ten opzichte van de hoogste flow-gecorrigeerde waarde; stortingen tellen niet als winst." />
          </span>
          <strong className="text-amber">{num(dd)}%</strong>
          <small>Noodrem bij {limit}% · actieve regels</small>
        </div>
      </div>
      <div className="human-risk-track">
        <span style={{ width: `${Math.min(100, (dd / limit) * 100)}%` }} />
      </div>
      <label className="human-deposit">
        Maandelijkse inleg voor je groeiscenario
        <select
          aria-label="Scenario maandinleg"
          value={deposit}
          onChange={(e) => setDeposit(Number(e.target.value))}
        >
          <option value={100}>€100 per maand</option>
          <option value={250}>€250 per maand</option>
        </select>
      </label>
      <p className="human-note">
        De verdeling geldt na de aparte kasbuffer: minimaal €10 of 1% blijft
        beschikbaar. Daarom kan ook bij 0% cash nog een kleine reserve staan.
      </p>
      <ActualCurve state={state} />
    </section>
  );
}

function ActualCurve({ state }: { state: OSState }) {
  const points = state.audit.days.map((d) =>
    Number(d.unit_nav ?? Number(d.nav_reference) / 1000),
  );
  const lo = Math.min(...points) - 0.001,
    hi = Math.max(...points) + 0.001;
  const line = points
    .map(
      (v, i) =>
        `${i ? "L" : "M"}${(i / Math.max(1, points.length - 1)) * 500},${77 - ((v - lo) / (hi - lo)) * 68}`,
    )
    .join(" ");
  return (
    <details className="human-actual-curve">
      <summary>Hoe liep de bestaande simulatie?</summary>
      <p>
        Indexwaarde <b>{num(points.at(-1), 4)}</b>. Inleg telt hier niet als
        koerswinst.
      </p>
      <svg
        viewBox="0 0 500 86"
        role="img"
        aria-label="Werkelijk gelogd, flow-gecorrigeerd waardeverloop van de simulatie"
      >
        <path d={line} className="chart-price" />
      </svg>
      <small>
        {dutchDate(state.replay.first)} — {dutchDate(state.replay.last)} ·
        actieve regels blijven gelijk
      </small>
    </details>
  );
}

function Indicators({ state }: { state: OSState }) {
  return (
    <section className="human-panel human-indicators">
      <Title
        eyebrow="DE VEILIGHEIDSLIJNEN"
        title="Hoe ver staat de koers van de noodrem?"
        help="Het model gebruikt de gemiddelden van 20 en 200 afgeronde beursdagen. Deze lijnen beperken risico in het model, maar garanderen geen verliesgrens."
      />
      <div className="human-asset-grid">
        {(["QQQ", "TQQQ"] as const).map((asset) => {
          const d = state.telemetry[asset],
            above = d.distance_sma200_pct >= 0;
          return (
            <article key={asset}>
              <div className="human-asset-heading">
                <span
                  className={`human-asset-symbol ${asset === "TQQQ" ? "purple" : ""}`}
                >
                  {asset === "QQQ" ? (
                    <Landmark size={21} />
                  ) : (
                    <Activity size={21} />
                  )}
                </span>
                <div>
                  <h3>
                    {asset === "QQQ" ? "Nasdaq-100 · QQQ" : "Turbo · TQQQ"}
                  </h3>
                  <small>
                    {asset === "QQQ"
                      ? "Je 1× kern"
                      : "3× dagelijkse blootstelling"}
                  </small>
                </div>
                <strong>${num(d.close)}</strong>
              </div>
              <div className="human-line-value">
                <span>
                  Lange veiligheidslijn{" "}
                  <Help text="Het gemiddelde slot van de laatste 200 beursdagen. Onder deze lijn geeft het model een uitstapsignaal, geen gegarandeerde verkoopprijs." />
                </span>
                <b>${num(d.sma200)}</b>
              </div>
              <div className={`human-distance ${above ? "green" : "red"}`}>
                <span
                  style={{
                    width: `${Math.min(100, Math.max(5, 50 + d.distance_sma200_pct * 2))}%`,
                  }}
                />
              </div>
              <p className={above ? "text-green" : "text-red"}>
                {above ? "+" : ""}
                {num(d.distance_sma200_pct)}% {above ? "boven" : "onder"} de
                200-daagse lijn
              </p>
              <div className="human-short-line">
                <span>Korte trend · 20 dagen</span>
                <b>${num(d.sma20)}</b>
                <span
                  className={
                    d.distance_sma20_pct >= 0 ? "text-green" : "text-amber"
                  }
                >
                  {num(d.distance_sma20_pct)}%
                </span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function NightScanner({ state }: { state: OSState }) {
  const q = state.telemetry.QQQ,
    checks = state.s1.conditions.slice(0, 3),
    labels = [
      "Koers boven het 20-daags gemiddelde",
      "Slot in de bovenste 15% van de dagrange",
      "Dagbeweging minstens 85% van de normale range",
    ];
  const values = [
    `$${num(q.close)} tegenover $${num(q.sma20)}`,
    `Kracht-score ${num(q.ibs * 100, 1)}% · vereist 85%`,
    `$${num(q.high - q.low)} tegenover $${num(0.85 * q.atr14_pre)}`,
  ];
  return (
    <section className="human-panel human-night">
      <Title
        eyebrow="S1 KANSEN-SCANNER"
        title="De nacht-sluipschutter"
        help="Een avondsignaal op basis van QQQ. De dagelijkse range wordt vergeleken met de gemiddelde true range van de voorgaande 14 dagen; echte nachtorders zijn uitgeschakeld."
      />
      <div
        className={`human-scanner-status ${state.s1.signal ? "green" : "amber"}`}
      >
        <Moon size={23} />
        <div>
          <strong>
            {state.s1.signal
              ? "Een kans in het model"
              : "Vanavond geen actief modelsignaal"}
          </strong>
          <small>
            Op basis van {dutchDate(state.market_asof)}, niet van een actuele
            livekoers
          </small>
        </div>
      </div>
      <div className="human-checklist">
        {checks.map((c, i) => (
          <div key={c.key}>
            <span className={c.passed ? "check-yes" : "check-no"}>
              {c.passed ? <Check size={16} /> : <X size={16} />}
            </span>
            <div>
              <strong>{labels[i]}</strong>
              <small>{values[i]}</small>
            </div>
            <b className={c.passed ? "text-green" : "text-red"}>
              {c.passed ? "Ja" : "Nee"}
            </b>
          </div>
        ))}
      </div>
      <p className="human-note">
        Daarnaast moet de markt in de groeistand staan:{" "}
        <b>{state.regime.state_code === 2 ? "ja" : "nee"}</b>. Alle nachtorders
        blijven uit totdat productrechten en bescherming zijn bevestigd.
      </p>
    </section>
  );
}

function Growth({
  state,
  profile,
  deposit,
}: {
  state: OSState;
  profile: Profile;
  deposit: number;
}) {
  const [years, setYears] = useState(10),
    [hover, setHover] = useState<number | null>(null),
    annual =
      profile === "defensive" ? 0.06 : profile === "balanced" ? 0.08 : 0.1;
  const points = growthPoints(1000, deposit, years, annual),
    last = points.at(-1)!,
    selected = points[Math.min(hover ?? points.length - 1, points.length - 1)];
  const w = 1000,
    h = 205,
    l = 18,
    r = 80,
    b = 30,
    t = 12,
    max = last.value * 1.08,
    x = (m: number) => l + ((w - l - r) * m) / (years * 12),
    y = (v: number) => h - b - ((h - b - t) * v) / max;
  const line = (k: "value" | "contributions") =>
    points.map((p, i) => `${i ? "L" : "M"}${x(p.month)},${y(p[k])}`).join(" ");
  const saved = state.scenarios.find(
    (s) =>
      s.profile === planNames[profile] &&
      Number(s.monthly_eur) === deposit &&
      Number(s.years) === years,
  );
  return (
    <section className="human-panel human-growth">
      <Title
        eyebrow="JE GELD OP LANGE TERMIJN"
        title="Wat als je elke maand blijft inleggen?"
        help="Een rekenvoorbeeld met vast rendement, geen verwachting uit een backtest. Belastingen, inflatie en echte euro-wisselkoersen zijn niet inbegrepen."
      >
        <div className="human-segment">
          {[5, 10].map((v) => (
            <button
              key={v}
              className={years === v ? "selected" : ""}
              aria-pressed={years === v}
              onClick={() => {
                setYears(v);
                setHover(null);
              }}
            >
              {v} jaar
            </button>
          ))}
        </div>
      </Title>
      <div className="human-growth-stats">
        <div>
          <span>
            <i className="legend-contribution" />
            Je eigen inleg
          </span>
          <strong>{eur(selected.contributions)}</strong>
        </div>
        <div>
          <span>
            <i className="legend-growth" />
            Rekenvoorbeeld bij {num(annual * 100, 0)}% per jaar
          </span>
          <strong className="text-green">{eur(selected.value)}</strong>
        </div>
        <p>
          Start met €1.000
          <br />
          en {eur(deposit)} per maand.
        </p>
      </div>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        role="img"
        aria-label={`Groeiscenario ${years} jaar, eigen inleg ${eur(last.contributions)}, rekenvoorbeeld ${eur(last.value)}`}
        onPointerMove={(e) => {
          const box = e.currentTarget.getBoundingClientRect();
          setHover(
            Math.max(
              0,
              Math.min(
                points.length - 1,
                Math.round(
                  ((((e.clientX - box.left) / box.width) * w - l) /
                    (w - l - r)) *
                    (years * 12),
                ),
              ),
            ),
          );
        }}
        onPointerLeave={() => setHover(null)}
      >
        {[0, 1, 2, 3].map((i) => {
          const val = (max * i) / 3;
          return (
            <g key={i}>
              <line
                x1={l}
                x2={w - r}
                y1={y(val)}
                y2={y(val)}
                className="chart-grid"
              />
              <text x={w - r + 12} y={y(val) + 4} className="chart-axis">
                €{num(val, 0)}
              </text>
            </g>
          );
        })}
        <path
          d={`${line("value")}L${x(years * 12)},${h - b}L${l},${h - b}Z`}
          fill="#10b981"
          fillOpacity=".07"
        />
        <path d={line("contributions")} className="chart-contributions" />
        <path d={line("value")} className="chart-growth" />
        {hover !== null && (
          <line
            x1={x(hover)}
            x2={x(hover)}
            y1={t}
            y2={h - b}
            className="chart-crosshair"
          />
        )}
        {[0, years / 2, years].map((v) => (
          <text
            key={v}
            x={x(v * 12)}
            y={h - 6}
            className="chart-axis"
            textAnchor={v === 0 ? "start" : v === years ? "end" : "middle"}
          >
            {v === 0 ? "Vandaag" : `Na ${num(v, 1)} jaar`}
          </text>
        ))}
      </svg>
      <div className="human-growth-foot">
        <span>
          Na {years} jaar:{" "}
          <b>{eur(Number(saved?.planning_central_eur ?? last.value))}</b> in het
          vaste rekenscenario.
        </span>
        <span>
          Bij −5% per jaar:{" "}
          <b>{eur(Number(saved?.adverse_minus5pct_pa_eur ?? 0))}</b>.
        </span>
      </div>
      <p className="human-note">
        Dit is geen belofte. De gekleurde groei is een aanname van{" "}
        {num(annual * 100, 0)}% per jaar, geen gemeten modelrendement. De
        actieve portefeuille wordt hierdoor niet aangepast.
      </p>
    </section>
  );
}

type CostProps = {
  state: OSState;
  amount: number;
  setAmount: (v: number) => void;
  spread: number;
  setSpread: (v: number) => void;
  broker: string;
  setBroker: (v: string) => void;
  gate: string;
  setGate: (v: string) => void;
  deposit: number;
};
function CostCheck({
  state,
  amount,
  setAmount,
  spread,
  setSpread,
  broker,
  setBroker,
  gate,
  setGate,
  deposit,
}: CostProps) {
  const routes = terminalCostRows(state.costs, gate),
    selected = routes.find((c) => c.key === broker)!,
    known = selected.roundtrip_bp !== null,
    total =
      ((selected.roundtrip_bp ?? selected.lower_bound_bp) * amount) / 10000,
    extra = selected.gate.extra_eur;
  return (
    <section className="human-panel human-cost">
      <Title
        eyebrow="MEER VAN JE INLEG OVERHOUDEN"
        title="Wat kost kopen én weer verkopen?"
        help="De schatting telt twee orderkanten, de volledige spread en 0,01% extra slippage. Kostenlimieten zijn modelaannames en bevestigen geen broker- of producttoegang."
      />
      <div className="human-cost-inputs">
        <label>
          Bedrag van je aankoop
          <input
            aria-label="Orderbudget in euro"
            type="number"
            min="1"
            max="1000000"
            value={amount}
            onChange={(e) =>
              setAmount(Math.max(1, Math.min(1e6, Number(e.target.value) || 1)))
            }
          />
        </label>
        <label>
          Geschatte spread{" "}
          <Help text="Het verschil tussen de koop- en verkoopprijs, als percentage van het aankoopbedrag." />
          <select
            aria-label="Volledige spread in basispunten"
            value={spread}
            onChange={(e) => setSpread(Number(e.target.value))}
          >
            {[0, 1, 2, 3, 5, 10].map((v) => (
              <option key={v} value={v}>
                {num(v / 100, 2)}%
              </option>
            ))}
          </select>
        </label>
        <label>
          Maximale kosten
          <select
            aria-label="Frictiepoort"
            value={gate}
            onChange={(e) => setGate(e.target.value)}
          >
            <option value="5">0,05% · strikte grens</option>
            <option value="10">0,10% · ruimere grens</option>
          </select>
        </label>
      </div>
      <div className="human-cost-table">
        <table>
          <thead>
            <tr>
              <th>Broker / rekenmodel</th>
              <th>Vaste & procentuele orderkosten</th>
              <th>Totaal heen + terug</th>
              <th>Deel van je aankoop</th>
              <th>Bedrag voor ≤{num(Number(gate) / 100, 2)}%</th>
            </tr>
          </thead>
          <tbody>
            {routes.map((c) => (
              <tr key={c.key} className={c.key === broker ? "selected" : ""}>
                <th>
                  <button
                    onClick={() => setBroker(c.key)}
                    aria-label={`Broker ${c.label}`}
                  >
                    <span className="human-radio" aria-hidden="true" />
                    {brokerNames[c.key]}
                  </button>
                </th>
                <td>{eur(c.fee_eur)}</td>
                <td>
                  {c.roundtrip_bp == null ? "Minstens " : ""}
                  {eur(((c.roundtrip_bp ?? c.lower_bound_bp) * amount) / 10000)}
                </td>
                <td
                  className={
                    c.math_status === "MATH_PASS" ? "text-green" : "text-amber"
                  }
                >
                  {c.roundtrip_bp == null ? "≥ " : ""}
                  {num((c.roundtrip_bp ?? c.lower_bound_bp) / 100, 3)}%
                </td>
                <td>
                  {c.key === "alpaca"
                    ? "Nog onbekend"
                    : c.gate.minimum_eur == null
                      ? "Niet haalbaar"
                      : eur(c.gate.minimum_eur)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div
        className={`human-savings ${selected.math_status === "MATH_PASS" ? "green" : "amber"}`}
      >
        <Wallet size={24} />
        <div>
          <h3>
            {!known
              ? "De totale kosten zijn nog niet bekend."
              : selected.gate.mathematical_pass
                ? "Dit bedrag past binnen je kostenlimiet."
                : extra == null
                  ? "Ook met meer sparen blijft deze kostengrens onhaalbaar."
                  : `Nog ${eur(extra)} sparen voor deze kostengrens.`}
          </h3>
          <p>
            Bij {brokerNames[broker]} kost {eur(amount)} kopen én verkopen{" "}
            {known ? "naar schatting" : "minstens"} <b>{eur(total)}</b> (
            {num((selected.roundtrip_bp ?? selected.lower_bound_bp) / 100, 3)}
            %).{" "}
            {extra != null && extra > 0
              ? `Met ${eur(deposit)} per maand is dat circa ${Math.ceil(extra / deposit)} maanden sparen.`
              : ""}
          </p>
          <p className="human-small">
            Voorwaardelijke rekensom. Geen vaste commissie betekent niet dat
            spread, slippage of overige kosten nul zijn.
          </p>
        </div>
      </div>
      <p className="human-note">
        <LockKeyhole size={13} />
        Brokerrechten en producttoegang zijn nog niet bevestigd. Een gunstige
        kostencheck geeft geen toestemming om een order te plaatsen.
      </p>
    </section>
  );
}

function Audit({ state }: { state: OSState }) {
  const [query, setQuery] = useState(""),
    [filter, setFilter] = useState("all"),
    [day, setDay] = useState(""),
    [mode, setMode] = useState("brief");
  const rows = useMemo(
    () =>
      terminalDays(state.audit.days, "", filter).filter((d) =>
        `${d.day} ${marketCopy(d.advisor.state === "BULL" ? 2 : d.advisor.state === "PULLBACK" ? 1 : 0).title} ${JSON.stringify(d.decisions)}`
          .toLowerCase()
          .includes(query.toLowerCase()),
      ),
    [state.audit.days, query, filter],
  );
  const current =
      state.audit.days.find((d) => d.day === day) ?? state.audit.days.at(-1)!,
    brief = state.briefs.find((b) => b.day === current.day),
    intents = state.audit.intents.filter((i) => i.day === current.day);
  return (
    <div className="human-audit-grid">
      <section className="human-panel">
        <Title eyebrow="VOLG DE BESLISSINGEN" title="Je dagboek" />
        <div className="human-audit-tools">
          <label>
            <Search size={16} />
            <input
              aria-label="Zoek in audit"
              placeholder="Zoek een datum of marktstatus"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
          <select
            aria-label="Auditfilter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">Alle dagen</option>
            <option value="fills">Met een simulatie-order</option>
            <option value="cost">Te hoge kosten</option>
            <option value="data">Gegevens ontbreken</option>
          </select>
        </div>
        <div className="human-audit-scroll">
          <table>
            <thead>
              <tr>
                <th>Beursdag</th>
                <th>Marktstatus</th>
                <th>Wat gebeurde er?</th>
                <th>Onder de top</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((d) => (
                <tr
                  key={d.day}
                  className={d.day === current.day ? "selected" : ""}
                >
                  <th>
                    <button
                      aria-label={`Inspecteer ${d.day}`}
                      onClick={() => setDay(d.day)}
                    >
                      {dutchDate(d.day)}
                    </button>
                  </th>
                  <td>
                    {d.advisor.state === "BULL"
                      ? "Groei"
                      : d.advisor.state === "PULLBACK"
                        ? "Korte dip"
                        : "Noodrem"}
                  </td>
                  <td>
                    {d.has_data_skip
                      ? "Koersanker ontbreekt"
                      : d.has_cost_block
                        ? "Kosten blokkeren order"
                        : d.fills
                          ? `${d.fills} simulatie-fill${d.fills > 1 ? "s" : ""}`
                          : "Geen transactie"}
                  </td>
                  <td>{num(Number(d.drawdown) * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && (
            <p className="human-note">
              Geen dagen gevonden voor deze selectie.
            </p>
          )}
        </div>
      </section>
      <section className="human-panel human-inspector">
        <Title eyebrow="DE DAG IN GEWONE TAAL" title={dutchDate(current.day)} />
        <div className="human-chart-tabs">
          <button
            className={mode === "brief" ? "selected" : ""}
            onClick={() => setMode("brief")}
          >
            Dagoverzicht
          </button>
          <button
            className={mode === "orders" ? "selected" : ""}
            onClick={() => setMode("orders")}
          >
            Orderdetails ({intents.length})
          </button>
        </div>
        {mode === "brief" ? (
          <div className="human-day-summary">
            <div
              className={`human-badge ${current.advisor.state === "BULL" ? "green" : "amber"}`}
            >
              {current.advisor.state === "BULL"
                ? "Opwaartse trend"
                : current.advisor.state === "PULLBACK"
                  ? "Dip binnen de lange trend"
                  : "Noodrem van het model"}
            </div>
            <h3>
              {current.has_data_skip
                ? "De simulatie heeft niet gehandeld zonder betrouwbaar koersanker."
                : current.fills
                  ? "De simulatie heeft een order uitgevoerd."
                  : "Er was geen nieuwe transactie nodig."}
            </h3>
            <p>
              Portefeuillewaarde in de simulatie:{" "}
              <b>{eur(Number(current.nav_reference))}</b>. De waarde staat{" "}
              <b>{num(Number(current.drawdown) * 100)}%</b> onder de eerdere
              top.
            </p>
            <p>
              {current.has_cost_block
                ? "De kosten waren te hoog voor de ingestelde limiet."
                : current.has_data_skip
                  ? "Een ontbrekende minuutkoers is niet vervangen door een geschatte uitvoering."
                  : "Dit verslag gebruikt historische koersen en synthetische spreads, geen echte brokerfills."}
            </p>
            <details>
              <summary>Oorspronkelijk verslag en technische details</summary>
              <pre>{brief?.markdown ?? "Geen verslag beschikbaar."}</pre>
            </details>
          </div>
        ) : (
          <div className="human-order-details">
            {intents.length ? (
              intents.map((i) => (
                <article key={i.id}>
                  <h3>
                    {i.side === "BUY" ? "Koop" : "Verkoop"} {i.key} ·{" "}
                    {i.status === "FILLED"
                      ? "Uitgevoerd in simulatie"
                      : i.status}
                  </h3>
                  <p>
                    {i.reason === "APPROVED_SHADOW_ONLY"
                      ? "Alleen goedgekeurd binnen de historische simulatie. Geen echte order verstuurd."
                      : "Raadpleeg het oorspronkelijke besluit in de gegevens hieronder."}
                  </p>
                  <details>
                    <summary>
                      Controlecode en oorspronkelijke ordergegevens
                    </summary>
                    <dl>
                      <dt>Unieke orderhash</dt>
                      <dd>{i.id}</dd>
                      <dt>Regelset-hash</dt>
                      <dd>{i.policy_hash}</dd>
                      <dt>Handtekening</dt>
                      <dd>
                        Proceslokaal; niet bewaard (PROCESS_LOCAL /
                        NOT_RETAINED)
                      </dd>
                    </dl>
                    <pre>{JSON.stringify(i, null, 2)}</pre>
                  </details>
                </article>
              ))
            ) : (
              <p>Op deze dag zijn geen orders aangemaakt.</p>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

function Evidence({ state }: { state: OSState }) {
  return (
    <details className="human-evidence">
      <summary>
        <ShieldCheck size={16} />
        Verantwoording, gegevensdekking en controles{" "}
        <span>Alleen simulatie</span>
      </summary>
      <div>
        <p>
          De historische replay bevat <b>{state.replay.days} beursdagen</b>.
          Exacte uitvoeringsankers zijn beschikbaar voor{" "}
          <b>
            {state.replay.days - state.replay.missing_minute_quote_days}/
            {state.replay.days}
          </b>{" "}
          dagen. Uitgevoerde simulatie-fills: <b>{state.replay.fills}</b>.
        </p>
        <p>
          Een historische replay bewijst geen onafhankelijke forwardfase
          (REPLAY_ONLY). Brokerrechten zijn onbevestigd; strategisch bewijs
          blijft onvoldoende. De profielkiezer verandert geen actieve regels
          (VIEW ≠ POLICY_CHANGE).
        </p>
        <p>
          Huidige regelset: <code>{state.policy_hash}</code>.{" "}
          {state.policy_hash === state.audit.meta.policy_hash
            ? "De hash komt overeen met het auditlog."
            : "Let op: de hashes komen niet overeen."}
        </p>
        <p>
          Vergelijking voor de lange trend: zonder buffer / ±0,5% buffer / twee
          dagen bevestiging. QQQ:{" "}
          {["naked", "schmitt", "confirm2"]
            .map((k) =>
              state.telemetry.QQQ.anti_whipsaw[k as "naked"]
                ? "belegd"
                : "cash",
            )
            .join(" / ")}
          . Dit wijzigt de gekozen signalen niet.
        </p>
        <p>
          Dagbar-anker 09:30: 2469/2469 voor beide fondsen. Geselecteerde
          uitvoeringsroute: {state.replay.execution_timing}.
        </p>
      </div>
    </details>
  );
}

export default function PortfolioOS() {
  const [state, setState] = useState<OSState | null>(null),
    [error, setError] = useState(""),
    [tab, setTab] = useState(1),
    [dataset, setDataset] = useState("current");
  const [profile, setProfile] = useState<Profile>("defensive"),
    [deposit, setDeposit] = useState(100),
    [amount, setAmount] = useState(100),
    [spread, setSpread] = useState(3),
    [gate, setGate] = useState("5"),
    [broker, setBroker] = useState("trading212"),
    [refresh, setRefresh] = useState(0);
  const [budget, setBudget] = useState(amount),
    [quoteSpread, setQuoteSpread] = useState(spread),
    refs = useRef<(HTMLButtonElement | null)[]>([]);
  useEffect(() => {
    const t = setTimeout(() => {
      setBudget(amount);
      setQuoteSpread(spread);
    }, 180);
    return () => clearTimeout(t);
  }, [amount, spread]);
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
        if (!response.ok)
          throw Error(
            "De gegevens zijn tijdelijk niet beschikbaar. Vernieuw de pagina of controleer de lokale agent.",
          );
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
    const onKey = (e: KeyboardEvent) => {
      const typing =
        e.target instanceof Element &&
        !!e.target.closest('input,textarea,select,[contenteditable="true"]');
      const t = terminalShortcut(
        e.key,
        typing,
        e.metaKey || e.ctrlKey || e.altKey,
      );
      if (t) {
        e.preventDefault();
        setTab(t);
        refs.current[t - 1]?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  if (!state)
    return (
      <main className="human-app human-loading" lang="nl">
        <Activity size={30} />
        <h1>Je portefeuille wordt geladen</h1>
        <p>{error || "We halen de laatste onderzoeksgegevens op."}</p>
        {error && (
          <button onClick={() => setRefresh((v) => v + 1)}>
            Opnieuw proberen
          </button>
        )}
      </main>
    );
  // One input snapshot for percentages and euro amounts, including during API refresh.
  const costState = { ...state, costs: publicCostRoutes(amount, spread) };
  const costs: CostProps = {
    state: costState,
    amount,
    setAmount,
    spread,
    setSpread,
    broker,
    setBroker,
    gate,
    setGate,
    deposit,
  };
  return (
    <div className="human-app" lang="nl">
      <header className="human-header">
        <a className="human-brand" href="/portfolio-os">
          <span>
            <Activity size={23} />
          </span>
          <div>
            <b>QUANT</b>
            <small>Jouw portefeuille, uitgelegd.</small>
          </div>
        </a>
        <Clocks />
        <div className="human-header-status">
          <span className="human-badge blue">
            <LockKeyhole size={12} />
            Alleen simulatie
          </span>
          <small>Marktdata t/m {dutchDate(state.market_asof)}</small>
        </div>
      </header>
      <nav className="human-navigation" aria-label="Portefeuille werkbladen">
        <div role="tablist" aria-label="Werkbladen">
          {tabs.map((label, i) => (
            <button
              key={label}
              ref={(el) => {
                refs.current[i] = el;
              }}
              role="tab"
              id={`human-tab-${i + 1}`}
              aria-selected={tab === i + 1}
              aria-controls="human-workspace"
              onClick={() => setTab(i + 1)}
            >
              {label}
              <kbd>{i + 1}</kbd>
            </button>
          ))}
        </div>
        <div>
          <label>
            Onderzoeksperiode
            <select
              aria-label="DATASET"
              value={dataset}
              onChange={(e) => setDataset(e.target.value)}
            >
              {state.datasets.map((d) => (
                <option key={d.key} value={d.key}>
                  {d.key === "current"
                    ? "Laatste opgeslagen overzicht"
                    : d.key === "60d_recent"
                      ? "60 recente dagen · minuutanker"
                      : d.key === "60d_complete"
                        ? "60 volledig gedekte dagen"
                        : "60 dagen · officiële openingskoers"}
                </option>
              ))}
            </select>
          </label>
          <button
            aria-label="State vernieuwen"
            title="Gegevens vernieuwen"
            onClick={() => setRefresh((v) => v + 1)}
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </nav>
      <main
        className="human-main"
        id="human-workspace"
        role="tabpanel"
        aria-labelledby={`human-tab-${tab}`}
      >
        {error && (
          <div className="human-error" role="alert">
            {error}
          </div>
        )}
        {tab === 1 ? (
          <>
            <Advice
              state={costState}
              broker={broker}
              amount={amount}
              deposit={deposit}
              onCosts={() => setTab(3)}
            />
            <div className="human-overview-grid">
              <PortfolioChart state={state} />
              <Allocation
                state={state}
                profile={profile}
                setProfile={setProfile}
                deposit={deposit}
                setDeposit={setDeposit}
              />
            </div>
            <div className="human-analysis-grid">
              <Indicators state={state} />
              <NightScanner state={state} />
            </div>
            <Growth state={state} profile={profile} deposit={deposit} />
            <CostCheck {...costs} />
          </>
        ) : tab === 2 ? (
          <>
            <PortfolioChart state={state} expanded />
            <div className="human-analysis-grid">
              <Indicators state={state} />
              <NightScanner state={state} />
            </div>
          </>
        ) : tab === 3 ? (
          <>
            <CostCheck {...costs} />
            <div className="human-analysis-grid">
              <Allocation
                state={state}
                profile={profile}
                setProfile={setProfile}
                deposit={deposit}
                setDeposit={setDeposit}
              />
              <Growth state={state} profile={profile} deposit={deposit} />
            </div>
          </>
        ) : (
          <Audit state={state} />
        )}
        <Evidence state={state} />
        <footer className="human-footer">
          <span>
            <LockKeyhole size={13} />
            Geen live-orders · historische onderzoeksdata · geen gegarandeerde
            opbrengst
          </span>
          <span>
            Marktprijzen in dollars · referentie-euro’s zonder
            wisselkoerscorrectie
          </span>
        </footer>
      </main>
    </div>
  );
}
