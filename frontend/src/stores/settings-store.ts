import { create } from "zustand";
import { persist } from "zustand/middleware";

import { STORAGE_KEYS } from "@/config";

import type { UserSettings } from "./types";

interface SettingsState {
  settings: UserSettings;
  updateSettings: (updates: Partial<UserSettings>) => void;
  resetSettings: () => void;
}

const defaultSettings: UserSettings = {
  emailNotifications: true,
  streamResponses: true,
  showConfidence: true,
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      settings: defaultSettings,

      updateSettings: (updates) =>
        set((state) => ({
          settings: { ...state.settings, ...updates },
        })),

      resetSettings: () => set({ settings: defaultSettings }),
    }),
    {
      name: STORAGE_KEYS.settings,
      partialize: (state) => ({ settings: state.settings }),
      merge: (persisted, current) => {
        const merged = { ...current, ...(persisted as Partial<SettingsState>) };
        migrateLegacyUserSettings(merged);
        return merged;
      },
    },
  ),
);

function migrateLegacyUserSettings(state: SettingsState): void {
  if (typeof window === "undefined") return;

  const hasNonDefaults =
    state.settings.emailNotifications !== defaultSettings.emailNotifications ||
    state.settings.streamResponses !== defaultSettings.streamResponses ||
    state.settings.showConfidence !== defaultSettings.showConfidence;

  if (hasNonDefaults) return;

  try {
    const raw = localStorage.getItem(STORAGE_KEYS.user);
    if (!raw) return;
    const legacy = JSON.parse(raw) as { settings?: UserSettings };
    if (legacy.settings) state.settings = legacy.settings;
  } catch {
    // ignore
  }
}

