"use client";

import { useStrategies } from "@/hooks/useStrategies";
import { cn } from "@/lib/utils";

type StrategySelectProps = {
  value: string | null;
  onChange: (id: string) => void;
  id?: string;
  className?: string;
  disabled?: boolean;
};

/** Reusable active-strategy picker. Used in Settings and the Trade Planner (M3). */
export function StrategySelect({ value, onChange, id, className, disabled }: StrategySelectProps) {
  const { data: strategies, isLoading } = useStrategies();

  return (
    <select
      id={id}
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled || isLoading}
      className={cn(
        "w-full rounded-md border border-border bg-panel-raised px-3 py-2 text-sm text-text outline-none focus:border-accent disabled:opacity-60",
        className,
      )}
    >
      <option value="" disabled>
        {isLoading ? "Loading strategies…" : "Select a strategy…"}
      </option>
      {strategies?.map((s) => (
        <option key={s.id} value={s.id}>
          {s.name}
        </option>
      ))}
    </select>
  );
}
