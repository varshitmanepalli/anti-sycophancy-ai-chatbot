"use client";

import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { useState } from "react";

import { Collapse } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { ReasoningItem } from "@/types/chat";

interface ReasoningSectionCardProps {
  title: string;
  description: string;
  items: ReasoningItem[];
  defaultOpen?: boolean;
  emptyLabel?: string;
}

/** Collapsible card for a single structured reasoning section. */
export function ReasoningSectionCard({
  title,
  description,
  items,
  defaultOpen = true,
  emptyLabel = "None identified",
}: ReasoningSectionCardProps) {
  const [open, setOpen] = useState(defaultOpen);
  const hasItems = items.length > 0;

  return (
    <Card className="overflow-hidden border-border/60 bg-background/80 shadow-none">
      <CardHeader className="p-0">
        <motion.button
          type="button"
          onClick={() => setOpen((prev) => !prev)}
          className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/40"
          aria-expanded={open}
          whileTap={{ scale: 0.99 }}
        >
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium">{title}</p>
              <Badge variant="secondary" className="h-5 px-1.5 text-[10px] font-normal">
                {items.length}
              </Badge>
            </div>
            <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
          </div>
          <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
          </motion.span>
        </motion.button>
      </CardHeader>

      <Collapse open={open}>
        <CardContent className="space-y-2 border-t px-4 pb-4 pt-3">
          {hasItems ? (
            items.map((item, index) => (
              <motion.div
                key={`${item.text}-${index}`}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
                className="rounded-lg border border-border/50 bg-muted/20 px-3 py-2.5"
              >
                <p className="text-sm leading-relaxed">{item.text}</p>
                {(item.source || item.confidence > 0) && (
                  <div className="mt-1.5 flex flex-wrap items-center gap-2 text-[10px] text-muted-foreground">
                    {item.source && (
                      <span className="rounded bg-muted px-1.5 py-0.5 font-medium uppercase tracking-wide">
                        {item.source.replace(/_/g, " ")}
                      </span>
                    )}
                    {item.confidence > 0 && (
                      <span>{Math.round(item.confidence * 100)}% confidence</span>
                    )}
                  </div>
                )}
              </motion.div>
            ))
          ) : (
            <p className="text-xs text-muted-foreground">{emptyLabel}</p>
          )}
        </CardContent>
      </Collapse>
    </Card>
  );
}
