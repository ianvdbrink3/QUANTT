import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "QUANTT — Quant Research Lab",
  description:
    "Auditable intraday market research, session analytics, and data quality.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
