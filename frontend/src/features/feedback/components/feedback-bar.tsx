"use client";

import { AnimatePresence } from "framer-motion";

import { cn } from "@/utils";

import { FEEDBACK_OPTIONS } from "../data/feedback-options";
import { useFeedback } from "../hooks/use-feedback";
import { useIsMobile } from "@/hooks";
import { FeedbackButton } from "./feedback-button";
import { FeedbackConfirmation } from "./feedback-confirmation";
import { ReportIssueForm } from "./report-issue-form";

interface FeedbackBarProps {
  messageId: string;
  conversationId: string;
  className?: string;
  /** Use shorter labels on narrow viewports. */
  compact?: boolean;
}

/** Reusable feedback bar for assistant message responses. */
export function FeedbackBar({
  messageId,
  conversationId,
  className,
  compact = false,
}: FeedbackBarProps) {
  const isMobile = useIsMobile();
  const useCompact = compact || isMobile;
  const {
    selectedType,
    isSubmitting,
    showConfirmation,
    showReportForm,
    handleSelect,
    handleReportSubmit,
    closeReportForm,
  } = useFeedback({ messageId, conversationId });

  return (
    <div className={cn("mt-4 space-y-3", className)}>
      <div className="flex flex-col gap-2">
        <p className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground">
          Was this response helpful?
        </p>

        <div className="flex flex-wrap gap-1.5">
          {FEEDBACK_OPTIONS.map((option) => (
            <FeedbackButton
              key={option.type}
              type={option.type}
              label={useCompact && option.shortLabel ? option.shortLabel : option.label}
              icon={option.icon}
              selected={selectedType === option.type}
              disabled={isSubmitting}
              onClick={() => handleSelect(option.type)}
            />
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        {showReportForm && (
          <ReportIssueForm
            onSubmit={handleReportSubmit}
            onCancel={closeReportForm}
            isSubmitting={isSubmitting}
          />
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {showConfirmation && !showReportForm && <FeedbackConfirmation />}
      </AnimatePresence>
    </div>
  );
}
