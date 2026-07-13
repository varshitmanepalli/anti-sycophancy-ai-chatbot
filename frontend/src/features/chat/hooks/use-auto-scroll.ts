"use client";

import { useCallback, useEffect, useRef } from "react";

/** Smart auto-scroll — only scrolls when the user is near the bottom. */
export function useAutoScroll<T>(deps: T[]) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const isNearBottomRef = useRef(true);

  const handleScroll = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    const threshold = 120;
    isNearBottomRef.current =
      el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
  }, []);

  const scrollToBottom = useCallback((behavior: ScrollBehavior = "smooth") => {
    bottomRef.current?.scrollIntoView({ behavior, block: "end" });
  }, []);

  useEffect(() => {
    if (isNearBottomRef.current) {
      scrollToBottom(deps.some((d) => d) ? "smooth" : "auto");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { containerRef, bottomRef, handleScroll, scrollToBottom, isNearBottomRef };
}
