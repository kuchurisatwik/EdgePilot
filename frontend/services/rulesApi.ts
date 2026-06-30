import { api } from "@/services/apiClient";
import type { RiskRule, RuleSeverity, RuleType } from "@/types";

export type RuleUpdate = {
  threshold?: number;
  severity?: RuleSeverity;
  is_enabled?: boolean;
};

export const rulesApi = {
  list: () => api.get<RiskRule[]>("/api/rules"),
  update: (ruleType: RuleType, body: RuleUpdate) =>
    api.put<RiskRule>(`/api/rules/${ruleType}`, body),
};
