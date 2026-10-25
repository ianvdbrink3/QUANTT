import Link from 'next/link';
import type {ReactNode} from 'react';

export default function PropResearchLayout({children}:{children:ReactNode}){
 return <><aside style={{background:'#15283a',color:'#e2edf8',padding:'14px 5vw',fontSize:14,borderBottom:'1px solid #38506a'}} aria-label="Nieuw onderzoek"><strong>Nieuw: rolling prop-challenge simulator</strong> · <Link href="/research/prop-challenge" style={{color:'#a8d5ff',textDecoration:'underline'}}>Vergelijk historische passfrequenties, sizing en evaluatiekosten →</Link></aside>{children}</>;
}
