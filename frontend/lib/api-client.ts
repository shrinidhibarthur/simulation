import type {
  Simulation,
  Scenario,
  Result,
  LedgerEvent,
  SimulationStatus,
  ClarifyResponse,
  DataSource,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });

  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      message = body.detail ?? body.message ?? message;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(res.status, message);
  }

  return res.json() as Promise<T>;
}

// ---- Simulations ----

export function createSimulation(body: {
  request_text: string;
  mvt?: string | null;
  budget?: number | null;
  sla_limit?: number | null;
}): Promise<Simulation> {
  return request<Simulation>('/api/simulations', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function listSimulations(
  page = 1,
  perPage = 50
): Promise<{ items: Simulation[]; total: number }> {
  return request<{ items: Simulation[]; total: number }>(
    `/api/simulations?page=${page}&per_page=${perPage}`
  );
}

export function getSimulation(id: string): Promise<Simulation> {
  return request<Simulation>(`/api/simulations/${id}`);
}

// ---- Clarify ----

export function clarify(
  id: string,
  answers?: Record<string, string>
): Promise<ClarifyResponse> {
  return request<ClarifyResponse>(`/api/simulations/${id}/clarify`, {
    method: 'POST',
    body: JSON.stringify({ answers: answers ?? null }),
  });
}

// ---- Scenarios ----

export function generateScenarios(id: string): Promise<{ scenarios: Scenario[] }> {
  return request<{ scenarios: Scenario[] }>(`/api/simulations/${id}/scenarios`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

// ---- CSV Profile ----

export async function profileCsv(
  id: string,
  file: File
): Promise<Simulation> {
  const form = new FormData();
  form.append('file', file);
  const url = `${BASE_URL}/api/simulations/${id}/profile-csv`;
  const res = await fetch(url, { method: 'POST', body: form });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      message = body.detail ?? message;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, message);
  }
  return res.json() as Promise<Simulation>;
}

// ---- Lock ----

export function lockSimulation(
  id: string,
  dataSources: DataSource[]
): Promise<{ locked: boolean; data_lock: Record<string, unknown> }> {
  return request(`/api/simulations/${id}/lock`, {
    method: 'POST',
    body: JSON.stringify({ data_sources: dataSources }),
  });
}

// ---- Run ----

export function runSimulation(
  id: string,
  scenarioIds: string[],
  nIterations = 10000
): Promise<{ task_id: string; status: string }> {
  return request(`/api/simulations/${id}/run`, {
    method: 'POST',
    body: JSON.stringify({ scenario_ids: scenarioIds, n_iterations: nIterations }),
  });
}

// ---- Status ----

export function getStatus(id: string): Promise<SimulationStatus> {
  return request<SimulationStatus>(`/api/simulations/${id}/status`);
}

// ---- Results ----

export function getResults(
  id: string
): Promise<{ results: Result[]; ranked: Result[] }> {
  return request<{ results: Result[]; ranked: Result[] }>(
    `/api/simulations/${id}/results`
  );
}

// ---- Rollout ----

export function generateRollout(id: string): Promise<Simulation> {
  return request<Simulation>(`/api/simulations/${id}/rollout`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

// ---- Ledger ----

export function getLedger(
  id: string,
  page = 1,
  perPage = 50
): Promise<{ events: LedgerEvent[]; total: number }> {
  return request<{ events: LedgerEvent[]; total: number }>(
    `/api/simulations/${id}/ledger?page=${page}&per_page=${perPage}`
  );
}
