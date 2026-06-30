import type { ConfidenceLevel } from "@/lib/constants";
import { cn } from "@/lib/utils";

const STYLES: Record<ConfidenceLevel, { label: string; className: string }> = {
  high: { label: "High Confidence", className: "text-success border-success/40 bg-success/10" },
  medium: { label: "Medium Confidence", className: "text-accent border-accent/40 bg-accent/10" },
  low: { label: "Low Confidence", className: "text-warning border-warning/40 bg-warning/10" },
  insufficient: {
    label: "Insufficient Data",
    className: "text-neutral border-neutral/40 bg-neutral/10",
  },
};

/** Required on every AI output (UX "AI Behavior Design"). */
export function ConfidenceBadge({ level }: { level: ConfidenceLevel }) {
  const { label, className } = STYLES[level];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        className,
      )}
    >
      {label}
    </span>
  );
}
