"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { CommandTerminal } from "@/components/CommandTerminal";
import { LiveRiskMeter } from "@/components/LiveRiskMeter";
import { ExplainabilityCard } from "@/components/ExplainabilityCard";
import { AIImpactReportModal } from "@/components/AIImpactReportModal";
import { AIDecisionTree } from "@/components/AIDecisionTree";
import { DependencyGraph } from "@/components/DependencyGraph";
import { ThreatTimeline } from "@/components/ThreatTimeline";
import { SafetyHeatmap } from "@/components/SafetyHeatmap";
import { FloatingAssistant } from "@/components/FloatingAssistant";
import { evaluateCommand, CommandEvaluationResponse } from "@/lib/api";

export default function Home() {
  const [data, setData] = useState<CommandEvaluationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [impactModalOpen, setImpactModalOpen] = useState<boolean>(false);

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

  useEffect(() => {
    handleEvaluate("sudo rm -rf /var/log/*");
  }, []);

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Terminal Safety Heatmap & User AI Safety Score */}
        <SafetyHeatmap />

        {/* Top Grid: Terminal Input & Adaptive Risk Meter */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CommandTerminal onEvaluateCommand={handleEvaluate} loading={loading} />
          <LiveRiskMeter data={data} loading={loading} />
        </div>

        {/* Dual Rationale View & ✨ AI Command Safe Rewrites */}
        <ExplainabilityCard
          data={data}
          onApplyAlternative={(altCmd) => handleEvaluate(altCmd)}
          onOpenImpactReport={() => setImpactModalOpen(true)}
        />

        {/* 🌳 AI Decision Tree Visualizer */}
        {data?.decision_tree && <AIDecisionTree nodes={data.decision_tree} />}

        {/* Predictive Blast-Radius Dependency Graph */}
        <DependencyGraph data={data} />

        {/* CrowdStrike-Style Threat Timeline Audit Log & OS Events */}
        <ThreatTimeline />
      </main>

      {/* Floating Shield Desktop Assistant Widget */}
      <FloatingAssistant
        data={data}
        onOpenImpactReport={() => setImpactModalOpen(true)}
        onApplyAlternative={(altCmd) => handleEvaluate(altCmd)}
      />

      {/* 📊 AI Impact Report Modal */}
      <AIImpactReportModal
        report={data?.ai_impact_report || null}
        isOpen={impactModalOpen}
        onClose={() => setImpactModalOpen(false)}
        onSelectAction={(action) => {
          if (action === "alternative" && data?.ai_command_rewrites?.length) {
            handleEvaluate(data.ai_command_rewrites[0].safe_command);
            setImpactModalOpen(false);
          }
        }}
      />

      <footer className="border-t border-gray-800 py-6 text-center text-xs text-gray-500 bg-[#0d1322]/50">
        ShellGuard Runtime (Powered by ShellGuard AI Engine) • OS Safety Layer • Hackathon Edition
      </footer>
    </div>
  );
}
