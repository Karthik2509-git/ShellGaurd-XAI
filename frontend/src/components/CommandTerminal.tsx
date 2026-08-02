"use client";

import React, { useState } from "react";
import { Terminal, Send, Sparkles, AlertOctagon } from "lucide-react";
import { translateNaturalLanguage } from "@/lib/api";

interface CommandTerminalProps {
  onEvaluateCommand: (command: string) => void;
  loading: boolean;
}

export const CommandTerminal: React.FC<CommandTerminalProps> = ({ onEvaluateCommand, loading }) => {
  const [commandInput, setCommandInput] = useState<string>("sudo rm -rf /var/log/*");
  const [nlInput, setNlInput] = useState<string>("");
  const [nlTranslating, setNlTranslating] = useState<boolean>(false);

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
    { label: "systemctl stop postgresql", risk: "MEDIUM" },
    { label: "echo c3VkbyBybSAtcmYgLw== | base64 -d | sh", risk: "EVASION" },
    { label: "trash-put notes.txt", risk: "SAFE" },
  ];

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-6">
      {/* Terminal Title Bar */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-4">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
          </div>
          <span className="text-xs font-mono text-gray-400 ml-2">bash - shellguard-interceptor</span>
        </div>
        <span className="text-xs text-blue-400 font-mono">PTY Interceptor Listening</span>
      </div>

      {/* Main Terminal Input */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <label className="text-xs font-semibold uppercase tracking-wider text-gray-400 block">
          Enter Linux Command:
        </label>
        <div className="flex items-center bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 focus-within:border-blue-500 transition-colors">
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

      {/* Voice / Natural Language Shell Translation Input */}
      <form onSubmit={handleNLSubmit} className="bg-gray-900/60 border border-gray-800/80 rounded-xl p-4 space-y-2">
        <label className="text-xs font-semibold text-indigo-400 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" /> Voice & Natural Language Shell Assistant:
        </label>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={nlInput}
            onChange={(e) => setNlInput(e.target.value)}
            placeholder="e.g., 'Safely delete docker build cache files older than 7 days'"
            className="bg-gray-950 border border-gray-800 text-xs text-gray-200 rounded-lg px-3 py-2 w-full focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={nlTranslating}
            className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium whitespace-nowrap flex items-center gap-1"
          >
            Translate & Run
          </button>
        </div>
      </form>

      {/* Quick Test Presets */}
      <div>
        <span className="text-[11px] font-medium text-gray-400 block mb-2">Quick Test Attack & Safety Vectors:</span>
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
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">{item.risk}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
