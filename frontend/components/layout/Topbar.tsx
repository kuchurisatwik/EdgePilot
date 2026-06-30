"use client";

import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/features/auth/AuthContext";
import { useSettings } from "@/hooks/useSettings";
import { formatMoney } from "@/lib/format";

export function Topbar() {
  const { user, logout } = useAuth();
  const { data: settings } = useSettings();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-panel px-5">
      <div className="text-sm text-text-muted">
        Decision support — the trader stays responsible for execution.
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-xs text-text-muted">{user?.name ?? "Account"}</p>
          <p className="numeric text-sm font-medium text-text">
            {settings ? formatMoney(settings.account_size, settings.quote_currency) : "—"}
          </p>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-sm text-text-muted hover:bg-panel-raised hover:text-text"
          aria-label="Log out"
        >
          <LogOut size={15} />
          Logout
        </button>
      </div>
    </header>
  );
}
