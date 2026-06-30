import { api } from "@/services/apiClient";
import type { OrderType, RiskCalcResponse, Trade, TradeDirection } from "@/types";

export type RiskCalcInput = {
  entry_price: number;
  stop_loss: number;
  take_profit?: number | null;
  risk_pct?: number | null;
};

export type TradePlanInput = {
  strategy_id: string;
  symbol: string;
  direction: TradeDirection;
  order_type: OrderType;
  entry_price: number;
  stop_loss: number;
  take_profit?: number | null;
  current_price?: number | null;
  risk_pct?: number | null;
  notes?: string | null;
  thesis?: string | null;
  acknowledge_override?: boolean;
};

export const tradeApi = {
  calculate: (body: RiskCalcInput) => api.post<RiskCalcResponse>("/api/risk/calculate", body),
  plan: (body: TradePlanInput) => api.post<Trade>("/api/trades/plan", body),
  get: (id: string) => api.get<Trade>(`/api/trades/${id}`),
  list: () => api.get<Trade[]>("/api/trades"),
};
