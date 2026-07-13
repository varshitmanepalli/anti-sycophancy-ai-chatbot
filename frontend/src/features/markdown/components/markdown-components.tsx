"use client";

import { createContext, useContext, useMemo } from "react";
import type { Components } from "react-markdown";

import { cn } from "@/utils";

import {
  extractText,
  isTaskList,
  isTaskListItem,
  normalizeCode,
  parseLanguage,
} from "../utils/helpers";
import { MarkdownCodeBlock } from "./markdown-code-block";
import { MarkdownMermaid } from "./markdown-mermaid";

interface MarkdownRenderContextValue {
  isStreaming: boolean;
}

const MarkdownRenderContext = createContext<MarkdownRenderContextValue>({
  isStreaming: false,
});

export function MarkdownRenderProvider({
  isStreaming,
  children,
}: {
  isStreaming: boolean;
  children: React.ReactNode;
}) {
  const value = useMemo(() => ({ isStreaming }), [isStreaming]);
  return (
    <MarkdownRenderContext.Provider value={value}>{children}</MarkdownRenderContext.Provider>
  );
}

function useMarkdownContext() {
  return useContext(MarkdownRenderContext);
}

function MarkdownCode({
  className,
  children,
  ...props
}: React.ComponentProps<"code"> & { className?: string }) {
  const { isStreaming } = useMarkdownContext();
  const language = parseLanguage(className);
  const code = normalizeCode(extractText(children));
  const isBlock = Boolean(language) || code.includes("\n");

  if (!isBlock) {
    return (
      <code
        className="rounded bg-muted px-1.5 py-0.5 font-mono text-[0.85em] text-foreground"
        {...props}
      >
        {children}
      </code>
    );
  }

  if (language === "mermaid") {
    if (isStreaming) {
      return (
        <pre className="my-4 overflow-x-auto rounded-lg border bg-muted/30 p-4 text-xs text-muted-foreground">
          <code>{code}</code>
        </pre>
      );
    }
    return <MarkdownMermaid chart={code} />;
  }

  return <MarkdownCodeBlock code={code} language={language} />;
}

/** Stable react-markdown component map. */
export const markdownComponents: Components = {
  pre({ children }) {
    return <>{children}</>;
  },
  code: MarkdownCode,

  a({ href, children, ...props }) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="font-medium text-primary underline underline-offset-2 hover:text-primary/80"
        {...props}
      >
        {children}
      </a>
    );
  },

  table({ children }) {
    return (
      <div className="markdown-table-wrapper my-4 w-full overflow-x-auto rounded-lg border">
        <table className="w-full min-w-[480px] text-sm">{children}</table>
      </div>
    );
  },

  thead({ children }) {
    return <thead className="bg-muted/50">{children}</thead>;
  },

  th({ children }) {
    return (
      <th className="border-b px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {children}
      </th>
    );
  },

  td({ children }) {
    return <td className="border-b px-3 py-2 align-top">{children}</td>;
  },

  tr({ children }) {
    return <tr className="transition-colors hover:bg-muted/20">{children}</tr>;
  },

  blockquote({ children }) {
    return (
      <blockquote className="my-4 border-l-2 border-primary/30 bg-muted/20 py-1 pl-4 pr-2 italic text-muted-foreground">
        {children}
      </blockquote>
    );
  },

  ul({ className, children, ...props }) {
    return (
      <ul
        className={cn(
          "my-3 space-y-1 pl-5",
          isTaskList(className) ? "list-none pl-0" : "list-disc",
          className,
        )}
        {...props}
      >
        {children}
      </ul>
    );
  },

  ol({ children }) {
    return <ol className="my-3 list-decimal space-y-1 pl-5">{children}</ol>;
  },

  li({ className, children, ...props }) {
    if (isTaskListItem(className)) {
      return (
        <li className={cn("task-list-item flex items-start gap-2 py-0.5", className)} {...props}>
          {children}
        </li>
      );
    }
    return (
      <li className={cn("leading-relaxed", className)} {...props}>
        {children}
      </li>
    );
  },

  input({ type, checked, disabled, ...props }) {
    if (type === "checkbox") {
      return (
        <input
          type="checkbox"
          checked={checked}
          disabled={disabled ?? true}
          className="mt-1 h-3.5 w-3.5 shrink-0 rounded border-input accent-primary"
          readOnly
          {...props}
        />
      );
    }
    return <input type={type} {...props} />;
  },

  hr() {
    return <hr className="my-6 border-border" />;
  },

  p({ children }) {
    return <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>;
  },

  h1({ children }) {
    return <h1 className="mb-3 mt-5 text-xl font-semibold tracking-tight first:mt-0">{children}</h1>;
  },

  h2({ children }) {
    return <h2 className="mb-2 mt-5 text-lg font-semibold tracking-tight first:mt-0">{children}</h2>;
  },

  h3({ children }) {
    return <h3 className="mb-2 mt-4 text-base font-semibold first:mt-0">{children}</h3>;
  },

  h4({ children }) {
    return <h4 className="mb-2 mt-3 text-sm font-semibold first:mt-0">{children}</h4>;
  },

  strong({ children }) {
    return <strong className="font-semibold text-foreground">{children}</strong>;
  },

  em({ children }) {
    return <em className="italic">{children}</em>;
  },
};
