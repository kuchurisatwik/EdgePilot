"use client";

import { ConfidenceBadge } from "@/components/feedback/ConfidenceBadge";
import { InsufficientData } from "@/components/feedback/InsufficientData";
import type { AIInsightResponse } from "@/types";

/** Renders an AI narrative + its confidence, or the honest insufficient-data state. */
export function AIInsightView({
  insight,
  loading,
}: {
  insight?: AIInsightResponse;
  loading?: boolean;
}) {
  if (loading) {
    return <p className="text-sm text-text-muted">Analyzing your history…</p>;
  }
  if (!insight || insight.confidence === "insufficient") {
    return <InsufficientData variant="ai" />;
  }
  return (
    <div className="space-y-2">
      <p className="text-sm text-text">{insight.content}</p>
      <ConfidenceBadge level={insight.confidence} />
    </div>
  );
}
