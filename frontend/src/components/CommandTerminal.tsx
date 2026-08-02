"use client";

import React, { useState, useEffect } from "react";
import { Terminal, Send, Sparkles, AlertOctagon, Eye } from "lucide-react";
import { evaluateCommand, translateNaturalLanguage, CommandEvaluationResponse } from "@/lib/api";

interface CommandTerminalProps {
  onEvaluateCommand: (command: string) => void;
  loading: boolean;
}

export const CommandTerminal: React.FC<CommandTerminalProps> = ({ onEvaluateCommand, loading }) => {
  const [commandInput, setCommandInput] = useState<string>("sudo rm -rf /var/log/*");
  const [nlInput, setNlInput] = useState<string>("");
  const [nlTranslating, setNlTranslating] = useState<boolean>(false);
  const [livePreview, setLivePreview] = useState<CommandEvaluationResponse | null>(null);

  // Live As-You-Type Command Estimation without pressing Enter
  useEffect(() => {
    if (!commandInput.trim()) {
      setLivePreview(null);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await evaluateCommand(commandInput.trim());
        setLivePreview(res);
      } catch (err) {
        console.error(err);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [commandInput]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (commandInput.trim()) {
      onEvaluateCommand(commandInput.trim());
    }
  };

  const handleNLSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nlInput.trim()) return;
    setNlTranslating(true);
    try {
      const result = await translateNaturalLanguage(nlInput.trim());
      setCommandInput(result.generated_command);
      onEvaluateCommand(result.generated_command);
    } catch (err) {
      console.error(err);
    } finally {
      setNlTranslating(false);
    }
  };

  const sampleCommands = [
    { label: "sudo rm -rf /var/log/*", risk: "CRITICAL" },
    { label: "chmod -R 777 /etc", risk: "HIGH" },
    { label: "systemctl stop postgresql", risk: "CAUTION" },
    { label: "echo c3VkbyBybSAtcmYgLw== | base64 -d | sh", risk: "CRITICAL" },
    { label: "trash-put notes.txt", risk: "SAFE" },
  ];

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-6">
      {/* Title Bar */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-4">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
          </div>
          <span className="text-xs font-mono text-gray-400 ml-2">bash - shellguard-runtime</span>
        </div>
        <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
          <Eye className="w-3 h-3 animate-pulse" /> Live As-You-Type Estimation Active
        </span>
      </div>

      {/* Terminal Input Form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <label className="text-xs font-bold uppercase tracking-wider text-gray-400 block">
          Enter Linux Command:
        </label>
        <div className="flex items-center bg-gray-950 border border-gray-800 rounded-xl px-4 py-3 focus-within:border-blue-500 transition-colors">
          <span className="text-emerald-400 font-mono text-sm mr-3 select-none">root@linux-dev:~#</span>
          <input
            type="text"
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            placeholder="e.g. sudo rm -rf /var/log/* or chmod 777 /etc"
            className="bg-transparent text-white font-mono text-sm w-full focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="ml-3 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 whitespace-nowrap"
          >
            <Send className="w-3.5 h-3.5" /> Evaluate Intent
          </button>
        </div>
      </form>

      {/* ⚡ Live As-You-Type Command Preview Box */}
      {livePreview && (
        <div className="bg-gray-900/90 border border-gray-800 rounded-xl p-3.5 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-gray-300 flex items-center gap-1.5">
              <Eye className="w-3.5 h-3.5 text-blue-400" /> Live As-You-Type Estimation:
            </span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
              livePreview.risk.threat_level === "CRITICAL" ? "bg-red-950 text-red-400 border-red-800" :
              livePreview.risk.threat_level === "HIGH" ? "bg-orange-950 text-orange-400 border-orange-800" :
              livePreview.risk.threat_level === "CAUTION" ? "bg-yellow-950 text-yellow-400 border-yellow-800" :
              "bg-emerald-950 text-emerald-400 border-emerald-800"
            }`}>
              ● {livePreview.risk.threat_level} THREAT
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
            <div className="bg-gray-950 p-2 rounded border border-gray-800">
              <span className="text-gray-500 block">Intent</span>
              <span className="font-semibold text-gray-200 truncate block">{livePreview.intent.user_intent}</span>
            </div>
            <div className="bg-gray-950 p-2 rounded border border-gray-800">
              <span className="text-gray-500 block">Est. Files Affected</span>
              <span className="font-semibold text-amber-400 block">{livePreview.ai_impact_report?.estimated_files || 0} Files</span>
            </div>
            <div className="bg-gray-950 p-2 rounded border border-gray-800">
              <span className="text-gray-500 block">Est. Repair Time</span>
              <span className="font-semibold text-blue-400 block">{livePreview.ai_impact_report?.estimated_repair_time || "0 mins"}</span>
            </div>
            <div className="bg-gray-950 p-2 rounded border border-gray-800">
              <span className="text-gray-500 block">Undo Capability</span>
              <span className="font-semibold text-emerald-400 block">
                {livePreview.context.recoverability_score > 0.3 ? "Yes (Trash/Git)" : "No (Permanent)"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Quick Test Presets */}
      <div>
        <span className="text-[11px] font-bold text-gray-400 block mb-2 uppercase tracking-wider">Quick Presets:</span>
        <div className="flex flex-wrap gap-2">
          {sampleCommands.map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                setCommandInput(item.label);
                onEvaluateCommand(item.label);
              }}
              className="text-xs font-mono bg-gray-900 hover:bg-gray-800 text-gray-300 px-3 py-1.5 rounded-lg border border-gray-800 transition-colors flex items-center gap-2"
            >
              <span>{item.label}</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 font-bold">{item.risk}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
