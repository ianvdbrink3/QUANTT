'use client';
import Link from 'next/link';
import {useEffect,useState} from 'react';

type Row={era:string;firm:string;model:string;profile:string;budget_USD:number|null;starts:number;
 evaluation_pass_rate:number;median_eval_cash_sessions_if_passed:number|null;
 mean_net_first_two_USD:number;mean_net_full_window_USD:number|null;
 mean_additional_cash_after_second_USD:number;mean_payouts:number;max_payouts:number;
 mean_received_first_two_USD:number;mean_received_full_window_observed_USD:number;live_transition_unmodeled:number;
 zero_size_skipped_signals:number;max_initial_overnight_risk_USD:number;
 max_initial_judas_risk_USD:number;payout2_all_starts:number;payout5_all_starts:number};
type Data={rows:Row[];sources:Record<string,string>};
const num=(x:number|null,d=1)=>x==null?'—':x.toLocaleString('nl-NL',{maximumFractionDigits:d});
const pct=(x:number)=>`${num(x*100)}%`;

export default function Dashboard(){
 const [data,setData]=useState<Data|null>(null),[error,setError]=useState('');
 const [firm,setFirm]=useState('TOPSTEP_STANDARD'),[era,setEra]=useState('COMBINED');
 const [budget,setBudget]=useState('ALL'),[counterfactual,setCounterfactual]=useState(false);
 useEffect(()=>{const abort=new AbortController();fetch('/data/prop-uniform/summary.json',{signal:abort.signal})
  .then(r=>{if(!r.ok)throw Error('Het uniforme jaaronderzoek is niet beschikbaar.');return r.json();})
  .then(setData).catch(e=>{if(e.name!=='AbortError')setError(e.message);});return()=>abort.abort();},[]);
 const rows=data?.rows.filter(r=>r.firm===firm&&r.era===era&&
  (counterfactual?r.profile.includes('COUNTERFACTUAL'):!r.profile.includes('COUNTERFACTUAL'))&&
  (budget==='ALL'||r.budget_USD===Number(budget)))??[];
 return <main className="pc-page" lang="nl">
  <nav aria-label="Onderzoeksnavigatie"><Link href="/research/prop-refinement">← Eerdere verfijning</Link>
   <Link href="/research/prop-lifecycle">Bevroren levenscyclus</Link>
   <a href="/reports/PROP_UNIFORM_RISK_FULL_YEAR_2026-10-26.md">Volledig rapport</a>
   <a href="/reports/PROP_UNIFORM_CASH_DETAILS_2026-10-26.md">Payouts en kosten apart</a>
   <a href="/data/prop-uniform/summary.csv" download>Alle tabellen · CSV</a></nav>
  <header><div className="pc-eyebrow">QUANT / UNIFORM DOLLAR-RISICO / 252 CASHSESSIES</div>
   <h1>Beide pijlers geschaald.<br/><span>Het hele jaar geteld.</span></h1>
   <p className="pc-intro">Drie vaste risicobudgets, maximaal 6 MNQ en geen minimumpositie. Vergelijk cash uit de eerste twee payouts met alle ontvangen cash binnen hetzelfde jaarvenster.</p>
   <div className="pc-status">Ontwikkelingsonderzoek · geobserveerde koerspaden en synthetische keep-alive · geen onafhankelijke validatie</div></header>
  <section className="pc-controls" aria-label="Uniforme risicofilters">
   <label>Programma<select aria-label="Programma" value={firm} onChange={e=>{setFirm(e.target.value);setCounterfactual(false);}}>
    <option value="TOPSTEP_STANDARD">Topstep Standard</option><option value="TOPSTEP_CONSISTENCY">Topstep Consistency</option><option value="MFFU_BUILDER">MFFU Builder</option></select></label>
   <label>Periode<select aria-label="Periode" value={era} onChange={e=>setEra(e.target.value)}>
    <option value="COMBINED">Beide perioden</option><option value="2019_2021">2019–2021</option><option value="2024_2026">Recent blok · januari 2025–september 2026</option></select></label>
   <label>Risicobudget<select aria-label="Risicobudget" value={budget} onChange={e=>setBudget(e.target.value)}>
    <option value="ALL">Alle budgets + oude sizingcontrole</option><option value="300">$300</option><option value="350">$350</option><option value="400">$400</option></select></label>
   <label className="pc-checkbox"><input type="checkbox" checked={counterfactual} disabled={firm!=='MFFU_BUILDER'} onChange={e=>setCounterfactual(e.target.checked)}/>Builder: hypothetisch door na 5 Sim-payouts</label>
  </section>
  <section><h2>Eerste twee tegenover het volledige jaar</h2>
   <p>Elke rij gebruikt alle starts: 498 oude en 171 recente. Netto cash is na winstdeling, aankoop, evaluatiebetalingen en activatie. Actieve rekeningequity is geen ontvangen geld. Tijd tot pass is alleen gemeten bij geslaagde evaluaties.</p>
   <p>Builder kent maximaal vijf Sim-payouts. Waar dat wordt bereikt is de verdere livefase onbekend en blijft het volledige jaargetal onbeslist. De aparte voortzettingsoptie houdt hypothetisch dezelfde Sim-regels aan; dit is geen geverifieerd live-account.</p>
   {error&&<p role="alert" className="pc-error">{error}</p>}{!data&&!error&&<p role="status">Jaarresultaten laden…</p>}
   <div className="pc-table"><table><thead><tr><th scope="col">Model / budget</th><th scope="col">Starts</th>
    <th scope="col">Pass</th><th scope="col">Mediane dagen</th><th scope="col">Ontvangen $ eerste 2</th><th scope="col">Netto $ eerste 2</th><th scope="col">Ontvangen $ jaar</th><th scope="col">Netto $ jaar</th>
    <th scope="col">Extra cash na 2</th><th scope="col">Gem. / max. payouts</th><th scope="col">Livefase onbekend</th><th scope="col">0-size skips</th></tr></thead>
    <tbody>{rows.map(r=><tr key={`${r.model}-${r.profile}`}><th scope="row">{r.model}<small>{r.budget_USD==null?'Oude sizing · door na payout 2':`$${r.budget_USD} · beide pijlers`}{r.profile.includes('COUNTERFACTUAL')?' · hypothetische voortzetting':''}</small></th>
     <td>{r.starts}</td><td>{pct(r.evaluation_pass_rate)}</td><td>{num(r.median_eval_cash_sessions_if_passed)}</td>
     <td>${num(r.mean_received_first_two_USD,2)}</td><td>${num(r.mean_net_first_two_USD,2)}</td>
     <td>${num(r.mean_received_full_window_observed_USD,2)}{r.live_transition_unmodeled>0?' · onvolledig':''}</td>
     <td>{r.mean_net_full_window_USD==null?'Livefase onbeslist':`$${num(r.mean_net_full_window_USD,2)}`}</td>
     <td>${num(r.mean_additional_cash_after_second_USD,2)}</td><td>{num(r.mean_payouts)} / {r.max_payouts}</td>
     <td>{r.live_transition_unmodeled}</td><td>{r.zero_size_skipped_signals}</td></tr>)}</tbody></table></div>
  </section>
  <section className="pc-notes"><h2>Vaste uitvoering en interpretatie</h2>
   <p>Aantal MNQ = floor(budget / (stopafstand × $2 + $3,22)), minimaal 0 en maximaal 6. De 1,25 × budgetgrens controleert ook de gebruikte kosten. Een nul-size plaatst geen order, betaalt geen fee en reset geen timer. Nominaal stoprisico is geen garantie tegen een slechtere gap-fill.</p>
   <p>De oorspronkelijke signalen en eerder gepubliceerde resultaten blijven intact. Dit onderzoek behoudt de vorige aannames over ontbrekende bronminuten en de kosten-only keep-alive. Voor Topstep wordt verblijf in XFA tot de jaargrens aangenomen; een werkelijke Live-callup is discretionair en niet uit deze historie af te leiden.</p>
   <p>De starts overlappen. Een achteraf gunstig profiel is geen onafhankelijke bevestiging en een veranderde mediane passtijd vergelijkt niet noodzakelijk dezelfde geslaagde accounts. Geen accounts gekocht of echte orders verzonden.</p>
   <details><summary>Officiële bronnen en overgangsregels</summary><ul>{Object.entries(data?.sources??{}).map(([k,v])=><li key={k}><a href={v}>{k}</a></li>)}</ul></details>
  </section>
 </main>;
}
