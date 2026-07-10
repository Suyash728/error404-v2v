import Link from "next/link";
import { apiServer } from "@/lib/api-server";
import { CalendarGrid, type CalendarCycle, type CalendarPrediction } from "@/components/calendar/calendar-grid";

const DEFAULT_PERIOD_LENGTH = 5;

async function getCycles(): Promise<CalendarCycle[]> {
  try {
    return await apiServer.get<CalendarCycle[]>("/cycles");
  } catch {
    return [];
  }
}

async function getPrediction(): Promise<CalendarPrediction | null> {
  try {
    return await apiServer.get<CalendarPrediction>("/cycles/prediction");
  } catch {
    // Same "brand-new user, predict() has nothing to anchor on" case as
    // dashboard/page.tsx — the calendar still renders, just without
    // predicted-period/fertile-window shading.
    return null;
  }
}

async function getPeriodLength(): Promise<number> {
  try {
    const profile = await apiServer.get<{ avg_period_len: number }>("/account/profile");
    return profile.avg_period_len;
  } catch {
    return DEFAULT_PERIOD_LENGTH;
  }
}

export default async function CalendarPage() {
  const [cycles, prediction, periodLength] = await Promise.all([
    getCycles(),
    getPrediction(),
    getPeriodLength(),
  ]);

  return (
    <main className="mx-auto flex max-w-[480px] flex-col gap-6 px-5 pb-28 pt-2">
      <header className="flex items-center">
        <Link
          href="/dashboard"
          aria-label="Back to dashboard"
          className="flex h-12 w-12 items-center justify-center rounded-full text-2xl text-brand-primary transition-opacity hover:opacity-80"
        >
          <span aria-hidden="true">←</span>
        </Link>
        <h1 className="flex-1 text-center text-xl font-extrabold text-brand-deep">Calendar</h1>
        <span aria-hidden="true" className="h-12 w-12" />
      </header>

      <CalendarGrid cycles={cycles} prediction={prediction} periodLength={periodLength} />
    </main>
  );
}
