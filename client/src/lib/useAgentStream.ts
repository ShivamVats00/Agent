import { useState, useCallback, useRef } from "react";
import { AgentState, StreamEvent } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const INITIAL_STATE: AgentState = {
  isProcessing: false,
  currentNode: null,
  stepCount: 0,
  messages: [],
  toolCalls: [],
  nodeHistory: [],
  requiresApproval: false,
  approvalSummary: null,
  error: null,
};

export function useAgentStream() {
  const [state, setState] = useState<AgentState>(INITIAL_STATE);
  const eventSourceRef = useRef<EventSource | null>(null);
  const tokenBufferRef = useRef<string>("");

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  const sendTask = useCallback((message: string, threadId: string) => {
    setState(prev => ({
      ...prev,
      isProcessing: true,
      currentNode: "start",
      requiresApproval: false,
      approvalSummary: null,
      error: null,
      messages: [...prev.messages, {
        id: Date.now().toString(),
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      }],
    }));

    disconnect();
    tokenBufferRef.current = "";

    const url = new URL(`${API_BASE_URL}/chat/stream/${threadId}`);
    url.searchParams.append("message", message);

    const es = new EventSource(url.toString());
    eventSourceRef.current = es;
    const aiMessageId = `ai-${Date.now()}`;

    es.onmessage = (event) => {
      try {
        const { type, data, timestamp }: StreamEvent = JSON.parse(event.data);

        setState(prev => {
          const next = { ...prev };

          switch (type) {
            case "node_start":
              next.currentNode = data.node as string;
              if (data.node === "human_gate") {
                next.requiresApproval = true;
                next.approvalSummary = "Agent requires permission to proceed.";
              }
              next.nodeHistory = [...next.nodeHistory, {
                node: data.node as string, timestamp, message: data.message as string,
              }];
              break;

            case "node_end":
              if (data.step) next.stepCount = data.step as number;
              break;

            case "tool_call":
              next.toolCalls = [...next.toolCalls, {
                id: data.id as string,
                tool: data.tool as string,
                args: data.args as Record<string, unknown>,
                status: "pending",
                timestamp,
              }];
              break;

            case "tool_result":
              next.toolCalls = next.toolCalls.map(tc =>
                tc.tool === data.tool && tc.status === "pending"
                  ? { ...tc, status: "success" as const, result: data.content as string }
                  : tc
              );
              break;

            case "token":
              tokenBufferRef.current += data.content as string;
              const idx = next.messages.findIndex(m => m.id === aiMessageId);
              if (idx >= 0) {
                const updated = [...next.messages];
                updated[idx] = { ...updated[idx], content: tokenBufferRef.current };
                next.messages = updated;
              } else {
                next.messages = [...next.messages, {
                  id: aiMessageId, role: "agent",
                  content: tokenBufferRef.current, timestamp,
                }];
              }
              break;

            case "ai_message":
              // Fallback: use full content if token streaming didn't fire
              if (!tokenBufferRef.current) {
                next.messages = [...next.messages, {
                  id: `ai-${Date.now()}`, role: "agent",
                  content: data.content as string, timestamp,
                }];
              }
              break;

            case "complete":
              next.isProcessing = false;
              next.currentNode = "end";
              es.close();
              break;

            case "error":
              next.isProcessing = false;
              next.error = typeof data.message === "string" ? data.message : JSON.stringify(data);
              es.close();
              break;
          }

          return next;
        });
      } catch (e) {
        console.error("SSE parse error:", e);
      }
    };

    es.onerror = () => {
      // Don't show errors for clean disconnects (e.g. graph interrupt)
      setState(prev => prev.requiresApproval ? prev : { ...prev, isProcessing: false });
      es.close();
    };
  }, [disconnect]);

  return { state, setState, sendTask, disconnect };
}
