"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

const PETAL_COUNT = 8;
const RADIUS = 120;

export function PetalBloom({ show }: { show: boolean }) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          aria-hidden="true"
          className="pointer-events-none fixed inset-0 z-[60] flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.2 }}
        >
          {prefersReducedMotion
            ? <span className="text-6xl">🌸</span>
            : Array.from({ length: PETAL_COUNT }).map((_, index) => {
                const angle = (index / PETAL_COUNT) * 2 * Math.PI;
                return (
                  <motion.span
                    key={index}
                    className="absolute text-3xl"
                    initial={{ x: 0, y: 0, opacity: 1, scale: 0.5 }}
                    animate={{
                      x: Math.cos(angle) * RADIUS,
                      y: Math.sin(angle) * RADIUS,
                      opacity: 0,
                      scale: 1,
                    }}
                    transition={{ duration: 0.9, ease: "easeOut", delay: index * 0.03 }}
                  >
                    🌸
                  </motion.span>
                );
              })}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
