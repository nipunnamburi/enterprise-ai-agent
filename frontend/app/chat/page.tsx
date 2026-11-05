"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import { GitBranch, List } from "lucide-react";
import DecisionTree from "@/components/trace/DecisionTree";
import { sendAgentChat, fetchConversations, fetchConversationDetails } from "@/lib/api";
import { ExecutionStepInfo, MessageItem } from "@/types";

const QUICK_DEMOS = [
  {
    name: "Demo 1: RAG Refund Policy",
    prompt: "What does our refund policy say regarding return windows and restocking fees?",
  },
  {
    name: "Demo 2: Calculate Refund (Order 1024)",
    prompt: "Calculate the refund for order 1024 with a 15% restocking fee deduction.",
  },
  {
    name: "Demo 3: Multi-Step Complaint Audit",
    prompt: "Analyze this customer complaint for order 1024, check our refund policy, look up order details, determine eligibility, calculate refund, and prepare a response.",
  },
  {
    name: "Demo 4: Tone Preference",
    prompt: "My preferred response style is concise bullet points.",
  },
  {
    name: "Demo 5: Q3 Sales Variance",
    prompt: "Compare Q3 sales against our target, query the database, and calculate the percentage difference.",
  },
];

function ChatContent() {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [activeConvId, setActiveConvId] = useState<string | undefined>(undefined);
  const [isProcessing, setIsProcessing] = useState(false);
  const [latestSteps, setLatestSteps] = useState<ExecutionStepInfo[]>([]);
  const [latestDuration, setLatestDuration] = useState<number | null>(null);
  const [traceViewMode, setTraceViewMode] = useState<"decision_tree" | "table">("decision_tree");

  useEffect(() => {
    fetchConversations()
      .then((convs) => {
        if (convs.length > 0 && !activeConvId) {
          fetchConversationDetails(convs[0].id).then((d) => {
            setActiveConvId(convs[0].id);
            setMessages(d.messages || []);
            const lastAsst = [...(d.messages || [])].reverse().find(m => m.role === "assistant");
            if (lastAsst && lastAsst.execution_steps) {
              setLatestSteps(lastAsst.execution_steps);
            }
          });
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    const p = searchParams?.get("prompt");
    if (p && !isProcessing) {
      setInputMessage(p);
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isProcessing) return;

    const userText = inputMessage.trim();
    setInputMessage("");

    const tempUserMsg: MessageItem = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsProcessing(true);
    setLatestSteps([]);

    try {
      const response = await sendAgentChat(userText, activeConvId);

      setActiveConvId(response.conversation_id);
      setLatestSteps(response.execution_steps);
      setLatestDuration(response.duration_ms);

      const assistantMsg: MessageItem = {
        id: response.task_id,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        tools_used: response.tools_used,
        execution_steps: response.execution_steps,
        confidence: response.confidence,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: MessageItem = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: `Execution Error: ${err.message || "Failed to complete workflow"}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClear = () => {
    setInputMessage("");
  };

  const handleResetChat = () => {
    setMessages([]);
    setLatestSteps([]);
    setLatestDuration(null);
    setActiveConvId(undefined);
  };

  return (
    <div className="ref-container">
      <h2 className="ref-heading">Autonomous Agent Chat & Execution Workspace</h2>
      <p className="text-center text-xs text-slate-600 font-medium mb-4">
        Multi-Step LangGraph Agent with Parameterized Tool Calling and Chroma RAG
      </p>

      {/* Quick Demo Links */}
      <div className="bg-[#0b101d]/80 border border-slate-800/80 p-3.5 rounded-xl mb-6 backdrop-blur-sm shadow-inner">
        <div className="flex items-center gap-2 mb-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-mono">
            Interactive Scenario Presets:
          </span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {QUICK_DEMOS.map((d, i) => (
            <button
              key={i}
              onClick={() => setInputMessage(d.prompt)}
              className="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-800/90 text-slate-300 hover:text-emerald-300 transition-all text-left shadow-xs"
            >
              {d.name}
            </button>
          ))}
        </div>
      </div>

      {/* Interactive Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="ref-form-group">
          <label className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-2">
            <span>Agent Directive / Query:</span>
            <span className="text-[11px] font-mono text-slate-500">Press Send to dispatch to LangGraph State Machine</span>
          </label>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type query or select scenario preset above..."
            required
            disabled={isProcessing}
            className="w-full bg-[#070b14] border border-slate-800 text-slate-100 placeholder-slate-500 text-sm px-4 py-3 rounded-lg focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40 transition-all font-mono"
          />
        </div>

        <div className="ref-buttons flex items-center gap-2.5">
          <button
            type="submit"
            disabled={isProcessing}
            className="ref-btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                <span>Executing Workflow...</span>
              </>
            ) : (
              <>
                <span>⚡</span>
                <span>Dispatch Workflow</span>
              </>
            )}
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="ref-btn-secondary"
          >
            Clear Input
          </button>
          <button
            type="button"
            onClick={handleResetChat}
            className="ref-btn-secondary"
          >
            Reset Session
          </button>
        </div>
      </form>

      {/* Conversation Thread */}
      {messages.length > 0 && (
        <div className="space-y-4 mb-8">
          <h3 className="ref-subheading">Conversation & Response Records</h3>
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-5 rounded-xl border transition-all ${
                msg.role === "user"
                  ? "bg-slate-900/60 border-slate-800 text-slate-100 shadow-sm"
                  : "bg-[#0b101d]/90 border-emerald-500/30 text-slate-100 shadow-md ring-1 ring-emerald-500/10"
              }`}
            >
              <div className="flex justify-between items-center mb-3 pb-2 border-b border-slate-800/80">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded tracking-wide ${
                      msg.role === "user"
                        ? "bg-cyan-950/60 text-cyan-300 border border-cyan-800/50"
                        : "bg-emerald-950/60 text-emerald-300 border border-emerald-700/50"
                    }`}
                  >
                    {msg.role === "user" ? "USER DIRECTIVE" : "ELYSIUM AGENT ENGINE"}
                  </span>
                  {msg.role === "assistant" && msg.confidence && (
                    <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/30 border border-emerald-900 px-1.5 py-0.5 rounded">
                      Confidence: {msg.confidence}
                    </span>
                  )}
                </div>
                <span className="text-[11px] font-mono text-slate-500">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </span>
              </div>

              <div className="text-xs text-slate-200 leading-relaxed space-y-2 prose prose-invert prose-xs max-w-none">
                {msg.role === "assistant" ? (
                  <ReactMarkdown
                    components={{
                      h1: ({ ...props }) => <h1 className="text-sm font-bold text-emerald-400 mt-3 mb-1" {...props} />,
                      h2: ({ ...props }) => <h2 className="text-xs font-bold text-cyan-300 mt-2.5 mb-1" {...props} />,
                      h3: ({ ...props }) => <h3 className="text-xs font-semibold text-slate-200 mt-2 mb-1" {...props} />,
                      p: ({ ...props }) => <p className="mb-1 leading-relaxed text-slate-300" {...props} />,
                      ul: ({ ...props }) => <ul className="list-disc pl-4 mb-2 space-y-1 text-slate-300" {...props} />,
                      ol: ({ ...props }) => <ol className="list-decimal pl-4 mb-2 space-y-1 text-slate-300" {...props} />,
                      li: ({ ...props }) => <li className="leading-relaxed" {...props} />,
                      strong: ({ ...props }) => <strong className="font-semibold text-white" {...props} />,
                      em: ({ ...props }) => <em className="italic text-slate-400" {...props} />,
                      code: ({ ...props }) => (
                        <code className="bg-[#050811] text-emerald-300 border border-slate-800 px-1.5 py-0.5 rounded text-[11px] font-mono" {...props} />
                      ),
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  <div className="whitespace-pre-wrap font-sans text-slate-200 text-sm leading-relaxed">{msg.content}</div>
                )}
              </div>

              {/* Citations and Tools */}
              {(msg.sources?.length || msg.tools_used?.length) ? (
                <div className="mt-3.5 pt-3 border-t border-slate-800/80 flex flex-wrap gap-2 text-xs">
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="flex items-center gap-1.5 bg-cyan-950/40 border border-cyan-800/40 px-2 py-0.5 rounded text-[11px]">
                      <span className="font-bold text-cyan-400 font-mono uppercase tracking-wider text-[10px]">Sources:</span>
                      <span className="text-cyan-200 font-mono">{msg.sources.join(", ")}</span>
                    </div>
                  )}
                  {msg.tools_used && msg.tools_used.length > 0 && (
                    <div className="flex items-center gap-1.5 bg-amber-950/40 border border-amber-800/40 px-2 py-0.5 rounded text-[11px]">
                      <span className="font-bold text-amber-400 font-mono uppercase tracking-wider text-[10px]">Tools:</span>
                      <span className="text-amber-200 font-mono">{msg.tools_used.join(", ")}</span>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}

      {/* Execution Trace & Elysia Decision Tree */}
      {latestSteps.length > 0 && (
        <div className="mt-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <h3 className="ref-subheading mb-0">
              Agent Execution & Decision Trace {latestDuration ? `(${latestDuration}ms)` : ""}
            </h3>
            <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 self-start sm:self-auto">
              <button
                type="button"
                onClick={() => setTraceViewMode("decision_tree")}
                className={`flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-md transition-all ${
                  traceViewMode === "decision_tree"
                    ? "bg-emerald-500 text-slate-950 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <GitBranch className="w-3.5 h-3.5" />
                Decision Tree
              </button>
              <button
                type="button"
                onClick={() => setTraceViewMode("table")}
                className={`flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-md transition-all ${
                  traceViewMode === "table"
                    ? "bg-emerald-500 text-slate-950 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <List className="w-3.5 h-3.5" />
                Linear Audit Table
              </button>
            </div>
          </div>

          {traceViewMode === "decision_tree" ? (
            <DecisionTree
              steps={latestSteps}
              totalDurationMs={latestDuration}
              confidence={messages[messages.length - 1]?.confidence}
            />
          ) : (
            <table className="ref-table">
              <thead>
                <tr>
                  <th style={{ width: "8%" }}>Step #</th>
                  <th style={{ width: "22%" }}>State Machine Node</th>
                  <th style={{ width: "15%" }}>Status</th>
                  <th style={{ width: "12%" }}>Duration</th>
                  <th style={{ width: "43%" }}>Description / Output Summary</th>
                </tr>
              </thead>
              <tbody>
                {latestSteps.map((step, idx) => (
                  <tr key={idx}>
                    <td className="text-center font-mono font-bold text-slate-400">{idx + 1}</td>
                    <td><b className="font-mono text-emerald-400">{step.step_name}</b></td>
                    <td><span className="text-emerald-400 font-mono font-bold">&#10004; {step.status}</span></td>
                    <td className="font-mono text-slate-300">{step.duration_ms} ms</td>
                    <td className="text-slate-300 text-xs">{step.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Bottom Navigation Links */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-800">
        <Link href="/">Back to Dashboard</Link> | 
        <Link href="/documents">Knowledge Base Documents</Link> | 
        <Link href="/memory">Persistent Memories</Link> | 
        <Link href="/tools">Deterministic Tool Registry</Link>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="text-center p-8 text-sm font-mono text-emerald-400">Loading Elysium Agent Workspace...</div>}>
      <ChatContent />
    </Suspense>
  );
}
