"use client";

import React, { useEffect, useState } from "react";
import { getUserSafetyScore } from "@/lib/api";
import { Award, ShieldCheck, Flame } from "lucide-react";

export const SafetyHeatmap: React.FC = () => {
  const [scoreData, setScoreData] = useState<{ score: number; max_score: number; grade: string }>({
    score: 94,
    max_score: 100,
    grade: "Excellent",
  });

  useEffect(() => {
    async function loadScore() {
      try {
        const data = await getUserSafetyScore();
        setScoreData(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadScore();
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* User AI Safety Score Gauge */}
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">User AI Safety Score</span>
          <Award className="w-5 h-5 text-amber-400" />
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-5xl font-black bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
            {scoreData.score}
          </span>
          <span className="text-sm text-gray-400 font-bold">/ 100</span>
          <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-950 text-emerald-400 border border-emerald-800 ml-auto">
            {scoreData.grade}
          </span>
        </div>

        <p className="text-[11px] text-gray-400 leading-relaxed">
          Gamified safety rating based on safe rewrites accepted, low ignored warnings, and preventive backup habits.
        </p>
      </div>

      {/* Terminal Safety Heatmap Widget */}
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 md:col-span-2 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Flame className="w-4 h-4 text-amber-500" /> Terminal Daily Safety Distribution
            </h4>
            <p className="text-[11px] text-gray-400">Analysis distribution across active terminal sessions.</p>
          </div>
          <span className="text-xs font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2.5 py-1 rounded-lg">
            92% Safe Today
          </span>
        </div>

        {/* Multi-Color Segmented Heatmap Bar */}
        <div className="w-full bg-gray-900 h-4 rounded-full overflow-hidden flex border border-gray-800 p-0.5">
          <div className="bg-emerald-500 h-full rounded-l-full" style={{ width: "92%" }} title="Safe Commands: 92%" />
          <div className="bg-amber-500 h-full" style={{ width: "6%" }} title="Caution Commands: 6%" />
          <div className="bg-red-500 h-full rounded-r-full" style={{ width: "2%" }} title="Critical Blocked: 2%" />
        </div>

        <div className="flex items-center justify-between text-xs text-gray-400 pt-1">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> Safe (92%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> Caution (6%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /> Critical (2%)
          </span>
        </div>
      </div>
    </div>
  );
};
