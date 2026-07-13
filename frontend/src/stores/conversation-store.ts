import { create } from "zustand";
import { persist } from "zustand/middleware";

import { STORAGE_KEYS } from "@/config";
import type { Conversation, Message, StructuredReasoning } from "@/types";
import { generateId, truncate } from "@/utils";

interface ConversationState {
  conversations: Record<string, Conversation>;
  activeConversationId: string | null;

  setActiveConversation: (id: string | null) => void;
  createConversation: (mode?: Conversation["mode"]) => string;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, title: string) => void;
  togglePinConversation: (id: string) => void;
  clearAllConversations: () => void;

  addMessage: (conversationId: string, message: Omit<Message, "id" | "createdAt">) => string;
  updateMessage: (conversationId: string, messageId: string, content: string) => void;
  deleteMessage: (conversationId: string, messageId: string) => void;
  editMessage: (conversationId: string, messageId: string, content: string) => void;
  truncateMessagesAfter: (conversationId: string, messageId: string, inclusive?: boolean) => void;

  updateMessageMeta: (
    conversationId: string,
    messageId: string,
    patch: Partial<Message>,
  ) => void;

  setStructuredReasoning: (
    conversationId: string,
    reasoning: StructuredReasoning | null,
  ) => void;

  getActiveConversation: () => Conversation | null;
  getConversationList: () => Conversation[];
  getConversation: (id: string) => Conversation | null;
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set, get) => ({
      conversations: {},
      activeConversationId: null,

      setActiveConversation: (id) => set({ activeConversationId: id }),

      createConversation: (mode) => {
        const id = generateId();
        const now = new Date().toISOString();
        const conversation: Conversation = {
          id,
          title: "New conversation",
          messages: [],
          createdAt: now,
          updatedAt: now,
          mode: mode ?? "standard",
        };
        set((state) => ({
          conversations: { ...state.conversations, [id]: conversation },
          activeConversationId: id,
        }));
        return id;
      },

      deleteConversation: (id) =>
        set((state) => {
          const { [id]: _, ...rest } = state.conversations;
          const nextActive =
            state.activeConversationId === id
              ? (Object.keys(rest)[0] ?? null)
              : state.activeConversationId;
          return { conversations: rest, activeConversationId: nextActive };
        }),

      renameConversation: (id, title) =>
        set((state) => {
          const conversation = state.conversations[id];
          if (!conversation) return state;
          const trimmed = title.trim();
          if (!trimmed) return state;
          return {
            conversations: {
              ...state.conversations,
              [id]: { ...conversation, title: trimmed, updatedAt: new Date().toISOString() },
            },
          };
        }),

      togglePinConversation: (id) =>
        set((state) => {
          const conversation = state.conversations[id];
          if (!conversation) return state;
          const pinned = !conversation.pinned;
          return {
            conversations: {
              ...state.conversations,
              [id]: {
                ...conversation,
                pinned,
                pinnedAt: pinned ? new Date().toISOString() : null,
              },
            },
          };
        }),

      clearAllConversations: () =>
        set({ conversations: {}, activeConversationId: null }),

      addMessage: (conversationId, message) => {
        const messageId = generateId();
        const now = new Date().toISOString();
        set((state) => {
          const conversation = state.conversations[conversationId];
          if (!conversation) return state;

          const isFirstUserMessage =
            message.role === "user" && conversation.messages.length === 0;

          return {
            conversations: {
              ...state.conversations,
              [conversationId]: {
                ...conversation,
                title: isFirstUserMessage ? truncate(message.content, 40) : conversation.title,
                messages: [
                  ...conversation.messages,
                  { ...message, id: messageId, createdAt: now },
                ],
                updatedAt: now,
              },
            },
          };
        });
        return messageId;
      },

      updateMessage: (conversationId, messageId, content) =>
        set((state) => {
          const conversation = state.conversations[conversationId];
          if (!conversation) return state;
          return {
            conversations: {
              ...state.conversations,
              [conversationId]: {
                ...conversation,
                messages: conversation.messages.map((m) =>
                  m.id === messageId ? { ...m, content } : m,
                ),
                updatedAt: new Date().toISOString(),
              },
            },
          };
        }),

      updateMessageMeta: (conversationId, messageId, patch) =>
        set((state) => {
          const conversation = state.conversations[conversationId];
          if (!conversation) return state;
          return {
            conversations: {
              ...state.conversations,
              [conversationId]: {
                ...conversation,
                messages: conversation.messages.map((m) =>
                  m.id === messageId ? { ...m, ...patch } : m,
                ),
              },
            },
          };
        }),

      deleteMessage: (conversationId, messageId) =>
        set((state) => {
          const conversation = state.conversations[conversationId];
          if (!conversation) return state;
          return {
            conversations: {
              ...state.conversations,
              [conversationId]: {
                ...conversation,
                messages: conversation.messages.filter((m) => m.id !== messageId),
                updatedAt: new Date().toISOString(),
              },
            },
          };
        }),

      editMessage: (conversationId, messageId, content) =>
        set((state) => {
          const conversation = state.conversations[conversationId];
          if (!conversation) return state;
          const message = conversation.messages.find((m) => m.id === messageId);
          const isFirstUserMessage =
            message?.role === "user" &&
            conversation.messages.findIndex((m) => m.role === "user") ===
              conversation.messages.findIndex((m) => m.id === messageId);

          return {
            conversations: {
              ...state.conversations,
              [conversationId]: {
                ...conversation,
                title: isFirstUserMessage ? truncate(content, 40) : conversation.title,
                messages: conversation.messages.map((m) =>
                  m.id === messageId ? { ...m, content, error: null } : m,
                ),
                updatedAt: new Date().toISOString(),
              },
            },
          };
        }),

      truncateMessagesAfter: (conversationId, messageId, inclusive = false) =>
        set((state) => {
          const conversation = state.conversations[conversationId];
          if (!conversation) return state;
          const index = conversation.messages.findIndex((m) => m.id === messageId);
          if (index === -1) return state;
          const endIndex = inclusive ? index : index + 1;
          return {
            conversations: {
              ...state.conversations,
              [conversationId]: {
                ...conversation,
                messages: conversation.messages.slice(0, endIndex),
                updatedAt: new Date().toISOString(),
              },
            },
          };
        }),

      setStructuredReasoning: (conversationId, reasoning) =>
        set((state) => {
          const conversation = state.conversations[conversationId];
          if (!conversation) return state;
          return {
            conversations: {
              ...state.conversations,
              [conversationId]: { ...conversation, structuredReasoning: reasoning },
            },
          };
        }),

      getActiveConversation: () => {
        const { activeConversationId, conversations } = get();
        return activeConversationId ? (conversations[activeConversationId] ?? null) : null;
      },

      getConversation: (id) => get().conversations[id] ?? null,

      getConversationList: () => {
        const { conversations } = get();
        return Object.values(conversations).sort((a, b) => {
          if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
          if (a.pinned && b.pinned) {
            const aPin = a.pinnedAt ? new Date(a.pinnedAt).getTime() : 0;
            const bPin = b.pinnedAt ? new Date(b.pinnedAt).getTime() : 0;
            if (aPin !== bPin) return bPin - aPin;
          }
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        });
      },
    }),
    {
      name: STORAGE_KEYS.conversation,
      partialize: (state) => ({
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
      }),
      merge: (persisted, current) => {
        const merged = { ...current, ...(persisted as Partial<ConversationState>) };
        migrateLegacyChatStorage(merged);
        return merged;
      },
    },
  ),
);

/** One-time migration from the legacy combined chat store key. */
function migrateLegacyChatStorage(state: ConversationState): void {
  if (typeof window === "undefined") return;
  if (Object.keys(state.conversations).length > 0) return;

  try {
    const raw = localStorage.getItem(STORAGE_KEYS.chat);
    if (!raw) return;
    const legacy = JSON.parse(raw) as {
      conversations?: Record<string, Conversation>;
      activeConversationId?: string | null;
    };
    if (legacy.conversations) state.conversations = legacy.conversations;
    if (legacy.activeConversationId) state.activeConversationId = legacy.activeConversationId;
  } catch {
    // ignore corrupt legacy data
  }
}
