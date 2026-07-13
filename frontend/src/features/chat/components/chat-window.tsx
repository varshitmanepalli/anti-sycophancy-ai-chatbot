"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useChatStore, useConversationStore } from "@/stores";

import { ChatInput } from "./chat-input";
import { ChatSkeleton } from "./chat-skeleton";
import { EmptyState } from "./empty-state";
import { MessageList } from "./message-list";
import { LazyReasoningPanel } from "./lazy";
import { useSendMessage } from "../hooks/use-send-message";

interface ChatWindowProps {
  conversationId?: string;
}

/** Main chat interface — messages, reasoning panel, and input. */
export function ChatWindow({ conversationId }: ChatWindowProps) {
  const router = useRouter();
  const conversations = useConversationStore((s) => s.conversations);
  const activeConversationId = useConversationStore((s) => s.activeConversationId);
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);
  const createConversation = useConversationStore((s) => s.createConversation);
  const chatMode = useChatStore((s) => s.chatMode);
  const { isBusy } = useSendMessage();
  const [draftMessage, setDraftMessage] = useState<string | undefined>();

  const resolvedId = conversationId ?? activeConversationId;
  const conversation = resolvedId ? conversations[resolvedId] : null;

  useEffect(() => {
    if (conversationId) {
      setActiveConversation(conversationId);
    }
  }, [conversationId, setActiveConversation]);

  useEffect(() => {
    if (!resolvedId && !conversationId) {
      const id = createConversation(chatMode);
      router.replace(`/c/${id}`);
    }
  }, [resolvedId, conversationId, createConversation, chatMode, router]);

  if (!resolvedId || !conversation) {
    return <ChatSkeleton />;
  }

  const hasMessages = conversation.messages.length > 0;
  const isGenerating =
    isBusy ||
    conversation.messages.some((m) => m.isStreaming);

  return (
    <div className="flex h-full flex-col">
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
        {hasMessages ? (
          <MessageList
            conversationId={resolvedId}
            messages={conversation.messages}
            isGenerating={isGenerating}
          />
        ) : (
          <EmptyState
            onSelectSuggestion={(text) => setDraftMessage(text)}
          />
        )}
      </div>

      <LazyReasoningPanel conversationId={resolvedId} />
      <ChatInput
        conversationId={resolvedId}
        initialMessage={draftMessage}
        onInitialMessageUsed={() => setDraftMessage(undefined)}
      />
    </div>
  );
}
