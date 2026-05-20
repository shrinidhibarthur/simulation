"use client";

export default function SimulationListPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-abs-blue-dark mb-2">
          Albertsons Simulation Lab
        </h1>
        <p className="text-gray-500 mb-8">Monte Carlo e-commerce strategy simulator</p>
        <a
          href="/simulation/new"
          className="inline-block bg-abs-blue-dark text-white px-6 py-3 rounded font-semibold hover:bg-abs-blue-dark2 transition-colors"
        >
          + New Simulation
        </a>
      </div>
    </main>
  );
}
