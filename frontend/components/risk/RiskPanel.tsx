"use client";

import { MetricTile } from "@/components/data/MetricTile";
import { formatMoney, toNumber } from "@/lib/format";
import type { TradeRiskBreakdown } from "@/types";

type RiskPanelProps = {
  breakdown?: TradeRiskBreakdown;
  currency: string;
  loading?: boolean;
  error?: string | null;
};

function sizeDisplay(value: string): string {
  return toNumber(value).toLocaleString(undefined, { maximumFractionDigits: 8 });
}

/**
 * Always-visible risk analysis (UX: the Trade Planner's right panel).
 * Values are the Risk Engine's output — the source of truth.
 */
export function RiskPanel({ breakdown, currency, loading, error }: RiskPanelProps) {
  const ready = Boolean(breakdown) && !error;
  const b = ready ? breakdown : undefined;

  const rrNum = b?.rr_ratio != null ? toNumber(b.rr_ratio) : null;
  const rrTone = rrNum == null ? "default" : rrNum >= 2 ? "success" : rrNum >= 1 ? "warning" : "danger";

  const exposurePct = b?.exposure_pct != null ? toNumber(b.exposure_pct) : null;
  const exposureTone =
    exposurePct == null ? "default" : exposurePct > 100 ? "danger" : exposurePct > 50 ? "warning" : "default";

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text">Risk Analysis</h2>
        {loading ? <span className="text-xs text-text-muted">updating…</span> : null}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MetricTile
          label="Risk Amount"
          value={b ? formatMoney(b.risk_amount, currency) : "—"}
          tone="warning"
        />
        <MetricTile label="Position Size" value={b ? sizeDisplay(b.position_size) : "—"} />
        <MetricTile
          label="Reward : Risk"
          value={rrNum != null ? `${rrNum.toFixed(2)} : 1` : "—"}
          tone={rrTone}
        />
        <MetricTile
          label="Max Loss"
          value={b ? formatMoney(b.max_loss, currency) : "—"}
          tone="danger"
        />
        <MetricTile
          label="Capital Exposure"
          value={b ? formatMoney(b.capital_exposure, currency) : "—"}
          hint={exposurePct != null ? `${exposurePct.toFixed(2)}% of account` : undefined}
          tone={exposureTone}
          className="col-span-2"
        />
      </div>

      <div className="rounded-lg border border-border bg-panel p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
          Rule Validation
        </p>
        <p className="numeric-lg mt-1 text-neutral">—</p>
        <p className="mt-1 text-xs text-text-muted">PASS / WARNING / BLOCK arrives in M4.</p>
      </div>

      {error ? <p className="text-xs text-danger">{error}</p> : null}
    </div>
  );
}
