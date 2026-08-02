"use client";

import React, { useState } from "react";
import { ImpactReport, SandboxPreviewResult } from "@/lib/api";
import { AlertTriangle, Clock, ShieldAlert, Cpu, CheckCircle2, X, AlertOctagon, Terminal } from "lucide-react";

interface ImpactReportModalProps {
  report: ImpactReport | null;
  sandboxPreview: SandboxPreviewResult | null;
  isOpen: boolean;
  onClose: () => void;
  onSelectAction: (action: "recovery" | "alternative" | "sandbox_preview" | "override") => void;
}

export const AIImpactReportModal: React.FC<ImpactReportModalProps> = ({
  report,
  digitalTwin,
  isOpen,
  onClose,
  onSelectAction,
}) => {
  const [trustModeOpen, setTrustModeOpen] = useState<boolean>(false);
  const [confirmInput, setConfirmInput] = useState<string>("");

  if (!isOpen || !report) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-gray-800 rounded-2xl max-w-2xl w-full p-6 space-y-6 shadow-2xl relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-red-950/60 border border-red-800/60 rounded-xl text-red-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                📊 IMPACT REPORT
              </h2>
              <p className="text-xs text-gray-400">Predictive Impact Assessment & Evidence Breakdown</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-white rounded-lg bg-gray-900 border border-gray-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Core Qualitative Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Failure Likelihood</span>
            <span className="text-lg font-black text-red-400 mt-1 block uppercase">{report.failure_likelihood}</span>
          </div>
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Estimated Files</span>
            <span className="text-xl font-black text-amber-400 mt-1 block">{report.estimated_files.toLocaleString()}</span>
          </div>
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Recovery Complexity</span>
            <span className="text-sm font-bold text-red-400 mt-1.5 block uppercase">{report.recovery_complexity}</span>
          </div>
          <div className="bg-gray-900/80 border border-gray-800 p-3 rounded-xl">
            <span className="text-[10px] text-gray-400 font-medium block">Sandbox Preview Clone</span>
            <span className="text-xs font-mono font-bold text-purple-400 mt-2 block truncate">
              {sandboxPreview?.sandbox_environment || "Active Clone"}
            </span>
          </div>
        </div>

        {/* 🛑 "Why Was I Interrupted?" Section */}
        {report.interruption_reasons && report.interruption_reasons.length > 0 && (
          <div className="bg-red-950/30 border border-red-800/50 rounded-xl p-3.5 space-y-1.5">
            <span className="text-xs font-bold text-red-400 flex items-center gap-1.5 uppercase tracking-wider">
              <AlertOctagon className="w-4 h-4" /> Why Was I Interrupted?
            </span>
            <ul className="space-y-1 text-xs text-red-200">
              {report.interruption_reasons.map((reason, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 🕵️ Trust Layer Evidence Checkmarks */}
        {report.evidence && report.evidence.length > 0 && (
          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5 space-y-1.5">
            <span className="text-xs font-bold text-gray-300 uppercase tracking-wider block mb-1">
              Evidence Supporting Reasoning:
            </span>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-1 text-xs text-gray-300">
              {report.evidence.map((ev, idx) => (
                <span key={idx} className="font-mono text-[11px] text-blue-300">
                  {ev}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Affected Components Progress Bars */}
        <div className="space-y-2.5">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">Affected Components Breakdown</h4>
          <ComponentBar label="Filesystem Integrity" score={report.affected_components.filesystem} color="bg-red-500" />
          <ComponentBar label="Security & Privilege Exposure" score={report.affected_components.security} color="bg-amber-500" />
          <ComponentBar label="Networking Sockets" score={report.affected_components.networking} color="bg-purple-500" />
          <ComponentBar label="Kernel & Boot Stability" score={report.affected_components.boot} color="bg-blue-500" />
        </div>

        {/* Action Footer */}
        {!trustModeOpen ? (
          <div className="flex flex-wrap items-center justify-between border-t border-gray-800 pt-4 gap-2">
            <button
              onClick={() => setTrustModeOpen(true)}
              className="px-3.5 py-2 bg-red-950/60 hover:bg-red-900/60 border border-red-800/60 text-red-300 rounded-xl text-xs font-bold transition-colors"
            >
              🔐 Run Anyway (Trust Mode)
            </button>

            <div className="flex items-center gap-2">
              <button
                onClick={() => onSelectAction("sandbox_preview")}
                className="px-3.5 py-2 bg-purple-950/60 border border-purple-800/60 hover:bg-purple-900/60 text-purple-300 rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5"
              >
                <Cpu className="w-3.5 h-3.5" /> 🧪 Sandbox Preview
              </button>
              <button
                onClick={() => onSelectAction("alternative")}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" /> Use Safe Rewrite
              </button>
            </div>
          </div>
        ) : (
          /* 🔐 Trust Mode Override Box (Type 'I UNDERSTAND') */
          <div className="bg-red-950/60 border border-red-800 p-4 rounded-xl space-y-3 animate-in fade-in">
            <div className="flex items-center gap-2 text-xs font-bold text-red-300">
              <AlertTriangle className="w-4 h-4 text-red-400" /> Confirm Dangerous Execution (Trust Mode)
            </div>
            <p className="text-xs text-gray-300">
              To bypass safety blocking, type <span className="font-mono text-white font-bold bg-black px-1.5 py-0.5 rounded">I UNDERSTAND</span> below:
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={confirmInput}
                onChange={(e) => setConfirmInput(e.target.value)}
                placeholder="Type I UNDERSTAND"
                className="bg-black text-white font-mono text-xs px-3 py-1.5 rounded-lg border border-red-800 w-full focus:outline-none"
              />
              <button
                disabled={confirmInput.trim() !== "I UNDERSTAND"}
                onClick={() => {
                  onSelectAction("override");
                  setTrustModeOpen(false);
                  onClose();
                }}
                className="px-4 py-1.5 bg-red-600 hover:bg-red-500 disabled:opacity-40 text-white text-xs font-bold rounded-lg whitespace-nowrap"
              >
                Execute
              </button>
              <button
                onClick={() => setTrustModeOpen(false)}
                className="px-3 py-1.5 bg-gray-900 text-gray-300 text-xs rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
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
