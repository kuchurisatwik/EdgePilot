"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/features/auth/AuthContext";

/** Gate for protected routes: redirects to /login once the session is known. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [status, router]);

  if (status !== "authenticated") {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-text-muted">
        {status === "loading" ? "Loading session…" : "Redirecting to sign in…"}
      </div>
    );
  }

  return <>{children}</>;
}
