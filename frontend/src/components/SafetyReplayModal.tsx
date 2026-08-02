"use client";

import React, { useState, useEffect } from "react";
import { SafetyReplayStep, getSafetyReplay } from "@/lib/api";
import { Play, CheckCircle2, AlertTriangle, XCircle, RotateCcw, X, Film } from "lucide-react";

interface SafetyReplayModalProps {
  command: string;
  isOpen: boolean;
  onClose: () => void;
}

export const SafetyReplayModal: React.FC<SafetyReplayModalProps> = ({ command, isOpen, onClose }) => {
  const [steps, setSteps] = useState<SafetyReplayStep[]>([]);
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen && command) {
      getSafetyReplay(command).then((res) => {
        setSteps(res);
        setActiveStep(0);
        setIsPlaying(true);
      });
    }
  }, [isOpen, command]);

  useEffect(() => {
    if (isPlaying && activeStep < steps.length - 1) {
      const timer = setTimeout(() => setActiveStep((prev) => prev + 1), 1200);
      return () => clearTimeout(timer);
    } else if (activeStep === steps.length - 1) {
      setIsPlaying(false);
    }
  }, [isPlaying, activeStep, steps]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-gray-800 rounded-2xl max-w-xl w-full p-6 space-y-6 shadow-2xl relative">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-purple-950 border border-purple-800 rounded-xl text-purple-400">
              <Film className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                🎞️ Safety Replay Simulator
              </h3>
              <p className="text-xs text-gray-400">Visualizing execution impact breakdown step-by-step</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-white rounded-lg bg-gray-900 border border-gray-800">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="bg-gray-950 p-3 rounded-xl border border-gray-800 font-mono text-xs text-blue-300">
          Command: <span className="text-white font-bold">{command}</span>
        </div>

        {/* Animated Replay Timeline Steps */}
        <div className="space-y-3">
          {steps.map((st, idx) => {
            const isCurrent = idx === activeStep;
            const isPassed = idx < activeStep;
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border transition-all duration-300 flex items-start gap-3 ${
                  isCurrent ? "bg-purple-950/40 border-purple-500 scale-[1.02]" :
                  isPassed ? "bg-gray-900/60 border-gray-800 opacity-80" : "bg-gray-950/40 border-gray-900 opacity-40"
                }`}
              >
                <div className="p-1.5 rounded-lg bg-gray-900 font-mono text-xs font-bold text-gray-300">
                  #{st.step_number}
                </div>
                <div className="space-y-0.5 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{st.title}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      st.status === "DANGER" ? "bg-red-950 text-red-400 border border-red-800" :
                      st.status === "WARN" ? "bg-amber-950 text-amber-400 border border-amber-800" : "bg-emerald-950 text-emerald-400 border border-emerald-800"
                    }`}>
                      {st.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-300">{st.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Replay Controls */}
        <div className="flex items-center justify-between border-t border-gray-800 pt-4">
          <button
            onClick={() => {
              setActiveStep(0);
              setIsPlaying(true);
            }}
            className="px-3.5 py-2 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-200 rounded-xl text-xs font-semibold flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Replay Animation
          </button>
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold">
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
