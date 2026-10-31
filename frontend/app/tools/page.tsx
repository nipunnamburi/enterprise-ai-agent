"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { fetchTools, fetchToolAuditLogs, executeToolDirect } from "@/lib/api";
import { ToolInfo, ToolExecutionLog } from "@/types";
import { formatDate } from "@/lib/utils";

export default function ToolsPage() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [auditLogs, setAuditLogs] = useState<ToolExecutionLog[]>([]);
  const [selectedTool, setSelectedTool] = useState<string>("calculator");
  const [toolArgsJson, setToolArgsJson] = useState('{\n  "expression": "2499.00 * 0.85"\n}');
  const [runnerResult, setRunnerResult] = useState<any>(null);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    fetchTools().then(setTools).catch(console.error);
    fetchToolAuditLogs().then(setAuditLogs).catch(console.error);
  }, []);

  const handleToolChange = (toolName: string) => {
    setSelectedTool(toolName);
    if (toolName === "calculator") {
      setToolArgsJson('{\n  "expression": "2499.00 * 0.85"\n}');
    } else if (toolName === "customer_order_lookup") {
      setToolArgsJson('{\n  "order_number": "1024"\n}');
    } else if (toolName === "query_database") {
      setToolArgsJson('{\n  "entity": "sales",\n  "filters": {\n    "quarter": "Q3",\n    "year": 2024\n  },\n  "aggregation": "sum_revenue"\n}');
    } else if (toolName === "search_documents") {
      setToolArgsJson('{\n  "query": "refund policy return conditions",\n  "top_k": 3\n}');
    } else if (toolName === "web_search") {
      setToolArgsJson('{\n  "query": "enterprise saas sla standards",\n  "num_results": 3\n}');
    } else if (toolName === "generate_report") {
      setToolArgsJson('{\n  "title": "Customer Refund Audit",\n  "summary": "Order 1024 eligible for full refund",\n  "recommendation": "Approve refund"\n}');
    } else if (toolName === "deep_research") {
      setToolArgsJson('{\n  "topic": "Enterprise SaaS uptime SLA standards and penalty benchmarks",\n  "depth": 2\n}');
    }
  };

  const handleRunTool = async (e: React.FormEvent) => {
    e.preventDefault();
    setExecuting(true);
    setRunnerResult(null);
    try {
      const parsedArgs = JSON.parse(toolArgsJson);
      const res = await executeToolDirect(selectedTool, parsedArgs);
      setRunnerResult(res);
      fetchToolAuditLogs().then(setAuditLogs);
    } catch (err: any) {
      setRunnerResult({ error: err.message || "Invalid JSON input" });
    } finally {
      setExecuting(false);
    }
  };

  const handleClear = () => {
    setToolArgsJson("{}");
    setRunnerResult(null);
  };

  return (
    <div className="ref-container">
      <div className="flex flex-col items-center mb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 text-xs font-mono mb-3">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Deterministic Execution Engine: {tools.length} Registered Tools
        </div>
        <h2 className="ref-heading">Deterministic Tool Registry & Execution Ledger</h2>
        <p className="text-center text-xs text-slate-400 font-mono max-w-xl">
          AST-Parsed Math Evaluator, Parameterized SQL Database Queries, Entity Graph Lookups, and Chroma RAG
        </p>
      </div>

      {/* Tool Execution Workbench */}
      <div className="bg-[#0b101d]/80 border border-slate-800/80 rounded-xl p-5 mb-8 backdrop-blur-sm shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 font-mono">
            <span className="text-emerald-400">01 //</span> Tool Execution Workbench
          </h3>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 px-2 py-0.5 rounded">
            Sandboxed Runner
          </span>
        </div>

        {/* Quick tool selector pills */}
        <div className="mb-4">
          <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-2">
            Select Tool to Dispatch:
          </label>
          <div className="flex flex-wrap gap-1.5">
            {tools.map((t) => (
              <button
                key={t.name}
                type="button"
                onClick={() => handleToolChange(t.name)}
                className={`text-xs font-mono px-3 py-1.5 rounded-lg border transition-all ${
                  selectedTool === t.name
                    ? "bg-emerald-500/10 border-emerald-500 text-emerald-300 shadow-sm"
                    : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                }`}
              >
                {t.name}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleRunTool} className="space-y-4">
          <div className="ref-form-group">
            <label className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-2">
              <span>Arguments Payload (JSON):</span>
              <span className="text-[11px] font-mono text-slate-500">Parameterized AST input</span>
            </label>
            <textarea
              rows={5}
              value={toolArgsJson}
              onChange={(e) => setToolArgsJson(e.target.value)}
              className="w-full bg-[#070b14] border border-slate-800 text-emerald-300 font-mono text-xs px-4 py-3 rounded-lg focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40 shadow-inner"
              required
            />
          </div>

          <div className="ref-buttons flex items-center gap-2">
            <button
              type="submit"
              disabled={executing}
              className="ref-btn-primary flex items-center gap-2"
            >
              {executing ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                  <span>Executing Tool...</span>
                </>
              ) : (
                <>
                  <span>⚡</span>
                  <span>Execute Tool</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleClear}
              className="ref-btn-secondary"
            >
              Clear Arguments
            </button>
          </div>
        </form>

        {/* Tool Execution Result Box */}
        {runnerResult && (
          <div className="mt-5 pt-4 border-t border-slate-800/80">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-bold text-slate-200 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                Execution Output Result:
              </span>
              {runnerResult.duration_ms && (
                <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-900 px-2 py-0.5 rounded">
                  Latency: {runnerResult.duration_ms}ms
                </span>
              )}
            </div>
            <pre className="overflow-x-auto bg-[#050811] text-emerald-300 border border-slate-800 p-4 rounded-xl text-xs font-mono max-h-60 shadow-inner">
              {JSON.stringify(runnerResult, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Registered Tools Grid Cards */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h3 className="ref-subheading mb-0">Registered Tool Capabilities ({tools.length})</h3>
          <span className="text-xs font-mono text-slate-400">Deterministic AST-safe execution</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {tools.map((t) => (
            <div
              key={t.name}
              className="p-3.5 rounded-xl bg-[#0b101d]/60 border border-slate-800/80 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono text-xs font-bold text-emerald-400">{t.name}</span>
                <span className="uppercase font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-300">
                  {t.category}
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">{t.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tool Execution Audit Log Table */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h3 className="ref-subheading mb-0">Tool Execution Audit Log Records ({auditLogs.length})</h3>
          <span className="text-xs font-mono text-slate-400">SQLite Audit Ledger</span>
        </div>
        <table className="ref-table">
          <thead>
            <tr>
              <th style={{ width: "20%" }}>Tool Name</th>
              <th style={{ width: "12%" }}>Status</th>
              <th style={{ width: "15%" }}>Latency</th>
              <th style={{ width: "35%" }}>Arguments Passed</th>
              <th style={{ width: "18%" }}>Execution Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {auditLogs.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-6 text-slate-500 font-mono text-xs">
                  No tool execution logs recorded yet.
                </td>
              </tr>
            ) : (
              auditLogs.map((log) => (
                <tr key={log.id}>
                  <td>
                    <b className="font-mono text-xs text-emerald-400">{log.tool_name}</b>
                  </td>
                  <td>
                    <span className="text-emerald-400 font-mono text-xs font-bold flex items-center gap-1">
                      <span>✓</span> {log.status}
                    </span>
                  </td>
                  <td className="font-mono text-xs font-bold text-slate-300">{log.duration_ms} ms</td>
                  <td className="font-mono text-[11px] text-slate-400 truncate max-w-xs">
                    {JSON.stringify(log.arguments)}
                  </td>
                  <td className="font-mono text-xs text-slate-400">{formatDate(log.created_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Navigation Links */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-800">
        <Link href="/">Back to Dashboard</Link> | 
        <Link href="/chat">Open Agent Workspace</Link> | 
        <Link href="/documents">Knowledge Base Documents</Link> | 
        <Link href="/memory">Persistent Memories</Link>
      </div>
    </div>
  );
}
