// Shared motion presets (Emil Kowalski philosophy): fast, purposeful, transform+
// opacity only, custom ease-out curve. Global reducedMotion="user" (see providers)
// makes Framer strip movement for users who ask for it.

import type { Transition, Variants } from "motion/react";

// Strong ease-out — starts fast, feels responsive (built-in easings are too weak).
export const EASE_OUT = [0.23, 1, 0.32, 1] as const;
export const EASE_DRAWER = [0.32, 0.72, 0, 1] as const;

export const fast: Transition = { duration: 0.22, ease: EASE_OUT };

// Element entering the screen (message, card): subtle rise + fade. Never scale(0).
export const enterUp: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: fast },
};

// Container that staggers its children in (landing chips, KPI tiles).
export const stagger = (delayChildren = 0): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: 0.05, delayChildren } },
});
