"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { fetchDocuments, uploadDocument, deleteDocument, reindexDocuments, executeToolDirect } from "@/lib/api";
import { DocumentItem } from "@/types";
import { formatBytes, formatDate } from "@/lib/utils";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const loadDocs = () => {
    fetchDocuments()
      .then(setDocuments)
      .catch((err) => console.error("Error loading documents:", err));
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatusMessage(`Uploading and chunking document: ${file.name}...`);
    try {
      await uploadDocument(file);
      setStatusMessage(`Success: ${file.name} indexed into Chroma vector database.`);
      loadDocs();
    } catch (err: any) {
      setStatusMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete ${name} from the vector database?`)) return;
    try {
      await deleteDocument(id);
      loadDocs();
    } catch (err) {
      console.error("Error deleting document:", err);
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    setStatusMessage("Re-indexing all document chunks in Chroma...");
    try {
      const res = await reindexDocuments();
      setStatusMessage(`Success: Re-indexed ${res.reindexed_documents} documents successfully.`);
      loadDocs();
    } catch (err: any) {
      setStatusMessage(`Reindex error: ${err.message}`);
    } finally {
      setReindexing(false);
    }
  };

  const handleVectorSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const res = await executeToolDirect("search_documents", { query: searchQuery.trim(), top_k: 3 });
      setSearchResults(res.result?.results || []);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="ref-container">
      <div className="flex flex-col items-center mb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/40 border border-cyan-800/50 text-cyan-300 text-xs font-mono mb-3">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          ChromaDB Vector Store: Active Collection
        </div>
        <h2 className="ref-heading">Knowledge Base & RAG Ingestion Engine</h2>
        <p className="text-center text-xs text-slate-400 font-mono max-w-xl">
          Multi-Format Document Ingestion, Recursive Chunking, and Chroma Vector Indexing
        </p>
      </div>

      {statusMessage && (
        <div className="p-3.5 mb-6 bg-emerald-950/40 border border-emerald-500/40 rounded-xl text-center text-xs font-mono font-medium text-emerald-300 backdrop-blur-sm shadow-sm flex items-center justify-center gap-2">
          <span className="text-emerald-400">⚡</span>
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Upload Document Form */}
      <div className="bg-[#0b101d]/80 border border-slate-800/80 rounded-xl p-5 mb-8 backdrop-blur-sm shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 font-mono">
            <span className="text-emerald-400">01 //</span> Document Ingestion & Chunking
          </h3>
          <span className="text-[11px] font-mono text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
            Recursive Splitter (600 / 100 overlap)
          </span>
        </div>

        <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
          <div className="border-2 border-dashed border-slate-800 hover:border-emerald-500/40 rounded-xl p-6 text-center transition-colors bg-slate-900/30">
            <div className="flex flex-col items-center justify-center gap-2">
              <span className="text-2xl">📄</span>
              <p className="text-xs font-mono text-slate-300">
                Choose a document to parse, embed, and index into Chroma vector database
              </p>
              <input
                type="file"
                accept=".pdf,.docx,.txt,.csv,.md"
                onChange={handleFileUpload}
                disabled={uploading}
                className="mt-2 text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-500 file:text-slate-950 hover:file:bg-emerald-400 cursor-pointer font-mono"
              />
              <div className="flex flex-wrap justify-center gap-1.5 mt-3">
                {["PDF", "DOCX", "TXT", "CSV", "MARKDOWN"].map((ext) => (
                  <span key={ext} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                    .{ext.toLowerCase()}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={handleReindex}
              disabled={reindexing}
              className="ref-btn-primary flex items-center gap-2 text-xs"
            >
              {reindexing ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                  <span>Re-indexing Chroma Vector Store...</span>
                </>
              ) : (
                <>
                  <span>↻</span>
                  <span>Reindex All Documents</span>
                </>
              )}
            </button>
            <span className="text-[11px] text-slate-500 font-mono">
              Total Documents: {documents.length}
            </span>
          </div>
        </form>
      </div>

      {/* Semantic Vector Search Sandbox Form */}
      <div className="bg-[#0b101d]/80 border border-slate-800/80 rounded-xl p-5 mb-8 backdrop-blur-sm shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 font-mono">
            <span className="text-cyan-400">02 //</span> Semantic Vector Similarity Playground
          </h3>
          <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/50 px-2 py-0.5 rounded">
            Cosine Similarity (Top K = 3)
          </span>
        </div>

        {/* Quick query presets */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          <span className="text-[11px] font-mono text-slate-500 self-center mr-1">Presets:</span>
          {[
            "restocking fee exception policy",
            "PTO rollover rules and accrual limits",
            "SLA uptime guarantee commitment",
          ].map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => setSearchQuery(q)}
              className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-300 hover:border-cyan-500/40 transition-colors"
            >
              "{q}"
            </button>
          ))}
        </div>

        <form onSubmit={handleVectorSearch} className="space-y-4">
          <div className="ref-form-group">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g. 'restocking fee exception policy', 'PTO rollover rules'..."
              required
              className="w-full bg-[#070b14] border border-slate-800 text-slate-100 placeholder-slate-500 text-sm px-4 py-2.5 rounded-lg focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 font-mono"
            />
          </div>

          <div className="ref-buttons flex items-center gap-2">
            <button
              type="submit"
              disabled={searching}
              className="ref-btn-primary flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
            >
              {searching ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                  <span>Searching Vector Space...</span>
                </>
              ) : (
                <>
                  <span>🔍</span>
                  <span>Execute Vector Search</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={() => { setSearchQuery(""); setSearchResults([]); }}
              className="ref-btn-secondary"
            >
              Clear Search
            </button>
          </div>
        </form>

        {/* Search Results Display */}
        {searchResults.length > 0 && (
          <div className="mt-5 pt-4 border-t border-slate-800/80 space-y-3">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Retrieved Relevant Chunks ({searchResults.length})</span>
              <span className="text-emerald-400 font-bold">Chroma Vector Distance Match</span>
            </div>
            <div className="space-y-2.5">
              {searchResults.map((r, i) => {
                const score = typeof r.similarity_score === "number" ? r.similarity_score : 0.85;
                const scorePercent = Math.min(Math.round(score * 100), 100);
                return (
                  <div key={i} className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-lg">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                      <span className="text-xs font-mono font-bold text-cyan-300">{r.source_citation}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full rounded-full"
                            style={{ width: `${scorePercent}%` }}
                          ></div>
                        </div>
                        <span className="text-[11px] font-mono text-emerald-400 font-bold">
                          {scorePercent}% match
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-300 font-sans leading-relaxed bg-[#070b14] p-3 rounded border border-slate-800/60 font-mono">
                      {r.content}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Indexed Documents Table */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h3 className="ref-subheading mb-0">Indexed Knowledge Base Records ({documents.length})</h3>
          <span className="text-xs font-mono text-slate-400">Embedded in Chroma Vector Space</span>
        </div>
        <table className="ref-table">
          <thead>
            <tr>
              <th style={{ width: "25%" }}>Filename</th>
              <th style={{ width: "10%" }}>Type</th>
              <th style={{ width: "12%" }}>File Size</th>
              <th style={{ width: "12%" }}>Chunks</th>
              <th style={{ width: "15%" }}>Status</th>
              <th style={{ width: "16%" }}>Upload Date</th>
              <th style={{ width: "10%" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-6 text-slate-500 font-mono text-xs">
                  No documents indexed yet. Upload a document above to begin RAG.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id}>
                  <td>
                    <span className="font-mono text-xs font-bold text-slate-100">{doc.filename}</span>
                  </td>
                  <td>
                    <span className="uppercase font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-300">
                      {doc.file_type}
                    </span>
                  </td>
                  <td className="font-mono text-xs text-slate-300">{formatBytes(doc.file_size)}</td>
                  <td>
                    <span className="font-mono text-xs font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-900/60 px-2 py-0.5 rounded">
                      {doc.chunk_count} chunks
                    </span>
                  </td>
                  <td>
                    <span className="text-emerald-400 font-mono text-xs font-bold flex items-center gap-1">
                      <span>✓</span> {doc.status}
                    </span>
                  </td>
                  <td className="font-mono text-xs text-slate-400">{formatDate(doc.created_at)}</td>
                  <td className="text-center">
                    <button
                      onClick={() => handleDelete(doc.id, doc.filename)}
                      className="text-xs font-mono text-red-400 hover:text-red-300 hover:underline transition-colors"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Navigation Links */}
      <div className="ref-link mt-8 pt-4 border-t border-slate-800">
        <Link href="/">Back to Dashboard</Link> | 
        <Link href="/chat">Open Agent Workspace</Link> | 
        <Link href="/memory">View Persistent Memories</Link> | 
        <Link href="/tools">Inspect Tool Logs</Link>
      </div>
    </div>
  );
}
