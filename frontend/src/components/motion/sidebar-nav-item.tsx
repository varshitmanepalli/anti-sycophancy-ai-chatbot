"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { transition } from "@/lib/motion";
import { cn } from "@/utils";

interface SidebarNavItemProps {
  href: string;
  label: string;
  icon: LucideIcon;
  isActive: boolean;
  onNavigate?: () => void;
}

/** Sidebar nav link with active indicator and subtle press feedback. */
export function SidebarNavItem({
  href,
  label,
  icon: Icon,
  isActive,
  onNavigate,
}: SidebarNavItemProps) {
  const reduceMotion = useReducedMotion();

  return (
    <Link href={href} onClick={onNavigate} className="relative block">
      {isActive && (
        <motion.span
          layoutId="sidebar-active"
          className="absolute inset-0 rounded-lg bg-sidebar-accent"
          transition={reduceMotion ? { duration: 0 } : { type: "spring", stiffness: 380, damping: 32 }}
        />
      )}
      <motion.span
        className={cn(
          "relative flex min-h-11 items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium touch-manipulation",
          isActive ? "text-foreground" : "text-muted-foreground",
        )}
        whileHover={reduceMotion ? undefined : { x: 2 }}
        whileTap={reduceMotion ? undefined : { scale: 0.98 }}
        transition={transition.fast}
      >
        <Icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
        {label}
      </motion.span>
    </Link>
  );
}
