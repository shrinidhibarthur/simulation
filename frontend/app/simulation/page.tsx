'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import * as api from '@/lib/api-client';
import type { Simulation } from '@/lib/types';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';
import Card from '@/components/ui/Card';

export default function SimulationListPage() {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listSimulations(1, 50)
      .then((data) => {
        setSimulations(data.items);
        setTotal(data.total);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to load simulations');
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-[calc(100vh-3.5rem)] bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-abs-blue-dark">Simulations</h1>
            {!loading && (
              <p className="text-gray-500 text-sm mt-1">
                {total} simulation{total !== 1 ? 's' : ''}
              </p>
            )}
          </div>
          <Link href="/intake">
            <Button size="lg">+ New Request</Button>
          </Link>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border-l-4 border-abs-red text-red-700 px-4 py-3 text-sm rounded mb-6">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-lg" />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && simulations.length === 0 && !error && (
          <Card className="text-center py-16">
            <p className="text-4xl mb-4">🧪</p>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">No simulations yet</h2>
            <p className="text-gray-400 mb-6 text-sm">
              Create your first Monte Carlo simulation to get started.
            </p>
            <Link href="/intake">
              <Button>+ New Request</Button>
            </Link>
          </Card>
        )}

        {/* Simulation list */}
        {!loading && simulations.length > 0 && (
          <div className="space-y-3">
            {simulations.map((sim) => (
              <Link
                key={sim.id}
                href={`/simulation/${sim.id}/step/${sim.step}`}
                className="block"
              >
                <Card className="hover:border-abs-blue-light transition-colors cursor-pointer hover:shadow-sm">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <h2 className="font-semibold text-gray-900 truncate">{sim.title}</h2>
                        <Badge status={sim.status} />
                      </div>
                      <p className="text-sm text-gray-500 truncate">{sim.request_text}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span>Step {sim.step} of 9</span>
                        {sim.mvt && <span>MVT: {sim.mvt}</span>}
                        <span>
                          Created {new Date(sim.created_at).toLocaleDateString(undefined, {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                          })}
                        </span>
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      {/* Step progress mini bar */}
                      <div className="flex items-center gap-1">
                        {Array.from({ length: 9 }).map((_, i) => (
                          <div
                            key={i}
                            className={[
                              'w-2 h-2 rounded-full',
                              i < sim.step ? 'bg-abs-blue-dark' : 'bg-gray-200',
                            ].join(' ')}
                          />
                        ))}
                      </div>
                      <p className="text-xs text-gray-400 text-right mt-1">
                        {sim.step}/9
                      </p>
                    </div>
                    <svg
                      className="h-4 w-4 text-gray-400 flex-shrink-0"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
