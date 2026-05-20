import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Albertsons Simulation Lab",
  description: "Monte Carlo simulation platform for e-commerce strategy testing",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
