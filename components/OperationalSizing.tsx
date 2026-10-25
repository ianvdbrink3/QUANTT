'use client';

import { useState } from 'react';
import { calculateForLeg } from '@/lib/operational-sizing.mjs';

const number=(value:string)=>value.trim()===''?null:Number(value);
const fmt=(value:number|null)=>value===null?'onbekend':value.toLocaleString('nl-NL',{maximumFractionDigits:2});

export default function OperationalSizing(){
  const [equity,setEquity]=useState('');
  const [percent,setPercent]=useState('');
  const [atr,setAtr]=useState('');
  const [cost,setCost]=useState('');
  const [stop,setStop]=useState('');
  const [free,setFree]=useState('');
  const [margin,setMargin]=useState('');
  const [leg,setLeg]=useState('S2');
  const result=calculateForLeg({equity:number(equity),percent:number(percent),atr:number(atr),cost:number(cost),stopDistance:number(stop),freeMargin:number(free),marginPerContract:number(margin)},leg);
  return <section className="op-sizing" aria-labelledby="sizing-title">
    <h2 id="sizing-title">MNQ-rekenhulp</h2>
    <p>Vul je eigen budget en bevestigde kosten in. ATR-blootstelling en gepland stoprisico zijn verschillende berekeningen. Dit is een rekenhulp voor het playbook, zonder orderkoppeling of aanbevolen risicopercentage.</p>
    <div className="op-inputs">
      <label>Pijler<select value={leg} onChange={e=>setLeg(e.target.value)}><option value="S2">S2 overnight — zonder stop</option><option value="S1">S1 overnight — vaste 0,50 ATR-stop</option><option value="B">Intraday B — feitelijke structurele stop</option></select></label>
      <label>Accountwaarde in USD<input inputMode="decimal" type="number" min="0" value={equity} onChange={e=>setEquity(e.target.value)}/></label>
      <label>Zelf gekozen budgetpercentage<input inputMode="decimal" type="number" min="0" max="100" step="any" value={percent} onChange={e=>setPercent(e.target.value)}/></label>
      <label>Vooraf bekende ATR14 in punten<input inputMode="decimal" type="number" min="0" step="any" value={atr} onChange={e=>setAtr(e.target.value)}/></label>
      <label>Totale MNQ-frictie per roundtrip in USD<input inputMode="decimal" type="number" min="0" step="any" value={cost} onChange={e=>setCost(e.target.value)}/></label>
      <label>Feitelijke B-stopafstand in punten<input inputMode="decimal" type="number" min="0" step="0.25" disabled={leg!=='B'} value={stop} onChange={e=>setStop(e.target.value)}/></label>
      <label>Vrij margebudget in USD<input inputMode="decimal" type="number" min="0" step="any" value={free} onChange={e=>setFree(e.target.value)}/></label>
      <label>Bevestigde overnight-marge per MNQ in USD<input inputMode="decimal" type="number" min="0" step="any" value={margin} onChange={e=>setMargin(e.target.value)}/></label>
    </div>
    <div aria-live="polite" className="op-sizing-result">{result?<>
      <p>Budget: <strong>${fmt(result.budget)}</strong>. ATR-blootstelling: <strong>{fmt(result.atrQuantity)} MNQ</strong>. Gepland stoprisico: <strong>{fmt(result.stopQuantity)} MNQ</strong>.</p>
      <p>Stopafstand in deze berekening: <strong>{fmt(result.plannedStopDistance)} punten</strong>{leg==='S2'?' — S2 overnight heeft geen stop.':''}</p>
      <p>Margecap: <strong>{fmt(result.marginCap)}</strong>. Na margecap: ATR <strong>{fmt(result.cappedAtr)}</strong>; stopbudget <strong>{fmt(result.cappedStop)}</strong>.</p>
    </>:<p>Vul accountwaarde, budgetpercentage en positieve ATR in om de berekening te zien.</p>}</div>
    <p className="op-note">q_ATR = floor(K / (2 × ATR)). q_stop = floor(K / (2 × stopafstand + werkelijke MNQ-frictie)). q=0 blijft nul. Voor S2 zonder overnight-stop bestaat geen vaste verliesgrens en is een stopbudget voor die pijler niet gedefinieerd. De rekenhulp kan de afstand van 0,50 ATR of de structurele B-stop gebruiken zodra je die feitelijke afstand invoert. Gaps blijven mogelijk. Een MNQ-sizing-backtest is niet uitgevoerd.</p>
  </section>;
}
