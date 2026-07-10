"use client";

import { useState } from "react";

const MOODS = [
  { key: "awful", emoji: "😫", label: "Awful" },
  { key: "low", emoji: "😔", label: "Low" },
  { key: "okay", emoji: "😐", label: "Okay" },
  { key: "good", emoji: "🙂", label: "Good" },
  { key: "great", emoji: "🤩", label: "Great" },
] as const;

type MoodKey = (typeof MOODS)[number]["key"];

export function QuickMoodRow() {
  const [selected, setSelected] = useState<MoodKey | null>(null);

  return (
    <div className="flex min-h-[120px] flex-col justify-center gap-3 rounded-2xl bg-surface p-4 shadow-sm">
      <h2 className="text-lg font-semibold text-foreground">How are you feeling?</h2>
      <div role="group" aria-label="Mood check-in" className="flex items-center justify-between">
        {MOODS.map((mood) => {
          const isSelected = selected === mood.key;
          return (
            <button
              key={mood.key}
              type="button"
              aria-pressed={isSelected}
              aria-label={mood.label}
              onClick={() => setSelected(mood.key)}
              className={`flex h-12 w-12 items-center justify-center rounded-full text-2xl transition-colors ${
                isSelected ? "border-2 border-accent bg-accent/20" : "bg-brand-blush hover:opacity-80"
              }`}
            >
              <span aria-hidden="true">{mood.emoji}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
