"use client";

import React, { useState } from "react";
import { ShieldAlert, CheckCircle2, XCircle, Terminal } from "lucide-react";
import { ApprovalRequest } from "@/types";

interface ActionApprovalCardProps {
  threadId: string;
  approvalRequest: ApprovalRequest;
  isSubmitting?: boolean;
  onDecision: (approved: boolean, feedback?: string) => Promise<void>;
}

export default function ActionApprovalCard({
  threadId,
  approvalRequest,
  isSubmitting = false,
  onDecision,
}: ActionApprovalCardProps) {
  const [feedback, setFeedback] = useState("");

  return (
    <div className="p-5 rounded-xl border border-amber-500/40 bg-amber-950/20 text-slate-100 shadow-lg ring-1 ring-amber-500/20 space-y-3">
      <div className="flex items-center justify-between border-b border-amber-500/20 pb-2.5">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-amber-300">
            Human-in-the-Loop Approval Required
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-400 truncate max-w-[220px]">
          Thread: {threadId}
        </span>
      </div>

      <div className="space-y-1">
        <div className="flex items-center gap-2 text-xs">
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Requested Tool:</span>
          <code className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-300 font-mono font-semibold">
            {approvalRequest.tool_name}
          </code>
        </div>
        {approvalRequest.reason && (
          <p className="text-xs text-slate-300">{approvalRequest.reason}</p>
        )}
      </div>

      <div className="bg-[#070b14] border border-slate-800 rounded-lg p-3 overflow-x-auto">
        <div className="text-[10px] font-mono uppercase text-slate-500 mb-1">
          Tool Arguments
        </div>
        <pre className="text-[11px] font-mono text-emerald-300 whitespace-pre-wrap break-all">
          {JSON.stringify(approvalRequest.tool_args || {}, null, 2)}
        </pre>
      </div>

      <div>
        <input
          type="text"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          disabled={isSubmitting}
          placeholder="Optional feedback or rejection reason..."
          className="w-full bg-[#070b14] border border-slate-800 text-slate-200 placeholder-slate-500 text-xs px-3 py-2 rounded-lg focus:outline-none focus:border-amber-500/50 font-mono"
        />
      </div>

      <div className="flex items-center gap-2.5 pt-1">
        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => onDecision(true, feedback || undefined)}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-colors disabled:opacity-50"
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{isSubmitting ? "Resuming..." : "Approve & Execute"}</span>
        </button>
        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => onDecision(false, feedback || "Rejected by operator")}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-rose-600/90 hover:bg-rose-500 text-white text-xs font-semibold transition-colors disabled:opacity-50"
        >
          <XCircle className="w-3.5 h-3.5" />
          <span>Reject</span>
        </button>
      </div>
    </div>
  );
}
