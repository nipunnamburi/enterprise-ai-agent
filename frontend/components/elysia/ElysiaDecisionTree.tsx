"use client";

import React, { useState } from "react";
import { 
  GitBranch, 
  CheckCircle2, 
  Clock, 
  Search, 
  Calculator, 
  Database, 
  ShieldCheck, 
  FileText, 
  ChevronRight, 
  Zap, 
  Cpu, 
  AlertCircle 
} from "lucide-react";
import { ExecutionStepInfo } from "@/types";

interface ElysiaDecisionTreeProps {
  steps: ExecutionStepInfo[];
  totalDurationMs?: number | null;
  taskObjective?: string;
  confidence?: string;
}

export default function ElysiaDecisionTree({
  steps,
  totalDurationMs,
  taskObjective,
  confidence = "high"
}: ElysiaDecisionTreeProps) {
  const [selectedStepIndex, setSelectedStepIndex] = useState<number>(steps.length ? steps.length - 1 : 0);

  if (!steps || steps.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-50 border border-dashed border-slate-300 rounded-lg">
        <GitBranch className="w-10 h-10 text-slate-400 mx-auto mb-2 animate-pulse" />
        <p className="text-sm font-semibold text-slate-700">Elysia Decision Tree Awaiting Task</p>
        <p className="text-xs text-slate-500 mt-1">
          Execute a query in chat or select a demo to visualize the agent's hierarchical reasoning branches and tool activations.
        </p>
      </div>
    );
  }

  const getNodeIcon = (stepName: string) => {
    switch (stepName) {
      case "analyze_request":
        return <ShieldCheck className="w-4 h-4 text-emerald-600" />;
      case "create_plan":
        return <Cpu className="w-4 h-4 text-blue-600" />;
      case "retrieve_context":
        return <Search className="w-4 h-4 text-purple-600" />;
      case "select_tools":
        return <GitBranch className="w-4 h-4 text-indigo-600" />;
      case "execute_tools":
        return <Zap className="w-4 h-4 text-amber-600" />;
      case "evaluate_progress":
        return <CheckCircle2 className="w-4 h-4 text-cyan-600" />;
      case "generate_response":
        return <FileText className="w-4 h-4 text-emerald-600" />;
      default:
        return <Clock className="w-4 h-4 text-slate-500" />;
    }
  };

  const getElysiaBadge = (stepName: string) => {
    switch (stepName) {
      case "analyze_request":
        return { label: "STATUS / COMPLIANCE", color: "bg-emerald-100 text-emerald-800 border-emerald-300" };
      case "create_plan":
        return { label: "ATLAS / REASONING", color: "bg-blue-100 text-blue-800 border-blue-300" };
      case "retrieve_context":
        return { label: "RETRIEVAL", color: "bg-purple-100 text-purple-800 border-purple-300" };
      case "select_tools":
        return { label: "DECISION", color: "bg-indigo-100 text-indigo-800 border-indigo-300" };
      case "execute_tools":
        return { label: "TOOL / EXECUTE", color: "bg-amber-100 text-amber-800 border-amber-300" };
      case "evaluate_progress":
        return { label: "EVALUATE", color: "bg-cyan-100 text-cyan-800 border-cyan-300" };
      case "generate_response":
        return { label: "COMPLETED / SYNTHESIS", color: "bg-emerald-100 text-emerald-800 border-emerald-300" };
      default:
        return { label: "UPDATE", color: "bg-slate-100 text-slate-800 border-slate-300" };
    }
  };

  const activeStep = steps[selectedStepIndex] || steps[0];
  const activeBadge = getElysiaBadge(activeStep.step_name);

  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden flex flex-col">
      {/* Header bar */}
      <div className="bg-gradient-to-r from-slate-900 to-[#1e3a8a] text-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitBranch className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold uppercase tracking-wider">Elysia Agent Decision Tree</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono">
          {totalDurationMs !== undefined && totalDurationMs !== null && (
            <span className="bg-white/10 px-2 py-0.5 rounded text-emerald-300">
              {totalDurationMs.toFixed(1)}ms total
            </span>
          )}
          <span className="bg-white/10 px-2 py-0.5 rounded capitalize text-cyan-300">
            {confidence} confidence
          </span>
        </div>
      </div>

      {/* Main split: Tree view on left, Node details on right */}
      <div className="grid grid-cols-1 md:grid-cols-12 divide-y md:divide-y-0 md:divide-x divide-slate-200">
        {/* Left Column: Visual Decision Tree Nodes */}
        <div className="md:col-span-6 p-3 bg-slate-50/70 overflow-y-auto max-h-[460px] space-y-2">
          <p className="text-[10px] font-bold uppercase text-slate-400 tracking-wider px-1">
            Execution Trajectory ({steps.length} Nodes)
          </p>

          <div className="relative pl-4 space-y-2.5 before:absolute before:left-2 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-300">
            {steps.map((step, idx) => {
              const isSelected = selectedStepIndex === idx;
              const badge = getElysiaBadge(step.step_name);
              const icon = getNodeIcon(step.step_name);

              return (
                <div
                  key={idx}
                  onClick={() => setSelectedStepIndex(idx)}
                  className={`relative cursor-pointer transition-all rounded-md p-2.5 border text-left flex items-start gap-2.5 ${
                    isSelected
                      ? "bg-white border-[#1e3a8a] shadow-sm ring-1 ring-[#1e3a8a]/20"
                      : "bg-white/80 hover:bg-white border-slate-200 hover:border-slate-300 text-slate-600"
                  }`}
                >
                  {/* Tree node bullet icon */}
                  <div
                    className={`mt-0.5 p-1 rounded-md border flex-shrink-0 ${
                      isSelected ? "bg-[#1e3a8a]/10 border-[#1e3a8a]/30" : "bg-slate-100 border-slate-200"
                    }`}
                  >
                    {icon}
                  </div>

                  {/* Node label and metadata */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className={`text-xs font-bold truncate ${isSelected ? "text-[#1e3a8a]" : "text-slate-800"}`}>
                        {step.step_name.replace(/_/g, " ").toUpperCase()}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500 font-medium">
                        {step.duration_ms.toFixed(1)}ms
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded border ${badge.color}`}>
                        {badge.label}
                      </span>
                      <span className="text-[10px] text-slate-500 truncate max-w-[150px]">
                        {step.description}
                      </span>
                    </div>
                  </div>

                  <ChevronRight
                    className={`w-4 h-4 flex-shrink-0 mt-1 transition-transform ${
                      isSelected ? "text-[#1e3a8a] translate-x-0.5" : "text-slate-300"
                    }`}
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Elysia Node State Inspector */}
        <div className="md:col-span-6 p-4 flex flex-col justify-between bg-white overflow-y-auto max-h-[460px]">
          <div>
            {/* Header info */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-3">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-slate-800 capitalize">
                    {activeStep.step_name.replace(/_/g, " ")}
                  </h4>
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${activeBadge.color}`}>
                    {activeBadge.label}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 font-medium mt-0.5">
                  Node Index #{selectedStepIndex + 1} of {steps.length} in Decision Tree
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs font-mono font-bold text-slate-700 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                  {activeStep.duration_ms.toFixed(2)} ms
                </span>
              </div>
            </div>

            {/* Description */}
            <div className="mb-3">
              <label className="text-[10px] font-bold uppercase text-slate-400 block mb-1">
                Elysia Reasoning & Action Description
              </label>
              <div className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200 leading-relaxed font-sans">
                {activeStep.description}
              </div>
            </div>

            {/* Structured Details / Payload */}
            {activeStep.details && Object.keys(activeStep.details).length > 0 && (
              <div>
                <label className="text-[10px] font-bold uppercase text-slate-400 block mb-1">
                  Atlas Context & State Payload
                </label>
                <div className="bg-slate-900 text-slate-100 p-2.5 rounded text-[11px] font-mono overflow-x-auto max-h-[190px] border border-slate-800">
                  <pre>{JSON.stringify(activeStep.details, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>

          {/* Footer badge */}
          <div className="pt-3 border-t border-slate-100 mt-3 flex items-center justify-between text-[11px] text-slate-400">
            <span>Verified by Elysia Agent Runtime</span>
            <span className="font-mono text-emerald-600 font-semibold">Status: 200 OK</span>
          </div>
        </div>
      </div>
    </div>
  );
}

