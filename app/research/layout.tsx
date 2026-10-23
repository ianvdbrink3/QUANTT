import Link from 'next/link';

export default function ResearchLayout({children}:{children:React.ReactNode}){
  return <>
    <aside lang="nl" aria-label="Actuele onderzoeksstand" style={{background:'#111c2c',borderBottom:'1px solid #314158',padding:'12px 24px',color:'#cbd8e9',fontSize:13,lineHeight:1.6}}>
      <strong>Actuele datastatus: 103/103 downloadblokken ontvangen.</strong>{' '}
      <Link href="/research/historical-preparation" style={{color:'#a9caff',textDecoration:'underline',textUnderlineOffset:3}}>Kwaliteitscontrole 2019–2021 en openstaande vrijgavevoorwaarden</Link>
      {' '}· Geen nieuwe onafhankelijke backtest uitgevoerd. Oudere rapporten hieronder behouden hun oorspronkelijke onderzoeksstand.
    </aside>
    {children}
  </>;
}
