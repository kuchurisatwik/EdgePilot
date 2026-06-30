"use client";

import { useMarketContext } from "@/hooks/useMarketContext";
import { formatDate } from "@/lib/format";
import type { MarketSession, TradeStatus } from "@/types";

const SESSION_LABEL: Record<MarketSession, string> = {
  asia: "Asia",
  london: "London",
  newyork: "New York",
  unknown: "Unknown",
};

function Cell({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="rounded-md border border-border bg-panel-raised px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-text-muted">{label}</p>
      <p className="numeric mt-0.5 text-sm text-text">
        {value ?? <span className="text-text-muted">unavailable</span>}
      </p>
    </div>
  );
}

function Card({ children }: { children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <h2 className="mb-3 text-sm font-semibold text-text">Market Context</h2>
      {children}
    </section>
  );
}

export function MarketContextPanel({
  tradeId,
  status,
}: {
  tradeId: string;
  status: TradeStatus;
}) {
  const captured = status !== "draft";
  const { data: ctx, isLoading } = useMarketContext(tradeId, captured);

  if (!captured) {
    return (
      <Card>
        <p className="text-sm text-text-muted">
          The market fingerprint is captured automatically when you open the trade.
        </p>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <p className="text-sm text-text-muted">Loading…</p>
      </Card>
    );
  }

  if (!ctx) {
    return (
      <Card>
        <p className="text-sm text-text-muted">Market context unavailable for this trade.</p>
      </Card>
    );
  }

  const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

  return (
    <Card>
      <div className="grid grid-cols-3 gap-2">
        <Cell label="Session" value={SESSION_LABEL[ctx.session]} />
        <Cell label="Trend" value={cap(ctx.trend)} />
        <Cell label="Volatility" value={cap(ctx.volatility_regime)} />
        <Cell label="ATR" value={ctx.atr} />
        <Cell label="RSI" value={ctx.rsi} />
        <Cell label="VWAP" value={ctx.vwap} />
        <Cell label="Volume" value={ctx.volume} />
      </div>
      <p className="mt-3 text-xs text-text-muted">
        Source: {ctx.data_source} · {ctx.timeframe}/{ctx.higher_timeframe} · captured{" "}
        {formatDate(ctx.captured_at)}. Live crypto indicators populate once a market-data feed is
        connected.
      </p>
    </Card>
  );
}
