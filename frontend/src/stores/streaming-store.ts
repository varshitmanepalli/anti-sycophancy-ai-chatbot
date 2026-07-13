import { create } from "zustand";

import type { ActiveStream, ChatMode, StreamPhase } from "@/types";

import { useConversationStore } from "./conversation-store";

export interface PendingStreamReply {
  conversationId: string;
  userContent: string;
  mode: ChatMode;
  existingAssistantId?: string;
}

interface StreamingState {
  activeStream: ActiveStream | null;
  pendingReply: PendingStreamReply | null;

  setActiveStream: (stream: ActiveStream | null) => void;
  setPendingReply: (reply: PendingStreamReply | null) => void;

  setMessageStreaming: (conversationId: string, messageId: string, streaming: boolean) => void;
  setMessageStreamPhase: (
    conversationId: string,
    messageId: string,
    phase: StreamPhase,
  ) => void;
  setMessageAborted: (conversationId: string, messageId: string) => void;
  setMessageError: (conversationId: string, messageId: string, error: string | null) => void;

  clearStream: () => void;
}

export const useStreamingStore = create<StreamingState>()((set, get) => ({
  activeStream: null,
  pendingReply: null,

  setActiveStream: (activeStream) => set({ activeStream }),

  setPendingReply: (pendingReply) => set({ pendingReply }),

  setMessageStreaming: (conversationId, messageId, streaming) => {
    useConversationStore.getState().updateMessageMeta(conversationId, messageId, {
      isStreaming: streaming,
      streamPhase: streaming ? "connecting" : undefined,
      error: streaming ? null : undefined,
      wasAborted: streaming ? false : undefined,
    });
  },

  setMessageStreamPhase: (conversationId, messageId, phase) => {
    const isStreaming =
      phase === "connecting" || phase === "streaming" || phase === "reconnecting";

    useConversationStore.getState().updateMessageMeta(conversationId, messageId, {
      streamPhase: phase,
      isStreaming,
    });
  },

  setMessageAborted: (conversationId, messageId) => {
    useConversationStore.getState().updateMessageMeta(conversationId, messageId, {
      isStreaming: false,
      streamPhase: "aborted",
      wasAborted: true,
      error: null,
    });
    set({ activeStream: null });
  },

  setMessageError: (conversationId, messageId, error) => {
    const { activeStream } = get();
    useConversationStore.getState().updateMessageMeta(conversationId, messageId, {
      error,
      isStreaming: false,
      streamPhase: error ? "error" : undefined,
    });

    set({
      activeStream:
        error && activeStream?.messageId === messageId
          ? { ...activeStream, phase: "error" }
          : error
            ? null
            : activeStream,
    });
  },

  clearStream: () => set({ activeStream: null, pendingReply: null }),
}));
