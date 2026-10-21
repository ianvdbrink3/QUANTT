import research from '../../../public/data/research-volume-path.json';

const labels: Record<string,string> = {A_London_sweep:'London Sweep',B_ORB5:'ORB 5m',B_ORB15:'ORB 15m',C_VWAP_extreme:'VWAP Extreme'};
const exitLabels: Record<string,string> = {target:'Target',stop:'Stop',time_session:'Tijd / sessie'};
const f = (v: number | null | undefined, digits=2): string => v == null ? '—' : (Math.sign(v)*Math.round((Math.abs(v)+1e-9)*10**digits)/10**digits).toLocaleString('nl-NL',{minimumFractionDigits:digits,maximumFractionDigits:digits});
const pct = (v: number | null | undefined): string => v == null ? '—' : `${f(100*v,1)}%`;
const interval = (lo: number | null, hi: number | null): string => lo===hi ? pct(lo) : `${pct(lo)}–${pct(hi)}`;
const q = (v: {median: number | null; p25: number | null; p75: number | null}): string => `${f(v.median)} [${f(v.p25)}–${f(v.p75)}]`;

export default function VolumePathResearch() {
  return <section id="volume-path" className="nq-section" aria-labelledby="volume-path-title">
    <p className="nq-eyebrow">NIEUWSTE ONDERZOEK · 30 DECEMBER 2024–30 SEPTEMBER 2025</p>
    <h2 id="volume-path-title">159 gedeelde dagen · volumecontinuïteit &amp; post-entry paden</h2>
    <p className="nq-warning">Verkennend op reeds bekeken data, geen nieuwe holdout of gevalideerde edge. Baseline v0.9 en de eerdere ATR-only vNext-export blijven ongewijzigd. Alleen de volumehistorie loopt nu over actieve contractgrenzen door; alle strategieparameters, ATR en uitvoeringsregels blijven gelijk.</p>
    <p className="nq-note">De ORB-signaalfilter blijft de mediaan van maximaal 20 eerdere observaties op dezelfde NY-minuut gebruiken, met minimaal 10 observaties en volume &gt;1,5× referentie. Dit is niet de aparte openings-RVOL14. Alle vier modellen hebben exact dezelfde 159 eligible datums; een eligible dag hoeft geen trade te bevatten. Kosten: $24,50 per roundtrip op één NQ.</p>
    <div className="nq-table"><table>
      <caption>159 dagen · afzonderlijke strategieën, geen opgeteld portfolio</caption>
      <thead><tr>{['Strategie','Dagen','Trades','Netto punten','Netto USD','Profit factor','Winrate'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(research.comparison).map(([key,v])=>{const m=v.active_reference_full159;return <tr key={key}><th scope="row">{labels[key]}</th><td>{m.eligible_days}</td><td>{m.trades}</td><td>{f(m.net_points,3)}</td><td>${f(m.net_usd)}</td><td>{f(m.profit_factor,3)}</td><td>{pct(m.win_rate)}</td></tr>;})}</tbody>
    </table></div>
    <h3>148 versus 159 · wat verandert er?</h3>
    <div className="nq-table"><table>
      <caption>Netto NQ-punten · gemeenschappelijke datums scheiden van 11 extra dagen</caption>
      <thead><tr>{['Strategie','Oude volumehistorie, 148','Doorlopend, dezelfde 148','Extra 11 dagen','Doorlopend, alle 159'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(research.comparison).map(([key,v])=><tr key={key}><th scope="row">{labels[key]}</th><td>{f(v.old_reference_common148.net_points,3)}</td><td>{f(v.active_reference_common148.net_points,3)}</td><td>{f(v.active_reference_added11.net_points,3)}</td><td>{f(v.active_reference_full159.net_points,3)}</td></tr>)}</tbody>
    </table></div>
    <p className="nq-note">De volumereferentie verandert ook ORB-signalen op bestaande dagen. De eerste twee kolommen vergelijken daarom exact dezelfde 148 dagen. London Sweep en VWAP gebruiken deze filter niet en hebben op hun oorspronkelijke 159 datums identieke trades behouden.</p>
    <h3>Bereikte R-niveaus en het uiteindelijke resultaat</h3>
    <p className="nq-note">1R = afstand van ruwe entry tot initiële stop, vóór kosten. Telling tot en met de gesimuleerde exit. Volledig doorlopen minuten en de bekende fill vormen de ondergrens; exitbar-extremen vormen een bovengrens, begrensd door target en stop of bekende slechtere gapfill. Op de drie gevraagde drempels vallen beide grenzen in deze dataset samen. Verlies/winst hieronder betreft netto P&amp;L ná kosten.</p>
    <div className="nq-table"><table>
      <caption>Alle trades op de 159 gedeelde dagen · conditionele verlies-/winstverdeling onder bereikte niveaus</caption>
      <thead><tr>{['Strategie','Niveau','Alle trades','Bereikt (aantal / grens)','Bereikt %','Verlies / winst (zeker)','Verlies % onder treffers','Winst % onder treffers'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(research.paths).flatMap(([key,v])=>v.thresholds.map(t=><tr key={`${key}-${t.R}`}><th scope="row">{labels[key]}</th><td>+{f(t.R,1)}R</td><td>{t.all_trades}</td><td>{t.certain_hits===t.possible_hits_including_certain ? t.certain_hits : `${t.certain_hits}–${t.possible_hits_including_certain}`}</td><td>{interval(t.hit_fraction_lower,t.hit_fraction_upper)}</td><td>{t.by_final_net_sign.negative.certain} / {t.by_final_net_sign.positive.certain}</td><td>{interval(t.conditional_sign_fraction_bounds.negative.lower,t.conditional_sign_fraction_bounds.negative.upper)}</td><td>{interval(t.conditional_sign_fraction_bounds.positive.lower,t.conditional_sign_fraction_bounds.positive.upper)}</td></tr>))}</tbody>
    </table></div>
    <h3>Tijd tot MFE en MAE · minuutresolutie</h3>
    <p className="nq-warning">Exacte vóór-exit piektijden zijn niet vast te stellen uit 1-minuut OHLC. Hieronder staat de eerste minuutbar met het waargenomen gunstige/ongunstige uiterste; een extremum in de exitbar kan ná de fill liggen. Minuut k betekent [k,k+1), geen exact transactietijdstip. Nul-excursies tellen als tijd 0 bij entry.</p>
    <div className="nq-table"><table>
      <caption>Mediaan [P25–P75] in minuten vanaf entry · eerste bij gelijke extremen</caption>
      <thead><tr>{['Strategie','Trades','Bar-MFE','Bar-MAE','MFE in exitbar','MAE in exitbar'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(research.paths).map(([key,v])=><tr key={key}><th scope="row">{labels[key]}</th><td>{v.trades}</td><td>{q(v.MFE_first_bar_minutes)}</td><td>{q(v.MAE_first_bar_minutes)}</td><td>{v.MFE_extreme_in_exit_bar}/{v.trades}</td><td>{v.MAE_extreme_in_exit_bar}/{v.trades}</td></tr>)}</tbody>
    </table></div>
    <details className="nq-details"><summary>Alleen volledig doorlopen minuten vóór de exitbar</summary>
      <p className="nq-note">Dit is een prefix, niet de volledige trade. Trades zonder positieve of negatieve excursie in die prefix hebben geen extremumtijd; n staat afzonderlijk vermeld.</p>
      <div className="nq-table"><table><thead><tr><th scope="col">Strategie</th><th scope="col">MFE mediaan [P25–P75]</th><th scope="col">n</th><th scope="col">MAE mediaan [P25–P75]</th><th scope="col">n</th></tr></thead>
        <tbody>{Object.entries(research.paths).map(([key,v])=><tr key={key}><th scope="row">{labels[key]}</th><td>{q(v.MFE_completed_prefix_minutes)}</td><td>{v.MFE_completed_prefix_minutes.n}</td><td>{q(v.MAE_completed_prefix_minutes)}</td><td>{v.MAE_completed_prefix_minutes.n}</td></tr>)}</tbody>
      </table></div>
    </details>
    <h3>Netto resultaat per uitstapreden</h3>
    <div className="nq-table"><table>
      <caption>Stop bevat stop_both · stop vóór target bij beide geraakt in één minuut</caption>
      <thead><tr>{['Strategie','Reden','Trades','Aandeel','Netto punten','Netto USD','Mediaan netto R [P25–P75]'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(research.paths).flatMap(([key,v])=>v.exits.map(e=><tr key={`${key}-${e.reason}`}><th scope="row">{labels[key]}</th><td>{exitLabels[e.reason]}</td><td>{e.trades}</td><td>{pct(e.share)}</td><td>{f(e.net_points,3)}</td><td>${f(e.net_usd)}</td><td>{q(e.net_R)}</td></tr>))}</tbody>
    </table></div>
    <p className="nq-note">Uitsluitend gemeten aantallen, percentages, kwantielen en intrabar-grenzen. Geen inferentiële toetsen uitgevoerd, dus geen p-waarden of multipliciteitscorrectie. Geen parameteroptimalisatie of nieuwe handelsfilters. Dit zijn modeluitvoeringen, geen geregistreerde brokerfills.</p>
    <p><a href="/data/research-volume-path.json" download>Download geaggregeerde 159-dagenanalyse (JSON)</a> · <a href="/data/research-volume-path.md" download>Download volledig rapport (Markdown)</a></p>
  </section>;
}
