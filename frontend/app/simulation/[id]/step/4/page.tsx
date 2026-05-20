'use client';

import React, { useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';

interface ColumnProfile {
  dtype: string;
  distribution?: string;
  params?: Record<string, number>;
  null_pct?: number;
  unique?: number;
  [key: string]: unknown;
}

function CsvProfileTable({ profile }: { profile: Record<string, unknown> }) {
  const columns = profile.columns as Record<string, ColumnProfile> | undefined;
  if (!columns) return null;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Column</th>
            <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Type</th>
            <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Distribution</th>
            <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Params</th>
            <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Null %</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(columns).map(([col, info]) => (
            <tr key={col} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-2 px-3 font-mono text-xs text-abs-blue-dark">{col}</td>
              <td className="py-2 px-3 text-gray-700">{info.dtype ?? '—'}</td>
              <td className="py-2 px-3 text-gray-700">{info.distribution ?? '—'}</td>
              <td className="py-2 px-3 text-gray-600 font-mono text-xs">
                {info.params
                  ? Object.entries(info.params)
                      .map(([k, v]) => `${k}: ${typeof v === 'number' ? v.toFixed(3) : v}`)
                      .join(', ')
                  : '—'}
              </td>
              <td className="py-2 px-3 text-gray-700">
                {info.null_pct !== undefined ? `${(info.null_pct * 100).toFixed(1)}%` : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Step4Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const simulation = useSimulationStore((s) => s.simulation);
  const setSimulation = useSimulationStore((s) => s.setSimulation);
  const setError = useSimulationStore((s) => s.setError);

  const [uploading, setUploading] = useState(false);
  const [profileData, setProfileData] = useState<Record<string, unknown> | null>(
    simulation?.csv_profile ?? null
  );
  const [fileName, setFileName] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file || !id) return;

      if (file.size > 10 * 1024 * 1024) {
        setError('File too large. Maximum size is 10MB.');
        return;
      }

      setFileName(file.name);
      setUploading(true);
      try {
        const updated = await api.profileCsv(id, file);
        setSimulation(updated);
        setProfileData(updated.csv_profile ?? null);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to profile CSV';
        setError(msg);
      } finally {
        setUploading(false);
      }
    },
    [id, setSimulation, setError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
    disabled: uploading,
  });

  const seed = simulation?.seed;
  const hasProfile = profileData !== null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 4 — Configuration</h1>
        <p className="text-gray-500 text-sm mt-1">
          Upload historical transaction data to fit distribution parameters.
        </p>
      </div>

      {/* CSV Upload */}
      <Card>
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Historical Data Upload</h2>
        <div
          {...getRootProps()}
          className={[
            'border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors',
            isDragActive
              ? 'border-abs-blue-light bg-blue-50'
              : 'border-gray-300 hover:border-abs-blue-light hover:bg-gray-50',
            uploading ? 'opacity-60 cursor-not-allowed' : '',
          ].join(' ')}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <div className="space-y-2">
              <div className="animate-spin h-8 w-8 border-4 border-abs-blue-light border-t-transparent rounded-full mx-auto" />
              <p className="text-sm text-gray-500">Profiling {fileName}…</p>
            </div>
          ) : (
            <>
              <svg
                className="h-10 w-10 text-gray-400 mx-auto mb-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              {fileName ? (
                <p className="text-sm text-gray-700">
                  <span className="font-medium">{fileName}</span> — drop a new file to replace
                </p>
              ) : (
                <>
                  <p className="text-sm font-medium text-gray-700">
                    {isDragActive ? 'Drop CSV here' : 'Drag & drop a CSV file, or click to browse'}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">Max 10MB · .csv only</p>
                </>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Profile Results */}
      {uploading && !hasProfile && (
        <Card>
          <Skeleton className="h-6 w-40 mb-4" />
          <Skeleton className="h-40 w-full" />
        </Card>
      )}

      {hasProfile && profileData && (
        <Card>
          <h2 className="text-sm font-semibold text-gray-700 mb-1">Column Distribution Profile</h2>
          {profileData.row_count !== undefined && (
            <p className="text-xs text-gray-500 mb-4">
              {(profileData.row_count as number).toLocaleString()} rows · {fileName ?? 'uploaded file'}
            </p>
          )}
          <CsvProfileTable profile={profileData} />
        </Card>
      )}

      {/* Seed display */}
      {seed !== undefined && seed !== null && (
        <Card>
          <h2 className="text-sm font-semibold text-gray-700 mb-2">Random Seed</h2>
          <div className="font-mono text-abs-blue-dark bg-blue-50 border border-abs-blue-light rounded px-4 py-2 inline-block text-sm">
            {seed}
          </div>
          <p className="text-xs text-gray-400 mt-2">
            This seed ensures reproducible Monte Carlo results. Locked at simulation creation.
          </p>
        </Card>
      )}

      <div className="flex justify-end">
        <Button onClick={() => router.push(`/simulation/${id}/step/5`)}>
          Continue to Data Lock →
        </Button>
      </div>
    </div>
  );
}
