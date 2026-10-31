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
      <h2 className="ref-heading">Deterministic Tool Registry & Execution Audit Records</h2>
      <p className="text-center text-xs text-slate-600 font-medium mb-6">
        AST-Parsed Math Evaluator, Parameterized SQL Database Queries, Entity Graph Lookups, and Chroma RAG
      </p>

      {/* Tool Execution Form */}
      <h3 className="ref-subheading">Tool Execution Entry Form</h3>
      <form onSubmit={handleRunTool}>
        <div className="ref-form-group">
          <label>Select Tool Name:</label>
          <select
            value={selectedTool}
            onChange={(e) => handleToolChange(e.target.value)}
          >
            {tools.map((t) => (
              <option key={t.name} value={t.name}>
                {t.name} ({t.category})
              </option>
            ))}
          </select>
        </div>

        <div className="ref-form-group">
          <label>Tool Arguments (JSON):</label>
          <textarea
            rows={5}
            value={toolArgsJson}
            onChange={(e) => setToolArgsJson(e.target.value)}
            className="font-mono text-xs"
            required
          />
        </div>

        <div className="ref-buttons">
          <input
            type="submit"
            value={executing ? "Executing Tool..." : "Execute Tool"}
            disabled={executing}
            className="ref-btn-primary"
          />
          <input
            type="button"
            value="Clear"
            onClick={handleClear}
            className="ref-btn-secondary"
          />
        </div>
      </form>

      {/* Tool Execution Result Box */}
      {runnerResult && (
        <div className="mt-4 mb-6 p-4 bg-slate-50 border border-slate-300 rounded">
          <h4 className="text-xs font-bold text-[#1e3a8a] mb-2">Tool Execution Output Result:</h4>
          <pre className="overflow-x-auto bg-slate-900 text-emerald-300 p-3 rounded text-xs font-mono max-h-52">
            {JSON.stringify(runnerResult, null, 2)}
          </pre>
        </div>
      )}

      {/* Registered Tools List Table */}
      <h3 className="ref-subheading">Registered Tool Capabilities ({tools.length})</h3>
      <table className="ref-table">
        <thead>
          <tr>
            <th style={{ width: "25%" }}>Tool Name</th>
            <th style={{ width: "18%" }}>Category</th>
            <th style={{ width: "57%" }}>Tool Purpose & Security Constraint</th>
          </tr>
        </thead>
        <tbody>
          {tools.map((t) => (
            <tr key={t.name}>
              <td><b className="font-mono text-[#1e3a8a]">{t.name}</b></td>
              <td className="uppercase font-bold text-xs text-slate-600">{t.category}</td>
              <td className="text-slate-700">{t.description}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Tool Execution Audit Log Table (Page 9 & 10 Style) */}
      <h3 className="ref-subheading">Tool Execution Audit Log Records ({auditLogs.length})</h3>
      <table className="ref-table">
        <thead>
          <tr>
            <th style={{ width: "20%" }}>Tool Name</th>
            <th style={{ width: "12%" }}>Status</th>
            <th style={{ width: "15%" }}>Latency (ms)</th>
            <th style={{ width: "35%" }}>Arguments Passed</th>
            <th style={{ width: "18%" }}>Execution Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {auditLogs.map((log) => (
            <tr key={log.id}>
              <td><b className="font-mono text-[#1e3a8a]">{log.tool_name}</b></td>
              <td><span className="text-green-700 font-bold">&#10004; {log.status}</span></td>
              <td className="font-bold">{log.duration_ms} ms</td>
              <td className="font-mono text-[11px] text-slate-600 truncate max-w-xs">{JSON.stringify(log.arguments)}</td>
              <td>{formatDate(log.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Navigation Links */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-200">
        <Link href="/">Back to Dashboard</Link> | 
        <Link href="/chat">Open Agent Workspace</Link> | 
        <Link href="/documents">View Knowledge Base Documents</Link> | 
        <Link href="/memory">View Persistent Memories</Link>
      </div>
    </div>
  );
}
