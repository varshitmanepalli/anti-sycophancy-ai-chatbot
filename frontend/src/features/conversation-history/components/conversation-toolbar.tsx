"use client";

import { MessageSquarePlus, Search } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ROUTES } from "@/config";
import { useChatStore, useConversationStore } from "@/stores";
import type { ConversationFilter } from "@/types/chat";

import { FILTER_OPTIONS } from "../utils/filters";
import { cn } from "@/utils";

interface ConversationToolbarProps {
  query: string;
  filter: ConversationFilter;
  onQueryChange: (value: string) => void;
  onFilterChange: (value: ConversationFilter) => void;
  onNavigate?: () => void;
}

/** Search, filter tabs, and new chat button. */
export function ConversationToolbar({
  query,
  filter,
  onQueryChange,
  onFilterChange,
  onNavigate,
}: ConversationToolbarProps) {
  const router = useRouter();
  const createConversation = useConversationStore((s) => s.createConversation);
  const chatMode = useChatStore((s) => s.chatMode);

  const handleNewChat = () => {
    const id = createConversation(chatMode);
    router.push(ROUTES.conversation(id));
    onNavigate?.();
  };

  return (
    <div className="space-y-2 px-3 pb-3">
      <Button
        onClick={handleNewChat}
        className="h-11 w-full justify-start gap-2 touch-manipulation"
        variant="secondary"
      >
        <MessageSquarePlus className="h-4 w-4" />
        New chat
      </Button>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Search conversations…"
          className="h-11 bg-background/50 pl-10 text-sm"
          aria-label="Search conversations"
        />
      </div>

      <div className="flex gap-1.5 overflow-x-auto pb-0.5 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {FILTER_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onFilterChange(option.value)}
            className={cn(
              "shrink-0 rounded-full px-3 py-2 text-xs font-medium transition-colors touch-manipulation",
              filter === option.value
                ? "bg-primary text-primary-foreground"
                : "bg-muted/60 text-muted-foreground hover:bg-muted hover:text-foreground active:bg-muted/80",
            )}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
