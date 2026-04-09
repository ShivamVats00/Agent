const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function submitChat(message: string, threadId?: string, requireApproval = false) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId, require_approval: requireApproval }),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function submitApproval(threadId: string, decision: "approved" | "rejected") {
  const res = await fetch(`${API_BASE_URL}/approve/${threadId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision }),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function fetchThreads() {
  const res = await fetch(`${API_BASE_URL}/threads`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}
