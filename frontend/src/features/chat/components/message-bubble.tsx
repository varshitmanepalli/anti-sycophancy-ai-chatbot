"use client";

import { motion, useReducedMotion } from "framer-motion";

import {
  assistantMessageVariants,
  noMotionTransition,
  userMessageVariants,
} from "@/lib/motion";
import { cn } from "@/utils";
import type { Message } from "@/types/chat";

import { LazyMarkdownRenderer } from "./lazy";
import { MessageActions } from "./message-actions";
import { MessageEditForm } from "./message-edit-form";
import { TypingIndicator } from "./typing-indicator";
import { MotionButton } from "@/components/motion";
import { RetryButton } from "@/components/feedback";
import { FeedbackBar } from "@/features/feedback";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { AlertCircle, Bot, RefreshCw, Square, User } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
  conversationId: string;
  isBusy?: boolean;
  isEditing?: boolean;
  onCopy: () => void;
  onRegenerate?: () => void;
  onEdit?: () => void;
  onDelete: () => void;
  onRetry?: () => void;
  onEditSave?: (content: string) => void;
  onEditCancel?: () => void;
}

/** Single chat message — ChatGPT-style layout with markdown and actions. */
export function MessageBubble({
  message,
  conversationId,
  isBusy,
  isEditing,
  onCopy,
  onRegenerate,
  onEdit,
  onDelete,
  onRetry,
  onEditSave,
  onEditCancel,
}: MessageBubbleProps) {
  const reduceMotion = useReducedMotion();
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const isConnecting = message.streamPhase === "connecting" || message.streamPhase === "reconnecting";
  const showTyping =
    isAssistant &&
    (message.isStreaming || isConnecting) &&
    !message.content &&
    !message.error;
  const showReconnecting =
    isAssistant && message.streamPhase === "reconnecting" && message.content.length > 0;

  return (
    <motion.article
      layout={!reduceMotion}
      variants={isUser ? userMessageVariants : assistantMessageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={reduceMotion ? noMotionTransition : undefined}
      className={cn(
        "group/message w-full border-b border-border/40 px-3 py-4 sm:px-4 sm:py-6",
        isAssistant && "bg-muted/20",
      )}
      aria-label={`${isUser ? "You" : "Assistant"} said`}
    >
      <div className="mx-auto flex w-full max-w-3xl gap-3 sm:gap-4">
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback
            className={cn(
              "text-xs",
              isUser
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground",
            )}
          >
            {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
          </AvatarFallback>
        </Avatar>

        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center justify-between gap-2">
            <p className="text-sm font-medium">{isUser ? "You" : "Reasoning Engine"}</p>
            <MessageActions
              message={message}
              onCopy={onCopy}
              onRegenerate={onRegenerate}
              onEdit={onEdit}
              onDelete={onDelete}
              onRetry={onRetry}
              isBusy={isBusy}
            />
          </div>

          {isEditing && onEditSave && onEditCancel ? (
            <MessageEditForm
              initialValue={message.content}
              onSave={onEditSave}
              onCancel={onEditCancel}
            />
          ) : isUser ? (
            <div className="rounded-2xl bg-muted/60 px-4 py-3 text-sm leading-relaxed">
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
            </div>
          ) : showTyping ? (
            <TypingIndicator phase={message.streamPhase ?? "streaming"} compact />
          ) : (
            <>
              {showReconnecting && (
                <p className="mb-2 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <RefreshCw className="h-3 w-3 animate-spin" />
                  Reconnecting…
                </p>
              )}
              <LazyMarkdownRenderer content={message.content} isStreaming={message.isStreaming} />
            </>
          )}

          {isAssistant && !showTyping && !message.isStreaming && message.content && !message.error && (
            <FeedbackBar
              messageId={message.id}
              conversationId={conversationId}
              compact
            />
          )}

          {message.wasAborted && (
            <div className="mt-3 flex items-center gap-2 rounded-lg border border-border/60 bg-muted/30 px-3 py-2 text-sm text-muted-foreground">
              <Square className="h-3.5 w-3.5 shrink-0 fill-current" />
              <span>Generation stopped</span>
              {onRegenerate && (
                <MotionButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="ml-auto h-7 text-xs"
                  onClick={onRegenerate}
                  disabled={isBusy}
                >
                  Continue
                </MotionButton>
              )}
            </div>
          )}

          {message.error && (
            <div className="mt-3 flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div className="flex min-w-0 flex-1 flex-col gap-2">
                <span>{message.error}</span>
                {onRetry && (
                  <RetryButton
                    onClick={onRetry}
                    label="Retry"
                    size="sm"
                    disabled={isBusy}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.article>
  );
}
