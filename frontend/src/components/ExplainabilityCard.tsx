"use client";

import React, { useState } from "react";
import { CommandEvaluationResponse } from "@/lib/api";
import { Sparkles, HelpCircle, ArrowRight, ShieldCheck, CheckCircle2, RotateCcw } from "lucide-react";

interface ExplainabilityCardProps {
  data: CommandEvaluationResponse | null;
  onApplyAlternative: (cmd: string) => void;
}

export const ExplainabilityCard: React.FC<ExplainabilityCardProps> = ({ data, onApplyAlternative }) => {
  const [viewMode, setViewMode] = useState<"technical" | "eli5">("technical");

  if (!data) return null;

  const { technical_rationale, eli5_rationale, why_dangerous_bullets, safe_alternatives, undo_playbook } = data.explanation;
  const { user_intent, category, intent_mismatch, mismatch_explanation } = data.intent;

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-6">
      {/* Intent & Mode Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <span className="text-xs text-gray-400 font-medium">Inferred Intent:</span>
          <h3 className="text-base font-bold text-white flex items-center gap-2 mt-0.5">
            <Sparkles className="w-4 h-4 text-blue-400" />
            {user_intent}
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-950 text-blue-400 border border-blue-800 font-mono">
              {category}
            </span>
          </h3>
        </div>

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

      {/* Intent Mismatch Alert */}
      {intent_mismatch && (
        <div className="bg-amber-950/40 border border-amber-800/50 rounded-xl p-4 text-xs text-amber-300">
          <span className="font-bold">⚠️ Intent Mismatch Detected: </span>
          {mismatch_explanation || "The target command impacts broader resources than stated operational goal."}
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

      {/* Why Dangerous Bullets */}
      {why_dangerous_bullets && why_dangerous_bullets.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Key Risk Factors & Damage Vectors</h4>
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

      {/* Safe Command Alternatives */}
      {safe_alternatives && safe_alternatives.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-3 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4" /> Recommended Safer Alternatives
          </h4>
          <div className="space-y-3">
            {safe_alternatives.map((alt, idx) => (
              <div key={idx} className="bg-emerald-950/20 border border-emerald-800/40 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="font-mono text-xs text-emerald-300 bg-gray-900 px-3 py-1.5 rounded-lg border border-gray-800 inline-block">
                    {alt.command}
                  </div>
                  <p className="text-xs text-gray-400">{alt.explanation}</p>
                  <span className="text-[10px] text-emerald-400 font-medium bg-emerald-900/40 px-2 py-0.5 rounded">
                    Benefit: {alt.safety_gain}
                  </span>
                </div>

                <button
                  onClick={() => onApplyAlternative(alt.command)}
                  className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-medium transition-colors flex items-center gap-1.5 whitespace-nowrap self-start md:self-auto"
                >
                  <CheckCircle2 className="w-4 h-4" /> Use Alternative
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Undo Playbook */}
      {undo_playbook && (
        <div className="bg-gray-900/50 border border-gray-800/60 rounded-xl p-4 text-xs text-gray-400 flex items-start gap-2.5">
          <RotateCcw className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-gray-300">Remediation Playbook: </span>
            {undo_playbook}
          </div>
        </div>
      )}
    </div>
  );
};
