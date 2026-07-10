"use client";

import { useEffect } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { usePhaseTheme, type CyclePhase } from "@/components/phase-theme";
import { PHASE_LABEL, PHASE_STROKE_CLASS, PHASE_TEXT_CLASS } from "./phase-classes";

const RADIUS = 100;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export function CycleWheel({
  phase,
  cycleDay,
  cycleLength,
  nextPeriodInDays,
}: {
  phase: CyclePhase;
  cycleDay: number;
  cycleLength: number;
  nextPeriodInDays: number;
}) {
  const { setPhase } = usePhaseTheme();
  const prefersReducedMotion = useReducedMotion();

  // Syncs the app-wide phase theme (data-phase, --accent/--accent-2/
  // --gradient) to whatever the server actually predicted for this user.
  useEffect(() => {
    setPhase(phase);
  }, [phase, setPhase]);

  const progress = Math.min(Math.max(cycleDay / cycleLength, 0), 1);
  const dashOffset = CIRCUMFERENCE * (1 - progress);
  const label = PHASE_LABEL[phase];

  return (
    <div
      role="img"
      aria-label={`Cycle day ${cycleDay} of ${cycleLength}, ${label} phase. Next period in ${nextPeriodInDays} days.`}
      className="relative mx-auto h-60 w-60 max-w-full"
    >
      <svg viewBox="0 0 240 240" className="h-full w-full -rotate-90" aria-hidden="true">
        <circle cx="120" cy="120" r={RADIUS} fill="none" stroke="var(--border)" strokeWidth="16" />
        <motion.circle
          cx="120"
          cy="120"
          r={RADIUS}
          fill="none"
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          className={PHASE_STROKE_CLASS[phase]}
          initial={false}
          animate={{ strokeDashoffset: dashOffset }}
          transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.8, ease: "easeOut" }}
        />
      </svg>
      <div
        aria-hidden="true"
        className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center"
      >
        <span className="text-xs font-semibold uppercase tracking-wider text-foreground/70">
          Day {cycleDay}
        </span>
        <p className={`mt-1 text-2xl font-extrabold ${PHASE_TEXT_CLASS[phase]}`}>{label} Phase</p>
        <span className="mt-2 rounded-full bg-surface px-3 py-1 text-xs text-foreground shadow-sm">
          Next period in {nextPeriodInDays} days
        </span>
      </div>
    </div>
  );
}
