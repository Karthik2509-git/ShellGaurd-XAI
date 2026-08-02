"use client";

import React, { useState } from "react";
import { CommandEvaluationResponse } from "@/lib/api";
import { Sparkles, HelpCircle, ShieldCheck, CheckCircle2, RotateCcw, BarChart2, HardDrive } from "lucide-react";

interface ExplainabilityCardProps {
  data: CommandEvaluationResponse | null;
  onApplyAlternative: (cmd: string) => void;
  onOpenImpactReport: () => void;
}

export const ExplainabilityCard: React.FC<ExplainabilityCardProps> = ({
  data,
  onApplyAlternative,
  onOpenImpactReport,
}) => {
  const [viewMode, setViewMode] = useState<"technical" | "eli5">("technical");

  if (!data) return null;

  const { technical_rationale, eli5_rationale, why_dangerous_bullets, undo_playbook } = data.explanation;
  const { user_intent, category, intent_mismatch, mismatch_explanation } = data.intent;
  const rewrites = data.ai_command_rewrites;

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-6">
      {/* Intent & Impact Report Trigger */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <span className="text-xs text-gray-400 font-medium">Inferred User Intent:</span>
          <h3 className="text-base font-bold text-white flex items-center gap-2 mt-0.5">
            <Sparkles className="w-4 h-4 text-blue-400" />
            {user_intent}
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-950 text-blue-400 border border-blue-800 font-mono">
              {category}
            </span>
          </h3>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onOpenImpactReport}
            className="px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-1.5"
          >
            <BarChart2 className="w-4 h-4" /> 📊 AI Impact Report
          </button>

          {/* View Mode Toggle */}
          <div className="flex bg-gray-900 p-1 rounded-xl border border-gray-800 text-xs">
            <button
              onClick={() => setViewMode("technical")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                viewMode === "technical" ? "bg-blue-600 text-white" : "text-gray-400 hover:text-gray-200"
              }`}
            >
              Technical Rationale
            </button>
            <button
              onClick={() => setViewMode("eli5")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                viewMode === "eli5" ? "bg-amber-600 text-white" : "text-gray-400 hover:text-gray-200"
              }`}
            >
              <HelpCircle className="w-3.5 h-3.5" /> ELI5 Mode
            </button>
          </div>
        </div>
      </div>

      {/* Intent Mismatch Alert */}
      {intent_mismatch && (
        <div className="bg-amber-950/40 border border-amber-800/50 rounded-xl p-4 text-xs text-amber-300">
          <span className="font-bold">⚠️ Intent Mismatch Warning: </span>
          {mismatch_explanation || "Target command impact exceeds stated user intent."}
        </div>
      )}

      {/* Rationale View */}
      <div className="bg-gray-900/70 border border-gray-800/80 rounded-xl p-4 text-xs leading-relaxed text-gray-300">
        {viewMode === "technical" ? (
          <div>
            <span className="font-semibold text-blue-400 uppercase tracking-wider block mb-1">Technical Rationale:</span>
            {technical_rationale}
          </div>
        ) : (
          <div>
            <span className="font-semibold text-amber-400 uppercase tracking-wider block mb-1">Explain Like I'm 5 (ELI5):</span>
            {eli5_rationale}
          </div>
        )}
      </div>

      {/* ✨ AI Command Rewrites & "Why Rewrite is Better" Educational Rationale */}
      {rewrites && rewrites.length > 0 && (
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-emerald-400" /> ✨ AI Command Safe Rewrites & Educational Rationale
          </h4>
          <div className="space-y-3">
            {rewrites.map((rw, idx) => (
              <div key={idx} className="bg-emerald-950/20 border border-emerald-800/40 rounded-xl p-4 space-y-3">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="font-mono text-xs text-emerald-300 bg-gray-950 px-3 py-1.5 rounded-lg border border-gray-800 font-bold inline-block">
                    {rw.safe_command}
                  </div>
                  <div className="flex items-center gap-2">
                    {rw.backup_command_suggestion && (
                      <button
                        onClick={() => onApplyAlternative(rw.backup_command_suggestion!)}
                        className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-700 text-amber-300 rounded-lg text-xs font-medium transition-colors flex items-center gap-1"
                      >
                        <HardDrive className="w-3.5 h-3.5" /> Backup First
                      </button>
                    )}
                    <button
                      onClick={() => onApplyAlternative(rw.safe_command)}
                      className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-colors flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-4 h-4" /> Apply Rewrite
                    </button>
                  </div>
                </div>

                {/* Why Rewrite is Better Rationale */}
                <div className="bg-gray-900/80 p-3 rounded-lg border border-gray-800 text-xs space-y-1">
                  <span className="font-semibold text-emerald-400 block">Why is this rewrite better?</span>
                  <p className="text-gray-300 leading-relaxed">{rw.why_better_rationale}</p>
                  <span className="text-[10px] text-emerald-300 font-mono inline-block mt-1">
                    Safety Benefit: {rw.safety_gain}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Why Dangerous Bullets */}
      {why_dangerous_bullets && why_dangerous_bullets.length > 0 && (
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Key Damage Vectors</h4>
          <ul className="space-y-2 text-xs">
            {why_dangerous_bullets.map((bullet, idx) => (
              <li key={idx} className="flex items-start gap-2 text-gray-300">
                <span className="text-red-400 font-bold">•</span>
                <span>{bullet}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
