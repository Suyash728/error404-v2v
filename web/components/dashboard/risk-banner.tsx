export type RiskFlag = {
  flag_type: string;
  severity: "low" | "medium" | "high";
  explanation: string;
};

export function RiskBanner({ flags }: { flags: RiskFlag[] }) {
  if (flags.length === 0) {
    return null;
  }

  const [primary] = flags;

  return (
    <div role="status" className="flex items-start gap-3 rounded-2xl bg-brand-blush p-4">
      <span aria-hidden="true" className="text-xl">
        💡
      </span>
      <p className="text-sm text-foreground">{primary.explanation}</p>
    </div>
  );
}
