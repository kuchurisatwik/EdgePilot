"use client";

import Link from "next/link";
import { AIInsightView } from "@/components/ai/AIInsightView";
import { EquityCurveChart } from "@/components/charts/EquityCurveChart";
import { MetricTile } from "@/components/data/MetricTile";
import { InsufficientData } from "@/components/feedback/InsufficientData";
import { useAIPerformance } from "@/hooks/useAI";
import { useDashboard, useEquityCurve } from "@/hooks/useAnalytics";
import { useJournal } from "@/hooks/useTrades";
import { cn } from "@/lib/utils";
import { formatMoney, signedColor, toNumber } from "@/lib/format";

function Panel({
  title,
  locked,
  children,
}: {
  title: string;
  locked?: boolean;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-3 rounded-lg border border-border bg-panel p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text">{title}</h2>
        {locked ? (
          <span className="rounded border border-border px-2 py-0.5 text-[10px] uppercase tracking-wide text-text-muted">
            Locked
          </span>
        ) : null}
      </div>
      {children}
    </section>
  );
}

export default function DashboardPage() {
  const { data: dash } = useDashboard();
  const { data: equity } = useEquityCurve();
  const { data: recent } = useJournal({ page: 1, page_size: 5 });
  const { data: aiPerformance, isLoading: aiLoading } = useAIPerformance();

  const currency = dash?.quote_currency ?? "USDT";
  const hasEquity = (equity?.points.length ?? 0) > 0;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-text">Dashboard</h1>
        <p className="text-sm text-text-muted">Overall account health.</p>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <MetricTile
          label="Account Balance"
          value={dash ? formatMoney(dash.account_balance, currency) : "—"}
        />
        <MetricTile
          label="Today's PnL"
          value={dash ? formatMoney(dash.today_pnl, currency) : "—"}
          tone={dash && toNumber(dash.today_pnl) >= 0 ? "success" : "danger"}
        />
        <MetricTile
          label="Risk Exposure"
          value={dash ? formatMoney(dash.risk_exposure, currency) : "—"}
          hint={dash ? `${dash.open_trades} open` : undefined}
          tone="warning"
        />
        <MetricTile
          label="Trade Score"
          value={dash?.trade_score != null ? `${dash.trade_score}/100` : "—"}
          tone={
            dash?.trade_score == null
              ? "default"
              : dash.trade_score >= 70
                ? "success"
                : dash.trade_score >= 40
                  ? "warning"
                  : "danger"
          }
        />
        <MetricTile
          label="Current Drawdown"
          value={dash ? formatMoney(dash.current_drawdown, currency) : "—"}
          tone={dash && toNumber(dash.current_drawdown) > 0 ? "danger" : "default"}
        />
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-8">
          <Panel title="Equity Curve">
            {hasEquity && equity ? (
              <EquityCurveChart points={equity.points} />
            ) : (
              <InsufficientData />
            )}
          </Panel>
        </div>
        <div className="col-span-12 lg:col-span-4">
          <Panel title="AI Insights">
            <AIInsightView insight={aiPerformance} loading={aiLoading} />
          </Panel>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Panel title="Recent Trades">
          {recent && recent.items.length > 0 ? (
            <ul className="divide-y divide-border">
              {recent.items.map((t) => (
                <li key={t.id}>
                  <Link
                    href={`/journal/${t.id}`}
                    className="flex items-center justify-between py-2 text-sm hover:text-text"
                  >
                    <span className="numeric">{t.symbol}</span>
                    <span className="text-xs capitalize text-text-muted">{t.status}</span>
                    <span className={cn("numeric", signedColor(t.pnl))}>
                      {t.pnl != null ? formatMoney(t.pnl, currency) : "—"}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-text-muted">No trades yet.</p>
          )}
        </Panel>

        <Panel title="Recent Recommendations" locked>
          <p className="text-sm text-text-muted">
            AI trade recommendations unlock in M9, once enough data exists.
          </p>
        </Panel>

        <Panel title="Recent Mistakes" locked>
          <p className="text-sm text-text-muted">
            Behavioral pattern detection unlocks in M10.
          </p>
        </Panel>
      </div>
    </div>
  );
}
