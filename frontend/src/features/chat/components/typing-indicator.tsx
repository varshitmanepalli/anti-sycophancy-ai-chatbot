"use client";

import { motion } from "framer-motion";

import type { StreamPhase } from "@/types";
import { cn } from "@/utils";

interface TypingIndicatorProps {
  phase?: StreamPhase;
  compact?: boolean;
  className?: string;
}

const PHASE_MESSAGES: Partial<Record<StreamPhase, string>> = {
  connecting: "Connecting to Reasoning Engine…",
  streaming: "Reasoning Engine is thinking…",
  reconnecting: "Connection lost — reconnecting…",
};

/** Animated typing indicator with optional stream phase label. */
export function TypingIndicator({ phase = "streaming", compact, className }: TypingIndicatorProps) {
  const message = PHASE_MESSAGES[phase] ?? "Reasoning Engine is thinking…";

  return (
    <div
      className={cn(
        "flex items-center gap-3 px-4 py-4",
        compact && "px-0 py-1",
        className,
      )}
      aria-label={message}
      role="status"
    >
      <div
        className={cn(
          "flex shrink-0 items-center justify-center rounded-full bg-muted",
          compact ? "h-6 w-6" : "h-8 w-8",
        )}
      >
        <div className="flex items-center gap-1">
          {[0, 1, 2].map((i) => (
            <motion.span
              key={i}
              className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60"
              animate={{ y: [0, -4, 0] }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: i * 0.15,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>
      </div>
      {!compact && (
        <span className="text-sm text-muted-foreground">{message}</span>
      )}
    </div>
  );
}
