'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Papa from 'papaparse';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import type { LedgerEvent } from '@/lib/types';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';

const STEP_LABELS: Record<number, string> = {
  1: 'Request',
  2: 'Clarify',
  3: 'Scenarios',
  4: 'Configure',
  5: 'Data Lock',
  6: 'Run',
  7: 'Results',
  8: 'Rollout',
  9: 'Ledger',
};

function PayloadCell({ payload }: { payload?: Record<string, unknown> }) {
  const [open, setOpen] = useState(false);
  if (!payload || Object.keys(payload).length === 0) {
    return <span className="text-gray-400 text-xs">—</span>;
  }
  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className="text-xs text-abs-blue-light underline hover:no-underline"
      >
        {open ? 'Collapse' : 'Expand'}
      </button>
      {open && (
        <pre className="mt-1 text-xs bg-gray-100 rounded p-2 overflow-x-auto max-w-xs whitespace-pre-wrap break-words">
          {JSON.stringify(payload, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default function Step9Page() {
  const params = useParams();
  const id = params?.id as string;

  const setError = useSimulationStore((s) => s.setError);

  const [events, setEvents] = useState<LedgerEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [stepFilter, setStepFilter] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const PER_PAGE = 50;

  const loadLedger = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await api.getLedger(id, page, PER_PAGE);
      setEvents(data.events);
      setTotal(data.total);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load ledger';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [id, page, setError]);

  useEffect(() => {
    loadLedger();
  }, [loadLedger]);

  const filteredEvents = stepFilter !== null
    ? events.filter((e) => e.step === stepFilter)
    : events;

  const handleExportCsv = () => {
    const rows = filteredEvents.map((e) => ({
      timestamp: e.created_at,
      step: e.step,
      event_type: e.event_type,
      actor: e.actor,
      payload: e.payload ? JSON.stringify(e.payload) : '',
    }));
    const csv = Papa.unparse(rows);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `simulation-${id}-ledger.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const totalPages = Math.ceil(total / PER_PAGE);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-abs-blue-dark">Step 9 — Audit Ledger</h1>
          <p className="text-gray-500 text-sm mt-1">
            Immutable record of all simulation events and state transitions.
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={handleExportCsv}>
          Export CSV
        </Button>
      </div>

      {/* Step filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => { setStepFilter(null); setPage(1); }}
          className={[
            'px-3 py-1.5 rounded text-xs font-semibold transition-colors',
            stepFilter === null
              ? 'bg-abs-blue-dark text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
          ].join(' ')}
        >
          All
        </button>
        {Object.entries(STEP_LABELS).map(([n, label]) => (
          <button
            key={n}
            onClick={() => { setStepFilter(parseInt(n)); setPage(1); }}
            className={[
              'px-3 py-1.5 rounded text-xs font-semibold transition-colors',
              stepFilter === parseInt(n)
                ? 'bg-abs-blue-dark text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
            ].join(' ')}
          >
            {n}: {label}
          </button>
        ))}
      </div>

      {/* Table */}
      <Card className="p-0 overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">
            No events found{stepFilter !== null ? ` for Step ${stepFilter}` : ''}.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase whitespace-nowrap">
                    Timestamp
                  </th>
                  <th className="text-left py-3 px-3 text-xs font-semibold text-gray-500 uppercase">
                    Step
                  </th>
                  <th className="text-left py-3 px-3 text-xs font-semibold text-gray-500 uppercase whitespace-nowrap">
                    Event Type
                  </th>
                  <th className="text-left py-3 px-3 text-xs font-semibold text-gray-500 uppercase">
                    Actor
                  </th>
                  <th className="text-left py-3 px-3 text-xs font-semibold text-gray-500 uppercase">
                    Payload
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredEvents.map((event) => (
                  <tr
                    key={event.id}
                    className="border-b border-gray-100 hover:bg-gray-50 align-top"
                  >
                    <td className="py-3 px-4 font-mono text-xs text-gray-500 whitespace-nowrap">
                      {new Date(event.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-3">
                      <span className="inline-block bg-gray-100 text-gray-700 text-xs font-semibold px-2 py-0.5 rounded">
                        {event.step} — {STEP_LABELS[event.step] ?? '?'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-gray-800 font-medium whitespace-nowrap">
                      {event.event_type}
                    </td>
                    <td className="py-3 px-3 text-gray-600 whitespace-nowrap">
                      {event.actor}
                    </td>
                    <td className="py-3 px-3">
                      <PayloadCell payload={event.payload} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            Showing {(page - 1) * PER_PAGE + 1}–{Math.min(page * PER_PAGE, total)} of {total} events
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              ← Prev
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page === totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next →
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
