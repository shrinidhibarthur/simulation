"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function NewSimulationPage() {
  const router = useRouter();
  const [requestText, setRequestText] = useState("");
  const [mvt, setMvt] = useState("");
  const [budget, setBudget] = useState("");
  const [slaLimit, setSlaLimit] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/simulations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_text: requestText,
          mvt: mvt || null,
          budget: budget ? parseFloat(budget) : null,
          sla_limit: slaLimit ? parseFloat(slaLimit) : null,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to create simulation");
      }

      const sim = await res.json();
      router.push(`/simulation/${sim.id}/step/2`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <a href="/simulation" className="text-abs-blue-light text-sm hover:underline">← Back to simulations</a>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-8">
          <h1 className="text-2xl font-bold text-abs-blue-dark mb-2">New Simulation</h1>
          <p className="text-gray-500 mb-6 text-sm">Describe the e-commerce strategy you want to test.</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Test Request <span className="text-abs-red">*</span>
              </label>
              <textarea
                value={requestText}
                onChange={e => setRequestText(e.target.value)}
                required
                minLength={10}
                rows={5}
                placeholder="e.g. We want to test a 20% promotional discount on the PLP with an enhanced grid layout to understand the impact on conversion rate and margin..."
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light resize-none"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">MVT Name</label>
                <input
                  type="text"
                  value={mvt}
                  onChange={e => setMvt(e.target.value)}
                  placeholder="e.g. Q4-PLP-Test"
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Budget ($)</label>
                <input
                  type="number"
                  value={budget}
                  onChange={e => setBudget(e.target.value)}
                  placeholder="e.g. 50000"
                  min="0"
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">SLA Limit (0–1)</label>
                <input
                  type="number"
                  value={slaLimit}
                  onChange={e => setSlaLimit(e.target.value)}
                  placeholder="e.g. 0.05"
                  min="0" max="1" step="0.01"
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border-l-4 border-abs-red text-red-700 px-4 py-3 text-sm rounded">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || requestText.length < 10}
              className="w-full bg-abs-blue-dark text-white py-3 rounded font-semibold text-sm hover:bg-abs-blue-dark2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Creating simulation…" : "Submit Request →"}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
