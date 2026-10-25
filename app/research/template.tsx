import Link from 'next/link';

export default function ResearchTemplate({children}:{children:React.ReactNode}){
  return <>
    <style>{'aside[aria-label="Actuele onderzoeksstand"]{display:none}'}</style>
    <nav lang="nl" aria-label="Laatste onderzoeksconsolidatie" style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:16,flexWrap:'wrap',padding:'15px 24px',background:'#102a31',borderBottom:'1px solid #306170',color:'#ddf5f3',fontSize:14}}>
      <Link href="/research/operational" style={{color:'#c7ffec',fontWeight:700,textDecoration:'underline',textUnderlineOffset:4}}>Actueel: S1 / S2 · resultaten, kwartalen en operationeel playbook →</Link>
      <span style={{fontSize:12}}>Ontwikkelingsonderzoek · niet onafhankelijk gevalideerd</span>
    </nav>
    {children}
  </>;
}
