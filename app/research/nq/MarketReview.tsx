import archive from '../../../public/data/research-experiment-archive.json';
import audit from '../../../public/data/research-execution-audit.json';
import raw from '../../../public/data/research-raw-market.json';

const names: Record<string, string> = { B_ORB5: 'ORB 5m', B_ORB15: 'ORB 15m', A_London_sweep: 'London Sweep', C_VWAP_extreme: 'VWAP Extreme' };
const n = (v: number | null | undefined, digits = 3) => v == null ? 'n.v.t.' : v.toLocaleString('nl-NL', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const ci = (lo: number | null, hi: number | null) => `[${n(lo)}; ${n(hi)}]`;
const events: Record<string, string> = { RECORD_HIGH: 'Nieuw RTH-high', RECORD_LOW: 'Nieuw RTH-low', PDH_TOUCH: 'Eerste PDH-touch', PDL_TOUCH: 'Eerste PDL-touch' };

export default function MarketReview() {
  return <section id="market-review" className="nq-section" aria-labelledby="market-review-title">
    <p className="nq-eyebrow">AFGESLOTEN EXPERIMENTEN · UITVOERINGSAUDIT · BESCHRIJVENDE MARKTMETINGEN</p>
    <h2 id="market-review-title">ARCHIVED_NOT_VALIDATED</h2>
    <p className="nq-lead">Alle vier basisschermen zijn definitief afgesloten. Geen parameter-tuning, reddingsfilters of hergebruik als kandidaat. Baseline v0.9, vNext159 en de jaar-holdout blijven ongewijzigde historische resultaten; eerdere HOLDOUT_FAILED-oordelen blijven staan.</p>
    <ul>{Object.entries(archive.models).map(([key, value]) => <li key={key}>{names[key]}: {value.status}</li>)}</ul>
    <p className="nq-note">{Object.keys(archive.files_sha256).length} archiefbestanden beschermd op SHA-256. Niet-gevalideerd is geen bewijs dat iedere denkbare variant universeel weerlegd is. Hieronder staan geen nieuwe handelsregels of handelssignalen.</p>

    <h3 id="execution-audit">Meetlat: wat simuleert de code werkelijk?</h3>
    <div className="nq-grid">
      <article className="nq-card"><h4>Geen stop- of limit-entries</h4><p>Alle modellen beslissen op een complete minuutbar en vullen op de open van de volgende exacte minuut. Een close-signaal is geen fill op die close. Werkelijke latency, bied/laat en wachtrij ontbreken.</p></article>
      <article className="nq-card"><h4>Conservatief én onvolledig</h4><p>Stop wint bij SL+TP in één bar; ongunstige stopgaps vullen op de slechtere open. Een target-touch telt echter als fill, zonder bewijs van uitvoerbaar volume of queuepositie. De bracket is direct op de entrybar actief.</p></article>
      <article className="nq-card"><h4>VWAP is een minuutproxy</h4><p>Vanaf 18:00 NY per contract/handelsdag: cumulatieve Volume × HLC3 gedeeld door volume. Inclusief de laatst afgeronde minuut; geen exacte transactie-VWAP. Basisfrictie $24,50RT.</p></article>
    </div>
    <details className="nq-details"><summary>Exacte extra stopfrictie op bestaande trades</summary>
      <p>1 extra tick per stop-fill kost $5 (0,25 punt), 2 ticks $10 (0,50 punt). Daardoor wordt een stoptrade $29,50 of $34,50RT; andere exits blijven $24,50RT. Er zijn geen stop-entry-orders om extra te belasten. Geen herberekende signalen of gewijzigde historische rapporten.</p>
      <div className="nq-table"><table><caption>Jaar en gecombineerd · ongewijzigde ledgers</caption><thead><tr><th scope="col">Periode</th><th scope="col">Model</th><th scope="col">Stop-exits</th><th scope="col">Basis netto pt</th><th scope="col">+1 tick/stop</th><th scope="col">+2 ticks/stop</th></tr></thead><tbody>{audit.models.map(r => <tr key={`${r.period}-${r.model}`}><th scope="row">{r.period}</th><td>{names[r.model]}</td><td>{r.stop_fills}</td><td>{n(r.scenarios[0].net_points)}</td><td>{n(r.scenarios[1].net_points)}</td><td>{n(r.scenarios[2].net_points)}</td></tr>)}</tbody></table></div>
      <p>De volledige audit vermeldt timing, afronding, conflicttellingen, conservatieve aannames en blinde vlekken. Nieuwe handmatig afgeleide synthetische controles zijn geen broker- of tickcertificatie.</p>
    </details>

    <h3 id="session-structure">Ruw marktgedrag · 30 december 2024–30 september 2026</h3>
    <p>{raw.complete_RTH_and_boundary_days} complete RTH-dagen uit {raw.scheduled_sessions} geplande sessies; {raw.excluded_days.length} uitgesloten. {raw.source_files} bestaande bronbestanden op hash gecontroleerd. Geen ATR-/strategiefilter. Prijzen en vorige-dagniveaus komen uit hetzelfde contract, ook op rolloverdagen.</p>
    <p className="nq-note">Logrendementen in basispunten (1 bp = 0,01%). Close-to-close vanaf de vorige minuutclose; het eerste halfuur begint bij 09:29-close. Volumeaandeel van RTH, niet van de volledige Globex-dag. High-low range is geen gerealiseerde variantie; de aparte RV-maat staat in het rapport.</p>
    <div className="nq-table"><table><caption>Halfuurstructuur · 435 sessies per venster · nominale 95%-intervallen</caption><thead><tr>{['NY-start','Gem. rendement bp','Mediaan bp','95%CI gemiddelde','Gem. range pt','Mediane range pt','Gem. RTH-volume','p Holm43'].map(h => <th key={h} scope="col">{h}</th>)}</tr></thead><tbody>{raw.half_hours.map(r => <tr key={r.clock}><th scope="row">{r.clock}</th><td>{n(r.return_bps.mean)}</td><td>{n(r.return_bps.median)}</td><td>{ci(r.return_bps.mean_ci_low,r.return_bps.mean_ci_high)}</td><td>{n(r.range_points.mean)}</td><td>{n(r.range_points.median)}</td><td>{n(100*r.volume_share.mean,2)}%</td><td>{n(r.return_bps.p_holm_global43,6)}</td></tr>)}</tbody></table></div>

    <h3 id="raw-correlations">Momentum en mean-reversion: gemeten correlaties</h3>
    <div className="nq-table"><table><caption>Niet-overlappende intraday vensters · dagblokken voor onzekerheid</caption><thead><tr><th scope="col">Meting</th><th scope="col">Paren</th><th scope="col">Dagen</th><th scope="col">Pearson r</th><th scope="col">95%CI</th><th scope="col">p nominaal</th><th scope="col">p Holm43</th></tr></thead><tbody>{raw.correlations.map(r => <tr key={r.name}><th scope="row">{r.name}</th><td>{r.pairs}</td><td>{r.days}</td><td>{n(r.coefficient,6)}</td><td>{ci(r.ci_low,r.ci_high)}</td><td>{n(r.p_value,6)}</td><td>{n(r.p_holm_global43,6)}</td></tr>)}</tbody></table></div>

    <h3 id="raw-extremes">Vervolgbeweging na extremen</h3>
    <p>Records zijn strikte nieuwe highs/lows na de eerste RTH-bar; PDH/PDL is de eerste werkelijk waargenomen touch per dag. Een gap zonder touch telt niet. Het rendement begint pas op de eventbarclose. Vensters van 15m, 60m en tot slot kunnen overlappen en hebben door censoring andere aantallen.</p>
    <details className="nq-details"><summary>Alle event- én daggewogen uitkomsten, geen geselecteerde winnaar</summary>
      <div className="nq-table"><table><caption>Gemiddelde log-bp · eventweging versus gemiddelde per eventdag</caption><thead><tr>{['Event','Horizon','Events','Dagen','Eventgem. bp','95%CI eventgem.','p Holm43 event','Daggem. bp','95%CI daggem.','p Holm43 dag'].map(h => <th key={h} scope="col">{h}</th>)}</tr></thead><tbody>{raw.events.map(r => <tr key={`${r.event}-${r.horizon}`}><th scope="row">{events[r.event]}</th><td>{r.horizon}</td><td>{r.event_weighted_bps.n}</td><td>{r.event_weighted_bps.days}</td><td>{n(r.event_weighted_bps.mean)}</td><td>{ci(r.event_weighted_bps.mean_ci_low,r.event_weighted_bps.mean_ci_high)}</td><td>{n(r.event_weighted_bps.p_holm_global43,6)}</td><td>{n(r.equal_event_day_mean_bps.mean)}</td><td>{ci(r.equal_event_day_mean_bps.mean_ci_low,r.equal_event_day_mean_bps.mean_ci_high)}</td><td>{n(r.equal_event_day_mean_bps.p_holm_global43,6)}</td></tr>)}</tbody></table></div>
      <p className="nq-warning">Dagweging is een ander estimand. Het gemiddelde van alle events van een dag is pas achteraf bekend en hangt af van het uiteindelijke aantal events. De significante daggewogen record-effecten zijn geen bewezen uitvoerbare edge. Eventrijke en eventarme dagen wegen anders; er wordt geen handelsregel uit afgeleid.</p>
    </details>
    <p className="nq-note">4.000 bootstrapreplicaties, vijf geplande sessies per blok. Alle overlappende events blijven per dag geclusterd. Eén vooraf vastgelegde globale Holm-familie van 43 toetsen. Intervallen zijn nominaal, niet simultaan; CI en de benaderende gecentreerde p-waarde zijn niet exact elkaars inversen. Alle data zijn al verbruikt.</p>
    <p><a href="/data/research-market-review.md" download>Volledig archief-, audit- en marktrapport</a>{' · '}<a href="/data/research-experiment-archive.json" download>Archiefregister</a>{' · '}<a href="/data/research-execution-audit.json" download>Uitvoeringsaudit JSON</a>{' · '}<a href="/data/research-execution-audit.csv" download>Extra stopfrictie CSV</a>{' · '}<a href="/data/research-raw-market.json" download>Alle marktverdelingen JSON</a>{' · '}<a href="/data/research-raw-market.half-hours.csv" download>Halfuren CSV</a>{' · '}<a href="/data/research-raw-market.correlations.csv" download>Correlaties CSV</a>{' · '}<a href="/data/research-raw-market.events.csv" download>Extremen CSV</a>{' · '}<a href="/data/research-raw-market.tests.csv" download>Alle 43 toetsen CSV</a></p>
  </section>;
}
