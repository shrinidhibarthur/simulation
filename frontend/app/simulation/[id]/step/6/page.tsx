'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import type { Scenario } from '@/lib/types';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import ProgressBar from '@/components/ui/ProgressBar';

const SCENARIO_COLORS: Record<Scenario['name'], string> = {
  Base: 'border-abs-blue-dark text-abs-blue-dark',
  Optimistic: 'border-green-600 text-green-700',
  Pessimistic: 'border-abs-red text-abs-red',
};

export default function Step6Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const scenarios = useSimulationStore((s) => s.scenarios);
  const setSimulation = useSimulationStore((s) => s.setSimulation);
  const setError = useSimulationStore((s) => s.setError);

  const [selectedIds, setSelectedIds] = useState<Set<string>>(
    new Set(scenarios.map((s) => s.id))
  );
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentScenario, setCurrentScenario] = useState<string | null>(null);
  const [eta, setEta] = useState<number | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Update selected when scenarios load
  useEffect(() => {
    if (scenarios.length > 0) {
      setSelectedIds(new Set(scenarios.map((s) => s.id)));
    }
  }, [scenarios]);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const startPolling = useCallback(() => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      try {
        const status = await api.getStatus(id);
        setProgress(status.progress ?? 0);
        setCurrentScenario(status.current_scenario ?? null);
        setEta(status.eta_seconds ?? null);

        if (status.status === 'results_ready' || status.status === 'complete') {
          stopPolling();
          setRunning(false);
          const updated = await api.getSimulation(id);
          setSimulation(updated);
          router.push(`/simulation/${id}/step/7`);
        } else if (status.status === 'failed') {
          stopPolling();
          setRunning(false);
          setError('Simulation run failed. Please try again.');
        }
      } catch (err: unknown) {
        // Don't stop polling on transient errors
        console.error('Status poll error:', err);
      }
    }, 2000);
  }, [id, router, setSimulation, setError, stopPolling]);

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  const handleRun = async () => {
    if (!id || selectedIds.size === 0) return;
    setRunning(true);
    setProgress(0);
    setCurrentScenario(null);
    try {
      await api.runSimulation(id, Array.from(selectedIds), 10000);
      startPolling();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start simulation';
      setError(msg);
      setRunning(false);
    }
  };

  const toggleScenario = (sid: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(sid)) next.delete(sid);
      else next.add(sid);
      return next;
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 6 — Run Simulation</h1>
        <p className="text-gray-500 text-sm mt-1">
          Select scenarios and run 10,000 Monte Carlo iterations.
        </p>
      </div>

      {/* Scenario selection */}
      <Card>
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Select Scenarios to Run</h2>
        {scenarios.length === 0 ? (
          <p className="text-gray-400 text-sm">No scenarios found. Please complete Step 3 first.</p>
        ) : (
          <div className="space-y-2">
            {scenarios.map((sc) => {
              const checked = selectedIds.has(sc.id);
              const colorClass = SCENARIO_COLORS[sc.name];
              return (
                <label
                  key={sc.id}
                  className={[
                    'flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-colors',
                    checked ? colorClass + ' bg-opacity-5' : 'border-gray-200 text-gray-500',
                    running ? 'pointer-events-none opacity-60' : '',
                  ].join(' ')}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleScenario(sc.id)}
                    disabled={running}
                    className="w-4 h-4 accent-abs-blue-dark"
                  />
                  <div>
                    <span className="font-semibold">{sc.name}</span>
                    {sc.notes && (
                      <span className="text-xs text-gray-500 ml-2">— {sc.notes}</span>
                    )}
                  </div>
                </label>
              );
            })}
          </div>
        )}
      </Card>

      {/* Run button */}
      {!running && (
        <div className="flex justify-end">
          <Button
            onClick={handleRun}
            disabled={selectedIds.size === 0}
            size="lg"
          >
            Run Simulation (10,000 iterations)
          </Button>
        </div>
      )}

      {/* Progress */}
      {running && (
        <Card className="border-abs-blue-light bg-blue-50">
          <h2 className="text-sm font-semibold text-abs-blue-dark mb-4 flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-abs-blue-light animate-pulse" />
            Simulation Running…
          </h2>

          <ProgressBar
            value={progress}
            label={currentScenario ? `Running: ${currentScenario}` : 'Initializing…'}
          />

          {eta !== null && (
            <p className="text-xs text-gray-500 mt-2">
              Estimated time remaining: {eta < 60 ? `${eta}s` : `${Math.round(eta / 60)}m`}
            </p>
          )}

          <div className="mt-4 space-y-1">
            {scenarios
              .filter((s) => selectedIds.has(s.id))
              .map((s) => (
                <div key={s.id} className="flex items-center gap-2 text-xs text-gray-600">
                  <span
                    className={
                      currentScenario === s.name
                        ? 'w-2 h-2 rounded-full bg-abs-blue-light animate-ping'
                        : 'w-2 h-2 rounded-full bg-gray-300'
                    }
                  />
                  {s.name}
                </div>
              ))}
          </div>
        </Card>
      )}
    </div>
  );
}
