import Dashboard from "@/components/Dashboard";
import { loadData } from "@/lib/data";
import Link from 'next/link';
export default async function Page() {
  return <><nav style={{ background:'#10251f',color:'#97f3d2',padding:'14px 24px' }}><Link href="/research/nq">Echte NQ-data: onderzoek, kosten en onzekerheid →</Link></nav><Dashboard view="explorer" data={await loadData()} /></>;
}
