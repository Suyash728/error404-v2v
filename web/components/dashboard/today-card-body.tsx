"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

type WorkoutContent = { intensity_label: string; plan: string[]; avoid: string };
type NutritionContent = { focus: string; foods: string[]; tip: string };
type PhaseContent = { phase_summary: string; workout: WorkoutContent; nutrition: NutritionContent };

export type RecommendationsResponse = {
  phase: string;
  cycle_day: number;
  content: PhaseContent;
  adaptive_line: string | null;
  disclaimer: string;
};

export function TodayCardBody({ recommendations }: { recommendations: RecommendationsResponse }) {
  const [expanded, setExpanded] = useState(false);
  const detailId = useId();
  const prefersReducedMotion = useReducedMotion();
  const { content, adaptive_line, disclaimer } = recommendations;

  return (
    <section aria-labelledby="today-heading" className="rounded-2xl bg-surface p-4 shadow-sm">
      <h2 id="today-heading" className="mb-2 flex items-center gap-2 text-lg font-semibold text-foreground">
        <span aria-hidden="true">✨</span>
        Today for you
      </h2>

      <p className="text-sm text-foreground/80">{content.phase_summary}</p>

      {adaptive_line && (
        <div className="mt-3 flex items-start gap-2 rounded-xl bg-brand-blush p-3">
          <span aria-hidden="true" className="text-lg">
            💡
          </span>
          <p className="text-sm text-foreground">{adaptive_line}</p>
        </div>
      )}

      <button
        type="button"
        onClick={() => setExpanded((current) => !current)}
        aria-expanded={expanded}
        aria-controls={detailId}
        className="mt-3 flex min-h-[44px] items-center gap-1 text-sm font-semibold text-brand-deep hover:opacity-80"
      >
        {expanded ? "Show less" : "See today's plan"}
        <span aria-hidden="true" className={`transition-transform ${expanded ? "rotate-180" : ""}`}>
          ▾
        </span>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            id={detailId}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.25, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div className="mt-4 flex flex-col gap-4">
              <div className="rounded-xl bg-brand-blush p-3">
                <p className="text-xs font-bold uppercase tracking-wide text-foreground/60">
                  Workout · {content.workout.intensity_label}
                </p>
                <ul className="mt-2 flex flex-col gap-1.5 text-sm text-foreground">
                  {content.workout.plan.map((item) => (
                    <li key={item} className="flex gap-2">
                      <span aria-hidden="true">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-foreground/70">{content.workout.avoid}</p>
              </div>

              <div className="rounded-xl bg-brand-blush p-3">
                <p className="text-xs font-bold uppercase tracking-wide text-foreground/60">
                  Nutrition · {content.nutrition.focus}
                </p>
                <ul className="mt-2 flex flex-wrap gap-1.5">
                  {content.nutrition.foods.map((food) => (
                    <li
                      key={food}
                      className="rounded-full bg-surface px-2.5 py-1 text-xs font-semibold text-foreground"
                    >
                      {food}
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-foreground/70">{content.nutrition.tip}</p>
              </div>

              <p className="text-xs italic text-foreground/50">{disclaimer}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
