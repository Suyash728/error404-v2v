"use client";

import { useState } from "react";

const RADIUS = 32;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export function HydrationRing({
  initialGlasses,
  goalGlasses,
}: {
  initialGlasses: number;
  goalGlasses: number;
}) {
  const [glasses, setGlasses] = useState(Math.min(initialGlasses, goalGlasses));
  const goalMet = glasses >= goalGlasses;

  function logGlass() {
    setGlasses((current) => Math.min(current + 1, goalGlasses));
  }

  const progress = glasses / goalGlasses;
  const dashOffset = CIRCUMFERENCE * (1 - progress);

  return (
    <div className="flex min-h-[120px] items-center justify-between gap-3 rounded-2xl bg-surface p-4 shadow-sm">
      <div>
        <h2 className="mb-1 text-lg font-semibold text-foreground">Hydration</h2>
        <p className="text-sm text-foreground/70">
          {glasses} of {goalGlasses} glasses
        </p>
      </div>
      <button
        type="button"
        onClick={logGlass}
        disabled={goalMet}
        aria-label={`Log a glass of water. ${glasses} of ${goalGlasses} logged today.`}
        className="relative h-20 w-20 shrink-0 rounded-full transition-transform hover:enabled:scale-95 disabled:cursor-default"
      >
        <svg viewBox="0 0 80 80" className="h-full w-full -rotate-90" aria-hidden="true">
          <circle cx="40" cy="40" r={RADIUS} fill="none" stroke="var(--border)" strokeWidth="8" />
          <circle
            cx="40"
            cy="40"
            r={RADIUS}
            fill="none"
            className="stroke-brand-primary transition-[stroke-dashoffset] duration-300"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={dashOffset}
          />
        </svg>
        <span aria-hidden="true" className="absolute inset-0 flex items-center justify-center text-xl">
          💧
        </span>
      </button>
    </div>
  );
}
