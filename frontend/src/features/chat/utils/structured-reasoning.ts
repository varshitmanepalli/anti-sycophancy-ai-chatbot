import type { StructuredReasoning } from "@/types/chat";

/** Returns true when there is user-facing structured reasoning to display. */
export function hasStructuredReasoning(
  reasoning: StructuredReasoning | null | undefined,
): boolean {
  if (!reasoning) return false;
  return (
    reasoning.facts.length > 0 ||
    reasoning.assumptions.length > 0 ||
    reasoning.evidence.length > 0 ||
    reasoning.counterarguments.length > 0 ||
    reasoning.alternative_explanations.length > 0 ||
    reasoning.confidence_score > 0
  );
}

/** Normalize confidence to 0–1 range for display. */
export function normalizeConfidence(score: number): number {
  if (score > 1) return Math.min(score / 100, 1);
  return Math.max(0, Math.min(score, 1));
}

export const REASONING_SECTIONS = [
  {
    key: "facts" as const,
    title: "Facts",
    description: "Verified or strongly supported statements",
  },
  {
    key: "assumptions" as const,
    title: "Assumptions",
    description: "Unstated beliefs required by the argument",
  },
  {
    key: "evidence" as const,
    title: "Evidence",
    description: "Information cited to support claims",
  },
  {
    key: "counterarguments" as const,
    title: "Counterarguments",
    description: "Challenges to the reasoning or conclusion",
  },
  {
    key: "alternative_explanations" as const,
    title: "Alternative Explanations",
    description: "Other plausible interpretations or unknowns",
  },
];
