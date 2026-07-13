import type { Transition, Variants } from "framer-motion";

/** Shared easing curve — smooth deceleration. */
export const EASE = [0.22, 1, 0.36, 1] as const;

export const DURATION = {
  fast: 0.15,
  normal: 0.25,
  slow: 0.4,
} as const;

export const transition = {
  fast: { duration: DURATION.fast, ease: EASE } satisfies Transition,
  normal: { duration: DURATION.normal, ease: EASE } satisfies Transition,
  slow: { duration: DURATION.slow, ease: EASE } satisfies Transition,
};

export const pageVariants: Variants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: transition.normal },
  exit: { opacity: 0, y: -4, transition: transition.fast },
};

export const fadeUpVariants: Variants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: transition.normal },
  exit: { opacity: 0, y: -8, transition: transition.fast },
};

export const scaleInVariants: Variants = {
  initial: { opacity: 0, scale: 0.96 },
  animate: { opacity: 1, scale: 1, transition: transition.normal },
  exit: { opacity: 0, scale: 0.98, transition: transition.fast },
};

export const slideFromLeftVariants: Variants = {
  initial: { opacity: 0, x: -16 },
  animate: { opacity: 1, x: 0, transition: transition.slow },
  exit: { opacity: 0, x: -12, transition: transition.fast },
};

export const slideFromRightVariants: Variants = {
  initial: { opacity: 0, x: 16 },
  animate: { opacity: 1, x: 0, transition: transition.slow },
  exit: { opacity: 0, x: 12, transition: transition.fast },
};

/** Full-width sheet slide — used for mobile drawers. */
export const sheetSlideLeftVariants: Variants = {
  initial: { x: "-100%" },
  animate: { x: 0, transition: transition.slow },
  exit: { x: "-100%", transition: transition.fast },
};

export const sheetSlideRightVariants: Variants = {
  initial: { x: "100%" },
  animate: { x: 0, transition: transition.slow },
  exit: { x: "100%", transition: transition.fast },
};

export const overlayVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: transition.normal },
  exit: { opacity: 0, transition: transition.fast },
};

export const collapseVariants: Variants = {
  initial: { height: 0, opacity: 0 },
  animate: { height: "auto", opacity: 1, transition: transition.normal },
  exit: { height: 0, opacity: 0, transition: transition.fast },
};

export const messageVariants: Variants = {
  initial: { opacity: 0, y: 10, scale: 0.99 },
  animate: { opacity: 1, y: 0, scale: 1, transition: transition.normal },
  exit: { opacity: 0, scale: 0.98, transition: transition.fast },
};

export const userMessageVariants: Variants = {
  initial: { opacity: 0, y: 8, x: 6 },
  animate: { opacity: 1, y: 0, x: 0, transition: transition.normal },
  exit: { opacity: 0, transition: transition.fast },
};

export const assistantMessageVariants: Variants = {
  initial: { opacity: 0, y: 8, x: -6 },
  animate: { opacity: 1, y: 0, x: 0, transition: transition.normal },
  exit: { opacity: 0, transition: transition.fast },
};

export const staggerContainer: Variants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.05, delayChildren: 0.04 },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: transition.normal },
};

export const cardHover = {
  rest: { y: 0, boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)" },
  hover: { y: -2, transition: transition.fast },
};

export const buttonTap = {
  whileHover: { scale: 1.02 },
  whileTap: { scale: 0.97 },
};

export const noMotionTransition: Transition = { duration: 0 };
