import Dashboard from "@/components/Dashboard";
import { loadData } from "@/lib/data";
export default async function Page() {
  return <Dashboard view="experiments" data={await loadData()} />;
}
