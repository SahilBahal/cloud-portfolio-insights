// Response shapes from the Flask API. Keeping these in one place means a
// change on the backend shows up as a type error here instead of a blank chart.

export type GroupBy = 'service' | 'category' | 'industry' | 'region';

export interface Summary {
  period_start: string;
  period_end: string;
  total_revenue: number;
  latest_month_revenue: number;
  mom_growth_pct: number | null;
  active_clients: number;
  total_signings: number;
  top_service: string | null;
}

export interface Consumption {
  group_by: GroupBy;
  groups: string[];
  series: Array<{ month: string } & Record<string, number | string>>;
}

export type PricePosition = 'premium' | 'discount' | 'at market' | 'unknown';

export interface PricingRow {
  service_id: number;
  service: string;
  category: string;
  unit: string;
  our_price: number;
  competitor_avg: number;
  competitor_min: number;
  gap_vs_avg_pct: number | null;
  position: PricePosition;
}

export interface TopClient {
  client_id: number;
  name: string;
  industry: string;
  region: string;
  revenue: number;
  services_used: number;
}

export interface SigningsPoint {
  month: string;
  revenue: number;
  signings: number;
}

export interface Forecast {
  service: string;
  monthly_trend: number;
  history: Array<{ month: string; actual: number; fitted: number }>;
  forecast: Array<{ month: string; forecast: number }>;
}

export interface Service {
  id: number;
  name: string;
  category: string;
  unit: string;
}
