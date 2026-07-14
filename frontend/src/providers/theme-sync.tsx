"use client";

import { useEffect, useRef } from "react";
import { useTheme } from "next-themes";

import { useThemeStore } from "@/stores/theme-store";
import type { ThemePreference } from "@/stores/types";

/** Mirrors next-themes preference into Zustand (one-way, once per theme value). */
export function ThemeStoreSync() {
  const { theme } = useTheme();
  const lastSynced = useRef<string | null>(null);

  useEffect(() => {
    if (!theme) return;
    if (lastSynced.current === theme) return;

    const preference = theme as ThemePreference;
    lastSynced.current = theme;

    if (useThemeStore.getState().theme !== preference) {
      useThemeStore.getState().setTheme(preference);
    }
  }, [theme]);

  return null;
}

/** Apply theme preference to Zustand (callers should also update next-themes). */
export function applyThemePreference(theme: ThemePreference): void {
  useThemeStore.getState().setTheme(theme);
}
