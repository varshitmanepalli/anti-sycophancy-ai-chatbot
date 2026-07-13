"use client";

import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ROUTES } from "@/config";

import { HERO } from "../data/content";
import { GridBackground } from "./landing-nav";

/** Hero section with headline, subtext, and CTAs. */
export function HeroSection() {
  return (
    <section className="relative overflow-hidden px-4 pb-24 pt-20 sm:px-6 sm:pb-32 sm:pt-28">
      <GridBackground />

      <div className="relative mx-auto max-w-4xl text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Badge variant="outline" className="mb-6 gap-1.5 px-3 py-1 text-xs font-normal">
            <Sparkles className="h-3 w-3" />
            Anti-sycophancy reasoning engine
          </Badge>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
          className="text-4xl font-semibold tracking-tight sm:text-5xl md:text-6xl md:leading-[1.1]"
        >
          {HERO.headline}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
          className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg"
        >
          {HERO.subheadline}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
          className="mt-10 flex w-full max-w-sm flex-col items-stretch justify-center gap-3 sm:mx-auto sm:max-w-none sm:flex-row sm:items-center"
        >
          <Button asChild size="lg" className="h-12 w-full gap-2 px-6 touch-manipulation sm:h-11 sm:w-auto">
            <Link href={ROUTES.chat}>
              {HERO.primaryCta}
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="h-12 w-full px-6 touch-manipulation sm:h-11 sm:w-auto">
            <a href="#how-it-works">{HERO.secondaryCta}</a>
          </Button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="mx-auto mt-16 max-w-2xl rounded-xl border bg-card/50 p-6 text-left shadow-sm backdrop-blur sm:p-8"
        >
          <div className="mb-4 flex items-center gap-2 text-xs text-muted-foreground">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-500/80" />
            Live reasoning preview
          </div>
          <div className="space-y-4 text-sm">
            <div className="rounded-lg bg-muted/50 px-4 py-3">
              <p className="text-xs font-medium text-muted-foreground">You</p>
              <p className="mt-1">Should I quit my job to pursue this startup idea?</p>
            </div>
            <div className="rounded-lg border px-4 py-3">
              <p className="text-xs font-medium text-muted-foreground">Reasoning Engine</p>
              <p className="mt-1 leading-relaxed">
                That decision depends on runway, validated demand, and risk tolerance — none of
                which appear in your question. I would not treat excitement alone as sufficient
                evidence. Let&apos;s examine what you actually know vs. what you are assuming.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
