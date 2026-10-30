export type ChartRow = {
  day: string;
  close: number;
  sma20: number | null;
  sma200: number | null;
  state: number;
  s1_candidate: boolean;
};
export type ChartData = {
  schema: number;
  asof: string;
  basis: string;
  context: string;
  assets: Record<"QQQ" | "TQQQ", ChartRow[]>;
};
export type ChartMarker = {
  day: string;
  price: number;
  side: string;
  label: string;
  id: string;
};
