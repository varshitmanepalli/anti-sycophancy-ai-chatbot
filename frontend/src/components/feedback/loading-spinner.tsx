import { Loader2 } from "lucide-react";

import { cn } from "@/utils";

import type { FeedbackSize } from "./types";

const sizeClasses: Record<FeedbackSize, string> = {
  sm: "h-3.5 w-3.5",
  md: "h-5 w-5",
  lg: "h-8 w-8",
};

interface LoadingSpinnerProps {
  size?: FeedbackSize;
  label?: string;
  className?: string;
  centered?: boolean;
}

/** Accessible loading spinner. */
export function LoadingSpinner({
  size = "md",
  label = "Loading",
  className,
  centered = false,
}: LoadingSpinnerProps) {
  const spinner = (
    <Loader2
      className={cn("animate-spin text-muted-foreground", sizeClasses[size], className)}
      aria-hidden="true"
    />
  );

  if (centered) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 py-8" role="status">
        {spinner}
        <span className="sr-only">{label}</span>
        {label !== "Loading" && (
          <p className="text-xs text-muted-foreground">{label}</p>
        )}
      </div>
    );
  }

  return (
    <span className="inline-flex items-center gap-2" role="status">
      {spinner}
      <span className="sr-only">{label}</span>
    </span>
  );
}
