"use client";

import { motion } from "framer-motion";
import Link from "next/link";

import { Logo } from "@/components/layout/logo";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { ROUTES } from "@/config";
import { cn } from "@/utils";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
}

/** Split auth layout — branding panel + form area. */
export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-dvh bg-background pt-safe pb-safe">
      <div className="mx-auto grid min-h-dvh lg:grid-cols-2">
        {/* Branding panel */}
        <div className="relative hidden overflow-hidden border-r bg-muted/20 lg:flex lg:flex-col lg:justify-between">
          <GridBackground />
          <div className="relative p-10">
            <Link href={ROUTES.home}>
              <Logo />
            </Link>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="relative px-10 pb-16"
          >
            <blockquote className="max-w-md space-y-4">
              <p className="text-2xl font-medium leading-snug tracking-tight">
                &ldquo;The AI that tells you the truth.&rdquo;
              </p>
              <p className="text-sm leading-relaxed text-muted-foreground">
                Sign in to access honest reasoning, structured debate analysis, and
                confidence-calibrated answers — not empty validation.
              </p>
            </blockquote>
          </motion.div>

          <div className="relative px-10 pb-10 text-xs text-muted-foreground">
            © {new Date().getFullYear()} Reasoning Engine
          </div>
        </div>

        {/* Form panel */}
        <div className="flex flex-col px-safe">
          <div className="flex items-center justify-between p-4 sm:p-6">
            <Link href={ROUTES.home} className="touch-manipulation lg:hidden">
              <Logo />
            </Link>
            <div className="ml-auto">
              <ThemeToggle />
            </div>
          </div>

          <div className="flex flex-1 items-center justify-center px-4 pb-8 sm:px-6 sm:pb-12">
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              className="w-full max-w-md"
            >
              <div className="mb-6 text-center sm:mb-8 lg:text-left">
                <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{title}</h1>
                {subtitle && (
                  <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
                )}
              </div>
              {children}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}

function GridBackground({ className }: { className?: string }) {
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
