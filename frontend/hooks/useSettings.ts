import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { settingsApi, type SettingsUpdate } from "@/services/settingsApi";

export function useSettings() {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["settings"],
    queryFn: settingsApi.get,
    enabled: status === "authenticated",
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: SettingsUpdate) => settingsApi.update(body),
    onSuccess: (data) => queryClient.setQueryData(["settings"], data),
  });
}
