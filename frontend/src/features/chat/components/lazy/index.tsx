"use client";

import dynamic from "next/dynamic";

import { ShimmerSkeleton } from "@/components/feedback";

function MarkdownLoadingFallback() {
  return (
    <div className="space-y-2 py-1" aria-hidden>
      <ShimmerSkeleton className="h-4 w-full" shimmer />
      <ShimmerSkeleton className="h-4 w-5/6" shimmer />
      <ShimmerSkeleton className="h-4 w-2/3" shimmer />
    </div>
  );
}

/** Code-split markdown renderer (react-markdown, katex, highlight.js). */
export const LazyMarkdownRenderer = dynamic(
  () =>
    import("@/features/markdown/components/markdown-renderer").then((mod) => ({
      default: mod.MarkdownRenderer,
    })),
  {
    loading: () => <MarkdownLoadingFallback />,
    ssr: false,
  },
);

/** Code-split reasoning panel (only loaded in reasoning mode). */
export const LazyReasoningPanel = dynamic(
  () =>
    import("../reasoning/reasoning-panel").then((mod) => ({
      default: mod.ReasoningPanel,
    })),
  {
    loading: () => null,
    ssr: false,
  },
);
