import LifecycleDashboard from './lifecycle-dashboard';
import '../prop-challenge/challenge.css';

export const metadata = {
  title: 'QUANT — Van evaluatie naar tweede payout',
  description: 'Accountlevenscyclus van de drie bestaande Judas-portefeuilles op 1 en 2 MNQ.',
};

export default function Page() {
  return <LifecycleDashboard />;
}
