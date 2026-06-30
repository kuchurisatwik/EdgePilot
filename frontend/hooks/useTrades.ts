import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { tradeApi, type RiskCalcInput, type TradePlanInput } from "@/services/tradeApi";

/** Live risk preview. Pass `null` to disable (e.g. inputs not yet valid). */
export function useRiskCalc(input: RiskCalcInput | null) {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["risk-calc", input],
    queryFn: () => tradeApi.calculate(input as RiskCalcInput),
    enabled: status === "authenticated" && input !== null,
    placeholderData: keepPreviousData,
    retry: false,
    staleTime: 0,
  });
}

export function usePlanTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: TradePlanInput) => tradeApi.plan(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["trades"] }),
  });
}
