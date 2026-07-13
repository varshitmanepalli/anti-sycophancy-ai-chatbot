import * as React from "react";

import { ShimmerSkeleton } from "@/components/feedback/shimmer-skeleton";
import { cn } from "@/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  shimmer?: boolean;
}

/** Base skeleton — delegates to ShimmerSkeleton for shimmer support. */
function Skeleton({ className, shimmer = true, ...props }: SkeletonProps) {
  return <ShimmerSkeleton className={cn(className)} shimmer={shimmer} {...props} />;
}

export { Skeleton };
