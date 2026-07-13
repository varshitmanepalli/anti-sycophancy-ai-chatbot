"use client";

import { motion } from "framer-motion";
import { Menu } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { Logo } from "@/components/layout/logo";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { AnimatedSheet, MotionButton } from "@/components/motion";
import { ROUTES } from "@/config";
import { cn } from "@/utils";

import { NAV_LINKS } from "../data/content";

/** Sticky landing page navigation. */
export function LandingNav() {
  const [open, setOpen] = useState(false);

  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="sticky top-0 z-50 border-b border-border/60 bg-background/80 pt-safe backdrop-blur-md"
    >
      <div className="mx-auto flex h-14 min-h-[3.5rem] max-w-6xl items-center justify-between px-4 sm:h-16 sm:px-6">
        <Link href={ROUTES.home} aria-label="Reasoning Engine home" className="touch-manipulation">
          <Logo />
        </Link>

        <nav className="hidden items-center gap-6 md:flex" aria-label="Main">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-1 sm:gap-2">
          <ThemeToggle />
          <MotionButton asChild variant="ghost" size="sm" className="hidden sm:inline-flex">
            <Link href={ROUTES.auth.login}>Sign in</Link>
          </MotionButton>
          <MotionButton asChild size="sm" className="hidden sm:inline-flex">
            <Link href={ROUTES.chat}>Get started</Link>
          </MotionButton>

          <MotionButton
            variant="ghost"
            size="iconTouch"
            className="md:hidden touch-manipulation"
            aria-label="Open menu"
            onClick={() => setOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </MotionButton>

          <AnimatedSheet
            open={open}
            onOpenChange={setOpen}
            side="right"
            className="w-[min(20rem,85vw)] p-6 pb-safe"
          >
            <p className="text-sm font-medium">Menu</p>
            <nav className="mt-6 flex flex-col gap-1" aria-label="Mobile">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="min-h-11 rounded-lg px-3 py-3 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground active:bg-muted/80 touch-manipulation"
                >
                  {link.label}
                </a>
              ))}
              <MotionButton asChild variant="outline" className="mt-4 h-11 touch-manipulation">
                <Link href={ROUTES.auth.login} onClick={() => setOpen(false)}>
                  Sign in
                </Link>
              </MotionButton>
              <MotionButton asChild className="h-11 touch-manipulation">
                <Link href={ROUTES.chat} onClick={() => setOpen(false)}>
                  Get started
                </Link>
              </MotionButton>
            </nav>
          </AnimatedSheet>
        </div>
      </div>
    </motion.header>
  );
}

/** Subtle grid background for hero and CTA sections. */
export function GridBackground({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,hsl(var(--border)/0.4)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--border)/0.4)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_75%)]",
        className,
      )}
      aria-hidden
    />
  );
}
