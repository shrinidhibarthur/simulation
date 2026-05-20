'use client';

import React, { useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';

interface FeatureFlag {
  name: string;
  weekly_rollout: number[];
  [key: string]: unknown;
}

interface PromoPlan {
  [key: string]: unknown;
}

interface InventoryGuardrails {
  [key: string]: unknown;
}

interface AutoRollback {
  trigger_metric?: string;
  threshold?: number;
  action?: string;
  [key: string]: unknown;
}

interface RolloutPlan {
  feature_flags?: FeatureFlag[];
  promo_plan?: PromoPlan;
  inventory_guardrails?: InventoryGuardrails;
  auto_rollback?: AutoRollback;
  [key: string]: unknown;
}

function FeatureFlagTable({ flags }: { flags: FeatureFlag[] }) {
  const weeks = Math.max(...flags.map((f) => f.weekly_rollout?.length ?? 0), 0);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Flag</th>
            {Array.from({ length: weeks }, (_, i) => (
              <th key={i} className="text-center py-2 px-2 text-xs font-semibold text-gray-500 uppercase">
                Wk {i + 1}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {flags.map((flag, fi) => (
            <tr key={fi} className="border-b border-gray-100">
              <td className="py-2 px-3 font-mono text-xs text-abs-blue-dark">{flag.name}</td>
              {flag.weekly_rollout?.map((pct: number, wi: number) => (
                <td key={wi} className="py-2 px-2 text-center">
                  <div className="flex flex-col items-center gap-0.5">
                    <span className="text-xs font-medium text-gray-700">{pct}%</span>
                    <div className="w-10 bg-gray-200 rounded-full h-1">
                      <div
                        className="bg-abs-blue-light h-1 rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PromoPlanCard({ plan }: { plan: PromoPlan }) {
  return (
    <Card>
      <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <span>🎯</span> Promotion Plan
      </h3>
      <dl className="grid grid-cols-2 gap-3">
        {Object.entries(plan).map(([k, v]) => (
          <div key={k}>
            <dt className="text-xs text-gray-500 capitalize">{k.replace(/_/g, ' ')}</dt>
            <dd className="text-sm font-medium text-gray-800">
              {typeof v === 'number'
                ? v.toLocaleString()
                : Array.isArray(v)
                ? (v as unknown[]).join(', ')
                : String(v)}
            </dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}

function InventoryGuardrailsCard({ guardrails }: { guardrails: InventoryGuardrails }) {
  return (
    <Card>
      <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <span>📦</span> Inventory Guardrails
      </h3>
      <dl className="grid grid-cols-2 gap-3">
        {Object.entries(guardrails).map(([k, v]) => (
          <div key={k}>
            <dt className="text-xs text-gray-500 capitalize">{k.replace(/_/g, ' ')}</dt>
            <dd className="text-sm font-medium text-gray-800">
              {typeof v === 'number'
                ? v.toLocaleString()
                : Array.isArray(v)
                ? (v as unknown[]).join(', ')
                : String(v)}
            </dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}

function AutoRollbackCard({ rollback }: { rollback: AutoRollback }) {
  return (
    <Card className="border-abs-red bg-red-50">
      <h3 className="font-semibold text-abs-red mb-3 flex items-center gap-2">
        <span>⚠️</span> Auto-Rollback Configuration
      </h3>
      <dl className="space-y-2">
        {rollback.trigger_metric && (
          <div>
            <dt className="text-xs text-gray-500">Trigger Metric</dt>
            <dd className="text-sm font-medium text-gray-800">{rollback.trigger_metric}</dd>
          </div>
        )}
        {rollback.threshold !== undefined && (
          <div>
            <dt className="text-xs text-gray-500">Threshold</dt>
            <dd className="text-sm font-medium text-gray-800">
              {typeof rollback.threshold === 'number'
                ? rollback.threshold.toLocaleString()
                : String(rollback.threshold)}
            </dd>
          </div>
        )}
        {rollback.action && (
          <div>
            <dt className="text-xs text-gray-500">Action</dt>
            <dd className="text-sm font-semibold text-abs-red">{rollback.action}</dd>
          </div>
        )}
        {Object.entries(rollback)
          .filter(([k]) => !['trigger_metric', 'threshold', 'action'].includes(k))
          .map(([k, v]) => (
            <div key={k}>
              <dt className="text-xs text-gray-500 capitalize">{k.replace(/_/g, ' ')}</dt>
              <dd className="text-sm font-medium text-gray-800">{String(v)}</dd>
            </div>
          ))}
      </dl>
    </Card>
  );
}

export default function Step8Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const simulation = useSimulationStore((s) => s.simulation);
  const setSimulation = useSimulationStore((s) => s.setSimulation);
  const setError = useSimulationStore((s) => s.setError);

  const [generating, setGenerating] = useState(false);
  const [rolloutPlan, setRolloutPlan] = useState<RolloutPlan | null>(
    (simulation?.rollout_plan as RolloutPlan) ?? null
  );

  const handleGenerate = useCallback(async () => {
    if (!id) return;
    setGenerating(true);
    try {
      const updated = await api.generateRollout(id);
      setSimulation(updated);
      setRolloutPlan((updated.rollout_plan as RolloutPlan) ?? null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to generate rollout plan';
      setError(msg);
    } finally {
      setGenerating(false);
    }
  }, [id, setSimulation, setError]);

  const hasFlags = rolloutPlan?.feature_flags && rolloutPlan.feature_flags.length > 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 8 — Rollout Plan</h1>
        <p className="text-gray-500 text-sm mt-1">
          Generate the deployment and rollout strategy for the winning scenario.
        </p>
      </div>

      {!rolloutPlan && (
        <Card>
          <div className="text-center py-8">
            <p className="text-gray-500 mb-6">
              Generate a structured rollout plan including feature flags, promotion schedule,
              inventory guardrails, and auto-rollback configuration.
            </p>
            <Button onClick={handleGenerate} loading={generating} size="lg">
              {generating ? 'Generating Rollout Plan…' : 'Generate Rollout Plan'}
            </Button>
          </div>
        </Card>
      )}

      {generating && !rolloutPlan && (
        <div className="space-y-4">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      )}

      {rolloutPlan && (
        <>
          {/* Feature Flags */}
          {hasFlags && (
            <Card>
              <h2 className="text-base font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <span>🚩</span> Feature Flag Rollout Schedule
              </h2>
              <FeatureFlagTable flags={rolloutPlan.feature_flags!} />
            </Card>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {rolloutPlan.promo_plan &&
              Object.keys(rolloutPlan.promo_plan).length > 0 && (
                <PromoPlanCard plan={rolloutPlan.promo_plan} />
              )}
            {rolloutPlan.inventory_guardrails &&
              Object.keys(rolloutPlan.inventory_guardrails).length > 0 && (
                <InventoryGuardrailsCard guardrails={rolloutPlan.inventory_guardrails} />
              )}
          </div>

          {rolloutPlan.auto_rollback &&
            Object.keys(rolloutPlan.auto_rollback).length > 0 && (
              <AutoRollbackCard rollback={rolloutPlan.auto_rollback} />
            )}

          <div className="flex justify-between items-center">
            <Button
              variant="secondary"
              onClick={handleGenerate}
              loading={generating}
              size="sm"
            >
              Regenerate Plan
            </Button>
            <Button onClick={() => router.push(`/simulation/${id}/step/9`)}>
              View Audit Ledger →
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
