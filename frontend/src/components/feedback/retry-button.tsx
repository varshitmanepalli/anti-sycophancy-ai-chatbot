"use client";

import { RefreshCw } from "lucide-react";

import { MotionButton } from "@/components/motion";
import { cn } from "@/utils";

interface RetryButtonProps {
  onClick: () => void;
  label?: string;
  loading?: boolean;
  disabled?: boolean;
  size?: "sm" | "default";
  className?: string;
}

/** Reusable retry action button. */
export function RetryButton({
  onClick,
  label = "Try again",
  loading = false,
  disabled = false,
  size = "default",
  className,
}: RetryButtonProps) {
  return (
    <MotionButton
      type="button"
      variant="outline"
      size={size === "sm" ? "sm" : "default"}
      className={cn(
        "gap-2 touch-manipulation",
        size === "sm" && "h-7 text-xs",
        className,
      )}
      onClick={onClick}
      disabled={disabled || loading}
    >
      <RefreshCw className={cn("h-4 w-4", loading && "animate-spin", size === "sm" && "h-3 w-3")} />
      {label}
    </MotionButton>
  );
}
