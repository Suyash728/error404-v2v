"use client";

export function PeriodToggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <section className="flex items-center justify-between rounded-[20px] bg-surface p-4 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-foreground">Period started today</h2>
        <p className="mt-1 text-sm text-foreground/70">Marks the start of a new cycle when saved.</p>
      </div>
      {/* Button hit area is 48x56 (touch-target minimum); the visual pill
          track inside it is a slimmer 32px tall, matching the mockup's
          proportions without shrinking the tappable area below 44px. */}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label="Period started today"
        onClick={() => onChange(!checked)}
        className="flex h-12 w-14 shrink-0 items-center"
      >
        <span
          aria-hidden="true"
          className={`relative h-8 w-14 rounded-full transition-colors ${
            checked ? "bg-brand-primary" : "bg-border"
          }`}
        >
          <span
            className={`absolute top-1 h-6 w-6 rounded-full bg-surface shadow-sm transition-transform ${
              checked ? "translate-x-7" : "translate-x-1"
            }`}
          />
        </span>
      </button>
    </section>
  );
}
