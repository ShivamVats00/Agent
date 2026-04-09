export type AgentRole = "user" | "agent" | "system";

export interface Message {
  id: string;
  role: AgentRole;
  content: string;
  timestamp: string;
}

export interface ToolCall {
  id: string;
  tool: string;
  args: Record<string, unknown>;
  status: "pending" | "success" | "error";
  result?: string;
  timestamp: string;
}

export interface NodeEvent {
  node: string;
  timestamp: string;
  message?: string;
}

export interface AgentState {
  isProcessing: boolean;
  currentNode: string | null;
  stepCount: number;
  messages: Message[];
  toolCalls: ToolCall[];
  nodeHistory: NodeEvent[];
  requiresApproval: boolean;
  approvalSummary: string | null;
  error: string | null;
}

export interface StreamEvent {
  type: string;
  timestamp: string;
  data: Record<string, unknown>;
}
