import Link from "next/link";
import "../research.css";
import snapshot from "../../../public/data/research09.json";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "QUANTT 0.9 — Observed Futures Research",
  description: "Audit-first observed NQ/ES data readiness; never synthetic market-performance claims.",
};

type Source = { instrument: string; source: string; rows: number; contracts: string[];
  observed_gaps: number; calendar_verified: boolean; contract_provenance_verified: boolean };
type Horizon = { complete_events: number; mean_forward_points: number | null;
  mean_mfe_points: number | null; mean_mae_points: number | null; inference: string };
type Snapshot = { schema_version: string; classification: string; status: string;
  row_count: number; edge_validated: boolean; sources: Source[];
  descriptive_forward: Record<string, Record<string,Horizon>>;
  limitations: string[] };

const data = snapshot as Snapshot;
const number = (value: number | null | undefined) =>
  value == null ? "—" : value.toLocaleString("en-US", { maximumFractionDigits: 3 });

export default function ObservedResearch() {
  const hasData = data.status === "STAGED_UNVERIFIED" && data.sources.length > 0;
  return (
    <main className="r08-workspace">
      <header className="r08-head">
        <div>
          <Link href="/research" className="r08-back">← Research Command Center 0.8</Link>
          <div className="r08-kicker">QUANTT · RELEASE 0.9 · OBSERVED FUTURES</div>
          <h1>Data-Ready Research</h1>
          <p>Actual source audit and descriptive forward screens, separate from simulated Release 0.8.</p>
        </div>
        <div className="r08-tag">NO VALIDATED EDGES</div>
      </header>
      <div className="r08-provenance">
        <span className="r08-tag">Status: {data.status}</span>
        <span className="r08-tag">Classification: {data.classification}</span>
        <span className="r08-tag">Observed bars: {number(data.row_count)}</span>
        <span className="r08-tag">Verified edges: 0</span>
      </div>
      {!hasData && (
        <section style={{ border: "1px solid #324157", borderRadius: 12, background: "#141e2d", padding: 24, marginBottom: 24 }}>
          <h2 style={{ fontSize: 20, color: "#e5f1ff" }}>Awaiting licensed contract-native NQ/ES input</h2>
          <p style={{ color: "#a4b5ce", marginTop: 12 }}>
            The 0.9 research importer is ready, but no audited CME futures observations have been published.
            This view does not substitute synthetic research results or claim exchange-verified provenance.
          </p>
          <p style={{ color: "#a4b5ce", marginTop: 12 }}>
            Use the private CSV-to-Parquet-to-research command documented in docs/RELEASE09_DATA_READY.md.
            Publication of aggregate research requires separate authorization.
          </p>
        </section>
      )}
      {hasData && (
        <>
          <h2 style={{ fontSize: 20, marginBottom: 12 }}>Staged source coverage — unverified</h2>
          <div style={{ overflowX: "auto", marginBottom: 24 }}>
            <table style={{ borderCollapse: "collapse", width: "100%", color: "#c9dbf1" }}>
              <thead><tr>{["Instrument", "Source", "One-minute bars", "Contract IDs", "Raw gaps", "Origin verified"].map(x =>
                <th key={x} style={{ padding: 12, textAlign: "left", borderBottom: "1px solid #334660" }}>{x}</th>
              )}</tr></thead>
              <tbody>{data.sources.map((s, i) => <tr key={String(i)}>
                <td style={{ padding: 12 }}>{s.instrument}</td>
                <td style={{ padding: 12 }}>{s.source}</td>
                <td style={{ padding: 12 }}>{number(s.rows)}</td>
                <td style={{ padding: 12 }}>{s.contracts.join(", ")}</td>
                <td style={{ padding: 12 }}>{number(s.observed_gaps)} (calendar not reconciled)</td>
                <td style={{ padding: 12 }}>No</td>
              </tr>)}</tbody>
            </table>
          </div>
          <h2 style={{ fontSize: 20, marginBottom: 12 }}>Descriptive forward windows — not a backtest</h2>
          <div style={{ overflowX: "auto", marginBottom: 24 }}>
            <table style={{ borderCollapse: "collapse", width: "100%", color: "#c9dbf1" }}>
              <thead><tr>{["Family", "Horizon", "Complete events", "Mean forward pts", "Mean MFE", "Mean MAE"].map(x =>
                <th key={x} style={{ padding: 12, textAlign: "left", borderBottom: "1px solid #334660" }}>{x}</th>
              )}</tr></thead>
              <tbody>{Object.entries(data.descriptive_forward).flatMap(([family, windows]) =>
                Object.entries(windows).map(([h, r]) => <tr key={family + h}>
                  <td style={{ padding: 12 }}>{family}</td><td style={{ padding: 12 }}>{h}m</td>
                  <td style={{ padding: 12 }}>{number(r.complete_events)}</td>
                  <td style={{ padding: 12 }}>{number(r.mean_forward_points)}</td>
                  <td style={{ padding: 12 }}>{number(r.mean_mfe_points)}</td>
                  <td style={{ padding: 12 }}>{number(r.mean_mae_points)}</td>
                </tr>)
              )}</tbody>
            </table>
          </div>
        </>
      )}
      <section style={{ border: "1px solid #324157", borderRadius: 12, padding: 20, marginTop: 24 }}>
        <h2 style={{ fontSize: 18, marginBottom: 10 }}>Research governance</h2>
        <p style={{ color: "#a4b5ce", marginBottom: 12 }}>
          Source license, CME provenance, exchange calendar, rollover policy and broker execution
          remain unverified. No sealed holdout was evaluated. This release cannot certify a trading edge.
        </p>
        <ul style={{ paddingLeft: 18, color: "#a4b5ce" }}>
          {data.limitations.map((line, i) => <li key={i} style={{ marginBottom: 6 }}>{line}</li>)}
        </ul>
      </section>
    </main>
  );
}
