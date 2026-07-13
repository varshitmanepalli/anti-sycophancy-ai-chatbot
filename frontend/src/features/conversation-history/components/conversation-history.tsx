"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/utils";

import { useConversationHistory } from "../hooks/use-conversation-history";
import { ConversationList } from "./conversation-list";
import { ConversationToolbar } from "./conversation-toolbar";

interface ConversationHistoryProps {
  onNavigate?: () => void;
  className?: string;
}

/** Full conversation history with search, filter, grouping, and infinite scroll. */
export function ConversationHistory({ onNavigate, className }: ConversationHistoryProps) {
  const history = useConversationHistory();

  return (
    <div className={cn("flex min-h-0 flex-1 flex-col", className)}>
      <ConversationToolbar
        query={history.query}
        filter={history.filter}
        onQueryChange={history.setQuery}
        onFilterChange={history.setFilter}
        onNavigate={onNavigate}
      />

      <ScrollArea className="flex-1 px-2">
        <ConversationList
          groups={history.groups}
          hasMore={history.hasMore}
          totalCount={history.totalCount}
          visibleCount={history.visibleCount}
          query={history.query}
          onLoadMore={history.loadMore}
          onNavigate={onNavigate}
        />
      </ScrollArea>
    </div>
  );
}
