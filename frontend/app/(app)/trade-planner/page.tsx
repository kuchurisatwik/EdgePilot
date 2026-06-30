"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { InsufficientData } from "@/components/feedback/InsufficientData";
import { ReasoningBlock } from "@/components/feedback/ReasoningBlock";
import { RiskPanel } from "@/components/risk/RiskPanel";
import { StrategySelect } from "@/components/strategies/StrategySelect";
import { Field } from "@/components/ui/Field";
import { useSimilar } from "@/hooks/useAI";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { useSettings } from "@/hooks/useSettings";
import { usePlanTrade, useRiskCalc } from "@/hooks/useTrades";
import { cn } from "@/lib/utils";
import { toNumber } from "@/lib/format";
import { ApiError } from "@/services/apiClient";
import type { SimilarInput } from "@/services/aiApi";
import type { RiskCalcInput } from "@/services/tradeApi";
import type { OrderType, Recommendation, TradeDirection } from "@/types";

const RECOMMENDATION_LABEL: Record<Recommendation, string> = {
  take: "Take Trade",
  reduce: "Reduce Size",
  avoid: "Avoid Trade",
  insufficient: "Insufficient Data",
};

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

  const { data, isFetching, error } = useRiskCalc(calcInput);
  const breakdown = data?.risk;
  const rules = data?.rules;
  const currency = settings?.quote_currency ?? "USDT";

  // Live AI recommendation from historically similar trades (debounced).
  const similarRaw = useMemo<SimilarInput | null>(() => {
    if (strategyId == null || entryN == null || stopN == null || entryN === stopN) return null;
    return {
      strategy_id: strategyId,
      direction,
      entry_price: entryN,
      stop_loss: stopN,
      take_profit: targetN,
    };
  }, [strategyId, direction, entryN, stopN, targetN]);
  const similarInput = useDebouncedValue(similarRaw, 600);
  const { data: similar } = useSimilar(similarInput);

  const canPlan =
    strategyId != null && symbol.trim().length > 0 && entryN != null && stopN != null;

  async function submitPlan(acknowledgeOverride: boolean) {
    if (strategyId == null || entryN == null || stopN == null) return;
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
      acknowledge_override: acknowledgeOverride,
    });
    setSavedId(trade.id);
  }

  async function onPlan() {
    setPlanError(null);
    setSavedId(null);
    if (!canPlan) {
      setPlanError("Select a strategy and enter a symbol, entry and stop.");
      return;
    }

    // Override-with-acknowledgment: a BLOCK requires explicit confirmation.
    if (rules?.status === "BLOCK") {
      const reasons = rules.violations
        .filter((v) => v.severity === "block")
        .map((v) => `• ${v.message}`)
        .join("\n");
      if (!window.confirm(`This trade violates your rules:\n\n${reasons}\n\nOverride and save anyway?`)) {
        return;
      }
      try {
        await submitPlan(true);
      } catch (err) {
        setPlanError(err instanceof ApiError ? err.message : "Could not plan the trade.");
      }
      return;
    }

    try {
      await submitPlan(false);
    } catch (err) {
      // Server-side BLOCK fallback (rules changed since the last preview).
      if (err instanceof ApiError && err.code === "rule_block") {
        if (window.confirm(`${err.message}\n\nOverride and save anyway?`)) {
          try {
            await submitPlan(true);
          } catch (err2) {
            setPlanError(err2 instanceof ApiError ? err2.message : "Could not plan the trade.");
          }
        }
        return;
      }
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
              className={cn(
                "rounded-md px-4 py-2 text-sm font-medium text-white disabled:opacity-60",
                rules?.status === "BLOCK"
                  ? "bg-danger hover:bg-danger/90"
                  : "bg-accent hover:bg-accent/90",
              )}
            >
              {planTrade.isPending
                ? "Saving…"
                : rules?.status === "BLOCK"
                  ? "Override & Save Draft"
                  : "Plan Trade (save draft)"}
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
            rules={rules}
            currency={currency}
            loading={isFetching}
            error={error instanceof ApiError ? error.message : null}
          />
        </aside>
      </div>

      {/* BOTTOM: AI recommendation (secondary to the Risk panel; never overrides it) */}
      <div className="rounded-lg border border-border bg-panel p-5">
        <h2 className="text-sm font-semibold text-text">AI Recommendation</h2>
        {!similar ? (
          <p className="mt-2 text-sm text-text-muted">
            Enter a strategy, entry and stop to see what your history says.
          </p>
        ) : similar.recommendation === "insufficient" ? (
          <div className="mt-2">
            <InsufficientData variant="ai" />
          </div>
        ) : (
          <div className="mt-2 space-y-2">
            <ReasoningBlock
              recommendation={RECOMMENDATION_LABEL[similar.recommendation]}
              reasoning={similar.reasoning}
              confidence={similar.confidence}
            />
            <div className="flex flex-wrap gap-4 text-xs text-text-muted">
              <span>
                Similar trades: <span className="text-text">{similar.match_count}</span>
              </span>
              {similar.historical_win_rate != null ? (
                <span>
                  Historical win rate:{" "}
                  <span className="text-text">
                    {(toNumber(similar.historical_win_rate) * 100).toFixed(0)}%
                  </span>
                </span>
              ) : null}
              {similar.historical_avg_r != null ? (
                <span>
                  Avg R: <span className="text-text">{toNumber(similar.historical_avg_r).toFixed(2)}</span>
                </span>
              ) : null}
            </div>
            {rules?.status === "BLOCK" ? (
              <p className="text-xs text-danger">
                Your Risk Engine BLOCK overrides this suggestion — the trader stays responsible.
              </p>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}
