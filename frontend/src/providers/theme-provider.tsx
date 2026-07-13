"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ThemeProviderProps } from "next-themes";

import { STORAGE_KEYS } from "@/config";

import { ThemeStoreSync } from "./theme-sync";

/** Dark/light theme provider using class strategy. */
export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
      storageKey={STORAGE_KEYS.theme}
      {...props}
    >
      <ThemeStoreSync />
      {children}
    </NextThemesProvider>
  );
}
