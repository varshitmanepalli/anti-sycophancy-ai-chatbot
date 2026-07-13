"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

import { collapseVariants, noMotionTransition } from "@/lib/motion";

interface CollapseProps {
  open: boolean;
  children: React.ReactNode;
  className?: string;
}

/** Height-based collapse animation for panels and accordions. */
export function Collapse({ open, children, className }: CollapseProps) {
  const reduceMotion = useReducedMotion();

  return (
    <AnimatePresence initial={false}>
      {open && (
        <motion.div
          variants={collapseVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={reduceMotion ? noMotionTransition : undefined}
          className={className}
          style={{ overflow: "hidden" }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
