import { usePortfolioStore } from '../store/usePortfolioStore';
import { pct, unitPrice } from '../format';

export function PricingTable() {
  const pricing = usePortfolioStore((s) => s.pricing);

  // Show the biggest gaps first, since those are the ones worth a pricing review
  const rows = [...pricing].sort(
    (a, b) => Math.abs(b.gap_vs_avg_pct ?? 0) - Math.abs(a.gap_vs_avg_pct ?? 0),
  );

  return (
    <section className="card">
      <header className="card-head">
        <div>
          <h2>Competitive pricing</h2>
          <p className="sub">Our list price vs. the average of three competitors</p>
        </div>
      </header>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Service</th>
              <th>Unit</th>
              <th className="num">Our price</th>
              <th className="num">Market avg</th>
              <th className="num">Gap</th>
              <th>Position</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.service_id}>
                <td>{r.service}</td>
                <td className="muted">{r.unit}</td>
                <td className="num">{unitPrice(r.our_price)}</td>
                <td className="num">{unitPrice(r.competitor_avg)}</td>
                <td className="num">{pct(r.gap_vs_avg_pct)}</td>
                <td>
                  <span className={`tag ${r.position.replace(' ', '-')}`}>{r.position}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
