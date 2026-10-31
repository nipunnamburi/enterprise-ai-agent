"use client";

import React, { useState } from "react";
import Link from "next/link";
import { 
  GitBranch, 
  ExternalLink, 
  Play, 
  Cpu, 
  Search, 
  Zap, 
  ShieldCheck, 
  Sparkles, 
  FileText, 
  Layers, 
  Activity,
  CheckCircle2,
  Database
} from "lucide-react";
import ElysiaDecisionTree from "@/components/elysia/ElysiaDecisionTree";
import { ExecutionStepInfo } from "@/types";

const SCENARIO_PRESETS = [
  {
    id: "complaint_audit",
    title: "1. Multi-Step Complaint & Refund Audit",
    category: "LangGraph + AST + RAG",
    description: "Evaluates Order #1024 warranty, cross-references Chroma refund policy, executes deterministic 15% restocking deduction, and generates executive report.",
    steps: [
      {
        step_name: "analyze_request",
        status: "completed",
        duration_ms: 12.4,
        description: "Scanned prompt with Enterprise Compliance Guardrails (Zero PII/Credentials detected). Evaluated active user memory constraints.",
        details: { format: "standard professional", compliance_findings: 0, pii_detected: false }
      },
      {
        step_name: "create_plan",
        status: "completed",
        duration_ms: 28.1,
        description: "Formulated hierarchical reasoning plan requiring 4 deterministic tools: customer_order_lookup, search_documents, calculator, generate_report.",
        details: { required_tools: ["customer_order_lookup", "search_documents", "calculator", "generate_report"] }
      },
      {
        step_name: "retrieve_context",
        status: "completed",
        duration_ms: 34.5,
        description: "Queried Chroma persistent vector store. Retrieved 3 chunks from 'refund_policy.pdf' (Section 2.2: Defective hardware restocking fee waiver).",
        details: { document: "refund_policy.pdf", top_k: 3, similarity_metric: "cosine" }
      },
      {
        step_name: "select_tools",
        status: "completed",
        duration_ms: 15.2,
        description: "Dispatched 'customer_order_lookup' for Order #1024 with typed Pydantic validation.",
        details: { tool: "customer_order_lookup", order_number: "1024" }
      },
      {
        step_name: "execute_tools",
        status: "completed",
        duration_ms: 42.8,
        description: "Retrieved Order #1024: Delivered 12 days ago, Total: $2,499.00 USD, Status: Delivered, Customer: Jane Doe.",
        details: { total_amount: 2499.0, days_since_delivery: 12, eligible: true }
      },
      {
        step_name: "execute_tools",
        status: "completed",
        duration_ms: 8.6,
        description: "Evaluated calculator AST expression: '2499.00 * 1.0' (Fee waived for defective item). Verified numerical precision.",
        details: { expression: "2499.00 * 1.0", result: 2499.0 }
      },
      {
        step_name: "evaluate_progress",
        status: "completed",
        duration_ms: 14.1,
        description: "Self-correction & completeness evaluator determined all 4 sub-goals achieved with 100% evidence verification.",
        details: { is_complete: true, confidence: "high", missing_information: null }
      },
      {
        step_name: "generate_response",
        status: "completed",
        duration_ms: 31.9,
        description: "Synthesized audited customer response citing refund_policy.pdf page 1, with verified $2,499.00 payout recommendation.",
        details: { sources: ["[Source: refund_policy.pdf, page 1]"], confidence: "high" }
      }
    ]
  },
  {
    id: "deep_research",
    title: "2. Recursive Multi-Hop Deep Web Research",
    category: "open-ai-research-agent + Synthesis",
    description: "Recursive sub-query decomposition across 3 focus areas, multi-hop evidence collection, proposition fact extraction, and verified dossier synthesis.",
    steps: [
      {
        step_name: "analyze_request",
        status: "completed",
        duration_ms: 8.9,
        description: "Identified deep research objective: 'Enterprise SaaS uptime SLA standards & financial penalty benchmarks'.",
        details: { depth: 2, focus_areas: ["technical", "compliance", "market"] }
      },
      {
        step_name: "create_plan",
        status: "completed",
        duration_ms: 19.3,
        description: "Scheduled recursive deep_research tool with 2 traversal hops and multi-dimensional gap closure.",
        details: { planned_hops: 2, synthesizer: "DeepResearchSynthesizer" }
      },
      {
        step_name: "execute_tools",
        status: "completed",
        duration_ms: 68.4,
        description: "Hop 1: Decomposed topic into 3 focus areas; swept 6 documents; extracted initial uptime metrics (99.9% guarantee).",
        details: { hop: 1, type: "domain_decomposition", docs_retrieved: 6 }
      },
      {
        step_name: "execute_tools",
        status: "completed",
        duration_ms: 54.2,
        description: "Hop 2: Generated follow-up queries regarding credit penalties; resolved gap on 43-minute downtime threshold.",
        details: { hop: 2, type: "gap_closure", claims_extracted: 6 }
      },
      {
        step_name: "generate_response",
        status: "completed",
        duration_ms: 26.7,
        description: "Compiled formal research dossier with 2 unique citations and structured strategic takeaways.",
        details: { claims_count: 6, unique_sources: 2, confidence: "high" }
      }
    ]
  },
  {
    id: "mcp_telemetry",
    title: "3. Model Context Protocol (MCP) Live Inspection",
    category: "MCP JSON-RPC 2.0 Integration",
    description: "Dynamic tool discovery over JSON-RPC 2.0 for enterprise Jira issue lookup and cloud microservice health telemetry.",
    steps: [
      {
        step_name: "analyze_request",
        status: "completed",
        duration_ms: 6.2,
        description: "Parsed request for Jira ticket SEC-809 and API gateway infrastructure latency.",
        details: { target_service: "api-gateway", issue_key: "SEC-809" }
      },
      {
        step_name: "create_plan",
        status: "completed",
        duration_ms: 14.8,
        description: "Scheduled dynamic MCP adapters: 'mcp_enterprise_jira_issue_lookup' and 'mcp_enterprise_cloud_health'.",
        details: { tools: ["mcp_enterprise_jira_issue_lookup", "mcp_enterprise_cloud_health"] }
      },
      {
        step_name: "execute_tools",
        status: "completed",
        duration_ms: 22.1,
        description: "Invoked JSON-RPC 2.0 tools/call for 'mcp_enterprise_jira_issue_lookup': Issue SEC-809 Status='IN_PROGRESS'.",
        details: { issue_key: "SEC-809", priority: "High", assignee: "Dev Team Lead" }
      },
      {
        step_name: "execute_tools",
        status: "completed",
        duration_ms: 18.5,
        description: "Invoked JSON-RPC 2.0 tools/call for 'mcp_enterprise_cloud_health': api-gateway Status=HEALTHY, P99=42ms.",
        details: { service: "api-gateway", cpu: "34.2%", p99_latency: "42ms" }
      },
      {
        step_name: "generate_response",
        status: "completed",
        duration_ms: 16.4,
        description: "Aggregated real-time Jira issue details and live cloud health telemetry into verified status brief.",
        details: { confidence: "high", status: "HEALTHY" }
      }
    ]
  }
];

export default function ElysiaPage() {
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>("complaint_audit");
  const activeScenario = SCENARIO_PRESETS.find((s) => s.id === selectedScenarioId) || SCENARIO_PRESETS[0];

  const totalDuration = activeScenario.steps.reduce((acc, curr) => acc + curr.duration_ms, 0);

  return (
    <div className="ref-container max-w-6xl">
      {/* Page Title & Elysia Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-1.5 rounded-lg bg-[#1e3a8a] text-white">
              <GitBranch className="w-5 h-5 text-emerald-400" />
            </div>
            <h2 className="text-xl font-bold text-[#1e3a8a] m-0">
              Elysia AI &bull; Agent Decision Tree & Reasoning Studio
            </h2>
          </div>
          <p className="text-xs text-slate-600 font-medium">
            Interactive Hierarchical Decision Trees, Chain-of-Thought Atlas, and Multi-Agent Reasoning Inspector
          </p>
        </div>

        {/* Live Elysia Studio External Link */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <a
            href="http://127.0.0.1:8000/elysia"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            Launch Live Elysia Webapp
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      {/* Overview Card */}
      <div className="bg-gradient-to-r from-slate-900 via-[#1e3a8a] to-slate-900 text-white rounded-lg p-5 shadow-sm mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded bg-white/10 text-emerald-400 mt-0.5">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-300 mb-1">Hierarchical Tree</h4>
              <p className="text-xs text-slate-200 leading-relaxed">
                Decomposes complex requests into transparent reasoning branches, tool call decision gates, and verification nodes.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="p-2 rounded bg-white/10 text-cyan-400 mt-0.5">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300 mb-1">Atlas & Environment</h4>
              <p className="text-xs text-slate-200 leading-relaxed">
                Maintains rolling environment state, citations, and tool payloads across multi-turn reasoning cycles.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="p-2 rounded bg-white/10 text-amber-400 mt-0.5">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-300 mb-1">Audited Compliance</h4>
              <p className="text-xs text-slate-200 leading-relaxed">
                Continuous pre- and post-execution guardrail inspection neutralizing PII, credit cards, and secret tokens.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="mb-4">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-2">
          Select Agent Trajectory Scenario:
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          {SCENARIO_PRESETS.map((scenario) => {
            const isSelected = selectedScenarioId === scenario.id;
            return (
              <button
                key={scenario.id}
                type="button"
                onClick={() => setSelectedScenarioId(scenario.id)}
                className={`text-left p-3 rounded-lg border transition-all ${
                  isSelected
                    ? "bg-white border-[#1e3a8a] shadow-sm ring-2 ring-[#1e3a8a]/20"
                    : "bg-slate-50/70 hover:bg-white border-slate-200 text-slate-600"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                    {scenario.category}
                  </span>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-[#1e3a8a]" />}
                </div>
                <div className="font-bold text-xs text-slate-800 mb-1">{scenario.title}</div>
                <p className="text-[11px] text-slate-500 line-clamp-2 leading-snug">
                  {scenario.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Interactive Elysia Decision Tree Component */}
      <div className="mb-8">
        <ElysiaDecisionTree
          steps={activeScenario.steps as ExecutionStepInfo[]}
          totalDurationMs={totalDuration}
          taskObjective={activeScenario.description}
          confidence="high"
        />
      </div>

      {/* Architectural Meta-Prompt Reference */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 mb-2">
          <Cpu className="w-4 h-4 text-[#1e3a8a]" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            Elysia Chain-of-Thought Protocol & Meta-Prompt Foundation
          </h4>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed mb-3">
          Our LangGraph state machine implements the Elysia multi-agent ensemble protocol. Specialized nodes operate as subtask specialists communicating via the shared state Atlas:
        </p>
        <div className="bg-slate-900 text-emerald-400 font-mono text-[11px] p-3 rounded border border-slate-800 overflow-x-auto leading-relaxed">
          {`"You are part of an ensemble of agents working together to solve an enterprise task.\nYour role is specialized: execute verification, tool calling, or knowledge extraction without whole-prompt hallucination.\nPass structured findings to the shared Atlas environment."`}
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="ref-link pt-4 border-t border-slate-200">
        <Link href="/chat">Test in Live Agent Chat</Link> | 
        <Link href="/tools">Inspect Deterministic Tools</Link> | 
        <Link href="/documents">Search Knowledge Base</Link> | 
        <Link href="/">Back to Dashboard</Link>
      </div>
    </div>
  );
}
