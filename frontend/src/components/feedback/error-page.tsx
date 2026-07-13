"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import {
  AlertTriangle,
  FileQuestion,
  Home,
  RefreshCw,
  WifiOff,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { ROUTES } from "@/config";
import { fadeUpVariants, noMotionTransition } from "@/lib/motion";
import { cn } from "@/utils";

import { RetryButton } from "./retry-button";

export type ErrorPageVariant = "error" | "notFound" | "offline";

interface ErrorPageProps {
  variant?: ErrorPageVariant;
  title?: string;
  message?: string;
  statusCode?: string | number;
  onRetry?: () => void;
  retryLabel?: string;
  homeHref?: string;
  homeLabel?: string;
  className?: string;
}

const variantDefaults: Record<
  ErrorPageVariant,
  { icon: LucideIcon; title: string; message: string; statusCode?: string }
> = {
  error: {
    icon: AlertTriangle,
    title: "Something went wrong",
    message: "An unexpected error occurred. Please try again.",
  },
  notFound: {
    icon: FileQuestion,
    title: "Page not found",
    message: "The page you are looking for does not exist or was moved.",
    statusCode: "404",
  },
  offline: {
    icon: WifiOff,
    title: "You are offline",
    message: "Check your connection and try again when you are back online.",
  },
};

/** Full-page error, 404, or offline experience. */
export function ErrorPage({
  variant = "error",
  title,
  message,
  statusCode,
  onRetry,
  retryLabel,
  homeHref = ROUTES.chat,
  homeLabel = "Back to chat",
  className,
}: ErrorPageProps) {
  const reduceMotion = useReducedMotion();
  const defaults = variantDefaults[variant];
  const Icon = defaults.icon;
  const displayCode = statusCode ?? defaults.statusCode;

  return (
    <div
      className={cn(
        "flex min-h-dvh items-center justify-center bg-background p-4 pb-safe pt-safe",
        className,
      )}
    >
      <motion.div
        variants={fadeUpVariants}
        initial="initial"
        animate="animate"
        transition={reduceMotion ? noMotionTransition : undefined}
        className="mx-auto max-w-md text-center"
      >
        {displayCode && (
          <p className="mb-2 text-5xl font-bold tracking-tight text-muted-foreground/40 sm:text-6xl">
            {displayCode}
          </p>
        )}

        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
          <Icon className="h-6 w-6" />
        </div>

        <h1 className="mb-2 text-xl font-semibold">{title ?? defaults.title}</h1>
        <p className="mb-6 text-sm text-muted-foreground">{message ?? defaults.message}</p>

        <div className="flex flex-wrap items-center justify-center gap-2">
          {onRetry && (
            <RetryButton onClick={onRetry} label={retryLabel ?? "Try again"} />
          )}
          <Button asChild variant={onRetry ? "outline" : "default"} className="min-h-11 gap-2 touch-manipulation">
            <Link href={homeHref}>
              {variant === "notFound" ? <Home className="h-4 w-4" /> : <RefreshCw className="h-4 w-4" />}
              {homeLabel}
            </Link>
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
