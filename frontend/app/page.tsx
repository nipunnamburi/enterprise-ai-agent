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
  Sparkles, 
  ArrowRight, 
  ShieldCheck, 
  CheckCircle2, 
  GitBranch,
  Search,
  ExternalLink
} from "lucide-react";
import { fetchDashboardStats } from "@/lib/api";
import { DashboardStats } from "@/types";

const DEMO_OPTIONS = [
  {
    id: "demo-1",
    label: "Demo 1: RAG Policy Retrieval (Refund Policy & Return Window)",
    prompt: "What does our refund policy say regarding return windows and restocking fees?",
    badge: "Vector RAG"
  },
  {
    id: "demo-2",
    label: "Demo 2: Deterministic Tool Calling (Order 1024 + 15% Fee)",
    prompt: "Calculate the refund for order 1024 with a 15% restocking fee deduction.",
    badge: "AST Math"
  },
  {
    id: "demo-3",
    label: "Demo 3: Autonomous Multi-Step Complaint Audit (Order 1024 Full Audit)",
    prompt: "Analyze this customer complaint for order 1024, check our refund policy, look up order details, determine eligibility, calculate refund, and prepare a response.",
    badge: "Full Graph"
  },
  {
    id: "demo-4",
    label: "Demo 4: Long-Term Memory Preference Registration",
    prompt: "My preferred response style is concise bullet points.",
    badge: "Memory"
  },
  {
    id: "demo-5",
    label: "Demo 5: Business Intelligence SQL Query (Q3 Sales Variance)",
    prompt: "Compare Q3 sales against our target, query the database, and calculate the percentage difference.",
    badge: "Database"
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
    <div className="ref-container">
      {/* Hero Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          Elysia-Inspired Agentic Architecture &bull; Production Platform
        </div>
        <h2 className="ref-heading">Enterprise AI Agent Dashboard & System Summary</h2>
        <p className="text-xs text-slate-400 max-w-2xl mx-auto leading-relaxed">
          State-of-the-art autonomous AI system coordinating 8-node LangGraph execution, Chroma vector RAG, 
          deterministic AST math, parameterized SQL lookups, and persistent PostgreSQL memory.
        </p>
      </div>

      {/* Metrics Card Grid */}
      <h3 className="ref-subheading">System Telemetry & Knowledge Base Summary</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {/* Metric 1 */}
        <div className="bg-[#0b1120] border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">Indexed Documents</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mb-1">
            {stats?.total_documents ?? 4} <span className="text-xs font-normal text-slate-400">files</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Active in Vector Store
          </div>
        </div>

        {/* Metric 2 */}
        <div className="bg-[#0b1120] border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">Chroma Vector Chunks</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Search className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mb-1">
            {stats?.indexed_chunks ?? 7} <span className="text-xs font-normal text-slate-400">chunks</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-cyan-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            Cosine Similarity HNSW
          </div>
        </div>

        {/* Metric 3 */}
        <div className="bg-[#0b1120] border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">Autonomous Tasks</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mb-1">
            {stats?.total_tasks ?? 20} <span className="text-xs font-normal text-slate-400">tasks</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-blue-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
            8-Node State Machine
          </div>
        </div>

        {/* Metric 4 */}
        <div className="bg-[#0b1120] border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">Deterministic Tool Calls</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mb-1">
            {stats?.total_tool_calls ?? 45} <span className="text-xs font-normal text-slate-400">calls</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-amber-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            AST Math / SQL Database
          </div>
        </div>

        {/* Metric 5 */}
        <div className="bg-[#0b1120] border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">Long-Term Memory Facts</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <Brain className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mb-1">
            {stats?.total_memories ?? 4} <span className="text-xs font-normal text-slate-400">facts</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-purple-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
            Persisted in PostgreSQL
          </div>
        </div>

        {/* Metric 6 */}
        <div className="bg-[#0b1120] border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">Average Task Latency</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mb-1">
            {stats?.avg_latency_seconds ?? 0.05} <span className="text-xs font-normal text-slate-400">seconds</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Optimal Execution Pipeline
          </div>
        </div>
      </div>

      {/* Interactive Workflow Launcher */}
      <h3 className="ref-subheading">Agent Workflow Entry Form</h3>
      <form onSubmit={handleLaunchWorkflow} className="bg-[#0b1120] border border-slate-800 rounded-xl p-6 mb-8">
        {/* Preset Selector */}
        <div className="mb-4">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Select Enterprise Task Scenario:
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {DEMO_OPTIONS.map((demo) => {
              const isSelected = selectedDemo === demo.id;
              return (
                <button
                  key={demo.id}
                  type="button"
                  onClick={() => handleSelectDemo(demo.id)}
                  className={`text-left p-2.5 rounded-lg border text-xs transition-all flex items-center justify-between gap-2 ${
                    isSelected
                      ? "bg-slate-800 border-emerald-500/80 text-white shadow-sm ring-1 ring-emerald-500/30"
                      : "bg-[#090d16] border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                  }`}
                >
                  <span className="truncate">{demo.label}</span>
                  <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-emerald-400 flex-shrink-0">
                    {demo.badge}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom prompt textarea */}
        <div className="mb-4">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
            User Request Objective:
          </label>
          <textarea
            rows={3}
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            className="w-full bg-[#090d16] border border-slate-800 rounded-lg p-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all font-mono"
            placeholder="Enter request objective for the LangGraph agent..."
            required
          />
        </div>

        {/* Target Model details */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/80">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="font-semibold text-slate-300">Target Engine:</span>
            <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800 font-mono text-emerald-400 text-[11px]">
              LangGraph 8-Node Stateful Graph (OpenAI Deterministic Mode)
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setCustomPrompt("")}
              className="ref-btn-secondary text-xs py-2 px-4"
            >
              Clear
            </button>
            <button
              type="submit"
              className="ref-btn-primary text-xs py-2 px-5"
            >
              <span>Execute Agent Workflow</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </form>

      {/* Navigation Links */}
      <div className="ref-link pt-4 border-t border-slate-800/80">
        <Link href="/chat">Open Agent Workspace</Link> &bull;
        <Link href="/documents">View Knowledge Base Documents</Link> &bull;
        <Link href="/memory">View Persistent Memories</Link> &bull;
        <Link href="/tools">Inspect Tool Execution Logs</Link>
      </div>
    </div>
  );
}
