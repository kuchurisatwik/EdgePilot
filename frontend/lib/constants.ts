/** Canonical copy. Keep the two "insufficient data" strings distinct (per spec). */
export const COPY = {
  /** AI recommendation surfaces (SOC §10). */
  AI_INSUFFICIENT_DATA:
    "Not enough historical data available for a reliable recommendation.",
  /** Empty-data UI states (Design "Empty State"). */
  UI_INSUFFICIENT_DATA:
    "Not enough historical data available. Continue collecting trades to unlock insights.",
} as const;

export type NavItem = {
  label: string;
  href: string;
  /** lucide-react icon name */
  icon: string;
};

/** Left sidebar navigation (UX "Global Navigation"). */
export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: "LayoutDashboard" },
  { label: "Trade Planner", href: "/trade-planner", icon: "Crosshair" },
  { label: "Journal", href: "/journal", icon: "BookOpen" },
  { label: "Analytics", href: "/analytics", icon: "BarChart3" },
  { label: "Strategy Insights", href: "/strategy-insights", icon: "FlaskConical" },
  { label: "AI Coach", href: "/ai-coach", icon: "Bot" },
  { label: "Settings", href: "/settings", icon: "Settings" },
];

export type ConfidenceLevel = "high" | "medium" | "low" | "insufficient";
export type RuleStatus = "PASS" | "WARNING" | "BLOCK";
