"use client";
import { useEffect, useState } from "react";
import {
  Activity,
  LockKeyhole,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";

type AgentState = {
  schema: number;
  kind: string;
  live_locked: boolean;
  mode: string;
  demo_account_verified?: boolean;
  broker_status?: string;
  readiness?: { status: string; ready_to_start: boolean; checks: {code:string;passed:boolean;message:string}[]; blocker_codes:string[] };
  product_review?: {ticker:string;isin:string;currency:string;legal_structure:string;catalog_identity_verified:boolean;backtest_performance_inherited:boolean}[];
  checked_at?: string;
  published_at?: string;
  market?: {
    status: string;
    source_day: string | null;
    expected_day: string;
    independent_check: string;
  };
  broker?: {
    connected: boolean;
    status: string;
    orders_enabled: boolean;
    bindings: number;
    execution_status: string;
  };
  heartbeat?: { age_seconds: number; status: string };
  orders?: { total: number; working: number; unknown: number; filled: number };
  trial?: {
    qualified_sessions: number;
    required_sessions: number;
    status: string;
  };
  forward_trial?: {
    qualified_sessions: number;
    required_sessions: number;
    status: string;
  };
  blockers?: string[];
  blocker?: string;
  halt?: string | null;
  last_local_check?: string;
  note?: string;
  steps?: { number: number; label: string; status: string }[];
  profiles?: Record<
    string,
    {
      state: string;
      core_weight: string;
      trend_weight: string;
      signal_day: string;
    }
  >;
  advice_preview?: Record<
    string,
    {
      state: string;
      core_weight: string;
      trend_weight: string;
      signal_day: string;
    }
  >;
};

const explain: Record<string, string> = {
  CURRENT: "Afgeronde dagdata actueel",
  STALE_OR_UNAVAILABLE: "Nieuwe dagdata ontbreekt of is verouderd",
  NOT_STARTED: "Nog niet gestart",
  DEMO_ACCOUNT_NOT_CONFIGURED: "Nog geen demo-account gekoppeld",
  DEMO_READ_CONNECTED: "Demo kan worden uitgelezen",
  DEMO_RECONCILIATION_REQUIRED: "Verschil met demo-administratie",
  WAITING_FOR_DEMO_ACCOUNT: "Wacht op jouw demo-account",
  PRODUCT_BINDINGS_PENDING: "Productkeuze nog niet bevestigd",
  FRESH_EXECUTION_QUOTE_MISSING: "Actuele uitvoeringsquote ontbreekt",
  WAITING_FOR_EXECUTION_WINDOW: "Wacht op het vaste ordermoment",
  EXECUTION_WINDOW_MISSED_NO_BACKFILL:
    "Ordermoment gemist; geen achteraf-order",
};
const format = (v?: string) =>
  v
    ? new Intl.DateTimeFormat("nl-NL", {
        dateStyle: "medium",
        timeStyle: "short",
        timeZone: "Europe/Amsterdam",
      }).format(new Date(v))
    : "Nog geen meting";

export default function AgentControl() {
  const [state, setState] = useState<AgentState | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    let controller = new AbortController();
    const local =
      process.env.NODE_ENV !== "production" &&
      ["127.0.0.1", "localhost", "[::1]"].includes(window.location.hostname);
    const load = async () => {
      controller.abort();
      controller = new AbortController();
      try {
        const r = await fetch(
          local
            ? "/api/portfolio-forward"
            : "/data/portfolio-os/agent-readiness.json",
          { cache: "no-store", signal: controller.signal },
        );
        if (!r.ok)
          throw Error(
            local
              ? "De lokale agent heeft nog geen leesbare status."
              : "De gepubliceerde bouwstatus is nog niet beschikbaar.",
          );
        const b = await r.json();
        if (b.live_locked !== true)
          throw Error("Onverwachte agentstatus; controle vereist.");
        if (active) {
          setState(b);
          setError("");
        }
      } catch (e) {
        if (active && e instanceof Error && e.name !== "AbortError")
          setError(e.message);
      }
    };
    void load();
    const timer = local ? setInterval(() => void load(), 15000) : undefined;
    return () => {
      active = false;
      controller.abort();
      if (timer) clearInterval(timer);
    };
  }, []);
  const local = state?.kind === "LOCAL_FORWARD_STATUS";
  const trial = state?.trial ?? state?.forward_trial;
  const connected = local ? state?.broker?.connected === true : state?.demo_account_verified === true;
  const brokerPaused = (local ? state?.broker?.status : state?.broker_status) === "DEMO_API_PAUSED_TERMS_REVIEW";
  return (
    <section
      className="human-panel agent-control"
      aria-label="Lokale agent controlekamer"
    >
      <header>
        <div>
          <span className="human-eyebrow">
            VAN ONDERZOEK NAAR DAGELIJKSE CONTROLE
          </span>
          <h2>
            <Activity size={20} /> De agent op je Mac
          </h2>
        </div>
        <span className="agent-lock">
          <LockKeyhole size={14} /> Echte orders geblokkeerd
        </span>
      </header>
      <p className="agent-intro">
        Dezelfde vaste signalen. S1 staat uit. De agent beslist niet met een LLM
        en verandert geen strategieparameters.
      </p>
      <div className="agent-warning">
        <AlertTriangle size={17} />
        <div>
          <strong>Trading 212: automatische API-handel is geblokkeerd</strong>
          <p>De actuele API-voorwaarden verbieden algoritmische handel. De toepassing op demo en de eigen interface moet de broker verduidelijken; de lokale marktcontrole blijft beschikbaar.</p>
          <a href="https://www.trading212.com/legal-documentation/API-Terms_EN.pdf" target="_blank" rel="noopener noreferrer">Lees de API-voorwaarden</a>
        </div>
      </div>
      {error ? (
        <p role="alert" className="agent-warning">
          {error}
        </p>
      ) : !state ? (
        <p className="agent-intro">Agentstatus laden…</p>
      ) : (
        <>
          {!local && (
            <div className="agent-warning">
              <AlertTriangle size={17} />
              <div>
                <strong>
                  Publicatiestand, geen live verbinding met je Mac
                </strong>
                <p>
                  De website toont wat gebouwd is. Actuele broncontroles,
                  heartbeat en demo-orderstatus zijn alleen lokaal beschikbaar.
                </p>
              </div>
            </div>
          )}
          <div className="agent-grid">
            <div>
              <span>Verbinding</span>
              <strong>
                {connected
                  ? local ? "Trading 212-demo uitgelezen" : "Demoverbinding geverifieerd bij publicatie"
                  : brokerPaused ? "Brokerverbinding gepauzeerd" : "Wacht op demo-account"}
              </strong>
              <p>
                {connected
                  ? "Een gelezen rekening is nog geen bewezen orderuitvoering."
                  : brokerPaused ? "De demo was eerder alleen-lezen gekoppeld. Er is geen actuele brokercontrole." : "Er is nog geen actuele, geverifieerde demolezing. Bekijk de startcontrole hieronder."}
              </p>
            </div>
            <div>
              <span>Marktgegevens</span>
              <strong>
                {explain[state.market?.status ?? "NOT_STARTED"] ??
                  "Controle vereist"}
              </strong>
              <p>
                Bron t/m {state.market?.source_day ?? "onbekend"} · verwacht{" "}
                {state.market?.expected_day ?? "onbekend"}. Tweede bron:{" "}
                {state.market?.independent_check === "MATCHED"
                  ? "bevestigd"
                  : "niet bevestigd"}
                .
              </p>
            </div>
            <div>
              <span>Twintig beursdagen proef</span>
              <strong>{trial?.qualified_sessions ?? 0} / 20</strong>
              <p>
                Alleen echte, volledige demo-observatiedagen tellen. Historische
                replays en technische fixtures tellen niet mee.
              </p>
            </div>
          </div>
          {local && (
            <div className="agent-local">
              <span>
                {state.heartbeat?.status === "RECENT" ? (
                  <CheckCircle2 size={15} />
                ) : (
                  <AlertTriangle size={15} />
                )}{" "}
                {state.heartbeat?.status === "RECENT"
                  ? "Agent heeft recent gecontroleerd"
                  : "Agent loopt mogelijk niet of de Mac slaapt"}
              </span>
              <span>Laatste controle: {format(state.checked_at)} NL</span>
              <span>
                Werkende demo-orders: {state.orders?.working ?? 0} · onzeker:{" "}
                {state.orders?.unknown ?? 0}
              </span>
            </div>
          )}
          {!local && (
            <ol className="agent-steps">
              {state.steps?.map((s) => (
                <li key={s.number}>
                  <strong>
                    {s.number}. {s.label}
                  </strong>
                  <span>
                    {s.status === "PAUSED_POLICY_REVIEW"
                      ? "Brokerverbinding gepauzeerd; voorwaarden te verduidelijken"
                      : s.status === "REAL_DEMO_READ_VERIFIED"
                      ? "Echte demo alleen-lezen gecontroleerd"
                      : s.status === "CATALOG_REVIEWED_BINDINGS_PENDING"
                        ? "Catalogus gecontroleerd; productvrijgave ontbreekt"
                        : s.number === 1
                      ? "Exact brokerproduct nog te bevestigen"
                      : s.number === 5
                        ? "Client gebouwd; nog niet verbonden"
                        : s.number === 6
                          ? "Wacht op twintig echte sessies"
                          : s.number === 3
                            ? "Storingen getest met een testserver"
                            : "Gebouwd; draait alleen lokaal"}
                  </span>
                </li>
              ))}
            </ol>
          )}
          {state.readiness && (
            <div className="agent-readiness">
              <h3>{state.readiness.ready_to_start ? "Startcontrole geslaagd voor de demo" : "Startcontrole: nog geen vrijgave voor demo-orders"}</h3>
              <p>{state.readiness.checks.filter(c=>c.passed).length} van {state.readiness.checks.length} controles geslaagd. Een werkende verbinding is één onderdeel van deze controle.</p>
              <ul>
                {state.readiness.checks.map(c=><li key={c.code} className={c.passed?"passed":"pending"}>
                  {c.passed?<CheckCircle2 size={16}/>:<AlertTriangle size={16}/>}
                  <span>{c.message}</span><strong>{c.passed?"Bevestigd":c.code==="BROKER_AUTOMATION_POLICY"?"Geblokkeerd":"Nog te bevestigen"}</strong>
                </li>)}
              </ul>
            </div>
          )}
          {state.product_review && state.product_review.length>0 && (
            <div className="agent-product-review">
              <h3>Producten in de gecontroleerde democatalogus</h3>
              <p>Catalogusvermelding is geen bewijs van fractierechten of uitvoerbaarheid. De Amerikaanse QQQ/TQQQ-prestaties worden niet overgenomen.</p>
              <div className="agent-steps">{state.product_review.map(p=><div key={p.ticker}>
                <strong>{p.ticker} · {p.currency}</strong><span>{p.isin}</span>
                <span>{p.legal_structure.includes("DEBT")?"Schuld-ETP met dagelijkse 3× hefboom; afzonderlijk te toetsen":p.legal_structure.includes("DISTRIBUTING")?"UCITS ETF · uitkerend":"UCITS ETF · herbeleggend"}</span>
              </div>)}</div>
            </div>
          )}
          {Object.keys(state.profiles ?? state.advice_preview ?? {}).length >
            0 && (
            <div className="agent-advice">
              <strong>
                Nieuwe adviesverdeling · nominale gewichten vóór de aparte
                cashbuffer
              </strong>
              <p>
                Afgeronde bronstand; geen rekeningpositie en geen orderopdracht.
              </p>
              <div className="agent-steps">
                {Object.entries(
                  state.profiles ?? state.advice_preview ?? {},
                ).map(([key, a]) => (
                  <div key={key}>
                    <strong>
                      {
                        (
                          {
                            defensive: "Voorzichtig",
                            balanced: "Gebalanceerd",
                            offensive: "Aanvallend",
                          } as Record<string, string>
                        )[key]
                      }
                    </strong>
                    <span>
                      {a.signal_day} · {a.state}
                    </span>
                    <span>
                      1× kern {(Number(a.core_weight) * 100).toFixed(0)}% · 3×{" "}
                      {(Number(a.trend_weight) * 100).toFixed(0)}% ·
                      cash/reserve{" "}
                      {(
                        (1 - Number(a.core_weight) - Number(a.trend_weight)) *
                        100
                      ).toFixed(0)}
                      %
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="agent-warning">
            <AlertTriangle size={17} />
            <div>
              <strong>Wat nog nodig is</strong>
              <p>
                {local
                  ? (state.halt ? `Geblokkeerd: ${state.halt}. ` : "") +
                    (state.blocker ??
                      "Controleer de lokale status voordat je verdergaat.")
                  : state.blockers?.join(" · ")}
              </p>
            </div>
          </div>
          <p className="agent-intro">
            De lokale marktcontrole vraagt een ingeschakelde, wakkere Mac. De
            brokerverbinding is gepauzeerd en de agent plaatst geen orders.
            Historische signalen zijn geen bewijs van Europese uitvoering.
          </p>
          <a className="agent-guide" href="/reports/TRADING212_DEMO_READINESS_2026-10-30.md" target="_blank" rel="noopener noreferrer">
            Lees de volledige product- en startcontrole →
          </a>
          <br />
          <a className="agent-guide" href="/reports/BROKER_ROUTES_AND_API_POLICY_2026-10-30.md" target="_blank" rel="noopener noreferrer">
            Vergelijk de twee brokerroutes en kosten →
          </a>
          <br />
          <a
            className="agent-guide"
            href="/reports/LOCAL_AGENT_EXECUTION_GUIDE_2026-10-30.md"
            target="_blank"
            rel="noopener noreferrer"
          >
            Handleiding, aansluitstappen en stopknop →
          </a>
          <small className="agent-public-date">
            {local ? "Lokale status" : "Bouwstatus gepubliceerd"}:{" "}
            {format(local ? state.checked_at : state.published_at)} NL
          </small>
        </>
      )}
    </section>
  );
}
