import { LogOut } from "lucide-react";

/**
 * Top bar: account/balance summary + logout. Balance is a placeholder until M1
 * (settings) and M6 (analytics) wire real values.
 */
export function Topbar() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-panel px-5">
      <div className="text-sm text-text-muted">
        Decision support — the trader stays responsible for execution.
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-xs text-text-muted">Account</p>
          <p className="numeric text-sm font-medium text-text">—</p>
        </div>
        <button
          type="button"
          className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-sm text-text-muted hover:bg-panel-raised hover:text-text"
          aria-label="Log out"
          disabled
        >
          <LogOut size={15} />
          Logout
        </button>
      </div>
    </header>
  );
}
