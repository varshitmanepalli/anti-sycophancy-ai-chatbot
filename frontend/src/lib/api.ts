/**
 * API client and backend communication layer.
 *
 * All HTTP calls to the FastAPI backend go through this module.
 * Components should never call fetch() directly.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export async function sendMessage(
  message: string,
  conversationId?: string,
): Promise<{ conversation_id: string; message: string }> {
  const response = await fetch(`${API_BASE}/v1/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
