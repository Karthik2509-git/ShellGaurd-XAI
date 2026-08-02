"use client";

import React from "react";
import { DecisionTreeNode } from "@/lib/api";
import { ArrowRight, CheckCircle, AlertTriangle, XCircle, GitCommit } from "lucide-react";

interface AIDecisionTreeProps {
  nodes: DecisionTreeNode[];
}

export const AIDecisionTree: React.FC<AIDecisionTreeProps> = ({ nodes }) => {
  if (!nodes || nodes.length === 0) return null;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "PASS":
        return <span className="flex items-center gap-1 text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded text-[10px] font-bold"><CheckCircle className="w-3 h-3" /> PASS</span>;
      case "WARN":
        return <span className="flex items-center gap-1 text-amber-400 bg-amber-950/60 border border-amber-800 px-2 py-0.5 rounded text-[10px] font-bold"><AlertTriangle className="w-3 h-3" /> WARN</span>;
      default:
        return <span className="flex items-center gap-1 text-red-400 bg-red-950/60 border border-red-800 px-2 py-0.5 rounded text-[10px] font-bold"><XCircle className="w-3 h-3" /> BLOCK</span>;
    }
  };

  return (
    <div id="tree" className="bg-[#111827] border border-gray-800 rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-gray-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-wider">
            <GitCommit className="w-4 h-4 text-blue-400" /> AI Decision Tree Explainability Engine
          </h3>
          <p className="text-xs text-gray-400">Step-by-step logic path demonstrating why an action passed, warned, or was blocked.</p>
        </div>
      </div>

      {/* Sequential Decision Nodes Flow */}
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto py-2">
        {nodes.map((node, idx) => (
          <React.Fragment key={idx}>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-3 space-y-1 min-w-[170px] shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">{node.step}</span>
                {getStatusBadge(node.status)}
              </div>
              <p className="text-xs font-mono font-medium text-gray-200 truncate">{node.decision}</p>
            </div>

            {idx < nodes.length - 1 && (
              <ArrowRight className="w-4 h-4 text-gray-600 shrink-0" />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
