'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';

interface BriefSection {
  [key: string]: unknown;
}

function UseCaseBriefPreview({ brief }: { brief: Record<string, unknown> }) {
  const [open, setOpen] = useState(false);

  return (
    <Card className="border-green-200 bg-green-50">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-green-800">Use Case Brief Generated</h3>
        <button
          onClick={() => setOpen((v) => !v)}
          className="text-xs text-green-700 underline hover:no-underline"
        >
          {open ? 'Collapse' : 'Expand'}
        </button>
      </div>
      {open && (
        <div className="mt-4 space-y-3">
          {Object.entries(brief).map(([key, value]) => (
            <div key={key}>
              <dt className="text-xs font-semibold text-green-700 uppercase tracking-wider mb-0.5">
                {key.replace(/_/g, ' ')}
              </dt>
              <dd className="text-sm text-gray-800">
                {typeof value === 'string'
                  ? value
                  : Array.isArray(value)
                  ? (value as unknown[]).join(', ')
                  : JSON.stringify(value)}
              </dd>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

export default function Step2Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const simulation = useSimulationStore((s) => s.simulation);
  const setSimulation = useSimulationStore((s) => s.setSimulation);
  const setError = useSimulationStore((s) => s.setError);

  const [questions, setQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [brief, setBrief] = useState<Record<string, unknown> | null>(null);
  const [complete, setComplete] = useState(false);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const loadInitialQuestions = useCallback(async () => {
    if (!id) return;
    setLoadingInitial(true);
    try {
      const res = await api.clarify(id);
      setQuestions(res.questions);
      if (res.complete && res.use_case_brief) {
        setBrief(res.use_case_brief);
        setComplete(true);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load questions';
      setError(msg);
    } finally {
      setLoadingInitial(false);
    }
  }, [id, setError]);

  useEffect(() => {
    loadInitialQuestions();
  }, [loadInitialQuestions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    setSubmitting(true);
    try {
      const res = await api.clarify(id, answers);
      setQuestions(res.questions);
      if (res.complete && res.use_case_brief) {
        setBrief(res.use_case_brief);
        setComplete(true);
        // Refresh simulation to get updated step/status
        const updated = await api.getSimulation(id);
        setSimulation(updated);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit answers';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingInitial) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 2 — AI Clarifier</h1>
        <p className="text-gray-500 text-sm mt-1">
          Answer the AI&apos;s questions to refine the simulation scope.
        </p>
      </div>

      {complete && brief && <UseCaseBriefPreview brief={brief} />}

      {!complete && questions.length > 0 && (
        <form onSubmit={handleSubmit} className="space-y-5">
          {questions.map((q, i) => (
            <Card key={i}>
              <label className="block text-sm font-medium text-gray-800 mb-2">
                <span className="text-abs-blue-dark font-semibold mr-2">Q{i + 1}.</span>
                {q}
              </label>
              <textarea
                rows={3}
                value={answers[q] ?? ''}
                onChange={(e) =>
                  setAnswers((prev) => ({ ...prev, [q]: e.target.value }))
                }
                placeholder="Your answer..."
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light resize-none"
              />
            </Card>
          ))}

          <div className="flex justify-end">
            <Button type="submit" loading={submitting}>
              Submit Answers
            </Button>
          </div>
        </form>
      )}

      {complete && (
        <div className="flex justify-end">
          <Button onClick={() => router.push(`/simulation/${id}/step/3`)}>
            Continue to Scenarios →
          </Button>
        </div>
      )}
    </div>
  );
}
