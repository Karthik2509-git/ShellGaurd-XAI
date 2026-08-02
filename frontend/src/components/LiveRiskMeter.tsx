"use client";

import React from "react";
import { AlertTriangle, ShieldCheck, ShieldAlert, Zap } from "lucide-react";
import { CommandEvaluationResponse } from "@/lib/api";

interface LiveRiskMeterProps {
  data: CommandEvaluationResponse | null;
  loading: boolean;
}

export const LiveRiskMeter: React.FC<LiveRiskMeterProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center min-h-[220px] animate-pulse">
        <Zap className="w-8 h-8 text-blue-500 animate-spin mb-3" />
        <p className="text-sm text-gray-400">Evaluating Command Intent & 5-Vector Risk...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center min-h-[220px] text-center">
        <ShieldCheck className="w-10 h-10 text-gray-600 mb-2" />
        <h3 className="text-base font-semibold text-gray-300">Ready for Interception</h3>
        <p className="text-xs text-gray-500 max-w-sm mt-1">
          Type or select a Linux shell command below to analyze user intent, predict blast radius, and compute dynamic risk vectors.
        </p>
      </div>
    );
  }

  const { overall_risk_score, risk_level, vectors, requires_confirmation } = data.risk;

  const getBadgeColor = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      case "HIGH":
        return "bg-amber-500/20 text-amber-400 border-amber-500/40";
      case "MEDIUM":
        return "bg-blue-500/20 text-blue-400 border-blue-500/40";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    }
  };

  const getMeterColor = (score: number) => {
    if (score >= 80) return "from-red-600 to-rose-500";
    if (score >= 60) return "from-amber-600 to-yellow-500";
    if (score >= 35) return "from-blue-600 to-cyan-500";
    return "from-emerald-600 to-teal-500";
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-6">
      {/* Header & Gauge */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Dynamic Risk Score</span>
          <div className="flex items-baseline gap-3 mt-1">
            <span className="text-4xl font-extrabold text-white">{overall_risk_score}</span>
            <span className="text-sm text-gray-400">/ 100</span>
            <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${getBadgeColor(risk_level)}`}>
              {risk_level} IMPACT
            </span>
          </div>
        </div>

        {requires_confirmation ? (
          <div className="flex items-center gap-2 bg-red-950/50 border border-red-800/60 px-3 py-2 rounded-xl text-red-400 text-xs font-medium">
            <AlertTriangle className="w-4 h-4 text-red-400 animate-bounce" />
            Interactive Prompt Required
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-emerald-950/50 border border-emerald-800/60 px-3 py-2 rounded-xl text-emerald-400 text-xs font-medium">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Auto-Execute Safe
          </div>
        )}
      </div>

      {/* Main Bar Meter */}
      <div className="w-full bg-gray-900 h-3.5 rounded-full overflow-hidden p-0.5 border border-gray-800">
        <div
          className={`h-full rounded-full transition-all duration-700 bg-gradient-to-r ${getMeterColor(overall_risk_score)}`}
          style={{ width: `${Math.max(5, overall_risk_score)}%` }}
        />
      </div>

      {/* 5-Vector Breakdown */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">5-Vector Risk Breakdown</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <VectorPill label="Data Loss" score={vectors.data_loss_risk} />
          <VectorPill label="System Stability" score={vectors.system_stability_risk} />
          <VectorPill label="Security Risk" score={vectors.security_escalation_risk} />
          <VectorPill label="Service Downtime" score={vectors.service_downtime_risk} />
          <VectorPill label="Unrecoverability" score={vectors.recoverability_rating} />
        </div>
      </div>
    </div>
  );
};

const VectorPill: React.FC<{ label: string; score: number }> = ({ label, score }) => {
  const getColor = (s: number) => {
    if (s >= 75) return "text-red-400 bg-red-950/40 border-red-800/40";
    if (s >= 50) return "text-amber-400 bg-amber-950/40 border-amber-800/40";
    return "text-emerald-400 bg-emerald-950/40 border-emerald-800/40";
  };

  return (
    <div className={`p-3 rounded-xl border flex flex-col justify-between ${getColor(score)}`}>
      <span className="text-[11px] font-medium text-gray-400 truncate">{label}</span>
      <span className="text-lg font-bold mt-1">{score}</span>
    </div>
  );
};
