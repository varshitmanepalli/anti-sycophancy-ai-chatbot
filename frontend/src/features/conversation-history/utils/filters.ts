import type { Conversation, ConversationFilter } from "@/types/chat";

/** Filter conversations by search query and active filter tab. */
export function filterConversations(
  conversations: Conversation[],
  query: string,
  filter: ConversationFilter,
): Conversation[] {
  const q = query.trim().toLowerCase();

  return conversations.filter((conversation) => {
    if (filter === "pinned" && !conversation.pinned) return false;
    if (filter === "standard" && conversation.mode !== "standard") return false;
    if (filter === "reasoning" && conversation.mode !== "reasoning") return false;

    if (!q) return true;

    const inTitle = conversation.title.toLowerCase().includes(q);
    const inMessages = conversation.messages.some((m) =>
      m.content.toLowerCase().includes(q),
    );

    return inTitle || inMessages;
  });
}

export const FILTER_OPTIONS: { value: ConversationFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "pinned", label: "Pinned" },
  { value: "standard", label: "Chat" },
  { value: "reasoning", label: "Reasoning" },
];

export const PAGE_SIZE = 20;
