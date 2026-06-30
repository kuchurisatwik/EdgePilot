import { api } from "@/services/apiClient";
import type { AIInsightResponse, SimilarTradeAnalysis, TradeDirection } from "@/types";

export type SimilarInput = {
  strategy_id: string;
  direction: TradeDirection;
  entry_price: number;
  stop_loss: number;
  take_profit?: number | null;
  risk_pct?: number | null;
};

export const aiApi = {
  performance: () => api.get<AIInsightResponse>("/api/ai/performance"),
  tradeSummary: (tradeId: string) =>
    api.get<AIInsightResponse>(`/api/ai/trades/${tradeId}/summary`),
  similar: (body: SimilarInput) => api.post<SimilarTradeAnalysis>("/api/ai/similar", body),
};
