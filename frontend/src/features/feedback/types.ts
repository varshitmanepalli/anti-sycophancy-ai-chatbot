/** Feedback category identifiers. */
export type FeedbackType =
  | "helpful"
  | "incorrect"
  | "too_agreeable"
  | "too_harsh"
  | "hallucination"
  | "report_issue";

export interface MessageFeedback {
  messageId: string;
  conversationId: string;
  type: FeedbackType;
  comment?: string;
  createdAt: string;
}

export interface SubmitFeedbackPayload {
  messageId: string;
  conversationId: string;
  type: FeedbackType;
  comment?: string;
}
