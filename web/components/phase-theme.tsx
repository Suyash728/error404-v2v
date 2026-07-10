"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

export type CyclePhase = "menstrual" | "follicular" | "ovulatory" | "luteal";

type PhaseThemeContextValue = {
  phase: CyclePhase;
  setPhase: (phase: CyclePhase) => void;
};

const PhaseThemeContext = createContext<PhaseThemeContextValue | null>(null);

export function PhaseThemeProvider({
  initialPhase = "menstrual",
  children,
}: {
  initialPhase?: CyclePhase;
  children: ReactNode;
}) {
  const [phase, setPhase] = useState<CyclePhase>(initialPhase);

  // Sets data-phase on <html>, which globals.css keys its [data-phase="..."]
  // blocks off to swap --accent/--accent-2/--gradient. Runs client-side, so
  // there's a brief flash of `initialPhase`'s theme on first paint — fine
  // for now given how this is used today; revisit with a blocking inline
  // script if that flash becomes a real problem once pages consume this.
  useEffect(() => {
    document.documentElement.dataset.phase = phase;
  }, [phase]);

  const value = useMemo(() => ({ phase, setPhase }), [phase]);

  return <PhaseThemeContext.Provider value={value}>{children}</PhaseThemeContext.Provider>;
}

export function usePhaseTheme(): PhaseThemeContextValue {
  const context = useContext(PhaseThemeContext);
  if (!context) {
    throw new Error("usePhaseTheme must be used within a PhaseThemeProvider");
  }
  return context;
}
