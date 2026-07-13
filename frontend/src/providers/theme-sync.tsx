"use client";

import { useEffect } from "react";
import { useTheme } from "next-themes";

import { useThemeStore } from "@/stores/theme-store";
import type { ThemePreference } from "@/stores/types";

/** Mirrors next-themes preference into Zustand (one-way). */
export function ThemeStoreSync() {
  const { theme } = useTheme();
  const setStoreTheme = useThemeStore((s) => s.setTheme);

  useEffect(() => {
    if (!theme) return;
    const preference = theme as ThemePreference;
    if (useThemeStore.getState().theme !== preference) {
      setStoreTheme(preference);
    }
  }, [theme, setStoreTheme]);

  return null;
}

/** Apply theme preference to Zustand (callers should also update next-themes). */
export function applyThemePreference(theme: ThemePreference): void {
  useThemeStore.getState().setTheme(theme);
}
