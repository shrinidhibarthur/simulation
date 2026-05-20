'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import type { Scenario } from '@/lib/types';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';

const SCENARIO_COLORS: Record<Scenario['name'], string> = {
  Base: 'text-abs-blue-dark border-abs-blue-dark bg-blue-50',
  Optimistic: 'text-green-700 border-green-600 bg-green-50',
  Pessimistic: 'text-abs-red border-abs-red bg-red-50',
};

const SCENARIO_HEADER_BG: Record<Scenario['name'], string> = {
  Base: 'bg-abs-blue-dark',
  Optimistic: 'bg-green-600',
  Pessimistic: 'bg-abs-red',
};

function ScenarioCard({ scenario }: { scenario: Scenario }) {
  const colorClass = SCENARIO_COLORS[scenario.name];
  const headerBg = SCENARIO_HEADER_BG[scenario.name];

  const summarize = (obj: Record<string, unknown>) => {
    return Object.entries(obj)
      .slice(0, 4)
      .map(([k, v]) => (
        <div key={k} className="flex justify-between text-xs py-0.5">
          <span className="text-gray-500 capitalize">{k.replace(/_/g, ' ')}</span>
          <span className="font-medium text-gray-800">
            {typeof v === 'number' ? v.toLocaleString() : String(v)}
          </span>
        </div>
      ));
  };

  return (
    <div className={`border rounded-lg overflow-hidden ${colorClass}`}>
      <div className={`${headerBg} text-white px-4 py-3`}>
        <h3 className="font-bold text-base">{scenario.name}</h3>
        {scenario.notes && (
          <p className="text-white/80 text-xs mt-0.5">{scenario.notes}</p>
        )}
      </div>
      <div className="p-4 space-y-3 bg-white">
        {Object.keys(scenario.storefront).length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Storefront</h4>
            {summarize(scenario.storefront)}
          </div>
        )}
        {Object.keys(scenario.marketing).length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Marketing</h4>
            {summarize(scenario.marketing)}
          </div>
        )}
        {Object.keys(scenario.ops).length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Operations</h4>
            {summarize(scenario.ops)}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Step3Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const scenarios = useSimulationStore((s) => s.scenarios);
  const setScenarios = useSimulationStore((s) => s.setScenarios);
  const setSimulation = useSimulationStore((s) => s.setSimulation);
  const setError = useSimulationStore((s) => s.setError);

  const [generating, setGenerating] = useState(false);
  const [loaded, setLoaded] = useState(scenarios.length > 0);

  // Try to load existing scenarios on mount
  useEffect(() => {
    if (scenarios.length > 0) {
      setLoaded(true);
    }
  }, [scenarios]);

  const handleGenerate = async () => {
    if (!id) return;
    setGenerating(true);
    try {
      const res = await api.generateScenarios(id);
      setScenarios(res.scenarios);
      const updated = await api.getSimulation(id);
      setSimulation(updated);
      setLoaded(true);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to generate scenarios';
      setError(msg);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 3 — Scenario Options</h1>
        <p className="text-gray-500 text-sm mt-1">
          Generate Base, Optimistic, and Pessimistic scenario configurations.
        </p>
      </div>

      {!loaded && (
        <Card>
          <div className="text-center py-8">
            <p className="text-gray-500 mb-6">
              Click below to have the AI generate three scenario variants based on your use case brief.
            </p>
            <Button onClick={handleGenerate} loading={generating} size="lg">
              {generating ? 'Generating Scenarios…' : 'Generate Scenarios'}
            </Button>
          </div>
        </Card>
      )}

      {generating && !loaded && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      )}

      {loaded && scenarios.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {scenarios.map((s) => (
              <ScenarioCard key={s.id} scenario={s} />
            ))}
          </div>

          <div className="flex justify-between items-center">
            <Button
              variant="secondary"
              onClick={handleGenerate}
              loading={generating}
              size="sm"
            >
              Regenerate
            </Button>
            <Button onClick={() => router.push(`/simulation/${id}/step/4`)}>
              Continue to Configuration →
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
