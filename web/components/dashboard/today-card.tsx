import { apiServer } from "@/lib/api-server";
import { TodayCardBody, type RecommendationsResponse } from "./today-card-body";

// services/gamification.py (streak/petals) doesn't exist yet (CC-18), but
// /recommendations/today is real — no placeholder needed for the happy
// path. This fallback only covers the endpoint being unreachable/erroring,
// same "render something today" spirit as dashboard/page.tsx's own
// getPrediction() fallback.
const FALLBACK: RecommendationsResponse = {
  phase: "luteal",
  cycle_day: 1,
  content: {
    phase_summary: "Here's a gentle starting point for today — your personalized guidance is on its way.",
    workout: {
      intensity_label: "Moderate",
      plan: ["Take a short walk", "Stretch for 10 minutes", "Rest if your body asks for it"],
      avoid: "Nothing specific today — just listen to your body.",
    },
    nutrition: {
      focus: "Balanced, nourishing meals",
      foods: ["Dal", "Rice", "Seasonal vegetables", "Fruit", "Nuts", "Dahi (yogurt)"],
      tip: "Stay hydrated and eat when you're hungry.",
    },
  },
  adaptive_line: null,
  disclaimer:
    "Cycle-phase fitness and nutrition guidance draws on emerging, still-developing research — it's a helpful starting point, not a strict prescription. Listen to your body first.",
};

async function getRecommendations(): Promise<RecommendationsResponse> {
  try {
    return await apiServer.get<RecommendationsResponse>("/recommendations/today");
  } catch {
    return FALLBACK;
  }
}

export async function TodayCard() {
  const recommendations = await getRecommendations();
  return <TodayCardBody recommendations={recommendations} />;
}
