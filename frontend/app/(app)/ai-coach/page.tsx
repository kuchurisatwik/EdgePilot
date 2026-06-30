"use client";

import type { ReactNode } from "react";
import { AIInsightView } from "@/components/ai/AIInsightView";
import { useAIPerformance } from "@/hooks/useAI";

function Section({
  title,
  locked,
  children,
}: {
  title: string;
  locked?: boolean;
  children: ReactNode;
}) {
  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text">{title}</h2>
        {locked ? (
          <span className="rounded border border-border px-2 py-0.5 text-[10px] uppercase tracking-wide text-text-muted">
            Locked
          </span>
        ) : null}
      </div>
      {children}
    </section>
  );
}

export default function AiCoachPage() {
  const { data: performance, isLoading } = useAIPerformance();

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-text">AI Coach</h1>
        <p className="text-sm text-text-muted">
          AI explains your data — it never forces a decision, and never fabricates confidence.
        </p>
      </div>

      <Section title="Performance Coaching">
        <AIInsightView insight={performance} loading={isLoading} />
      </Section>

      <Section title="Behavior Coaching" locked>
        <p className="text-sm text-text-muted">
          Overtrading, revenge trading, FOMO and early exits — behavioral pattern detection
          arrives in M10.
        </p>
      </Section>

      <Section title="Strategy Coaching" locked>
        <p className="text-sm text-text-muted">
          When each strategy works best (and what to avoid) — strategy intelligence arrives in M10.
        </p>
      </Section>
    </div>
  );
}
