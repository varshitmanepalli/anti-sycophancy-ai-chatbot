"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface UseInfiniteScrollOptions {
  hasMore: boolean;
  onLoadMore: () => void;
  rootMargin?: string;
}

/** Intersection observer hook for paginated list loading. */
export function useInfiniteScroll({
  hasMore,
  onLoadMore,
  rootMargin = "120px",
}: UseInfiniteScrollOptions) {
  const sentinelRef = useRef<HTMLDivElement>(null);
  const onLoadMoreRef = useRef(onLoadMore);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    onLoadMoreRef.current = onLoadMore;
  }, [onLoadMore]);

  const loadMore = useCallback(() => {
    if (!hasMore || isLoading) return;
    setIsLoading(true);
    onLoadMoreRef.current();
    // Defer clearing so rapid IntersectionObserver callbacks cannot nest updates.
    queueMicrotask(() => setIsLoading(false));
  }, [hasMore, isLoading]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          loadMore();
        }
      },
      { rootMargin },
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loadMore, rootMargin]);

  return { sentinelRef, isLoading };
}
