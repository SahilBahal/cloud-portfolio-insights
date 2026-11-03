import { usePortfolioStore } from '../store/usePortfolioStore';
import { money, monthLabel, pct } from '../format';

export function KpiCards() {
  const summary = usePortfolioStore((s) => s.summary);
  if (!summary) return null;

  const growth = summary.mom_growth_pct;

  const cards = [
    {
      label: 'Consumption revenue',
      value: money(summary.total_revenue),
      note: `${monthLabel(summary.period_start)} – ${monthLabel(summary.period_end)}`,
    },
    {
      label: 'Latest month',
      value: money(summary.latest_month_revenue),
      note: `${pct(growth)} vs. prior month`,
      tone: growth === null ? undefined : growth >= 0 ? 'up' : 'down',
    },
    {
      label: 'New signings',
      value: money(summary.total_signings),
      note: 'Total contract value',
    },
    {
      label: 'Active clients',
      value: String(summary.active_clients),
      note: `Top service: ${summary.top_service ?? '–'}`,
    },
  ];

  return (
    <section className="kpis">
      {cards.map((c) => (
        <div className="card kpi" key={c.label}>
          <span className="kpi-label">{c.label}</span>
          <span className="kpi-value">{c.value}</span>
          <span className={`kpi-note ${c.tone ?? ''}`}>{c.note}</span>
        </div>
      ))}
    </section>
  );
}
