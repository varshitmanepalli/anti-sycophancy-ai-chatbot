"use client";

import { useMemo, useState } from "react";

import type { ConversationFilter } from "@/types/chat";
import { useConversationStore } from "@/stores";

import { filterConversations, PAGE_SIZE } from "../utils/filters";
import { groupConversationsByDate } from "../utils/group-by-date";

function sortConversations(
  conversations: ReturnType<typeof useConversationStore.getState>["conversations"],
) {
  return Object.values(conversations).sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
    if (a.pinned && b.pinned) {
      const aPin = a.pinnedAt ? new Date(a.pinnedAt).getTime() : 0;
      const bPin = b.pinnedAt ? new Date(b.pinnedAt).getTime() : 0;
      if (aPin !== bPin) return bPin - aPin;
    }
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  });
}

/** Search, filter, paginate, and group conversations for the history list. */
export function useConversationHistory() {
  // Select the map (stable reference) — never call getConversationList() in the
  // selector; it returns a new array every time and causes infinite re-renders.
  const conversationsMap = useConversationStore((s) => s.conversations);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ConversationFilter>("all");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const conversations = useMemo(
    () => sortConversations(conversationsMap),
    [conversationsMap],
  );

  const filtered = useMemo(
    () => filterConversations(conversations, query, filter),
    [conversations, query, filter],
  );

  const visible = useMemo(
    () => filtered.slice(0, visibleCount),
    [filtered, visibleCount],
  );

  const groups = useMemo(() => groupConversationsByDate(visible), [visible]);

  const hasMore = visibleCount < filtered.length;
  const totalCount = filtered.length;

  const loadMore = () => {
    setVisibleCount((prev) => Math.min(prev + PAGE_SIZE, filtered.length));
  };

  const resetPagination = () => setVisibleCount(PAGE_SIZE);

  const handleQueryChange = (value: string) => {
    setQuery(value);
    resetPagination();
  };

  const handleFilterChange = (value: ConversationFilter) => {
    setFilter(value);
    resetPagination();
  };

  return {
    query,
    filter,
    groups,
    hasMore,
    totalCount,
    visibleCount,
    setQuery: handleQueryChange,
    setFilter: handleFilterChange,
    loadMore,
    resetPagination,
  };
}
