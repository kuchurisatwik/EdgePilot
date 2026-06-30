"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { CloseTradeDialog } from "@/components/trades/CloseTradeDialog";
import { EmptyState } from "@/components/feedback/EmptyState";
import { useSettings } from "@/hooks/useSettings";
import { useStrategies } from "@/hooks/useStrategies";
import { useJournal, useOpenTrade } from "@/hooks/useTrades";
import { cn } from "@/lib/utils";
import { formatDate, formatMoney, signedColor, toNumber } from "@/lib/format";
import { ApiError } from "@/services/apiClient";
import type { JournalFilters, Trade, TradeResult, TradeStatus } from "@/types";

const STATUS_TONE: Record<TradeStatus, string> = {
  draft: "text-neutral border-neutral/40",
  open: "text-accent border-accent/40",
  closed: "text-text-muted border-border",
};

const RESULT_TONE: Record<TradeResult, string> = {
  win: "text-success",
  loss: "text-danger",
  breakeven: "text-neutral",
};

const PAGE_SIZE = 20;

export default function JournalPage() {
  const router = useRouter();
  const { data: settings } = useSettings();
  const { data: strategies } = useStrategies();
  const openTrade = useOpenTrade();

  const [status, setStatus] = useState<TradeStatus | "">("");
  const [result, setResult] = useState<TradeResult | "">("");
  const [strategyId, setStrategyId] = useState("");
  const [symbol, setSymbol] = useState("");
  const [page, setPage] = useState(1);
  const [closingId, setClosingId] = useState<string | null>(null);

  const filters: JournalFilters = {
    page,
    page_size: PAGE_SIZE,
    ...(status ? { status } : {}),
    ...(result ? { result } : {}),
    ...(strategyId ? { strategy_id: strategyId } : {}),
    ...(symbol.trim() ? { symbol: symbol.trim() } : {}),
  };

  const { data, isLoading } = useJournal(filters);
  const currency = settings?.quote_currency ?? "USDT";
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  function resetPageAnd<T>(setter: (v: T) => void) {
    return (v: T) => {
      setter(v);
      setPage(1);
    };
  }

  async function onOpen(trade: Trade) {
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

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-text">Journal</h1>
        <p className="text-sm text-text-muted">Every trade you plan, open and close.</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-end gap-3 rounded-lg border border-border bg-panel p-4">
        <Select
          label="Status"
          value={status}
          onChange={resetPageAnd(setStatus)}
          options={[
            ["", "All"],
            ["draft", "Draft"],
            ["open", "Open"],
            ["closed", "Closed"],
          ]}
        />
        <Select
          label="Result"
          value={result}
          onChange={resetPageAnd(setResult)}
          options={[
            ["", "All"],
            ["win", "Win"],
            ["loss", "Loss"],
            ["breakeven", "Breakeven"],
          ]}
        />
        <Select
          label="Strategy"
          value={strategyId}
          onChange={resetPageAnd(setStrategyId)}
          options={[["", "All"], ...(strategies ?? []).map((s) => [s.id, s.name] as [string, string])]}
        />
        <label className="space-y-1">
          <span className="block text-xs text-text-muted">Symbol</span>
          <input
            value={symbol}
            onChange={(e) => resetPageAnd(setSymbol)(e.target.value.toUpperCase())}
            placeholder="BTC_USDT"
            className="w-36 rounded-md border border-border bg-panel-raised px-2 py-1.5 text-sm text-text outline-none focus:border-accent"
          />
        </label>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="bg-panel-raised text-left text-xs uppercase tracking-wide text-text-muted">
            <tr>
              <th className="px-4 py-2.5">Date</th>
              <th className="px-4 py-2.5">Strategy</th>
              <th className="px-4 py-2.5">Symbol</th>
              <th className="px-4 py-2.5">Dir</th>
              <th className="px-4 py-2.5 text-right">Risk</th>
              <th className="px-4 py-2.5">Result</th>
              <th className="px-4 py-2.5 text-right">PnL</th>
              <th className="px-4 py-2.5 text-right">R</th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data?.items.map((t) => (
              <tr
                key={t.id}
                onClick={() => router.push(`/journal/${t.id}`)}
                className="cursor-pointer bg-panel hover:bg-panel-raised"
              >
                <td className="px-4 py-2.5 text-text-muted">{formatDate(t.created_at)}</td>
                <td className="px-4 py-2.5">{t.strategy_name}</td>
                <td className="numeric px-4 py-2.5">{t.symbol}</td>
                <td className="px-4 py-2.5 capitalize text-text-muted">{t.direction}</td>
                <td className="numeric px-4 py-2.5 text-right">
                  {formatMoney(t.risk.risk_amount, currency)}
                </td>
                <td className={cn("px-4 py-2.5 capitalize", t.result ? RESULT_TONE[t.result] : "")}>
                  {t.result ?? "—"}
                </td>
                <td className={cn("numeric px-4 py-2.5 text-right", signedColor(t.pnl))}>
                  {t.pnl != null ? formatMoney(t.pnl, currency) : "—"}
                </td>
                <td className={cn("numeric px-4 py-2.5 text-right", signedColor(t.r_multiple))}>
                  {t.r_multiple != null ? `${toNumber(t.r_multiple).toFixed(2)}R` : "—"}
                </td>
                <td className="px-4 py-2.5">
                  <span
                    className={cn(
                      "rounded border px-1.5 py-0.5 text-[10px] uppercase",
                      STATUS_TONE[t.status],
                    )}
                  >
                    {t.status}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-right" onClick={(e) => e.stopPropagation()}>
                  {t.status === "draft" ? (
                    <button
                      type="button"
                      onClick={() => onOpen(t)}
                      className="rounded border border-border px-2 py-1 text-xs text-text-muted hover:text-text"
                    >
                      Open
                    </button>
                  ) : t.status === "open" ? (
                    <button
                      type="button"
                      onClick={() => setClosingId(t.id)}
                      className="rounded border border-border px-2 py-1 text-xs text-text-muted hover:text-text"
                    >
                      Close
                    </button>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!isLoading && total === 0 ? (
          <div className="bg-panel p-8">
            <EmptyState
              title="No trades yet"
              description="Plan your first trade to start building your journal."
              action={
                <Link
                  href="/trade-planner"
                  className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90"
                >
                  Go to Trade Planner
                </Link>
              }
            />
          </div>
        ) : null}
      </div>

      {/* Pagination */}
      {total > 0 ? (
        <div className="flex items-center justify-between text-sm text-text-muted">
          <span>
            {total} trade{total === 1 ? "" : "s"} · page {page} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="rounded-md border border-border px-3 py-1.5 disabled:opacity-50"
            >
              Prev
            </button>
            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="rounded-md border border-border px-3 py-1.5 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      ) : null}

      {closingId ? (
        <CloseTradeDialog tradeId={closingId} onClose={() => setClosingId(null)} />
      ) : null}
    </div>
  );
}

function Select<T extends string>({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: T;
  onChange: (v: T) => void;
  options: [string, string][];
}) {
  return (
    <label className="space-y-1">
      <span className="block text-xs text-text-muted">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="rounded-md border border-border bg-panel-raised px-2 py-1.5 text-sm text-text outline-none focus:border-accent"
      >
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
}
