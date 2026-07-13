"use client";

import { useCallback, useState } from "react";

import { submitMessageFeedback } from "@/services/api/feedback.service";
import { useFeedbackStore } from "@/stores";
import type { FeedbackType } from "@/features/feedback/types";

interface UseFeedbackOptions {
  messageId: string;
  conversationId: string;
}

/** Submit and track feedback for a single message. */
export function useFeedback({ messageId, conversationId }: UseFeedbackOptions) {
  const existing = useFeedbackStore((s) => s.getFeedback(messageId));
  const submitToStore = useFeedbackStore((s) => s.submitFeedback);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [showReportForm, setShowReportForm] = useState(false);

  const submit = useCallback(
    async (type: FeedbackType, comment?: string) => {
      setIsSubmitting(true);
      try {
        const payload = { messageId, conversationId, type, comment };
        submitToStore(payload);
        await submitMessageFeedback(payload);

        if (type === "report_issue") {
          setShowReportForm(false);
        }

        setShowConfirmation(true);
        setTimeout(() => setShowConfirmation(false), 2500);
      } finally {
        setIsSubmitting(false);
      }
    },
    [conversationId, messageId, submitToStore],
  );

  const handleSelect = useCallback(
    (type: FeedbackType) => {
      if (type === "report_issue") {
        setShowReportForm((prev) => !prev);
        return;
      }
      void submit(type);
    },
    [submit],
  );

  const handleReportSubmit = useCallback(
    (comment: string) => {
      void submit("report_issue", comment);
    },
    [submit],
  );

  return {
    selectedType: existing?.type ?? null,
    isSubmitting,
    showConfirmation,
    showReportForm,
    handleSelect,
    handleReportSubmit,
    closeReportForm: () => setShowReportForm(false),
  };
}
