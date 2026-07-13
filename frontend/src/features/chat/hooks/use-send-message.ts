"use client";

import { useMutation } from "@tanstack/react-query";
import { useCallback, useEffect, useRef } from "react";

import { sendPipelineMessage } from "@/services";
import { StreamChatError, streamChatWithRetry } from "@/services/api/stream-chat.service";
import {
  useConversationStore,
  useReasoningPanelStore,
  useStreamingStore,
} from "@/stores";
import type { ChatMode, StreamPhase } from "@/types";

const MAX_STREAM_RETRIES = 3;

interface SendMessageOptions {
  conversationId: string;
  message: string;
  mode: ChatMode;
  skipUserMessage?: boolean;
}

interface AssistantReplyOptions {
  conversationId: string;
  userContent: string;
  mode: ChatMode;
  existingAssistantId?: string;
}

/** Shared abort controller so cancel works across hook instances. */
let sharedAbortController: AbortController | null = null;

function clearSharedAbort() {
  sharedAbortController = null;
}

function isAbortError(error: unknown): boolean {
  if (error instanceof StreamChatError && error.code === "aborted") return true;
  if (error instanceof DOMException && error.name === "AbortError") return true;
  if (error instanceof Error && error.name === "AbortError") return true;
  return false;
}

function formatStreamError(error: unknown): string {
  if (error instanceof StreamChatError) {
    switch (error.code) {
      case "offline":
        return "You are offline. Reconnect when your network is back and try again.";
      case "server":
        return error.message || "The server encountered an error. Please try again.";
      case "network":
        return "Connection lost. Tap retry to continue.";
      case "timeout":
        return "The request timed out. Please try again.";
      default:
        return error.message;
    }
  }
  return error instanceof Error ? error.message : "Failed to generate response";
}

/** Hook encapsulating chat send, stream, regenerate, retry, abort, and reconnect logic. */
export function useSendMessage() {
  const addMessage = useConversationStore((s) => s.addMessage);
  const updateMessage = useConversationStore((s) => s.updateMessage);
  const setMessageStreaming = useStreamingStore((s) => s.setMessageStreaming);
  const setMessageStreamPhase = useStreamingStore((s) => s.setMessageStreamPhase);
  const setMessageAborted = useStreamingStore((s) => s.setMessageAborted);
  const setMessageError = useStreamingStore((s) => s.setMessageError);
  const setStructuredReasoning = useConversationStore((s) => s.setStructuredReasoning);
  const setLastConfidence = useReasoningPanelStore((s) => s.setLastConfidence);
  const setActiveStream = useStreamingStore((s) => s.setActiveStream);
  const truncateMessagesAfter = useConversationStore((s) => s.truncateMessagesAfter);
  const activeStream = useStreamingStore((s) => s.activeStream);

  const pendingReconnectRef = useRef<AssistantReplyOptions | null>(null);

  const cancel = useCallback(() => {
    sharedAbortController?.abort();
    clearSharedAbort();

    const stream = useStreamingStore.getState().activeStream;
    if (stream) {
      setMessageAborted(stream.conversationId, stream.messageId);
    }
    setActiveStream(null);
    pendingReconnectRef.current = null;
  }, [setActiveStream, setMessageAborted]);

  const streamAssistantReply = useCallback(
    async ({ conversationId, userContent, mode, existingAssistantId }: AssistantReplyOptions) => {
      pendingReconnectRef.current = { conversationId, userContent, mode, existingAssistantId };

      if (mode === "reasoning") {
        setActiveStream({
          conversationId,
          messageId: existingAssistantId ?? "",
          phase: "connecting",
          attempt: 0,
          maxAttempts: 1,
        });

        try {
          const response = await sendPipelineMessage({
            conversation_id: conversationId,
            message: userContent,
          });

          if (existingAssistantId) {
            updateMessage(conversationId, existingAssistantId, response.response);
            setMessageStreamPhase(conversationId, existingAssistantId, "completed");
            setMessageStreaming(conversationId, existingAssistantId, false);
          } else {
            const id = addMessage(conversationId, {
              role: "assistant",
              content: response.response,
              streamPhase: "completed",
            });
            setActiveStream({
              conversationId,
              messageId: id,
              phase: "completed",
              attempt: 0,
              maxAttempts: 1,
            });
          }

          setStructuredReasoning(conversationId, response.structured_reasoning ?? null);
          setLastConfidence(
            response.structured_reasoning?.confidence_score ?? response.confidence,
          );
          setActiveStream(null);
          pendingReconnectRef.current = null;
          return response.response;
        } catch (error) {
          const messageId = existingAssistantId;
          if (messageId) {
            setMessageError(conversationId, messageId, formatStreamError(error));
          }
          setActiveStream(null);
          throw error;
        }
      }

      let assistantMessageId = existingAssistantId;
      if (!assistantMessageId) {
        assistantMessageId = addMessage(conversationId, {
          role: "assistant",
          content: "",
          isStreaming: true,
          streamPhase: "connecting",
        });
      } else {
        updateMessage(conversationId, assistantMessageId, "");
        setMessageStreaming(conversationId, assistantMessageId, true);
        setMessageStreamPhase(conversationId, assistantMessageId, "connecting");
        setMessageError(conversationId, assistantMessageId, null);
      }

      setActiveStream({
        conversationId,
        messageId: assistantMessageId,
        phase: "connecting",
        attempt: 0,
        maxAttempts: MAX_STREAM_RETRIES,
      });

      sharedAbortController = new AbortController();
      let accumulated = "";

      const handlePhaseChange = (phase: StreamPhase, attempt = 0) => {
        setMessageStreamPhase(conversationId, assistantMessageId!, phase);
        setActiveStream({
          conversationId,
          messageId: assistantMessageId!,
          phase,
          attempt,
          maxAttempts: MAX_STREAM_RETRIES,
        });

        if (phase === "reconnecting") {
          accumulated = "";
          updateMessage(conversationId, assistantMessageId!, "");
        }
      };

      try {
        accumulated = await streamChatWithRetry({
          payload: { message: userContent, conversation_id: conversationId },
          onToken: (token) => {
            accumulated += token;
            updateMessage(conversationId, assistantMessageId!, accumulated);
          },
          onComplete: () => {
            setMessageStreaming(conversationId, assistantMessageId!, false);
            setMessageStreamPhase(conversationId, assistantMessageId!, "completed");
          },
          onPhaseChange: handlePhaseChange,
          signal: sharedAbortController.signal,
          maxRetries: MAX_STREAM_RETRIES,
          fallbackToNonStreaming: true,
        });
      } catch (error) {
        if (isAbortError(error)) {
          setMessageAborted(conversationId, assistantMessageId!);
          pendingReconnectRef.current = null;
          return accumulated;
        }

        setMessageError(conversationId, assistantMessageId!, formatStreamError(error));
        throw error;
      } finally {
        clearSharedAbort();
      }

      setActiveStream(null);
      pendingReconnectRef.current = null;

      setStructuredReasoning(conversationId, null);
      setLastConfidence(null);
      return accumulated;
    },
    [
      addMessage,
      setActiveStream,
      setLastConfidence,
      setMessageAborted,
      setMessageError,
      setMessageStreamPhase,
      setMessageStreaming,
      setStructuredReasoning,
      updateMessage,
    ],
  );

  const reconnect = useCallback(async () => {
    const pending = pendingReconnectRef.current;
    if (!pending) return;

    const messageId = pending.existingAssistantId;
    if (messageId) {
      setMessageError(pending.conversationId, messageId, null);
      setMessageStreaming(pending.conversationId, messageId, true);
      setMessageStreamPhase(pending.conversationId, messageId, "connecting");
    }

    return streamAssistantReply(pending);
  }, [setMessageError, setMessageStreamPhase, setMessageStreaming, streamAssistantReply]);

  useEffect(() => {
    const handleOnline = () => {
      const stream = useStreamingStore.getState().activeStream;
      if (stream?.phase === "error" && pendingReconnectRef.current) {
        void reconnect();
      }
    };

    window.addEventListener("online", handleOnline);
    return () => window.removeEventListener("online", handleOnline);
  }, [reconnect]);

  const mutation = useMutation({
    mutationFn: async ({ conversationId, message, mode, skipUserMessage }: SendMessageOptions) => {
      if (!skipUserMessage) {
        addMessage(conversationId, { role: "user", content: message });
      }
      return streamAssistantReply({ conversationId, userContent: message, mode });
    },
  });

  const regenerate = useMutation({
    mutationFn: async ({
      conversationId,
      assistantMessageId,
      mode,
    }: {
      conversationId: string;
      assistantMessageId: string;
      mode: ChatMode;
    }) => {
      const conversation = useConversationStore.getState().conversations[conversationId];
      if (!conversation) throw new Error("Conversation not found");

      const assistantIndex = conversation.messages.findIndex((m) => m.id === assistantMessageId);
      if (assistantIndex <= 0) throw new Error("Cannot regenerate this message");

      const userMessage = [...conversation.messages]
        .slice(0, assistantIndex)
        .reverse()
        .find((m) => m.role === "user");
      if (!userMessage) throw new Error("No user message to regenerate from");

      truncateMessagesAfter(conversationId, assistantMessageId, true);

      return streamAssistantReply({
        conversationId,
        userContent: userMessage.content,
        mode,
      });
    },
  });

  const retry = useMutation({
    mutationFn: async ({
      conversationId,
      messageId,
      mode,
    }: {
      conversationId: string;
      messageId: string;
      mode: ChatMode;
    }) => {
      const conversation = useConversationStore.getState().conversations[conversationId];
      if (!conversation) throw new Error("Conversation not found");

      const message = conversation.messages.find((m) => m.id === messageId);
      if (!message) throw new Error("Message not found");

      if (message.role === "assistant") {
        const index = conversation.messages.findIndex((m) => m.id === messageId);
        const userMessage = [...conversation.messages]
          .slice(0, index)
          .reverse()
          .find((m) => m.role === "user");
        if (!userMessage) throw new Error("No user message to retry");

        return streamAssistantReply({
          conversationId,
          userContent: userMessage.content,
          mode,
          existingAssistantId: messageId,
        });
      }

      truncateMessagesAfter(conversationId, messageId, false);
      return streamAssistantReply({
        conversationId,
        userContent: message.content,
        mode,
      });
    },
  });

  const editAndResend = useMutation({
    mutationFn: async ({
      conversationId,
      messageId,
      content,
      mode,
    }: {
      conversationId: string;
      messageId: string;
      content: string;
      mode: ChatMode;
    }) => {
      useConversationStore.getState().editMessage(conversationId, messageId, content);
      truncateMessagesAfter(conversationId, messageId, false);
      return streamAssistantReply({ conversationId, userContent: content, mode });
    },
  });

  const isBusy =
    mutation.isPending ||
    regenerate.isPending ||
    retry.isPending ||
    editAndResend.isPending ||
    activeStream !== null;

  const streamPhase = activeStream?.phase ?? null;

  return {
    mutation,
    regenerate,
    retry,
    editAndResend,
    cancel,
    reconnect,
    isBusy,
    streamPhase,
    activeStream,
  };
}
