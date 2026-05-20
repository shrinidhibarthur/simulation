export interface Simulation {
  id: string;
  title: string;
  status: string;
  step: number;
  request_text: string;
  use_case_brief?: Record<string, unknown>;
  mvt?: string;
  budget?: number;
  sla_limit?: number;
  seed?: number;
  csv_profile?: Record<string, unknown>;
  data_lock?: Record<string, unknown>;
  rollout_plan?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Scenario {
  id: string;
  simulation_id: string;
  name: 'Base' | 'Optimistic' | 'Pessimistic';
  storefront: Record<string, unknown>;
  marketing: Record<string, unknown>;
  ops: Record<string, unknown>;
  notes?: string;
  distribution_params?: Record<string, unknown>;
  created_at: string;
}

export interface Result {
  id: string;
  simulation_id: string;
  scenario_id: string;
  conversion_lift: number;
  aov_delta: number;
  rpv_lift: number;
  margin_impact: number;
  stockout_change: number;
  markdown_change: number;
  cost_to_serve_delta: number;
  sla_risk: number;
  confidence: number;
  composite_score: number;
  kde_x_values: number[];
  kde_y_values: number[];
  win_probability?: number;
  demand_momentum?: number;
  visibility_budget?: number;
  raw_summary?: Record<string, unknown>;
}

export interface LedgerEvent {
  id: string;
  simulation_id: string;
  step: number;
  event_type: string;
  actor: string;
  payload?: Record<string, unknown>;
  created_at: string;
}

export interface SimulationStatus {
  step: number;
  status: string;
  task_id?: string;
  progress?: number;
  current_scenario?: string;
  eta_seconds?: number;
}

export interface ClarifyResponse {
  questions: string[];
  use_case_brief?: Record<string, unknown> | null;
  complete: boolean;
}

export interface DataSource {
  name: string;
  latency_minutes: number;
  ok?: boolean;
  threshold?: number;
  status?: string;
  notes?: string;
}
