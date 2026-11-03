import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { usePortfolioStore } from '../store/usePortfolioStore';
import { money, monthLabel } from '../format';

export function ForecastPanel() {
  const forecast = usePortfolioStore((s) => s.forecast);
  const services = usePortfolioStore((s) => s.services);
  const serviceId = usePortfolioStore((s) => s.forecastServiceId);
  const horizon = usePortfolioStore((s) => s.horizon);
  const setService = usePortfolioStore((s) => s.setForecastService);
  const setHorizon = usePortfolioStore((s) => s.setHorizon);

  // Merge history and projection into one series. The last actual point is
  // repeated as a forecast point so the two lines connect.
  const data = forecast
    ? [
        ...forecast.history.map((h, i) => ({
          month: h.month,
          actual: h.actual,
          trend: h.fitted,
          forecast: i === forecast.history.length - 1 ? h.actual : undefined,
        })),
        ...forecast.forecast.map((f) => ({ month: f.month, forecast: f.forecast })),
      ]
    : [];

  return (
    <section className="card">
      <header className="card-head">
        <div>
          <h2>Revenue forecast</h2>
          <p className="sub">
            Linear trend baseline
            {forecast && <> · trending {money(forecast.monthly_trend)} per month</>}
          </p>
        </div>
        <div className="controls">
          <label>
            Service
            <select
              value={serviceId ?? ''}
              onChange={(e) => setService(e.target.value === '' ? null : Number(e.target.value))}
            >
              <option value="">All services</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Months ahead
            <select value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}>
              {[3, 6, 12].map((h) => (
                <option key={h} value={h}>
                  {h}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="month" tickFormatter={monthLabel} tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={money} tick={{ fontSize: 12 }} width={64} />
          <Tooltip formatter={(v: number) => money(v)} labelFormatter={(m: string) => monthLabel(m)} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line dataKey="actual" name="Actual" stroke="#2f5fd0" strokeWidth={2} dot={false} />
          <Line dataKey="trend" name="Fitted trend" stroke="#94a3b8" strokeDasharray="4 4" dot={false} />
          <Line dataKey="forecast" name="Forecast" stroke="#d9822b" strokeWidth={2} strokeDasharray="6 3" dot />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}
