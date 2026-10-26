import Link from 'next/link';
import type {ReactNode} from 'react';

export default function Layout({children}:{children:ReactNode}){
 return <><aside style={{background:'#142638',color:'#d5e8ff',padding:'14px 24px',fontSize:14}}>
  Naast deze bevroren uitkomsten: <Link href="/research/prop-refinement" style={{textDecoration:'underline'}}>geobserveerde bars, keep-alive en hybride sizing →</Link>
 </aside>{children}</>;
}
