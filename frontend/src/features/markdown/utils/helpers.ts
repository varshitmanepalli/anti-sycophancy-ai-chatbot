import type { ReactNode } from "react";

/** Recursively extract plain text from React markdown children. */
export function extractText(children: ReactNode): string {
  if (typeof children === "string") return children;
  if (typeof children === "number") return String(children);
  if (Array.isArray(children)) return children.map(extractText).join("");
  if (children && typeof children === "object" && "props" in children) {
    const props = (children as { props?: { children?: ReactNode } }).props;
    return extractText(props?.children ?? "");
  }
  return String(children ?? "");
}

/** Strip trailing newline from fenced code blocks. */
export function normalizeCode(code: string): string {
  return code.replace(/\n$/, "");
}

/** Detect fenced code block language from className. */
export function parseLanguage(className?: string): string | undefined {
  const match = /language-([\w-]+)/.exec(className ?? "");
  return match?.[1]?.toLowerCase();
}

/** True when className indicates a GFM task list item. */
export function isTaskListItem(className?: string): boolean {
  return Boolean(className?.includes("task-list-item"));
}

/** True when className indicates a GFM task list container. */
export function isTaskList(className?: string): boolean {
  return Boolean(className?.includes("contains-task-list"));
}
