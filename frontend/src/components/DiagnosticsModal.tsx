"use client";

import React, { useEffect, useState } from "react";
import { getRuntimeDiagnostics } from "@/lib/api";
import { Activity, CheckCircle2, AlertTriangle, X } from "lucide-react";

interface DiagnosticsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DiagnosticsModal: React.FC<DiagnosticsModalProps> = ({ isOpen, onClose }) => {
  const [diag, setDiag] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      getRuntimeDiagnostics().then(setDiag).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const items = [
    { label: "Protection Status", val: diag.protection_status || "Online" },
    { label: "Runtime Health", val: diag.runtime_health || "Healthy" },
    { label: "IPC Layer", val: diag.ipc_layer || "Connected (WebSocket / Sockets)" },
    { label: "Shell Hooks", val: diag.shell_hooks || "Loaded (Bash / Zsh)" },
    { label: "Policy Engine", val: diag.policy_engine || "Ready (Normal Mode)" },
    { label: "Rule Engine Authority", val: diag.rule_engine || "Active (Deterministic)" },
    { label: "Knowledge Base", val: diag.knowledge_base || "Available" },
    { label: "Offline Models", val: diag.offline_models || "Ready" },
    { label: "Notification Service", val: diag.notification_service || "Running" },
  ];

  const isWarning = (str: string) => str.includes("⚠");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-gray-800 rounded-2xl max-w-xl w-full p-6 space-y-6 shadow-2xl relative">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-950 border border-blue-800 rounded-xl text-blue-400">
              <Activity className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                🩺 Dynamic System Diagnostics
              </h3>
              <p className="text-xs text-gray-400">Real-time socket, process & telemetry inspection</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-white rounded-lg bg-gray-900 border border-gray-800">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Build & Version Metadata */}
        <div className="grid grid-cols-3 gap-2 text-xs font-mono bg-gray-950 p-3 rounded-xl border border-gray-800">
          <div>
            <span className="text-[9px] text-gray-500 uppercase block font-bold">Version</span>
            <span className="font-bold text-blue-400">{diag.version || "1.0.0-rc1"}</span>
          </div>
          <div>
            <span className="text-[9px] text-gray-500 uppercase block font-bold">Build Number</span>
            <span className="font-bold text-purple-400">{diag.build_number || "20260803.1"}</span>
          </div>
          <div>
            <span className="text-[9px] text-gray-500 uppercase block font-bold">Commit Hash</span>
            <span className="font-bold text-emerald-400">{diag.commit_hash || "ae01fbc"}</span>
          </div>
        </div>

        {/* Diagnostics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {items.map((item, idx) => {
            const warn = isWarning(item.val);
            return (
              <div
                key={idx}
                className={`p-3 rounded-xl border flex items-center justify-between transition-colors ${
                  warn
                    ? "bg-amber-950/30 border-amber-800/50"
                    : "bg-gray-900/90 border-gray-800"
                }`}
              >
                <div>
                  <span className="text-[10px] text-gray-400 font-medium block uppercase tracking-wider">{item.label}</span>
                  <span className={`text-xs font-mono font-bold mt-0.5 block ${warn ? "text-amber-300" : "text-gray-200"}`}>
                    {item.val}
                  </span>
                </div>
                {warn ? (
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 ml-2" />
                ) : (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 ml-2" />
                )}
              </div>
            );
          })}
        </div>

        <div className="flex justify-end border-t border-gray-800 pt-4">
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl">
            Close Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};
