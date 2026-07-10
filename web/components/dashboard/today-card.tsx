const ITEMS = [
  {
    icon: "🧘",
    title: "Gentle yoga",
    description: "Focus on restorative poses to ease tension.",
  },
  {
    icon: "🥗",
    title: "Nutrient-rich foods",
    description: "Try adding leafy greens or nuts to your meals today.",
  },
] as const;

export function TodayCard() {
  return (
    <section aria-labelledby="today-heading" className="rounded-2xl bg-surface p-4 shadow-sm">
      <h2 id="today-heading" className="mb-4 flex items-center gap-2 text-lg font-semibold text-foreground">
        <span aria-hidden="true">✨</span>
        Today for you
      </h2>
      <div className="flex flex-col gap-3">
        {ITEMS.map((item) => (
          <div key={item.title} className="flex items-start gap-3 rounded-xl bg-brand-blush p-3">
            <div
              aria-hidden="true"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/20 text-lg"
            >
              {item.icon}
            </div>
            <div>
              <p className="font-semibold text-foreground">{item.title}</p>
              <p className="text-sm text-foreground/70">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
