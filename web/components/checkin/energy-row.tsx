"use client";

// Mirrors design-reference's own flow-selector pattern: one icon repeated at
// increasing sizes, rather than five distinct icons (source uses 5 battery
// ligatures here, but the same "one glyph, growing size" idea is simpler
// and matches how the mockup already treats flow intensity).
const LEVELS = [
  { value: 1, label: "Very low energy", sizeClass: "text-sm" },
  { value: 2, label: "Low energy", sizeClass: "text-base" },
  { value: 3, label: "Medium energy", sizeClass: "text-lg" },
  { value: 4, label: "High energy", sizeClass: "text-xl" },
  { value: 5, label: "Very high energy", sizeClass: "text-2xl" },
] as const;

export function EnergyRow({
  value,
  onChange,
}: {
  value: number | null;
  onChange: (value: number) => void;
}) {
  return (
    <section aria-labelledby="energy-heading" className="rounded-[20px] bg-surface p-4 shadow-sm">
      <h2 id="energy-heading" className="mb-4 text-lg font-semibold text-foreground">
        Energy Level
      </h2>
      <div role="group" aria-label="Energy level" className="flex items-end justify-between">
        {LEVELS.map((level) => {
          const isSelected = value === level.value;
          return (
            <button
              key={level.value}
              type="button"
              aria-pressed={isSelected}
              aria-label={level.label}
              onClick={() => onChange(level.value)}
              className={`flex h-12 w-12 items-center justify-center rounded-full transition-colors ${
                isSelected
                  ? "bg-brand-primary text-on-accent ring-2 ring-brand-primary ring-offset-2 ring-offset-surface"
                  : "bg-brand-blush text-foreground/60 hover:opacity-80"
              }`}
            >
              <span aria-hidden="true" className={level.sizeClass}>
                ⚡
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
