import axios, { AxiosError } from 'axios';
import type {
  Consumption,
  Forecast,
  GroupBy,
  PricingRow,
  Service,
  SigningsPoint,
  Summary,
  TopClient,
} from './types';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  timeout: 10_000,
});

// Turn Flask's { error: "..." } responses into readable messages
export function errorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    const apiError = (err.response?.data as { error?: string } | undefined)?.error;
    if (apiError) return apiError;
    // With the Vite proxy, a stopped Flask server shows up as a 5xx with no body
    if (err.code === 'ERR_NETWORK' || (err.response?.status ?? 0) >= 500) {
      return 'Cannot reach the API. Is the Flask server running on port 5000?';
    }
    return err.message;
  }
  return 'Something went wrong';
}

export const api = {
  services: () => http.get<Service[]>('/services').then((r) => r.data),

  summary: (months: number) =>
    http.get<Summary>('/summary', { params: { months } }).then((r) => r.data),

  consumption: (groupBy: GroupBy, months: number) =>
    http
      .get<Consumption>('/consumption', { params: { group_by: groupBy, months } })
      .then((r) => r.data),

  pricing: () => http.get<PricingRow[]>('/pricing').then((r) => r.data),

  topClients: (months: number, limit = 8) =>
    http.get<TopClient[]>('/clients/top', { params: { months, limit } }).then((r) => r.data),

  signings: (months: number) =>
    http.get<SigningsPoint[]>('/signings', { params: { months } }).then((r) => r.data),

  forecast: (serviceId: number | null, horizon: number) =>
    http
      .get<Forecast>('/forecast', {
        params: { horizon, ...(serviceId !== null && { service_id: serviceId }) },
      })
      .then((r) => r.data),
};
