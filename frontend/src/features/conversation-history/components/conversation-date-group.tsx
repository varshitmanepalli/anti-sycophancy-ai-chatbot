"use client";

import { motion } from "framer-motion";

import type { DateGroup } from "../utils/group-by-date";
import { ConversationItem } from "./conversation-item";

interface ConversationDateGroupProps {
  group: DateGroup;
  activeId: string | null;
  onNavigate?: () => void;
}

/** Date-grouped section header and conversation items. */
export function ConversationDateGroup({
  group,
  activeId,
  onNavigate,
}: ConversationDateGroupProps) {
  return (
    <motion.section
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      aria-label={group.label}
    >
      <h3 className="sticky top-0 z-10 bg-sidebar/95 px-2 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground backdrop-blur">
        {group.label}
      </h3>
      <div className="space-y-0.5">
        {group.conversations.map((conversation, index) => (
          <ConversationItem
            key={conversation.id}
            conversation={conversation}
            isActive={activeId === conversation.id}
            onNavigate={onNavigate}
            index={index}
          />
        ))}
      </div>
    </motion.section>
  );
}
