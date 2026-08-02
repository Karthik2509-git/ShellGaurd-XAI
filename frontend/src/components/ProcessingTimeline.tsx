"use client";

import React from "react";
import { ProcessingLatency } from "@/lib/api";
import { Zap, Clock, ArrowRight, CheckCircle2 } from "lucide-react";

interface ProcessingTimelineProps {
  latency: ProcessingLatency | null;
}

export const ProcessingTimeline: React.FC<ProcessingTimelineProps> = ({ latency }) => {
  if (!latency) return null;

  const steps = [
    { label: "Received", time: `${latency.received_ms}ms`, desc: "Shell Telemetry Ingestion" },
    { label: "AST Parse", time: `${latency.ast_parser_ms}ms`, desc: "bashlex De-obfuscation" },
    { label: "OS Context", time: `${latency.context_collector_ms}ms`, desc: "pathlib & Service Inspection" },
    { label: "Rule Engine & Risk", time: `${latency.adaptive_risk_ms}ms`, desc: "Rule Policy & Risk Matrix" },
    { label: "Explanation Engine", time: `${latency.explanation_ms}ms`, desc: "Dual Rationale Generation" },
  ];

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 space-y-3">
      <div className="flex items-center justify-between border-b border-gray-800 pb-2">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Runtime Processing Latency Timeline
          </span>
        </div>
        <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded-lg flex items-center gap-1">
          <Clock className="w-3 h-3" /> Total Pipeline Latency: {latency.total_ms}ms
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2 overflow-x-auto py-1">
        {steps.map((st, idx) => (
          <React.Fragment key={idx}>
            <div className="bg-gray-900 border border-gray-800 p-2.5 rounded-xl min-w-[130px] space-y-0.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-gray-400 font-semibold">{st.label}</span>
                <span className="text-[10px] font-mono font-bold text-blue-400">{st.time}</span>
              </div>
              <span className="text-[9px] text-gray-500 block truncate">{st.desc}</span>
            </div>

            {idx < steps.length - 1 && (
              <ArrowRight className="w-3.5 h-3.5 text-gray-600 shrink-0" />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
