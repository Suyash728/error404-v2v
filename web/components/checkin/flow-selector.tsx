"use client";

// Sizes and value scale match design-reference/daily_check_in/code.html's
// selectFlow(): 5 droplets growing w-8 -> w-16. Values are 0-4 to match the
// DB's `flow between 0 and 4` CHECK constraint directly (source's own
// onclick args were 1-indexed 1..5; this is 0-indexed on purpose).
//
// The two smallest visual sizes (32px, 40px) are under the 44px touch
// target minimum, so each button's hit area is a fixed 48x48 regardless of
// the visual circle size drawn inside it.
const LEVELS = [
  { value: 0, label: "No flow", circleClass: "h-8 w-8", iconClass: "text-sm" },
  { value: 1, label: "Light flow", circleClass: "h-10 w-10", iconClass: "text-base" },
  { value: 2, label: "Medium flow", circleClass: "h-12 w-12", iconClass: "text-lg" },
  { value: 3, label: "Heavy flow", circleClass: "h-14 w-14", iconClass: "text-xl" },
  { value: 4, label: "Very heavy flow", circleClass: "h-16 w-16", iconClass: "text-2xl" },
] as const;

export function FlowSelector({
  value,
  onChange,
}: {
  value: number | null;
  onChange: (value: number) => void;
}) {
  return (
    <section aria-labelledby="flow-heading" className="rounded-[20px] bg-surface p-4 shadow-sm">
      <h2 id="flow-heading" className="mb-4 text-lg font-semibold text-foreground">
        Flow Intensity
      </h2>
      <div role="group" aria-label="Flow intensity" className="flex h-16 items-end justify-between">
        {LEVELS.map((level) => {
          const isSelected = value === level.value;
          return (
            <button
              key={level.value}
              type="button"
              aria-pressed={isSelected}
              aria-label={level.label}
              onClick={() => onChange(level.value)}
              className="flex h-12 w-12 items-end justify-center"
            >
              <span
                aria-hidden="true"
                className={`flex items-center justify-center rounded-full transition-colors ${level.circleClass} ${
                  isSelected
                    ? "bg-phase-menstrual text-on-accent shadow-sm"
                    : "bg-brand-blush text-foreground/60"
                }`}
              >
                <span className={level.iconClass}>💧</span>
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
