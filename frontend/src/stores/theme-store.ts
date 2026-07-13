import { create } from "zustand";

import type { ThemePreference } from "./types";

interface ThemeState {
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>()((set, get) => ({
  // Match ThemeProvider defaultTheme to avoid a sync race on mount.
  theme: "dark",

  setTheme: (theme) => set({ theme }),

  toggleTheme: () => {
    const current = get().theme;
    if (current === "dark") {
      set({ theme: "light" });
    } else {
      set({ theme: "dark" });
    }
  },
}));
