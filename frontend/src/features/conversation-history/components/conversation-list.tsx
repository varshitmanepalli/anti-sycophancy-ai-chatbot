"use client";

import { MessageSquarePlus } from "lucide-react";
import { usePathname } from "next/navigation";

import { EmptyStateView, LoadingSpinner } from "@/components/feedback";

import type { DateGroup } from "../utils/group-by-date";
import { useInfiniteScroll } from "../hooks/use-infinite-scroll";
import { ConversationDateGroup } from "./conversation-date-group";

interface ConversationListProps {
  groups: DateGroup[];
  hasMore: boolean;
  totalCount: number;
  visibleCount: number;
  query: string;
  onLoadMore: () => void;
  onNavigate?: () => void;
}

/** Grouped, paginated conversation list with infinite scroll. */
export function ConversationList({
  groups,
  hasMore,
  totalCount,
  visibleCount,
  query,
  onLoadMore,
  onNavigate,
}: ConversationListProps) {
  const pathname = usePathname();

  const { sentinelRef, isLoading } = useInfiniteScroll({
    hasMore,
    onLoadMore,
  });

  const activeId = pathname.startsWith("/c/")
    ? pathname.split("/c/")[1]?.split("/")[0] ?? null
    : null;

  if (totalCount === 0) {
    return (
      <EmptyStateView
        size="sm"
        icon={MessageSquarePlus}
        title={query ? "No matches found" : "No conversations yet"}
        description={
          query
            ? "Try a different search term or clear filters."
            : "Start a new chat to begin your first conversation."
        }
        className="py-6"
      />
    );
  }

  return (
    <div className="space-y-3 pb-3">
      {groups.map((group) => (
        <ConversationDateGroup
          key={group.key}
          group={group}
          activeId={activeId}
          onNavigate={onNavigate}
        />
      ))}

      {hasMore && (
        <div
          ref={sentinelRef}
          className="flex items-center justify-center py-3"
          aria-hidden={!isLoading}
        >
          {isLoading && <LoadingSpinner size="sm" label="Loading more" />}
        </div>
      )}

      {!hasMore && visibleCount > 0 && totalCount > 10 && (
        <p className="px-2 py-1 text-center text-[10px] text-muted-foreground">
          {totalCount} conversation{totalCount !== 1 ? "s" : ""}
        </p>
      )}
    </div>
  );
}
