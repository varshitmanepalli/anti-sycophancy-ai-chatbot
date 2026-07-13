"use client";

import { motion } from "framer-motion";
import { Check, X } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { COMPARISON } from "../data/content";
import { AnimatedSection } from "./animated-section";

/** Side-by-side comparison with traditional AI assistants. */
export function ComparisonSection() {
  return (
    <AnimatedSection
      id="compare"
      className="border-t bg-muted/20 px-4 py-24 sm:px-6"
    >
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-muted-foreground">
            Compare
          </p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            Traditional AI vs. Reasoning Engine
          </h2>
          <p className="mt-4 text-muted-foreground">
            Most assistants optimize for engagement. We optimize for accuracy and intellectual
            honesty.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          >
            <Card className="h-full border-border/60 bg-background/40 shadow-none">
              <CardHeader>
                <CardTitle className="text-base font-medium text-muted-foreground">
                  Traditional AI
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {COMPARISON.traditional.map((item) => (
                  <div key={item} className="flex items-start gap-3 text-sm">
                    <X className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground/60" strokeWidth={1.5} />
                    <span className="text-muted-foreground">{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          >
            <Card className="h-full border-foreground/20 bg-background shadow-sm">
              <CardHeader>
                <CardTitle className="text-base font-medium">Reasoning Engine</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {COMPARISON.reasoningEngine.map((item) => (
                  <div key={item} className="flex items-start gap-3 text-sm">
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-foreground" strokeWidth={1.5} />
                    <span>{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </AnimatedSection>
  );
}
