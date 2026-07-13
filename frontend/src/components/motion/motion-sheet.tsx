"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { X } from "lucide-react";

import {
  noMotionTransition,
  overlayVariants,
  sheetSlideLeftVariants,
  sheetSlideRightVariants,
} from "@/lib/motion";
import { cn } from "@/lib/utils";

interface AnimatedSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
  side?: "left" | "right";
  className?: string;
  showClose?: boolean;
  title?: string;
}

/** Mobile sidebar / dialog sheet with Framer Motion enter and exit. */
export function AnimatedSheet({
  open,
  onOpenChange,
  children,
  side = "left",
  className,
  showClose = true,
  title = "Dialog",
}: AnimatedSheetProps) {
  const reduceMotion = useReducedMotion();
  const slideVariants = side === "left" ? sheetSlideLeftVariants : sheetSlideRightVariants;

  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence mode="wait">
        {open && (
          <DialogPrimitive.Portal forceMount>
            <DialogPrimitive.Overlay asChild forceMount>
              <motion.div
                className="fixed inset-0 z-50 bg-black/80"
                variants={overlayVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                transition={reduceMotion ? noMotionTransition : undefined}
              />
            </DialogPrimitive.Overlay>

            <DialogPrimitive.Content asChild forceMount>
              <motion.aside
                className={cn(
                  "fixed z-50 flex h-full flex-col bg-background shadow-lg outline-none",
                  side === "left" ? "inset-y-0 left-0 border-r" : "inset-y-0 right-0 border-l",
                  className,
                )}
                variants={slideVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                transition={reduceMotion ? noMotionTransition : undefined}
              >
                <DialogPrimitive.Title className="sr-only">{title}</DialogPrimitive.Title>
                {children}
                {showClose && (
                  <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
                    <X className="h-4 w-4" />
                    <span className="sr-only">Close</span>
                  </DialogPrimitive.Close>
                )}
              </motion.aside>
            </DialogPrimitive.Content>
          </DialogPrimitive.Portal>
        )}
      </AnimatePresence>
    </DialogPrimitive.Root>
  );
}

/** @deprecated Use AnimatedSheet */
export { AnimatedSheet as MotionSheetContent };
