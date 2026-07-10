import type { CyclePhase } from "@/components/phase-theme";

export const PHASE_LABEL: Record<CyclePhase, string> = {
  menstrual: "Menstrual",
  follicular: "Follicular",
  ovulatory: "Ovulatory",
  luteal: "Luteal",
};

// Tailwind's JIT scanner needs complete literal class strings somewhere in
// the source — these lookup maps exist so picking a class by the current
// phase never becomes a runtime-constructed string like
// `text-phase-${phase}-text`, which Tailwind can't see and won't generate.

// Phase color used AS text (headline "Luteal Phase" on --background). Per
// CLAUDE.md's Color usage rules, this is the only tier allowed for that.
export const PHASE_TEXT_CLASS: Record<CyclePhase, string> = {
  menstrual: "text-phase-menstrual-text",
  follicular: "text-phase-follicular-text",
  ovulatory: "text-phase-ovulatory-text",
  luteal: "text-phase-luteal-text",
};

// CycleWheel's progress arc deliberately also uses the *-text tier rather
// than the raw decorative accent — see the component for why (raw
// menstrual/follicular/luteal accents fail WCAG 1.4.11 non-text contrast
// against the wheel's track/background; the darker *-text tier clears it).
export const PHASE_STROKE_CLASS: Record<CyclePhase, string> = {
  menstrual: "stroke-phase-menstrual-text",
  follicular: "stroke-phase-follicular-text",
  ovulatory: "stroke-phase-ovulatory-text",
  luteal: "stroke-phase-luteal-text",
};

// Soft tint background, paired with default --foreground text.
export const PHASE_SOFT_CLASS: Record<CyclePhase, string> = {
  menstrual: "bg-phase-menstrual-soft",
  follicular: "bg-phase-follicular-soft",
  ovulatory: "bg-phase-ovulatory-soft",
  luteal: "bg-phase-luteal-soft",
};
