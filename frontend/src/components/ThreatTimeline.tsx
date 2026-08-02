"use client";

import React, { useEffect, useState } from "react";
import { ThreatLogEntry, OSEvent, getThreatTimeline, getOSEvents } from "@/lib/api";
import { ShieldCheck, AlertTriangle, XCircle, Clock, ShieldAlert, Cpu } from "lucide-react";

export const ThreatTimeline: React.FC = () => {
  const [timeline, setTimeline] = useState<ThreatLogEntry[]>([]);
  const [osEvents, setOSEvents] = useState<OSEvent[]>([]);
  const [activeTab, setActiveTab] = useState<"commands" | "os_events">("commands");

  useEffect(() => {
    async function loadData() {
      try {
        const [tl, evts] = await Promise.all([getThreatTimeline(), getOSEvents()]);
        setTimeline(tl);
        setOSEvents(evts);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const getThreatBadge = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-400 border border-red-800 flex items-center gap-1"><XCircle className="w-3 h-3" /> CRITICAL</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-400 border border-amber-800 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> HIGH</span>;
      case "CAUTION":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-yellow-950 text-yellow-400 border border-yellow-800 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> CAUTION</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800 flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> SAFE</span>;
    }
  };

  return (
    <div id="timeline" className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-4">
      {/* Header & Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4 text-purple-400" /> CrowdStrike-Style Threat Timeline
          </h3>
          <p className="text-xs text-gray-400">Real-time audit log of terminal executions and OS system events.</p>
        </div>

        <div className="flex bg-gray-900 p-1 rounded-xl border border-gray-800 text-xs">
          <button
            onClick={() => setActiveTab("commands")}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              activeTab === "commands" ? "bg-blue-600 text-white" : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Command Audit Log ({timeline.length})
          </button>
          <button
            onClick={() => setActiveTab("os_events")}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "os_events" ? "bg-purple-600 text-white" : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <Cpu className="w-3.5 h-3.5" /> OS System Events ({osEvents.length})
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="overflow-x-auto">
        {activeTab === "commands" ? (
          <table className="w-full text-left text-xs">
            <thead className="text-gray-400 uppercase text-[10px] bg-gray-900/60 border-b border-gray-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Command</th>
                <th className="py-2.5 px-3">Inferred Intent</th>
                <th className="py-2.5 px-3">Threat Level</th>
                <th className="py-2.5 px-3">Risk Score</th>
                <th className="py-2.5 px-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 text-gray-200">
              {timeline.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-900/40 transition-colors">
                  <td className="py-2.5 px-3 font-mono text-gray-400 flex items-center gap-1.5">
                    <Clock className="w-3 h-3 text-gray-500" /> {entry.timestamp}
                  </td>
                  <td className="py-2.5 px-3 font-mono font-medium text-blue-300">{entry.command}</td>
                  <td className="py-2.5 px-3 text-gray-300">{entry.intent}</td>
                  <td className="py-2.5 px-3">{getThreatBadge(entry.threat_level)}</td>
                  <td className="py-2.5 px-3 font-bold font-mono">{entry.overall_risk_score}/100</td>
                  <td className="py-2.5 px-3 font-bold">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      entry.action_taken === "BLOCKED" ? "bg-red-950 text-red-400" :
                      entry.action_taken === "REWRITTEN" ? "bg-emerald-950 text-emerald-400" : "bg-gray-900 text-gray-400"
                    }`}>
                      {entry.status_icon} {entry.action_taken}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="text-gray-400 uppercase text-[10px] bg-gray-900/60 border-b border-gray-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Event Type</th>
                <th className="py-2.5 px-3">Description</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 text-gray-200">
              {osEvents.map((evt, idx) => (
                <tr key={idx} className="hover:bg-gray-900/40 transition-colors">
                  <td className="py-2.5 px-3 font-mono text-gray-400">{evt.timestamp}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-purple-300">{evt.event_type}</td>
                  <td className="py-2.5 px-3 text-gray-300">{evt.description}</td>
                  <td className="py-2.5 px-3">{getThreatBadge(evt.severity)}</td>
                  <td className="py-2.5 px-3 font-mono text-gray-400">{evt.source_process}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
