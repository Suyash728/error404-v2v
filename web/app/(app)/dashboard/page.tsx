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

// Matches api/models/schemas.py's Prediction exactly — current_phase (not
// phase) and next_period_start as a date (not a precomputed day count) are
// the API's real field names. A prior version of this file used a made-up
// shape that never matched what GET /cycles/prediction actually returns,
// which silently rendered blank phase/day labels on every real response
// (cycle_day/cycle_length happened to match by coincidence, phase and the
// day-count didn't).
type Prediction = {
  next_period_start: string;
  fertile_window: { start: string; end: string };
  current_phase: CyclePhase;
  cycle_day: number;
  cycle_length: number;
  confidence: "high" | "medium" | "low";
};

const PHASE_MESSAGE: Record<CyclePhase, string> = {
  menstrual: "Rest is productive too — be gentle with yourself today.",
  follicular: "Energy's building. A great day to start something new.",
  ovulatory: "You're at your peak — channel it into what matters most.",
  luteal: "Winding down. Small, steady steps will serve you well today.",
};

function daysFromToday(isoDate: string): number {
  const target = new Date(`${isoDate}T00:00:00`);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

// null means "we genuinely have no prediction to show" — a brand-new user
// with no logged cycles and no onboarding data makes predict() raise on the
// backend (GET /cycles/prediction 500s), which is a real, expected state,
// not an error to paper over with fabricated numbers.
async function getPrediction(): Promise<Prediction | null> {
  try {
    return await apiServer.get<Prediction>("/cycles/prediction");
  } catch {
    return null;
  }
}

export default async function DashboardPage() {
  const prediction = await getPrediction();
  const riskFlags: RiskFlag[] = [];

  return (
    <main className="mx-auto flex max-w-[480px] flex-col gap-8 px-5 pb-28 pt-6">
      <header className="flex items-start justify-between gap-3">
        <SakhiGreeting message={prediction ? PHASE_MESSAGE[prediction.current_phase] : "Let's get your cycle set up."} />
        <StreakFlower petals={12} />
      </header>

      <section aria-label="Cycle overview">
        {prediction ? (
          <CycleWheel
            phase={prediction.current_phase}
            cycleDay={prediction.cycle_day}
            cycleLength={prediction.cycle_length}
            nextPeriodInDays={daysFromToday(prediction.next_period_start)}
          />
        ) : (
          <div
            role="status"
            className="mx-auto flex h-60 w-60 max-w-full flex-col items-center justify-center gap-2 rounded-full bg-surface px-6 text-center shadow-sm"
          >
            <span aria-hidden="true" className="text-3xl">
              🌱
            </span>
            <p className="text-sm font-semibold text-foreground">Log a cycle to see your phase</p>
            <p className="text-xs text-foreground/70">We need at least one logged period to get started.</p>
          </div>
        )}
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
