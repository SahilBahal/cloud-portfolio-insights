import { usePortfolioStore } from '../store/usePortfolioStore';
import { money } from '../format';

export function TopClients() {
  const clients = usePortfolioStore((s) => s.topClients);
  const max = clients[0]?.revenue ?? 1;

  return (
    <section className="card">
      <header className="card-head">
        <div>
          <h2>Top clients</h2>
          <p className="sub">Ranked by consumption revenue in the period</p>
        </div>
      </header>
      <ol className="client-list">
        {clients.map((c) => (
          <li key={c.client_id}>
            <div className="client-row">
              <span className="client-name">{c.name}</span>
              <span className="num">{money(c.revenue)}</span>
            </div>
            <div className="bar">
              <span style={{ width: `${(c.revenue / max) * 100}%` }} />
            </div>
            <span className="muted small">
              {c.industry} · {c.region} · {c.services_used} services
            </span>
          </li>
        ))}
      </ol>
    </section>
  );
}
