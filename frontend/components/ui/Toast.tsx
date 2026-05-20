'use client';

import React from 'react';
import { useSimulationStore } from '@/lib/store';

export default function Toast() {
  const error = useSimulationStore((s) => s.error);
  const clearError = useSimulationStore((s) => s.clearError);

  if (!error) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm w-full">
      <div className="bg-red-600 text-white rounded-lg shadow-lg px-4 py-3 flex items-start gap-3">
        <svg
          className="h-5 w-5 shrink-0 mt-0.5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.07 16.5c-.77.833.192 2.5 1.732 2.5z"
          />
        </svg>
        <p className="text-sm flex-1 leading-snug">{error}</p>
        <button
          onClick={clearError}
          className="shrink-0 text-white/80 hover:text-white transition-colors"
          aria-label="Dismiss error"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
