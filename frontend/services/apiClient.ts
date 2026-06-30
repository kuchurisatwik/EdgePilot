/**
 * Thin fetch wrapper for the backend API.
 *
 * - Attaches the in-memory access token as a Bearer header.
 * - Sends cookies (credentials: "include") so the httpOnly refresh cookie flows.
 * - On 401, performs a single-flight refresh and retries once (wired in M1 once
 *   the /api/auth/refresh endpoint exists).
 * - Normalizes the backend error envelope `{ error: { code, message } }`.
 */

import { tokenStorage } from "@/lib/tokenStorage";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

type RequestOptions = Omit<RequestInit, "body"> & { body?: unknown };

let refreshInFlight: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  // Implemented in M1. For now, no refresh endpoint exists yet.
  return false;
}

async function rawRequest<T>(path: string, options: RequestOptions): Promise<T> {
  const { body, headers, ...rest } = options;
  const token = tokenStorage.get();

  const response = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const err = (payload as { error?: { code?: string; message?: string } } | null)?.error;
    throw new ApiError(
      response.status,
      err?.code ?? "error",
      err?.message ?? response.statusText,
    );
  }

  return payload as T;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  try {
    return await rawRequest<T>(path, options);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401 && tokenStorage.get()) {
      refreshInFlight ??= refreshAccessToken().finally(() => {
        refreshInFlight = null;
      });
      const refreshed = await refreshInFlight;
      if (refreshed) {
        return rawRequest<T>(path, options);
      }
      tokenStorage.clear();
    }
    throw error;
  }
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "POST", body }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "PUT", body }),
  del: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "DELETE" }),
};

export type HealthResponse = { status: string; db: string };
