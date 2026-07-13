"use client";

import { useEffect, useRef } from "react";

interface SwipeEdgeOptions {
  /** Called when the user swipes right (e.g. open sidebar). */
  onSwipeRight?: () => void;
  /** Called when the user swipes left (e.g. close sidebar). */
  onSwipeLeft?: () => void;
  /** Distance from screen edge that starts an edge swipe. */
  edgeWidth?: number;
  /** Minimum horizontal distance to count as a swipe. */
  threshold?: number;
  enabled?: boolean;
}

/**
 * Detect horizontal edge swipes for mobile navigation gestures.
 * Swipe right from the left edge opens drawers; swipe left closes them.
 */
export function useSwipeEdge({
  onSwipeRight,
  onSwipeLeft,
  edgeWidth = 28,
  threshold = 60,
  enabled = true,
}: SwipeEdgeOptions) {
  const touchRef = useRef<{ x: number; y: number; fromEdge: boolean } | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const onTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0];
      if (!touch) return;
      touchRef.current = {
        x: touch.clientX,
        y: touch.clientY,
        fromEdge: touch.clientX <= edgeWidth,
      };
    };

    const onTouchEnd = (e: TouchEvent) => {
      const start = touchRef.current;
      touchRef.current = null;
      if (!start) return;

      const touch = e.changedTouches[0];
      if (!touch) return;

      const dx = touch.clientX - start.x;
      const dy = touch.clientY - start.y;

      if (Math.abs(dx) < threshold || Math.abs(dx) < Math.abs(dy) * 1.5) return;

      if (dx > 0 && start.fromEdge) {
        onSwipeRight?.();
      } else if (dx < 0) {
        onSwipeLeft?.();
      }
    };

    document.addEventListener("touchstart", onTouchStart, { passive: true });
    document.addEventListener("touchend", onTouchEnd, { passive: true });

    return () => {
      document.removeEventListener("touchstart", onTouchStart);
      document.removeEventListener("touchend", onTouchEnd);
    };
  }, [edgeWidth, enabled, onSwipeLeft, onSwipeRight, threshold]);
}
