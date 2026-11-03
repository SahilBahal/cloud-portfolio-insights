const compact = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  notation: 'compact',
  maximumFractionDigits: 1,
});

const precise = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 5,
});

export const money = (n: number) => compact.format(n);
export const unitPrice = (n: number) => precise.format(n);

export const pct = (n: number | null) =>
  n === null ? '–' : `${n > 0 ? '+' : ''}${n.toFixed(1)}%`;

// "2026-03" -> "Mar '26"
export const monthLabel = (m: string) => {
  const [y, mo] = m.split('-').map(Number);
  const name = new Date(y, mo - 1, 1).toLocaleString('en-US', { month: 'short' });
  return `${name} '${String(y).slice(2)}`;
};

// Fixed palette so the same group always gets the same color
export const SERIES_COLORS = [
  '#2f5fd0', '#d9822b', '#2a9d8f', '#c2410c', '#7c3aed',
  '#0f766e', '#be185d', '#4d7c0f',
];
