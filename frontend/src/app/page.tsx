"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { CommandTerminal } from "@/components/CommandTerminal";
import { LiveRiskMeter } from "@/components/LiveRiskMeter";
import { ExplainabilityCard } from "@/components/ExplainabilityCard";
import { DependencyGraph } from "@/components/DependencyGraph";
import { evaluateCommand, CommandEvaluationResponse } from "@/lib/api";

export default function Home() {
  const [data, setData] = useState<CommandEvaluationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleEvaluate = async (command: string) => {
    setLoading(true);
    try {
      const res = await evaluateCommand(command);
      setData(res);
    } catch (err) {
      console.error("Evaluation error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Run initial default evaluation on page load
  useEffect(() => {
    handleEvaluate("sudo rm -rf /var/log/*");
  }, []);

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col font-sans">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Top Grid: Terminal Input & Dynamic Risk Gauge */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CommandTerminal onEvaluateCommand={handleEvaluate} loading={loading} />
          <LiveRiskMeter data={data} loading={loading} />
        </div>

        {/* Explainability & Dual Rationale View */}
        <ExplainabilityCard
          data={data}
          onApplyAlternative={(altCmd) => handleEvaluate(altCmd)}
        />

        {/* Predictive Blast-Radius Dependency Graph */}
        <DependencyGraph data={data} />
      </main>

      <footer className="border-t border-gray-800 py-6 text-center text-xs text-gray-500 bg-[#0d1322]/50">
        ShellGuard AI — Explainable Intent Engine for Safe Linux Command Execution • Hackathon Edition
      </footer>
    </div>
  );
}
