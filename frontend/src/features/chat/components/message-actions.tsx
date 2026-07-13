"use client";

import {
  Copy,
  Pencil,
  RefreshCw,
  RotateCcw,
  Trash2,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useIsMobile } from "@/hooks";
import { cn } from "@/utils";
import type { Message } from "@/types/chat";

interface MessageActionsProps {
  message: Message;
  onCopy: () => void;
  onRegenerate?: () => void;
  onEdit?: () => void;
  onDelete: () => void;
  onRetry?: () => void;
  isBusy?: boolean;
  className?: string;
}

function ActionButton({
  label,
  icon: Icon,
  onClick,
  disabled,
  variant = "ghost",
  mobile,
}: {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  onClick: () => void;
  disabled?: boolean;
  variant?: "ghost" | "destructive";
  mobile?: boolean;
}) {
  const button = (
    <Button
      type="button"
      variant="ghost"
      size={mobile ? "iconTouch" : "icon"}
      className={cn(
        "touch-manipulation text-muted-foreground hover:text-foreground",
        !mobile && "h-7 w-7",
        variant === "destructive" && "hover:text-destructive",
      )}
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
    >
      <Icon className={mobile ? "h-4 w-4" : "h-3.5 w-3.5"} />
    </Button>
  );

  if (mobile) return button;

  return (
    <Tooltip>
      <TooltipTrigger asChild>{button}</TooltipTrigger>
      <TooltipContent side="bottom">{label}</TooltipContent>
    </Tooltip>
  );
}

/** Action bar for chat messages — always visible on mobile, hover on desktop. */
export function MessageActions({
  message,
  onCopy,
  onRegenerate,
  onEdit,
  onDelete,
  onRetry,
  isBusy,
  className,
}: MessageActionsProps) {
  const isMobile = useIsMobile();
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const hasError = Boolean(message.error);
  const isStreaming = message.isStreaming;

  if (isStreaming) return null;

  return (
    <TooltipProvider delayDuration={300}>
      <div
        className={cn(
          "flex items-center gap-0.5 transition-opacity",
          isMobile
            ? "opacity-100"
            : "opacity-0 group-hover/message:opacity-100 focus-within:opacity-100",
          className,
        )}
      >
        <ActionButton
          label="Copy"
          icon={Copy}
          onClick={onCopy}
          disabled={isBusy}
          mobile={isMobile}
        />

        {isAssistant && onRegenerate && (
          <ActionButton
            label="Regenerate"
            icon={RefreshCw}
            onClick={onRegenerate}
            disabled={isBusy}
            mobile={isMobile}
          />
        )}

        {isUser && onEdit && (
          <ActionButton
            label="Edit"
            icon={Pencil}
            onClick={onEdit}
            disabled={isBusy}
            mobile={isMobile}
          />
        )}

        {hasError && onRetry && (
          <ActionButton
            label="Retry"
            icon={RotateCcw}
            onClick={onRetry}
            disabled={isBusy}
            mobile={isMobile}
          />
        )}

        <ActionButton
          label="Delete"
          icon={Trash2}
          onClick={onDelete}
          disabled={isBusy}
          variant="destructive"
          mobile={isMobile}
        />
      </div>
    </TooltipProvider>
  );
}
