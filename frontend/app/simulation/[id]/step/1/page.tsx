'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import { useSimulationStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';

export default function Step1Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();
  const simulation = useSimulationStore((s) => s.simulation);

  if (!simulation) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 1 — Request</h1>
        <p className="text-gray-500 text-sm mt-1">Original simulation request submitted.</p>
      </div>

      <Card>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Request Text</h2>
        <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{simulation.request_text}</p>
      </Card>

      {(simulation.mvt || simulation.budget || simulation.sla_limit) && (
        <Card>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Parameters</h2>
          <dl className="grid grid-cols-3 gap-4">
            {simulation.mvt && (
              <div>
                <dt className="text-xs text-gray-500">MVT Name</dt>
                <dd className="font-medium text-gray-900">{simulation.mvt}</dd>
              </div>
            )}
            {simulation.budget !== undefined && simulation.budget !== null && (
              <div>
                <dt className="text-xs text-gray-500">Budget</dt>
                <dd className="font-medium text-gray-900">${simulation.budget.toLocaleString()}</dd>
              </div>
            )}
            {simulation.sla_limit !== undefined && simulation.sla_limit !== null && (
              <div>
                <dt className="text-xs text-gray-500">SLA Limit</dt>
                <dd className="font-medium text-gray-900">{(simulation.sla_limit * 100).toFixed(1)}%</dd>
              </div>
            )}
          </dl>
        </Card>
      )}

      <div className="flex justify-end">
        <Button onClick={() => router.push(`/simulation/${id}/step/2`)}>
          Continue to Clarify →
        </Button>
      </div>
    </div>
  );
}
