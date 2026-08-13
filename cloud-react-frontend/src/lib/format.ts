/**
 * Postgres NUMERIC columns can reach the client as either a JSON number or a
 * string depending on the serializer, so every money/quantity helper coerces
 * defensively rather than trusting the static type.
 */
export type Decimalish = number | string;

export const toNumber = (value: Decimalish | null | undefined): number => {
  if (value === null || value === undefined || value === '') return 0;
  const n = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(n) ? n : 0;
};

/** Money: always 2 decimals, grouped thousands. Pair with `tabular-nums`. */
export const formatMoney = (value: Decimalish | null | undefined): string =>
  toNumber(value).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

/** Warehouse quantities are NUMERIC(12,3). Trailing zeros are kept for alignment. */
export const formatQuantity = (value: Decimalish | null | undefined): string =>
  toNumber(value).toLocaleString(undefined, {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  });

export const formatDate = (value: string | null | undefined): string => {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
};

/** Groups a permission code such as `order.void` under its domain (`order`). */
export const permissionDomain = (code: string): string => code.split('.')[0] ?? 'general';

/** `order.read_shift` -> `Read shift` */
export const permissionLabel = (code: string): string => {
  const action = code.split('.').slice(1).join('.') || code;
  const spaced = action.replace(/_/g, ' ');
  return spaced.charAt(0).toUpperCase() + spaced.slice(1);
};
