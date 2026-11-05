"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  FileText, 
  Database, 
  Cpu, 
  Zap, 
  Brain, 
  Clock, 
  ArrowRight, 
  CheckCircle2, 
  Search
} from "lucide-react";
import { fetchDashboardStats } from "@/lib/api";
import { DashboardStats } from "@/types";

const DEMO_OPTIONS = [
  {
    id: "demo-1",
    label: "Demo 1: RAG Policy Retrieval (Refund Policy & Return Window)",
    prompt: "What does our refund policy say regarding return windows and restocking fees?",
    badge: "Vector RAG",
    dwg: "DWG-01"
  },
  {
    id: "demo-2",
    label: "Demo 2: Deterministic Tool Calling (Order 1024 + 15% Fee)",
    prompt: "Calculate the refund for order 1024 with a 15% restocking fee deduction.",
    badge: "AST Math",
    dwg: "DWG-02"
  },
  {
    id: "demo-3",
    label: "Demo 3: Autonomous Multi-Step Complaint Audit (Order 1024 Full Audit)",
    prompt: "Analyze this customer complaint for order 1024, check our refund policy, look up order details, determine eligibility, calculate refund, and prepare a response.",
    badge: "Full Graph",
    dwg: "DWG-03"
  },
  {
    id: "demo-4",
    label: "Demo 4: Long-Term Memory Preference Registration",
    prompt: "My preferred response style is concise bullet points.",
    badge: "Memory",
    dwg: "DWG-04"
  },
  {
    id: "demo-5",
    label: "Demo 5: Business Intelligence SQL Query (Q3 Sales Variance)",
    prompt: "Compare Q3 sales against our target, query the database, and calculate the percentage difference.",
    badge: "Database",
    dwg: "DWG-05"
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

  return (
    <div className="w-[95%] max-w-[1140px] mx-auto my-5 p-6 md:p-8 bg-[var(--color-paper-2)] border border-[var(--color-rule)] relative blueprint-grid">
      {/* Blueprint Sheet Header Block */}
      <header className="border-b border-[var(--color-rule)] pb-5 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-[var(--color-muted)] mb-2">
          <span>Sheet DWG-AI-001 rev 2.4</span>
          <span>Enterprise state machine</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-semibold uppercase text-[var(--color-ink)]">
          Enterprise AI Agent
        </h1>
        <p className="text-xs text-[var(--color-ink-2)] mt-2 max-w-xl">
          Autonomous execution platform coordinating LangGraph planning, vector retrieval, and deterministic tool calls.
        </p>

        {/* Blueprint Dimension String */}
        <div className="dim-string my-4" />
      </header>

      {/* System Telemetry & Register */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-3 border-b border-[var(--color-rule-2)] pb-1">
          <h2 className="text-sm font-semibold text-[var(--color-ink)]">
            System telemetry and specification register
          </h2>
          <span className="text-xs text-[var(--color-muted)]">Metric matrix</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-0 border-t border-l border-[var(--color-rule)]">
          {/* Metric 1 */}
          <div className="p-4 border-r border-b border-[var(--color-rule)] bg-[var(--color-paper)]">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-2">
              <span>Indexed documents</span>
              <span className="mono-num">DWG-DOC</span>
            </div>
            <div className="text-3xl font-semibold text-[var(--color-ink)] mono-num">
              {stats?.total_documents ?? 4}
            </div>
            <div className="text-[11px] text-[var(--color-ink-2)] mt-1">
              Verified in vector store
            </div>
          </div>

          {/* Metric 2 */}
          <div className="p-4 border-r border-b border-[var(--color-rule)] bg-[var(--color-paper)]">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-2">
              <span>Vector chunks</span>
              <span className="mono-num">DIM-HNSW</span>
            </div>
            <div className="text-3xl font-semibold text-[var(--color-ink)] mono-num">
              {stats?.indexed_chunks ?? 7}
            </div>
            <div className="text-[11px] text-[var(--color-ink-2)] mt-1">
              Cosine similarity index
            </div>
          </div>

          {/* Metric 3 */}
          <div className="p-4 border-r border-b border-[var(--color-rule)] bg-[var(--color-paper)]">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-2">
              <span>Autonomous tasks</span>
              <span className="mono-num">GRAPH-08</span>
            </div>
            <div className="text-3xl font-semibold text-[var(--color-ink)] mono-num">
              {stats?.total_tasks ?? 20}
            </div>
            <div className="text-[11px] text-[var(--color-ink-2)] mt-1">
              8-node state machine
            </div>
          </div>

          {/* Metric 4 */}
          <div className="p-4 border-r border-b border-[var(--color-rule)] bg-[var(--color-paper)]">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-2">
              <span>Tool executions</span>
              <span className="mono-num">AST-CALL</span>
            </div>
            <div className="text-3xl font-semibold text-[var(--color-ink)] mono-num">
              {stats?.total_tool_calls ?? 45}
            </div>
            <div className="text-[11px] text-[var(--color-ink-2)] mt-1">
              Deterministic calculations
            </div>
          </div>

          {/* Metric 5 */}
          <div className="p-4 border-r border-b border-[var(--color-rule)] bg-[var(--color-paper)]">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-2">
              <span>Persisted memories</span>
              <span className="mono-num">MEM-STORE</span>
            </div>
            <div className="text-3xl font-semibold text-[var(--color-ink)] mono-num">
              {stats?.total_memories ?? 4}
            </div>
            <div className="text-[11px] text-[var(--color-ink-2)] mt-1">
              PostgreSQL stored facts
            </div>
          </div>

          {/* Metric 6 */}
          <div className="p-4 border-r border-b border-[var(--color-rule)] bg-[var(--color-paper)]">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-2">
              <span>Execution latency</span>
              <span className="mono-num">SEC/TASK</span>
            </div>
            <div className="text-3xl font-semibold text-[var(--color-ink)] mono-num">
              {stats?.avg_latency_seconds ?? 0.05}s
            </div>
            <div className="text-[11px] text-[var(--color-ink-2)] mt-1">
              Pipeline response time
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Workflow Launcher (Title Block Style) */}
      <section className="mb-8 border border-[var(--color-rule)] p-6 bg-[var(--color-paper)]">
        <div className="flex items-center justify-between border-b border-[var(--color-rule)] pb-2 mb-5">
          <h2 className="text-sm font-semibold text-[var(--color-ink)]">
            Workflow title block and execution specification
          </h2>
          <span className="text-xs text-[var(--color-muted)]">Entry spec 01</span>
        </div>

        <form onSubmit={handleLaunchWorkflow}>
          {/* Preset Selector */}
          <div className="mb-5">
            <label className="text-xs font-medium text-[var(--color-ink)] block mb-2">
              Preset test elevation
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {DEMO_OPTIONS.map((demo) => {
                const isSelected = selectedDemo === demo.id;
                return (
                  <button
                    key={demo.id}
                    type="button"
                    onClick={() => handleSelectDemo(demo.id)}
                    className={`text-left p-3 border text-xs transition-colors flex items-center justify-between gap-2 active:bg-[var(--color-paper-3)] ${
                      isSelected
                        ? "bg-[var(--color-paper-3)] border-[var(--color-ink)] text-[var(--color-ink)]"
                        : "bg-[var(--color-paper-2)] border-[var(--color-rule-2)] text-[var(--color-muted)] hover:border-[var(--color-rule)] hover:text-[var(--color-ink)]"
                    }`}
                  >
                    <span className="truncate">{demo.label}</span>
                    <span className="text-[10px] px-1.5 py-0.5 border border-[var(--color-rule)] text-[var(--color-ink)] flex-shrink-0 mono-num">
                      {demo.dwg}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Custom prompt textarea */}
          <div className="mb-5">
            <label className="text-xs font-medium text-[var(--color-ink)] block mb-1">
              Objective definition
            </label>
            <textarea
              rows={3}
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              className="w-full bg-[var(--color-paper-2)] border border-[var(--color-rule)] p-3 text-sm text-[var(--color-ink)] placeholder-[var(--color-muted)] focus:outline-none focus:border-[var(--color-ink)] transition-colors mono-num"
              placeholder="Enter specification objective for LangGraph..."
              required
            />
          </div>

          {/* Actions & Target Engine */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-[var(--color-rule)]">
            <div className="text-xs text-[var(--color-muted)]">
              Engine: <span className="text-[var(--color-ink)] mono-num">LangGraph 8-node state machine</span>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setCustomPrompt("")}
                className="ref-btn-secondary active:bg-[var(--color-paper-3)] disabled:opacity-50"
              >
                Clear
              </button>
              <button
                type="submit"
                className="ref-btn-primary active:bg-[var(--color-ink-2)] disabled:opacity-50"
              >
                <span>Execute agent workflow</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </form>
      </section>

      {/* Blueprint Navigation Footer */}
      <nav className="flex flex-wrap items-center gap-4 text-xs text-[var(--color-muted)] pt-4 border-t border-[var(--color-rule)]">
        <Link href="/chat" className="text-[var(--color-ink)] underline hover:no-underline">Open agent workspace</Link>
        <span>&bull;</span>
        <Link href="/documents" className="text-[var(--color-ink)] underline hover:no-underline">Knowledge base documents</Link>
        <span>&bull;</span>
        <Link href="/memory" className="text-[var(--color-ink)] underline hover:no-underline">Persistent memories</Link>
        <span>&bull;</span>
        <Link href="/tools" className="text-[var(--color-ink)] underline hover:no-underline">Tool execution logs</Link>
      </nav>
    </div>
  );
}
