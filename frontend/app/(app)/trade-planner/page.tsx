"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { RiskPanel } from "@/components/risk/RiskPanel";
import { StrategySelect } from "@/components/strategies/StrategySelect";
import { Field } from "@/components/ui/Field";
import { useSettings } from "@/hooks/useSettings";
import { usePlanTrade, useRiskCalc } from "@/hooks/useTrades";
import { cn } from "@/lib/utils";
import { ApiError } from "@/services/apiClient";
import type { RiskCalcInput } from "@/services/tradeApi";
import type { OrderType, TradeDirection } from "@/types";

function parseNum(value: string): number | null {
  if (value.trim() === "") return null;
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function Toggle<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
}) {
  return (
    <div className="inline-flex rounded-md border border-border p-0.5">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={cn(
            "rounded px-3 py-1 text-sm capitalize transition-colors",
            value === o.value ? "bg-accent text-white" : "text-text-muted hover:text-text",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

export default function TradePlannerPage() {
  const { data: settings } = useSettings();
  const planTrade = usePlanTrade();

  const [strategyId, setStrategyId] = useState<string | null>(null);
  const [symbol, setSymbol] = useState("");
  const [direction, setDirection] = useState<TradeDirection>("long");
  const [orderType, setOrderType] = useState<OrderType>("market");
  const [entry, setEntry] = useState("");
  const [stop, setStop] = useState("");
  const [target, setTarget] = useState("");
  const [currentPrice, setCurrentPrice] = useState("");
  const [notes, setNotes] = useState("");

  const [planError, setPlanError] = useState<string | null>(null);
  const [savedId, setSavedId] = useState<string | null>(null);

  const entryN = parseNum(entry);
  const stopN = parseNum(stop);
  const targetN = parseNum(target);

  // Stable identity so the debounce only fires on real value changes.
  const calcInput = useMemo<RiskCalcInput | null>(() => {
    if (entryN == null || stopN == null || entryN === stopN) return null;
    return { entry_price: entryN, stop_loss: stopN, take_profit: targetN };
  }, [entryN, stopN, targetN]);

  const { data: breakdown, isFetching, error } = useRiskCalc(calcInput);
  const currency = settings?.quote_currency ?? "USDT";

  const canPlan =
    strategyId != null && symbol.trim().length > 0 && entryN != null && stopN != null;

  async function onPlan() {
    setPlanError(null);
    setSavedId(null);
    if (!canPlan || strategyId == null || entryN == null || stopN == null) {
      setPlanError("Select a strategy and enter a symbol, entry and stop.");
      return;
    }
    try {
      const trade = await planTrade.mutateAsync({
        strategy_id: strategyId,
        symbol: symbol.trim(),
        direction,
        order_type: orderType,
        entry_price: entryN,
        stop_loss: stopN,
        take_profit: targetN,
        current_price: parseNum(currentPrice),
        notes: notes.trim() || null,
      });
      setSavedId(trade.id);
    } catch (err) {
      setPlanError(err instanceof ApiError ? err.message : "Could not plan the trade.");
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-text">Trade Planner</h1>
        <p className="text-sm text-text-muted">
          Validate a trade before execution. Risk updates live as you type.
        </p>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* LEFT: setup */}
        <section className="col-span-12 space-y-4 rounded-lg border border-border bg-panel p-5 lg:col-span-3">
          <div className="space-y-1">
            <span className="text-xs font-medium text-text-muted">Strategy</span>
            <StrategySelect value={strategyId} onChange={setStrategyId} />
          </div>
          <div className="space-y-1">
            <span className="text-xs font-medium text-text-muted">Order type</span>
            <div>
              <Toggle
                value={orderType}
                onChange={setOrderType}
                options={[
                  { value: "market", label: "Market" },
                  { value: "limit", label: "Limit" },
                ]}
              />
            </div>
          </div>
          <Field
            label="Symbol"
            placeholder="BTC_USDT"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          />
          <label className="block space-y-1">
            <span className="text-xs font-medium text-text-muted">Notes (optional)</span>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              className="w-full rounded-md border border-border bg-panel-raised px-3 py-2 text-sm text-text outline-none focus:border-accent"
            />
          </label>
        </section>

        {/* CENTER: prices */}
        <section className="col-span-12 space-y-4 rounded-lg border border-border bg-panel p-5 lg:col-span-5">
          <div className="space-y-1">
            <span className="text-xs font-medium text-text-muted">Direction</span>
            <div>
              <Toggle
                value={direction}
                onChange={setDirection}
                options={[
                  { value: "long", label: "Long" },
                  { value: "short", label: "Short" },
                ]}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Field
              label="Entry price"
              type="number"
              step="any"
              value={entry}
              onChange={(e) => setEntry(e.target.value)}
            />
            <Field
              label="Stop loss"
              type="number"
              step="any"
              value={stop}
              onChange={(e) => setStop(e.target.value)}
            />
            <Field
              label="Target (optional)"
              type="number"
              step="any"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
            />
            <Field
              label="Current price (optional)"
              type="number"
              step="any"
              value={currentPrice}
              onChange={(e) => setCurrentPrice(e.target.value)}
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              type="button"
              onClick={onPlan}
              disabled={!canPlan || planTrade.isPending}
              className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-60"
            >
              {planTrade.isPending ? "Saving…" : "Plan Trade (save draft)"}
            </button>
            {savedId ? (
              <span className="text-sm text-success">
                Draft saved.{" "}
                <Link href="/journal" className="underline">
                  View in Journal
                </Link>
              </span>
            ) : null}
            {planError ? <span className="text-sm text-danger">{planError}</span> : null}
          </div>
        </section>

        {/* RIGHT: always-visible risk */}
        <aside className="col-span-12 rounded-lg border border-border bg-panel-raised p-5 lg:col-span-4">
          <RiskPanel
            breakdown={breakdown}
            currency={currency}
            loading={isFetching}
            error={error instanceof ApiError ? error.message : null}
          />
        </aside>
      </div>

      {/* BOTTOM: locked AI recommendation */}
      <div className="rounded-lg border border-border bg-panel p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text">AI Recommendation</h2>
          <span className="rounded border border-border px-2 py-0.5 text-[10px] uppercase tracking-wide text-text-muted">
            Locked
          </span>
        </div>
        <p className="mt-2 max-w-3xl text-sm text-text-muted">
          Historical similarity, win rate and a Take / Reduce / Avoid recommendation unlock in M9,
          once enough trades have been collected. The platform never fabricates confidence.
        </p>
      </div>
    </div>
  );
}
