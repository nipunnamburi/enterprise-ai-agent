import {
  AgentChatResponse,
  DashboardStats,
  DocumentItem,
  MemoryItem,
  ToolInfo,
  ToolExecutionLog,
  ConversationItem
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/dashboard/stats`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
  return res.json();
}

export async function sendAgentChat(message: string, conversationId?: string): Promise<AgentChatResponse> {
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      user_id: "demo-user-123"
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Agent execution failed");
  }
  return res.json();
}

export async function fetchConversations(): Promise<ConversationItem[]> {
  const res = await fetch(`${API_BASE}/conversations`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

export async function fetchConversationDetails(id: string) {
  const res = await fetch(`${API_BASE}/conversations/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch conversation messages");
  return res.json();
}

export async function deleteConversation(id: string) {
  const res = await fetch(`${API_BASE}/conversations/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete conversation");
  return res.json();
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch indexed documents");
  return res.json();
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Upload failed");
  }
  return res.json();
}

export async function deleteDocument(id: string) {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete document");
  return res.json();
}

export async function reindexDocuments() {
  const res = await fetch(`${API_BASE}/documents/reindex`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reindex documents");
  return res.json();
}

export async function fetchMemories(): Promise<MemoryItem[]> {
  const res = await fetch(`${API_BASE}/memory`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch long-term memories");
  return res.json();
}

export async function createMemory(category: string, content: string, importance: number = 1.0) {
  const res = await fetch(`${API_BASE}/memory`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ category, content, importance, confidence: 1.0 }),
  });
  if (!res.ok) throw new Error("Failed to create memory");
  return res.json();
}

export async function deleteMemory(id: string) {
  const res = await fetch(`${API_BASE}/memory/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete memory");
  return res.json();
}

export async function fetchTools(): Promise<ToolInfo[]> {
  const res = await fetch(`${API_BASE}/tools`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch tools registry");
  return res.json();
}

export async function fetchToolAuditLogs(): Promise<ToolExecutionLog[]> {
  const res = await fetch(`${API_BASE}/tools/audit`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch tool audit logs");
  return res.json();
}

export async function executeToolDirect(tool_name: string, args: Record<string, any>) {
  const res = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool_name, arguments: args }),
  });
  if (!res.ok) throw new Error("Tool execution failed");
  return res.json();
}
