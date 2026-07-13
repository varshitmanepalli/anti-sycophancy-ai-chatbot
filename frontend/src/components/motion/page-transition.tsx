"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { usePathname } from "next/navigation";

import { noMotionTransition, pageVariants } from "@/lib/motion";
import { cn } from "@/utils";

interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

/** Subtle fade/slide when navigating between dashboard routes. */
export function PageTransition({ children, className }: PageTransitionProps) {
  const pathname = usePathname();
  const reduceMotion = useReducedMotion();

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={pathname}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={reduceMotion ? noMotionTransition : undefined}
        className={cn("flex flex-1 flex-col overflow-hidden", className)}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
