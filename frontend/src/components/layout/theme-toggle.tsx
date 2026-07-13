"use client";

import { motion } from "framer-motion";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useMounted } from "@/hooks";
import { applyThemePreference } from "@/providers/theme-sync";
import { useThemeStore } from "@/stores";

/** Dark / light theme toggle. */
export function ThemeToggle() {
  const { setTheme } = useTheme();
  const themePreference = useThemeStore((s) => s.theme);
  const toggleTheme = useThemeStore((s) => s.toggleTheme);
  const mounted = useMounted();

  if (!mounted) {
    return (
      <Button variant="ghost" size="iconTouch" className="touch-manipulation sm:h-9 sm:w-9" aria-label="Toggle theme">
        <Sun className="h-4 w-4" />
      </Button>
    );
  }

  const isDark = themePreference === "dark" || (themePreference === "system" && typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="iconTouch"
            className="touch-manipulation sm:h-9 sm:w-9"
            aria-label="Toggle theme"
            onClick={() => {
              toggleTheme();
              const next = useThemeStore.getState().theme;
              applyThemePreference(next);
              setTheme(next);
            }}
          >
            <motion.div
              key={themePreference}
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </motion.div>
          </Button>
        </TooltipTrigger>
        <TooltipContent>Toggle theme</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
