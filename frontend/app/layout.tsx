import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'Albertsons Simulation Lab',
  description: 'Monte Carlo simulation platform for e-commerce strategy testing',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <nav className="bg-abs-blue-dark text-white shadow-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
            <Link
              href="/simulation"
              className="flex items-center gap-2 font-bold text-lg tracking-tight hover:opacity-90 transition-opacity"
            >
              <span>🛒</span>
              <span>Simulation Lab</span>
            </Link>
            <div className="flex items-center gap-6 text-sm font-medium">
              <Link
                href="/simulation"
                className="text-white/80 hover:text-white transition-colors"
              >
                Simulations
              </Link>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
