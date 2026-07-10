"use client";

import { useMemo, useRef, useState, type KeyboardEvent } from "react";
import { motion, useReducedMotion } from "framer-motion";

export type CalendarCycle = {
  id: string;
  start_date: string;
  end_date: string | null;
  length: number | null;
};

export type CalendarPrediction = {
  next_period_start: string;
  fertile_window: { start: string; end: string };
  current_phase: "menstrual" | "follicular" | "ovulatory" | "luteal";
};

type DayStatus = "period" | "predicted-period" | "fertile" | null;

const WEEKDAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTH_FORMATTER = new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric" });
const CELL_LABEL_FORMATTER = new Intl.DateTimeFormat("en-US", { month: "long", day: "numeric", year: "numeric" });

const STATUS_LABEL: Record<Exclude<DayStatus, null>, string> = {
  period: "period day",
  "predicted-period": "predicted period",
  fertile: "fertile window",
};

function toLocalISODate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addDays(dateISO: string, days: number): string {
  const date = new Date(`${dateISO}T00:00:00`);
  date.setDate(date.getDate() + days);
  return toLocalISODate(date);
}

function isInRange(dateISO: string, startISO: string, endExclusiveISO: string): boolean {
  return dateISO >= startISO && dateISO < endExclusiveISO;
}

// Priority: an actually-logged period always wins over a prediction, and a
// predicted period wins over the fertile window (predicted period should
// never overlap the fertile window in practice, but if data ever puts a day
// in both, "period" is the more concrete claim).
function statusFor(
  dateISO: string,
  cycles: CalendarCycle[],
  prediction: CalendarPrediction | null,
  periodLength: number
): DayStatus {
  for (const cycle of cycles) {
    if (isInRange(dateISO, cycle.start_date, addDays(cycle.start_date, periodLength))) {
      return "period";
    }
  }
  if (prediction) {
    if (isInRange(dateISO, prediction.next_period_start, addDays(prediction.next_period_start, periodLength))) {
      return "predicted-period";
    }
    // fertile_window.end is inclusive (services/prediction.py), so +1 day
    // for the exclusive-end range check.
    if (isInRange(dateISO, prediction.fertile_window.start, addDays(prediction.fertile_window.end, 1))) {
      return "fertile";
    }
  }
  return null;
}

function getMonthGridDates(year: number, month: number): Date[] {
  const firstOfMonth = new Date(year, month, 1);
  const gridStart = new Date(year, month, 1 - firstOfMonth.getDay());
  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(gridStart);
    d.setDate(gridStart.getDate() + i);
    return d;
  });
}

function dayCellClassName({
  status,
  isToday,
  inMonth,
  isFirstOfFertileRange,
  isLastOfFertileRange,
}: {
  status: DayStatus;
  isToday: boolean;
  inMonth: boolean;
  isFirstOfFertileRange: boolean;
  isLastOfFertileRange: boolean;
}): string {
  const base =
    "relative flex h-11 w-11 items-center justify-center text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-deep";

  if (!inMonth) {
    return `${base} text-foreground/20`;
  }

  const todayRing = isToday ? "ring-2 ring-brand-deep ring-offset-2 ring-offset-surface" : "";

  // Solid fill + on-accent text: the same decorative-fill-with-safe-text
  // pairing TOKENS.md already established for raw phase accents (CycleWheel
  // uses the analogous *-text tier for its arc; this is the "badge" case
  // that tier table explicitly carves out as fine for raw accents).
  if (status === "period") {
    return `${base} rounded-full bg-phase-menstrual text-on-accent ${todayRing}`;
  }

  // Dashed outline + soft fill: not shown in any design-reference mockup
  // (nothing there distinguishes "happened" from "predicted"), so this is a
  // deliberate extrapolation — solid means confirmed, dashed/soft means
  // not-yet-happened. Both tokens are the already-AA-audited *-soft/*-text
  // tiers, not raw accents, so no new contrast risk either way.
  if (status === "predicted-period") {
    return `${base} rounded-full border-2 border-dashed border-phase-menstrual-text bg-phase-menstrual-soft text-foreground ${todayRing}`;
  }

  // Soft pill spanning the date range, rounded only at the range's actual
  // start/end — this one IS lifted directly from design-reference's
  // reproductive_health/code.html "Fertile Window" mini-calendar.
  if (status === "fertile") {
    const capClass =
      isFirstOfFertileRange && isLastOfFertileRange
        ? "rounded-full"
        : isFirstOfFertileRange
          ? "rounded-l-full"
          : isLastOfFertileRange
            ? "rounded-r-full"
            : "rounded-none";
    return `${base} ${capClass} bg-phase-ovulatory-soft text-foreground ${todayRing}`;
  }

  return `${base} rounded-full text-foreground hover:bg-brand-blush/50 ${todayRing}`;
}

export function CalendarGrid({
  cycles,
  prediction,
  periodLength,
}: {
  cycles: CalendarCycle[];
  prediction: CalendarPrediction | null;
  periodLength: number;
}) {
  const today = useMemo(() => new Date(), []);
  const todayISO = useMemo(() => toLocalISODate(today), [today]);
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const prefersReducedMotion = useReducedMotion();

  const gridDates = useMemo(() => getMonthGridDates(viewYear, viewMonth), [viewYear, viewMonth]);
  const cellRefs = useRef(new Map<string, HTMLButtonElement>());
  const [focusedISO, setFocusedISO] = useState<string>(() => {
    const todayInView = gridDates.find((d) => d.getMonth() === viewMonth && toLocalISODate(d) === todayISO);
    return todayInView ? todayISO : toLocalISODate(gridDates.find((d) => d.getMonth() === viewMonth) ?? gridDates[0]);
  });

  function goToMonth(delta: number) {
    const next = new Date(viewYear, viewMonth + delta, 1);
    setViewYear(next.getFullYear());
    setViewMonth(next.getMonth());
    const firstInMonth = getMonthGridDates(next.getFullYear(), next.getMonth()).find(
      (d) => d.getMonth() === next.getMonth()
    );
    if (firstInMonth) {
      setFocusedISO(toLocalISODate(firstInMonth));
    }
  }

  function moveFocus(fromISO: string, deltaDays: number) {
    const nextISO = addDays(fromISO, deltaDays);
    const nextDate = new Date(`${nextISO}T00:00:00`);
    if (nextDate.getMonth() !== viewMonth || nextDate.getFullYear() !== viewYear) {
      setViewYear(nextDate.getFullYear());
      setViewMonth(nextDate.getMonth());
    }
    setFocusedISO(nextISO);
    requestAnimationFrame(() => {
      cellRefs.current.get(nextISO)?.focus();
    });
  }

  function handleKeyDown(event: KeyboardEvent<HTMLButtonElement>, dateISO: string) {
    const arrowDeltas: Record<string, number> = {
      ArrowLeft: -1,
      ArrowRight: 1,
      ArrowUp: -7,
      ArrowDown: 7,
    };
    const delta = arrowDeltas[event.key];
    if (delta !== undefined) {
      event.preventDefault();
      moveFocus(dateISO, delta);
      return;
    }
    const dayOfWeek = new Date(`${dateISO}T00:00:00`).getDay();
    if (event.key === "Home") {
      event.preventDefault();
      moveFocus(dateISO, -dayOfWeek);
    } else if (event.key === "End") {
      event.preventDefault();
      moveFocus(dateISO, 6 - dayOfWeek);
    }
  }

  const monthLabel = MONTH_FORMATTER.format(new Date(viewYear, viewMonth, 1));

  return (
    <section aria-label="Cycle calendar" className="flex flex-col gap-4">
      <div className="flex items-center justify-between rounded-2xl bg-surface p-3 shadow-sm">
        <button
          type="button"
          onClick={() => goToMonth(-1)}
          aria-label="Previous month"
          className="flex h-11 w-11 items-center justify-center rounded-full text-lg text-brand-primary hover:bg-brand-blush"
        >
          <span aria-hidden="true">‹</span>
        </button>
        <p aria-live="polite" className="text-base font-bold text-foreground">
          {monthLabel}
        </p>
        <button
          type="button"
          onClick={() => goToMonth(1)}
          aria-label="Next month"
          className="flex h-11 w-11 items-center justify-center rounded-full text-lg text-brand-primary hover:bg-brand-blush"
        >
          <span aria-hidden="true">›</span>
        </button>
      </div>

      <motion.div
        key={`${viewYear}-${viewMonth}`}
        role="grid"
        aria-label={monthLabel}
        initial={prefersReducedMotion ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: prefersReducedMotion ? 0 : 0.2 }}
        className="rounded-2xl bg-surface p-3 shadow-sm"
      >
        <div role="row" className="mb-2 grid grid-cols-7 gap-1 text-center">
          {WEEKDAY_LABELS.map((label, index) => (
            <span
              key={index}
              role="columnheader"
              aria-hidden="true"
              className="text-xs font-bold uppercase text-foreground/50"
            >
              {label}
            </span>
          ))}
        </div>

        {Array.from({ length: 6 }, (_, week) => (
          <div key={week} role="row" className="grid grid-cols-7 gap-1">
            {gridDates.slice(week * 7, week * 7 + 7).map((date) => {
              const dateISO = toLocalISODate(date);
              const inMonth = date.getMonth() === viewMonth;
              const isToday = inMonth && dateISO === todayISO;
              const status = inMonth ? statusFor(dateISO, cycles, prediction, periodLength) : null;
              const isFirstOfFertileRange =
                status === "fertile" && statusFor(addDays(dateISO, -1), cycles, prediction, periodLength) !== "fertile";
              const isLastOfFertileRange =
                status === "fertile" && statusFor(addDays(dateISO, 1), cycles, prediction, periodLength) !== "fertile";

              const label = inMonth
                ? `${CELL_LABEL_FORMATTER.format(date)}${isToday ? ", today" : ""}${
                    status ? `, ${STATUS_LABEL[status]}` : ""
                  }`
                : "";

              return (
                <div key={dateISO} role="gridcell" className="flex items-center justify-center">
                  <button
                    type="button"
                    ref={(el) => {
                      if (el) {
                        cellRefs.current.set(dateISO, el);
                      } else {
                        cellRefs.current.delete(dateISO);
                      }
                    }}
                    tabIndex={inMonth && dateISO === focusedISO ? 0 : -1}
                    onFocus={() => inMonth && setFocusedISO(dateISO)}
                    onKeyDown={(event) => handleKeyDown(event, dateISO)}
                    aria-label={label || undefined}
                    disabled={!inMonth}
                    className={dayCellClassName({ status, isToday, inMonth, isFirstOfFertileRange, isLastOfFertileRange })}
                  >
                    <span aria-hidden="true">{date.getDate()}</span>
                  </button>
                </div>
              );
            })}
          </div>
        ))}
      </motion.div>

      <Legend />
    </section>
  );
}

function Legend() {
  const items: { swatchClassName: string; label: string }[] = [
    { swatchClassName: "bg-phase-menstrual", label: "Period" },
    {
      swatchClassName: "border-2 border-dashed border-phase-menstrual-text bg-phase-menstrual-soft",
      label: "Predicted period",
    },
    { swatchClassName: "bg-phase-ovulatory-soft", label: "Fertile window" },
    { swatchClassName: "ring-2 ring-brand-deep ring-offset-2 ring-offset-surface", label: "Today" },
  ];

  return (
    <ul className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-2xl bg-surface p-3 text-xs text-foreground/70 shadow-sm">
      {items.map((item) => (
        <li key={item.label} className="flex items-center gap-1.5">
          <span aria-hidden="true" className={`h-4 w-4 shrink-0 rounded-full ${item.swatchClassName}`} />
          {item.label}
        </li>
      ))}
    </ul>
  );
}
