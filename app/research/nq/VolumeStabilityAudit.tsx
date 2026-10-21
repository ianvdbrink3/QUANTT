import audit from '../../../public/data/research-volume-stability.json';

const labels: Record<string,string>={A_London_sweep:'London Sweep',B_ORB5:'ORB 5m',B_ORB15:'ORB 15m',C_VWAP_extreme:'VWAP Extreme'};
const periods: Record<string,string>={full:'Dec–sep',discovery:'Dec–17 april',observed_apr_sep:'18 april–sep (reeds bekeken)'};
const f=(v: number|null|undefined,d=3): string=>v==null?'—':(Math.sign(v)*Math.round((Math.abs(v)+1e-9)*10**d)/10**d).toLocaleString('nl-NL',{minimumFractionDigits:d,maximumFractionDigits:d});
const pct=(v:number|null):string=>v==null?'—':`${f(100*v,1)}%`;
const primary=audit.strategies.B_ORB15;

export default function VolumeStabilityAudit(){
  return <section id="volume-stability" className="nq-section" aria-labelledby="stability-title">
    <p className="nq-eyebrow">NIEUWSTE AUDIT · ZONDER NIEUWE PARAMETERS</p>
    <h2 id="stability-title">Stabiliteit · waar komt de volumeverbetering vandaan?</h2>
    <p className="nq-warning">Retrospectief op reeds bekeken data, geen nieuwe holdout. De handelsregels en alle eerdere exports blijven ongewijzigd. ORB 15m is over december–september positief, maar over 18 april–september nog steeds negatief. Geen van de 16 toetsen is significant na globale Holm-correctie.</p>
    <div className="nq-kpis" aria-label="ORB15 stabiliteitsbevindingen">{[
      ['Netto ORB15, april–sep',`${f(primary.periods.observed_apr_sep.metrics.net_points)} pt`],
      ['Beste drie / nettowinst hele periode',`${f(primary.periods.full.sensitivity.best3_share_net_profit_pct,1)}%`],
      ['Veranderde common148-dagen',String(primary.changed_common_days)],
      ['Daarvan buiten rollovervensters',String(primary.changed_common_days_outside_roll_window)]
    ].map(([label,value])=><div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
    <p className="nq-note">Bij ORB15 verklaren twee verwijderde verliestrades +341,450 punten, twee richtingswijzigingen +178,500 en tien gewijzigde instapmomenten −59,250: samen +460,700 op dezelfde 148 dagen. De 11 extra datums leveren daarnaast +87,700 punten. Alle common148-veranderingen zitten in de eerste 20 geobserveerde sessies na een roll. Dat is ook waar de referentie door constructie kan verschillen; dit bewijst geen zelfstandige rollover-edge.</p>
    <h3>De perioden blijven apart</h3>
    <div className="nq-table"><table><caption>Nieuwe 159-dagenvariant · netto na $24,50 roundtripkosten · nominale 95% CI per eligible dag</caption>
      <thead><tr>{['Strategie','Periode','Dagen','Trades','Netto punten','PF','Winrate','95% CI pt/dag','Globale Holm p'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(audit.strategies).flatMap(([key,v])=>Object.entries(v.periods).map(([period,p])=>{const m=p.metrics,t=audit.tests[p.test_index];return <tr key={`${key}-${period}`}><th scope="row">{labels[key]}</th><td>{periods[period]}</td><td>{m.eligible_days}</td><td>{m.trades}</td><td>{f(m.net_points)}</td><td>{f(m.profit_factor)}</td><td>{pct(m.win_rate)}</td><td>[{f(t.ci_low)}; {f(t.ci_high)}]</td><td>{f(t.p_holm_global)}</td></tr>;}))}</tbody>
    </table></div>
    <h3>Gepaard verschil op dezelfde 148 dagen</h3>
    <div className="nq-table"><table><caption>Nieuwe minus oude volumehistorie · nul-tradedagen inbegrepen</caption><thead><tr>{['Strategie','Veranderde dagen','Buiten rollvenster','Gem. verschil pt/dag','95% CI','Ruwe p','Globale Holm p'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(audit.strategies).map(([key,v])=>{const t=audit.tests[v.paired_test_index];return <tr key={key}><th scope="row">{labels[key]}</th><td>{v.changed_common_days}</td><td>{v.changed_common_days_outside_roll_window}</td><td>{f(t.estimate_mean_daily_points)}</td><td>[{f(t.ci_low)}; {f(t.ci_high)}]</td><td>{f(t.p_value)}</td><td>{f(t.p_holm_global)}</td></tr>;})}</tbody>
    </table></div>
    <p className="nq-note">Eén globale familie: 4 strategieën × 3 periode-winsttoetsen + 4 gepaarde verbeteringen = 16. Circular block-bootstrap met 2000 replicaties, blokken van 5 eligible sessies en vaste seed. De intervallen zijn nominaal, niet gelijktijdig. Percentiel-CI en gecentreerde tweezijdige p zijn bij scheve verdelingen niet exacte inversen. Maand-, richting-, roll- en kostentabellen zijn uitsluitend beschrijvend.</p>
    <h3>Uitbijters en hogere kosten</h3>
    <div className="nq-table"><table><caption>Zelfde fills · exact drie beste trades verwijderd, of alleen uitvoeringskosten verhoogd</caption><thead><tr>{['Strategie','Periode','Basis netto pt','Beste 3 / nettowinst','Zonder beste 3 pt','$44,50 RT netto pt','$64,50 RT netto pt','Max. gerealiseerde DD pt'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
      <tbody>{Object.entries(audit.strategies).flatMap(([key,v])=>Object.entries(v.periods).map(([period,p])=>{const s=p.sensitivity;return <tr key={`${key}-${period}`}><th scope="row">{labels[key]}</th><td>{periods[period]}</td><td>{f(p.metrics.net_points)}</td><td>{s.best3_share_net_profit_pct==null?'—':`${f(s.best3_share_net_profit_pct,1)}%`}</td><td>{f(s.without_best3.net_points)}</td><td>{f(s.cost_scenarios[1].net_points)}</td><td>{f(s.cost_scenarios[2].net_points)}</td><td>{f(p.metrics.realized_max_drawdown_points)}</td></tr>;}))}</tbody>
    </table></div>
    <p className="nq-note">Kosten: respectievelijk 2, 4 en 6 ticks slippage per kant plus ongewijzigd $4,50 RT commissie. Geen aangepaste stops/targets of nieuwe signaalsimulatie. Bij netto verlies is beste-drie/nettowinst niet gedefinieerd. Drawdown betreft gesloten trades, niet intratrade mark-to-market.</p>
    <details className="nq-details"><summary>Alle tradeverschillen per strategie</summary><p className="nq-note">De categorie extra_dates betreft de 11 datums buiten common148. London en VWAP waren daar al eligible; hun volledige trades zijn identiek gebleven. Individuele tradegegevens blijven privé.</p><div className="nq-table"><table><thead><tr>{['Strategie','Categorie','Dagen','Oude trades','Nieuwe trades','Oud netto pt','Nieuw netto pt','Verschil pt'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead><tbody>{Object.entries(audit.strategies).flatMap(([key,v])=>v.attribution.map(r=><tr key={`${key}-${r.category}`}><th scope="row">{labels[key]}</th><td>{r.category}</td><td>{r.days}</td><td>{r.old_trades}</td><td>{r.new_trades}</td><td>{f(r.old_net_points)}</td><td>{f(r.new_net_points)}</td><td>{f(r.delta_points)}</td></tr>))}</tbody></table></div></details>
    <details className="nq-details"><summary>Rollovervensters, maanden en long/short</summary>
      <p className="nq-note">Vast venster: eerste 20 geobserveerde actieve sessies vanaf iedere roll, inclusief geobserveerde feestdagen en onvolledige sessies; september is aan het dataset-einde afgekapt.</p>
      <ul>{audit.roll_windows.map(r=><li key={r.start}>{r.start}–{r.end}: {r.observed_sessions} geobserveerde sessies</li>)}</ul>
      <div className="nq-table"><table><thead><tr>{['Strategie','Periode','Venster','Dagen','Trades','Netto pt','Common148 verschil pt','Veranderde common-dagen'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead><tbody>{Object.entries(audit.strategies).flatMap(([key,v])=>v.slices.filter(r=>r.dimension==='roll_window').map(r=><tr key={`${key}-${r.period}-${r.group}`}><th scope="row">{labels[key]}</th><td>{periods[r.period]}</td><td>{r.group}</td><td>{r.eligible_days}</td><td>{r.trades}</td><td>{f(r.net_points)}</td><td>{f('common148_delta_points' in r ? r.common148_delta_points : null)}</td><td>{'changed_common_days' in r ? r.changed_common_days : '—'}</td></tr>))}</tbody></table></div>
      <div className="nq-table"><table><thead><tr>{['Strategie','Periode','Uitsplitsing','Groep','Trades','Netto pt','PF','Winrate'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead><tbody>{Object.entries(audit.strategies).flatMap(([key,v])=>v.slices.filter(r=>r.dimension!=='roll_window').map(r=><tr key={`${key}-${r.period}-${r.dimension}-${r.group}`}><th scope="row">{labels[key]}</th><td>{periods[r.period]}</td><td>{r.dimension}</td><td>{r.group}</td><td>{r.trades}</td><td>{f(r.net_points)}</td><td>{f(r.profit_factor)}</td><td>{pct(r.win_rate)}</td></tr>))}</tbody></table></div>
    </details>
    <p><a href="/data/research-volume-stability.json" download>Download volledige stabiliteitsaudit (JSON)</a> · <a href="/data/research-volume-stability.md" download>Download rapport (Markdown)</a></p>
  </section>;
}
