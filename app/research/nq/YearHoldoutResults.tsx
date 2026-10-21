import data from '../../../public/data/research-year-holdout.json';
import verification from '../../../public/data/research-year-holdout-verification.json';

const names = { B_ORB15: 'ORB 15m · primair', B_ORB5: 'ORB 5m · referentie', A_London_sweep: 'London Sweep · referentie', C_VWAP_extreme: 'VWAP Extreme · referentie' };
const order = ['B_ORB15', 'B_ORB5', 'A_London_sweep', 'C_VWAP_extreme'] as const;
const number = (value: number | null | undefined, digits = 2) => value == null ? 'n.v.t.' : value.toLocaleString('nl-NL', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const pct = (value: number | null) => value == null ? 'n.v.t.' : `${number(100 * value, 1)}%`;
const share = (value: number | null) => value == null ? 'n.v.t.' : `${number(value, 1)}%`;
const checkNames: Record<string, string> = { sample_size: 'Minstens 20 eligible dagen', net_profit: 'Netto resultaat boven nul', profit_factor: 'Profit factor boven 1', positive_95pct_lower_bound: '95%-ondergrens boven nul', significant_primary_test: 'Tweezijdige p onder 0,05' };

export default function YearHoldoutResults() {
  const primary = data.results.year.B_ORB15.metrics;
  return <section id="year-holdout" className="nq-section" aria-labelledby="year-holdout-title">
    <p className="nq-eyebrow">EENMALIGE JAAR-HOLDOUT · OKTOBER 2025–SEPTEMBER 2026 · NU VERBRUIKT</p>
    <h2 id="year-holdout-title">ORB 15m: {data.status}</h2>
    <p className="nq-lead">Vaste regels, één NQ, $24,50 roundtripkosten en 249 technisch eligible dagen per model. Alleen het jaarresultaat van ORB 15m bepaalt de vooraf vastgelegde promotiebeslissing. De andere modellen en gecombineerde historie zijn uitsluitend beschrijvend.</p>
    <div className="nq-grid">
      <article className="nq-card"><h3>{number(primary.net_points)} punten netto</h3><p>${number(primary.net_usd)} over {primary.trades} trades. Winrate {pct(primary.win_rate)}, profit factor {number(primary.profit_factor, 3)}.</p></article>
      <article className="nq-card"><h3>Onzekerheid van het daggemiddelde</h3><p>95%-block-bootstrapinterval: {number(primary.ci_low)} tot {number(primary.ci_high)} netto punten per eligible dag. Tweezijdige primaire p={number(primary.p_value, 6)}. Eligible nultrade-dagen tellen mee.</p></article>
      <article className="nq-card"><h3>Risico en concentratie</h3><p>Maximale gesloten-trade drawdown: {number(primary.max_drawdown_points)} punten. Grootste verliesdag: {number(primary.worst_day_points)} punten. Top3-aandeel van de netto winst: {share(primary.best3_share_net_profit_pct)} (niet gedefinieerd bij nettoverlies).</p></article>
    </div>
    <h3>Vooraf geldende criteria</h3>
    <ul>{Object.entries(data.primary_checks).map(([key, passed]) => <li key={key}>{checkNames[key]}: {passed ? 'gehaald' : 'niet gehaald'}</li>)}</ul>
    {(['year', 'combined'] as const).map(period => <div key={period}>
      <h3>{period === 'year' ? 'Jaar-holdout · 1 oktober 2025–30 september 2026' : 'Gecombineerd · 30 december 2024–30 september 2026 · niet onafhankelijk'}</h3>
      <div className="nq-table"><table>
        <caption>Vaste kosten · geen opgeteld portfolio · nominale p-waarden; correctie aanvullende familie in rapport</caption>
        <thead><tr>{['Model','Eligible','Trades','Netto punten','Netto USD','Winrate','PF','Max DD punten','95% CI daggemiddelde','p'].map(h => <th key={h} scope="col">{h}</th>)}</tr></thead>
        <tbody>{order.map(strategy => { const m = data.results[period][strategy].metrics; return <tr key={strategy}>
          <th scope="row">{names[strategy]}</th><td>{m.eligible_days}</td><td>{m.trades}</td><td>{number(m.net_points)}</td><td>${number(m.net_usd)}</td><td>{pct(m.win_rate)}</td><td>{number(m.profit_factor,3)}</td><td>{number(m.max_drawdown_points)}</td><td>{number(m.ci_low)} tot {number(m.ci_high)}</td><td>{number(m.p_value,6)}</td>
        </tr>; })}</tbody>
      </table></div>
      <details className="nq-details"><summary>Maanden, long/short, kosten en MFE/MAE · {period === 'year' ? 'jaar' : 'gecombineerd'}</summary>
        {order.map(strategy => { const r = data.results[period][strategy]; return <div key={strategy}>
          <h4>{names[strategy]}</h4>
          <p>Grootste verliesdag: {r.metrics.worst_day}, {number(r.metrics.worst_day_points)} punten. Top3-aandeel: {share(r.metrics.best3_share_net_profit_pct)}. Netto zonder beste3 trades: {number(r.metrics.net_points_without_best3)} punten.</p>
          <div className="nq-table"><table><caption>Maandverdeling</caption><thead><tr><th scope="col">Maand</th><th scope="col">Eligible</th><th scope="col">Trades</th><th scope="col">Netto punten</th><th scope="col">Winrate</th><th scope="col">PF</th></tr></thead><tbody>{r.monthly.map(m => <tr key={m.month}><th scope="row">{m.month}</th><td>{m.eligible_days}</td><td>{m.trades}</td><td>{number(m.net_points)}</td><td>{pct(m.win_rate)}</td><td>{number(m.profit_factor,3)}</td></tr>)}</tbody></table></div>
          <p>Long: {r.direction.long.trades} trades, {number(r.direction.long.net_points)} punten, PF {number(r.direction.long.profit_factor,3)}, winrate {pct(r.direction.long.win_rate)}. Short: {r.direction.short.trades} trades, {number(r.direction.short.net_points)} punten, PF {number(r.direction.short.profit_factor,3)}, winrate {pct(r.direction.short.win_rate)}.</p>
          <ul>{r.cost_sensitivity.map(m => <li key={m.cost_rt_usd}>${number(m.cost_rt_usd)} RT: {number(m.net_points)} netto punten, PF {number(m.profit_factor,3)}. Fills en signalen ongewijzigd.</li>)}</ul>
          <p>MFE mediaan, onder-/bovengrens: {number(r.excursions.MFE_points_lower.median)} / {number(r.excursions.MFE_points_bar_upper.median)} punten. MAE: {number(r.excursions.MAE_points_lower.median)} / {number(r.excursions.MAE_points_bar_upper.median)} punten. Volledige P05/P25/P50/P75/P95-verdelingen in punten en R staan in het rapport en de downloads.</p>
        </div>; })}
      </details>
    </div>)}
    <p className="nq-note">{verification.fresh_processes} afzonderlijke bronreproducties. Alle {Object.keys(verification.files_sha256).length} private uitvoerbestanden en {Object.keys(verification.publication_files_sha256).length} publicatiebestanden byte-identiek. Dit verifieert dezelfde implementatie, niet een tweede onafhankelijk geschreven engine. De oude 435 trades blijven exact gelijk; alle 73 bevroren bestanden en het voorbereidingspakket zijn intact.</p>
    <p className="nq-warning">Geen live-handelsgoedkeuring. Het jaarvenster is nu verbruikt. Gecombineerde statistiek, referenties of clean-sensitiviteit kunnen een mislukte primaire toets niet redden. MFE/MAE zijn intrabar-grenzen, geen bekende tickvolgorde. Kalender-, leveranciersvintage- en niet-gebruikbeperkingen blijven gelden.</p>
    <p><a href="/data/research-year-holdout.md" download>Volledig jaar- en gecombineerd rapport</a>{' · '}<a href="/data/research-year-holdout.json" download>Alle resultaten (JSON)</a>{' · '}<a href="/data/research-year-holdout-verification.json" download>Reproductie en SHA-256</a>{' · '}<a href="/data/research-year-holdout.metrics.csv" download>Kerncijfers CSV</a>{' · '}<a href="/data/research-year-holdout.monthly.csv" download>Maanden CSV</a>{' · '}<a href="/data/research-year-holdout.direction.csv" download>Long/short CSV</a>{' · '}<a href="/data/research-year-holdout.excursions.csv" download>MFE/MAE CSV</a>{' · '}<a href="/data/research-year-holdout.costs.csv" download>Kosten CSV</a>{' · '}<a href="/data/research-year-holdout.monthly-equity.csv" download>Maandequity CSV</a></p>
  </section>;
}
