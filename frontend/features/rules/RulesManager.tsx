"use client";

import { useState } from "react";
import { useRules, useUpdateRule } from "@/hooks/useRules";
import type { RiskRule, RuleSeverity, RuleType } from "@/types";

const RULE_META: Record<RuleType, { label: string; unit: string }> = {
  max_risk_per_trade: { label: "Max risk per trade", unit: "%" },
  daily_loss_limit: { label: "Daily loss limit", unit: "% of account" },
  weekly_loss_limit: { label: "Weekly loss limit", unit: "% of account" },
  consecutive_loss_limit: { label: "Consecutive loss limit", unit: "trades" },
};

function RuleRow({ rule }: { rule: RiskRule }) {
  const updateRule = useUpdateRule();
  const [threshold, setThreshold] = useState(rule.threshold);
  const [severity, setSeverity] = useState<RuleSeverity>(rule.severity);
  const [enabled, setEnabled] = useState(rule.is_enabled);
  const [saved, setSaved] = useState(false);

  const meta = RULE_META[rule.rule_type];
  const dirty =
    threshold !== rule.threshold || severity !== rule.severity || enabled !== rule.is_enabled;

  async function save() {
    setSaved(false);
    await updateRule.mutateAsync({
      ruleType: rule.rule_type,
      body: { threshold: Number(threshold), severity, is_enabled: enabled },
    });
    setSaved(true);
  }

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-md border border-border bg-panel-raised px-4 py-3">
      <div className="min-w-[180px] flex-1">
        <p className="text-sm font-medium text-text">{meta.label}</p>
        <p className="text-xs text-text-muted">{meta.unit}</p>
      </div>
      <label className="space-y-1">
        <span className="block text-xs text-text-muted">Threshold</span>
        <input
          type="number"
          step="any"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          className="w-24 rounded-md border border-border bg-panel px-2 py-1.5 text-sm text-text outline-none focus:border-accent"
        />
      </label>
      <label className="space-y-1">
        <span className="block text-xs text-text-muted">Severity</span>
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value as RuleSeverity)}
          className="rounded-md border border-border bg-panel px-2 py-1.5 text-sm capitalize text-text outline-none focus:border-accent"
        >
          <option value="warning">Warning</option>
          <option value="block">Block</option>
        </select>
      </label>
      <label className="flex items-center gap-2 pb-1.5 text-sm text-text-muted">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => setEnabled(e.target.checked)}
          className="accent-accent"
        />
        Enabled
      </label>
      <button
        type="button"
        onClick={save}
        disabled={!dirty || updateRule.isPending}
        className="rounded-md border border-border px-3 py-1.5 text-sm text-text-muted hover:bg-panel hover:text-text disabled:opacity-50"
      >
        {updateRule.isPending ? "Saving…" : "Save"}
      </button>
      {saved && !dirty ? <span className="pb-1.5 text-xs text-success">Saved</span> : null}
    </div>
  );
}

export function RulesManager() {
  const { data: rules, isLoading } = useRules();

  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-text">Risk Rules</h2>
        <p className="text-xs text-text-muted">
          Validated on every trade. A BLOCK can be overridden with explicit acknowledgment —
          the override is recorded.
        </p>
      </div>
      {isLoading ? (
        <p className="text-sm text-text-muted">Loading…</p>
      ) : (
        <div className="space-y-2">
          {rules?.map((rule) => (
            <RuleRow key={rule.rule_type} rule={rule} />
          ))}
        </div>
      )}
    </section>
  );
}
