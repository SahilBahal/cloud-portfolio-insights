import { useEffect } from 'react';
import { usePortfolioStore } from './store/usePortfolioStore';
import { KpiCards } from './components/KpiCards';
import { ConsumptionChart } from './components/ConsumptionChart';
import { PricingTable } from './components/PricingTable';
import { TopClients } from './components/TopClients';
import { SigningsChart } from './components/SigningsChart';
import { ForecastPanel } from './components/ForecastPanel';

const PERIODS = [6, 12, 18];

export default function App() {
  const loadAll = usePortfolioStore((s) => s.loadAll);
  const months = usePortfolioStore((s) => s.months);
  const setMonths = usePortfolioStore((s) => s.setMonths);
  const loading = usePortfolioStore((s) => s.loading);
  const error = usePortfolioStore((s) => s.error);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  return (
    <div className="page">
      <header className="top">
        <div>
          <h1>Cloud Portfolio Insights</h1>
          <p className="sub">Consumption, pricing, and signings across a cloud services portfolio (synthetic data)</p>
        </div>
        <div className="segmented" role="group" aria-label="Period">
          {PERIODS.map((p) => (
            <button key={p} className={p === months ? 'active' : ''} onClick={() => setMonths(p)}>
              Last {p} mo
            </button>
          ))}
        </div>
      </header>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Loading…</div>}

      <KpiCards />
      <ConsumptionChart />
      <div className="grid-2">
        <PricingTable />
        <TopClients />
      </div>
      <div className="grid-2">
        <SigningsChart />
        <ForecastPanel />
      </div>
    </div>
  );
}
