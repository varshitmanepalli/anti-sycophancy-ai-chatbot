import { create } from "zustand";
import { persist } from "zustand/middleware";

import { STORAGE_KEYS } from "@/config";
import type { ReasoningStep } from "@/types";

interface ReasoningPanelState {
  /** Per-conversation panel expanded state. */
  expandedByConversation: Record<string, boolean>;
  reasoningSteps: ReasoningStep[];
  lastConfidence: number | null;

  isExpanded: (conversationId: string) => boolean;
  setExpanded: (conversationId: string, expanded: boolean) => void;
  toggleExpanded: (conversationId: string) => void;
  setReasoningSteps: (steps: ReasoningStep[]) => void;
  setLastConfidence: (confidence: number | null) => void;
  resetForConversation: (conversationId: string) => void;
}

export const useReasoningPanelStore = create<ReasoningPanelState>()(
  persist(
    (set, get) => ({
      expandedByConversation: {},
      reasoningSteps: [],
      lastConfidence: null,

      isExpanded: (conversationId) => get().expandedByConversation[conversationId] ?? false,

      setExpanded: (conversationId, expanded) =>
        set((state) => ({
          expandedByConversation: {
            ...state.expandedByConversation,
            [conversationId]: expanded,
          },
        })),

      toggleExpanded: (conversationId) =>
        set((state) => ({
          expandedByConversation: {
            ...state.expandedByConversation,
            [conversationId]: !state.expandedByConversation[conversationId],
          },
        })),

      setReasoningSteps: (reasoningSteps) => set({ reasoningSteps }),

      setLastConfidence: (lastConfidence) => set({ lastConfidence }),

      resetForConversation: (conversationId) =>
        set((state) => {
          const { [conversationId]: _, ...rest } = state.expandedByConversation;
          return {
            expandedByConversation: rest,
            reasoningSteps: [],
            lastConfidence: null,
          };
        }),
    }),
    {
      name: STORAGE_KEYS.reasoningPanel,
      partialize: (state) => ({
        expandedByConversation: state.expandedByConversation,
      }),
    },
  ),
);
