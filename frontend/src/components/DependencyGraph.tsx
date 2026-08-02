"use client";

import React, { useMemo } from "react";
import { ReactFlow, Background, Controls, Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CommandEvaluationResponse } from "@/lib/api";

interface DependencyGraphProps {
  data: CommandEvaluationResponse | null;
}

export const DependencyGraph: React.FC<DependencyGraphProps> = ({ data }) => {
  const { nodes, edges } = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };

    const cmdName = data.metadata.base_command || "command";
    const targets = data.metadata.targets.length > 0 ? data.metadata.targets : ["target"];
    const services = data.context.impacted_services;
    const riskLevel = data.risk.risk_level;

    const n: Node[] = [
      {
        id: "cmd",
        data: { label: `⚡ ${data.metadata.clean_command}` },
        position: { x: 50, y: 150 },
        style: { background: "#1e293b", color: "#38bdf8", border: "1px solid #0284c7", borderRadius: "12px", padding: "10px 14px", fontSize: "12px", fontWeight: "bold" },
      },
    ];

    const e: Edge[] = [];

    // Target Nodes
    targets.forEach((tgt, idx) => {
      const targetId = `target-${idx}`;
      n.push({
        id: targetId,
        data: { label: `📂 ${tgt} (${data.risk.affected_files_count} files)` },
        position: { x: 300, y: 80 + idx * 90 },
        style: { background: "#111827", color: "#f3f4f6", border: "1px solid #374151", borderRadius: "10px", padding: "8px 12px", fontSize: "11px" },
      });
      e.push({ id: `e-cmd-${targetId}`, source: "cmd", target: targetId, animated: true });
    });

    // Service Impact Nodes
    if (services.length > 0) {
      services.forEach((svc, idx) => {
        const svcId = `svc-${idx}`;
        n.push({
          id: svcId,
          data: { label: `⚙️ Service: ${svc}` },
          position: { x: 550, y: 60 + idx * 80 },
          style: { background: "#450a0a", color: "#fca5a5", border: "1px solid #991b1b", borderRadius: "10px", padding: "8px 12px", fontSize: "11px" },
        });
        e.push({ id: `e-tgt-${svcId}`, source: "target-0", target: svcId, animated: true });
      });
    } else {
      n.push({
        id: "svc-none",
        data: { label: "🛡️ No Active Service Impact" },
        position: { x: 550, y: 150 },
        style: { background: "#064e3b", color: "#6ee7b7", border: "1px solid #047857", borderRadius: "10px", padding: "8px 12px", fontSize: "11px" },
      });
      e.push({ id: "e-tgt-none", source: "target-0", target: "svc-none" });
    }

    // Final System Risk Node
    n.push({
      id: "risk-node",
      data: { label: `🚨 Risk: ${data.risk.overall_risk_score}/100 (${riskLevel})` },
      position: { x: 800, y: 150 },
      style: {
        background: riskLevel === "CRITICAL" || riskLevel === "HIGH" ? "#7f1d1d" : "#064e3b",
        color: "#ffffff",
        border: "1px solid #ef4444",
        borderRadius: "12px",
        padding: "10px 14px",
        fontSize: "12px",
        fontWeight: "bold",
      },
    });

    e.push({ id: "e-svc-risk", source: services.length > 0 ? "svc-0" : "svc-none", target: "risk-node" });

    return { nodes: n, edges: e };
  }, [data]);

  if (!data) return null;

  return (
    <div id="graph" className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Predictive Blast Radius Dependency Graph</h3>
          <p className="text-xs text-gray-400">Visual node flow mapping command ➔ filesystem targets ➔ impacted background services ➔ overall system risk level.</p>
        </div>
      </div>

      <div className="h-[280px] w-full rounded-xl border border-gray-800 bg-[#0b0f19] overflow-hidden">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="#1f293d" gap={16} />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
};
