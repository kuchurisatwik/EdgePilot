"use client";

import { Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Field } from "@/components/ui/Field";
import {
  useCreateStrategy,
  useDeleteStrategy,
  useStrategies,
  useUpdateStrategy,
} from "@/hooks/useStrategies";
import { cn } from "@/lib/utils";
import { ApiError } from "@/services/apiClient";
import type { RiskAppetite, Strategy } from "@/types";

const RISK_OPTIONS: RiskAppetite[] = ["conservative", "moderate", "aggressive"];

const RISK_STYLES: Record<RiskAppetite, string> = {
  conservative: "text-success border-success/40",
  moderate: "text-warning border-warning/40",
  aggressive: "text-danger border-danger/40",
};

type FormValues = {
  name: string;
  risk_appetite: RiskAppetite;
  description: string;
  notes: string;
};

function StrategyForm({
  initial,
  submitting,
  error,
  submitLabel,
  onSubmit,
  onCancel,
}: {
  initial?: Partial<Strategy>;
  submitting: boolean;
  error: string | null;
  submitLabel: string;
  onSubmit: (values: FormValues) => void;
  onCancel: () => void;
}) {
  const [values, setValues] = useState<FormValues>({
    name: initial?.name ?? "",
    risk_appetite: initial?.risk_appetite ?? "moderate",
    description: initial?.description ?? "",
    notes: initial?.notes ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(values);
      }}
      className="space-y-3 rounded-md border border-border bg-panel-raised p-4"
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <Field
          label="Name"
          value={values.name}
          onChange={(e) => setValues((v) => ({ ...v, name: e.target.value }))}
        />
        <label className="block space-y-1">
          <span className="text-xs font-medium text-text-muted">Risk appetite</span>
          <select
            value={values.risk_appetite}
            onChange={(e) =>
              setValues((v) => ({ ...v, risk_appetite: e.target.value as RiskAppetite }))
            }
            className="w-full rounded-md border border-border bg-panel px-3 py-2 text-sm capitalize text-text outline-none focus:border-accent"
          >
            {RISK_OPTIONS.map((r) => (
              <option key={r} value={r} className="capitalize">
                {r}
              </option>
            ))}
          </select>
        </label>
      </div>
      <Field
        label="Description (optional)"
        value={values.description}
        onChange={(e) => setValues((v) => ({ ...v, description: e.target.value }))}
      />
      <Field
        label="Notes (optional)"
        value={values.notes}
        onChange={(e) => setValues((v) => ({ ...v, notes: e.target.value }))}
      />
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <div className="flex items-center gap-2">
        <button
          type="submit"
          disabled={submitting || values.name.trim().length === 0}
          className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-60"
        >
          {submitting ? "Saving…" : submitLabel}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-border px-3 py-1.5 text-sm text-text-muted hover:text-text"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

function toInput(values: FormValues) {
  return {
    name: values.name.trim(),
    risk_appetite: values.risk_appetite,
    description: values.description.trim() || null,
    notes: values.notes.trim() || null,
  };
}

export function StrategyManager() {
  const { data: strategies, isLoading } = useStrategies();
  const createStrategy = useCreateStrategy();
  const updateStrategy = useUpdateStrategy();
  const deleteStrategy = useDeleteStrategy();

  const [creating, setCreating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function errorMessage(err: unknown, fallback: string) {
    return err instanceof ApiError ? err.message : fallback;
  }

  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-text">Strategies</h2>
          <p className="text-xs text-text-muted">
            Six defaults are provided; add your own. Every trade references a strategy.
          </p>
        </div>
        {!creating ? (
          <button
            type="button"
            onClick={() => {
              setError(null);
              setCreating(true);
              setEditingId(null);
            }}
            className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-sm text-text-muted hover:bg-panel-raised hover:text-text"
          >
            <Plus size={15} />
            New strategy
          </button>
        ) : null}
      </div>

      {creating ? (
        <div className="mb-4">
          <StrategyForm
            submitting={createStrategy.isPending}
            error={error}
            submitLabel="Create"
            onCancel={() => {
              setCreating(false);
              setError(null);
            }}
            onSubmit={async (values) => {
              setError(null);
              try {
                await createStrategy.mutateAsync(toInput(values));
                setCreating(false);
              } catch (err) {
                setError(errorMessage(err, "Could not create strategy."));
              }
            }}
          />
        </div>
      ) : null}

      {isLoading ? (
        <p className="text-sm text-text-muted">Loading…</p>
      ) : (
        <ul className="space-y-2">
          {strategies?.map((s) =>
            editingId === s.id ? (
              <li key={s.id}>
                <StrategyForm
                  initial={s}
                  submitting={updateStrategy.isPending}
                  error={error}
                  submitLabel="Save"
                  onCancel={() => {
                    setEditingId(null);
                    setError(null);
                  }}
                  onSubmit={async (values) => {
                    setError(null);
                    try {
                      await updateStrategy.mutateAsync({ id: s.id, body: toInput(values) });
                      setEditingId(null);
                    } catch (err) {
                      setError(errorMessage(err, "Could not update strategy."));
                    }
                  }}
                />
              </li>
            ) : (
              <li
                key={s.id}
                className="flex items-center justify-between rounded-md border border-border bg-panel-raised px-4 py-3"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="truncate text-sm font-medium text-text">{s.name}</span>
                    <span
                      className={cn(
                        "rounded border px-1.5 py-0.5 text-[10px] uppercase tracking-wide",
                        RISK_STYLES[s.risk_appetite],
                      )}
                    >
                      {s.risk_appetite}
                    </span>
                    {s.is_default ? (
                      <span className="rounded border border-border px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-text-muted">
                        default
                      </span>
                    ) : null}
                  </div>
                  {s.description ? (
                    <p className="mt-0.5 truncate text-xs text-text-muted">{s.description}</p>
                  ) : null}
                </div>
                <div className="ml-3 flex shrink-0 items-center gap-1">
                  <button
                    type="button"
                    aria-label={`Edit ${s.name}`}
                    onClick={() => {
                      setError(null);
                      setEditingId(s.id);
                      setCreating(false);
                    }}
                    className="rounded p-1.5 text-text-muted hover:bg-panel hover:text-text"
                  >
                    <Pencil size={15} />
                  </button>
                  {!s.is_default ? (
                    <button
                      type="button"
                      aria-label={`Delete ${s.name}`}
                      onClick={async () => {
                        if (!window.confirm(`Deactivate strategy "${s.name}"?`)) return;
                        try {
                          await deleteStrategy.mutateAsync(s.id);
                        } catch {
                          setError("Could not delete strategy.");
                        }
                      }}
                      className="rounded p-1.5 text-text-muted hover:bg-panel hover:text-danger"
                    >
                      <Trash2 size={15} />
                    </button>
                  ) : null}
                </div>
              </li>
            ),
          )}
        </ul>
      )}
    </section>
  );
}
