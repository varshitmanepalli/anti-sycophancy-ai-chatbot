import type { LucideIcon } from "lucide-react";

export type FeedbackSize = "sm" | "md" | "lg";

export interface FeedbackAction {
  label: string;
  onClick: () => void;
  variant?: "default" | "outline" | "ghost" | "destructive";
  loading?: boolean;
  icon?: LucideIcon;
}
