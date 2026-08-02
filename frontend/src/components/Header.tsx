"use client";

import React from "react";
import { ShieldCheck, Activity, Cpu, HardDrive, Shield, Info, Sliders } from "lucide-react";

interface HeaderProps {
  runtimeState?: "Watching" | "Analyzing" | "Warning" | "Blocking" | "Healthy";
  systemTrust?: string;
  onOpenDiagnostics?: () => void;
  onOpenAbout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  runtimeState = "Watching",
  systemTrust = "Verified",
  onOpenDiagnostics,
  onOpenAbout,
}) => {
  const getStateStyle = (st: string) => {
    switch (st) {
      case "Blocking":
        return "bg-red-950/80 text-red-400 border-red-800";
      case "Analyzing":
        return "bg-blue-950/80 text-blue-400 border-blue-800 animate-pulse";
      case "Warning":
        return "bg-amber-950/80 text-amber-400 border-amber-800";
      default:
        return "bg-emerald-950/80 text-emerald-400 border-emerald-800";
    }
  };

  return (
    <header className="border-b border-gray-800 bg-[#0d1322]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400">
            <ShieldCheck className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
                ShellGuard Runtime
              </h1>
              <span className="text-[10px] text-blue-400 font-mono bg-blue-950/60 border border-blue-800/60 px-2 py-0.5 rounded-full">
                v1.0 RC1
              </span>
            </div>
            <p className="text-[11px] text-gray-400">OS Safety Layer & Telemetry Interceptor</p>
          </div>
        </div>

        {/* Commercial Telemetry & Action Buttons */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-4 bg-gray-950/80 border border-gray-800 px-4 py-1.5 rounded-xl text-xs font-mono">
            <div className="flex items-center gap-1.5 text-gray-300">
              <Shield className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-gray-500">Protection:</span> <span className="text-emerald-400 font-bold">Online</span>
            </div>
            <span className="text-gray-700">|</span>
            <div className="text-gray-300">
              <span className="text-gray-500">Mode:</span> <span className="text-blue-400 font-bold">Normal</span>
            </div>
            <span className="text-gray-700">|</span>
            <div className="flex items-center gap-1 text-gray-300">
              <Activity className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-gray-500">Trust:</span> <span className="text-emerald-300 font-bold">{systemTrust}</span>
            </div>
          </div>

          <button
            onClick={onOpenDiagnostics}
            className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Sliders className="w-3.5 h-3.5 text-blue-400" /> Diagnostics
          </button>

          <button
            onClick={onOpenAbout}
            className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Info className="w-3.5 h-3.5 text-purple-400" /> About
          </button>

          {/* Dynamic Runtime State Badge */}
          <div className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-bold ${getStateStyle(runtimeState)}`}>
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
            </span>
            <span>State: {runtimeState}</span>
          </div>
        </div>
      </div>

      {/* Killer Slogan Banner */}
      <div className="text-center text-[11px] text-gray-400 font-medium bg-blue-950/20 border border-blue-900/30 py-1 rounded-lg">
        <span className="text-blue-400 font-bold">"Before Linux executes a command, ShellGuard Runtime understands what the user actually means."</span>
      </div>
    </header>
  );
};
