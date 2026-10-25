'use client';
import {useState} from 'react';

type Row={fill:string;period:string;model:string;family:string;timeframe:number;bias:string;level:string;mode:string;target:string;N:number;net_ATR_R:number;net_stop_R:number;net_points:number;winrate:number|null;PF_ATR_R:number|null;PF_stop_R:number|null;sharpe_ATR_R:number|null;max_marked_drawdown_ATR_R:number;max_marked_drawdown_stop_R:number;positive_quarters_ATR_R:number;traded_quarters:number;calendar_quarters:number;inference:{ZERO:{total_ci95:number[];p_holm480:number};MINUS_B:{p_holm480:number}}|null};
const n=(x:number|null,d=3)=>x==null?'n.v.t.':x.toLocaleString('nl-NL',{maximumFractionDigits:d,minimumFractionDigits:d});

export default function ICTStudyTable({rows}:{rows:Row[]}){
  const [period,setPeriod]=useState('COMBINED');const [fill,setFill]=useState('TOUCH');const [family,setFamily]=useState('ALL');const [tf,setTf]=useState('ALL');const [bias,setBias]=useState('ALL');
  const shown=rows.filter(r=>r.period===period&&r.fill===fill&&(family==='ALL'||r.family===family)&&(tf==='ALL'||String(r.timeframe)===tf)&&(bias==='ALL'||r.bias===bias));
  return <section aria-labelledby="ict-results"><h2 id="ict-results">Alle vooraf vastgelegde varianten</h2>
    <div style={{display:'flex',gap:16,flexWrap:'wrap',marginBottom:20}}>
      <label>Periode <select value={period} onChange={e=>setPeriod(e.target.value)}><option value="COMBINED">Gecombineerd</option><option value="2019_2021">2019–2021</option><option value="2024_2026">2024–2026</option></select></label>
      <label>Limietfill <select value={fill} onChange={e=>setFill(e.target.value)}><option value="TOUCH">Aanraking — primaire aanname</option><option value="TRADE_THROUGH">Eén tick trade-through</option></select></label>
      <label>Familie <select value={family} onChange={e=>setFamily(e.target.value)}><option value="ALL">Alle</option><option>ICT1</option><option>ICT2</option><option>ICT3</option></select></label>
      <label>Signaalbars <select value={tf} onChange={e=>setTf(e.target.value)}><option value="ALL">1m en 5m</option><option value="1">1 minuut</option><option value="5">5 minuten</option></select></label>
      <label>Richting <select value={bias} onChange={e=>setBias(e.target.value)}><option value="ALL">Beide specificaties</option><option value="BOTH">Tweezijdig</option><option value="BULL_LONG">Bull-bias long-only</option></select></label>
    </div>
    <p aria-live="polite">{shown.length} van de 80 varianten. Geen sortering op winst; de vaste catalogusvolgorde blijft staan.</p>
    <div className="op-table" tabIndex={0} role="region" aria-label="ICT-resultaten"><table>
      <caption>Alle bedragen netto na $24,50 per NQ-roundtrip. ATR-R en stopR hebben verschillende risiconoemers.</caption>
      <thead><tr><th>Variant</th><th>N</th><th>Netto ATR-R</th><th>Netto stopR</th><th>Netto pt</th><th>Win%</th><th>PF ATR</th><th>PF stop</th><th>Sharpe ATR</th><th>DD ATR</th><th>DD stop</th><th>Pos. kalenderkwartalen</th><th>95%-BI totaal ATR-R</th><th>Holm480 nul</th><th>Holm480 vs. B</th></tr></thead>
      <tbody>{shown.map(r=><tr key={r.model}><th scope="row">{r.model}</th><td>{r.N}</td><td>{n(r.net_ATR_R)}</td><td>{n(r.net_stop_R)}</td><td>{n(r.net_points)}</td><td>{n(r.winrate==null?null:r.winrate*100,1)}</td><td>{n(r.PF_ATR_R)}</td><td>{n(r.PF_stop_R)}</td><td>{n(r.sharpe_ATR_R)}</td><td>{n(r.max_marked_drawdown_ATR_R)}</td><td>{n(r.max_marked_drawdown_stop_R)}</td><td>{r.positive_quarters_ATR_R}/{r.calendar_quarters}</td><td>{r.inference?'['+r.inference.ZERO.total_ci95.map(x=>n(x)).join('; ')+']':'diagnostische fillcontrole'}</td><td>{r.inference?n(r.inference.ZERO.p_holm480,4):'n.v.t.'}</td><td>{r.inference?n(r.inference.MINUS_B.p_holm480,4):'n.v.t.'}</td></tr>)}</tbody>
    </table></div>
  </section>;
}
