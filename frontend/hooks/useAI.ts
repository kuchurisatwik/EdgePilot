import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { aiApi, type SimilarInput } from "@/services/aiApi";

export function useAIPerformance() {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["ai", "performance"],
    queryFn: aiApi.performance,
    enabled: status === "authenticated",
    staleTime: 60_000,
  });
}

export function useTradeSummary(tradeId: string, enabled: boolean) {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["ai", "summary", tradeId],
    queryFn: () => aiApi.tradeSummary(tradeId),
    enabled: status === "authenticated" && enabled,
  });
}

/** Live similar-trade analysis for the Trade Planner. Pass null to disable. */
export function useSimilar(input: SimilarInput | null) {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["ai", "similar", input],
    queryFn: () => aiApi.similar(input as SimilarInput),
    enabled: status === "authenticated" && input !== null,
    placeholderData: keepPreviousData,
    retry: false,
  });
}
