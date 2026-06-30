import { COPY } from "@/lib/constants";
import { cn } from "@/lib/utils";

/**
 * Honest empty state for data-driven surfaces. Never fabricates numbers.
 * `variant="ai"` uses the SOC recommendation string; default uses the UI string.
 */
export function InsufficientData({
  variant = "ui",
  className,
}: {
  variant?: "ui" | "ai";
  className?: string;
}) {
  const message = variant === "ai" ? COPY.AI_INSUFFICIENT_DATA : COPY.UI_INSUFFICIENT_DATA;
  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-lg border border-dashed border-border bg-panel/40 p-6 text-center text-sm text-text-muted",
        className,
      )}
    >
      {message}
    </div>
  );
}
