"use client";

import { motion, useReducedMotion } from "framer-motion";
import * as React from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fadeUpVariants, noMotionTransition } from "@/lib/motion";
import { cn } from "@/utils";

interface MotionCardProps extends React.HTMLAttributes<HTMLDivElement> {
  delay?: number;
  hover?: boolean;
}

/** Card with a subtle entrance animation and optional hover lift. */
export function MotionCard({
  children,
  className,
  delay = 0,
  hover = true,
  ...props
}: MotionCardProps) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      variants={fadeUpVariants}
      initial="initial"
      animate="animate"
      transition={reduceMotion ? noMotionTransition : { delay }}
      whileHover={
        hover && !reduceMotion
          ? { y: -2, transition: { duration: 0.15 } }
          : undefined
      }
    >
      <Card className={cn("border-border/60 shadow-sm", className)} {...props}>
        {children}
      </Card>
    </motion.div>
  );
}

export { CardHeader as MotionCardHeader, CardTitle as MotionCardTitle, CardContent as MotionCardContent };
