"use client";

const MOODS = [
  { value: 1, emoji: "😢", label: "Very low mood" },
  { value: 2, emoji: "😕", label: "Low mood" },
  { value: 3, emoji: "😐", label: "Okay mood" },
  { value: 4, emoji: "🙂", label: "Good mood" },
  { value: 5, emoji: "😄", label: "Great mood" },
] as const;

export function MoodRow({
  value,
  onChange,
}: {
  value: number | null;
  onChange: (value: number) => void;
}) {
  return (
    <section aria-labelledby="mood-heading" className="rounded-[20px] bg-surface p-4 shadow-sm">
      <h2 id="mood-heading" className="mb-4 text-lg font-semibold text-foreground">
        Mood
      </h2>
      <div role="group" aria-label="Mood" className="flex items-center justify-between">
        {MOODS.map((mood) => {
          const isSelected = value === mood.value;
          return (
            <button
              key={mood.value}
              type="button"
              aria-pressed={isSelected}
              aria-label={mood.label}
              onClick={() => onChange(mood.value)}
              className={`flex h-12 w-12 items-center justify-center rounded-full text-2xl transition-colors ${
                isSelected
                  ? "bg-brand-primary text-on-accent ring-2 ring-brand-primary ring-offset-2 ring-offset-surface"
                  : "bg-brand-blush hover:opacity-80"
              }`}
            >
              <span aria-hidden="true">{mood.emoji}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
