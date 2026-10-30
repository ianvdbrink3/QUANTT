export type Profile = "defensive" | "balanced" | "offensive";
export type Asset = {
  close: number;
  high: number;
  low: number;
  sma20: number;
  sma200: number;
  atr14_pre: number;
  ibs: number;
  vol_ratio: number;
  vol_p90_pre: number;
  high_vol: boolean | null;
  distance_sma20_dollars: number;
  distance_sma200_dollars: number;
  distance_sma20_pct: number;
  distance_sma200_pct: number;
  anti_whipsaw: Record<"naked" | "schmitt" | "confirm2", boolean>;
};
export type Day = {
  day: string;
  advisor: { state: string };
  nav_reference: string;
  unit_nav?: string;
  drawdown: string;
  decisions: (string | object)[];
  fills: number;
  has_data_skip: boolean;
  has_cost_block: boolean;
  execution_timing?: string;
};
export type CostGate = {
  minimum_eur: number | null;
  extra_eur: number | null;
  months: number | null;
  progress_pct: number;
  mathematical_pass: boolean;
  execution_approved: boolean;
};
export type Cost = {
  key: string;
  label: string;
  roundtrip_bp: number | null;
  lower_bound_bp: number;
  amount_eur: number;
  spread_bp: number;
  slippage_bp: number;
  note: string;
  gates: Record<string, CostGate>;
};
export type Intent = {
  id: string;
  day: string;
  key: string;
  sleeve: string;
  side: string;
  qty?: string;
  filled_qty?: string;
  status: string;
  reason: string;
  policy_hash: string;
};
export type OSState = {
  public_summary?: boolean;
  sleeve_balances?: Record<string, number>;
  mode: string;
  live_locked: boolean;
  policy_hash: string;
  active_profile: Profile;
  market_asof: string;
  market_status: string;
  generated_at: string;
  clocks: {
    utc: string;
    new_york: string;
    amsterdam: string;
    offset_hours: number;
    ny_dst: boolean;
    nl_dst: boolean;
  };
  telemetry: Record<"QQQ" | "TQQQ", Asset>;
  regime: { state: string; state_code: number };
  s1: {
    signal: boolean;
    execution_allowed: boolean;
    conditions: {
      key: string;
      label: string;
      passed: boolean | null;
      value: number | null;
      unit: string;
    }[];
    blockers: string[];
  };
  profiles: Record<Profile, { weights: number[]; dd_limit_pct: number }>;
  costs: Cost[];
  scenarios: Record<string, string>[];
  replay: {
    first: string;
    last: string;
    days: number;
    execution_timing: string;
    orders: number;
    fills: number;
    missing_minute_quote_days: number;
  };
  dataset: string;
  datasets: {
    key: string;
    first: string;
    last: string;
    days: number;
    anchor_days: number;
    missing_days: number;
    timing: string;
  }[];
  audit: {
    fills?: { intent_id: string; price: string; id: string }[];
    days: Day[];
    intents: Intent[];
    meta: Record<string, string>;
    wallets: { sleeve: string; cash: string }[];
    positions: { sleeve: string; key: string; qty: string }[];
    settlements: { sleeve: string; amount: string }[];
    dividends: { sleeve: string; amount: string }[];
    database: { status: string; modified_at: string };
  };
  briefs: { day: string; markdown: string }[];
  database_checked_at: string;
};
