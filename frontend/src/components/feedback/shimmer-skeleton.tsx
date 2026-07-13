import * as React from "react";

import { cn } from "@/utils";

export interface ShimmerSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Use shimmer gradient instead of pulse animation. */
  shimmer?: boolean;
}

/** Skeleton placeholder with optional shimmer animation. */
export function ShimmerSkeleton({
  className,
  shimmer = true,
  ...props
}: ShimmerSkeletonProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-md bg-muted",
        !shimmer && "animate-pulse",
        className,
      )}
      aria-hidden="true"
      {...props}
    >
      {shimmer && (
        <div
          className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-foreground/10 to-transparent"
          aria-hidden="true"
        />
      )}
    </div>
  );
}

/** Multi-line text skeleton. */
export function SkeletonText({
  lines = 3,
  className,
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={cn("space-y-2", className)} aria-hidden="true">
      {Array.from({ length: lines }).map((_, index) => (
        <ShimmerSkeleton
          key={index}
          className={cn("h-3", index === lines - 1 ? "w-4/5" : "w-full")}
        />
      ))}
    </div>
  );
}

/** Circular avatar skeleton. */
export function SkeletonAvatar({ className }: { className?: string }) {
  return <ShimmerSkeleton className={cn("h-10 w-10 rounded-full", className)} />;
}

/** Card-shaped skeleton block. */
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("space-y-3 rounded-xl border border-border/60 p-4", className)} aria-hidden="true">
      <ShimmerSkeleton className="h-4 w-1/3" />
      <SkeletonText lines={2} />
    </div>
  );
}
