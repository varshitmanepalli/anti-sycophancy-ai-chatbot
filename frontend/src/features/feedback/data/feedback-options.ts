import {
  AlertTriangle,
  Flag,
  Frown,
  Heart,
  Sparkles,
  ThumbsUp,
  type LucideIcon,
} from "lucide-react";

import type { FeedbackType } from "../types";

export interface FeedbackOption {
  type: FeedbackType;
  label: string;
  shortLabel?: string;
  icon: LucideIcon;
  description: string;
}

export const FEEDBACK_OPTIONS: FeedbackOption[] = [
  {
    type: "helpful",
    label: "Helpful",
    icon: ThumbsUp,
    description: "This response was useful and accurate",
  },
  {
    type: "incorrect",
    label: "Incorrect",
    icon: AlertTriangle,
    description: "Contains factual or logical errors",
  },
  {
    type: "too_agreeable",
    label: "Too Agreeable",
    shortLabel: "Agreeable",
    icon: Heart,
    description: "Validated without sufficient critical analysis",
  },
  {
    type: "too_harsh",
    label: "Too Harsh",
    shortLabel: "Harsh",
    icon: Frown,
    description: "Overly dismissive or unnecessarily critical",
  },
  {
    type: "hallucination",
    label: "Hallucination",
    icon: Sparkles,
    description: "Invented facts or unsupported claims",
  },
  {
    type: "report_issue",
    label: "Report Issue",
    shortLabel: "Report",
    icon: Flag,
    description: "Report a bug, safety concern, or other issue",
  },
];

export function getFeedbackOption(type: FeedbackType): FeedbackOption | undefined {
  return FEEDBACK_OPTIONS.find((option) => option.type === type);
}
