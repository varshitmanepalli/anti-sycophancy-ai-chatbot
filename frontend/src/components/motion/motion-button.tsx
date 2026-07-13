"use client";

import { motion, useReducedMotion } from "framer-motion";
import * as React from "react";

import { Button, type ButtonProps } from "@/components/ui/button";
import { transition } from "@/lib/motion";
import { cn } from "@/utils";

/** Button with subtle hover/tap feedback — respects reduced motion. */
export const MotionButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  function MotionButton({ className, asChild, ...props }, ref) {
    const reduceMotion = useReducedMotion();

    if (asChild || reduceMotion) {
      return <Button ref={ref} asChild={asChild} className={className} {...props} />;
    }

    return (
      <motion.span
        className={cn("inline-flex", className?.includes("w-full") && "w-full")}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.97 }}
        transition={transition.fast}
      >
        <Button ref={ref} className={cn("w-full", className)} {...props} />
      </motion.span>
    );
  },
);

MotionButton.displayName = "MotionButton";
