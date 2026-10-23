import type { Metadata } from 'next';
import Link from 'next/link';
import data from '../../../public/data/edge-marathon.json';
import './marathon.css';

export const metadata: Metadata = {
  title: 'QUANTT — Autonome onderzoeksronde',
  description: 'Alle 25 vastgelegde NQ-uitkomsten, bronfragmenten en onzekerheid. Geen onafhankelijk gevalideerd winstmodel.',
};

type Row = {
  id: string; label: string; rank: number; serious_discovery_candidate: boolean;
  metrics: { trades: number; net_points: number; mean_net?: number | null; winrate: number | null;
    profit_factor: number | null; drawdown?: number | null; positive_quarter_fraction: number | null;
    quarters: number; top3_share_of_net?: number | null; mae?: { median: number; p90: number } };
  inference: { bootstrap95: number[] | null; signflip_p: number; signflip_holm25: number;
    conservative_status: string; conservative_holm25: number };
  historical_replications: { sample: string; trades: number; net_points: number;
    profit_factor: number | null; ci95: number[] | null; p_holm_all_sources: number }[];
};

const rows: Row[] = data.scorecard;
const number = (n: number | null | undefined, digits = 2) => n == null ? '—' : n.toLocaleString('nl-NL', {
  minimumFractionDigits: digits, maximumFractionDigits: digits,
});
const ci = (value: number[] | null) => value ? `[${number(value[0])}; ${number(value[1])}]` : 'Onvoldoende data';
const paths = data.phase1_paths.ALL;
const older = 'CONTINUOUS_2022_2024_UNVERIFIED';
const compared = ['TOM_RTH', 'TOM_ATR_CAP', 'FRIDAY_CONT', 'COMPRESSED_BREAK5', 'SWEEP_REV_1200', 'AFTERNOON_V2_2', 'AFTERNOON_V2_15'];

export default function MarathonResearch() {
  return <main lang="nl" className="marathon">
    <nav aria-label="Onderzoeksnavigatie" className="marathon-nav">
      <Link href="/research/nq">← Bestaand NQ-onderzoeksarchief</Link>
      <a href="/data/edge-marathon.json" download>Resultaten downloaden · JSON</a>
    </nav>

    <header className="marathon-header">
      <p className="marathon-eyebrow">QUANTT · ONDERZOEKSRONDE · 22 OKTOBER 2026</p>
      <h1>Meer getest. Geen onafhankelijke bevestiging.</h1>
      <p className="marathon-lead">De drie maandwisselvarianten lossen de onzekerheid niet op. De bestaande 15:00-observatie is sterk op ontdekkingsdata,
        maar negatief op een grotere oudere bron met onbevestigde herkomst. Alle vooraf gekozen uitkomsten staan hieronder.</p>
      <p className="marathon-warning">Verkennend onderzoek, geen live-handelsadvies. Bronnen met overlappende dagen zijn niet samengevoegd.
        De bevroren v2-specificatie en beschermde archieven zijn niet aangepast.</p>
    </header>

    <section className="marathon-counters" aria-label="Onderzoeksbereik">
      {[
        ['Vaste uitkomsten', data.registered_outcomes], ['Ontdekkingsdagen', data.discovery_complete_days],
        ['Unieke bronbestanden', data.unique_source_contents], ['Onafhankelijk gevalideerde modellen', data.independent_validation_passes],
      ].map(([label, value]) => <div key={String(label)}><span>{label}</span><strong>{value}</strong></div>)}
    </section>

    <section aria-labelledby="marathon-evidence">
      <h2 id="marathon-evidence">Ontdekking tegenover oudere bron</h2>
      <p>493 complete oudere continuous-sessies. De contractketen, adjustmentmethode en publicatievintages zijn niet gecertificeerd.
        Deze bron is dus een afzonderlijke gevoeligheidscontrole, geen definitieve onafhankelijke holdout.</p>
      <div className="marathon-table" tabIndex={0} aria-label="Vergelijking van ontdekkingsdata en oudere bron">
        <table><caption>Netto na $24,50 per ronde · één NQ-contract · geen gepoolde resultaten</caption>
          <thead><tr><th>Model</th><th>Discovery N</th><th>Discovery netto pt</th><th>Oudere bron N</th><th>Oudere netto pt</th><th>Oudere PF</th><th>Oudere 95%-interval</th></tr></thead>
          <tbody>{compared.map(id => {
            const r = rows.find(row => row.id === id)!;
            const h = r.historical_replications.find(source => source.sample === older);
            return <tr key={id}><th scope="row">{r.label}</th><td>{r.metrics.trades}</td><td>{number(r.metrics.net_points)}</td>
              <td>{h?.trades ?? '—'}</td><td>{number(h?.net_points)}</td><td>{number(h?.profit_factor, 3)}</td><td>{h ? ci(h.ci95) : 'Niet geselecteerd'}</td></tr>;
          })}</tbody>
        </table>
      </div>
    </section>

    <section aria-labelledby="marathon-scorecard">
      <h2 id="marathon-scorecard">Volledige Master Scorecard</h2>
      <p>Alle 25 uitkomsten blijven in de Holm-correctie staan, ook lege subgroepen. Intervallen zijn nominale dagblok-bootstrapintervallen.
        Een groen ontdekkingsscherm is geen onafhankelijke validatie.</p>
      <div className="marathon-table" tabIndex={0} aria-label="Alle vooraf vastgelegde hypothesen">
        <table><caption>435 reeds onderzochte RTH-dagen · vaste parameters · kosten inbegrepen</caption>
          <thead><tr><th>Rang</th><th>Uitkomst</th><th>N</th><th>Netto pt</th><th>PF</th><th>Win%</th><th>+ kwartalen</th><th>95%-interval gem. netto pt</th><th>Holm25 signflip</th><th>Conservatieve meetlat</th></tr></thead>
          <tbody>{rows.map(r => <tr key={r.id}>
            <td>{r.rank}</td><th scope="row">{r.label}<small>{r.id}</small></th><td>{r.metrics.trades}</td>
            <td>{number(r.metrics.net_points)}</td><td>{number(r.metrics.profit_factor, 3)}</td>
            <td>{r.metrics.winrate == null ? '—' : number(r.metrics.winrate * 100, 1)}</td>
            <td>{r.metrics.positive_quarter_fraction == null ? '—' : `${number(r.metrics.positive_quarter_fraction * 100, 1)}% / ${r.metrics.quarters}`}</td>
            <td>{ci(r.inference.bootstrap95)}</td><td>{number(r.inference.signflip_holm25, 5)}</td>
            <td>{r.inference.conservative_status === 'DATA_INSUFFICIENT' ? 'Onvoldoende informatie' : `Holm ${number(r.inference.conservative_holm25, 5)}`}</td>
          </tr>)}</tbody>
        </table>
      </div>
      <p className="marathon-note">Bij de 162 v2-events blijven na de vaste kalendergaps 109 gescoorde events over; de conservatieve toets vereist 120.
        Die grens is niet verlaagd. Signflip veronderstelt teken-symmetrie; de ruwe p is bij grotere groepen een Monte-Carlo-schatting.
        De Holm-berekening zelf is exact.</p>
    </section>

    <section aria-labelledby="marathon-paths">
      <h2 id="marathon-paths">Waar zit de maandwisselbeweging?</h2>
      <p>De oorspronkelijke basis blijft exact 81 trades en +4.364,025 netto punten. Geen van de drie vaste varianten brengt de 95%-ondergrens boven nul.</p>
      <div className="marathon-table" tabIndex={0}>
        <table><caption>Bruto beweging op ToM-dagen · vaste deelvensters, niet geoptimaliseerd</caption>
          <thead><tr><th>Venster</th><th>N</th><th>Gemiddeld pt</th><th>Mediaan pt</th><th>P10 pt</th><th>P90 pt</th></tr></thead>
          <tbody>{[
            ['18:00–09:30 · overnight', paths.overnight_points], ['09:30–11:00', paths.morning],
            ['11:00–14:00', paths.midday], ['14:00–16:00', paths.afternoon],
          ].map(([label, value]) => {
            const r = value as typeof paths.morning;
            return <tr key={String(label)}><th scope="row">{String(label)}</th><td>{r.days}</td><td>{number(r.mean)}</td>
              <td>{number(r.distribution.median)}</td><td>{number(r.distribution.p10)}</td><td>{number(r.distribution.p90)}</td></tr>;
          })}</tbody>
        </table>
      </div>
      <p className="marathon-note">Interbar-open/closebruggen staan afzonderlijk in het volledige lokale rapport. Het nieuwe dagblok-interval van de basis
        is nipt positief; het eerdere maandblok-interval bevatte nul. Dat is gevoeligheid voor de meetmethode, geen verbeterd model.</p>
    </section>

    <section aria-labelledby="marathon-sources">
      <h2 id="marathon-sources">Bronnen en resterende onzekerheid</h2>
      <p>{data.source_paths} lokale CSV-paden zijn gehasht en tot {data.unique_source_contents} unieke byte-inhouden gegroepeerd.
        Hogere timeframes zijn niet omgebouwd tot ontbrekende minuten. Technische compleetheid bewijst geen onafhankelijke herkomst.</p>
      <div className="marathon-table" tabIndex={0}>
        <table><caption>Extra sessies per afzonderlijke bron · niet optellen als onafhankelijke steekproeven</caption>
          <thead><tr><th>Bron</th><th>Periode</th><th>Complete sessies</th><th>Status</th></tr></thead>
          <tbody>{data.source_quality.map(q => <tr key={q.sample}><th scope="row">{q.sample}</th>
            <td>{q.period.join(' — ')}</td><td>{q.complete_days}</td><td>Fragment / herkomst niet volledig gecertificeerd</td></tr>)}</tbody>
        </table>
      </div>
      <p className="marathon-note">De acht januaridagen uit 2019 zijn een apart fragment, niet de afgeronde driejaarsproef.
        De oudere continuous-data en de H24-pilot overlappen in datums. De oktober-2026-sample is historische data, geen prospectieve forwardtest.</p>
      <details><summary>Uitvoeringsrisico en onderzoeksmethode</summary>
        <p>Entries gebruiken de open ná een bevestigde barclose. Uitstappen zijn vooraf vastgelegde barcloses. Geen stops, targets of bewezen tickfills.
          Basiskosten $24,50; stress op $34,50 en $44,50. Dag-Sharpe en Sortino gebruiken één-contract punt-P&amp;L, geen rekeningrendement.</p>
        <p>Positieve rijen zijn gecontroleerd met leave-one-day/quarter-out, winstconcentratie, MFE/MAE en extra frictie. De uitslagen zijn verkennend;
          geen nieuw model wordt als onafhankelijk gevalideerd gepresenteerd. Ruwe CSV&apos;s en individuele tradeledgers blijven privé.</p>
      </details>
    </section>
    <footer className="marathon-footer">
      <a href="/data/edge-marathon.json" download>Alle afgeleide cijfers · JSON</a>
      <a href="/reports/AUTONOMOUS_EDGE_DISCOVERY_SUMMARY.md" download>Korte onderzoeksstatus · Markdown</a>
      <Link href="/research/nq">Terug naar het ongewijzigde archief</Link>
    </footer>
  </main>;
}
