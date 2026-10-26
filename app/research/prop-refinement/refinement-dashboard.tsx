'use client';
import Link from 'next/link';
import {useEffect,useState} from 'react';

type Row={era:string;firm:string;model:string;overnight_MNQ:number;profile:string;horizon:string;
 starts:number;evaluation_pass_rate:number;payout1_all_starts:number;payout2_all_starts:number;
 median_eval_cash_sessions_if_passed:number|null;mean_net_cash_per_start_USD:number|null;
 unknown_rate:number;censored:number;failures:number;mean_keep_alive_roundtrips:number;
 judas_budget_overruns:number;minimum_one_MNQ_budget_overruns:number;max_initial_judas_risk_USD:number};
type Payload={rows:Row[];sources:Record<string,string>};
const names:Record<string,string>={FROZEN_STRICT:'Bevroren strikt · vast',OBSERVED_BARS:'Geobserveerde bars · vast',
 OBSERVED_KEEPALIVE:'Geobserveerd + keep-alive · vast',OBSERVED_KEEPALIVE_R250:'Hybride $250 + keep-alive',
 OBSERVED_KEEPALIVE_R300:'Hybride $300 + keep-alive',OBSERVED_KEEPALIVE_R250_KA650:'Hybride $250 · keep-alive $6,50',
 OBSERVED_KEEPALIVE_R300_KA650:'Hybride $300 · keep-alive $6,50'};
const num=(x:number|null,d=1)=>x==null?'—':x.toLocaleString('nl-NL',{maximumFractionDigits:d});
const pct=(x:number)=>`${num(100*x)}%`;

export default function RefinementDashboard(){
 const [data,setData]=useState<Payload|null>(null),[error,setError]=useState('');
 const [firm,setFirm]=useState('TOPSTEP_STANDARD'),[era,setEra]=useState('COMBINED');
 const [profile,setProfile]=useState('OBSERVED_KEEPALIVE_R300'),[horizon,setHorizon]=useState('252_SESSIONS');
 useEffect(()=>{const abort=new AbortController();
  fetch('/data/prop-refinement/summary.json',{signal:abort.signal}).then(r=>{if(!r.ok)throw Error('Verfijningsrapport niet beschikbaar.');return r.json();})
   .then(setData).catch(e=>{if(e.name!=='AbortError')setError(e.message);});
  return()=>abort.abort();},[]);
 const rows=data?.rows.filter(r=>r.firm===firm&&r.era===era&&r.horizon===horizon&&(profile==='ALL'||r.profile===profile))??[];
 return <main className="pc-page" lang="nl">
  <nav aria-label="Onderzoeksnavigatie"><Link href="/research/prop-lifecycle">← Bevroren levenscyclus</Link>
   <Link href="/research/prop-challenge">Challenge-onderzoek</Link>
   <a href="/reports/PROP_ACCOUNT_REFINEMENT_REPORT_2026-10-26.md">Volledig verfijningsrapport</a>
   <a href="/data/prop-refinement/summary.csv" download>Alle scenario's · CSV</a></nav>
  <header><div className="pc-eyebrow">QUANT / LEVENSCYCLUS / GERICHTE VERFIJNING</div>
   <h1>Andere aannames.<br/><span>Dezelfde meetlat.</span></h1>
   <p className="pc-intro">Vergelijk de strikte broncontrole met geobserveerde koerspaden, een synthetische onderhoudstrade en vaste stoprisico-sizing op de bestaande Judas-signalen.</p>
   <div className="pc-status">Voorwaardelijke scenario's · geen echte slaagkans of prop-goedkeuring</div></header>
  <section className="pc-controls" aria-label="Verfijningsfilters">
   <label>Programma<select aria-label="Programma" value={firm} onChange={e=>setFirm(e.target.value)}>
    <option value="TOPSTEP_STANDARD">Topstep 50K · Standard</option><option value="TOPSTEP_CONSISTENCY">Topstep 50K · Consistency</option>
    <option value="MFFU_BUILDER">MFFU Builder 50K</option></select></label>
   <label>Periode<select aria-label="Periode" value={era} onChange={e=>setEra(e.target.value)}>
    <option value="COMBINED">Beide perioden</option><option value="2019_2021">2019–2021</option>
    <option value="2024_2026">Recent blok · januari 2025–september 2026</option></select></label>
   <label>Scenario<select aria-label="Scenario" value={profile} onChange={e=>setProfile(e.target.value)}>
    <option value="ALL">Alle scenario's naast elkaar</option>{Object.entries(names).map(([key,name])=><option key={key} value={key}>{name}</option>)}</select></label>
   <label>Follow-up<select aria-label="Follow-up" value={horizon} onChange={e=>setHorizon(e.target.value)}>
    <option value="252_SESSIONS">Gelijke jaarvensters · 252 cashsessies</option><option value="ERA_END">Iedere start tot eigen era-einde</option></select></label>
  </section>
  <section><h2>Van evaluatie tot tweede payout</h2>
   {rows.length>0&&rows.every(r=>r.mean_net_cash_per_start_USD!=null&&r.mean_net_cash_per_start_USD<0)&&<p className="pc-status">Alle hieronder geselecteerde scenario's hebben gemiddeld een negatieve netto cashopbrengst per gestart account binnen deze follow-up.</p>}
   <p>Geobserveerde bars vullen geen ontbrekende marktinformatie aan. De keep-alive rekent met nul bruto koersresultaat en $3,22 kosten; één-seconde fills en acceptatie door de firm zijn onbevestigd. De hybride minimum-size van 1 MNQ kan het opgegeven risicobudget overschrijden.</p>
   {error&&<p role="alert" className="pc-error">{error}</p>}{!data&&!error&&<p role="status">Rapport laden…</p>}
   {data&&rows.length===0&&<p role="status">Dit profiel is niet getest voor deze combinatie. S2 heeft uitsluitend vaste sizing; het $6,50-onderhoudsscenario geldt alleen voor Builder.</p>}
   <div className="pc-table"><table><thead><tr>
    <th scope="col">Bestaand model / scenario</th><th scope="col">Nacht-MNQ</th><th scope="col">Starts</th><th scope="col">Pass</th>
    <th scope="col">Mediane dagen tot pass</th><th scope="col">Payout 1</th><th scope="col">Payout 2</th>
    <th scope="col">Netto $/start</th><th scope="col">Bron onbekend</th><th scope="col">Gem. keep-alives</th>
    <th scope="col">Budgetoverschrijdingen</th><th scope="col">Grootste Judas-stoprisico</th></tr></thead>
    <tbody>{rows.map(r=><tr key={`${r.model}-${r.overnight_MNQ}-${r.profile}`}>
     <th scope="row">{r.model}<small>{names[r.profile]}</small></th><td>{r.overnight_MNQ}</td><td>{r.starts}</td>
     <td>{pct(r.evaluation_pass_rate)}</td><td>{num(r.median_eval_cash_sessions_if_passed)}</td>
     <td>{pct(r.payout1_all_starts)}</td><td>{pct(r.payout2_all_starts)}</td>
     <td>{r.mean_net_cash_per_start_USD==null?'Onbekend':`$${num(r.mean_net_cash_per_start_USD,2)}`}</td>
     <td>{pct(r.unknown_rate)}</td><td>{num(r.mean_keep_alive_roundtrips)}</td>
     <td>{r.profile.includes('_R')?r.judas_budget_overruns:'—'}</td><td>{r.profile.includes('_R')?`$${num(r.max_initial_judas_risk_USD,2)}`:'—'}</td></tr>)}</tbody></table></div>
  </section>
  <section className="pc-notes"><h2>Lees de vergelijking eerlijk</h2>
   <p>Alle percentages gebruiken alle starts als noemer. De gelijke jaarvensters hebben 498 oude en 171 recente starts. Ze overlappen en zijn geen onafhankelijke replicaties. Netto dollars zijn cash na winstdeling, evaluatiebetalingen en activatie, tot tweede payout, falen of horizon; resterende equity is geen inkomen.</p>
   <p>Gewone trades blijven $3,22 per MNQ bij Topstep en voorlopig $6,50 bij Builder. De size-formule gebruikt op verzoek $3,22; ook daardoor kan werkelijk gemodelleerd stoprisico bij Builder boven het budget uitkomen. Budgettellingen zijn account-executies over overlappende starts, geen unieke markttrades.</p>
   <p>De bevroren brononzekerheidsgrenzen en eerdere resultaten zijn ongewijzigd. Er zijn geen nieuwe strategieën, accounts of echte orders toegevoegd.</p>
   <details><summary>Geraadpleegde officiële bronnen</summary><ul>{Object.entries(data?.sources??{}).map(([name,url])=><li key={name}><a href={url}>{name}</a></li>)}</ul></details>
  </section>
 </main>;
}
