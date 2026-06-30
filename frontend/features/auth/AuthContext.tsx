"use client";

import { useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { tokenStorage } from "@/lib/tokenStorage";
import { authApi } from "@/services/authApi";
import type { AuthUser } from "@/types";

type Status = "loading" | "authenticated" | "unauthenticated";

type AuthContextValue = {
  user: AuthUser | null;
  status: Status;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<Status>("loading");
  const queryClient = useQueryClient();

  // Bootstrap: try to restore the session from the httpOnly refresh cookie.
  useEffect(() => {
    let active = true;
    authApi
      .refresh()
      .then((res) => {
        if (!active) return;
        tokenStorage.set(res.access_token);
        setUser(res.user);
        setStatus("authenticated");
      })
      .catch(() => {
        if (!active) return;
        tokenStorage.clear();
        setUser(null);
        setStatus("unauthenticated");
      });
    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      status,
      login: async (email, password) => {
        const res = await authApi.login({ email, password });
        tokenStorage.set(res.access_token);
        setUser(res.user);
        setStatus("authenticated");
      },
      register: async (email, password, name) => {
        const res = await authApi.register({ email, password, name });
        tokenStorage.set(res.access_token);
        setUser(res.user);
        setStatus("authenticated");
      },
      logout: async () => {
        try {
          await authApi.logout();
        } finally {
          tokenStorage.clear();
          setUser(null);
          setStatus("unauthenticated");
          queryClient.clear();
        }
      },
      refreshUser: async () => {
        setUser(await authApi.me());
      },
    }),
    [user, status, queryClient],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
