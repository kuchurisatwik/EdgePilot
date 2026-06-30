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
