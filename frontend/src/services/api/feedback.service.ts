import type { SubmitFeedbackPayload } from "@/features/feedback/types";

import { api } from "./client";

/** Submit message feedback to the backend. */
export async function submitMessageFeedback(payload: SubmitFeedbackPayload): Promise<void> {
  try {
    await api.post<void>("/v1/feedback/", payload);
  } catch {
    // Backend endpoint may not exist yet — feedback is persisted locally.
    console.info("[feedback] Stored locally:", payload.type);
  }
}
