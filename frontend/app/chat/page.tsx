"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
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
      <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 mb-5 text-center text-xs font-bold">
        <span className="text-slate-500 mr-2 uppercase">Quick Demo Prompts:</span>
        {QUICK_DEMOS.map((d, i) => (
          <button
            key={i}
            onClick={() => setInputMessage(d.prompt)}
            className="mx-1 my-0.5 px-2.5 py-1 bg-white border border-slate-300 rounded text-[#1e3a8a] hover:bg-[#1e3a8a] hover:text-white transition-colors"
          >
            {d.name}
          </button>
        ))}
      </div>

      {/* Interactive Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="ref-form-group">
          <label>Agent Request / Query:</label>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type query or select demo prompt above..."
            required
            disabled={isProcessing}
          />
        </div>

        <div className="ref-buttons">
          <input
            type="submit"
            value={isProcessing ? "Executing Workflow..." : "Send Agent Request"}
            className="ref-btn-primary"
            disabled={isProcessing}
          />
          <input
            type="button"
            value="Clear Input"
            onClick={handleClear}
            className="ref-btn-secondary"
          />
          <input
            type="button"
            value="Reset Session"
            onClick={handleResetChat}
            className="ref-btn-secondary"
          />
        </div>
      </form>

      {/* Conversation Thread */}
      {messages.length > 0 && (
        <div className="space-y-4 mb-8">
          <h3 className="ref-subheading">Conversation & Response Records</h3>
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-4 rounded-lg border ${
                msg.role === "user"
                  ? "bg-blue-50 border-blue-200"
                  : "bg-white border-slate-300 shadow-xs"
              }`}
            >
              <div className="flex justify-between items-center mb-2 pb-1 border-b border-slate-200">
                <span className="text-xs font-bold text-[#1e3a8a] uppercase">
                  {msg.role === "user" ? "User Request" : "Autonomous Agent Response"}
                </span>
                <span className="text-[11px] text-slate-500">{new Date(msg.created_at).toLocaleTimeString()}</span>
              </div>

              <div className="text-xs text-slate-800 whitespace-pre-wrap leading-relaxed">
                {msg.content}
              </div>

              {/* Citations and Tools */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-200 text-xs">
                  <span className="font-bold text-cyan-800">Citations: </span>
                  <span className="text-slate-600">{msg.sources.join(", ")}</span>
                </div>
              )}
              {msg.tools_used && msg.tools_used.length > 0 && (
                <div className="mt-1 text-xs">
                  <span className="font-bold text-amber-800">Tools Called: </span>
                  <span className="font-mono text-slate-700">{msg.tools_used.join(", ")}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* LangGraph Execution Trace Table */}
      {latestSteps.length > 0 && (
        <div>
          <h3 className="ref-subheading">
            LangGraph Multi-Step Execution Trace {latestDuration ? `(${latestDuration}ms)` : ""}
          </h3>
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
                  <td className="text-center font-bold">{idx + 1}</td>
                  <td><b className="text-[#1e3a8a]">{step.step_name}</b></td>
                  <td><span className="text-green-700 font-bold">&#10004; {step.status}</span></td>
                  <td>{step.duration_ms} ms</td>
                  <td>{step.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Bottom Navigation Links */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-200">
        <Link href="/">Back to Dashboard</Link> | 
        <Link href="/documents">View Knowledge Base Documents</Link> | 
        <Link href="/memory">View Persistent Memories</Link> | 
        <Link href="/tools">Inspect Tool Logs</Link>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="text-center p-8 text-sm font-bold text-[#1e3a8a]">Loading Workspace...</div>}>
      <ChatContent />
    </Suspense>
  );
}
