"use client";

import React, { useEffect, useState } from "react";
import { ShieldCheck, Activity, Cpu } from "lucide-react";

export const StartupSplash: React.FC = () => {
  const [visible, setVisible] = useState<boolean>(true);
  const [step, setStep] = useState<string>("Initializing Runtime...");

  useEffect(() => {
    const t1 = setTimeout(() => setStep("Loading Policies & Rule Engine..."), 500);
    const t2 = setTimeout(() => setStep("Connecting Shell Telemetry Interceptor..."), 1000);
    const t3 = setTimeout(() => setStep("Protection Online"), 1500);
    const t4 = setTimeout(() => setVisible(false), 2200);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
    };
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed top-20 right-6 z-50 bg-[#111827] border border-blue-800/80 rounded-2xl p-4 shadow-2xl flex items-center gap-3 animate-in slide-in-from-right duration-300">
      <div className="p-2.5 bg-blue-950 border border-blue-700 rounded-xl text-blue-400">
        <ShieldCheck className="w-6 h-6 animate-pulse" />
      </div>
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-white">ShellGuard Runtime</span>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 font-mono border border-blue-800">
            v1.0 RC1
          </span>
        </div>
        <p className="text-[11px] font-mono text-emerald-400 mt-0.5">{step}</p>
      </div>
    </div>
  );
};
