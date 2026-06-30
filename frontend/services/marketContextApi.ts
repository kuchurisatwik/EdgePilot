import { api } from "@/services/apiClient";
import type { MarketContext } from "@/types";

export const marketContextApi = {
  get: (tradeId: string) => api.get<MarketContext>(`/api/market-context/${tradeId}`),
};
