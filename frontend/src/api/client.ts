import { AIRequest, AIResponse, UsageHistoryItem } from "./types";

const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function sendAIRequest(req: AIRequest): Promise<AIResponse> {
  const res = await fetch(`${baseUrl}/api/v1/ai`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.error?.message || "Request failed");
  }
  return data as AIResponse;
}

export async function streamAIRequest(
  req: AIRequest,
  onChunk: (text: string) => void,
  onEnd: (meta: { usage: any; model: string; task: string; estimated_cost: number; id: string }) => void,
  onError: (message: string) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${baseUrl}/api/v1/ai/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  });

  if (!res.body) {
    onError("No stream body");
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const evt of events) {
      const lines = evt.split("\n");
      let eventType = "message";
      let dataStr = "";
      for (const line of lines) {
        if (line.startsWith("event:")) eventType = line.replace("event:", "").trim();
        else if (line.startsWith("data:")) dataStr += line.replace("data:", "").trim();
      }
      if (!dataStr) continue;
      try {
        const data = JSON.parse(dataStr);
        if (eventType === "chunk") onChunk(data.text || "");
        if (eventType === "end") onEnd(data);
        if (eventType === "error") onError(data.message || "Streaming error");
      } catch (err) {
        onError("Failed to parse stream");
      }
    }
  }
}

export async function getRecentUsage(): Promise<UsageHistoryItem[]> {
  const res = await fetch(`${baseUrl}/api/v1/usage/recent`);
  const data = await res.json();
  if (!res.ok) throw new Error(data?.error?.message || "Failed to fetch usage");
  return data.items as UsageHistoryItem[];
}
