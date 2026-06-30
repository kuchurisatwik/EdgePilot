import { api } from "@/services/apiClient";
import type { RiskAppetite, Strategy } from "@/types";

export type StrategyInput = {
  name: string;
  description?: string | null;
  risk_appetite?: RiskAppetite;
  notes?: string | null;
};

export const strategyApi = {
  list: () => api.get<Strategy[]>("/api/strategies"),
  create: (body: StrategyInput) => api.post<Strategy>("/api/strategies", body),
  update: (id: string, body: Partial<StrategyInput>) =>
    api.put<Strategy>(`/api/strategies/${id}`, body),
  remove: (id: string) => api.del<void>(`/api/strategies/${id}`),
};
