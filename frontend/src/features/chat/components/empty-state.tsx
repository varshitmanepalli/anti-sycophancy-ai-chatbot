"use client";

import { motion } from "framer-motion";
import { Brain, MessageSquare, Sparkles } from "lucide-react";

import { MotionButton } from "@/components/motion";
import { useChatStore } from "@/stores";

interface EmptyStateProps {
  onSelectSuggestion: (text: string) => void;
}

/** Welcome screen shown when no messages exist. */
export function EmptyState({ onSelectSuggestion }: EmptyStateProps) {
  const chatMode = useChatStore((s) => s.chatMode);

  const suggestions = [
    "Should I trust this investment plan without independent verification?",
    "What assumptions am I making in this decision?",
    "Help me evaluate this claim critically — don't just agree with me.",
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex flex-1 flex-col items-center justify-center px-4 py-8 sm:py-12"
    >
      <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        {chatMode === "reasoning" ? <Brain className="h-7 w-7" /> : <Sparkles className="h-7 w-7" />}
      </div>

      <h2 className="mb-2 text-center text-xl font-semibold tracking-tight sm:text-2xl">
        How can I help you today?
      </h2>
      <p className="mb-8 max-w-md text-center text-sm text-muted-foreground">
        {chatMode === "reasoning"
          ? "Reasoning mode runs the full analysis pipeline — classification, claims, fallacies, and confidence scoring."
          : "Ask anything. Expect honest, critical answers — not empty validation."}
      </p>

      <div className="grid w-full max-w-xl gap-2">
        {suggestions.map((suggestion) => (
          <MotionButton
            key={suggestion}
            variant="outline"
            className="h-auto min-h-11 justify-start whitespace-normal rounded-xl px-4 py-3 text-left text-sm font-normal touch-manipulation hover:bg-muted/50"
            onClick={() => onSelectSuggestion(suggestion)}
          >
            <MessageSquare className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            {suggestion}
          </MotionButton>
        ))}
      </div>
    </motion.div>
  );
}
