/**
 * Always-on risk bar (UX Principle 4: "No screen should hide these metrics").
 * Rendered in the protected app shell so Risk %, Risk Amount, Drawdown,
 * Exposure and Rule Status are visible on every screen. Values are placeholders
 * until M1 (settings) and M3/M4 (risk + rules) wire them.
 */
const ITEMS: { label: string; value: string }[] = [
  { label: "Risk %", value: "—" },
  { label: "Risk Amount", value: "—" },
  { label: "Drawdown", value: "—" },
  { label: "Exposure", value: "—" },
  { label: "Rule Status", value: "—" },
];

export function RiskStrip() {
  return (
    <div className="flex items-center gap-6 border-b border-border bg-panel-raised px-5 py-2">
      <span className="text-xs font-semibold uppercase tracking-wide text-text-muted">
        Risk
      </span>
      {ITEMS.map((item) => (
        <div key={item.label} className="flex items-baseline gap-2">
          <span className="text-xs text-text-muted">{item.label}</span>
          <span className="numeric text-sm font-medium text-text">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
