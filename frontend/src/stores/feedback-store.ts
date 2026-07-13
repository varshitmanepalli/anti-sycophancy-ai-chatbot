import { create } from "zustand";
import { persist } from "zustand/middleware";

import { STORAGE_KEYS } from "@/config";

import type { FeedbackType, MessageFeedback, SubmitFeedbackPayload } from "@/features/feedback/types";

interface FeedbackState {
  byMessageId: Record<string, MessageFeedback>;
  submitFeedback: (payload: SubmitFeedbackPayload) => void;
  getFeedback: (messageId: string) => MessageFeedback | null;
  clearFeedback: (messageId: string) => void;
}

export const useFeedbackStore = create<FeedbackState>()(
  persist(
    (set, get) => ({
      byMessageId: {},

      submitFeedback: ({ messageId, conversationId, type, comment }) =>
        set((state) => ({
          byMessageId: {
            ...state.byMessageId,
            [messageId]: {
              messageId,
              conversationId,
              type,
              comment,
              createdAt: new Date().toISOString(),
            },
          },
        })),

      getFeedback: (messageId) => get().byMessageId[messageId] ?? null,

      clearFeedback: (messageId) =>
        set((state) => {
          const { [messageId]: _, ...rest } = state.byMessageId;
          return { byMessageId: rest };
        }),
    }),
    {
      name: STORAGE_KEYS.feedback,
      partialize: (state) => ({ byMessageId: state.byMessageId }),
    },
  ),
);

export function isPositiveFeedback(type: FeedbackType): boolean {
  return type === "helpful";
}
