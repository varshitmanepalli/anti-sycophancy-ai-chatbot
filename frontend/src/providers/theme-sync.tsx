"use client";

import { useEffect } from "react";
import { useTheme } from "next-themes";

import { useThemeStore } from "@/stores/theme-store";
import type { ThemePreference } from "@/stores/types";

/** Keeps Zustand theme preference in sync with next-themes. */
export function ThemeStoreSync() {
  const { theme: resolvedTheme, setTheme } = useTheme();
  const storeTheme = useThemeStore((s) => s.theme);
  const setStoreTheme = useThemeStore((s) => s.setTheme);

  useEffect(() => {
    if (!resolvedTheme) return;
    const preference = resolvedTheme as ThemePreference;
    if (preference !== storeTheme) {
      setStoreTheme(preference);
    }
  }, [resolvedTheme, setStoreTheme, storeTheme]);

  useEffect(() => {
    if (storeTheme && storeTheme !== resolvedTheme) {
      setTheme(storeTheme);
    }
  }, [resolvedTheme, setTheme, storeTheme]);

  return null;
}

/** Apply theme to both Zustand and next-themes. */
export function applyThemePreference(theme: ThemePreference): void {
  useThemeStore.getState().setTheme(theme);
}
