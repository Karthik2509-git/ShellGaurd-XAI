"use client";

import React, { useState } from "react";
import { CommandEvaluationResponse } from "@/lib/api";
import { ShieldAlert, ShieldCheck, AlertTriangle, Sparkles, X, ChevronUp, ChevronDown, CheckCircle2, BarChart2 } from "lucide-react";

interface FloatingAssistantProps {
  data: CommandEvaluationResponse | null;
  onOpenImpactReport: () => void;
  onApplyAlternative: (cmd: string) => void;
}

export const FloatingAssistant: React.FC<FloatingAssistantProps> = ({
  data,
  onOpenImpactReport,
  onApplyAlternative,
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);

  const level = data?.risk.threat_level || "SAFE";
  const score = data?.risk.overall_risk_score || 0;

  // 4-Color Shift: Green (Safe), Yellow (Caution), Orange (High), Red (Critical)
  const getShieldStyle = (lvl: string) => {
    switch (lvl) {
      case "CRITICAL":
        return "bg-red-600 border-red-400 text-white shadow-red-500/50 animate-pulse";
      case "HIGH":
        return "bg-orange-500 border-orange-300 text-white shadow-orange-500/50";
      case "CAUTION":
        return "bg-yellow-500 border-yellow-200 text-gray-950 shadow-yellow-500/50";
      default:
        return "bg-emerald-600 border-emerald-400 text-white shadow-emerald-500/50";
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end space-y-2 font-sans select-none">
      {/* Expanded Floating Assistant Panel */}
      {expanded && data && (
        <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 w-80 shadow-2xl space-y-4 text-xs animate-in slide-in-from-bottom duration-200">
          <div className="flex items-center justify-between border-b border-gray-800 pb-3">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white">ShellGuard Runtime</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                level === "CRITICAL" ? "bg-red-950 text-red-400 border-red-800" :
                level === "HIGH" ? "bg-orange-950 text-orange-400 border-orange-800" :
                level === "CAUTION" ? "bg-yellow-950 text-yellow-400 border-yellow-800" :
                "bg-emerald-950 text-emerald-400 border-emerald-800"
              }`}>
                ● {level}
              </span>
            </div>
            <button onClick={() => setExpanded(false)} className="text-gray-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div>
            <span className="text-[10px] text-gray-400 font-bold block uppercase">Command</span>
            <span className="font-mono text-blue-300 font-bold block truncate mt-0.5">{data.metadata.clean_command}</span>
          </div>

          <div>
            <span className="text-[10px] text-gray-400 font-bold block uppercase">Inferred Intent</span>
            <span className="text-gray-200 font-semibold block mt-0.5">{data.intent.user_intent}</span>
          </div>

          {data.ai_command_rewrites && data.ai_command_rewrites.length > 0 && (
            <div className="bg-emerald-950/30 border border-emerald-800/40 p-3 rounded-xl space-y-2">
              <span className="font-bold text-emerald-400 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" /> ✨ Safe Rewrite Available:
              </span>
              <div className="font-mono text-[11px] text-emerald-300 bg-gray-950 p-2 rounded border border-gray-800">
                {data.ai_command_rewrites[0].safe_command}
              </div>
              <button
                onClick={() => {
                  onApplyAlternative(data.ai_command_rewrites[0].safe_command);
                  setExpanded(false);
                }}
                className="w-full py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs transition-colors flex items-center justify-center gap-1"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Apply Rewrite
              </button>
            </div>
          )}

          <div className="pt-1 flex items-center gap-2">
            <button
              onClick={() => {
                onOpenImpactReport();
                setExpanded(false);
              }}
              className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs transition-colors flex items-center justify-center gap-1.5"
            >
              <BarChart2 className="w-4 h-4" /> 📊 AI Impact Report
            </button>
          </div>
        </div>
      )}

      {/* Floating Circular Shield Trigger */}
      <button
        onClick={() => setExpanded(!expanded)}
        className={`p-3.5 rounded-full border-2 shadow-2xl flex items-center justify-center transition-transform hover:scale-110 cursor-pointer ${getShieldStyle(level)}`}
        title={`ShellGuard Runtime Assistant - ${level} (${score}%)`}
      >
        <ShieldCheck className="w-6 h-6" />
      </button>
    </div>
  );
};
