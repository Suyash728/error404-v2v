import Link from "next/link";
import { apiServer } from "@/lib/api-server";
import type { CyclePhase } from "@/components/phase-theme";
import { CycleWheel } from "@/components/dashboard/cycle-wheel";
import { SakhiGreeting } from "@/components/dashboard/sakhi-greeting";
import { TodayCard } from "@/components/dashboard/today-card";
import { HydrationRing } from "@/components/dashboard/hydration-ring";
import { QuickMoodRow } from "@/components/dashboard/quick-mood-row";
import { StreakFlower } from "@/components/dashboard/streak-flower";
import { RiskBanner, type RiskFlag } from "@/components/dashboard/risk-banner";

type CyclePrediction = {
  phase: CyclePhase;
  cycle_day: number;
  cycle_length: number;
  next_period_in_days: number;
};

const PHASE_MESSAGE: Record<CyclePhase, string> = {
  menstrual: "Rest is productive too — be gentle with yourself today.",
  follicular: "Energy's building. A great day to start something new.",
  ovulatory: "You're at your peak — channel it into what matters most.",
  luteal: "Winding down. Small, steady steps will serve you well today.",
};

// services/prediction.py doesn't exist on the API yet, so there's no real
// GET /cycles/prediction to call. Falls back to placeholder data so this
// page renders today — swap this for a real api.get() call once that
// endpoint ships, no other change needed here.
async function getPrediction(): Promise<CyclePrediction> {
  try {
    return await apiServer.get<CyclePrediction>("/cycles/prediction");
  } catch {
    return { phase: "luteal", cycle_day: 22, cycle_length: 28, next_period_in_days: 6 };
  }
}

export default async function DashboardPage() {
  const prediction = await getPrediction();
  const riskFlags: RiskFlag[] = [];

  return (
    <main className="mx-auto flex max-w-[480px] flex-col gap-8 px-5 pb-28 pt-6">
      <header className="flex items-start justify-between gap-3">
        <SakhiGreeting message={PHASE_MESSAGE[prediction.phase]} />
        <StreakFlower petals={12} />
      </header>

      <section aria-label="Cycle overview">
        <CycleWheel
          phase={prediction.phase}
          cycleDay={prediction.cycle_day}
          cycleLength={prediction.cycle_length}
          nextPeriodInDays={prediction.next_period_in_days}
        />
      </section>

      <RiskBanner flags={riskFlags} />

      <section aria-label="Today's insights" className="flex flex-col gap-4">
        <TodayCard />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <HydrationRing initialGlasses={5} goalGlasses={8} />
          <QuickMoodRow />
        </div>
      </section>

      <Link
        href="/checkin"
        className="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-full bg-brand-primary px-6 py-4 font-bold text-on-accent shadow-sm transition-opacity hover:opacity-90"
      >
        <span aria-hidden="true">📝</span>
        Log Symptoms
      </Link>
    </main>
  );
}
