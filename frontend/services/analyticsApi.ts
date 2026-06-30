import { api } from "@/services/apiClient";
import type {
  AnalyticsSummary,
  DashboardSummary,
  EquityCurveResponse,
  GroupPerformance,
} from "@/types";

export const analyticsApi = {
  summary: () => api.get<AnalyticsSummary>("/api/analytics/summary"),
  equityCurve: () => api.get<EquityCurveResponse>("/api/analytics/equity-curve"),
  strategy: () => api.get<GroupPerformance[]>("/api/analytics/strategy"),
  session: () => api.get<GroupPerformance[]>("/api/analytics/session"),
  period: (period: "weekly" | "monthly") =>
    api.get<GroupPerformance[]>(`/api/analytics/period?period=${period}`),
  dashboard: () => api.get<DashboardSummary>("/api/analytics/dashboard"),
};
