import { create } from "zustand";

import type { ThemePreference } from "./types";

interface ThemeState {
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>()((set, get) => ({
  theme: "system",

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
