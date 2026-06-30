import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/AuthContext";
import { screenshotsApi } from "@/services/screenshotsApi";
import type { ScreenshotSlot } from "@/types";

export function useScreenshots(tradeId: string) {
  const { status } = useAuth();
  return useQuery({
    queryKey: ["screenshots", tradeId],
    queryFn: () => screenshotsApi.list(tradeId),
    enabled: status === "authenticated",
  });
}

export function useUploadScreenshot(tradeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ slot, file }: { slot: ScreenshotSlot; file: File }) =>
      screenshotsApi.upload(tradeId, slot, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["screenshots", tradeId] }),
  });
}

export function useDeleteScreenshot(tradeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (screenshotId: string) => screenshotsApi.remove(screenshotId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["screenshots", tradeId] }),
  });
}
