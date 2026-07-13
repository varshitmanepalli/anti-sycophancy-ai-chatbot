"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  Brain,
  Check,
  MessageSquare,
  MoreHorizontal,
  Pencil,
  Pin,
  PinOff,
  Trash2,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { ROUTES } from "@/config";
import { useIsMobile } from "@/hooks";
import { useConversationStore } from "@/stores";
import type { Conversation } from "@/types/chat";
import { cn, formatRelativeTime } from "@/utils";

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onNavigate?: () => void;
  index?: number;
}

/** Single conversation row with rename, pin, and delete actions. */
export function ConversationItem({
  conversation,
  isActive,
  onNavigate,
  index = 0,
}: ConversationItemProps) {
  const router = useRouter();
  const pathname = usePathname();
  const renameConversation = useConversationStore((s) => s.renameConversation);
  const deleteConversation = useConversationStore((s) => s.deleteConversation);
  const togglePinConversation = useConversationStore((s) => s.togglePinConversation);
  const isMobile = useIsMobile();

  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(conversation.title);
  const inputRef = useRef<HTMLInputElement>(null);

  const href = ROUTES.conversation(conversation.id);

  useEffect(() => {
    if (isRenaming) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [isRenaming]);

  const handleRenameSubmit = () => {
    const trimmed = renameValue.trim();
    if (trimmed && trimmed !== conversation.title) {
      renameConversation(conversation.id, trimmed);
    } else {
      setRenameValue(conversation.title);
    }
    setIsRenaming(false);
  };

  const handleDelete = () => {
    deleteConversation(conversation.id);
    if (pathname === href) {
      router.push(ROUTES.chat);
    }
  };

  return (
    <AnimatePresence mode="popLayout">
      <motion.div
        layout
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -8, height: 0 }}
        transition={{ duration: 0.2, delay: index * 0.02 }}
        className="group relative"
      >
        {isRenaming ? (
          <div className="flex items-center gap-1 rounded-lg border bg-background px-2 py-1.5">
            <Input
              ref={inputRef}
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleRenameSubmit();
                if (e.key === "Escape") {
                  setRenameValue(conversation.title);
                  setIsRenaming(false);
                }
              }}
              className="h-7 border-0 bg-transparent px-1 text-sm shadow-none focus-visible:ring-0"
              aria-label="Rename conversation"
            />
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 shrink-0"
              onClick={handleRenameSubmit}
              aria-label="Save rename"
            >
              <Check className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 shrink-0"
              onClick={() => {
                setRenameValue(conversation.title);
                setIsRenaming(false);
              }}
              aria-label="Cancel rename"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        ) : (
          <>
            <Link
              href={href}
              onClick={onNavigate}
              className={cn(
                "flex w-full items-start gap-2 rounded-lg px-3 py-3 pr-12 text-sm transition-colors touch-manipulation sm:py-2.5 sm:pr-10",
                isActive
                  ? "bg-sidebar-accent text-foreground"
                  : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground active:bg-sidebar-accent/80",
              )}
            >
              <span className="mt-0.5 shrink-0">
                {conversation.mode === "reasoning" ? (
                  <Brain className="h-3.5 w-3.5 opacity-60" />
                ) : (
                  <MessageSquare className="h-3.5 w-3.5 opacity-60" />
                )}
              </span>
              <span className="min-w-0 flex-1">
                <span className="flex items-center gap-1.5">
                  {conversation.pinned && (
                    <Pin className="h-3 w-3 shrink-0 text-primary" aria-label="Pinned" />
                  )}
                  <span className="truncate font-medium leading-tight">{conversation.title}</span>
                </span>
                <span className="mt-0.5 block text-[10px] opacity-60">
                  {formatRelativeTime(new Date(conversation.updatedAt))}
                  {conversation.messages.length > 0 &&
                    ` · ${conversation.messages.length} msg${conversation.messages.length !== 1 ? "s" : ""}`}
                </span>
              </span>
            </Link>

            <div
              className={cn(
                "absolute right-1 top-1/2 flex -translate-y-1/2 items-center transition-opacity",
                isMobile
                  ? "opacity-100"
                  : "opacity-0 group-hover:opacity-100 group-focus-within:opacity-100",
              )}
            >
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size={isMobile ? "iconTouch" : "icon"}
                    className={cn(!isMobile && "h-7 w-7", "touch-manipulation")}
                    aria-label={`Actions for ${conversation.title}`}
                    onClick={(e) => e.preventDefault()}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem
                    className="min-h-11"
                    onClick={(e) => {
                      e.preventDefault();
                      togglePinConversation(conversation.id);
                    }}
                  >
                    {conversation.pinned ? (
                      <>
                        <PinOff className="h-3.5 w-3.5" />
                        Unpin
                      </>
                    ) : (
                      <>
                        <Pin className="h-3.5 w-3.5" />
                        Pin
                      </>
                    )}
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="min-h-11"
                    onClick={(e) => {
                      e.preventDefault();
                      setIsRenaming(true);
                    }}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                    Rename
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="min-h-11 text-destructive focus:text-destructive"
                    onClick={(e) => {
                      e.preventDefault();
                      handleDelete();
                    }}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
