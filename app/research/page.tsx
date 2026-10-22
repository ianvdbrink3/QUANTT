import "./research.css";
import Link from "next/link";
import ResearchCommandCenter from "@/components/ResearchCommandCenter";
import type { Metadata } from "next";
export const metadata:Metadata={title:"QUANTT — Research Command Center",description:"Isolated synthetic 0.8 and observed futures 0.9 research."};
export default function ResearchPage(){return <>
  <nav style={{background:"#0b1220",padding:"12px 32px",color:"#9fc9ff",display:"flex",gap:20,flexWrap:"wrap"}}>
    <Link href="/research/nq#afternoon-falsification" style={{textDecoration:"underline"}}>15:00 falsificatie · onderzoeksregister →</Link>
    <Link href="/research/nq" style={{textDecoration:"underline"}}>NQ historical research →</Link>
    <Link href="/research/observed" style={{textDecoration:"underline"}}>Observed 0.9 audit →</Link>
    <Link href="/explorer" style={{textDecoration:"underline"}}>Original explorer →</Link>
  </nav><ResearchCommandCenter /></>}
