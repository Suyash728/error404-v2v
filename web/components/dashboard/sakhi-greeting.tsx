export function SakhiGreeting({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-3">
      <div
        aria-hidden="true"
        className="relative flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full bg-phase-gradient text-2xl"
      >
        {/* Sakhi mascot placeholder — no illustration asset yet. */}
        🌸
      </div>
      <div>
        <h1 className="text-xl font-bold text-foreground">Good morning!</h1>
        <p className="text-sm text-foreground/70">{message}</p>
      </div>
    </div>
  );
}
