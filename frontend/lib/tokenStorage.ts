/**
 * Access-token storage abstraction.
 *
 * The access token lives in memory only (XSS-safe). The refresh token is held
 * in an httpOnly cookie set by the backend (M1), so it is never touched here.
 * Centralizing access here means the strategy can change without touching callers.
 */

let accessToken: string | null = null;

export const tokenStorage = {
  get(): string | null {
    return accessToken;
  },
  set(token: string | null): void {
    accessToken = token;
  },
  clear(): void {
    accessToken = null;
  },
};
