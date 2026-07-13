"use client";

import { motion } from "framer-motion";

import { STEPS } from "../data/content";
import { AnimatedSection, StaggerChildren, staggerItem } from "./animated-section";

/** Three-step how-it-works section. */
export function HowItWorksSection() {
  return (
    <AnimatedSection id="how-it-works" className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-muted-foreground">
            How it works
          </p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            From question to honest answer
          </h2>
        </div>

        <StaggerChildren className="relative mt-16 grid gap-8 md:grid-cols-3">
          <div
            className="absolute left-0 right-0 top-8 hidden h-px bg-border md:block"
            aria-hidden
          />
          {STEPS.map((step, index) => (
            <motion.div key={step.step} variants={staggerItem} className="relative text-center md:text-left">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border bg-background font-mono text-sm text-muted-foreground md:mx-0">
                {step.step}
              </div>
              <h3 className="mt-6 text-lg font-medium">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{step.description}</p>
              {index < STEPS.length - 1 && (
                <div className="mx-auto mt-8 h-8 w-px bg-border md:hidden" aria-hidden />
              )}
            </motion.div>
          ))}
        </StaggerChildren>
      </div>
    </AnimatedSection>
  );
}
