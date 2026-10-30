export type BenchmarkRow = {
  currency: "EUR" | "USD";
  RT_bp: number;
  monthly: number;
  model: string;
  period: "FULL" | "2022";
  ending: number;
  contributions: number;
  profit: number;
  CAGR_pct: number;
  total_growth_pct: number;
  max_DD_pct: number;
  Sharpe: number | null;
  max_underwater_sessions: number;
  max_underwater_calendar_days: number;
  last_drawdown_unrecovered: boolean;
  fees: number | null;
};
export type ProfileBenchmark = {
  schema: number;
  status: string;
  first: string;
  last: string;
  days: string[];
  curves: Record<string, number[]>;
  models: Record<string, string>;
  rows: BenchmarkRow[];
  s1: {
    status: string;
    required: number;
    anchors: number;
    complete_stop_paths: number;
    missing_anchors: number;
    incomplete_stop_paths: number;
  };
};
