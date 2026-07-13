"use client";

import { motion, useReducedMotion } from "framer-motion";
import * as React from "react";

import { noMotionTransition, staggerContainer, staggerItem } from "@/lib/motion";
import { cn } from "@/utils";

interface StaggerListProps {
  children: React.ReactNode;
  className?: string;
}

/** Container that staggers child entrance animations. */
export function StaggerList({ children, className }: StaggerListProps) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      transition={reduceMotion ? noMotionTransition : undefined}
      className={className}
    >
      {children}
    </motion.div>
  );
}

interface StaggerItemProps {
  children: React.ReactNode;
  className?: string;
}

/** Single staggered list/card item. */
export function StaggerItem({ children, className }: StaggerItemProps) {
  return (
    <motion.div variants={staggerItem} className={cn(className)}>
      {children}
    </motion.div>
  );
}
