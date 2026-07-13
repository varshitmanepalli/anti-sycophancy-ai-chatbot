"use client";

import { motion } from "framer-motion";
import { Send } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ReportIssueFormProps {
  onSubmit: (comment: string) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

/** Expandable form for detailed issue reports. */
export function ReportIssueForm({ onSubmit, onCancel, isSubmitting }: ReportIssueFormProps) {
  const [comment, setComment] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = comment.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setComment("");
  };

  return (
    <motion.form
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
      onSubmit={handleSubmit}
      className="overflow-hidden"
    >
      <div className="space-y-2 rounded-xl border border-border/60 bg-muted/20 p-3">
        <label htmlFor="report-issue" className="text-xs font-medium text-muted-foreground">
          Describe the issue (optional details help us investigate)
        </label>
        <Textarea
          id="report-issue"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="What went wrong? Include any relevant context…"
          rows={3}
          className="min-h-[72px] resize-none bg-background text-sm"
          disabled={isSubmitting}
        />
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" size="sm" disabled={!comment.trim() || isSubmitting} className="gap-1.5">
            <Send className="h-3.5 w-3.5" />
            Submit report
          </Button>
        </div>
      </div>
    </motion.form>
  );
}
