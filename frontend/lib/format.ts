export function toNumber(value: string | number | null | undefined): number {
  const n = typeof value === "string" ? Number.parseFloat(value) : (value ?? 0);
  return Number.isFinite(n) ? n : 0;
}

export function formatMoney(value: string | number | null | undefined, currency = "USDT"): string {
  const n = toNumber(value);
  return `${n.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} ${currency}`;
}

export function formatPct(value: string | number | null | undefined): string {
  return `${toNumber(value).toFixed(2)}%`;
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? "—"
    : d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

/** Tailwind text-color class for a signed value (profit/loss). */
export function signedColor(value: string | number | null | undefined): string {
  const n = toNumber(value);
  if (value === null || value === undefined || value === "") return "text-text";
  return n > 0 ? "text-success" : n < 0 ? "text-danger" : "text-neutral";
}
