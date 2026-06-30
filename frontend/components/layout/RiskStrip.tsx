"use client";

import { useSettings } from "@/hooks/useSettings";
import { formatMoney, formatPct, toNumber } from "@/lib/format";

/**
 * Always-on risk bar (UX Principle 4: "No screen should hide these metrics").
 * Risk % and the baseline Risk Amount come from settings (M1). Drawdown,
 * Exposure and live Rule Status are wired in M3/M4/M6.
 */
export function RiskStrip() {
  const { data: settings } = useSettings();

  const riskPct = settings ? toNumber(settings.default_risk_pct) : null;
  const accountSize = settings ? toNumber(settings.account_size) : null;
  const currency = settings?.quote_currency ?? "USDT";
  const riskAmount =
    riskPct !== null && accountSize !== null ? (accountSize * riskPct) / 100 : null;

  const items: { label: string; value: string }[] = [
    { label: "Risk %", value: riskPct !== null ? formatPct(riskPct) : "—" },
    {
      label: "Risk Amount",
      value: riskAmount !== null ? formatMoney(riskAmount, currency) : "—",
    },
    { label: "Drawdown", value: "—" },
    { label: "Exposure", value: "—" },
    { label: "Rule Status", value: "—" },
  ];

  return (
    <div className="flex items-center gap-6 border-b border-border bg-panel-raised px-5 py-2">
      <span className="text-xs font-semibold uppercase tracking-wide text-text-muted">Risk</span>
      {items.map((item) => (
        <div key={item.label} className="flex items-baseline gap-2">
          <span className="text-xs text-text-muted">{item.label}</span>
          <span className="numeric text-sm font-medium text-text">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
