'use client';

import { create } from 'zustand';
import type { Simulation, Scenario, Result } from './types';

interface SimulationStore {
  simulation: Simulation | null;
  scenarios: Scenario[];
  results: Result[];
  currentStep: number;
  isLoading: boolean;
  error: string | null;
  setSimulation: (s: Simulation) => void;
  setScenarios: (s: Scenario[]) => void;
  setResults: (r: Result[]) => void;
  setLoading: (v: boolean) => void;
  setError: (e: string | null) => void;
  clearError: () => void;
}

export const useSimulationStore = create<SimulationStore>((set) => ({
  simulation: null,
  scenarios: [],
  results: [],
  currentStep: 1,
  isLoading: false,
  error: null,

  setSimulation: (s) => set({ simulation: s, currentStep: s.step }),
  setScenarios: (s) => set({ scenarios: s }),
  setResults: (r) => set({ results: r }),
  setLoading: (v) => set({ isLoading: v }),
  setError: (e) => set({ error: e }),
  clearError: () => set({ error: null }),
}));
