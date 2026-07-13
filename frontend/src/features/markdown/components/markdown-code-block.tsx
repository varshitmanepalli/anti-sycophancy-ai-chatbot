"use client";

import { useMemo } from "react";

import { cn } from "@/utils";

import { highlightCode } from "../utils/highlight";
import { CopyCodeButton } from "./copy-code-button";

interface MarkdownCodeBlockProps {
  code: string;
  language?: string;
  className?: string;
}

/** Syntax-highlighted fenced code block with copy button. */
export function MarkdownCodeBlock({ code, language, className }: MarkdownCodeBlockProps) {
  const highlighted = useMemo(
    () => highlightCode(code, language),
    [code, language],
  );

  return (
    <div
      className={cn(
        "markdown-code-block group/code relative my-4 overflow-hidden rounded-lg border bg-[#0d1117]",
        className,
      )}
    >
      <div className="flex items-center justify-between border-b border-white/10 bg-[#161b22] px-3 py-1.5">
        <span className="text-[11px] font-medium uppercase tracking-wide text-zinc-400">
          {language ?? "code"}
        </span>
        <CopyCodeButton
          value={code}
          className="text-zinc-400 hover:bg-white/10 hover:text-zinc-200"
        />
      </div>
      <pre className="overflow-x-auto p-3 text-[13px] leading-relaxed sm:p-4">
        <code
          className="hljs block min-w-0 font-mono text-zinc-100"
          dangerouslySetInnerHTML={{ __html: highlighted }}
        />
      </pre>
    </div>
  );
}
