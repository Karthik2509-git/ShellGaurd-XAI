"use client";

import React from "react";
import { ShieldCheck, X } from "lucide-react";

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-gray-800 rounded-2xl max-w-lg w-full p-6 space-y-6 shadow-2xl relative">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400">
              <ShieldCheck className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-white flex items-center gap-2">
                About ShellGuard Runtime
              </h3>
              <p className="text-xs text-gray-400">v1.0.0-rc1 • Canonical OS Safety Layer</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-white rounded-lg bg-gray-900 border border-gray-800">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4 text-xs text-gray-300">
          <div className="bg-blue-950/20 border border-blue-900/40 p-3.5 rounded-xl font-medium text-blue-300 italic">
            "Before Linux executes a command, ShellGuard Runtime understands what the user actually means."
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-gray-900 p-2.5 rounded-xl border border-gray-800">
              <span className="text-[10px] text-gray-500 uppercase block font-bold">Semantic Version</span>
              <span className="font-mono font-bold text-white">v1.0.0-rc1</span>
            </div>
            <div className="bg-gray-900 p-2.5 rounded-xl border border-gray-800">
              <span className="text-[10px] text-gray-500 uppercase block font-bold">Build Number</span>
              <span className="font-mono font-bold text-purple-300">20260803.1</span>
            </div>
            <div className="bg-gray-900 p-2.5 rounded-xl border border-gray-800">
              <span className="text-[10px] text-gray-500 uppercase block font-bold">Commit Hash</span>
              <span className="font-mono font-bold text-emerald-300">ae01fbc</span>
            </div>
            <div className="bg-gray-900 p-2.5 rounded-xl border border-gray-800">
              <span className="text-[10px] text-gray-500 uppercase block font-bold">Release Channel</span>
              <span className="font-mono font-bold text-blue-300">stable-rc</span>
            </div>
          </div>

          <div className="bg-gray-950 p-3 rounded-xl border border-gray-800 space-y-1">
            <span className="font-bold text-gray-200 block">Engineering Philosophy:</span>
            <p className="text-[11px] text-gray-400">
              Deterministic Rule Engine Authority • Dynamic Health Inspections • Real Shell Hooks • Privacy First.
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-gray-800 pt-4">
          <span className="text-[11px] text-gray-500 font-mono">License: MIT • Canonical Quality</span>
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
