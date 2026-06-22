"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const STRATEGY_CATEGORIES = [
  "Pricing & Promotions",
  "UX / Storefront",
  "Search & Discovery",
  "Checkout & Conversion",
  "Fulfillment & SLA",
  "Inventory & Merchandising",
  "Marketing & Campaigns",
  "Loyalty & CRM",
  "Other",
];

const DATA_SOURCES = [
  "Adobe / EDDL (clickstream)",
  "OMS (order data)",
  "Inventory system",
  "Pricing engine",
  "CRM / loyalty data",
  "WMS",
  "Carrier / delivery data",
];

const TIMELINE_OPTIONS = [
  "< 1 week",
  "1–2 weeks",
  "2–4 weeks",
  "1–3 months",
  "3+ months",
];

const BUDGET_OPTIONS = [
  "< $10K",
  "$10K – $50K",
  "$50K – $200K",
  "$200K – $500K",
  "$500K+",
  "Not yet determined",
];

interface FormData {
  // Submitter info
  teamName: string;
  contactName: string;
  contactEmail: string;
  department: string;

  // Strategy
  strategyCategory: string;
  mvtName: string;
  strategyDescription: string;
  businessGoal: string;
  successMetric: string;

  // Parameters
  budget: string;
  slaLimit: string;
  launchTimeline: string;

  // Data
  availableDataSources: string[];
  hasCsvData: string;
  csvDescription: string;

  // Risk
  riskAppetite: string;
  additionalContext: string;
}

const EMPTY: FormData = {
  teamName: "",
  contactName: "",
  contactEmail: "",
  department: "",
  strategyCategory: "",
  mvtName: "",
  strategyDescription: "",
  businessGoal: "",
  successMetric: "",
  budget: "",
  slaLimit: "",
  launchTimeline: "",
  availableDataSources: [],
  hasCsvData: "",
  csvDescription: "",
  riskAppetite: "",
  additionalContext: "",
};

export default function IntakePage() {
  const router = useRouter();
  const [form, setForm] = useState<FormData>(EMPTY);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [simId, setSimId] = useState<string | null>(null);

  const set = (field: keyof FormData, value: string) =>
    setForm((f) => ({ ...f, [field]: value }));

  const toggleDataSource = (src: string) => {
    setForm((f) => ({
      ...f,
      availableDataSources: f.availableDataSources.includes(src)
        ? f.availableDataSources.filter((s) => s !== src)
        : [...f.availableDataSources, src],
    }));
  };

  const buildRequestText = (): string => {
    const parts = [
      `Team: ${form.teamName} (${form.department})`,
      `Contact: ${form.contactName} <${form.contactEmail}>`,
      `Strategy Category: ${form.strategyCategory}`,
      `MVT Name: ${form.mvtName || "TBD"}`,
      "",
      `STRATEGY DESCRIPTION:`,
      form.strategyDescription,
      "",
      `BUSINESS GOAL:`,
      form.businessGoal,
      "",
      `SUCCESS METRIC:`,
      form.successMetric,
      "",
      `Launch Timeline: ${form.launchTimeline}`,
      `Risk Appetite: ${form.riskAppetite}`,
      `Budget Range: ${form.budget}`,
      "",
      `Available Data Sources: ${form.availableDataSources.join(", ") || "None specified"}`,
      `Has CSV Data: ${form.hasCsvData}`,
      form.csvDescription ? `CSV Description: ${form.csvDescription}` : "",
      form.additionalContext ? `Additional Context: ${form.additionalContext}` : "",
    ]
      .filter(Boolean)
      .join("\n");
    return parts;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/simulations`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            request_text: buildRequestText(),
            mvt: form.mvtName || undefined,
            budget: form.budget && !form.budget.includes("Not")
              ? undefined  // budget is a range string, not a number — stored in request_text
              : undefined,
            sla_limit: form.slaLimit ? parseFloat(form.slaLimit) : undefined,
          }),
        }
      );

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to submit intake form");
      }

      const sim = await res.json();
      setSimId(sim.id);
      setSubmitted(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setLoading(false);
    }
  };

  if (submitted && simId) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
        <div className="max-w-lg w-full bg-white rounded-xl border border-gray-200 shadow-sm p-10 text-center">
          <div className="text-5xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-abs-blue-dark mb-2">
            Intake Submitted!
          </h1>
          <p className="text-gray-600 mb-6 text-sm leading-relaxed">
            Your simulation request has been created and is ready for the
            AI clarification step. The Gemini agent will now ask targeted
            questions to refine your use-case brief.
          </p>
          <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
            <p className="text-xs text-gray-500 font-medium mb-1">Simulation ID</p>
            <p className="font-mono text-sm text-gray-800 break-all">{simId}</p>
          </div>
          <div className="flex flex-col gap-3">
            <button
              onClick={() => router.push(`/simulation/${simId}/step/2`)}
              className="w-full bg-abs-blue-dark text-white py-3 rounded-lg font-semibold text-sm hover:bg-abs-blue-dark2 transition-colors"
            >
              Start AI Clarification →
            </button>
            <Link
              href="/simulation"
              className="w-full border border-gray-300 text-gray-700 py-3 rounded-lg font-semibold text-sm hover:bg-gray-50 transition-colors text-center"
            >
              View All Simulations
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/simulation"
            className="text-abs-blue-light text-sm hover:underline"
          >
            ← Back to Simulations
          </Link>
          <div className="mt-4 flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-abs-blue-dark flex items-center justify-center text-white text-xl shrink-0">
              📋
            </div>
            <div>
              <h1 className="text-3xl font-bold text-abs-blue-dark">
                Simulation Lab — Intake Form
              </h1>
              <p className="text-gray-500 mt-1">
                Describe your strategy. Our AI will design scenarios, run
                10,000 Monte Carlo iterations, and return a ranked outcome
                with a phased rollout plan.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Section 1: Team Info */}
          <section className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-abs-blue-dark text-white text-xs flex items-center justify-center font-bold">1</span>
              Team Information
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Name <span className="text-abs-red">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={form.contactName}
                  onChange={(e) => set("contactName", e.target.value)}
                  placeholder="Jane Smith"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email <span className="text-abs-red">*</span>
                </label>
                <input
                  type="email"
                  required
                  value={form.contactEmail}
                  onChange={(e) => set("contactEmail", e.target.value)}
                  placeholder="jane.smith@albertsons.com"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team / Squad <span className="text-abs-red">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={form.teamName}
                  onChange={(e) => set("teamName", e.target.value)}
                  placeholder="e.g. Checkout Experience"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department <span className="text-abs-red">*</span>
                </label>
                <select
                  required
                  value={form.department}
                  onChange={(e) => set("department", e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light bg-white"
                >
                  <option value="">Select department…</option>
                  {["Product", "Pricing", "Merchandising", "Marketing", "Fulfillment & Ops", "Data & Analytics", "Engineering", "Finance", "Other"].map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            </div>
          </section>

          {/* Section 2: Strategy */}
          <section className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-abs-blue-dark text-white text-xs flex items-center justify-center font-bold">2</span>
              Strategy Description
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Strategy Category <span className="text-abs-red">*</span>
                  </label>
                  <select
                    required
                    value={form.strategyCategory}
                    onChange={(e) => set("strategyCategory", e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light bg-white"
                  >
                    <option value="">Select category…</option>
                    {STRATEGY_CATEGORIES.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    MVT / Experiment Name
                  </label>
                  <input
                    type="text"
                    value={form.mvtName}
                    onChange={(e) => set("mvtName", e.target.value)}
                    placeholder="e.g. Q4-PLP-GridTest-2025"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Strategy Description <span className="text-abs-red">*</span>
                </label>
                <textarea
                  required
                  minLength={30}
                  rows={4}
                  value={form.strategyDescription}
                  onChange={(e) => set("strategyDescription", e.target.value)}
                  placeholder="Describe what you want to test. Include the change, the audience, the channel, and what you expect to happen. E.g. 'We want to test a 20% promotional discount on the PLP with an enhanced grid layout to understand impact on conversion rate and margin across grocery and household categories.'"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light resize-none"
                />
                <p className="text-xs text-gray-400 mt-1">{form.strategyDescription.length} / 30 min characters</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Business Goal <span className="text-abs-red">*</span>
                  </label>
                  <textarea
                    required
                    rows={3}
                    value={form.businessGoal}
                    onChange={(e) => set("businessGoal", e.target.value)}
                    placeholder="e.g. Increase Q4 e-commerce revenue by 8% without eroding grocery margin below 40%"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light resize-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Success Metric <span className="text-abs-red">*</span>
                  </label>
                  <textarea
                    required
                    rows={3}
                    value={form.successMetric}
                    onChange={(e) => set("successMetric", e.target.value)}
                    placeholder="e.g. RPV lift ≥ 5%, CVR uplift ≥ 2%, Margin impact ≥ -1%"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light resize-none"
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Section 3: Parameters */}
          <section className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-abs-blue-dark text-white text-xs flex items-center justify-center font-bold">3</span>
              Experiment Parameters
            </h2>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget Range <span className="text-abs-red">*</span>
                </label>
                <select
                  required
                  value={form.budget}
                  onChange={(e) => set("budget", e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light bg-white"
                >
                  <option value="">Select range…</option>
                  {BUDGET_OPTIONS.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Launch Timeline <span className="text-abs-red">*</span>
                </label>
                <select
                  required
                  value={form.launchTimeline}
                  onChange={(e) => set("launchTimeline", e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light bg-white"
                >
                  <option value="">Select timeline…</option>
                  {TIMELINE_OPTIONS.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  SLA / Stockout Limit
                  <span className="text-gray-400 font-normal ml-1">(0–1)</span>
                </label>
                <input
                  type="number"
                  value={form.slaLimit}
                  onChange={(e) => set("slaLimit", e.target.value)}
                  placeholder="e.g. 0.05"
                  min="0" max="1" step="0.01"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
                <p className="text-xs text-gray-400 mt-1">Max acceptable stockout rate. Default: 0.05</p>
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risk Appetite <span className="text-abs-red">*</span>
              </label>
              <div className="flex gap-3">
                {["Conservative", "Moderate", "Aggressive"].map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => set("riskAppetite", r)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-colors ${
                      form.riskAppetite === r
                        ? r === "Conservative"
                          ? "bg-blue-50 border-abs-blue-dark text-abs-blue-dark"
                          : r === "Moderate"
                          ? "bg-yellow-50 border-yellow-500 text-yellow-700"
                          : "bg-red-50 border-abs-red text-abs-red"
                        : "border-gray-300 text-gray-500 hover:bg-gray-50"
                    }`}
                  >
                    {r === "Conservative" ? "🛡️" : r === "Moderate" ? "⚖️" : "🚀"} {r}
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* Section 4: Data Availability */}
          <section className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-abs-blue-dark text-white text-xs flex items-center justify-center font-bold">4</span>
              Data Availability
            </h2>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Which data sources can you provide access to?
              </label>
              <div className="grid grid-cols-2 gap-2">
                {DATA_SOURCES.map((src) => (
                  <label
                    key={src}
                    className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer text-sm transition-colors ${
                      form.availableDataSources.includes(src)
                        ? "border-abs-blue-light bg-blue-50 text-abs-blue-dark"
                        : "border-gray-200 hover:bg-gray-50 text-gray-700"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={form.availableDataSources.includes(src)}
                      onChange={() => toggleDataSource(src)}
                      className="accent-abs-blue-dark"
                    />
                    {src}
                  </label>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Do you have historical transaction CSV data? <span className="text-abs-red">*</span>
                </label>
                <div className="flex gap-3 mt-1">
                  {["Yes — ready to upload", "Yes — needs prep", "No"].map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => set("hasCsvData", opt)}
                      className={`flex-1 py-2 rounded-lg text-xs font-medium border transition-colors ${
                        form.hasCsvData === opt
                          ? "bg-abs-blue-dark text-white border-abs-blue-dark"
                          : "border-gray-300 text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  CSV Description
                  <span className="text-gray-400 font-normal ml-1">(optional)</span>
                </label>
                <input
                  type="text"
                  value={form.csvDescription}
                  onChange={(e) => set("csvDescription", e.target.value)}
                  placeholder="e.g. 90-day order history with CVR, AOV, margin per SKU"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light"
                />
              </div>
            </div>
          </section>

          {/* Section 5: Additional Context */}
          <section className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-abs-blue-dark text-white text-xs flex items-center justify-center font-bold">5</span>
              Anything Else?
            </h2>
            <textarea
              rows={3}
              value={form.additionalContext}
              onChange={(e) => set("additionalContext", e.target.value)}
              placeholder="Any constraints, dependencies, prior experiments, stakeholder requirements, or context the simulator should know about…"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-abs-blue-light resize-none"
            />
          </section>

          {/* Validation summary */}
          {error && (
            <div className="bg-red-50 border-l-4 border-abs-red text-red-700 px-4 py-3 text-sm rounded-lg">
              {error}
            </div>
          )}

          {/* What happens next */}
          <div className="bg-blue-50 border border-abs-blue-light/30 rounded-xl p-5">
            <p className="text-xs font-semibold text-abs-blue-dark mb-2 uppercase tracking-wide">What happens after you submit</p>
            <ol className="text-sm text-gray-700 space-y-1 list-decimal list-inside">
              <li>Your intake is saved and a simulation record is created</li>
              <li>Gemini AI asks 3–5 clarifying questions to sharpen your brief</li>
              <li>AI generates Base, Optimistic, and Pessimistic scenarios</li>
              <li>You upload CSV data — AI fits statistical distributions</li>
              <li>10,000 Monte Carlo iterations run in seconds</li>
              <li>You receive ranked results, probability charts, and a rollout plan</li>
            </ol>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={
              loading ||
              !form.contactName ||
              !form.contactEmail ||
              !form.teamName ||
              !form.department ||
              !form.strategyCategory ||
              form.strategyDescription.length < 30 ||
              !form.businessGoal ||
              !form.successMetric ||
              !form.budget ||
              !form.launchTimeline ||
              !form.riskAppetite ||
              !form.hasCsvData
            }
            className="w-full bg-abs-blue-dark text-white py-4 rounded-xl font-bold text-base hover:bg-abs-blue-dark2 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            {loading ? "Submitting…" : "Submit Intake & Start Simulation →"}
          </button>
          <p className="text-center text-xs text-gray-400 pb-6">
            All fields marked <span className="text-abs-red">*</span> are required.
            Your intake is saved immediately — you can continue the workflow at any time.
          </p>
        </form>
      </div>
    </main>
  );
}
