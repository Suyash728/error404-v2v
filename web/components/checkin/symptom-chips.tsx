"use client";

import { motion, useReducedMotion } from "framer-motion";

// Matches api/constants.py's Symptom enum exactly — these values go
// straight into the DailyLogCreate.symptoms POST body, so they must stay in
// sync with the backend enum, not just look right.
const SYMPTOMS = [
  { value: "cramps", label: "Cramps" },
  { value: "bloating", label: "Bloating" },
  { value: "headache", label: "Headache" },
  { value: "acne", label: "Acne" },
  { value: "fatigue", label: "Fatigue" },
  { value: "tender_breasts", label: "Tender breasts" },
  { value: "back_pain", label: "Back pain" },
  { value: "nausea", label: "Nausea" },
  { value: "mood_swings", label: "Mood swings" },
  { value: "insomnia", label: "Insomnia" },
  { value: "cravings", label: "Cravings" },
  { value: "spotting", label: "Spotting" },
  { value: "diarrhea", label: "Diarrhea" },
  { value: "constipation", label: "Constipation" },
] as const;

export type SymptomValue = (typeof SYMPTOMS)[number]["value"];

export function SymptomChips({
  selected,
  onToggle,
}: {
  selected: Set<SymptomValue>;
  onToggle: (symptom: SymptomValue) => void;
}) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section aria-labelledby="symptoms-heading">
      <h2 id="symptoms-heading" className="mb-4 px-2 text-lg font-semibold text-foreground">
        Symptoms
      </h2>
      <div
        role="group"
        aria-label="Symptoms"
        className="no-scrollbar -mx-2 flex gap-2 overflow-x-auto px-2 pb-2"
      >
        {SYMPTOMS.map((symptom) => {
          const isSelected = selected.has(symptom.value);
          return (
            <motion.button
              key={symptom.value}
              type="button"
              aria-pressed={isSelected}
              onClick={() => onToggle(symptom.value)}
              animate={{ scale: isSelected ? 1.05 : 1 }}
              transition={
                prefersReducedMotion ? { duration: 0 } : { type: "spring", stiffness: 400, damping: 17 }
              }
              className={`min-h-[48px] flex-shrink-0 whitespace-nowrap rounded-full px-6 py-2 text-sm font-semibold transition-colors ${
                isSelected ? "bg-brand-primary text-on-accent shadow-sm" : "bg-brand-blush text-foreground/70"
              }`}
            >
              {symptom.label}
            </motion.button>
          );
        })}
      </div>
    </section>
  );
}
