export interface ExecutionStepInfo {
  step_name: string;
  status: 'completed' | 'running' | 'failed' | 'skipped';
  duration_ms: number;
  description: string;
  details?: any;
}

export interface AgentPlan {
  objective: string;
  steps: string[];
  required_tools: string[];
  reasoning: string;
}

export interface AgentChatResponse {
  task_id: string;
  conversation_id: string;
  answer: string;
  sources: string[];
  tools_used: string[];
  confidence: string;
  execution_steps: ExecutionStepInfo[];
  plan?: AgentPlan;
  duration_ms: number;
}

export interface MessageItem {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: string[];
  tools_used?: string[];
  execution_steps?: ExecutionStepInfo[];
  confidence?: string;
  created_at: string;
}

export interface ConversationItem {
  id: string;
  title: string;
  summary?: string;
  message_count: number;
  last_message?: string;
  updated_at: string;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: 'pending' | 'indexing' | 'indexed' | 'error';
  doc_metadata: Record<string, any>;
  created_at: string;
}

export interface MemoryItem {
  id: string;
  user_id: string;
  category: 'preference' | 'fact' | 'task_context' | 'entity';
  content: string;
  importance: number;
  confidence: number;
  source_task_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ToolInfo {
  name: string;
  description: string;
  category: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface ToolExecutionLog {
  id: string;
  task_id?: string;
  tool_name: string;
  arguments: Record<string, any>;
  result?: any;
  status: string;
  duration_ms: number;
  created_at: string;
}

export interface DashboardStats {
  total_documents: number;
  indexed_chunks: number;
  total_conversations: number;
  total_tasks: number;
  total_tool_calls: number;
  total_memories: number;
  avg_latency_seconds: number;
  system_status: string;
  recent_activity: Array<{
    id: string;
    objective: string;
    status: string;
    duration_s: number;
    created_at: string;
  }>;
}
