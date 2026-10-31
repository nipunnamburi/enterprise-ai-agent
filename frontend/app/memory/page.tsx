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

  return (
    <div className="ref-container">
      <h2 className="ref-heading">Persistent Agent Memory Records</h2>
      <p className="text-center text-xs text-slate-600 font-medium mb-6">
        PostgreSQL / SQLite Long-Term Memory Extraction and Selective Persistence
      </p>

      {statusMessage && (
        <div className="p-3 mb-5 bg-blue-50 border border-blue-300 rounded text-center text-xs font-bold text-[#1e3a8a]">
          {statusMessage}
        </div>
      )}

      {/* Add Memory Form */}
      <h3 className="ref-subheading">Add New Agent Memory Record Form</h3>
      <form onSubmit={handleCreate}>
        <div className="ref-form-group">
          <label>Memory Category:</label>
          <select
            value={newCategory}
            onChange={(e) => setNewCategory(e.target.value)}
          >
            <option value="preference">Preference (User Style/Format)</option>
            <option value="fact">Fact (Organizational Rule)</option>
            <option value="entity">Entity (Customer/Product Context)</option>
            <option value="task_context">Task Context (Workflow Rule)</option>
          </select>
        </div>

        <div className="ref-form-group">
          <label>Memory Statement:</label>
          <input
            type="text"
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="e.g. 'User requires responses in concise bullet points with policy citations.'"
            required
          />
        </div>

        <div className="ref-form-group">
          <label>Importance Rating:</label>
          <select
            value={newImportance}
            onChange={(e) => setNewImportance(parseFloat(e.target.value))}
          >
            <option value="1.0">1.0 (Critical Priority)</option>
            <option value="0.9">0.9 (High Priority)</option>
            <option value="0.8">0.8 (Medium Priority)</option>
            <option value="0.5">0.5 (Standard Priority)</option>
          </select>
        </div>

        <div className="ref-buttons">
          <input
            type="submit"
            value={isSubmitting ? "Saving Memory..." : "Add Memory Record"}
            disabled={isSubmitting}
            className="ref-btn-primary"
          />
          <input
            type="button"
            value="Clear"
            onClick={handleClear}
            className="ref-btn-secondary"
          />
        </div>
      </form>

      {/* Memory Table (Page 9 Style) */}
      <h3 className="ref-subheading">Active Persistent Memory Records ({memories.length})</h3>
      <table className="ref-table">
        <thead>
          <tr>
            <th style={{ width: "12%" }}>Category</th>
            <th style={{ width: "50%" }}>Memory Statement Content</th>
            <th style={{ width: "12%" }}>Importance</th>
            <th style={{ width: "16%" }}>Recorded Date</th>
            <th style={{ width: "10%" }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {memories.map((mem) => (
            <tr key={mem.id}>
              <td>
                <b className={
                  mem.category === "preference" ? "text-purple-700 uppercase" :
                  mem.category === "fact" ? "text-cyan-700 uppercase" :
                  "text-[#1e3a8a] uppercase"
                }>
                  {mem.category}
                </b>
              </td>
              <td className="font-medium text-slate-800">"{mem.content}"</td>
              <td className="text-center font-bold text-amber-700">{mem.importance.toFixed(1)}</td>
              <td>{formatDate(mem.created_at)}</td>
              <td className="text-center">
                <button
                  onClick={() => handleDelete(mem.id)}
                  className="text-red-700 font-bold underline hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Navigation Links */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-200">
        <Link href="/">Back to Dashboard</Link> | 
        <Link href="/chat">Open Agent Workspace</Link> | 
        <Link href="/documents">View Knowledge Base Documents</Link> | 
        <Link href="/tools">Inspect Tool Logs</Link>
      </div>
    </div>
  );
}
