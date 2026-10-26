import Link from 'next/link';
import type {ReactNode} from 'react';
export default function Layout({children}:{children:ReactNode}){return <><aside style={{background:'#142638',color:'#d5e8ff',padding:'14px 24px',fontSize:14}}>
 Nieuw vervolg: <Link href="/research/prop-uniform" style={{textDecoration:'underline'}}>uniform dollar-risico en alle payouts binnen 252 sessies →</Link>
 </aside>{children}</>;}
