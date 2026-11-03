import { create } from 'zustand';
import { api, errorMessage } from '../api/client';
import type {
  Consumption,
  Forecast,
  GroupBy,
  PricingRow,
  Service,
  SigningsPoint,
  Summary,
  TopClient,
} from '../api/types';

// All dashboard state lives here. Components read what they need and call
// the setters; the store handles refetching when a filter changes.

interface PortfolioState {
  months: number;
  groupBy: GroupBy;
  forecastServiceId: number | null;
  horizon: number;

  services: Service[];
  summary: Summary | null;
  consumption: Consumption | null;
  pricing: PricingRow[];
  topClients: TopClient[];
  signings: SigningsPoint[];
  forecast: Forecast | null;

  loading: boolean;
  error: string | null;

  setMonths: (months: number) => void;
  setGroupBy: (groupBy: GroupBy) => void;
  setForecastService: (id: number | null) => void;
  setHorizon: (horizon: number) => void;
  loadAll: () => Promise<void>;
  loadForecast: () => Promise<void>;
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
  months: 12,
  groupBy: 'service',
  forecastServiceId: null,
  horizon: 3,

  services: [],
  summary: null,
  consumption: null,
  pricing: [],
  topClients: [],
  signings: [],
  forecast: null,

  loading: false,
  error: null,

  setMonths: (months) => {
    set({ months });
    void get().loadAll();
  },

  setGroupBy: async (groupBy) => {
    set({ groupBy });
    try {
      set({ consumption: await api.consumption(groupBy, get().months), error: null });
    } catch (err) {
      set({ error: errorMessage(err) });
    }
  },

  setForecastService: (forecastServiceId) => {
    set({ forecastServiceId });
    void get().loadForecast();
  },

  setHorizon: (horizon) => {
    set({ horizon });
    void get().loadForecast();
  },

  loadAll: async () => {
    const { months, groupBy } = get();
    set({ loading: true, error: null });
    try {
      // These requests don't depend on each other, so send them together
      const [services, summary, consumption, pricing, topClients, signings] = await Promise.all([
        api.services(),
        api.summary(months),
        api.consumption(groupBy, months),
        api.pricing(),
        api.topClients(months),
        api.signings(months),
      ]);
      set({ services, summary, consumption, pricing, topClients, signings });
      await get().loadForecast();
    } catch (err) {
      set({ error: errorMessage(err) });
    } finally {
      set({ loading: false });
    }
  },

  loadForecast: async () => {
    const { forecastServiceId, horizon } = get();
    try {
      set({ forecast: await api.forecast(forecastServiceId, horizon) });
    } catch (err) {
      set({ error: errorMessage(err) });
    }
  },
}));
