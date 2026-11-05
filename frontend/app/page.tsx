"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { fetchDashboardStats } from "@/lib/api";
import { DashboardStats } from "@/types";

const DEMO_OPTIONS = [
  {
    id: "demo-1",
    label: "rag policy retrieval: return windows and restocking fees",
    prompt: "What does our refund policy say regarding return windows and restocking fees?",
    badge: "chroma vector"
  },
  {
    id: "demo-2",
    label: "deterministic calculation: order 1024 with 15% restocking fee",
    prompt: "Calculate the refund for order 1024 with a 15% restocking fee deduction.",
    badge: "ast calculator"
  },
  {
    id: "demo-3",
    label: "autonomous complaint audit: order 1024 full verification",
    prompt: "Analyze this customer complaint for order 1024, check our refund policy, look up order details, determine eligibility, calculate refund, and prepare a response.",
    badge: "8-node graph"
  },
  {
    id: "demo-4",
    label: "user preference registration: concise bullet points tone",
    prompt: "My preferred response style is concise bullet points.",
    badge: "postgres memory"
  },
  {
    id: "demo-5",
    label: "business intelligence query: q3 sales variance vs target",
    prompt: "Compare Q3 sales against our target, query the database, and calculate the percentage difference.",
    badge: "parameterized sql"
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
    <div className="w-[95%] max-w-[1100px] mx-auto my-6 px-4 md:px-8">
      {/* Hero Header */}
      <header className="mb-10 pt-4">
        <div className="flex items-center gap-2 mb-3 text-xs text-[var(--color-muted)]">
          <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-live)]" />
          <span>runtime active</span>
          <span>&bull;</span>
          <span className="mono-readout">langgraph 0.0.30</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-normal tracking-tight text-[var(--color-ink)] mb-3">
          enterprise ai agent <span className="verb">orchestrates</span> complex workflows.
        </h1>
        <p className="text-sm text-[var(--color-ink-2)] max-w-xl leading-relaxed">
          Autonomous state machine coordinating policy retrieval, deterministic calculations, and persistent user memory.
        </p>
      </header>

      {/* Telemetry Matrix (Hairline Wells) */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-4 border-b border-[var(--color-rule)] pb-2">
          <h2 className="text-xl md:text-2xl text-[var(--color-ink)]">system telemetry</h2>
          <span className="text-xs text-[var(--color-muted)] mono-readout">live state readouts</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {/* Card 1 */}
          <div className="lumen-well p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-3">
              <span>indexed documents</span>
              <span className="mono-readout">files</span>
            </div>
            <div className="text-3xl font-normal text-[var(--color-ink)] mono-readout mb-1">
              {stats?.total_documents ?? 4}
            </div>
            <div className="text-xs text-[var(--color-muted)]">
              active in chroma vector store
            </div>
          </div>

          {/* Card 2 */}
          <div className="lumen-well p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-3">
              <span>vector chunks</span>
              <span className="mono-readout">embeddings</span>
            </div>
            <div className="text-3xl font-normal text-[var(--color-ink)] mono-readout mb-1">
              {stats?.indexed_chunks ?? 7}
            </div>
            <div className="text-xs text-[var(--color-muted)]">
              cosine similarity retrieval
            </div>
          </div>

          {/* Card 3 */}
          <div className="lumen-well p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-3">
              <span>autonomous tasks</span>
              <span className="mono-readout">completed</span>
            </div>
            <div className="text-3xl font-normal text-[var(--color-ink)] mono-readout mb-1">
              {stats?.total_tasks ?? 20}
            </div>
            <div className="text-xs text-[var(--color-muted)]">
              8-node execution cycles
            </div>
          </div>

          {/* Card 4 */}
          <div className="lumen-well p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-3">
              <span>tool executions</span>
              <span className="mono-readout">calls</span>
            </div>
            <div className="text-3xl font-normal text-[var(--color-ink)] mono-readout mb-1">
              {stats?.total_tool_calls ?? 45}
            </div>
            <div className="text-xs text-[var(--color-muted)]">
              ast math and sql queries
            </div>
          </div>

          {/* Card 5 */}
          <div className="lumen-well p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-3">
              <span>persisted memories</span>
              <span className="mono-readout">records</span>
            </div>
            <div className="text-3xl font-normal text-[var(--color-ink)] mono-readout mb-1">
              {stats?.total_memories ?? 4}
            </div>
            <div className="text-xs text-[var(--color-muted)]">
              postgres user context facts
            </div>
          </div>

          {/* Card 6 */}
          <div className="lumen-well p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-3">
              <span>task latency</span>
              <span className="mono-readout">latency</span>
            </div>
            <div className="text-3xl font-normal text-[var(--color-accent)] mono-readout mb-1">
              {stats?.avg_latency_seconds ?? 0.05}s
            </div>
            <div className="text-xs text-[var(--color-muted)]">
              graph pipeline execution time
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Workflow Console */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-4 border-b border-[var(--color-rule)] pb-2">
          <h2 className="text-xl md:text-2xl text-[var(--color-ink)]">execution console</h2>
          <span className="text-xs text-[var(--color-muted)] mono-readout">graph entry point</span>
        </div>

        <form onSubmit={handleLaunchWorkflow} className="lumen-well p-6">
          {/* Preset Selector */}
          <div className="mb-6">
            <label className="text-xs text-[var(--color-muted)] block mb-3">
              preset scenarios
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {DEMO_OPTIONS.map((demo) => {
                const isSelected = selectedDemo === demo.id;
                return (
                  <button
                    key={demo.id}
                    type="button"
                    onClick={() => handleSelectDemo(demo.id)}
                    className={`text-left p-3.5 rounded-[var(--radius-card)] border text-xs transition-colors flex items-center justify-between gap-3 ${
                      isSelected
                        ? "bg-[var(--color-paper-3)] border-[var(--color-accent)] text-[var(--color-ink)]"
                        : "bg-[var(--color-paper)] border-[var(--color-rule)] text-[var(--color-muted)] hover:border-[var(--color-rule-2)] hover:text-[var(--color-ink)]"
                    }`}
                  >
                    <span className="truncate">{demo.label}</span>
                    <span className="text-[11px] px-2 py-0.5 rounded-[var(--radius-pill)] border border-[var(--color-rule-2)] text-[var(--color-ink-2)] mono-readout flex-shrink-0">
                      {demo.badge}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Custom prompt textarea */}
          <div className="mb-6">
            <label className="text-xs text-[var(--color-muted)] block mb-2">
              task objective
            </label>
            <textarea
              rows={3}
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              className="w-full bg-[var(--color-paper)] border border-[var(--color-rule-2)] rounded-[var(--radius-card)] p-3.5 text-sm text-[var(--color-ink)] placeholder-[var(--color-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)] transition-colors mono-readout"
              placeholder="describe execution objective for the agent..."
              required
            />
          </div>

          {/* Console Actions */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-[var(--color-rule)]">
            <div className="text-xs text-[var(--color-muted)] mono-readout">
              engine: <span className="text-[var(--color-ink-2)]">langgraph 8-node state machine</span>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setCustomPrompt("")}
                className="ref-btn-secondary active:opacity-75 disabled:opacity-40"
              >
                clear
              </button>
              <button
                type="submit"
                className="ref-btn-primary active:opacity-75 disabled:opacity-40"
              >
                <span>execute workflow</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </form>
      </section>

      {/* Navigation Footer */}
      <nav className="flex flex-wrap items-center gap-4 text-xs text-[var(--color-muted)] pt-4 border-t border-[var(--color-rule)]">
        <Link href="/chat" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] hover:underline">agent workspace</Link>
        <span>&bull;</span>
        <Link href="/documents" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] hover:underline">knowledge base</Link>
        <span>&bull;</span>
        <Link href="/memory" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] hover:underline">memory records</Link>
        <span>&bull;</span>
        <Link href="/tools" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] hover:underline">tool audit logs</Link>
      </nav>
    </div>
  );
}
