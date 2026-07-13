"use client";

import { motion } from "framer-motion";
import {
  Brain,
  Code2,
  Gauge,
  Layers,
  Scale,
  Shield,
  type LucideIcon,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

import { FEATURES } from "../data/content";
import { AnimatedSection, StaggerChildren, staggerItem } from "./animated-section";

const ICONS: Record<(typeof FEATURES)[number]["icon"], LucideIcon> = {
  shield: Shield,
  layers: Layers,
  scale: Scale,
  gauge: Gauge,
  brain: Brain,
  code: Code2,
};

/** Feature grid highlighting core capabilities. */
export function FeaturesSection() {
  return (
    <AnimatedSection
      id="features"
      className="border-t bg-muted/20 px-4 py-24 sm:px-6"
    >
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-muted-foreground">
            Features
          </p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            Built for critical thinking, not applause
          </h2>
          <p className="mt-4 text-muted-foreground">
            Every layer of the stack is designed to reduce sycophancy, hallucination, and
            overconfidence.
          </p>
        </div>

        <StaggerChildren className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => {
            const Icon = ICONS[feature.icon];
            return (
              <motion.div key={feature.title} variants={staggerItem}>
                <Card className="h-full border-border/60 bg-background/60 shadow-none transition-colors hover:border-border hover:bg-background">
                  <CardContent className="p-6">
                    <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg border bg-muted/50">
                      <Icon className="h-5 w-5 text-foreground/80" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-medium">{feature.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </StaggerChildren>
      </div>
    </AnimatedSection>
  );
}
