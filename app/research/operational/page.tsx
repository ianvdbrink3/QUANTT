import type { Metadata } from 'next';
import Link from 'next/link';
import OperationalSizing from '@/components/OperationalSizing';
import data from '@/public/data/operational-consolidation.json';
import './operational.css';

export const metadata:Metadata={title:'QUANTT — S1 / S2: resultaten en operationeel playbook',description:'Volledige ontwikkelingsresultaten, onzekerheid, kwartaalstabiliteit en exacte paperuitvoeringsregels voor S1 en S2.'};
type Period='2019_2021'|'2024_2026'|'COMBINED';
type Sample='OBSERVED_PATH'|'COMPLETE_DAY_SENSITIVITY';
type Model='S1_SELECTIVE'|'S2_BROAD_NO_STOP'|'S2_BROAD_STOP'|'S3_BASE_1X'|'S3_NONHOT_1X';
type Quarter={quarter:string;N:number;net_R:number;net_points:number};
type Row={N:number;net_R:number;net_points:number;trade_PF_R:number|null;sharpe_daily_R:number|null;max_marked_drawdown_R:number;max_marked_drawdown_points:number;positive_quarters_R:number;traded_quarters:number;cash_days:number;quarterly:Quarter[];inference:{mean_net_R_per_cash_day:number;mean_ci95:number[];expected_total_R_ci95:number[];mean_familywise95_bonf15:number[];p_raw_two_sided?:number;p_holm15?:number}};
const samples=data.samples as unknown as Record<Sample,Record<Period,Record<Model,Row>>>;
const periods:Period[]=['2019_2021','2024_2026','COMBINED'];
const models:Model[]=['S1_SELECTIVE','S2_BROAD_NO_STOP','S2_BROAD_STOP','S3_BASE_1X','S3_NONHOT_1X'];
const periodNames:Record<Period,string>={'2019_2021':'2019–2021','2024_2026':'2024–2026',COMBINED:'Gecombineerd'};
const names:Record<Model,string>={S1_SELECTIVE:'S1 · selectief met stop + B',S2_BROAD_NO_STOP:'S2 · breed zonder overnight-stop + B',S2_BROAD_STOP:'S2 · breed met overnight-stop + B',S3_BASE_1X:'S3 · bull-overnight met stop, 1×',S3_NONHOT_1X:'S3 · met stop, range ≤ 0,85 ATR'};
const n=(v:number|null|undefined,digits=3)=>v==null?'n.v.t.':v.toLocaleString('nl-NL',{minimumFractionDigits:digits,maximumFractionDigits:digits});
const band=(v:number[],digits=3)=>`[${n(v[0],digits)}; ${n(v[1],digits)}]`;

function Results({sample}:{sample:Sample}){
  const primary=sample==='OBSERVED_PATH';
  return <>{periods.map(period=><div key={period} className="op-period">
    <h3>{periodNames[period]}</h3>
    <div className="op-table" tabIndex={0} role="region" aria-label={`Prestaties ${periodNames[period]} ${primary?'waargenomen paden':'volledige dagen'}`}><table>
      <caption>{primary?'Waargenomen prijspaden':'Gelijke volledige-dagensteekproef'} · {samples[sample][period].S1_SELECTIVE.cash_days} cashsessies · netto na $24,50 per NQ-roundtrip</caption>
      <thead><tr><th>Variant</th><th>N</th><th>Netto R</th><th>Netto NQ-pt</th><th>PF R</th><th>Sharpe</th><th>Max DD R</th><th>Max DD pt</th><th>Pos. kwartalen</th></tr></thead>
      <tbody>{models.map(model=>{const x=samples[sample][period][model];return <tr key={model}><th scope="row">{names[model]}</th><td>{x.N}</td><td>{n(x.net_R)}</td><td>{n(x.net_points)}</td><td>{n(x.trade_PF_R)}</td><td>{n(x.sharpe_daily_R)}</td><td>{n(x.max_marked_drawdown_R)}</td><td>{n(x.max_marked_drawdown_points)}</td><td>{x.positive_quarters_R}/{x.traded_quarters}</td></tr>;})}</tbody>
    </table></div>
    <div className="op-table" tabIndex={0} role="region" aria-label={`Onzekerheid ${periodNames[period]}`}><table>
      <caption>Gemiddelde netto R per cashsessie, inclusief vlakke dagen · 20.000 bloktrekkingen</caption>
      <thead><tr><th>Variant</th><th>R / cashdag</th><th>Nominaal 95%-BI R/dag</th><th>95%-BI verwacht totaal R</th><th>Ruwe p</th><th>Holm15 p</th><th>Simultane 95%-band R/dag</th></tr></thead>
      <tbody>{models.map(model=>{const x=samples[sample][period][model].inference;return <tr key={model}><th scope="row">{names[model]}</th><td>{n(x.mean_net_R_per_cash_day,6)}</td><td>{band(x.mean_ci95,6)}</td><td>{band(x.expected_total_R_ci95)}</td><td>{primary?n(x.p_raw_two_sided,4):'diagnostisch BI'}</td><td>{primary?n(x.p_holm15,4):'n.v.t.'}</td><td>{band(x.mean_familywise95_bonf15,6)}</td></tr>;})}</tbody>
    </table></div>
  </div>)}</>;
}

export default function OperationalPage(){
  const combined=samples.OBSERVED_PATH.COMBINED;
  const focus:Model[]=['S1_SELECTIVE','S2_BROAD_NO_STOP'];
  const coverage=Object.values(data.coverage);
  const incomplete=coverage.reduce((sum,x)=>sum+x.BULL_STOP.incomplete_full_paths,0);
  const unidentified=coverage.reduce((sum,x)=>sum+x.BULL_STOP.unidentified_stop_paths,0);
  const excluded=coverage.reduce((sum,x)=>sum+x.strict_excluded_cash_days,0);
  const a=new Map(combined.S1_SELECTIVE.quarterly.map(q=>[q.quarter,q]));
  const b=new Map(combined.S2_BROAD_NO_STOP.quarterly.map(q=>[q.quarter,q]));
  const quarters=[...new Set([...a.keys(),...b.keys()])].sort();
  return <main lang="nl" className="operational-page">
    <nav aria-label="Onderzoek en downloads"><Link href="/research/nq">Eerder NQ-onderzoek</Link><Link href="/research/historical-validation">Historische falsificatie</Link><a href={data.reports.full}>Volledig consolidatierapport</a><a href={data.playbook.report}>Operationeel playbook</a><a href={data.reports.performance}>Alle cijfers als CSV</a></nav>
    <header><p className="op-eyebrow">QUANT · ONDERZOEKSCONSOLIDATIE · 25 OKTOBER 2026</p><h1>S1 en S2: regels, resultaten en risico.</h1>
      <p className="op-lead">Twee vastgelegde uitvoeringsspecificaties op {n(data.entry_sessions,0)} geschikte instapsessies, {n(data.cash_sessions,0)} cashsessies en {data.quarters} kwartalen. De afzonderlijke blokken 2019–2021 en 2024–2026 zijn al gebruikt bij selectie. Geen aaneengesloten vijfjarige trackrecord.</p>
      <p className="op-status">Niet onafhankelijk gevalideerd · operationele specificatie voor onderzoek en paperuitvoering</p>
      <p>{Object.values(data.criteria.OBSERVED_PATH).filter(x=>x.nominal95_above_zero_all_periods).length} van de vijf varianten hebben een nominaal 95%-interval boven nul in beide deelperioden én gecombineerd. S2 zonder overnight-stop: gecombineerd Holm15 p={n(combined.S2_BROAD_NO_STOP.inference.p_holm15,4)}. De contractcorrectie is een herberekening op bekeken ontwikkelingsdata.</p>
      <div className="op-actions"><a href="#playbook">Dagelijkse regels lezen</a><a href="#quarters">Alle 19 kwartalen bekijken</a><a href="#sizing-title">MNQ-budget berekenen</a></div>
    </header>
    <div className="op-cards">{focus.map(model=>{const x=combined[model];return <article key={model}>
      <p className="op-eyebrow">{model==='S1_SELECTIVE'?'SELECTIEF MET OVERNIGHT-STOP':'BREED ZONDER OVERNIGHT-STOP'}</p><h2>{model==='S1_SELECTIVE'?'S1 · historisch lagere gemeten drawdown':'S2 · hoogste totale R in deze scan'}</h2>
      <div className="op-big">{n(x.net_R)}R</div><p>{n(x.net_points)} netto NQ-punten · {x.N} uitvoeringen</p>
      <dl><div><dt>PF in R</dt><dd>{n(x.trade_PF_R)}</dd></div><div><dt>Sharpe</dt><dd>{n(x.sharpe_daily_R)}</dd></div><div><dt>Gemeten max. DD</dt><dd>{n(x.max_marked_drawdown_R)}R</dd></div><div><dt>Positieve kwartalen</dt><dd>{x.positive_quarters_R}/{x.traded_quarters}</dd></div></dl>
      <p className="op-note">{model==='S1_SELECTIVE'?'Een stop en gemeten drawdown vormen geen gegarandeerde verlieslimiet; historische onzekerheid blijft breed.':'S2 heeft geen overnight-stop. Een ATR-budget is daar geen vast maximaal kapitaalrisico per positie.'}</p>
    </article>;})}</div>
    <section id="daily"><h2>De dagelijkse volgorde, New York-tijd</h2><ol className="op-timeline">
      <li><strong>Vóór 09:30</strong><span>Leg ATR14, SMA20 en het al geactiveerde RTH-contract vast. Controleer vóór de sessie de derde-vrijdag-expiratie ten opzichte van de volgende cash-09:30.</span></li>
      <li><strong>09:45–14:30</strong><span>B: eerste voltooide 5m-omkeerbar na ≥0,50 ATR pullback, preopen bullfilter en volume &gt;1,5× de vorige 20 voltooide RTH-5m-bars. Entry op de volgende minuutopen.</span></li>
      <li><strong>Uiterlijk 15:55</strong><span>B is flat. Bevestig voor de overnight-order dezelfde vaste NQ/MNQ-contractmaand en hetzelfde jaar; de latere 18:00-volume-switch verandert een open positie niet.</span></li>
      <li><strong>Na bevestiging van 15:59</strong><span>Bereken de terminale SMA20. S1 vereist een sterke trenddag en een vaste 0,50 ATR-stop. S2 vereist slot &gt; SMA20 en houdt zonder overnight-stop dezelfde ene positie.</span></li>
      <li><strong>Volgende daadwerkelijke cashsessie, 09:30</strong><span>Overnight-exit op de open, tenzij de S1-stop eerder geraakt is. Daarna kan B pas vanaf 09:45 instappen.</span></li>
    </ol><p className="op-limit">Contractkeuze causaal: houd vanaf 16:00 tot de volgende cash-09:30 hetzelfde, vóór de RTH gekozen contract. Rollover-nachten worden niet achteraf uitgesloten. Expiratie wordt vooraf via de kalender afgevangen. Exacte first-print fills blijven onbewezen op minuutdata.</p></section>
    <section id="contract-correction"><h2>Causale contractcorrectie versus bevroren archief</h2><p>Alle eerder opgenomen trades reproduceren dezelfde prijzen en uitkomst. Alleen extra same-contract nachten veranderen de totalen. {data.contract_selection.expiry_guard_sessions} expiratie-overrides waren nodig. Strategieparameters en $24,50 frictie zijn ongewijzigd.</p>
    <div className="op-table" tabIndex={0} role="region" aria-label="Archief en causale uitvoering"><table><caption>Alle vijf modellen en beide perioden, inclusief gecombineerd resultaat</caption><thead><tr><th>Periode</th><th>Model</th><th>Oud N</th><th>Nieuw N</th><th>Oud netto pt</th><th>Nieuw netto pt</th><th>Verschil pt</th><th>Verschil R</th></tr></thead><tbody>{data.comparison.map(x=><tr key={`${x.period}-${x.model}`}><th scope="row">{periodNames[x.period as Period]}</th><td>{names[x.model as Model]}</td><td>{x.old_N}</td><td>{x.new_N}</td><td>{n(x.old_net_points)}</td><td>{n(x.new_net_points)}</td><td>{n(x.delta_points)}</td><td>{n(x.delta_R)}</td></tr>)}</tbody></table></div><p><a href={data.reports.archive}>Ongewijzigd oud rapport</a> · <a href={data.reports.archive_data}>Oude aggregaten</a> · <a href="/reports/OPERATIONAL_TRADING_PLAYBOOK_PRE_CAUSAL_ARCHIVE.md">Oud playbook</a></p></section>
    <section><h2>Volledige prestatietabellen en statistische toetsing</h2><p>Alle vijf varianten blijven zichtbaar. R is resultaat gedeeld door de vóór de instapdag bekende ATR14; de puntenkolom blijft 1 NQ per uitvoering. PF betreft netto R per uitvoering. Sharpe gebruikt dagelijkse netto R inclusief vlakke dagen. DD volgt waargenomen minuutopens/-closes en bekende fills.</p><Results sample="OBSERVED_PATH"/>
      <p className="op-note">De nominale intervallen komen uit een gezamenlijke basic bootstrap met blokken van twee kalendermaanden, apart per tijdperk. Het gecombineerde resultaat behoudt de oorspronkelijke daggewichten. Holm15 corrigeert vijf unieke varianten × drie perioden; de simultane band gebruikt Bonferroni15. Beide zijn beperkt tot deze ronde en herstellen de eerdere selectie op bekeken data niet.</p>
      <details><summary>Volledige-dagencontrole: alle prestatietabellen en intervallen</summary><p>{excluded} cashdagen met onvolledige kwalificerende overnight-paden worden voor alle systemen gelijk uitgesloten, inclusief B op die dag. Dit is een diagnostische dekkingstoets; geen reddingsfilter of tweede onafhankelijke test. De uitkomsten blijven apart weergegeven; geen selectie van de gunstigste steekproef.</p><Results sample="COMPLETE_DAY_SENSITIVITY"/></details>
    </section>
    <section id="quarters"><h2>Alle 19 kwartalen van S1 en S2 zonder overnight-stop</h2><p>Geen negatieve kwartalen weggelaten. Kwartalen volgen de cashsessie waarin de positie vóór de dagelijkse 16:00-grens is afgerekend. Positieve kwartalen hierboven zijn op basis van netto R.</p>
      <div className="op-table" tabIndex={0} role="region" aria-label="Kwartaalvergelijking S1 en S2"><table><caption>Beide pijlers betalen hun eigen volledige frictie; geen kostennetting of extra positie op sterke trenddagen.</caption><thead><tr><th>Kwartaal</th><th>S1 N</th><th>S1 netto R</th><th>S1 netto pt</th><th>S2 N</th><th>S2 netto R</th><th>S2 netto pt</th></tr></thead><tbody>{quarters.map(q=>{const x=a.get(q)!;const y=b.get(q)!;return <tr key={q}><th scope="row">{q}</th><td>{x.N}</td><td>{n(x.net_R)}</td><td>{n(x.net_points)}</td><td>{y.N}</td><td>{n(y.net_R)}</td><td>{n(y.net_points)}</td></tr>;})}</tbody></table></div><p><a href={data.reports.quarters}>Kwartaal-CSV van alle varianten en beide steekproeven</a></p>
    </section>
    <section><h2>Wat de stopcijfers vaststellen</h2><p>Bij de brede bull-pijler zijn {incomplete} holdingpaden onvolledig; bij {unidentified} kan een verborgen eerdere stop niet worden uitgesloten. Intervallen over gesimuleerde P&amp;L modelleren die onbekende fills niet.</p><p>De vaste stop en de variant zonder stop worden op dezelfde causale instapdagen getoond. Het volledige rapport bevat ook de volledige-dagencontrole en alle kwartalen.</p></section>
    <OperationalSizing/>
    <section id="playbook"><h2>Operationeel trading-playbook</h2><p>Exacte regels, formules, tijdstippen, rollovergrenzen en kosten staan hieronder en in het <a href={data.playbook.report}>volledige Markdown-playbook</a>. De MNQ-formules zijn rekenregels; zij zijn geen nieuwe MNQ-sizing-backtest.</p>
      {data.playbook.sections.map(section=><details key={section.title}><summary>{section.title}</summary><div className="op-document">{section.body}</div></details>)}
      <p className="op-note">MNQ-puntwaarde en tick: <a href={data.playbook.mnq_specification_source}>officiële CME-contractspecificaties</a>. Vul eigen actuele brokerkosten en overnight-marge in; de NQ-frictie is geen MNQ-prijsofferte.</p>
    </section>
    <section id="register"><h2>Publiek onderzoeksregister</h2><ul><li><strong>S1 / S2 consolidatie:</strong> ontwikkelingsonderzoek, geen onafhankelijke validatie. <a href={data.reports.full}>Volledig rapport</a> · <a href="/data/operational-consolidation.json">Geaggregeerde JSON</a></li><li><strong>Operationeel playbook:</strong> paperuitvoeringsspecificatie; ATR-schaling en stoprisico apart. <a href={data.playbook.report}>Document</a></li><li><Link href="/research/historical-validation">Eerdere gefalsificeerde modellen</Link> · <a href="/data/operational-research-register.json">Nieuwe registeraanvulling</a> · <a href="/data/research-register.json">Bevroren eerdere registerstand</a></li></ul></section>
    <footer><p>Brondata, minuutarrays en private dag-/tradeledgers worden niet op deze pagina gepubliceerd. De volledige bronreplays en eerdere onderzoeksstanden blijven ongewijzigd.</p></footer>
  </main>;
}
