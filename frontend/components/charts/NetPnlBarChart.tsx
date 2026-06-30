"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toNumber } from "@/lib/format";
import type { GroupPerformance } from "@/types";

const AXIS = { fontSize: 11, fill: "#8A93A2" } as const;
const TOOLTIP_STYLE = {
  backgroundColor: "#13161B",
  border: "1px solid #252A33",
  borderRadius: 8,
  fontSize: 12,
  color: "#E6E8EB",
} as const;

export function NetPnlBarChart({ data }: { data: GroupPerformance[] }) {
  const rows = data.map((g) => ({ label: g.label, net: toNumber(g.net_pnl) }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={rows} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
        <XAxis dataKey="label" tick={AXIS} stroke="#252A33" />
        <YAxis tick={AXIS} stroke="#252A33" width={64} />
        <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "#1B1F26" }} />
        <Bar dataKey="net" radius={[3, 3, 0, 0]}>
          {rows.map((r) => (
            <Cell key={r.label} fill={r.net >= 0 ? "#22C55E" : "#EF4444"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
