"use client";

import { useCallback, useState } from "react";

import { useChatStore, useConversationStore } from "@/stores";
import type { Message } from "@/types/chat";

import { useSendMessage } from "./use-send-message";

interface UseMessageActionsOptions {
  conversationId: string;
}

/** Handlers for per-message actions: copy, edit, delete, regenerate, retry. */
export function useMessageActions({ conversationId }: UseMessageActionsOptions) {
  const chatMode = useChatStore((s) => s.chatMode);
  const deleteMessage = useConversationStore((s) => s.deleteMessage);
  const { regenerate, retry, editAndResend, isBusy } = useSendMessage();
  const [editingId, setEditingId] = useState<string | null>(null);

  const handleCopy = useCallback(async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch {
      // clipboard unavailable
    }
  }, []);

  const handleDelete = useCallback(
    (messageId: string) => {
      deleteMessage(conversationId, messageId);
    },
    [conversationId, deleteMessage],
  );

  const handleRegenerate = useCallback(
    (assistantMessageId: string) => {
      regenerate.mutate({ conversationId, assistantMessageId, mode: chatMode });
    },
    [chatMode, conversationId, regenerate],
  );

  const handleRetry = useCallback(
    (messageId: string) => {
      retry.mutate({ conversationId, messageId, mode: chatMode });
    },
    [chatMode, conversationId, retry],
  );

  const handleEditStart = useCallback((messageId: string) => {
    setEditingId(messageId);
  }, []);

  const handleEditCancel = useCallback(() => {
    setEditingId(null);
  }, []);

  const handleEditSave = useCallback(
    (messageId: string, content: string) => {
      setEditingId(null);
      editAndResend.mutate({ conversationId, messageId, content, mode: chatMode });
    },
    [chatMode, conversationId, editAndResend],
  );

  const getActions = useCallback(
    (message: Message) => ({
      isEditing: editingId === message.id,
      onCopy: () => handleCopy(message.content),
      onDelete: () => handleDelete(message.id),
      onRegenerate:
        message.role === "assistant" ? () => handleRegenerate(message.id) : undefined,
      onEdit: message.role === "user" ? () => handleEditStart(message.id) : undefined,
      onRetry: message.error || message.wasAborted ? () => handleRetry(message.id) : undefined,
      onEditSave: (content: string) => handleEditSave(message.id, content),
      onEditCancel: handleEditCancel,
    }),
    [
      editingId,
      handleCopy,
      handleDelete,
      handleEditCancel,
      handleEditSave,
      handleEditStart,
      handleRegenerate,
      handleRetry,
    ],
  );

  return { getActions, isBusy, editingId };
}
