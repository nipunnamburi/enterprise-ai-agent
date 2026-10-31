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

let cachedToken: string | null = null;

async function getAuthToken(): Promise<string> {
  if (cachedToken) return cachedToken;
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("enterprise_auth_token");
    if (stored) {
      cachedToken = stored;
      return stored;
    }
  }

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "analyst@enterprise.ai",
        password: "password123",
      }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.access_token) {
        cachedToken = data.access_token;
        if (typeof window !== "undefined") {
          localStorage.setItem("enterprise_auth_token", data.access_token);
        }
        return data.access_token;
      }
    }
  } catch {
    // ignore login fallback errors
  }
  return "";
}

async function authHeaders(existingHeaders: Record<string, string> = {}): Promise<Record<string, string>> {
  const token = await getAuthToken();
  const headers = { ...existingHeaders };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/dashboard/stats`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
  return res.json();
}

export async function sendAgentChat(message: string, conversationId?: string): Promise<AgentChatResponse> {
  const headers = await authHeaders({ "Content-Type": "application/json" });
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: "POST",
    headers,
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
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/conversations`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

export async function fetchConversationDetails(id: string) {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/conversations/${id}`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch conversation messages");
  return res.json();
}

export async function deleteConversation(id: string) {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/conversations/${id}`, { method: "DELETE", headers });
  if (!res.ok) throw new Error("Failed to delete conversation");
  return res.json();
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/documents`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch indexed documents");
  return res.json();
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers,
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Upload failed");
  }
  return res.json();
}

export async function deleteDocument(id: string) {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE", headers });
  if (!res.ok) throw new Error("Failed to delete document");
  return res.json();
}

export async function reindexDocuments() {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/documents/reindex`, { method: "POST", headers });
  if (!res.ok) throw new Error("Failed to reindex documents");
  return res.json();
}

export async function fetchMemories(): Promise<MemoryItem[]> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/memory`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch long-term memories");
  return res.json();
}

export async function createMemory(category: string, content: string, importance: number = 1.0) {
  const headers = await authHeaders({ "Content-Type": "application/json" });
  const res = await fetch(`${API_BASE}/memory`, {
    method: "POST",
    headers,
    body: JSON.stringify({ category, content, importance, confidence: 1.0 }),
  });
  if (!res.ok) throw new Error("Failed to create memory");
  return res.json();
}

export async function deleteMemory(id: string) {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/memory/${id}`, { method: "DELETE", headers });
  if (!res.ok) throw new Error("Failed to delete memory");
  return res.json();
}

export async function fetchTools(): Promise<ToolInfo[]> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/tools`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch tools registry");
  return res.json();
}

export async function fetchToolAuditLogs(): Promise<ToolExecutionLog[]> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/tools/audit`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch tool audit logs");
  return res.json();
}

export async function executeToolDirect(tool_name: string, args: Record<string, any>) {
  const headers = await authHeaders({ "Content-Type": "application/json" });
  const res = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers,
    body: JSON.stringify({ tool_name, arguments: args }),
  });
  if (!res.ok) throw new Error("Tool execution failed");
  return res.json();
}

export async function executeDeepResearch(topic: string, depth: number = 2, focus_areas?: string[]) {
  const headers = await authHeaders({ "Content-Type": "application/json" });
  const res = await fetch(`${API_BASE}/agent/research`, {
    method: "POST",
    headers,
    body: JSON.stringify({ topic, depth, focus_areas }),
  });
  if (!res.ok) throw new Error("Deep research request failed");
  return res.json();
}
