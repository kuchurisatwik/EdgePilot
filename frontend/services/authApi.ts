import { api } from "@/services/apiClient";
import type { AuthUser, TokenResponse } from "@/types";

export const authApi = {
  register: (body: { email: string; password: string; name: string }) =>
    api.post<TokenResponse>("/api/auth/register", body),

  login: (body: { email: string; password: string }) =>
    api.post<TokenResponse>("/api/auth/login", body),

  /** Uses the httpOnly refresh cookie; returns a fresh access token + user. */
  refresh: () => api.post<TokenResponse>("/api/auth/refresh"),

  logout: () => api.post<{ message: string }>("/api/auth/logout"),

  me: () => api.get<AuthUser>("/api/auth/me"),
};
