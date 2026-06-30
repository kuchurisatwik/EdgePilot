import { api } from "@/services/apiClient";
import type { Screenshot, ScreenshotSlot } from "@/types";

export const screenshotsApi = {
  list: (tradeId: string) => api.get<Screenshot[]>(`/api/trades/${tradeId}/screenshots`),
  upload: (tradeId: string, slot: ScreenshotSlot, file: File) => {
    const form = new FormData();
    form.append("slot", slot);
    form.append("file", file);
    return api.upload<Screenshot>(`/api/trades/${tradeId}/screenshots`, form);
  },
  remove: (screenshotId: string) => api.del<void>(`/api/screenshots/${screenshotId}`),
};
