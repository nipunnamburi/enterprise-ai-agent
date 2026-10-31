"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { fetchMemories, createMemory, deleteMemory } from "@/lib/api";
import { MemoryItem } from "@/types";
import { formatDate } from "@/lib/utils";

export default function MemoryPage() {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [newContent, setNewContent] = useState("");
  const [newCategory, setNewCategory] = useState("preference");
  const [newImportance, setNewImportance] = useState(1.0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  const loadMemories = () => {
    fetchMemories()
      .then(setMemories)
      .catch((err) => console.error("Error loading memories:", err));
  };

  useEffect(() => {
    loadMemories();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newContent.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await createMemory(newCategory, newContent.trim(), newImportance);
      setNewContent("");
      setStatusMessage("Memory record created successfully in database.");
      loadMemories();
    } catch (err: any) {
      setStatusMessage(`Failed to save memory: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this memory record?")) return;
    try {
      await deleteMemory(id);
      loadMemories();
    } catch (err) {
      console.error("Error deleting memory:", err);
    }
  };

  const handleClear = () => {
    setNewContent("");
    setNewCategory("preference");
    setNewImportance(1.0);
  };

  const filteredMemories = categoryFilter === "all"
    ? memories
    : memories.filter((m) => m.category.toLowerCase() === categoryFilter.toLowerCase());

  return (
    <div className="ref-container">
      <div className="flex flex-col items-center mb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-950/40 border border-purple-800/50 text-purple-300 text-xs font-mono mb-3">
          <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
          Long-Term Agent Memory Ledger: {memories.length} Active Records
        </div>
        <h2 className="ref-heading">Persistent Agent Memory & Context Graph</h2>
        <p className="text-center text-xs text-slate-400 font-mono max-w-xl">
          PostgreSQL / SQLite Long-Term Memory Extraction and Selective Context Persistence
        </p>
      </div>

      {statusMessage && (
        <div className="p-3.5 mb-6 bg-emerald-950/40 border border-emerald-500/40 rounded-xl text-center text-xs font-mono font-medium text-emerald-300 backdrop-blur-sm shadow-sm flex items-center justify-center gap-2">
          <span className="text-emerald-400">⚡</span>
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Add Memory Form */}
      <div className="bg-[#0b101d]/80 border border-slate-800/80 rounded-xl p-5 mb-8 backdrop-blur-sm shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 font-mono">
            <span className="text-purple-400">01 //</span> Append Persistent Memory Record
          </h3>
          <span className="text-[11px] font-mono text-purple-400 bg-purple-950/40 border border-purple-800/50 px-2 py-0.5 rounded">
            Auto-Extracted Context
          </span>
        </div>

        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="ref-form-group">
              <label className="text-xs font-semibold text-slate-300 mb-1.5 block">
                Memory Category:
              </label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full bg-[#070b14] border border-slate-800 text-slate-200 text-xs px-3 py-2.5 rounded-lg focus:outline-none focus:border-purple-500/60 font-mono"
              >
                <option value="preference">Preference (User Style/Format)</option>
                <option value="fact">Fact (Organizational Rule)</option>
                <option value="entity">Entity (Customer/Product Context)</option>
                <option value="task_context">Task Context (Workflow Rule)</option>
              </select>
            </div>

            <div className="ref-form-group">
              <label className="text-xs font-semibold text-slate-300 mb-1.5 block">
                Importance Rating:
              </label>
              <select
                value={newImportance}
                onChange={(e) => setNewImportance(parseFloat(e.target.value))}
                className="w-full bg-[#070b14] border border-slate-800 text-slate-200 text-xs px-3 py-2.5 rounded-lg focus:outline-none focus:border-purple-500/60 font-mono"
              >
                <option value="1.0">1.0 (Critical Priority - Always Injected)</option>
                <option value="0.9">0.9 (High Priority)</option>
                <option value="0.8">0.8 (Medium Priority)</option>
                <option value="0.5">0.5 (Standard Priority)</option>
              </select>
            </div>
          </div>

          <div className="ref-form-group">
            <label className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-1.5">
              <span>Memory Statement Content:</span>
              <span className="text-[11px] font-mono text-slate-500">Atomic factual or procedural directive</span>
            </label>
            <input
              type="text"
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="e.g. 'User requires responses in concise bullet points with policy citations.'"
              required
              className="w-full bg-[#070b14] border border-slate-800 text-slate-100 placeholder-slate-500 text-sm px-4 py-2.5 rounded-lg focus:outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/40 font-mono"
            />
          </div>

          <div className="ref-buttons flex items-center gap-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="ref-btn-primary flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white"
            >
              {isSubmitting ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                  <span>Saving Memory Record...</span>
                </>
              ) : (
                <>
                  <span>💾</span>
                  <span>Add Memory Record</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleClear}
              className="ref-btn-secondary"
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      {/* Memory Table */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <h3 className="ref-subheading mb-0">Active Persistent Memory Records ({filteredMemories.length})</h3>
          
          {/* Category Filter Pills */}
          <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
            {["all", "preference", "fact", "entity", "task_context"].map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setCategoryFilter(cat)}
                className={`px-2.5 py-1 text-[11px] font-mono font-medium rounded-md transition-all uppercase ${
                  categoryFilter === cat
                    ? "bg-purple-600 text-white shadow-xs"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {cat.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>

        <table className="ref-table">
          <thead>
            <tr>
              <th style={{ width: "14%" }}>Category</th>
              <th style={{ width: "48%" }}>Memory Statement Content</th>
              <th style={{ width: "12%" }}>Importance</th>
              <th style={{ width: "16%" }}>Recorded Date</th>
              <th style={{ width: "10%" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredMemories.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-6 text-slate-500 font-mono text-xs">
                  No memory records found for category "{categoryFilter}".
                </td>
              </tr>
            ) : (
              filteredMemories.map((mem) => {
                const cat = mem.category.toLowerCase();
                const badgeClass =
                  cat === "preference"
                    ? "bg-purple-950/40 text-purple-300 border-purple-800/50"
                    : cat === "fact"
                    ? "bg-cyan-950/40 text-cyan-300 border-cyan-800/50"
                    : cat === "entity"
                    ? "bg-emerald-950/40 text-emerald-300 border-emerald-800/50"
                    : "bg-amber-950/40 text-amber-300 border-amber-800/50";

                return (
                  <tr key={mem.id}>
                    <td>
                      <span className={`uppercase font-mono text-[10px] font-bold px-2 py-0.5 rounded border ${badgeClass}`}>
                        {mem.category}
                      </span>
                    </td>
                    <td className="text-slate-200 font-sans text-xs">
                      "{mem.content}"
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs font-bold text-amber-400">
                          {mem.importance.toFixed(1)}
                        </span>
                        <div className="w-12 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-amber-400 h-full rounded-full"
                            style={{ width: `${mem.importance * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="font-mono text-xs text-slate-400">{formatDate(mem.created_at)}</td>
                    <td className="text-center">
                      <button
                        onClick={() => handleDelete(mem.id)}
                        className="text-xs font-mono text-red-400 hover:text-red-300 hover:underline transition-colors"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Navigation Links */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-800">
        <Link href="/">Back to Dashboard</Link> | 
        <Link href="/chat">Open Agent Workspace</Link> | 
        <Link href="/documents">Knowledge Base Documents</Link> | 
        <Link href="/tools">Inspect Tool Logs</Link>
      </div>
    </div>
  );
}
