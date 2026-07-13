"use client";

import { AnimatePresence, motion } from "framer-motion";

import { MotionButton } from "@/components/motion";
import { RetryButton } from "@/components/feedback";
import { fadeUpVariants } from "@/lib/motion";
import type { ActiveStream, StreamPhase } from "@/types";
import { cn } from "@/utils";
import { Loader2, RefreshCw, WifiOff } from "lucide-react";

interface StreamStatusBarProps {
  activeStream: ActiveStream | null;
  onReconnect?: () => void;
  onCancel?: () => void;
  className?: string;
}

const PHASE_LABELS: Record<StreamPhase, string> = {
  connecting: "Connecting…",
  streaming: "Generating response…",
  reconnecting: "Reconnecting…",
  completed: "Complete",
  aborted: "Stopped",
  error: "Connection error",
};

function phaseIcon(phase: StreamPhase) {
  switch (phase) {
    case "connecting":
    case "streaming":
      return <Loader2 className="h-3.5 w-3.5 animate-spin" />;
    case "reconnecting":
      return <RefreshCw className="h-3.5 w-3.5 animate-spin" />;
    case "error":
      return <WifiOff className="h-3.5 w-3.5" />;
    default:
      return null;
  }
}

/** Inline banner showing stream connection state during generation. */
export function StreamStatusBar({
  activeStream,
  onReconnect,
  onCancel,
  className,
}: StreamStatusBarProps) {
  const showBanner =
    activeStream &&
    (activeStream.phase === "connecting" ||
      activeStream.phase === "reconnecting" ||
      activeStream.phase === "error");

  return (
    <AnimatePresence mode="wait">
      {showBanner && activeStream && (
        <motion.div
          key={`${activeStream.phase}-${activeStream.attempt}`}
          variants={fadeUpVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          className={cn(
            "mx-auto flex max-w-3xl items-center justify-between gap-3 rounded-lg border px-3 py-2 text-xs",
            activeStream.phase === "error"
              ? "border-destructive/30 bg-destructive/5 text-destructive"
              : "border-border/60 bg-muted/40 text-muted-foreground",
            className,
          )}
          role="status"
          aria-live="polite"
        >
          <div className="flex items-center gap-2">
            {phaseIcon(activeStream.phase)}
            <span>
              {activeStream.phase === "reconnecting"
                ? `${PHASE_LABELS[activeStream.phase]} (attempt ${activeStream.attempt}/${activeStream.maxAttempts})`
                : PHASE_LABELS[activeStream.phase]}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {activeStream.phase === "error" && onReconnect && (
              <RetryButton
                onClick={onReconnect}
                label="Retry connection"
                size="sm"
              />
            )}
            {(activeStream.phase === "connecting" || activeStream.phase === "reconnecting") &&
              onCancel && (
                <MotionButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={onCancel}
                >
                  Cancel
                </MotionButton>
              )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
