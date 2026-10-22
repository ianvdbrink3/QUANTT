import data from '../../../public/data/research-afternoon-falsification.json';
import registry from '../../../public/data/research-register.json';

const f = (n: number, digits = 2) => n.toLocaleString('nl-NL', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const cohorts = { fixed: 'Vast om 14:30', dynamic: 'Dynamisch' } as const;

export default function AfternoonFalsification() {
  return <section id="afternoon-falsification" className="nq-section" aria-labelledby="afternoon-title">
    <p className="nq-eyebrow">PUBLIEK ONDERZOEKSREGISTER · FALSIFICATIE OP REEDS GEBRUIKTE DATA</p>
    <h2 id="afternoon-title">15:00-effect: wat overleeft de controles?</h2>
    <p className="nq-warning"><strong>{data.status}</strong><br />De positieve gemiddelde impuls overleeft cohortbevriezing en alle dag-/kwartaalweglatingen. Geen onafhankelijke bevestiging, nieuwe holdout of gevalideerde handelsedge.</p>
    <div className="nq-table"><table><caption>Geregistreerde publicatie · dezelfde 435 volledige RTH-dagen</caption>
      <thead><tr><th scope="col">Onderzoek</th><th scope="col">Status</th><th scope="col">Rapport</th></tr></thead>
      <tbody>{registry.entries.filter(r => r.id === 'NQ-AFTERNOON-FALSIFICATION').map(r => <tr key={r.id}><th scope="row">{r.title}</th><td>{r.status}</td><td><a href={r.report} download>Download rapport</a></td></tr>)}</tbody>
    </table></div>
    <div className="nq-table"><table><caption>Volledige kwartieren · gemiddelde / mediaan punten · positief bij voortzetting van de genoemde richting</caption>
      <thead><tr>{['Cohort', 'Richting', 'Start NY', 'Dagen', 'Gemiddelde pt', 'Mediaan pt'].map(h => <th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{data.tables.filter(r => r.part === 'FULL').map(r => <tr key={`${r.scheme}-${r.group}-${r.clock}`}><th scope="row">{cohorts[r.scheme as keyof typeof cohorts]}</th><td>{r.group}</td><td>{r.clock}</td><td>{r.days}</td><td>{f(r.mean_points)}</td><td>{f(r.median_points)}</td></tr>)}</tbody>
    </table></div>
    <p className="nq-note">Vast: selectie uitsluitend met de voltooide 14:29-bar; richting vanaf 09:30 en opgebouwde range / vooraf bekende ATR14 in [0,5; 1,2). Dynamisch: dezelfde selectie opnieuw op elk meetmoment. 26 dagen veranderen van status tussen 14:30 en 15:00; 30 op minstens één van de drie meetpunten. DOWN is positief bij een daling.</p>
    <h3>Minuut 1 versus resterende 14 minuten</h3>
    <div className="nq-table"><table><caption>UP om 15:00 · nominale 95%-intervallen op punten · p-waarden op log-basispunten</caption>
      <thead><tr>{['Cohort', 'Deel', 'Gem. pt', '95%-interval pt', 'p ruw', 'p Holm24'].map(h => <th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{data.tests.filter(r => r.group === 'UP' && r.comparison === '15:00 mean vs0').map(r => <tr key={`${r.scheme}-${r.part}`}><th scope="row">{cohorts[r.scheme as keyof typeof cohorts]}</th><td>{r.part === 'FIRST' ? 'Minuut 15:00' : '15:01–15:15'}</td><td>{f(r.points.delta)}</td><td>[{r.points.ci95.map(n => f(n)).join('; ')}]</td><td>{f(r.bps.p_raw, 6)}</td><td>{f(r.p_Holm24, 4)}</td></tr>)}</tbody>
    </table></div>
    <p className="nq-note">De eerste minuut bevat circa 44–46% van het volledige gemiddelde. Het restant is positief gemeten, maar geen restant-toets overleeft Holm24. Dat bewijst niet dat het restant nul is. De eerste minuut wijkt wel af van 14:45, niet overtuigend van 14:30. Alle 24 toetsen staan in de downloads; HAC(5) op dag-invloedscores houdt rekening met cohortoverlap.</p>
    <p className="nq-note">Volledig kwartier: vorige minuutclose tot close van start+14 (15:14, bekend om 15:15). Minuut 1: 15:00-open tot close; restant: 15:01-open tot 15:14-close. Close/open-prijsverschillen blijven apart behouden. Geen seconden- of fillbewijs.</p>
    <h3>Alle dag- en kwartaalweglatingen</h3>
    <div className="nq-table"><table><caption>UP · gemiddelde punten overblijvende dagen · geen tekenomslag</caption>
      <thead><tr><th scope="col">Cohort</th><th scope="col">Origineel</th><th scope="col">Dagweglating min–max</th><th scope="col">Kwartaalweglating min–max</th></tr></thead>
      <tbody>{data.concentration.map(r => <tr key={r.scheme}><th scope="row">{cohorts[r.scheme as keyof typeof cohorts]}</th><td>{f(r.original_mean)}</td><td>{f(r.day_out_min_mean)} – {f(r.day_out_max_mean)}</td><td>{f(r.quarter_out_min.remaining_mean)} – {f(r.quarter_out_max.remaining_mean)}</td></tr>)}</tbody>
    </table></div>
    <p className="nq-note">De laagste gemiddelden ontstaan zonder de +148-puntendag 19 maart 2026 en zonder 2026Q2. Richtingrobuustheid is geen bewijs van uniforme kwartaalstabiliteit, significantie na weglating of economische uitvoerbaarheid.</p>
    <details className="nq-details"><summary>Integriteit, technisch erratum en beslisboom</summary>
      <p>{data.integrity.observed_bars}/{data.integrity.expected_bars} bars aanwezig op 14:59, 15:00 en 15:01; {data.integrity.missing} ontbrekend, {data.integrity.duplicates} dubbel en {data.integrity.flagged_days} afgekeurde dagen. Geen resterende grid-, OHLC- of tickrasterfouten in deze controle.</p>
      <p>De eerste audit vergeleek microseconden met een nanosecondentelling en markeerde daardoor onterecht 435 dagen. Een afzonderlijke eenheid-onafhankelijke controle corrigeert alleen die afstandstest; de oorspronkelijke evidence blijft bewaard. Geen rendement of p-waarde is gewijzigd.</p>
      <ol><li>Vast UP-gemiddelde verdwijnt? Nee: +8,00 pt.</li><li>Enige dag-/kwartaalweglating met tekenomslag? Nee.</li><li>Onafhankelijke bronbevestiging? Nee. Daarom: interessante, onafhankelijk onbevestigde observatie.</li></ol>
      <p>Bronreplay byte-identiek; {data.verification.prefix_checks} toekomst-afknipcontroles; {data.verification.protected_archive_files} beschermde archiefbestanden ongewijzigd; geen nieuwe strategie-runs. De Holm-correctie geldt alleen voor deze ronde, niet voor alle eerdere analyses.</p>
      <p>Het rapport is een ongewijzigde historische momentopname. De daarin genoemde lokale publicatiestatus dateert van vóór de latere expliciete vrijgave voor deze publicatie.</p>
    </details>
    <p><a href="/data/AFTERNOON_FALSIFICATION_REPORT.md" download>Volledig falsificatierapport</a>{' · '}<a href="/data/research-afternoon-falsification.json" download>Aggregaten JSON</a>{' · '}<a href="/data/research-afternoon-falsification.rows.csv" download>Alle meettabellen CSV</a>{' · '}<a href="/data/research-afternoon-falsification.tests.csv" download>Alle 24 toetsen CSV</a>{' · '}<a href="/data/research-afternoon-falsification.leave-quarters.csv" download>Kwartaalweglatingen CSV</a>{' · '}<a href="/data/research-afternoon-falsification.transitions.csv" download>Statusovergangen CSV</a>{' · '}<a href="/data/research-register.json" download>Publiek register</a></p>
  </section>;
}
