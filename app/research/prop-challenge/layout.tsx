import Link from 'next/link';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return <>
    <aside style={{background: '#142638', color: '#d5e8ff', padding: '14px 24px', fontSize: 14}}>
      Nieuw vervolgonderzoek: <Link href="/research/prop-lifecycle" style={{textDecoration: 'underline'}}>
        van evaluatie tot eerste en tweede payout →
      </Link>
    </aside>
    {children}
  </>;
}
