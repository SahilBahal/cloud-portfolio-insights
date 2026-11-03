import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { usePortfolioStore } from '../store/usePortfolioStore';
import { money, monthLabel } from '../format';

export function SigningsChart() {
  const data = usePortfolioStore((s) => s.signings);

  return (
    <section className="card">
      <header className="card-head">
        <div>
          <h2>Signings vs. revenue</h2>
          <p className="sub">New contract value signed each month against usage revenue</p>
        </div>
      </header>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="month" tickFormatter={monthLabel} tick={{ fontSize: 12 }} />
          <YAxis yAxisId="left" tickFormatter={money} tick={{ fontSize: 12 }} width={64} />
          <YAxis yAxisId="right" orientation="right" tickFormatter={money} tick={{ fontSize: 12 }} width={64} />
          <Tooltip formatter={(v: number) => money(v)} labelFormatter={(m: string) => monthLabel(m)} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar yAxisId="left" dataKey="signings" name="Signings" fill="#93a8e6" radius={[3, 3, 0, 0]} />
          <Line yAxisId="right" dataKey="revenue" name="Revenue" stroke="#d9822b" strokeWidth={2} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </section>
  );
}
