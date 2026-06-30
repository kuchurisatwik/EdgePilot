"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { MetricTile } from "@/components/data/MetricTile";
import { CloseTradeDialog } from "@/components/trades/CloseTradeDialog";
import { useSettings } from "@/hooks/useSettings";
import { useDeleteTrade, useOpenTrade, useTrade } from "@/hooks/useTrades";
import { cn } from "@/lib/utils";
import { formatDate, formatMoney, signedColor, toNumber } from "@/lib/format";
import { ApiError } from "@/services/apiClient";

function LockedCard({ title, note }: { title: string; note: string }) {
  return (
    <div className="rounded-lg border border-border bg-panel p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text">{title}</h2>
        <span className="rounded border border-border px-2 py-0.5 text-[10px] uppercase tracking-wide text-text-muted">
          Locked
        </span>
      </div>
      <p className="mt-2 text-sm text-text-muted">{note}</p>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-text-muted">{label}</p>
      <p className="numeric mt-0.5 text-sm text-text">{value}</p>
    </div>
  );
}

export default function TradeReviewPage() {
  const { tradeId } = useParams<{ tradeId: string }>();
  const router = useRouter();
  const { data: trade, isLoading } = useTrade(tradeId);
  const { data: settings } = useSettings();
  const openTrade = useOpenTrade();
  const deleteTrade = useDeleteTrade();
  const [closing, setClosing] = useState(false);

  const currency = settings?.quote_currency ?? "USDT";

  if (isLoading) return <p className="text-sm text-text-muted">Loading…</p>;
  if (!trade) return <p className="text-sm text-text-muted">Trade not found.</p>;

  async function onOpen() {
    if (!trade) return;
    try {
      await openTrade.mutateAsync({ id: trade.id });
    } catch (err) {
      if (err instanceof ApiError && err.code === "rule_block") {
        if (window.confirm(`${err.message}\n\nOverride and open anyway?`)) {
          await openTrade.mutateAsync({ id: trade.id, acknowledgeOverride: true });
        }
      }
    }
  }

  async function onDelete() {
    if (!trade) return;
    if (!window.confirm("Delete this draft trade?")) return;
    await deleteTrade.mutateAsync(trade.id);
    router.replace("/journal");
  }

  const isClosed = trade.status === "closed";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/journal" className="text-xs text-text-muted hover:text-text">
            ← Back to Journal
          </Link>
          <h1 className="mt-1 flex items-center gap-3 text-xl font-semibold text-text">
            <span className="numeric">{trade.symbol}</span>
            <span className="text-sm capitalize text-text-muted">{trade.direction}</span>
            <span className="rounded border border-border px-2 py-0.5 text-[10px] uppercase tracking-wide text-text-muted">
              {trade.status}
            </span>
            {trade.rule_overridden ? (
              <span className="rounded border border-danger/40 px-2 py-0.5 text-[10px] uppercase tracking-wide text-danger">
                rule overridden
              </span>
            ) : null}
          </h1>
        </div>
        <div className="flex gap-2">
          {trade.status === "draft" ? (
            <>
              <button
                type="button"
                onClick={onOpen}
                className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90"
              >
                Open trade
              </button>
              <button
                type="button"
                onClick={onDelete}
                className="rounded-md border border-border px-3 py-1.5 text-sm text-text-muted hover:text-danger"
              >
                Delete
              </button>
            </>
          ) : null}
          {trade.status === "open" ? (
            <button
              type="button"
              onClick={() => setClosing(true)}
              className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90"
            >
              Close trade
            </button>
          ) : null}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Details */}
        <section className="col-span-12 space-y-4 rounded-lg border border-border bg-panel p-5 lg:col-span-7">
          <h2 className="text-sm font-semibold text-text">Trade Details</h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Detail label="Strategy" value={trade.strategy_name} />
            <Detail label="Order type" value={trade.order_type} />
            <Detail label="Planned" value={formatDate(trade.created_at)} />
            <Detail label="Entry" value={trade.entry_price} />
            <Detail label="Stop loss" value={trade.stop_loss} />
            <Detail label="Target" value={trade.take_profit ?? "—"} />
            <Detail label="Risk %" value={`${toNumber(trade.risk_pct).toFixed(2)}%`} />
            <Detail label="Opened" value={formatDate(trade.opened_at)} />
            <Detail label="Closed" value={formatDate(trade.closed_at)} />
          </div>
          {trade.notes ? (
            <div>
              <p className="text-xs text-text-muted">Notes</p>
              <p className="mt-0.5 whitespace-pre-wrap text-sm text-text">{trade.notes}</p>
            </div>
          ) : null}
        </section>

        {/* Risk + outcome */}
        <section className="col-span-12 space-y-3 rounded-lg border border-border bg-panel-raised p-5 lg:col-span-5">
          <h2 className="text-sm font-semibold text-text">Risk Metrics</h2>
          <div className="grid grid-cols-2 gap-3">
            <MetricTile
              label="Risk Amount"
              value={formatMoney(trade.risk.risk_amount, currency)}
              tone="warning"
            />
            <MetricTile
              label="Position Size"
              value={toNumber(trade.risk.position_size).toLocaleString(undefined, {
                maximumFractionDigits: 8,
              })}
            />
            <MetricTile
              label="Reward : Risk"
              value={
                trade.risk.rr_ratio != null
                  ? `${toNumber(trade.risk.rr_ratio).toFixed(2)} : 1`
                  : "—"
              }
            />
            <MetricTile
              label="Max Loss"
              value={formatMoney(trade.risk.max_loss, currency)}
              tone="danger"
            />
          </div>

          {isClosed ? (
            <>
              <h2 className="pt-2 text-sm font-semibold text-text">Outcome</h2>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-border bg-panel p-4">
                  <p className="text-xs uppercase tracking-wide text-text-muted">PnL</p>
                  <p className={cn("numeric-lg mt-1", signedColor(trade.pnl))}>
                    {trade.pnl != null ? formatMoney(trade.pnl, currency) : "—"}
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-panel p-4">
                  <p className="text-xs uppercase tracking-wide text-text-muted">R Multiple</p>
                  <p className={cn("numeric-lg mt-1", signedColor(trade.r_multiple))}>
                    {trade.r_multiple != null ? `${toNumber(trade.r_multiple).toFixed(2)}R` : "—"}
                  </p>
                </div>
                <Detail label="Result" value={trade.result ?? "—"} />
                <Detail label="Exit price" value={trade.exit_price ?? "—"} />
              </div>
            </>
          ) : null}
        </section>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-4">
          <LockedCard
            title="Market Context"
            note="ATR, RSI, VWAP, volume, trend and session captured per trade — arrives in M7."
          />
        </div>
        <div className="col-span-12 lg:col-span-4">
          <LockedCard
            title="Screenshots"
            note="Entry and exit chart screenshots (trade + higher timeframe) — arrives in M8."
          />
        </div>
        <div className="col-span-12 lg:col-span-4">
          <LockedCard
            title="AI Summary"
            note="A plain-language summary of this trade — arrives in M9, once enough data exists."
          />
        </div>
      </div>

      {closing ? <CloseTradeDialog tradeId={trade.id} onClose={() => setClosing(false)} /> : null}
    </div>
  );
}
