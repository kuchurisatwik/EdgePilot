import type { ConfidenceLevel } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { ConfidenceBadge } from "./ConfidenceBadge";

/**
 * Every AI recommendation MUST carry its reasoning — the `reasoning` prop is
 * required, so a recommendation can never render without it (UX: bad example
 * "Take this trade." vs good example with the why).
 */
export function ReasoningBlock({
  recommendation,
  reasoning,
  confidence,
  className,
}: {
  recommendation: string;
  reasoning: string;
  confidence: ConfidenceLevel;
  className?: string;
}) {
  return (
    <div className={cn("rounded-lg border border-border bg-panel-raised p-4", className)}>
      <div className="flex items-center justify-between gap-3">
        <p className="text-lg font-semibold text-text">{recommendation}</p>
        <ConfidenceBadge level={confidence} />
      </div>
      <p className="mt-2 text-sm text-text-muted">{reasoning}</p>
    </div>
  );
}
