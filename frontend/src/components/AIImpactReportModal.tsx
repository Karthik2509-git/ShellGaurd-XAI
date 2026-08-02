"use client";

import React from "react";
import { AIImpactReport } from "@/lib/api";
import { AlertTriangle, Clock, ShieldAlert, Cpu, CheckCircle2, X } from "lucide-react";

interface AIImpactReportModalProps {
  report: AIImpactReport | null;
  isOpen: boolean;
  onClose: () => void;
  onSelectAction: (action: "recovery" | "alternative" | "simulation" | "docs") => void;
}

export const AIImpactReportModal: React.FC<AIImpactReportModalProps> = ({
  report,
  isOpen,
  onClose,
  onSelectAction,
}) => {
  if (!isOpen || !report) return null;

  const failPercent = Math.round(report.failure_probability * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-gray-800 rounded-2xl max-w-2xl w-full p-6 space-y-6 shadow-2xl relative overflow-hidden">
        {/* Top Header */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-red-950/60 border border-red-800/60 rounded-xl text-red-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                📊 AI IMPACT REPORT
              </h2>
              <p className="text-xs text-gray-400">OS-Level Predictive Damage & Service Exposure Assessment</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-white rounded-lg bg-gray-900 border border-gray-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Core Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Failure Probability</span>
            <span className="text-2xl font-black text-red-400 mt-1 block">{failPercent}%</span>
          </div>
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Estimated Files</span>
            <span className="text-2xl font-black text-amber-400 mt-1 block">{report.estimated_files.toLocaleString()}</span>
          </div>
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Recovery Difficulty</span>
            <span className="text-sm font-bold text-red-400 mt-2 block uppercase">{report.recovery_difficulty}</span>
          </div>
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Estimated Repair Time</span>
            <span className="text-sm font-bold text-blue-400 mt-2 block flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> {report.estimated_repair_time}
            </span>
          </div>
        </div>

        {/* Critical Services Impact */}
        {report.critical_services && report.critical_services.length > 0 && (
          <div className="bg-red-950/20 border border-red-900/40 rounded-xl p-3.5">
            <span className="text-xs font-semibold text-red-400 block mb-1.5 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" /> Affected Critical Services:
            </span>
            <div className="flex flex-wrap gap-2">
              {report.critical_services.map((svc, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-red-900/40 text-red-200 border border-red-800 font-mono">
                  ⚙️ {svc}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Affected Components Progress Bars */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">Affected Components Breakdown</h4>
          <ComponentBar label="Filesystem Integrity" score={report.affected_components.filesystem} color="bg-red-500" />
          <ComponentBar label="Security & Privilege Exposure" score={report.affected_components.security} color="bg-amber-500" />
          <ComponentBar label="Networking & Active Sockets" score={report.affected_components.networking} color="bg-purple-500" />
          <ComponentBar label="Boot & Kernel Stability" score={report.affected_components.boot} color="bg-blue-500" />
        </div>

        {/* Action Buttons Footer */}
        <div className="flex flex-wrap items-center justify-end gap-2 border-t border-gray-800 pt-4">
          <button
            onClick={() => onSelectAction("recovery")}
            className="px-3.5 py-2 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-200 rounded-xl text-xs font-semibold transition-colors"
          >
            🔄 Recovery Guide
          </button>
          <button
            onClick={() => onSelectAction("simulation")}
            className="px-3.5 py-2 bg-blue-950/60 border border-blue-800/60 hover:bg-blue-900/60 text-blue-300 rounded-xl text-xs font-semibold transition-colors"
          >
            🧪 Simulation Mode
          </button>
          <button
            onClick={() => onSelectAction("alternative")}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5"
          >
            <CheckCircle2 className="w-4 h-4" /> Use Safe Alternative
          </button>
        </div>
      </div>
    </div>
  );
};

const ComponentBar: React.FC<{ label: string; score: number; color: string }> = ({ label, score, color }) => (
  <div className="space-y-1">
    <div className="flex justify-between text-xs">
      <span className="text-gray-300 font-medium">{label}</span>
      <span className="text-gray-400 font-mono">{score}%</span>
    </div>
    <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden border border-gray-800">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.max(4, score)}%` }} />
    </div>
  </div>
);
