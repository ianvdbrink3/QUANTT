import "./research.css";
import Link from "next/link";
import ResearchCommandCenter from "@/components/ResearchCommandCenter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "QUANTT — Research Command Center 0.8 / 0.9",
  description: "Synthetic research 0.8 and separately audited observed futures 0.9.",
};

export default function ResearchPage() {
  return (
    <>
      <nav style={{ background: "#0b1220", padding: "12px 32px", color: "#9fc9ff" }}>
        <Link href="/research/nq" style={{ display: "block", paddingBottom: 8, color: "#67dfbd", textDecoration: "underline" }}>
          Echte NQ-data: 78 handelsdagen, kostenbacktests en edge-robuustheid →
        </Link>
        <Link href="/research/observed" style={{ textDecoration: "underline" }}>
          View 0.9 observed-futures readiness and provenance →
        </Link>
      </nav>
      <ResearchCommandCenter />
    </>
  );
}
