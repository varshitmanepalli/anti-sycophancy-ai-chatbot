"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowUp, Loader2, Square } from "lucide-react";
import { useCallback, useEffect, useRef } from "react";
import { useForm } from "react-hook-form";

import { MotionButton } from "@/components/motion";
import { ErrorStateView } from "@/components/feedback";
import { Textarea } from "@/components/ui/textarea";
import { useIsMobile, useVisualViewportBottomInset } from "@/hooks";
import { useChatStore } from "@/stores";
import { cn } from "@/utils";

import { useSendMessage } from "../hooks/use-send-message";
import { chatMessageSchema, type ChatMessageFormValues } from "../validators/chat.schema";

interface ChatInputProps {
  conversationId: string;
  disabled?: boolean;
  initialMessage?: string;
  onInitialMessageUsed?: () => void;
}

const STREAM_STATUS_LABELS: Record<string, string> = {
  connecting: "Connecting…",
  streaming: "Generating…",
  reconnecting: "Reconnecting…",
};

/** Message composer with auto-resize, streaming stop, and keyboard shortcuts. */
export function ChatInput({
  conversationId,
  disabled,
  initialMessage,
  onInitialMessageUsed,
}: ChatInputProps) {
  const chatMode = useChatStore((s) => s.chatMode);
  const isMobile = useIsMobile();
  const keyboardInset = useVisualViewportBottomInset(isMobile);
  const { mutation, cancel, isBusy, streamPhase, activeStream } = useSendMessage();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isStreamingThisConversation =
    activeStream?.conversationId === conversationId &&
    (streamPhase === "connecting" ||
      streamPhase === "streaming" ||
      streamPhase === "reconnecting");

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ChatMessageFormValues>({
    resolver: zodResolver(chatMessageSchema),
    defaultValues: { message: "" },
  });

  const message = watch("message");
  const isPending = mutation.isPending || isBusy;
  const canSend = message.trim().length > 0 && !isPending && !disabled;
  const showStop = isPending && isStreamingThisConversation;

  useEffect(() => {
    if (initialMessage) {
      setValue("message", initialMessage);
      onInitialMessageUsed?.();
      textareaRef.current?.focus();
    }
  }, [initialMessage, onInitialMessageUsed, setValue]);

  const autoResize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, []);

  useEffect(() => {
    autoResize();
  }, [message, autoResize]);

  const onSubmit = useCallback(
    (values: ChatMessageFormValues) => {
      mutation.mutate(
        { conversationId, message: values.message.trim(), mode: chatMode },
        {
          onSuccess: () => {
            reset();
            if (textareaRef.current) {
              textareaRef.current.style.height = "auto";
            }
            textareaRef.current?.focus();
          },
        },
      );
    },
    [chatMode, conversationId, mutation, reset],
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (canSend) handleSubmit(onSubmit)();
    }
  };

  return (
    <div
      className="border-t bg-background/80 px-3 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/60 sm:px-4 sm:py-4"
      style={keyboardInset > 0 ? { paddingBottom: keyboardInset + 12 } : undefined}
    >
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="mx-auto flex max-w-3xl flex-col gap-2"
      >
        {streamPhase && isStreamingThisConversation && (
          <p className="flex items-center gap-2 px-2 text-xs text-muted-foreground" role="status">
            <Loader2 className="h-3 w-3 animate-spin" />
            {STREAM_STATUS_LABELS[streamPhase] ?? "Working…"}
          </p>
        )}

        <div
          className={cn(
            "relative flex items-end gap-2 rounded-[26px] border bg-muted/40 p-2 shadow-sm transition-all",
            "focus-within:border-ring focus-within:shadow-md focus-within:ring-2 focus-within:ring-ring/15",
            errors.message && "border-destructive",
            isPending && "opacity-95",
          )}
        >
          <Textarea
            {...register("message")}
            ref={(e) => {
              register("message").ref(e);
              textareaRef.current = e;
            }}
            placeholder={
              isPending
                ? "Reasoning Engine is responding…"
                : "Message Reasoning Engine…"
            }
            className="max-h-[200px] min-h-[44px] resize-none border-0 bg-transparent px-3 py-2.5 text-sm shadow-none focus-visible:ring-0"
            rows={1}
            disabled={isPending || disabled}
            onKeyDown={handleKeyDown}
            onInput={autoResize}
            aria-label="Message input"
            aria-invalid={!!errors.message}
            aria-busy={isPending}
          />

          {showStop ? (
            <MotionButton
              type="button"
              size="iconTouch"
              variant="secondary"
              className="mb-0.5 shrink-0 rounded-full touch-manipulation"
              onClick={cancel}
              aria-label="Stop generating"
            >
              <Square className="h-4 w-4 fill-current" />
            </MotionButton>
          ) : (
            <MotionButton
              type="submit"
              size="iconTouch"
              className="mb-0.5 shrink-0 rounded-full touch-manipulation"
              disabled={!canSend}
              aria-label="Send message"
            >
              {mutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <ArrowUp className="h-4 w-4" />
              )}
            </MotionButton>
          )}
        </div>

        {errors.message && (
          <p className="px-2 text-xs text-destructive" role="alert">
            {errors.message.message}
          </p>
        )}

        {mutation.isError && (
          <ErrorStateView
            inline
            size="sm"
            title="Failed to send"
            message={mutation.error.message}
            onRetry={() => mutation.reset()}
            retryLabel="Dismiss"
          />
        )}

        <p className="hidden text-center text-[10px] text-muted-foreground sm:block">
          Reasoning Engine may challenge your assumptions · Shift+Enter for new line
        </p>
      </form>
    </div>
  );
}
