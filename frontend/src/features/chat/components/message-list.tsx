"use client";

import { AnimatePresence } from "framer-motion";
import { useMemo } from "react";

import type { Message } from "@/types/chat";

import { useAutoScroll } from "../hooks/use-auto-scroll";
import { useMessageActions } from "../hooks/use-message-actions";
import { useSendMessage } from "../hooks/use-send-message";
import { MessageBubble } from "./message-bubble";
import { StreamStatusBar } from "./stream-status-bar";
import { TypingIndicator } from "./typing-indicator";

interface MessageListProps {
  conversationId: string;
  messages: Message[];
  isGenerating?: boolean;
}

/** Scrollable message list with smart auto-scroll and message actions. */
export function MessageList({ conversationId, messages, isGenerating }: MessageListProps) {
  const { getActions, isBusy } = useMessageActions({ conversationId });
  const { activeStream, cancel, reconnect } = useSendMessage();
  const conversationActiveStream =
    activeStream?.conversationId === conversationId ? activeStream : null;

  const scrollKey = useMemo(
    () =>
      messages
        .map(
          (m) =>
            `${m.id}:${m.content.length}:${m.isStreaming}:${m.streamPhase ?? ""}:${m.error ?? ""}:${m.wasAborted ?? false}`,
        )
        .join("|"),
    [messages],
  );

  const { containerRef, bottomRef, handleScroll } = useAutoScroll([
    scrollKey,
    isGenerating,
    conversationActiveStream?.phase,
  ]);

  const showGlobalTyping =
    isGenerating &&
    messages.length > 0 &&
    messages[messages.length - 1]?.role === "user";

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto overscroll-contain"
      role="log"
      aria-live="polite"
      aria-relevant="additions"
    >
      <div className="mx-auto w-full px-2 pt-2 sm:px-4 sm:pt-3">
        <StreamStatusBar
          activeStream={conversationActiveStream}
          onReconnect={() => void reconnect()}
          onCancel={cancel}
        />
      </div>

      <div className="mx-auto w-full">
        <AnimatePresence mode="popLayout" initial={false}>
          {messages.map((message) => {
            const actions = getActions(message);
            return (
              <MessageBubble
                key={message.id}
                message={message}
                conversationId={conversationId}
                isBusy={isBusy}
                isEditing={actions.isEditing}
                onCopy={actions.onCopy}
                onRegenerate={actions.onRegenerate}
                onEdit={actions.onEdit}
                onDelete={actions.onDelete}
                onRetry={actions.onRetry}
                onEditSave={actions.onEditSave}
                onEditCancel={actions.onEditCancel}
              />
            );
          })}
        </AnimatePresence>

        {showGlobalTyping && <TypingIndicator phase={conversationActiveStream?.phase ?? "connecting"} />}
      </div>
      <div ref={bottomRef} className="h-px shrink-0" aria-hidden />
    </div>
  );
}
