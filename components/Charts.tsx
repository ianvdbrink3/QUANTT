"use client";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from "recharts";
const tooltip = {
  backgroundColor: "#151b25",
  border: "1px solid #303949",
  borderRadius: 8,
  color: "#e4e9f0",
  fontSize: 12,
};
const axis = {
  stroke: "#748095",
  fontSize: 10,
  tickLine: false,
  axisLine: false,
};
export type Point = Record<string, string | number | null>;
export default function Chart({
  data,
  x,
  y,
  kind = "area",
  color = "#5b9dff",
  height = 280,
  second,
  format = "number",
  brush = false,
}: {
  data: Point[];
  x: string;
  y: string;
  kind?: "area" | "bar" | "line";
  color?: string;
  height?: number;
  second?: string;
  format?: "number" | "time";
  brush?: boolean;
}) {
  const intraday =
    format === "time" &&
    data.length > 0 &&
    Number(data.at(-1)?.[x]) - Number(data[0][x]) < 172800;
  const tick = (v: number) =>
    format === "time"
      ? intraday
        ? new Date(v * 1000).toLocaleTimeString("en-GB", {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: "UTC",
          })
        : new Date(v * 1000).toLocaleDateString("en-GB", {
            month: "short",
            day: "numeric",
            timeZone: "UTC",
          })
      : Number(v).toLocaleString("en-US", { maximumFractionDigits: 2 });
  const shared = { data, margin: { top: 12, right: 14, bottom: 0, left: 0 } };
  const grid = (
    <CartesianGrid stroke="#202833" strokeDasharray="3 5" vertical={false} />
  );
  const axes = (
    <>
      <XAxis dataKey={x} {...axis} minTickGap={45} tickFormatter={tick} />
      <YAxis
        {...axis}
        width={58}
        domain={kind === "bar" ? undefined : ["auto", "auto"]}
        tickFormatter={(v) =>
          Number(v).toLocaleString("en-US", { maximumFractionDigits: 1 })
        }
      />
      <Tooltip
        contentStyle={tooltip}
        labelFormatter={(v) =>
          format === "time"
            ? new Date(Number(v) * 1000)
                .toISOString()
                .replace("T", " ")
                .slice(0, 16) + " UTC"
            : String(v)
        }
        formatter={(v) =>
          typeof v === "number"
            ? v.toLocaleString("en-US", { maximumFractionDigits: 4 })
            : String(v)
        }
      />
    </>
  );
  if (!data.length || !data.some((p) => typeof p[y] === "number"))
    return (
      <div className="chart-empty" style={{ height }}>
        Insufficient observations for this measure.
      </div>
    );
  return (
    <div style={{ width: "100%", height, minWidth: 0 }}>
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        minHeight={0}
        initialDimension={{ width: 800, height }}
      >
        {kind === "bar" ? (
          <BarChart {...shared}>
            {grid}
            {axes}
            <ReferenceLine y={0} stroke="#3c4658" />
            <Bar
              dataKey={y}
              fill={color}
              radius={[3, 3, 0, 0]}
              isAnimationActive={false}
            />
            {second && (
              <Bar dataKey={second} fill="#a78bfa" isAnimationActive={false} />
            )}
          </BarChart>
        ) : kind === "line" ? (
          <LineChart {...shared}>
            {grid}
            {axes}
            <ReferenceLine y={0} stroke="#3c4658" />
            <Line
              type="linear"
              dataKey={y}
              stroke={color}
              dot={false}
              strokeWidth={1.8}
              isAnimationActive={false}
              connectNulls={false}
            />
            {second && (
              <Line
                dataKey={second}
                stroke="#a78bfa"
                dot={false}
                isAnimationActive={false}
              />
            )}
          </LineChart>
        ) : (
          <AreaChart {...shared}>
            <defs>
              <linearGradient id={`fill-${y}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.22} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            {grid}
            {axes}
            <Area
              type="linear"
              dataKey={y}
              stroke={color}
              strokeWidth={1.8}
              fill={`url(#fill-${y})`}
              isAnimationActive={false}
              connectNulls={false}
            />
            {brush && (
              <Brush
                dataKey={x}
                height={24}
                stroke="#3b5d8c"
                fill="#0d131c"
                tickFormatter={tick}
              />
            )}
          </AreaChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
