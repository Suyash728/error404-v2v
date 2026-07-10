"use client";

import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

export function WaterCounter({
  glasses,
  onIncrement,
}: {
  glasses: number;
  onIncrement: () => void;
}) {
  const [ripples, setRipples] = useState<number[]>([]);
  const prefersReducedMotion = useReducedMotion();

  function handleClick() {
    onIncrement();
    if (!prefersReducedMotion) {
      const id = Date.now();
      setRipples((current) => [...current, id]);
      setTimeout(() => {
        setRipples((current) => current.filter((rippleId) => rippleId !== id));
      }, 500);
    }
  }

  return (
    <section className="flex items-center justify-between rounded-[20px] bg-surface p-4 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-foreground">Water Intake</h2>
        <p className="mt-1 text-sm text-foreground/70">{glasses} glasses today</p>
      </div>
      <button
        type="button"
        onClick={handleClick}
        aria-label={`Add a glass of water. ${glasses} glasses logged today.`}
        className="relative flex h-12 w-12 items-center justify-center overflow-hidden rounded-full bg-brand-blush text-xl font-bold text-brand-primary transition-transform hover:opacity-80 active:scale-95"
      >
        <AnimatePresence>
          {ripples.map((id) => (
            <motion.span
              key={id}
              aria-hidden="true"
              className="absolute inset-0 rounded-full bg-brand-primary/30"
              initial={{ scale: 0, opacity: 0.6 }}
              animate={{ scale: 1.8, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          ))}
        </AnimatePresence>
        <span aria-hidden="true" className="relative">
          +
        </span>
      </button>
    </section>
  );
}
