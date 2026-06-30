import type { ReactNode } from "react";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { RiskStrip } from "@/components/layout/RiskStrip";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

/** Protected app shell: left sidebar + top bar + always-visible RiskStrip. */
export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <RequireAuth>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar />
          <RiskStrip />
          <main className="flex-1 overflow-y-auto p-6">{children}</main>
        </div>
      </div>
    </RequireAuth>
  );
}
