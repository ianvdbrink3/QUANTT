import type { Metadata } from 'next';
import PortfolioOS from './portfolio-os';
import './portfolio-os.css';

export const metadata: Metadata = { title: 'QUANTT — Portfolio OS', description: 'Historische Portfolio OS-onderzoeksresultaten. Geen livefeed of orderverbinding.' };
export default function Page() { return <PortfolioOS />; }
