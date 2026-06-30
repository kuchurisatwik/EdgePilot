import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { rulesApi, type RuleUpdate } from "@/services/rulesApi";
import type { RuleType } from "@/types";

const KEY = ["rules"];

export function useRules() {
  const { status } = useAuth();
  return useQuery({
    queryKey: KEY,
    queryFn: rulesApi.list,
    enabled: status === "authenticated",
  });
}

export function useUpdateRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ ruleType, body }: { ruleType: RuleType; body: RuleUpdate }) =>
      rulesApi.update(ruleType, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}
