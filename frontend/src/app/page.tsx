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
import { ProcessingTimeline } from "@/components/ProcessingTimeline";
import { SafetyReplayModal } from "@/components/SafetyReplayModal";
import { FloatingAssistant } from "@/components/FloatingAssistant";
import { DiagnosticsModal } from "@/components/DiagnosticsModal";
import { AboutModal } from "@/components/AboutModal";
import { StartupSplash } from "@/components/StartupSplash";
import { evaluateCommand, CommandEvaluationResponse } from "@/lib/api";

export default function Home() {
  const [data, setData] = useState<CommandEvaluationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [impactModalOpen, setImpactModalOpen] = useState<boolean>(false);
  const [replayModalOpen, setReplayModalOpen] = useState<boolean>(false);
  const [diagnosticsOpen, setDiagnosticsOpen] = useState<boolean>(false);
  const [aboutOpen, setAboutOpen] = useState<boolean>(false);
  const [currentCommand, setCurrentCommand] = useState<string>("sudo rm -rf /var/log/*");

  const handleEvaluate = async (command: string) => {
    setLoading(true);
    setCurrentCommand(command);
    try {
      const res = await evaluateCommand(command);
      setData(res);

      // Smart Notification Tiering
      // SAFE: Quiet (No modal)
      // CAUTION / HIGH: Handled in UI card
      // CRITICAL: Auto-trigger Impact Report Modal
      if (res.risk.threat_level === "CRITICAL") {
        setImpactModalOpen(true);
      }
    } catch (err) {
      console.error("Evaluation error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleEvaluate("sudo rm -rf /var/log/*");
  }, []);

  const runtimeState = loading
    ? "Analyzing"
    : data?.risk.threat_level === "CRITICAL"
    ? "Blocking"
    : data?.risk.threat_level === "HIGH"
    ? "Warning"
    : "Watching";

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Startup 2-Second Card */}
      <StartupSplash />

      <Header
        runtimeState={runtimeState}
        systemTrust={data?.system_trust_level || "Verified"}
        onOpenDiagnostics={() => setDiagnosticsOpen(true)}
        onOpenAbout={() => setAboutOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Terminal Safety Heatmap & Safety Score */}
        <SafetyHeatmap />

        {/* ⚡ Runtime Processing Latency Timeline */}
        {data?.processing_latency && <ProcessingTimeline latency={data.processing_latency} />}

        {/* Top Grid: Command Input Terminal & Adaptive Risk Meter */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CommandTerminal onEvaluateCommand={handleEvaluate} loading={loading} />
          <LiveRiskMeter data={data} loading={loading} />
        </div>

        {/* Technical Rationale View & Command Safe Rewrites */}
        <ExplainabilityCard
          data={data}
          onApplyAlternative={(altCmd) => handleEvaluate(altCmd)}
          onOpenImpactReport={() => setImpactModalOpen(true)}
        />

        {/* Step-by-Step Decision Tree Visualizer */}
        {data?.decision_tree && <AIDecisionTree nodes={data.decision_tree} />}

        {/* Predictive Blast-Radius Dependency Graph */}
        <DependencyGraph data={data} />

        {/* CrowdStrike-Style Threat Timeline Audit Log */}
        <ThreatTimeline />
      </main>

      {/* Floating Shield Desktop Assistant Widget */}
      <FloatingAssistant
        data={data}
        onOpenImpactReport={() => setImpactModalOpen(true)}
        onApplyAlternative={(altCmd) => handleEvaluate(altCmd)}
      />

      {/* 📊 Impact Report Modal */}
      <AIImpactReportModal
        report={data?.impact_report || null}
        sandboxPreview={data?.sandbox_preview || null}
        isOpen={impactModalOpen}
        onClose={() => setImpactModalOpen(false)}
        onSelectAction={(action) => {
          if (action === "alternative" && data?.command_rewrites?.length) {
            handleEvaluate(data.command_rewrites[0].safe_command);
            setImpactModalOpen(false);
          } else if (action === "sandbox_preview") {
            setImpactModalOpen(false);
            setReplayModalOpen(true);
          } else if (action === "override") {
            handleEvaluate("echo 'Bypassed safety block via Trust Mode'");
          }
        }}
      />

      {/* 🎞️ Safety Replay Simulator Modal */}
      <SafetyReplayModal
        command={currentCommand}
        isOpen={replayModalOpen}
        onClose={() => setReplayModalOpen(false)}
      />

      {/* 🩺 Runtime Diagnostics Modal */}
      <DiagnosticsModal isOpen={diagnosticsOpen} onClose={() => setDiagnosticsOpen(false)} />

      {/* ℹ️ About Dialog Modal */}
      <AboutModal isOpen={aboutOpen} onClose={() => setAboutOpen(false)} />

      <footer className="border-t border-gray-800 py-6 text-center text-xs text-gray-500 bg-[#0d1322]/50">
        ShellGuard Runtime v1.0 RC1 • OS Safety Layer & Telemetry Interceptor • Production Quality
      </footer>
    </div>
  );
}
