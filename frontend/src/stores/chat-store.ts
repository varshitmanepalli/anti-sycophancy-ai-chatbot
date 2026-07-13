import { create } from "zustand";
import { persist } from "zustand/middleware";

import { STORAGE_KEYS } from "@/config";
import type { ChatMode } from "@/types";

interface ChatUiState {
  chatMode: ChatMode;
  isSidebarOpen: boolean;

  setChatMode: (mode: ChatMode) => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useChatStore = create<ChatUiState>()(
  persist(
    (set) => ({
      chatMode: "standard",
      isSidebarOpen: false,

      setChatMode: (chatMode) => set({ chatMode }),

      setSidebarOpen: (isSidebarOpen) => set({ isSidebarOpen }),

      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    }),
    {
      name: STORAGE_KEYS.chatUi,
      partialize: (state) => ({ chatMode: state.chatMode }),
      merge: (persisted, current) => {
        const merged = { ...current, ...(persisted as Partial<ChatUiState>) };
        migrateLegacyChatMode(merged);
        return merged;
      },
    },
  ),
);

function migrateLegacyChatMode(state: ChatUiState): void {
  if (typeof window === "undefined") return;
  if (state.chatMode !== "standard") return;

  try {
    const raw = localStorage.getItem(STORAGE_KEYS.chat);
    if (!raw) return;
    const legacy = JSON.parse(raw) as { chatMode?: ChatMode };
    if (legacy.chatMode) state.chatMode = legacy.chatMode;
  } catch {
    // ignore
  }
}
