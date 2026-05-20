'use client';

import React, { useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import StepSidebar from '@/components/layout/StepSidebar';
import Badge from '@/components/ui/Badge';
import Toast from '@/components/ui/Toast';

export default function SimulationLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const id = params?.id as string;

  const simulation = useSimulationStore((s) => s.simulation);
  const setSimulation = useSimulationStore((s) => s.setSimulation);
  const setError = useSimulationStore((s) => s.setError);

  useEffect(() => {
    if (!id) return;
    // Only load if we don't have the simulation or it's a different one
    if (simulation?.id === id) return;

    api
      .getSimulation(id)
      .then((sim) => setSimulation(sim))
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : 'Failed to load simulation';
        setError(msg);
      });
  }, [id, simulation?.id, setSimulation, setError]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top nav */}
      <header className="bg-abs-blue-dark text-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/simulation" className="flex items-center gap-2 font-bold text-lg tracking-tight hover:opacity-90 transition-opacity">
            <span>🛒</span>
            <span>Simulation Lab</span>
          </Link>
          {simulation && (
            <div className="flex items-center gap-3 text-sm">
              <span className="text-white/70 truncate max-w-xs">{simulation.title}</span>
              <Badge status={simulation.status} />
            </div>
          )}
        </div>
      </header>

      <div className="flex flex-1 max-w-7xl mx-auto w-full px-6 py-6 gap-6">
        {/* Sidebar */}
        <aside className="w-56 flex-shrink-0">
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden sticky top-20">
            {id && <StepSidebar simulationId={id} />}
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>

      <Toast />
    </div>
  );
}
