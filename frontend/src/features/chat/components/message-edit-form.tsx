"use client";

import { Check, X } from "lucide-react";
import { useEffect, useRef } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface MessageEditFormProps {
  initialValue: string;
  onSave: (value: string) => void;
  onCancel: () => void;
}

/** Inline editor for user messages. */
export function MessageEditForm({ initialValue, onSave, onCancel }: MessageEditFormProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.focus();
    el.setSelectionRange(el.value.length, el.value.length);
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, []);

  const handleSave = () => {
    const value = textareaRef.current?.value.trim() ?? "";
    if (value) onSave(value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    }
    if (e.key === "Escape") {
      onCancel();
    }
  };

  return (
    <div className="space-y-2">
      <Textarea
        ref={textareaRef}
        defaultValue={initialValue}
        onKeyDown={handleKeyDown}
        className="min-h-[80px] resize-none rounded-xl border bg-background text-sm"
        aria-label="Edit message"
      />
      <div className="flex justify-end gap-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
          <X className="h-3.5 w-3.5" />
          Cancel
        </Button>
        <Button type="button" size="sm" onClick={handleSave}>
          <Check className="h-3.5 w-3.5" />
          Save & resend
        </Button>
      </div>
    </div>
  );
}
