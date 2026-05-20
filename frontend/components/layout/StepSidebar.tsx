'use client';

import React from 'react';
import Link from 'next/link';
import { useSimulationStore } from '@/lib/store';

const STEPS = [
  { n: 1, label: 'Request' },
  { n: 2, label: 'Clarify' },
  { n: 3, label: 'Scenarios' },
  { n: 4, label: 'Configure' },
  { n: 5, label: 'Data Lock' },
  { n: 6, label: 'Run' },
  { n: 7, label: 'Results' },
  { n: 8, label: 'Rollout' },
  { n: 9, label: 'Ledger' },
];

interface StepSidebarProps {
  simulationId: string;
}

export default function StepSidebar({ simulationId }: StepSidebarProps) {
  const simulation = useSimulationStore((s) => s.simulation);
  const simStep = simulation?.step ?? 1;

  return (
    <nav className="flex flex-col gap-1 py-4">
      {STEPS.map(({ n, label }) => {
        const isActive = n === simStep;
        const isComplete = n < simStep;
        const isLocked = n > simStep;

        if (isComplete) {
          return (
            <Link
              key={n}
              href={`/simulation/${simulationId}/step/${n}`}
              className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-green-700 hover:bg-green-50 transition-colors group"
            >
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold">
                ✓
              </span>
              <span>{label}</span>
            </Link>
          );
        }

        if (isActive) {
          return (
            <div
              key={n}
              className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-semibold bg-abs-blue-dark text-white"
            >
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-white text-abs-blue-dark flex items-center justify-center text-xs font-bold">
                {n}
              </span>
              <span>{label}</span>
            </div>
          );
        }

        // locked
        return (
          <div
            key={n}
            className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-gray-400 cursor-not-allowed"
          >
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 text-gray-400 flex items-center justify-center text-xs">
              🔒
            </span>
            <span>{label}</span>
          </div>
        );
      })}
    </nav>
  );
}
