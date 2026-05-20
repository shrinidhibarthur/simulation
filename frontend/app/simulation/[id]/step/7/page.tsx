'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  Label,
} from 'recharts';
import { useSimulationStore } from '@/lib/store';
import * as api from '@/lib/api-client';
import type { Result, Scenario } from '@/lib/types';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';

const SCENARIO_COLORS: Record<string, string> = {
  Base: '#0051A1',
  Optimistic: '#16a34a',
  Pessimistic: '#E41720',
};

// ── Ranking Table ──────────────────────────────────────────────
function ScenarioRankingTable({
  ranked,
  scenarios,
}: {
  ranked: Result[];
  scenarios: Scenario[];
}) {
  const getScenarioName = (scenarioId: string) =>
    scenarios.find((s) => s.id === scenarioId)?.name ?? scenarioId;

  const winner = ranked[0];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="text-left py-3 px-3 text-xs font-semibold text-gray-500 uppercase">Scenario</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-gray-500 uppercase">CVR Lift %</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-gray-500 uppercase">AOV Delta $</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-gray-500 uppercase">RPV Lift %</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-gray-500 uppercase">Margin Impact</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-gray-500 uppercase">SLA Risk</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-gray-500 uppercase">Composite Score</th>
          </tr>
        </thead>
        <tbody>
          {ranked.map((r) => {
            const name = getScenarioName(r.scenario_id);
            const isWinner = r.scenario_id === winner?.scenario_id;
            return (
              <tr
                key={r.id}
                className={[
                  'border-b transition-colors',
                  isWinner
                    ? 'border-abs-blue-light bg-blue-50 font-semibold'
                    : 'border-gray-100 hover:bg-gray-50',
                ].join(' ')}
              >
                <td className="py-3 px-3">
                  <span
                    className="inline-block w-2.5 h-2.5 rounded-full mr-2"
                    style={{ backgroundColor: SCENARIO_COLORS[name] ?? '#888' }}
                  />
                  {name}
                  {isWinner && (
                    <span className="ml-2 text-xs bg-abs-blue-light text-white px-1.5 py-0.5 rounded-full">
                      Winner
                    </span>
                  )}
                </td>
                <td className="py-3 px-3 text-right tabular-nums">
                  {(r.conversion_lift * 100).toFixed(2)}%
                </td>
                <td className="py-3 px-3 text-right tabular-nums">
                  ${r.aov_delta.toFixed(2)}
                </td>
                <td className="py-3 px-3 text-right tabular-nums">
                  {(r.rpv_lift * 100).toFixed(2)}%
                </td>
                <td className="py-3 px-3 text-right tabular-nums">
                  {(r.margin_impact * 100).toFixed(2)}%
                </td>
                <td className="py-3 px-3 text-right tabular-nums">
                  <span className={r.sla_risk > 0.05 ? 'text-abs-red font-bold' : ''}>
                    {(r.sla_risk * 100).toFixed(2)}%
                  </span>
                </td>
                <td className="py-3 px-3 text-right tabular-nums font-bold">
                  {r.composite_score.toFixed(4)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ── KDE Curve Chart ────────────────────────────────────────────
function KdeCurveChart({
  results,
  scenarios,
}: {
  results: Result[];
  scenarios: Scenario[];
}) {
  const getScenarioName = (sid: string) =>
    scenarios.find((s) => s.id === sid)?.name ?? sid;

  // Build combined data points indexed by x position
  const xSet = new Set<number>();
  results.forEach((r) => r.kde_x_values.forEach((x) => xSet.add(x)));
  const xValues = Array.from(xSet).sort((a, b) => a - b);

  // Map each result to its name
  const resultsByName: Record<string, Result> = {};
  results.forEach((r) => {
    resultsByName[getScenarioName(r.scenario_id)] = r;
  });

  // Build chart data: sample intelligently if too many points
  const MAX_POINTS = 200;
  const step = Math.max(1, Math.floor(xValues.length / MAX_POINTS));

  const chartData = xValues
    .filter((_, i) => i % step === 0)
    .map((x) => {
      const row: Record<string, number> = { x };
      Object.entries(resultsByName).forEach(([name, r]) => {
        const idx = r.kde_x_values.indexOf(x);
        if (idx !== -1) row[name] = r.kde_y_values[idx];
      });
      return row;
    });

  const names = Object.keys(resultsByName);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={chartData} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="x"
          type="number"
          domain={['dataMin', 'dataMax']}
          tickFormatter={(v: number) => `${(v * 100).toFixed(1)}%`}
          tick={{ fontSize: 11 }}
        >
          <Label value="RPV Lift" offset={-10} position="insideBottom" style={{ fontSize: 11 }} />
        </XAxis>
        <YAxis tick={{ fontSize: 11 }} width={45} />
        <Tooltip
          formatter={(value: number, name: string) => [value.toFixed(4), name]}
          labelFormatter={(label: number) => `RPV: ${(label * 100).toFixed(2)}%`}
        />
        <Legend />
        <ReferenceLine
          x={0.0245}
          stroke="#dc2626"
          strokeDasharray="4 2"
          label={{ value: 'Baseline', position: 'top', fontSize: 10 }}
        />
        {names.map((name) => (
          <Area
            key={name}
            type="monotone"
            dataKey={name}
            stroke={SCENARIO_COLORS[name] ?? '#888'}
            fill={SCENARIO_COLORS[name] ?? '#888'}
            fillOpacity={0.3}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
}

// ── Scenario Comparison Bar Chart ──────────────────────────────
function ScenarioComparisonChart({
  results,
  scenarios,
}: {
  results: Result[];
  scenarios: Scenario[];
}) {
  const getScenarioName = (sid: string) =>
    scenarios.find((s) => s.id === sid)?.name ?? sid;

  const chartData = [
    {
      metric: 'CVR Lift %',
      ...Object.fromEntries(
        results.map((r) => [getScenarioName(r.scenario_id), +(r.conversion_lift * 100).toFixed(3)])
      ),
    },
    {
      metric: 'RPV Lift %',
      ...Object.fromEntries(
        results.map((r) => [getScenarioName(r.scenario_id), +(r.rpv_lift * 100).toFixed(3)])
      ),
    },
    {
      metric: 'Margin Impact %',
      ...Object.fromEntries(
        results.map((r) => [getScenarioName(r.scenario_id), +(r.margin_impact * 100).toFixed(3)])
      ),
    },
  ];

  const names = results.map((r) => getScenarioName(r.scenario_id));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="metric" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v: number) => `${v}%`} />
        <Tooltip formatter={(v: number) => `${v.toFixed(3)}%`} />
        <Legend />
        {names.map((name) => (
          <Bar
            key={name}
            dataKey={name}
            fill={SCENARIO_COLORS[name] ?? '#888'}
            isAnimationActive={false}
            radius={[3, 3, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Risk/Return Scatter ────────────────────────────────────────
function RiskReturnScatter({
  results,
  scenarios,
}: {
  results: Result[];
  scenarios: Scenario[];
}) {
  const getScenarioName = (sid: string) =>
    scenarios.find((s) => s.id === sid)?.name ?? sid;

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          type="number"
          dataKey="x"
          name="SLA Risk"
          tickFormatter={(v: number) => `${(v * 100).toFixed(1)}%`}
          tick={{ fontSize: 11 }}
        >
          <Label value="SLA Risk" offset={-10} position="insideBottom" style={{ fontSize: 11 }} />
        </XAxis>
        <YAxis
          type="number"
          dataKey="y"
          name="Composite Score"
          tick={{ fontSize: 11 }}
          width={60}
        >
          <Label
            value="Composite Score"
            angle={-90}
            position="insideLeft"
            style={{ fontSize: 11 }}
          />
        </YAxis>
        <Tooltip
          cursor={{ strokeDasharray: '3 3' }}
          content={({ payload }) => {
            if (!payload?.length) return null;
            const d = payload[0].payload as { x: number; y: number; name: string };
            return (
              <div className="bg-white border border-gray-200 rounded px-3 py-2 text-xs shadow">
                <p className="font-semibold">{d.name}</p>
                <p>SLA Risk: {(d.x * 100).toFixed(2)}%</p>
                <p>Score: {d.y.toFixed(4)}</p>
              </div>
            );
          }}
        />
        <ReferenceLine
          x={0.05}
          stroke="#E41720"
          strokeDasharray="4 2"
          label={{ value: 'SLA Threshold', position: 'top', fontSize: 9 }}
        />
        <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="4 2" />
        {results.map((r) => {
          const name = getScenarioName(r.scenario_id);
          const data = [{ x: r.sla_risk, y: r.composite_score, name }];
          return (
            <Scatter
              key={r.id}
              name={name}
              data={data}
              fill={SCENARIO_COLORS[name] ?? '#888'}
              isAnimationActive={false}
            />
          );
        })}
        <Legend />
      </ScatterChart>
    </ResponsiveContainer>
  );
}

// ── Beacon Metrics Panel ───────────────────────────────────────
function BeaconMetricsPanel({
  winner,
  winnerName,
}: {
  winner: Result;
  winnerName: string;
}) {
  return (
    <Card className="border-yellow-300 bg-yellow-50">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🏆</span>
        <div>
          <h3 className="font-bold text-yellow-800">Winner: {winnerName}</h3>
          <p className="text-xs text-yellow-700">Beacon Metrics</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-4 text-center shadow-sm">
          <div className="text-2xl font-bold text-abs-blue-dark">
            {winner.win_probability !== undefined
              ? `${(winner.win_probability * 100).toFixed(1)}%`
              : '—'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Win Probability</div>
        </div>
        <div className="bg-white rounded-lg p-4 text-center shadow-sm">
          <div className="text-2xl font-bold text-green-700">
            {winner.demand_momentum !== undefined
              ? winner.demand_momentum.toFixed(3)
              : '—'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Demand Momentum</div>
        </div>
        <div className="bg-white rounded-lg p-4 text-center shadow-sm">
          <div className="text-2xl font-bold text-abs-blue-dark">
            {winner.visibility_budget !== undefined
              ? `$${winner.visibility_budget.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
              : '—'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Visibility Budget</div>
        </div>
      </div>
    </Card>
  );
}

// ── Main Page ──────────────────────────────────────────────────
export default function Step7Page() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const scenarios = useSimulationStore((s) => s.scenarios);
  const storeResults = useSimulationStore((s) => s.results);
  const setResults = useSimulationStore((s) => s.setResults);
  const setError = useSimulationStore((s) => s.setError);

  const [results, setLocalResults] = useState<Result[]>(storeResults);
  const [ranked, setRanked] = useState<Result[]>([]);
  const [loading, setLoading] = useState(storeResults.length === 0);

  const loadResults = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await api.getResults(id);
      setLocalResults(data.results);
      setRanked(data.ranked);
      setResults(data.results);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load results';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [id, setResults, setError]);

  useEffect(() => {
    if (storeResults.length > 0) {
      setLocalResults(storeResults);
      setRanked([...storeResults].sort((a, b) => b.composite_score - a.composite_score));
      setLoading(false);
    } else {
      loadResults();
    }
  }, [storeResults, loadResults]);

  const winner = ranked[0];
  const getScenarioName = (sid: string) =>
    scenarios.find((s) => s.id === sid)?.name ?? sid;

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-60 w-full" />
        <Skeleton className="h-60 w-full" />
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 7 — Results Dashboard</h1>
        <Card>
          <p className="text-gray-500 text-center py-8">
            No results available yet. Please complete Step 6 to run the simulation.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-abs-blue-dark">Step 7 — Results Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">
          Monte Carlo simulation results across all scenarios.
        </p>
      </div>

      {/* Beacon Metrics for winner */}
      {winner && (
        <BeaconMetricsPanel winner={winner} winnerName={getScenarioName(winner.scenario_id)} />
      )}

      {/* Ranking Table */}
      <Card>
        <h2 className="text-base font-semibold text-gray-800 mb-4">Scenario Rankings</h2>
        <ScenarioRankingTable ranked={ranked} scenarios={scenarios} />
      </Card>

      {/* KDE Curve */}
      <Card>
        <h2 className="text-base font-semibold text-gray-800 mb-4">
          RPV Lift Distribution (KDE)
        </h2>
        <KdeCurveChart results={results} scenarios={scenarios} />
      </Card>

      {/* Comparison Bar Chart */}
      <Card>
        <h2 className="text-base font-semibold text-gray-800 mb-4">
          Scenario Comparison
        </h2>
        <ScenarioComparisonChart results={results} scenarios={scenarios} />
      </Card>

      {/* Risk / Return Scatter */}
      <Card>
        <h2 className="text-base font-semibold text-gray-800 mb-4">
          Risk vs. Return
        </h2>
        <RiskReturnScatter results={results} scenarios={scenarios} />
      </Card>

      <div className="flex justify-end">
        <Button onClick={() => router.push(`/simulation/${id}/step/8`)}>
          Continue to Rollout →
        </Button>
      </div>
    </div>
  );
}
