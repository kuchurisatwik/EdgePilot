import { api } from "@/services/apiClient";
import type { AuthUser, UserSettings } from "@/types";

export type SettingsUpdate = {
  account_size?: number;
  default_risk_pct?: number;
  quote_currency?: string;
  timezone?: string;
};

export const settingsApi = {
  get: () => api.get<UserSettings>("/api/settings"),
  update: (body: SettingsUpdate) => api.put<UserSettings>("/api/settings", body),
  updateProfile: (body: { name: string }) => api.put<AuthUser>("/api/profile", body),
};
