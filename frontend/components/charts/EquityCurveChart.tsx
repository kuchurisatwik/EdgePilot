"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { toNumber } from "@/lib/format";
import type { EquityPoint } from "@/types";

const AXIS = { fontSize: 11, fill: "#8A93A2" } as const;
const TOOLTIP_STYLE = {
  backgroundColor: "#13161B",
  border: "1px solid #252A33",
  borderRadius: 8,
  fontSize: 12,
  color: "#E6E8EB",
} as const;

export function EquityCurveChart({ points }: { points: EquityPoint[] }) {
  const data = points.map((p, i) => ({ i: i + 1, equity: toNumber(p.equity) }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#252A33" vertical={false} />
        <XAxis dataKey="i" tick={AXIS} stroke="#252A33" />
        <YAxis tick={AXIS} stroke="#252A33" width={64} domain={["auto", "auto"]} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelFormatter={(l) => `Trade #${l}`} />
        <Area
          type="monotone"
          dataKey="equity"
          stroke="#3B82F6"
          strokeWidth={2}
          fill="url(#equityFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
