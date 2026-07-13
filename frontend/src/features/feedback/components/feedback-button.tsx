"use client";

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/utils";

import type { FeedbackType } from "../types";

interface FeedbackButtonProps {
  type: FeedbackType;
  label: string;
  icon: LucideIcon;
  selected?: boolean;
  disabled?: boolean;
  onClick: () => void;
}

/** Single animated feedback pill button. */
export function FeedbackButton({
  label,
  icon: Icon,
  selected,
  disabled,
  onClick,
}: FeedbackButtonProps) {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      disabled={disabled}
      whileTap={{ scale: 0.96 }}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      animate={
        selected
          ? { scale: [1, 1.04, 1], transition: { duration: 0.35 } }
          : { scale: 1 }
      }
      className={cn(
        "inline-flex min-h-10 items-center gap-1.5 rounded-full border px-3 py-2 text-xs font-medium transition-colors touch-manipulation",
        "disabled:cursor-not-allowed disabled:opacity-50",
        selected
          ? "border-primary/30 bg-primary/10 text-foreground shadow-sm"
          : "border-border/60 bg-background/80 text-muted-foreground hover:border-border hover:bg-muted/50 hover:text-foreground",
      )}
      aria-pressed={selected}
    >
      <Icon className="h-3 w-3 shrink-0" strokeWidth={1.75} />
      <span className="whitespace-nowrap">{label}</span>
    </motion.button>
  );
}
