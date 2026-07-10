import type { ReactNode } from "react";
import { PhaseThemeProvider } from "@/components/phase-theme";

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <PhaseThemeProvider>
      <div className="min-h-screen bg-background">{children}</div>
    </PhaseThemeProvider>
  );
}
