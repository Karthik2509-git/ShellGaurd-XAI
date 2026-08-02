"use client";

import React from "react";
import { ShieldAlert, Terminal, Activity, FileText, Cpu } from "lucide-react";

export const Header: React.FC = () => {
  return (
    <header className="border-b border-gray-800 bg-[#0d1322]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            ShellGuard AI
          </h1>
          <p className="text-xs text-gray-400">AI-Based Intent Engine for Safe Linux Command Execution</p>
        </div>
      </div>

      <nav className="flex items-center gap-6">
        <a href="/" className="flex items-center gap-2 text-sm text-blue-400 font-medium hover:text-blue-300 transition-colors">
          <Terminal className="w-4 h-4" /> Live Dashboard
        </a>
        <a href="#graph" className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200 transition-colors">
          <Cpu className="w-4 h-4" /> Blast Radius Graph
        </a>
        <a href="#history" className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200 transition-colors">
          <Activity className="w-4 h-4" /> Audit Telemetry
        </a>
      </nav>

      <div className="flex items-center gap-2">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <span className="text-xs text-emerald-400 font-medium bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-1 rounded-full">
          AI Interceptor Active
        </span>
      </div>
    </header>
  );
};
