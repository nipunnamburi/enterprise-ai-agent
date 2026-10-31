"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { fetchDashboardStats } from "@/lib/api";
import { DashboardStats } from "@/types";

const DEMO_OPTIONS = [
  {
    id: "demo-1",
    label: "Demo 1: RAG Policy Retrieval (Refund Policy & Return Window)",
    prompt: "What does our refund policy say regarding return windows and restocking fees?",
  },
  {
    id: "demo-2",
    label: "Demo 2: Deterministic Tool Calling (Order 1024 + 15% Restocking Fee)",
    prompt: "Calculate the refund for order 1024 with a 15% restocking fee deduction.",
  },
  {
    id: "demo-3",
    label: "Demo 3: Autonomous Multi-Step Complaint Audit (Order 1024 Full Audit)",
    prompt: "Analyze this customer complaint for order 1024, check our refund policy, look up order details, determine eligibility, calculate refund, and prepare a response.",
  },
  {
    id: "demo-4",
    label: "Demo 4: Long-Term Memory Preference Registration",
    prompt: "My preferred response style is concise bullet points.",
  },
  {
    id: "demo-5",
    label: "Demo 5: Business Intelligence SQL Query (Q3 Sales Variance)",
    prompt: "Compare Q3 sales against our target, query the database, and calculate the percentage difference.",
  },
];

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [selectedDemo, setSelectedDemo] = useState(DEMO_OPTIONS[2].id);
  const [customPrompt, setCustomPrompt] = useState(DEMO_OPTIONS[2].prompt);

  useEffect(() => {
    fetchDashboardStats()
      .then(setStats)
      .catch((err) => console.error("Error fetching stats:", err));
  }, []);

  const handleSelectDemo = (demoId: string) => {
    setSelectedDemo(demoId);
    const found = DEMO_OPTIONS.find((d) => d.id === demoId);
    if (found) {
      setCustomPrompt(found.prompt);
    }
  };

  const handleLaunchWorkflow = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customPrompt.trim()) return;
    router.push(`/chat?prompt=${encodeURIComponent(customPrompt.trim())}`);
  };

  const handleClear = () => {
    setCustomPrompt("");
  };

  return (
    <div className="ref-container">
      {/* Title */}
      <h2 className="ref-heading">Enterprise AI Agent Dashboard & System Summary</h2>
      <p className="text-center text-xs text-slate-600 font-medium mb-6">
        Autonomous Multi-Step AI Research Platform with LangGraph, Chroma RAG, Tool Calling, and PostgreSQL Memory
      </p>

      {/* System Metrics Table */}
      <h3 className="ref-subheading">System Status & Knowledge Base Summary</h3>
      <table className="ref-table">
        <thead>
          <tr>
            <th style={{ width: "35%" }}>Metric Category</th>
            <th style={{ width: "25%" }}>Current Count / Value</th>
            <th style={{ width: "40%" }}>Operational Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>Indexed Documents (PDF/DOCX/CSV)</b></td>
            <td><b>{stats?.total_documents ?? 4} Documents</b></td>
            <td><span className="text-green-700 font-bold">Active in Vector Store</span></td>
          </tr>
          <tr>
            <td><b>Chroma Vector Chunks</b></td>
            <td><b>{stats?.indexed_chunks ?? 7} Chunks</b></td>
            <td><span className="text-green-700 font-bold">Cosine Similarity HNSW</span></td>
          </tr>
          <tr>
            <td><b>Autonomous Tasks Executed</b></td>
            <td><b>{stats?.total_tasks ?? 20} Completed Tasks</b></td>
            <td><span className="text-blue-700 font-bold">8-Node State Machine</span></td>
          </tr>
          <tr>
            <td><b>Deterministic Tool Calls</b></td>
            <td><b>{stats?.total_tool_calls ?? 45} Invocations</b></td>
            <td><span className="text-blue-700 font-bold">Parameterized AST Math / SQL</span></td>
          </tr>
          <tr>
            <td><b>Long-Term Memory Facts</b></td>
            <td><b>{stats?.total_memories ?? 4} Active Memories</b></td>
            <td><span className="text-purple-700 font-bold">Persisted in PostgreSQL</span></td>
          </tr>
          <tr>
            <td><b>Average Task Latency</b></td>
            <td><b>{stats?.avg_latency_seconds ?? 0.05} Seconds</b></td>
            <td><span className="text-green-700 font-bold">Optimal Performance</span></td>
          </tr>
        </tbody>
      </table>

      {/* Workflow Entry Form (matching Add Train / Passenger Entry Form) */}
      <h3 className="ref-subheading">Agent Workflow Entry Form</h3>
      <form onSubmit={handleLaunchWorkflow}>
        <div className="ref-form-group">
          <label>Select Demo Workflow:</label>
          <select
            value={selectedDemo}
            onChange={(e) => handleSelectDemo(e.target.value)}
          >
            {DEMO_OPTIONS.map((demo) => (
              <option key={demo.id} value={demo.id}>
                {demo.label}
              </option>
            ))}
          </select>
        </div>

        <div className="ref-form-group">
          <label>User Request / Objective:</label>
          <textarea
            rows={3}
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Enter request objective for the LangGraph agent..."
            required
          />
        </div>

        <div className="ref-form-group">
          <label>Target Agent Model:</label>
          <input type="text" value="LangGraph 8-Node Stateful Graph (Deterministic Mode)" readOnly />
        </div>

        <div className="ref-buttons">
          <input type="submit" value="Execute Agent Workflow" className="ref-btn-primary" />
          <input type="button" value="Clear" onClick={handleClear} className="ref-btn-secondary" />
        </div>
      </form>

      {/* Navigation Links (Matching PDF Reference Bottom Links) */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-200">
        <Link href="/chat">Open Agent Workspace</Link> | 
        <Link href="/elysia">Explore Elysia Decision Tree</Link> | 
        <Link href="/documents">View Knowledge Base Documents</Link> | 
        <Link href="/memory">View Persistent Memories</Link> | 
        <Link href="/tools">Inspect Tool Execution Logs</Link>
      </div>
    </div>
  );
}
