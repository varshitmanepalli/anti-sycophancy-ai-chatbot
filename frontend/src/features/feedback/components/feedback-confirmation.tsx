"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

/** Brief thank-you confirmation after feedback submission. */
export function FeedbackConfirmation() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -4, scale: 0.98 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
      className="flex items-center gap-2 text-xs text-muted-foreground"
      role="status"
    >
      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400">
        <Check className="h-3 w-3" />
      </span>
      Thanks for your feedback — it helps improve Reasoning Engine.
    </motion.div>
  );
}
