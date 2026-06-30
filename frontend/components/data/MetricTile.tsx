import { cn } from "@/lib/utils";

type Tone = "default" | "success" | "warning" | "danger" | "neutral";

const TONE_TEXT: Record<Tone, string> = {
  default: "text-text",
  success: "text-success",
  warning: "text-warning",
  danger: "text-danger",
  neutral: "text-neutral",
};

/** Big-number card for risk metrics and dashboard KPIs (readable from a distance). */
export function MetricTile({
  label,
  value,
  hint,
  tone = "default",
  className,
}: {
  label: string;
  value: string;
  hint?: string;
  tone?: Tone;
  className?: string;
}) {
  return (
    <div className={cn("rounded-lg border border-border bg-panel p-4", className)}>
      <p className="text-xs font-medium uppercase tracking-wide text-text-muted">{label}</p>
      <p className={cn("numeric-lg mt-1", TONE_TEXT[tone])}>{value}</p>
      {hint ? <p className="mt-1 text-xs text-text-muted">{hint}</p> : null}
    </div>
  );
}
