"use client";

import { useMemo, useState } from "react";

import type { ConversationFilter } from "@/types/chat";
import { useConversationStore } from "@/stores";

import { filterConversations, PAGE_SIZE } from "../utils/filters";
import { groupConversationsByDate } from "../utils/group-by-date";

/** Search, filter, paginate, and group conversations for the history list. */
export function useConversationHistory() {
  const conversations = useConversationStore((s) => s.getConversationList());
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ConversationFilter>("all");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

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
