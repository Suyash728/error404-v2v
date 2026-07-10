export function StreakFlower({ petals }: { petals: number }) {
  return (
    <div className="flex min-h-[48px] min-w-[48px] flex-col items-center justify-center gap-0.5 rounded-full bg-surface p-2 shadow-sm">
      <span aria-hidden="true" className="text-xl leading-none">
        🌸
      </span>
      <span aria-hidden="true" className="text-xs font-bold text-foreground">
        {petals}
      </span>
      <span className="sr-only">{petals} day streak, {petals} petals earned</span>
    </div>
  );
}
