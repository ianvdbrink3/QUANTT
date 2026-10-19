import "./research.css";
import ResearchCommandCenter from "@/components/ResearchCommandCenter";
import type { Metadata } from "next";
export const metadata:Metadata={title:"QUANTT — Research Command Center 0.8",description:"Deterministic, audited NQ/ES research sandbox with rigorous provenance."};
export default function ResearchPage(){return <ResearchCommandCenter/>}
