import type { ReactNode } from "react";
import { PhaseThemeProvider } from "@/components/phase-theme";
import { BottomNav } from "@/components/navigation/BottomNav";

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <PhaseThemeProvider>
      <div className="min-h-screen bg-background">
        {children}
        <BottomNav />
      </div>
    </PhaseThemeProvider>
  );
}
