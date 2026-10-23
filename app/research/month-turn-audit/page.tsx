import type { Metadata } from 'next';
import Link from 'next/link';
import data from '../../../public/data/month-turn-audit.json';
import './month-turn.css';

export const metadata: Metadata = {
  title: 'QUANTT — Maandwissel-audit',
  description: 'De oorspronkelijke maandwisselregel vergeleken met gewone RTH-marktdrift, vooraf bekende volatiliteit en uitvoeringsrisico. Verkennend onderzoek.',
};

const n = (value: number | null | undefined, digits = 2) => value == null ? '—' : value.toLocaleString('nl-NL', {
  minimumFractionDigits: digits, maximumFractionDigits: digits,
});
const interval = (values: number[]) => `[${n(values[0], 3)}; ${n(values[1], 3)}]`;
const samples = Object.entries(data.samples);
const sourceLabel = (id: string) => id === 'DISCOVERY' ? 'Ontdekkingsperiode' : 'Oudere bron · herkomst onbevestigd';

export default function MonthTurnAudit() {
  return <main lang="nl" className="tom-audit">
    <nav aria-label="Onderzoeksnavigatie">
      <Link href="/research/marathon">← Onderzoeksronde met 25 uitkomsten</Link>
      <a href="/reports/MONTH_TURN_AUDIT.md" download>Volledig rapport</a>
    </nav>
    <header>
      <p className="tom-eyebrow">QUANTT · OORSPRONKELIJKE MAANDWISSELREGEL</p>
      <h1>Meer dan gewone marktdrift?</h1>
      <p className="tom-lead">{data.verdict_text}</p>
      <p className="tom-warning">Geen onafhankelijke holdout. De regels zijn ongewijzigd. Alle gegevens waren al voor onderzoek gebruikt;
        de oudere continuous-reeks heeft onbevestigde contract- en publicatieherkomst. Geen gevalideerd winstmodel.</p>
    </header>

    <section aria-labelledby="tom-rule">
      <h2 id="tom-rule">Wat wordt vergeleken?</h2>
      <p>Laatste cashhandelsdag en eerste drie cashhandelsdagen van de maand. Long vanaf de 09:30-open tot de 15:59-closebar,
        één NQ-contract en $24,50 roundtripkosten. Geen nieuwe filters, stops, targets of positiegrootteregels.</p>
      <p>De blinde long-benchmark handelt op alle complete RTH-dagen. De andere-dagen-benchmark is het complement van de maandwisseldagen.
        Gemiddelden zijn per blootgestelde dag; totale winsten bij verschillende aantallen posities zijn geen gelijke vergelijking.</p>
      <div className="tom-table" tabIndex={0} aria-label="Maandwissel en beide benchmarks">
        <table><caption>Netto na 1,225 punt per ronde · één NQ-punt = $20</caption>
          <thead><tr><th>Bron</th><th>Groep</th><th>Dagen</th><th>Netto totaal pt</th><th>Gem. netto pt</th><th>Mediaan pt</th><th>Win%</th><th>PF</th></tr></thead>
          <tbody>{samples.flatMap(([id, s]) => ([['tom', 'Maandwissel'], ['non_tom', 'Andere dagen'], ['all_rth_long', 'Alle dagen long']] as const).map(([field, label]) => {
            const r = s[field];
            return <tr key={`${id}-${field}`}><th scope="row">{sourceLabel(id)}</th><td>{label}</td><td>{r.days}</td>
              <td>{n(r.net_points)}</td><td>{n(r.mean_net)}</td><td>{n(r.median_net)}</td><td>{n(r.winrate * 100, 1)}</td><td>{n(r.profit_factor, 3)}</td></tr>;
          }))}</tbody>
        </table>
      </div>
    </section>

    <section aria-labelledby="tom-premium">
      <h2 id="tom-premium">Kalenderpremie na volatiliteitsvergelijking</h2>
      <p>Verschil tussen maandwissel en andere dagen. De tweede vergelijking deelt elke netto dagbeweging door de vóór die dag bekende ATR14.
        Dit is een beschrijvende vergelijking in risico-eenheden, geen nieuw handelsfilter.</p>
      <div className="tom-table" tabIndex={0} aria-label="Meerwaarde en onzekerheidsintervallen">
        <table><caption>Vaste tweemaands-blokbootstrap · 10.000 herhalingen · vier verkennende contrasten, Holm4</caption>
          <thead><tr><th>Bron</th><th>Eenheid</th><th>ToM / andere N</th><th>Gem. ToM</th><th>Gem. andere</th><th>Verschil</th><th>95%-interval verschil</th><th>Ruwe p</th><th>Holm4 p</th></tr></thead>
          <tbody>{samples.flatMap(([id, s]) => (['raw_contrast', 'normalized_contrast'] as const).map(field => {
            const r = s[field];
            return <tr key={`${id}-${field}`}><th scope="row">{sourceLabel(id)}</th><td>{field === 'raw_contrast' ? 'Netto punten' : 'Netto / vooraf-ATR'}</td>
              <td>{r.tom_days} / {r.non_tom_days}</td><td>{n(r.tom_mean, 3)}</td><td>{n(r.non_tom_mean, 3)}</td><td>{n(r.difference, 3)}</td>
              <td>{interval(r.difference_ci95)}</td><td>{n(r.p_raw, 5)}</td><td>{n(r.p_holm4, 5)}</td></tr>;
          }))}</tbody>
        </table>
      </div>
      <p className="tom-note">Hele maanden worden samen geresampled; gemiddelden gebruiken gepoolde sommen en aantallen. Intervallen zijn nominaal,
        niet simultaan. De benaderende p-waarden veronderstellen passende zwakke afhankelijkheid en stationariteit. Holm4 corrigeert deze audit,
        niet de volledige eerdere zoektocht. Een positieve simulatie is geen onafhankelijke bevestiging.</p>
      <details><summary>Eerdere onzekerheidsmethoden blijven zichtbaar</summary>
        <p className="tom-note">Voor dezelfde 81 maandwisseltrades gaf de eerdere maandcluster-bootstrap een gemiddeld-netto-interval
          van [−0,113; +111,695] punten; de vijfdaagse marathon-bootstrap gaf [+1,818; +105,682].
          Het nieuwe tweemaandsinterval is geen reden om het eerdere nulbevattende interval weg te laten.
          De huidige benchmark telt bovendien twee december-2024-dagen extra mee, zonder extra ToM-trades.</p>
        <a href="/reports/MONTH_TURN_UNCERTAINTY_CONTEXT.md" download>Volledige toelichting op onzekerheid en steekproefverschillen</a>
      </details>
      <div className="tom-notes">
        {samples.map(([id, s]) => <article key={id}><h3>{sourceLabel(id)}</h3>
          <p>{s.normalization.common_sample_days} dagen hebben vooraf bekende ATR. Daarvan zijn {s.normalization.groups.tom.days} maandwisseldagen.
            De {s.normalization.tom_missing_atr} maandwisseldagen zonder ATR blijven in het oorspronkelijke modelresultaat staan.</p>
          <p>Gemiddelde vooraf-ATR: {n(s.normalization.groups.tom.mean_prior_atr)} punten bij maandwissel,
            tegenover {n(s.normalization.groups.non_tom.mean_prior_atr)} op andere dagen.</p></article>)}
      </div>
    </section>

    <section aria-labelledby="tom-risk">
      <h2 id="tom-risk">Winstconcentratie en werkelijk zichtbare risico’s</h2>
      <div className="tom-table" tabIndex={0} aria-label="Concentratie drawdown en adverse excursion">
        <table><caption>Alleen de oorspronkelijke maandwisseldagen · geen weglaatcontrole verandert de handelsregels</caption>
          <thead><tr><th>Bron</th><th>Top 3 aandeel netto</th><th>Netto zonder top 3 pt</th><th>Gesloten-trade DD pt</th><th>Minuut-close DD pt</th><th>Slechtste dag pt</th><th>MAE mediaan / P95 / max pt</th></tr></thead>
          <tbody>{samples.map(([id, s]) => <tr key={id}><th scope="row">{sourceLabel(id)}</th>
            <td>{n(s.risk.top3_share_of_total_net * 100, 1)}%</td><td>{n(s.risk.without_top3.net_points)}</td>
            <td>{n(s.tom.closed_trade_drawdown)}</td><td>{n(s.risk.minute_close_equity_drawdown)}</td><td>{n(s.tom.worst_day)}</td>
            <td>{n(s.risk.mae.median)} / {n(s.risk.mae.p95)} / {n(s.risk.mae.max)}</td></tr>)}</tbody>
        </table>
      </div>
      <p className="tom-note">Minuut-close-drawdown telt ook verlies tijdens open posities en rekent alle roundtripkosten bij entry.
        Dit is geen tick-drawdown of gegarandeerde intrabar-worst-case. Zonder rekeninggrootte, marginhistorie en risicobudget kunnen we
        niet vaststellen dat deze verliezen financieel aanvaardbaar zijn.</p>
      <details><summary>Alle leave-one-quarter-out controles</summary>
        <div className="tom-table" tabIndex={0}><table><caption>Overblijvende oorspronkelijke trades na weglaten van één kwartaal</caption>
          <thead><tr><th>Bron</th><th>Weggelaten</th><th>Trades</th><th>Netto pt</th><th>Gemiddeld netto pt</th></tr></thead>
          <tbody>{samples.flatMap(([id, s]) => s.risk.leave_one_quarter_out.map(r => <tr key={`${id}-${r.omitted}`}>
            <th scope="row">{sourceLabel(id)}</th><td>{r.omitted}</td><td>{r.days}</td><td>{n(r.net_points)}</td><td>{n(r.mean_net)}</td></tr>))}</tbody>
        </table></div>
      </details>
    </section>

    <section aria-labelledby="tom-execution">
      <h2 id="tom-execution">Kosten en entryvertraging</h2>
      <p>Hetzelfde cohort en dezelfde exit, met drie vooraf vastgelegde entryankers en kostenvarianten. Geen scenario is achteraf tot nieuwe regel gekozen.</p>
      <div className="tom-table" tabIndex={0} aria-label="Alle negen uitvoeringsscenario’s per bron">
        <table><caption>$34,50 en $44,50 zijn één en twee extra ticks per leg bovenop de vaste $24,50</caption>
          <thead><tr><th>Bron</th><th>Entryvertraging min</th><th>RT kosten $</th><th>Trades</th><th>Netto pt</th><th>Gem. netto pt</th><th>PF</th><th>Gesloten DD pt</th></tr></thead>
          <tbody>{samples.flatMap(([id, s]) => s.execution_sensitivity.map(r => <tr key={`${id}-${r.entry_delay_minutes}-${r.roundtrip_cost_usd}`}>
            <th scope="row">{sourceLabel(id)}</th><td>{r.entry_delay_minutes}</td><td>{n(r.roundtrip_cost_usd)}</td><td>{r.days}</td>
            <td>{n(r.net_points)}</td><td>{n(r.mean_net)}</td><td>{n(r.profit_factor, 3)}</td><td>{n(r.closed_trade_drawdown)}</td></tr>))}</tbody>
        </table>
      </div>
      <p className="tom-note">Minuutopens en closes zijn onderzoeksankers. Bid/ask, latency, queue en daadwerkelijke fills zijn niet bewezen.
        De technische volledigheid van een dag is achteraf vastgesteld en mag niet worden uitgelegd als een vóór entry bekende selectievoorwaarde.</p>
    </section>

    <section aria-labelledby="tom-source">
      <h2 id="tom-source">Broncontrole en beperkingen</h2>
      <p>Op {data.source_parity.complete_common_days} gemeenschappelijke volledige NQH24-pilotdagen was de RTH-open/closebeweging
        voor {n(data.source_parity.exact_rth_movement_fraction * 100, 1)}% exact gelijk aan de generieke reeks.
        De grootste afwijking was {n(data.source_parity.maximum_abs_difference_points)} punt.
        Dit controleert niet de volledige oudere keten. De eerder gevonden 15,5-puntsafwijking op een twee-minutenanker blijft gedocumenteerd.</p>
      <p>Beide oorspronkelijke ToM-ledgers zijn vanaf de bronbars gereproduceerd, inclusief dezelfde dagen, bruto/netto en MFE/MAE.
        De {data.protected_files} bestaande bestanden blijven ongewijzigd. Geen nieuwe holdout, aankoop, live orders of externe publicatie.</p>
    </section>
    <footer>
      <a href="/reports/MONTH_TURN_AUDIT.md" download>Volledig rapport · Markdown</a>
      <a href="/data/month-turn-audit.json" download>Afgeleide cijfers · JSON</a>
      <a href="/data/month-turn-audit-verification.json" download>Reproductie en controles · JSON</a>
      <Link href="/research/marathon">Terug naar eerdere onderzoeksronde</Link>
    </footer>
  </main>;
}
