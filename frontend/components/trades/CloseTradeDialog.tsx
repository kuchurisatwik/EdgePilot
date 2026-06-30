"use client";

import { useState } from "react";
import { Field } from "@/components/ui/Field";
import { useCloseTrade } from "@/hooks/useTrades";
import { ApiError } from "@/services/apiClient";

export function CloseTradeDialog({
  tradeId,
  onClose,
}: {
  tradeId: string;
  onClose: () => void;
}) {
  const closeTrade = useCloseTrade();
  const [exitPrice, setExitPrice] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    const n = Number(exitPrice);
    if (!Number.isFinite(n) || n <= 0) {
      setError("Enter a valid exit price.");
      return;
    }
    try {
      await closeTrade.mutateAsync({ id: tradeId, exitPrice: n, exitNotes: notes.trim() || null });
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not close the trade.");
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm rounded-lg border border-border bg-panel p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-base font-semibold text-text">Close trade</h2>
        <p className="mt-1 text-xs text-text-muted">
          PnL and R-multiple are computed from your exit price.
        </p>
        <div className="mt-4 space-y-3">
          <Field
            label="Exit price"
            type="number"
            step="any"
            value={exitPrice}
            onChange={(e) => setExitPrice(e.target.value)}
          />
          <label className="block space-y-1">
            <span className="text-xs font-medium text-text-muted">Exit notes (optional)</span>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full rounded-md border border-border bg-panel-raised px-3 py-2 text-sm text-text outline-none focus:border-accent"
            />
          </label>
          {error ? <p className="text-sm text-danger">{error}</p> : null}
        </div>
        <div className="mt-5 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-border px-3 py-1.5 text-sm text-text-muted hover:text-text"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={closeTrade.isPending}
            className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-60"
          >
            {closeTrade.isPending ? "Closing…" : "Close trade"}
          </button>
        </div>
      </div>
    </div>
  );
}
