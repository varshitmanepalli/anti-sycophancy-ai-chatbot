"use client";

import { useEffect, useState } from "react";

/** Bottom inset when the mobile virtual keyboard is open (visual viewport API). */
export function useVisualViewportBottomInset(enabled = true): number {
  const [inset, setInset] = useState(0);

  useEffect(() => {
    if (!enabled || typeof window === "undefined") return;

    const viewport = window.visualViewport;
    if (!viewport) return;

    const update = () => {
      const bottom = window.innerHeight - viewport.height - viewport.offsetTop;
      setInset(Math.max(0, Math.round(bottom)));
    };

    viewport.addEventListener("resize", update);
    viewport.addEventListener("scroll", update);
    update();

    return () => {
      viewport.removeEventListener("resize", update);
      viewport.removeEventListener("scroll", update);
    };
  }, [enabled]);

  return inset;
}
