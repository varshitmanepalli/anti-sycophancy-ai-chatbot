"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { Inbox } from "lucide-react";

import { MotionButton } from "@/components/motion";
import { fadeUpVariants, noMotionTransition } from "@/lib/motion";
import { cn } from "@/utils";

import type { FeedbackAction, FeedbackSize } from "./types";

interface EmptyStateViewProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: FeedbackAction;
  secondaryAction?: FeedbackAction;
  size?: FeedbackSize;
  className?: string;
  children?: React.ReactNode;
}

const iconSizes: Record<FeedbackSize, string> = {
  sm: "h-10 w-10",
  md: "h-14 w-14",
  lg: "h-16 w-16",
};

/** Generic empty state for lists, panels, and pages. */
export function EmptyStateView({
  icon: Icon = Inbox,
  title,
  description,
  action,
  secondaryAction,
  size = "md",
  className,
  children,
}: EmptyStateViewProps) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      variants={fadeUpVariants}
      initial="initial"
      animate="animate"
      transition={reduceMotion ? noMotionTransition : undefined}
      className={cn(
        "flex flex-col items-center justify-center px-4 py-8 text-center",
        className,
      )}
    >
      <div
        className={cn(
          "mb-4 flex items-center justify-center rounded-2xl bg-muted/60 text-muted-foreground",
          iconSizes[size],
        )}
      >
        <Icon className={cn(size === "sm" ? "h-5 w-5" : size === "md" ? "h-7 w-7" : "h-8 w-8")} />
      </div>

      <h3 className={cn("font-semibold tracking-tight", size === "sm" ? "text-sm" : "text-base")}>
        {title}
      </h3>

      {description && (
        <p className="mt-1.5 max-w-sm text-sm text-muted-foreground">{description}</p>
      )}

      {children}

      {(action || secondaryAction) && (
        <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
          {action && (
            <MotionButton
              variant={action.variant ?? "default"}
              size={size === "sm" ? "sm" : "default"}
              className="touch-manipulation"
              onClick={action.onClick}
              disabled={action.loading}
            >
              {action.icon && <action.icon className="mr-2 h-4 w-4" />}
              {action.label}
            </MotionButton>
          )}
          {secondaryAction && (
            <MotionButton
              variant={secondaryAction.variant ?? "outline"}
              size={size === "sm" ? "sm" : "default"}
              className="touch-manipulation"
              onClick={secondaryAction.onClick}
              disabled={secondaryAction.loading}
            >
              {secondaryAction.icon && <secondaryAction.icon className="mr-2 h-4 w-4" />}
              {secondaryAction.label}
            </MotionButton>
          )}
        </div>
      )}
    </motion.div>
  );
}
