import Link from "next/link";
import report from "../../../public/data/nq-overnight.json";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "QUANTT — NQ Observed Historical Research",
  description: "Historical NQ contract-native exploratory results, source unverified and no validated edge.",
};

type Stats = {
  trades: number; eligible_days: number; net_points: number; net_usd: number;
  profit_factor: number; win_rate: number; max_drawdown_points: number;
  ci_low: number | null; ci_high: number | null; p_value: number | null;
};
type Trade = {
  id: string; metrics: Stats; candidate: boolean; edge_validated: boolean;
  holm_original: number | null;
  net_points_without_best: Record<string,number>;
  splits: Record<string,Stats>;
  monthly: {month:string;trades:number;net_points:number}[];
  cost_scenarios: Record<string,Stats & {round_trip_points:number}>;
  paired_daily_inference?: {p_value:number|null;ci_low:number|null;ci_high:number|null};
};
type Report = {
  period:string[]; row_count:number; trade_dates:number; clean_days:number; flagged_days:number;
  atr_ready_days:number; eligible_days:number; missing_minutes:number; cost_rt_usd:number;
  status:string; edge_validated:boolean; strategies:Trade[];
  day_quality: {trade_date:string;contract:string;data_quality_flag:string;missing_minutes:number}[];
  baseline: {entry_ny:string;horizon:string;n:number;mean_net_points:number;win_rate_net:number}[];
  overnight_regimes: {regime:string;n:number;mean_net_points:number;positive_net_probability:number}[];
  checks: Record<string,boolean>; limitations:string[];
};
const data=report as Report;
const nf=(v:number|null|undefined, digits=2)=>v==null?"—":v.toLocaleString("en-US",{maximumFractionDigits:digits});
const money=(v:number)=>new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(v);
const pct=(v:number)=>nf(v*100,1)+"%";
const cell:React.CSSProperties={padding:"10px 12px",borderBottom:"1px solid #27384d",textAlign:"left"};
const h:React.CSSProperties={fontSize:18,fontWeight:650,color:"#ebf3ff",marginBottom:12};
const panel:React.CSSProperties={background:"#131e2c",border:"1px solid #304057",borderRadius:12,padding:20,marginBottom:20};
const muted="#a8b7ca";
function Table({heads,rows}:{heads:string[];rows:(string|number)[][]}) {
  return <div style={{overflowX:"auto"}}><table style={{width:"100%",borderCollapse:"collapse",color:"#dbe7f5",fontSize:13}}>
    <thead><tr>{heads.map(x=><th key={x} style={{...cell,color:"#9fb4cb",fontWeight:600,whiteSpace:"nowrap"}}>{x}</th>)}</tr></thead>
    <tbody>{rows.map((r,i)=><tr key={i}>{r.map((x,j)=><td key={j} style={{...cell,whiteSpace:"nowrap"}}>{x}</td>)}</tr>)}</tbody>
  </table></div>;
}
export default function NQResearchPage(){
  const flags=Object.entries(data.day_quality.reduce((acc:Record<string,number>,d)=>{
    acc[d.data_quality_flag]=(acc[d.data_quality_flag]||0)+1;return acc;
  },{}));
  return <main style={{background:"#0a111d",color:"#e4edfa",minHeight:"100vh",padding:"30px clamp(16px,4vw,64px)",fontFamily:"Arial,sans-serif"}}>
    <nav style={{display:"flex",gap:18,flexWrap:"wrap",fontSize:13,marginBottom:20}}>
      <Link style={{color:"#96c5ff"}} href="/research">← Research Command Center</Link>
      <Link style={{color:"#96c5ff"}} href="/research/observed">Observed 0.9 audit</Link>
      <Link style={{color:"#96c5ff"}} href="/explorer">Market explorer</Link>
    </nav>
    <p style={{color:"#78b2ff",fontSize:11,letterSpacing:2,fontWeight:700}}>QUANTT · 2024–2025 HISTORICAL NQ RESEARCH</p>
    <h1 style={{fontSize:"clamp(27px,4vw,39px)",margin:"12px 0"}}>NQ Intraday & Overnight Lab</h1>
    <p style={{color:muted,marginBottom:24,maxWidth:860}}>
      Contract-native observed NQ exports, Barchart as supplied source. Publication is a reproducible
      research snapshot, <strong>not independent source authentication, live signals or trading advice</strong>.
      Strategy outputs are separate hypothetical backtests, not an additive portfolio.
    </p>
    <div style={{...panel,borderColor:"#836d45",background:"#211f1a"}}>
      <strong>NO VALIDATED TRADING EDGE — {data.status}</strong>
      <p style={{color:"#e2ceb5",margin:"8px 0 0"}}>
        There is no independently sealed holdout, certified vendor origin, authoritative exchange calendar
        or broker-verified execution. All candidate flags indicate further research only.
      </p>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(160px,1fr))",gap:12,marginBottom:24}}>
      {[
        ["Minute bars",nf(data.row_count,0)],
        ["Trade dates",nf(data.trade_dates,0)],
        ["Eligible days",nf(data.eligible_days,0)],
        ["Clean days",nf(data.clean_days,0)],
        ["Flagged days",nf(data.flagged_days,0)],
        ["Validated edges","0"]
      ].map(([label,value])=><div key={label} style={{...panel,marginBottom:0,padding:16}}>
        <span style={{fontSize:11,color:muted}}>{label}</span>
        <div style={{fontSize:25,fontWeight:750,marginTop:6}}>{value}</div>
      </div>)}
    </div>
    <section style={panel}><h2 style={h}>Four pre-data research screens (hypothetical, after modeled costs)</h2>
      <Table heads={["Strategy","Trades","Net P&L","Profit factor","Win rate","Bootstrap p","Holm-adjusted p","Status"]}
        rows={data.strategies.map(s=>[
          s.id,s.metrics.trades,money(s.metrics.net_usd),nf(s.metrics.profit_factor),
          pct(s.metrics.win_rate),nf(s.metrics.p_value,3),nf(s.holm_original,3),
          s.candidate?"CANDIDATE · NOT VALIDATED":"INCONCLUSIVE"
        ])}/>
      <p style={{color:muted,fontSize:12,marginTop:12}}>Round-trip assumed cost: {money(data.cost_rt_usd)} per NQ contract. Profitability and significance are not established; the 95% intervals include zero.</p>
    </section>
    <section style={panel}><h2 style={h}>Chronological half-splits and tail dependence</h2>
      <Table heads={["Strategy","First half points","Second half points","Without largest trade","Without 3 best trades","Double-slippage net points"]}
        rows={data.strategies.map(s=>[s.id,nf(s.splits.first.net_points),nf(s.splits.second.net_points),
          nf(s.net_points_without_best["1"]),nf(s.net_points_without_best["3"]),
          nf(s.cost_scenarios.double_slippage.net_points)])}/>
      <p style={{fontSize:12,color:muted,marginTop:12}}>
        Positive aggregate performance is not sufficient. In particular, removing the three best ORB15 trades
        leaves only 49.1 points, and the strategy lacks an independent post-selection holdout.
      </p>
    </section>
    <section style={panel}><h2 style={h}>Overnight range / prior ATR conditioning</h2>
      <Table heads={["Regime","Days","Positive net fraction","Mean 60-minute net points"]}
        rows={data.overnight_regimes.map(x=>[x.regime,x.n,pct(x.positive_net_probability),nf(x.mean_net_points)])}/>
      <p style={{fontSize:12,color:muted,marginTop:12}}>
        Broad overnight sample n=3: statistical inference withheld. Regime selection is post-hoc exploratory.
      </p>
    </section>
    <section style={panel}><h2 style={h}>Unconditional 09:30 long baseline</h2>
      <Table heads={["Horizon","Observations","Mean net points","Positive fraction"]}
        rows={data.baseline.map(x=>[x.horizon,x.n,nf(x.mean_net_points),pct(x.win_rate_net)])}/>
    </section>
    <section style={panel}><h2 style={h}>Data quality and audit gates</h2>
      <p style={{color:muted}}>Source period: {data.period.join(" — ")}; NQH25 / NQM25. Missing in-session minutes: {nf(data.missing_minutes,0)}. ATR-ready: {data.atr_ready_days} days.</p>
      <Table heads={["Day classification","Count"]} rows={flags.map(([name,n])=>[name,n])}/>
      <p style={{color:muted,marginTop:14,fontSize:12}}>
        Automated checks passed: {Object.values(data.checks).filter(Boolean).length} of {Object.keys(data.checks).length}.
        Automated assertions are not independent audit of original licensed CSVs.
      </p>
    </section>
    <section style={panel}><h2 style={h}>Limitations and release provenance</h2>
      <ul style={{paddingLeft:19,color:muted}}>{data.limitations.map((x,i)=><li key={i} style={{marginBottom:7}}>{x}</li>)}</ul>
      <div style={{display:"flex",gap:18,flexWrap:"wrap",fontSize:13,marginTop:18}}>
        <a style={{color:"#9bc8ff"}} href="/data/nq-overnight.json">Published NQ aggregate JSON</a>
        <a style={{color:"#9bc8ff"}} href="/data/research09.json">Observed 0.9 source audit</a>
      </div>
    </section>
  </main>;
}
