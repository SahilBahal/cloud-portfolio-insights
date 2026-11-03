import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { usePortfolioStore } from '../store/usePortfolioStore';
import { money, monthLabel, SERIES_COLORS } from '../format';
import type { GroupBy } from '../api/types';

const GROUP_OPTIONS: Array<{ value: GroupBy; label: string }> = [
  { value: 'service', label: 'Service' },
  { value: 'category', label: 'Category' },
  { value: 'industry', label: 'Industry' },
  { value: 'region', label: 'Region' },
];

export function ConsumptionChart() {
  const consumption = usePortfolioStore((s) => s.consumption);
  const groupBy = usePortfolioStore((s) => s.groupBy);
  const setGroupBy = usePortfolioStore((s) => s.setGroupBy);

  return (
    <section className="card">
      <header className="card-head">
        <div>
          <h2>Client consumption</h2>
          <p className="sub">Monthly revenue from usage, stacked by {groupBy}</p>
        </div>
        <div className="segmented" role="group" aria-label="Group by">
          {GROUP_OPTIONS.map((o) => (
            <button
              key={o.value}
              className={o.value === groupBy ? 'active' : ''}
              onClick={() => setGroupBy(o.value)}
            >
              {o.label}
            </button>
          ))}
        </div>
      </header>

      {consumption && (
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={consumption.series} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" tickFormatter={monthLabel} tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={money} tick={{ fontSize: 12 }} width={64} />
            <Tooltip
              formatter={(v: number) => money(v)}
              labelFormatter={(m: string) => monthLabel(m)}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {consumption.groups.map((g, i) => (
              <Area
                key={g}
                type="monotone"
                dataKey={g}
                stackId="1"
                stroke={SERIES_COLORS[i % SERIES_COLORS.length]}
                fill={SERIES_COLORS[i % SERIES_COLORS.length]}
                fillOpacity={0.55}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}
