import { api } from "@/services/apiClient";
import type {
  JournalFilters,
  OrderType,
  RiskCalcResponse,
  Trade,
  TradeDirection,
  TradeListResponse,
} from "@/types";

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

function journalQuery(filters: JournalFilters): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const tradeApi = {
  calculate: (body: RiskCalcInput) => api.post<RiskCalcResponse>("/api/risk/calculate", body),
  plan: (body: TradePlanInput) => api.post<Trade>("/api/trades/plan", body),
  get: (id: string) => api.get<Trade>(`/api/journal/${id}`),
  journal: (filters: JournalFilters) =>
    api.get<TradeListResponse>(`/api/journal${journalQuery(filters)}`),
  open: (id: string, acknowledgeOverride = false) =>
    api.post<Trade>(`/api/trades/${id}/open`, { acknowledge_override: acknowledgeOverride }),
  close: (id: string, body: { exit_price: number; exit_notes?: string | null }) =>
    api.post<Trade>(`/api/trades/${id}/close`, body),
  remove: (id: string) => api.del<void>(`/api/trades/${id}`),
};
