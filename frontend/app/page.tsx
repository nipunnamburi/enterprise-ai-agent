"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Check, Copy } from "lucide-react";
import { fetchDashboardStats } from "@/lib/api";
import { DashboardStats } from "@/types";

const DEMO_OPTIONS = [
  {
    id: "demo-1",
    flag: "--workflow rag-policy",
    label: "rag policy retrieval: return windows and restocking fees",
    prompt: "What does our refund policy say regarding return windows and restocking fees?",
    badge: "chroma vector",
    command: "agent run --workflow rag-policy --query 'return windows & restocking fees'"
  },
  {
    id: "demo-2",
    flag: "--workflow ast-calc",
    label: "deterministic calculation: order 1024 with 15% restocking fee",
    prompt: "Calculate the refund for order 1024 with a 15% restocking fee deduction.",
    badge: "ast calculator",
    command: "agent run --workflow ast-calc --order 1024 --deduct 0.15"
  },
  {
    id: "demo-3",
    flag: "--workflow complaint-audit",
    label: "autonomous complaint audit: order 1024 full verification",
    prompt: "Analyze this customer complaint for order 1024, check our refund policy, look up order details, determine eligibility, calculate refund, and prepare a response.",
    badge: "8-node graph",
    command: "agent run --workflow audit-complaint --order 1024 --full-graph"
  },
  {
    id: "demo-4",
    flag: "--workflow memory-reg",
    label: "user preference registration: concise bullet points tone",
    prompt: "My preferred response style is concise bullet points.",
    badge: "postgres memory",
    command: "agent run --workflow memory-persist --pref 'concise bullet points'"
  },
  {
    id: "demo-5",
    flag: "--workflow sql-bi",
    label: "business intelligence query: q3 sales variance vs target",
    prompt: "Compare Q3 sales against our target, query the database, and calculate the percentage difference.",
    badge: "parameterized sql",
    command: "agent run --workflow bi-query --sql 'q3 sales variance vs target'"
  },
];

const SUBSYSTEM_MAN_PAGE = [
  {
    cmd: "rag_retriever",
    args: "--query <str> [--top-k 4] [--collection docs]",
    description: "chroma vector semantic lookup across enterprise refund policy documentation"
  },
  {
    cmd: "ast_evaluator",
    args: "--expr <math> [--precision 2]",
    description: "deterministic safe AST calculator eliminating LLM arithmetic hallucinations"
  },
  {
    cmd: "order_db_lookup",
    args: "--order-id <int> [--fields status,total]",
    description: "parameterized PostgreSQL query retrieving customer order history and shipping records"
  },
  {
    cmd: "memory_sync",
    args: "--user-id <uuid> [--scope persistent]",
    description: "extracts and commits behavioral preferences to long-term relational storage"
  },
  {
    cmd: "state_graph",
    args: "--entrypoint router [--nodes 8]",
    description: "LangGraph cyclic state machine orchestrating multi-step execution and audits"
  }
];

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [selectedDemo, setSelectedDemo] = useState(DEMO_OPTIONS[2].id);
  const [customPrompt, setCustomPrompt] = useState(DEMO_OPTIONS[2].prompt);
  const [copied, setCopied] = useState(false);

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

  const handleCopyCommand = () => {
    const active = DEMO_OPTIONS.find((d) => d.id === selectedDemo) || DEMO_OPTIONS[2];
    navigator.clipboard.writeText(`$ ${active.command}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  };

  const handleLaunchWorkflow = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customPrompt.trim()) return;
    router.push(`/chat?prompt=${encodeURIComponent(customPrompt.trim())}`);
  };

  const currentOption = DEMO_OPTIONS.find((d) => d.id === selectedDemo) || DEMO_OPTIONS[2];

  return (
    <div className="w-full max-w-[1240px] mx-auto my-4 px-3 md:px-6">
      {/* Multiplexer Subheader Status Line */}
      <div className="flex flex-wrap items-center justify-between gap-2 py-2 px-3 mb-6 bg-[var(--color-paper-2)] border border-[var(--color-rule)] text-xs text-[var(--color-muted)]">
        <div className="flex items-center gap-2">
          <span className="text-[var(--color-accent)] font-semibold">$</span>
          <span className="text-[var(--color-ink)]">whoami</span>
          <span className="text-[var(--color-rule-2)]">&rarr;</span>
          <span className="text-[var(--color-ink-2)]">analyst@enterprise.ai</span>
          <span className="text-[var(--color-rule-2)]">|</span>
          <span>tty: /dev/pts/1</span>
        </div>
        <div className="flex items-center gap-3">
          <span>state: nominal</span>
          <span className="text-[var(--color-rule-2)]">|</span>
          <span className="text-[var(--color-accent)] font-medium">exit 0</span>
        </div>
      </div>

      {/* Split Hero: Command/Synopsis (Left) + ASCII State Machine DAG (Right) */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-10 items-stretch">
        {/* Left: Terminal Head & Quick Command Line */}
        <div className="lg:col-span-7 flex flex-col justify-between p-5 md:p-6 bg-[var(--color-paper-2)] border border-[var(--color-rule)]">
          <div>
            <div className="inline-flex items-center gap-2 mb-3 text-xs text-[var(--color-muted)]">
              <span className="w-1.5 h-1.5 bg-[var(--color-accent)]" />
              <span>runtime: active</span>
              <span className="text-[var(--color-rule-2)]">/</span>
              <span>langgraph 0.0.30</span>
              <span className="text-[var(--color-rule-2)]">/</span>
              <span>pid: 4180</span>
            </div>

            <h1 className="text-3xl md:text-4xl lg:text-5xl font-medium tracking-tight text-[var(--color-ink)] mb-4 leading-tight">
              enterprise ai agent orchestrates complex workflows.
            </h1>

            <p className="text-xs md:text-sm text-[var(--color-ink-2)] leading-relaxed mb-6">
              Single-binary autonomous state machine coordinating vector policy retrieval, deterministic AST calculation, parameterized database queries, and persistent user memory.
            </p>
          </div>

          {/* Quick-run CLI Well (Hallmark Terminal signature install well) */}
          <div className="mt-4 border border-[var(--color-rule)] bg-[var(--color-paper)]">
            <div className="flex items-center justify-between border-b border-[var(--color-rule)] px-3 py-1.5 text-[11px] text-[var(--color-muted)]">
              <span>active command synopsis</span>
              <span className="text-[var(--color-accent)]">{currentOption.badge}</span>
            </div>
            <div className="flex items-center justify-between gap-3 p-3 text-xs md:text-sm">
              <code className="text-[var(--color-ink)] overflow-x-auto whitespace-nowrap scrollbar-none font-mono">
                <span className="text-[var(--color-muted)] mr-2">$</span>
                <span>{currentOption.command}</span>
              </code>
              <button
                type="button"
                onClick={handleCopyCommand}
                aria-label="Copy shell command"
                className="flex-shrink-0 p-1.5 border border-transparent hover:border-[var(--color-rule)] text-[var(--color-muted)] hover:text-[var(--color-ink)] transition-colors"
                title="Copy command"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-[var(--color-accent)]" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right: ASCII State Graph DAG Diagram */}
        <div className="lg:col-span-5 flex flex-col justify-between p-4 md:p-5 bg-[var(--color-paper-2)] border border-[var(--color-rule)] overflow-hidden">
          <div className="flex items-center justify-between border-b border-[var(--color-rule)] pb-2 mb-3 text-xs text-[var(--color-muted)]">
            <span className="text-[var(--color-accent)]">// STATE_GRAPH.DAG</span>
            <span>8 compiled nodes</span>
          </div>

          <pre className="text-[11px] sm:text-[11.5px] leading-tight text-[var(--color-ink-2)] overflow-x-auto p-2 bg-[var(--color-paper)] border border-[var(--color-rule)] select-none font-mono">
{`+---------------------------------------+
| [00] INPUT_STREAM (complaint/task)    |
|   |                                   |
|   v                                   |
| [01] INTENT_ROUTER =================+ |
|   |                                 | |
|   +---------------+                 v |
|   |               |          [04] SQL |
|   v               v                 | |
| [02] RAG_POLICY  [03] AST_CALC      | |
|   | (chroma)      | (math)          | |
|   +-------+-------+                 | |
|           |                         | |
|           v                         v |
|   [05] COMPLAINT_AUDIT_ENGINE <=====+ |
|           |                           |
|           v                           |
|   [06] MEMORY_PERSISTENCE (postgres)  |
|           |                           |
|           v                           |
|   [07] SYNTHESIZE_RESPONSE            |
|           |                           |
|           v                           |
|   [08] RETURN_STREAM (exit 0)         |
+---------------------------------------+`}
          </pre>

          <div className="mt-3 flex items-center justify-between text-[11px] text-[var(--color-muted)] pt-2 border-t border-[var(--color-rule)]">
            <span>cyclic conditional edges</span>
            <span className="text-[var(--color-ink)]">recursion_limit: 25</span>
          </div>
        </div>
      </section>

      {/* Figures as Tool's Output (Hallmark Terminal signature telemetry grid) */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-3 pb-1 border-b border-[var(--color-rule-2)] text-xs text-[var(--color-muted)]">
          <h2 className="text-sm font-medium uppercase tracking-wider text-[var(--color-ink)]">
            system telemetry matrix
          </h2>
          <span>sysctl · vmstat format</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 border border-[var(--color-rule)] bg-[var(--color-paper-2)]">
          {/* Metric 1 */}
          <div className="p-4 border-r border-b lg:border-b-0 border-[var(--color-rule)]">
            <div className="figure-output text-2xl md:text-3xl text-[var(--color-ink)] mb-2">
              {String(stats?.total_documents ?? 4).padStart(2, "0")}
            </div>
            <div className="text-[11px] text-[var(--color-muted)] leading-tight">
              # 01 docs indexed in chroma vector
            </div>
          </div>

          {/* Metric 2 */}
          <div className="p-4 border-r-0 md:border-r border-b lg:border-b-0 border-[var(--color-rule)]">
            <div className="figure-output text-2xl md:text-3xl text-[var(--color-ink)] mb-2">
              {String(stats?.indexed_chunks ?? 7).padStart(2, "0")}
            </div>
            <div className="text-[11px] text-[var(--color-muted)] leading-tight">
              # 02 vector embeddings (384-dim)
            </div>
          </div>

          {/* Metric 3 */}
          <div className="p-4 border-r border-b md:border-b-0 border-[var(--color-rule)]">
            <div className="figure-output text-2xl md:text-3xl text-[var(--color-accent)] mb-2">
              08
            </div>
            <div className="text-[11px] text-[var(--color-muted)] leading-tight">
              # 03 compiled state machine graph nodes
            </div>
          </div>

          {/* Metric 4 */}
          <div className="p-4 border-r-0 md:border-r border-b md:border-b-0 border-[var(--color-rule)]">
            <div className="figure-output text-2xl md:text-3xl text-[var(--color-ink)] mb-2">
              {String(stats?.total_memories ?? 12).padStart(2, "0")}
            </div>
            <div className="text-[11px] text-[var(--color-muted)] leading-tight">
              # 04 long-term memories in postgres
            </div>
          </div>

          {/* Metric 5 */}
          <div className="p-4 border-r border-[var(--color-rule)]">
            <div className="figure-output text-2xl md:text-3xl text-[var(--color-ink)] mb-2">
              {stats?.avg_latency_seconds ? `${stats.avg_latency_seconds}s` : "0.05s"}
            </div>
            <div className="text-[11px] text-[var(--color-muted)] leading-tight">
              # 05 graph execution pipeline latency
            </div>
          </div>

          {/* Metric 6 */}
          <div className="p-4">
            <div className="figure-output text-2xl md:text-3xl text-[var(--color-accent)] mb-2">
              0
            </div>
            <div className="text-[11px] text-[var(--color-muted)] leading-tight">
              # 06 error exit code (status: active)
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Execution Console (Terminal Command Dispatch) */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-3 pb-1 border-b border-[var(--color-rule-2)] text-xs text-[var(--color-muted)]">
          <h2 className="text-sm font-medium uppercase tracking-wider text-[var(--color-ink)]">
            interactive execution console
          </h2>
          <span>graph entry point</span>
        </div>

        <form onSubmit={handleLaunchWorkflow} className="terminal-well p-5 md:p-6">
          {/* Preset Flag Selectors */}
          <div className="mb-6">
            <label className="text-xs text-[var(--color-muted)] block mb-2 uppercase tracking-wide">
              select workflow preset flag
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {DEMO_OPTIONS.map((demo) => {
                const isSelected = selectedDemo === demo.id;
                return (
                  <button
                    key={demo.id}
                    type="button"
                    onClick={() => handleSelectDemo(demo.id)}
                    className={`text-left p-3 border text-xs transition-colors flex flex-col justify-between gap-2 ${
                      isSelected
                        ? "bg-[var(--color-paper-3)] border-[var(--color-accent)] text-[var(--color-ink)] shadow-[inset_2px_0_0_var(--color-accent)]"
                        : "bg-[var(--color-paper)] border-[var(--color-rule)] text-[var(--color-muted)] hover:border-[var(--color-rule-2)] hover:text-[var(--color-ink)]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[var(--color-accent)] font-mono text-[11px]">
                        {demo.flag}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 border border-[var(--color-rule-2)] text-[var(--color-ink-2)]">
                        {demo.badge}
                      </span>
                    </div>
                    <span className="text-[11.5px] leading-tight line-clamp-2 text-[var(--color-ink-2)]">
                      {demo.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Objective Textarea Terminal Prompt */}
          <div className="mb-6">
            <div className="flex items-center justify-between text-xs text-[var(--color-muted)] mb-2">
              <span>task objective specification</span>
              <span className="text-[11px] text-[var(--color-ink-2)]">--stdin</span>
            </div>
            <div className="border border-[var(--color-rule-2)] bg-[var(--color-paper)] p-3">
              <div className="text-xs text-[var(--color-muted)] mb-2 font-mono flex items-center gap-1.5">
                <span className="text-[var(--color-accent)]">user@enterprise:~$</span>
                <span>agent exec --prompt \</span>
              </div>
              <textarea
                rows={3}
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                className="w-full bg-transparent text-sm text-[var(--color-ink)] placeholder-[var(--color-muted)] focus:outline-none resize-none font-mono"
                placeholder="enter execution objective for the autonomous state machine..."
                required
              />
            </div>
          </div>

          {/* Console Actions */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-[var(--color-rule)] text-xs">
            <div className="text-[var(--color-muted)] font-mono flex items-center gap-2">
              <span>engine:</span>
              <span className="text-[var(--color-ink-2)]">langgraph 8-node state machine</span>
              <span className="text-[var(--color-rule-2)]">|</span>
              <span className="text-[var(--color-accent)]">ready</span>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setCustomPrompt("")}
                className="btn-terminal-secondary"
              >
                clear
              </button>
              <button
                type="submit"
                className="btn-terminal-primary"
              >
                <span>execute workflow</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </form>
      </section>

      {/* Signature Hallmark Terminal Element: Comparison as a Unified Diff */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-3 pb-1 border-b border-[var(--color-rule-2)] text-xs text-[var(--color-muted)]">
          <h2 className="text-sm font-medium uppercase tracking-wider text-[var(--color-ink)]">
            execution diff · complaint resolution
          </h2>
          <span>git unified diff format</span>
        </div>

        <div className="diff-container text-xs font-mono">
          <div className="diff-header flex flex-wrap items-center justify-between gap-2">
            <div>
              <span className="text-[var(--color-muted)]">--- a/var/log/customer_complaint_1024.raw</span>
              <br />
              <span className="text-[var(--color-accent)]">+++ b/var/state/agent_settlement_1024.json</span>
            </div>
            <span className="text-[var(--color-muted)]">@@ -1,7 +1,9 @@</span>
          </div>

          <ul className="list-none p-2 m-0 divide-y divide-[var(--color-rule)]">
            <li className="diff-line del py-1.5">
              <span className="text-[var(--color-rule-2)] text-right pr-4 select-none">01</span>
              <span className="text-[var(--color-muted)] select-none">-</span>
              <span className="truncate">customer: "I ordered keyboard #1024, want a full refund, item unopened."</span>
            </li>
            <li className="diff-line del py-1.5">
              <span className="text-[var(--color-rule-2)] text-right pr-4 select-none">02</span>
              <span className="text-[var(--color-muted)] select-none">-</span>
              <span className="truncate">support_bot: "Please wait 3-5 business days for human supervisor review."</span>
            </li>
            <li className="diff-line add py-1.5">
              <span className="text-[var(--color-rule-2)] text-right pr-4 select-none">03</span>
              <span className="text-[var(--color-accent)] font-bold select-none">+</span>
              <span className="truncate text-[var(--color-ink)]">node_rag: refund policy retrieved (30-day window verified, 15% restocking fee applicable)</span>
            </li>
            <li className="diff-line add py-1.5">
              <span className="text-[var(--color-rule-2)] text-right pr-4 select-none">04</span>
              <span className="text-[var(--color-accent)] font-bold select-none">+</span>
              <span className="truncate text-[var(--color-ink)]">node_sql: order #1024 retrieved (subtotal: $120.00, delivery: 12 days ago, status: eligible)</span>
            </li>
            <li className="diff-line add py-1.5">
              <span className="text-[var(--color-rule-2)] text-right pr-4 select-none">05</span>
              <span className="text-[var(--color-accent)] font-bold select-none">+</span>
              <span className="truncate text-[var(--color-ink)]">node_calc: AST deterministic evaluation: 120.00 - (120.00 * 0.15) = $102.00 exact</span>
            </li>
            <li className="diff-line add py-1.5">
              <span className="text-[var(--color-rule-2)] text-right pr-4 select-none">06</span>
              <span className="text-[var(--color-accent)] font-bold select-none">+</span>
              <span className="truncate text-[var(--color-ink)]">node_memory: committed preference (concise bullet points, order 1024 audit log)</span>
            </li>
            <li className="diff-line py-1.5 text-[var(--color-muted)]">
              <span className="text-[var(--color-rule-2)] text-right pr-4 select-none">07</span>
              <span className="text-[var(--color-muted)] select-none"> </span>
              <span className="truncate">status: settlement generated autonomously in 0.05s · exit code 0</span>
            </li>
          </ul>
        </div>
      </section>

      {/* Signature Hallmark Terminal Element: Reference as Rows (Man-Page Synopsis) */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-3 pb-1 border-b border-[var(--color-rule-2)] text-xs text-[var(--color-muted)]">
          <h2 className="text-sm font-medium uppercase tracking-wider text-[var(--color-ink)]">
            subsystem reference & command synopsis
          </h2>
          <span>man (1) agent</span>
        </div>

        <div className="overflow-x-auto">
          <table className="terminal-table">
            <thead>
              <tr>
                <th className="w-1/4">subsystem</th>
                <th className="w-1/3">flags & arguments</th>
                <th>operational synopsis</th>
              </tr>
            </thead>
            <tbody>
              {SUBSYSTEM_MAN_PAGE.map((row) => (
                <tr key={row.cmd}>
                  <td className="font-semibold text-[var(--color-ink)] font-mono">
                    ${" "}{row.cmd}
                  </td>
                  <td className="text-[var(--color-accent)] font-mono text-[11px]">
                    {row.args}
                  </td>
                  <td className="text-[var(--color-ink-2)] text-xs">
                    {row.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Terminal Directory Shortcuts Footer */}
      <nav className="flex flex-wrap items-center gap-4 text-xs text-[var(--color-muted)] pt-4 pb-8 border-t border-[var(--color-rule)] font-mono">
        <div className="flex items-center gap-1.5">
          <span className="text-[var(--color-accent)]">$</span>
          <Link href="/chat" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] underline underline-offset-4">
            cd /chat
          </Link>
          <span className="text-[var(--color-muted)]"># workspace</span>
        </div>
        <span className="text-[var(--color-rule-2)]">|</span>
        <div className="flex items-center gap-1.5">
          <span className="text-[var(--color-accent)]">$</span>
          <Link href="/documents" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] underline underline-offset-4">
            cd /documents
          </Link>
          <span className="text-[var(--color-muted)]"># vector index</span>
        </div>
        <span className="text-[var(--color-rule-2)]">|</span>
        <div className="flex items-center gap-1.5">
          <span className="text-[var(--color-accent)]">$</span>
          <Link href="/memory" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] underline underline-offset-4">
            cd /memory
          </Link>
          <span className="text-[var(--color-muted)]"># postgres records</span>
        </div>
        <span className="text-[var(--color-rule-2)]">|</span>
        <div className="flex items-center gap-1.5">
          <span className="text-[var(--color-accent)]">$</span>
          <Link href="/tools" className="text-[var(--color-ink)] hover:text-[var(--color-accent)] underline underline-offset-4">
            cd /tools
          </Link>
          <span className="text-[var(--color-muted)]"># audit logs</span>
        </div>
      </nav>
    </div>
  );
}
