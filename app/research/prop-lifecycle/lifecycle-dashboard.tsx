'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';

type Row = {
  era: string; firm: string; model: string; MNQ: number; horizon: string; starts: number;
  known_evaluation_passes: number; evaluation_pass_rate: number;
  payout1_all_starts: number; payout2_all_starts: number; unknown_rate: number;
  failures: number; censored: number; mean_net_cash_per_start_USD: number | null;
  median_eval_cash_sessions_if_passed: number | null;
  mean_eval_calendar_days_if_passed: number | null;
  buffer2600_rate_given_pass: number | null;
  payout1_rate_given_pass: number | null; payout2_rate_given_pass: number | null;
  partial_identification_cash_bounds_USD: [number, number];
};
type Payload = { rows: Row[]; sources: Record<string, string> };
const pct = (x: number | null) => x == null ? '—' : `${(100*x).toLocaleString('nl-NL', {maximumFractionDigits: 1})}%`;
const number = (x: number | null) => x == null ? '—' : x.toLocaleString('nl-NL', {maximumFractionDigits: 1});

export default function LifecycleDashboard() {
  const [payload, setPayload] = useState<Payload | null>(null);
  const [error, setError] = useState('');
  const [firm, setFirm] = useState('TOPSTEP_STANDARD');
  const [era, setEra] = useState('COMBINED');
  const [horizon, setHorizon] = useState('252_SESSIONS');
  useEffect(() => {
    const abort = new AbortController();
    fetch('/data/prop-lifecycle/summary.json', {signal: abort.signal})
      .then(r => { if (!r.ok) throw Error('Het levenscyclusrapport kon niet worden geladen.'); return r.json(); })
      .then(setPayload).catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    return () => abort.abort();
  }, []);
  const rows = payload?.rows.filter(r => r.firm === firm && r.era === era && r.horizon === horizon) ?? [];
  return <main className="pc-page" lang="nl">
    <nav aria-label="Onderzoeksnavigatie">
      <Link href="/research/prop-challenge">← Challenge-onderzoek</Link>
      <Link href="/research/prop-firm">Bestaande prop-studie</Link>
      <a href="/reports/PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md">Volledig rapport</a>
      <a href="/data/prop-lifecycle/summary.csv" download>Alle aggregaten · CSV</a>
    </nav>
    <header>
      <div className="pc-eyebrow">QUANT / ACCOUNTLEVENSCYCLUS / 26 OKTOBER 2026</div>
      <h1>Een pass is pas<br/><span>het begin.</span></h1>
      <p className="pc-intro">Drie bestaande portefeuilles, vaste 1 of 2 MNQ en aparte rekeningregels. Van een nieuwe evaluatie tot twee uitbetalingen, zonder verliesgevende extra pijlers.</p>
      <div className="pc-status">Ontwikkelingsonderzoek · geen onafhankelijk gevalideerd handelsmodel</div>
    </header>
    <section className="pc-controls" aria-label="Rapportfilters">
      <label>Programma en payout-route<select value={firm} onChange={e => setFirm(e.target.value)}>
        <option value="TOPSTEP_STANDARD">Topstep 50K · XFA Standard</option>
        <option value="TOPSTEP_CONSISTENCY">Topstep 50K · XFA Consistency</option>
        <option value="MFFU_BUILDER">MFFU Builder 50K · officiële inactiviteitsregel</option>
        <option value="MFFU_BUILDER_NO_EVAL_INACTIVITY_SENSITIVITY">Builder · hypothetisch zonder eval-inactiviteit</option>
      </select></label>
      <label>Periode<select value={era} onChange={e => setEra(e.target.value)}>
        <option value="COMBINED">Beide perioden</option>
        <option value="2019_2021">2019–2021</option>
        <option value="2024_2026">Recent blok · vanaf januari 2025</option>
      </select></label>
      <label>Beschikbare follow-up<select value={horizon} onChange={e => setHorizon(e.target.value)}>
        <option value="252_SESSIONS">Gelijk venster · 252 cashsessies</option>
        <option value="ERA_END">Iedere start · tot einde eigen periode</option>
      </select></label>
    </section>
    {error && <p role="alert" className="pc-error">{error}</p>}
    {!payload && !error && <p role="status">Rapport laden…</p>}
    <section>
      <h2>Wat blijft er per gestart account over?</h2>
      <p>De payout-percentages gebruiken alle starts als noemer. Actief aan het einde betekent onvoltooid. Bij ontbrekende bronminuten is de netto dollarverwachting onbekend; onbekend wordt nooit als nul ingevuld.</p>
      <div className="pc-table"><table>
        <thead><tr><th scope="col">Bestaand model</th><th scope="col">MNQ</th><th scope="col">Starts</th><th scope="col">Evaluatie gehaald</th><th scope="col">Eerste payout</th><th scope="col">Tweede payout</th><th scope="col">Gefaald</th><th scope="col">Actief einde</th><th scope="col">Bronpad onbekend</th><th scope="col">Netto $ per start</th></tr></thead>
        <tbody>{rows.map(r => <tr key={`${r.model}-${r.MNQ}`}>
          <th scope="row">{r.model}</th><td>{r.MNQ}</td><td>{r.starts}</td>
          <td>{pct(r.evaluation_pass_rate)}</td><td>{pct(r.payout1_all_starts)}</td><td>{pct(r.payout2_all_starts)}</td>
          <td>{pct(r.failures)}</td><td>{pct(r.censored)}</td><td>{pct(r.unknown_rate)}</td>
          <td>{r.mean_net_cash_per_start_USD == null ? <>Onbekend<small>Mogelijke band: ${number(r.partial_identification_cash_bounds_USD[0])} tot ${number(r.partial_identification_cash_bounds_USD[1])}</small></> : `$${number(r.mean_net_cash_per_start_USD)}`}</td>
        </tr>)}</tbody>
      </table></div>
    </section>
    <section>
      <h2>Na een bekende evaluatiepass</h2>
      <p>De tijdsduur geldt alleen voor geslaagde evaluaties. De $2.600 is voor Topstep een vergelijkingspunt, geen verplichte buffer. Payouts kunnen daar eerder plaatsvinden.</p>
      <div className="pc-table"><table>
        <thead><tr><th scope="col">Model</th><th scope="col">MNQ</th><th scope="col">Bekende passes</th><th scope="col">Mediane cashdagen tot pass</th><th scope="col">Gemiddelde kalenderdagen</th><th scope="col">Buffer bereikt / passes</th><th scope="col">Payout 1 / passes</th><th scope="col">Payout 2 / passes</th></tr></thead>
        <tbody>{rows.map(r => <tr key={`${r.model}-${r.MNQ}`}>
          <th scope="row">{r.model}</th><td>{r.MNQ}</td><td>{r.known_evaluation_passes}</td>
          <td>{number(r.median_eval_cash_sessions_if_passed)}</td><td>{number(r.mean_eval_calendar_days_if_passed)}</td>
          <td>{pct(r.buffer2600_rate_given_pass)}</td><td>{pct(r.payout1_rate_given_pass)}</td><td>{pct(r.payout2_rate_given_pass)}</td>
        </tr>)}</tbody>
      </table></div>
    </section>
    <aside className="pc-notes">
      <h2>Lees de uitkomst op de juiste schaal</h2>
      <p>Netto dollars zijn ontvangen payouts na winstdeling minus aankoop, evaluatie-abonnementen en activatie, tot de tweede payout of het einde van de follow-up. Resterend rekeningsaldo is geen ontvangen geld. Geen automatische retries, belasting, transfer- of automatiseringskosten meegerekend.</p>
      <p>Alle startvensters overlappen. Dit zijn geen onafhankelijke accountproeven. Ontbrekende nachtminuten, conservatieve intrabarvolgorde en NQ-prijzen als MNQ-proxy begrenzen de conclusie. Er zijn geen accounts gekocht of orders verzonden.</p>
      <details><summary>Officiële bronnen en regels</summary><ul>{Object.entries(payload?.sources ?? {}).map(([name,url]) => <li key={name}><a href={url}>{name}</a></li>)}</ul></details>
    </aside>
  </main>;
}
