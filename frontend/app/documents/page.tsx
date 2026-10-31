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
      <h2 className="ref-heading">Knowledge Base & RAG Document Management</h2>
      <p className="text-center text-xs text-slate-600 font-medium mb-6">
        Multi-Format Document Ingestion, Recursive Chunking, and Chroma Vector Indexing
      </p>

      {statusMessage && (
        <div className="p-3 mb-5 bg-blue-50 border border-blue-300 rounded text-center text-xs font-bold text-[#1e3a8a]">
          {statusMessage}
        </div>
      )}

      {/* Upload Document Form */}
      <h3 className="ref-subheading">Document Ingestion Form</h3>
      <form onSubmit={(e) => e.preventDefault()}>
        <div className="ref-form-group">
          <label>Select Document File:</label>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.csv,.md"
            onChange={handleFileUpload}
            disabled={uploading}
          />
        </div>

        <div className="ref-form-group">
          <label>Supported Formats:</label>
          <input type="text" value="PDF (.pdf), Word (.docx), Plain Text (.txt), CSV (.csv)" readOnly />
        </div>

        <div className="ref-form-group">
          <label>Chunking Strategy:</label>
          <input type="text" value="Recursive Character Splitter (600 chars, 100 overlap)" readOnly />
        </div>

        <div className="ref-buttons">
          <input
            type="button"
            value={reindexing ? "Reindexing..." : "Reindex All Documents"}
            onClick={handleReindex}
            disabled={reindexing}
            className="ref-btn-primary"
          />
        </div>
      </form>

      {/* Semantic Vector Search Sandbox Form */}
      <h3 className="ref-subheading">Semantic Vector Similarity Search</h3>
      <form onSubmit={handleVectorSearch}>
        <div className="ref-form-group">
          <label>Semantic Search Query:</label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="e.g. 'restocking fee exception policy', 'PTO rollover rules'..."
            required
          />
        </div>

        <div className="ref-buttons">
          <input
            type="submit"
            value={searching ? "Searching Vector Store..." : "Execute Vector Search"}
            disabled={searching}
            className="ref-btn-primary"
          />
          <input
            type="button"
            value="Clear Search"
            onClick={() => { setSearchQuery(""); setSearchResults([]); }}
            className="ref-btn-secondary"
          />
        </div>
      </form>

      {/* Search Results Display */}
      {searchResults.length > 0 && (
        <div className="mt-4 mb-6">
          <h4 className="text-xs font-bold text-[#1e3a8a] mb-2">Chroma Semantic Search Results:</h4>
          <div className="space-y-2">
            {searchResults.map((r, i) => (
              <div key={i} className="p-3 bg-slate-50 border border-slate-300 rounded text-xs">
                <div className="flex justify-between font-bold text-[#1e3a8a] mb-1">
                  <span>{r.source_citation}</span>
                  <span className="text-emerald-700">Similarity Score: {r.similarity_score}</span>
                </div>
                <p className="text-slate-700">{r.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Indexed Documents Table (Page 9 Style) */}
      <h3 className="ref-subheading">Indexed Knowledge Base Records</h3>
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
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td><b>{doc.filename}</b></td>
              <td className="uppercase font-bold text-slate-600">{doc.file_type}</td>
              <td>{formatBytes(doc.file_size)}</td>
              <td><b className="text-emerald-700">{doc.chunk_count} chunks</b></td>
              <td><span className="text-green-700 font-bold">&#10004; {doc.status}</span></td>
              <td>{formatDate(doc.created_at)}</td>
              <td className="text-center">
                <button
                  onClick={() => handleDelete(doc.id, doc.filename)}
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
        <Link href="/memory">View Persistent Memories</Link> | 
        <Link href="/tools">Inspect Tool Logs</Link>
      </div>
    </div>
  );
}
