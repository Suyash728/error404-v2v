"use client";

import { useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { MoodRow } from "@/components/checkin/mood-row";
import { EnergyRow } from "@/components/checkin/energy-row";
import { SymptomChips, type SymptomValue } from "@/components/checkin/symptom-chips";
import { FlowSelector } from "@/components/checkin/flow-selector";
import { WaterCounter } from "@/components/checkin/water-counter";
import { PeriodToggle } from "@/components/checkin/period-toggle";
import { PetalBloom } from "@/components/checkin/petal-bloom";

function todayLocalISODate(): string {
  const now = new Date();
  const offsetMs = now.getTimezoneOffset() * 60000;
  return new Date(now.getTime() - offsetMs).toISOString().slice(0, 10);
}

function extractErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError && error.body && typeof error.body === "object" && "detail" in error.body) {
    const detail = (error.body as { detail?: unknown }).detail;
    if (detail && typeof detail === "object" && "message" in detail) {
      const message = (detail as { message?: unknown }).message;
      if (typeof message === "string") {
        return message;
      }
    }
  }
  return fallback;
}

type Toast = { id: number; message: string; tone: "success" | "error" };

export default function CheckinPage() {
  const [mood, setMood] = useState<number | null>(null);
  const [energy, setEnergy] = useState<number | null>(null);
  const [symptoms, setSymptoms] = useState<Set<SymptomValue>>(new Set());
  const [flow, setFlow] = useState<number | null>(null);
  const [glasses, setGlasses] = useState(0);
  const [notes, setNotes] = useState("");
  const [periodStartedToday, setPeriodStartedToday] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showBloom, setShowBloom] = useState(false);
  const [toast, setToast] = useState<Toast | null>(null);

  function toggleSymptom(symptom: SymptomValue) {
    setSymptoms((current) => {
      const next = new Set(current);
      if (next.has(symptom)) {
        next.delete(symptom);
      } else {
        next.add(symptom);
      }
      return next;
    });
  }

  function showToast(message: string, tone: Toast["tone"] = "success") {
    const id = Date.now();
    setToast({ id, message, tone });
    setTimeout(() => {
      setToast((current) => (current?.id === id ? null : current));
    }, 3000);
  }

  async function handleSave() {
    if (isSaving) {
      return;
    }
    setIsSaving(true);

    // Optimistic: the ritual is "done" the moment you tap Save. The bloom
    // and success toast show immediately; the network calls below either
    // confirm that silently or correct it with an error toast.
    setShowBloom(true);
    setTimeout(() => setShowBloom(false), 1000);
    showToast("Saved! Keep blooming 🌸", "success");

    const today = todayLocalISODate();

    try {
      await api.post("/logs", {
        log_date: today,
        flow,
        symptoms: Array.from(symptoms),
        mood,
        energy,
        water_ml: glasses * 250,
        notes: notes.trim() || null,
      });
    } catch {
      showToast("Couldn't save your check-in — check your connection and try again.", "error");
      setIsSaving(false);
      return;
    }

    if (periodStartedToday) {
      try {
        await api.post("/cycles", { start_date: today });
      } catch (error) {
        showToast(
          extractErrorMessage(error, "Check-in saved, but couldn't mark the period start."),
          "error",
        );
      }
    }

    // Best-effort: gamification's own check-in endpoint (CC-18) doesn't
    // exist on the API yet. Never blocks the save flow above — the ritual
    // succeeding doesn't depend on petals actually being awarded.
    api.post("/gamification/checkin", {}).catch(() => {});

    setIsSaving(false);
  }

  return (
    <main className="mx-auto flex max-w-[480px] flex-col gap-6 px-5 pb-12 pt-2">
      <header className="flex items-center">
        <Link
          href="/dashboard"
          aria-label="Back to dashboard"
          className="flex h-12 w-12 items-center justify-center rounded-full text-2xl text-brand-primary transition-opacity hover:opacity-80"
        >
          <span aria-hidden="true">←</span>
        </Link>
      </header>

      <div className="flex flex-col items-center text-center">
        <div
          aria-hidden="true"
          className="mb-4 flex h-24 w-24 items-center justify-center rounded-full bg-brand-blush text-4xl shadow-sm"
        >
          🌸
        </div>
        <h1 className="text-2xl font-extrabold text-brand-deep">How are you today?</h1>
        <p className="mt-2 text-foreground/70">Let&apos;s log your daily check-in.</p>
      </div>

      <MoodRow value={mood} onChange={setMood} />
      <EnergyRow value={energy} onChange={setEnergy} />
      <SymptomChips selected={symptoms} onToggle={toggleSymptom} />
      <FlowSelector value={flow} onChange={setFlow} />
      <WaterCounter glasses={glasses} onIncrement={() => setGlasses((current) => current + 1)} />
      <PeriodToggle checked={periodStartedToday} onChange={setPeriodStartedToday} />

      <section>
        <label htmlFor="checkin-notes" className="mb-2 block px-2 text-lg font-semibold text-foreground">
          Notes (optional)
        </label>
        <textarea
          id="checkin-notes"
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Anything else you want to note?"
          className="h-24 w-full resize-none rounded-xl bg-brand-blush p-4 text-sm text-foreground placeholder:text-foreground/50 focus:outline-none focus:ring-2 focus:ring-brand-primary"
        />
      </section>

      <button
        type="button"
        onClick={handleSave}
        disabled={isSaving}
        className="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-full bg-brand-primary px-6 py-4 font-bold text-on-accent shadow-sm transition-opacity hover:opacity-90 disabled:opacity-60"
      >
        Save &amp; bloom
        <span aria-hidden="true">🌸</span>
      </button>

      <PetalBloom show={showBloom} />

      {toast && (
        <div
          role={toast.tone === "error" ? "alert" : "status"}
          className={`fixed inset-x-4 bottom-6 z-50 rounded-2xl px-4 py-3 text-center text-sm font-semibold shadow-lg ${
            toast.tone === "error"
              ? "border-2 border-phase-menstrual-text bg-surface text-foreground"
              : "bg-brand-primary text-on-accent"
          }`}
        >
          {toast.message}
        </div>
      )}
    </main>
  );
}
