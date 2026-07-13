"use client";

import { cn } from "@/utils";
import { normalizeConfidence } from "../../utils/structured-reasoning";

interface ConfidenceScoreCardProps {
  score: number;
  className?: string;
}

/** Visual confidence score with progress bar. */
export function ConfidenceScoreCard({ score, className }: ConfidenceScoreCardProps) {
  const normalized = normalizeConfidence(score);
  const percent = Math.round(normalized * 100);

  const tone =
    normalized >= 0.7 ? "text-emerald-600 dark:text-emerald-400" : normalized >= 0.4 ? "text-amber-600 dark:text-amber-400" : "text-red-600 dark:text-red-400";

  const barTone =
    normalized >= 0.7 ? "bg-emerald-500" : normalized >= 0.4 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className={cn("text-3xl font-semibold tabular-nums tracking-tight", tone)}>
            {percent}%
          </p>
          <p className="text-xs text-muted-foreground">Overall confidence in this analysis</p>
        </div>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className={cn("h-full rounded-full transition-all duration-500 ease-out", barTone)}
          style={{ width: `${percent}%` }}
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Confidence score ${percent} percent`}
        />
      </div>
    </div>
  );
}
