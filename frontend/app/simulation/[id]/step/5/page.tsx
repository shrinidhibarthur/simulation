'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import type { DataSource } from '@/lib/types';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

const DATA_SOURCES_DEFAULTS: DataSource[] = [
  { name: 'Adobe/EDDL', latency_minutes: 5, status: 'fresh', ok: true, notes: '' },
  { name: 'OMS', latency_minutes: 2, status: 'fresh', ok: true, notes: '' },
  { name: 'Inventory', latency_minutes: 10, status: 'fresh', ok: true, notes: '' },
  { name: 'Pricing', latency_minutes: 3, status: 'fresh', ok: true, notes: '' },
  { name: 'CRM', latency_minutes: 15, status: 'fresh', ok: true, notes: '' },
  { name: 'WMS', latency_minutes: 8, status: 'fresh', ok: true, notes: '' },
  { name: 'Carriers', latency_minutes: 12, status: 'fresh', ok: true, notes: '' },
];

const STATUS_COLORS: Record<string, string> = {
  fresh: 'text-green-700',
  stale: 'text-yellow-700',
  warning: 'text-abs-red',
};

export default function Step5Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const simulation = useSimulationStore((s) => s.simulation);
  const setSimulation = useSimulationStore((s) => s.setSimulation);
  const setError = useSimulationStore((s) => s.setError);

  const [sources, setSources] = useState<DataSource[]>(DATA_SOURCES_DEFAULTS);
  const [locking, setLocking] = useState(false);
  const [locked, setLocked] = useState(simulation?.status === 'locked' || !!simulation?.data_lock);

  const updateSource = (index: number, field: keyof DataSource, value: string | number | boolean) => {
    setSources((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };

  const handleLock = async () => {
    if (!id) return;
    setLocking(true);
    try {
      await api.lockSimulation(id, sources);
      const updated = await api.getSimulation(id);
      setSimulation(updated);
      setLocked(true);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to lock data sources';
      setError(msg);
    } finally {
      setLocking(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 5 — Data Lock</h1>
        <p className="text-gray-500 text-sm mt-1">
          Verify and lock all data sources before running the simulation. This action is irreversible.
        </p>
      </div>

      {locked && (
        <div className="bg-yellow-50 border border-yellow-300 rounded-lg px-4 py-3 flex items-center gap-3">
          <span className="text-yellow-600 text-lg">🔒</span>
          <div>
            <p className="font-semibold text-yellow-800">Data Sources Locked</p>
            <p className="text-xs text-yellow-700">
              All sources have been committed. Proceed to run the simulation.
            </p>
          </div>
        </div>
      )}

      <Card className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Source</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Latency (min)</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Notes</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((src, i) => (
                <tr key={src.name} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-semibold text-gray-800">{src.name}</td>
                  <td className="py-3 px-4">
                    {locked ? (
                      <span className={`font-medium ${STATUS_COLORS[src.status ?? 'fresh']}`}>
                        {src.status}
                      </span>
                    ) : (
                      <select
                        value={src.status ?? 'fresh'}
                        onChange={(e) => updateSource(i, 'status', e.target.value)}
                        className="border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                      >
                        <option value="fresh">fresh</option>
                        <option value="stale">stale</option>
                        <option value="warning">warning</option>
                      </select>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {locked ? (
                      <span className="text-gray-700">{src.latency_minutes}</span>
                    ) : (
                      <input
                        type="number"
                        min={0}
                        value={src.latency_minutes}
                        onChange={(e) => updateSource(i, 'latency_minutes', parseInt(e.target.value) || 0)}
                        className="w-20 border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                      />
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {locked ? (
                      <span className="text-gray-500">{src.notes || '—'}</span>
                    ) : (
                      <input
                        type="text"
                        value={src.notes ?? ''}
                        onChange={(e) => updateSource(i, 'notes', e.target.value)}
                        placeholder="Optional notes…"
                        className="w-full border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                      />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="flex justify-between items-center">
        {!locked ? (
          <Button
            variant="danger"
            onClick={handleLock}
            loading={locking}
            size="lg"
          >
            🔒 Lock Data Sources (Irreversible)
          </Button>
        ) : (
          <div className="text-sm text-gray-500">Data sources are locked and immutable.</div>
        )}

        {locked && (
          <Button onClick={() => router.push(`/simulation/${id}/step/6`)}>
            Continue to Run →
          </Button>
        )}
      </div>
    </div>
  );
}
