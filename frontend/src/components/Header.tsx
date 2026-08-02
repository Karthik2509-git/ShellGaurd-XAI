"use client";

import React from "react";
import { ShieldCheck, Activity, Cpu, Layers } from "lucide-react";

export const Header: React.FC = () => {
  return (
    <header className="border-b border-gray-800 bg-[#0d1322]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400">
          <ShieldCheck className="w-6 h-6 text-blue-400" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
              ShellGuard Runtime
            </h1>
            <span className="text-[10px] text-blue-400 font-mono bg-blue-950/60 border border-blue-800/60 px-2 py-0.5 rounded-full">
              v2.0 OS Layer
            </span>
          </div>
          <p className="text-[11px] text-gray-400">Powered by ShellGuard AI Engine</p>
        </div>
      </div>

      <nav className="flex items-center gap-6">
        <a href="/" className="flex items-center gap-2 text-xs text-blue-400 font-medium hover:text-blue-300 transition-colors">
          <Layers className="w-4 h-4" /> Control Center
        </a>
        <a href="#timeline" className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-200 transition-colors">
          <Activity className="w-4 h-4" /> Threat Timeline
        </a>
        <a href="#tree" className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-200 transition-colors">
          <Cpu className="w-4 h-4" /> Decision Tree
        </a>
      </nav>

      {/* AI Safety Badge */}
      <div className="flex items-center gap-3 bg-gray-900/90 border border-emerald-800/60 px-3.5 py-1.5 rounded-xl">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <div className="text-left">
          <div className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
            Protected ✓ <span className="text-gray-400 font-normal">| ShellGuard Runtime Active</span>
          </div>
          <div className="text-[10px] text-gray-500 font-mono">Monitoring 3 active terminals</div>
        </div>
      </div>
    </header>
  );
};
