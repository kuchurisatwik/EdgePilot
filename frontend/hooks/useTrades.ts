import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { tradeApi, type RiskCalcInput, type TradePlanInput } from "@/services/tradeApi";
import type { JournalFilters } from "@/types";

function invalidateTrades(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ["journal"] });
  qc.invalidateQueries({ queryKey: ["trade"] });
}

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
    onSuccess: () => invalidateTrades(qc),
  });
}

export function useJournal(filters: JournalFilters) {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["journal", filters],
    queryFn: () => tradeApi.journal(filters),
    enabled: status === "authenticated",
    placeholderData: keepPreviousData,
  });
}

export function useTrade(id: string | null) {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["trade", id],
    queryFn: () => tradeApi.get(id as string),
    enabled: status === "authenticated" && id !== null,
  });
}

export function useOpenTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, acknowledgeOverride }: { id: string; acknowledgeOverride?: boolean }) =>
      tradeApi.open(id, acknowledgeOverride ?? false),
    onSuccess: () => invalidateTrades(qc),
  });
}

export function useCloseTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      exitPrice,
      exitNotes,
    }: {
      id: string;
      exitPrice: number;
      exitNotes?: string | null;
    }) => tradeApi.close(id, { exit_price: exitPrice, exit_notes: exitNotes }),
    onSuccess: () => invalidateTrades(qc),
  });
}

export function useDeleteTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => tradeApi.remove(id),
    onSuccess: () => invalidateTrades(qc),
  });
}
