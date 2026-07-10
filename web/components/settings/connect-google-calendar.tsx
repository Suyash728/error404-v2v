"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Toast = { message: string; tone: "success" | "error" };

export function ConnectGoogleCalendar({ initiallyConnected }: { initiallyConnected: boolean }) {
  const [connected, setConnected] = useState(initiallyConnected);
  const [isConnecting, setIsConnecting] = useState(false);
  const [toast, setToast] = useState<Toast | null>(null);

  // The OAuth callback (routers/calendar.py) redirects back here with
  // ?gcal=connected|error after Google returns control to the app. Read via
  // window.location rather than next/navigation's useSearchParams to avoid
  // that hook's Suspense-boundary requirement for a one-time-on-mount read.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const gcalStatus = params.get("gcal");

    if (gcalStatus === "connected") {
      setConnected(true);
      setToast({ message: "Google Calendar connected — your predictions are synced.", tone: "success" });
    } else if (gcalStatus === "error") {
      setToast({ message: "Couldn't connect Google Calendar. Please try again.", tone: "error" });
    }

    if (gcalStatus) {
      window.history.replaceState(null, "", window.location.pathname);
    }
  }, []);

  async function handleConnect() {
    setIsConnecting(true);
    setToast(null);
    try {
      const { auth_url } = await api.get<{ auth_url: string }>("/calendar/oauth/start");
      window.location.href = auth_url;
    } catch {
      setToast({
        message: "Couldn't start the connection — check your connection and try again.",
        tone: "error",
      });
      setIsConnecting(false);
    }
  }

  return (
    <div className="rounded-2xl bg-surface p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            aria-hidden="true"
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-blush text-lg"
          >
            📅
          </div>
          <div>
            <p className="font-semibold text-foreground">Google Calendar</p>
            <p className="text-sm text-foreground/70">
              {connected ? "Connected — predictions sync automatically" : "Sync cycle predictions to your calendar"}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleConnect}
          disabled={connected || isConnecting}
          aria-label={connected ? "Google Calendar connected" : "Connect Google Calendar"}
          className="min-h-[44px] shrink-0 rounded-full bg-brand-primary px-4 py-2 text-sm font-bold text-on-accent transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {connected ? "Connected" : isConnecting ? "Connecting…" : "Connect"}
        </button>
      </div>

      {toast && (
        <p
          role={toast.tone === "error" ? "alert" : "status"}
          className={`mt-3 text-sm ${toast.tone === "error" ? "text-phase-menstrual-text" : "text-foreground/70"}`}
        >
          {toast.message}
        </p>
      )}
    </div>
  );
}
