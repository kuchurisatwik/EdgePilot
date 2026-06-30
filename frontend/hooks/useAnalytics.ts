import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { analyticsApi } from "@/services/analyticsApi";

const ANALYTICS_STALE = 60_000;

function useAuthedQuery<T>(key: unknown[], queryFn: () => Promise<T>) {
  const { status } = useAuth();
  return useQuery({
    queryKey: key,
    queryFn,
    enabled: status === "authenticated",
    staleTime: ANALYTICS_STALE,
  });
}

export function useDashboard() {
  return useAuthedQuery(["analytics", "dashboard"], analyticsApi.dashboard);
}

export function useAnalyticsSummary() {
  return useAuthedQuery(["analytics", "summary"], analyticsApi.summary);
}

export function useEquityCurve() {
  return useAuthedQuery(["analytics", "equity-curve"], analyticsApi.equityCurve);
}

export function useStrategyPerformance() {
  return useAuthedQuery(["analytics", "strategy"], analyticsApi.strategy);
}

export function useSessionPerformance() {
  return useAuthedQuery(["analytics", "session"], analyticsApi.session);
}

export function usePeriodPerformance(period: "weekly" | "monthly") {
  return useAuthedQuery(["analytics", "period", period], () => analyticsApi.period(period));
}
