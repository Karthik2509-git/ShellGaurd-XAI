"use client";

import React, { useState } from "react";
import { ShieldCheck, Activity, PauseCircle, PlayCircle, Sliders, Info, Power, ChevronDown } from "lucide-react";

interface TraySystemBarProps {
  threatLevel?: string;
  onOpenDiagnostics: () => void;
  onOpenAbout: () => void;
}

export const TraySystemBar: React.FC<TraySystemBarProps> = ({
  threatLevel = "SAFE",
  onOpenDiagnostics,
  onOpenAbout,
}) => {
  const [menuOpen, setMenuOpen] = useState<boolean>(false);
  const [paused, setPaused] = useState<boolean>(false);

  const getTrayColor = () => {
    if (paused) return "bg-gray-500 text-gray-300 border-gray-600";
    switch (threatLevel) {
      case "CRITICAL":
        return "bg-red-600 text-white border-red-400 animate-pulse";
      case "HIGH":
        return "bg-orange-500 text-white border-orange-300";
      case "CAUTION":
        return "bg-yellow-500 text-black border-yellow-300";
      default:
        return "bg-emerald-500 text-white border-emerald-300";
    }
  };

  return (
    <div className="relative inline-block">
      {/* System Tray Badge Applet */}
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className={`px-3 py-1.5 rounded-xl border font-mono text-xs font-bold flex items-center gap-2 shadow-lg transition-all ${getTrayColor()}`}
      >
        <ShieldCheck className="w-4 h-4 shrink-0" />
        <span>ShellGuard Tray: {paused ? "Paused" : threatLevel}</span>
        <ChevronDown className="w-3.5 h-3.5 opacity-80" />
      </button>

      {/* Tray Context Menu */}
      {menuOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-[#111827] border border-gray-800 rounded-xl shadow-2xl p-1.5 z-50 text-xs text-gray-200 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="px-3 py-2 border-b border-gray-800 font-bold text-[11px] text-gray-400 uppercase tracking-wider flex items-center justify-between">
            <span>System Tray Applet</span>
            <span className="text-emerald-400 font-mono text-[9px]">v1.0.0-rc2</span>
          </div>

          <div className="py-1 space-y-0.5">
            <button
              onClick={() => {
                setPaused(!paused);
                setMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2 hover:bg-gray-800 rounded-lg flex items-center gap-2 transition-colors text-gray-300"
            >
              {paused ? (
                <>
                  <PlayCircle className="w-4 h-4 text-emerald-400" /> Resume Protection
                </>
              ) : (
                <>
                  <PauseCircle className="w-4 h-4 text-amber-400" /> Pause Protection
                </>
              )}
            </button>

            <button
              onClick={() => {
                onOpenDiagnostics();
                setMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2 hover:bg-gray-800 rounded-lg flex items-center gap-2 transition-colors text-gray-300"
            >
              <Sliders className="w-4 h-4 text-blue-400" /> Diagnostics Matrix
            </button>

            <button
              onClick={() => {
                onOpenAbout();
                setMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2 hover:bg-gray-800 rounded-lg flex items-center gap-2 transition-colors text-gray-300"
            >
              <Info className="w-4 h-4 text-purple-400" /> About ShellGuard
            </button>
          </div>

          <div className="border-t border-gray-800 pt-1 mt-1">
            <button
              onClick={() => setMenuOpen(false)}
              className="w-full text-left px-3 py-1.5 text-red-400 hover:bg-red-950/40 rounded-lg flex items-center gap-2 transition-colors text-[11px] font-semibold"
            >
              <Power className="w-3.5 h-3.5" /> Close Menu
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
