"use client";

import {
  BarChart3,
  BookOpen,
  Bot,
  Crosshair,
  FlaskConical,
  LayoutDashboard,
  Settings,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ITEMS } from "@/lib/constants";
import { cn } from "@/lib/utils";

const ICONS: Record<string, LucideIcon> = {
  LayoutDashboard,
  Crosshair,
  BookOpen,
  BarChart3,
  FlaskConical,
  Bot,
  Settings,
};

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-panel">
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <span className="flex h-7 w-7 items-center justify-center rounded bg-accent/15 text-accent">
          <Crosshair size={16} />
        </span>
        <span className="text-sm font-semibold tracking-tight text-text">Trader Copilot AI</span>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {NAV_ITEMS.map((item) => {
          const Icon = ICONS[item.icon] ?? LayoutDashboard;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-accent/15 font-medium text-text"
                  : "text-text-muted hover:bg-panel-raised hover:text-text",
              )}
            >
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-3 text-xs text-text-muted">
        Risk desk · MVP
      </div>
    </aside>
  );
}
