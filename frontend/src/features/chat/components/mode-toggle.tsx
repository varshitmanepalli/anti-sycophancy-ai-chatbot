"use client";

import { Brain, MessageSquare } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useChatStore } from "@/stores";
import type { ChatMode } from "@/types";
import { cn } from "@/utils";

const modes: {
  value: ChatMode;
  label: string;
  icon: typeof MessageSquare;
  description: string;
}[] = [
  {
    value: "standard",
    label: "Chat",
    icon: MessageSquare,
    description: "Streaming responses with anti-sycophancy persona",
  },
  {
    value: "reasoning",
    label: "Reasoning",
    icon: Brain,
    description: "Full pipeline with confidence and reasoning steps",
  },
];

interface ModeToggleProps {
  className?: string;
  mobile?: boolean;
}

/** Toggle between standard chat and reasoning pipeline modes. */
export function ModeToggle({ className, mobile }: ModeToggleProps) {
  const chatMode = useChatStore((s) => s.chatMode);
  const setChatMode = useChatStore((s) => s.setChatMode);
  const active = modes.find((m) => m.value === chatMode) ?? modes[0];
  const ActiveIcon = active.icon;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size={mobile ? "iconTouch" : "sm"}
          className={cn("gap-2 touch-manipulation", className)}
          aria-label={`Chat mode: ${active.label}`}
        >
          <ActiveIcon className="h-4 w-4" />
          {!mobile && <span className="hidden sm:inline">{active.label}</span>}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        {modes.map((mode) => (
          <DropdownMenuItem
            key={mode.value}
            onClick={() => setChatMode(mode.value)}
            className={cn(
              "min-h-11 flex-col items-start gap-0.5 py-2.5",
              chatMode === mode.value && "bg-accent",
            )}
          >
            <span className="flex items-center gap-2 font-medium">
              <mode.icon className="h-4 w-4" />
              {mode.label}
            </span>
            <span className="text-xs text-muted-foreground">{mode.description}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
