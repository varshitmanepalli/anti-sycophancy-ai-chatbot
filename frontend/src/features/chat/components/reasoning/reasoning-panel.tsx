"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Brain, ChevronDown } from "lucide-react";
import { useEffect } from "react";

import { Collapse, MotionButton } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useIsMobile } from "@/hooks";
import { fadeUpVariants, noMotionTransition } from "@/lib/motion";
import { useChatStore, useConversationStore, useReasoningPanelStore } from "@/stores";

import { hasStructuredReasoning, REASONING_SECTIONS } from "../../utils/structured-reasoning";
import { ConfidenceScoreCard } from "./confidence-score-card";
import { ReasoningSectionCard } from "./reasoning-section-card";

interface ReasoningPanelProps {
  conversationId: string;
}

/** Collapsible panel displaying backend structured reasoning (not chain-of-thought). */
export function ReasoningPanel({ conversationId }: ReasoningPanelProps) {
  const isMobile = useIsMobile();
  const reduceMotion = useReducedMotion();
  const chatMode = useChatStore((s) => s.chatMode);
  const structuredReasoning = useConversationStore(
    (s) => s.conversations[conversationId]?.structuredReasoning,
  );
  const expanded = useReasoningPanelStore((s) => s.isExpanded(conversationId));
  const setExpanded = useReasoningPanelStore((s) => s.setExpanded);
  const toggleExpanded = useReasoningPanelStore((s) => s.toggleExpanded);

  useEffect(() => {
    if (!useReasoningPanelStore.getState().expandedByConversation[conversationId]) {
      setExpanded(conversationId, !isMobile);
    }
  }, [conversationId, isMobile, setExpanded]);

  if (chatMode !== "reasoning" || !hasStructuredReasoning(structuredReasoning)) {
    return null;
  }

  const reasoning = structuredReasoning!;
  const confidencePercent = Math.round(reasoning.confidence_score * 100);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={conversationId}
        variants={fadeUpVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={reduceMotion ? noMotionTransition : undefined}
        className="border-t bg-muted/10 px-3 py-2 sm:px-4 sm:py-3"
      >
        <Card className="mx-auto max-w-3xl border-border/60 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 py-3">
            <div className="flex items-center gap-2.5">
              <motion.div
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary"
                animate={reduceMotion ? undefined : { scale: [1, 1.05, 1] }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              >
                <Brain className="h-4 w-4" />
              </motion.div>
              <div>
                <p className="text-sm font-medium">Structured Reasoning</p>
                <p className="text-xs text-muted-foreground">
                  Facts, assumptions, and evidence — not raw chain-of-thought
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge
                variant={reasoning.confidence_score >= 0.7 ? "success" : "warning"}
                className="hidden sm:inline-flex"
              >
                {confidencePercent}% confidence
              </Badge>
              <MotionButton
                variant="ghost"
                size="iconTouch"
                className="touch-manipulation sm:h-8 sm:w-8"
                onClick={() => toggleExpanded(conversationId)}
                aria-label={expanded ? "Collapse reasoning panel" : "Expand reasoning panel"}
              >
                <motion.span
                  animate={{ rotate: expanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="h-4 w-4" />
                </motion.span>
              </MotionButton>
            </div>
          </CardHeader>

          <Collapse open={expanded}>
            <CardContent className="max-h-[40vh] space-y-3 overflow-y-auto border-t px-3 pb-3 pt-3 sm:max-h-none sm:px-4 sm:pb-4">
              <motion.div
                initial={reduceMotion ? false : { opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
              >
                <Card className="border-border/60 bg-muted/20 shadow-none">
                  <CardContent className="p-4">
                    <p className="mb-3 text-sm font-medium">Confidence Score</p>
                    <ConfidenceScoreCard score={reasoning.confidence_score} />
                  </CardContent>
                </Card>
              </motion.div>

              <div className="grid gap-3 sm:grid-cols-2">
                {REASONING_SECTIONS.map((section, index) => (
                  <motion.div
                    key={section.key}
                    initial={reduceMotion ? false : { opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.08 + index * 0.04 }}
                  >
                    <ReasoningSectionCard
                      title={section.title}
                      description={section.description}
                      items={reasoning[section.key]}
                      defaultOpen={reasoning[section.key].length > 0}
                    />
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Collapse>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
}
