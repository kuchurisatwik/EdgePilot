import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { marketContextApi } from "@/services/marketContextApi";

export function useMarketContext(tradeId: string, enabled: boolean) {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["market-context", tradeId],
    queryFn: () => marketContextApi.get(tradeId),
    enabled: status === "authenticated" && enabled,
    retry: false,
  });
}
