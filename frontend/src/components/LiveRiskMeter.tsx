"use client";

import React from "react";
import { AlertTriangle, ShieldCheck, Zap, Lock, Database, Server, RotateCcw, EyeOff } from "lucide-react";
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
        <p className="text-xs text-gray-400">ShellGuard Runtime Evaluating Keystrokes & Adaptive Risk...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center min-h-[220px] text-center">
        <ShieldCheck className="w-10 h-10 text-gray-600 mb-2" />
        <h3 className="text-base font-semibold text-gray-300">ShellGuard Runtime Active</h3>
        <p className="text-xs text-gray-500 max-w-sm mt-1">
          Monitoring terminal activity. Keystrokes and commands are analyzed in real time before execution.
        </p>
      </div>
    );
  }

  const { overall_risk_score, threat_level, risk_confidence, vectors, requires_confirmation } = data.risk;
  const intentConfidence = Math.round(data.intent.confidence_score * 100);
  const riskConfidence = Math.round(risk_confidence * 100);

  // 4-Tier Threat Hierarchy Colors: SAFE (Green), CAUTION (Yellow), HIGH (Orange), CRITICAL (Red)
  const getThreatBadge = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/40";
      case "CAUTION":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/40";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    }
  };

  const getMeterColor = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "from-red-600 to-rose-500";
      case "HIGH":
        return "from-orange-600 to-amber-500";
      case "CAUTION":
        return "from-yellow-500 to-amber-400";
      default:
        return "from-emerald-600 to-teal-500";
    }
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-6">
      {/* Header & Threat Badge */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">Risk Assessment</span>
          <div className="flex items-baseline gap-3 mt-1">
            <span className="text-4xl font-black text-white">
              {overall_risk_score === 0 ? "Minimal" : overall_risk_score}
            </span>
            {overall_risk_score > 0 && <span className="text-sm text-gray-400">/ 100</span>}
            <span className={`text-xs px-3 py-1 rounded-full font-bold border ${getThreatBadge(threat_level)}`}>
              ● {threat_level} THREAT
            </span>
          </div>
        </div>

        {/* AI Confidence Badges */}
        <div className="text-right space-y-1">
          <div className="text-[10px] text-gray-400 bg-gray-900 border border-gray-800 px-2.5 py-1 rounded-lg font-mono">
            Intent Confidence: <span className="text-blue-400 font-bold">{intentConfidence}%</span>
          </div>
          <div className="text-[10px] text-gray-400 bg-gray-900 border border-gray-800 px-2.5 py-1 rounded-lg font-mono">
            Risk Confidence: <span className="text-emerald-400 font-bold">{riskConfidence}%</span>
          </div>
        </div>
      </div>

      {/* Main Bar Meter */}
      <div className="w-full bg-gray-900 h-3.5 rounded-full overflow-hidden p-0.5 border border-gray-800">
        <div
          className={`h-full rounded-full transition-all duration-700 bg-gradient-to-r ${getMeterColor(threat_level)}`}
          style={{ width: `${Math.max(5, overall_risk_score)}%` }}
        />
      </div>

      {/* 5-Category Risk Matrix */}
      <div>
        <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-3">5-Category Risk Matrix</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <VectorTile label="Data Loss" score={vectors.data_loss_risk} icon={<Database className="w-3.5 h-3.5" />} />
          <VectorTile label="Security" score={vectors.security_risk} icon={<Lock className="w-3.5 h-3.5" />} />
          <VectorTile label="Downtime" score={vectors.downtime_risk} icon={<Server className="w-3.5 h-3.5" />} />
          <VectorTile label="Unrecoverable" score={vectors.recoverability_risk} icon={<RotateCcw className="w-3.5 h-3.5" />} />
          <VectorTile label="Privacy" score={vectors.privacy_risk} icon={<EyeOff className="w-3.5 h-3.5" />} />
        </div>
      </div>
    </div>
  );
};

const VectorTile: React.FC<{ label: string; score: number; icon: React.ReactNode }> = ({ label, score, icon }) => {
  const getColor = (s: number) => {
    if (s >= 75) return "text-red-400 bg-red-950/40 border-red-800/40";
    if (s >= 40) return "text-amber-400 bg-amber-950/40 border-amber-800/40";
    return "text-emerald-400 bg-emerald-950/40 border-emerald-800/40";
  };

  return (
    <div className={`p-3 rounded-xl border flex flex-col justify-between ${getColor(score)}`}>
      <div className="flex items-center gap-1 text-[11px] font-medium text-gray-400">
        {icon} <span className="truncate">{label}</span>
      </div>
      <span className="text-lg font-extrabold mt-1">{score}</span>
    </div>
  );
};
