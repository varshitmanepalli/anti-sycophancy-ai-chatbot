"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { AlertCircle } from "lucide-react";

import { fadeUpVariants, noMotionTransition } from "@/lib/motion";
import { cn } from "@/utils";

import { RetryButton } from "./retry-button";
import type { FeedbackAction, FeedbackSize } from "./types";

interface ErrorStateViewProps {
  title?: string;
  message?: string;
  icon?: LucideIcon;
  onRetry?: () => void;
  retryLabel?: string;
  retryLoading?: boolean;
  action?: FeedbackAction;
  size?: FeedbackSize;
  inline?: boolean;
  className?: string;
}

/** Inline or block error state with optional retry. */
export function ErrorStateView({
  title = "Something went wrong",
  message = "An unexpected error occurred. Please try again.",
  icon: Icon = AlertCircle,
  onRetry,
  retryLabel,
  retryLoading = false,
  action,
  size = "md",
  inline = false,
  className,
}: ErrorStateViewProps) {
  const reduceMotion = useReducedMotion();

  const content = (
    <>
      <div
        className={cn(
          "flex shrink-0 items-center justify-center rounded-full bg-destructive/10 text-destructive",
          inline ? "h-8 w-8" : size === "sm" ? "h-10 w-10" : "h-12 w-12",
        )}
      >
        <Icon className={cn(inline ? "h-4 w-4" : "h-5 w-5")} />
      </div>

      <div className={cn("min-w-0", inline ? "flex-1" : "text-center")}>
        <p className={cn("font-medium text-destructive", size === "sm" ? "text-sm" : "text-base")}>
          {title}
        </p>
        {message && (
          <p className={cn("text-muted-foreground", size === "sm" ? "text-xs" : "text-sm", !inline && "mt-1")}>
            {message}
          </p>
        )}

        {(onRetry || action) && (
          <div className={cn("flex flex-wrap gap-2", inline ? "mt-2" : "mt-4 justify-center")}>
            {onRetry && (
              <RetryButton
                onClick={onRetry}
                label={retryLabel}
                loading={retryLoading}
                size={size === "sm" ? "sm" : "default"}
              />
            )}
          </div>
        )}
      </div>
    </>
  );

  if (inline) {
    return (
      <div
        className={cn(
          "flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-3",
          className,
        )}
        role="alert"
      >
        {content}
      </div>
    );
  }

  return (
    <motion.div
      variants={fadeUpVariants}
      initial="initial"
      animate="animate"
      transition={reduceMotion ? noMotionTransition : undefined}
      className={cn("flex flex-col items-center px-4 py-8 text-center", className)}
      role="alert"
    >
      {content}
    </motion.div>
  );
}
