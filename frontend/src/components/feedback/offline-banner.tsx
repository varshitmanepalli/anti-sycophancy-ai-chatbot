"use client";

import { motion, useReducedMotion } from "framer-motion";
import { WifiOff } from "lucide-react";

import { useOnlineStatus } from "@/hooks/use-online-status";
import { cn } from "@/utils";

interface OfflineBannerProps {
  /** When true, always show the banner (for demos/testing). */
  forceShow?: boolean;
  className?: string;
}

/** Sticky banner shown when the browser is offline. */
export function OfflineBanner({ forceShow = false, className }: OfflineBannerProps) {
  const isOnline = useOnlineStatus();
  const reduceMotion = useReducedMotion();
  const visible = forceShow || !isOnline;

  if (!visible) return null;

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className={cn(
        "flex items-center justify-center gap-2 border-b border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-900 dark:text-amber-100",
        className,
      )}
      role="status"
      aria-live="polite"
    >
      <WifiOff className="h-3.5 w-3.5 shrink-0" />
      <span>You are offline. Some features may be unavailable until you reconnect.</span>
    </motion.div>
  );
}
