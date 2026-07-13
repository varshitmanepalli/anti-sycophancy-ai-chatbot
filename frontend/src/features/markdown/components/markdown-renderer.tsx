"use client";

import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import { cn } from "@/utils";

import {
  MarkdownRenderProvider,
  markdownComponents,
} from "./markdown-components";

interface MarkdownRendererProps {
  content: string;
  isStreaming?: boolean;
  className?: string;
}

interface StreamingCursorProps {
  className?: string;
}

function StreamingCursor({ className }: StreamingCursorProps) {
  return (
    <span
      className={cn(
        "ml-0.5 inline-block h-[1.1em] w-[2px] translate-y-[2px] animate-pulse bg-foreground/70",
        className,
      )}
      aria-hidden
    />
  );
}

const remarkPlugins = [remarkGfm, remarkMath];
const rehypePlugins = [rehypeKatex];

/** Production markdown renderer with GFM, math, mermaid, and syntax highlighting. */
export function MarkdownRenderer({ content, isStreaming = false, className }: MarkdownRendererProps) {
  const plugins = useMemo(() => ({ remarkPlugins, rehypePlugins }), []);

  if (!content && isStreaming) {
    return <StreamingCursor />;
  }

  return (
    <MarkdownRenderProvider isStreaming={isStreaming}>
      <div
        className={cn(
          "markdown-body prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed",
          "prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent",
          "break-words [overflow-wrap:anywhere]",
          className,
        )}
      >
        <ReactMarkdown
          remarkPlugins={plugins.remarkPlugins}
          rehypePlugins={plugins.rehypePlugins}
          components={markdownComponents}
        >
          {content}
        </ReactMarkdown>
        {isStreaming && content && <StreamingCursor />}
      </div>
    </MarkdownRenderProvider>
  );
}
