"use client";

import { useState } from "react";
import { EquityCurveChart } from "@/components/charts/EquityCurveChart";
import { NetPnlBarChart } from "@/components/charts/NetPnlBarChart";
import { MetricTile } from "@/components/data/MetricTile";
import { InsufficientData } from "@/components/feedback/InsufficientData";
import { useSettings } from "@/hooks/useSettings";
import {
  useAnalyticsSummary,
  useEquityCurve,
  usePeriodPerformance,
  useSessionPerformance,
  useStrategyPerformance,
} from "@/hooks/useAnalytics";
import { cn } from "@/lib/utils";
import { formatMoney, signedColor, toNumber } from "@/lib/format";
import type { GroupPerformance } from "@/types";

function pct(value: string | null): string {
  return value == null ? "—" : `${(toNumber(value) * 100).toFixed(1)}%`;
}

function GroupTable({ rows, currency }: { rows: GroupPerformance[]; currency: string }) {
  if (rows.length === 0) {
    return <InsufficientData />;
  }
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead className="bg-panel-raised text-left text-xs uppercase tracking-wide text-text-muted">
          <tr>
            <th className="px-4 py-2">Group</th>
            <th className="px-4 py-2 text-right">Trades</th>
            <th className="px-4 py-2 text-right">Win %</th>
            <th className="px-4 py-2 text-right">Profit factor</th>
            <th className="px-4 py-2 text-right">Avg R</th>
            <th className="px-4 py-2 text-right">Net PnL</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {rows.map((g) => (
            <tr key={g.key} className="bg-panel">
              <td className="px-4 py-2">{g.label}</td>
              <td className="numeric px-4 py-2 text-right">{g.trade_count}</td>
              <td className="numeric px-4 py-2 text-right">{pct(g.win_rate)}</td>
              <td className="numeric px-4 py-2 text-right">
                {g.profit_factor == null ? "—" : toNumber(g.profit_factor).toFixed(2)}
              </td>
              <td className="numeric px-4 py-2 text-right">
                {g.average_r == null ? "—" : `${toNumber(g.average_r).toFixed(2)}R`}
              </td>
              <td className={cn("numeric px-4 py-2 text-right", signedColor(g.net_pnl))}>
                {formatMoney(g.net_pnl, currency)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3 rounded-lg border border-border bg-panel p-5">
      <h2 className="text-sm font-semibold text-text">{title}</h2>
      {children}
    </section>
  );
}

export default function AnalyticsPage() {
  const { data: settings } = useSettings();
  const { data: summary } = useAnalyticsSummary();
  const { data: equity } = useEquityCurve();
  const { data: strategies } = useStrategyPerformance();
  const { data: sessions } = useSessionPerformance();
  const [period, setPeriod] = useState<"weekly" | "monthly">("monthly");
  const { data: periods } = usePeriodPerformance(period);

  const currency = settings?.quote_currency ?? "USDT";
  const hasData = (summary?.trade_count ?? 0) > 0;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-text">Analytics</h1>
        <p className="text-sm text-text-muted">Pure performance statistics — no AI involved.</p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <MetricTile label="Win Rate" value={pct(summary?.win_rate ?? null)} />
        <MetricTile
          label="Profit Factor"
          value={
            summary?.profit_factor == null ? "—" : toNumber(summary.profit_factor).toFixed(2)
          }
        />
        <MetricTile
          label="Expectancy"
          value={summary ? formatMoney(summary.expectancy ?? 0, currency) : "—"}
          tone={summary && toNumber(summary.expectancy) >= 0 ? "success" : "danger"}
        />
        <MetricTile
          label="Avg R"
          value={summary?.average_r == null ? "—" : `${toNumber(summary.average_r).toFixed(2)}R`}
        />
        <MetricTile
          label="Net PnL"
          value={summary ? formatMoney(summary.net_pnl, currency) : "—"}
          tone={summary && toNumber(summary.net_pnl) >= 0 ? "success" : "danger"}
        />
        <MetricTile
          label="Max Drawdown"
          value={summary ? formatMoney(summary.max_drawdown, currency) : "—"}
          hint={summary?.max_drawdown_pct ? `${toNumber(summary.max_drawdown_pct).toFixed(2)}%` : undefined}
          tone="danger"
        />
      </div>

      <Card title="Equity Curve">
        {hasData && equity ? (
          <EquityCurveChart points={equity.points} />
        ) : (
          <InsufficientData />
        )}
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Strategy Performance">
          {hasData && strategies && strategies.length > 0 ? (
            <>
              <NetPnlBarChart data={strategies} />
              <GroupTable rows={strategies} currency={currency} />
            </>
          ) : (
            <InsufficientData />
          )}
        </Card>
        <Card title="Session Performance">
          <GroupTable rows={sessions ?? []} currency={currency} />
        </Card>
      </div>

      <Card title="Period Performance">
        <div className="flex gap-2">
          {(["weekly", "monthly"] as const).map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPeriod(p)}
              className={cn(
                "rounded-md border px-3 py-1 text-sm capitalize",
                period === p
                  ? "border-accent text-accent"
                  : "border-border text-text-muted hover:text-text",
              )}
            >
              {p}
            </button>
          ))}
        </div>
        {hasData && periods && periods.length > 0 ? (
          <>
            <NetPnlBarChart data={periods} />
            <GroupTable rows={periods} currency={currency} />
          </>
        ) : (
          <InsufficientData />
        )}
      </Card>
    </div>
  );
}
