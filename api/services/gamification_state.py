"""Read-only helpers for GET /gamification/state: figures out which Sakhi
copy context/streak_state apply today from the *existing* public.gamification
row. Streak/petal mutation (incrementing streaks, freezes, badges) is
CC-18's services/gamification.py — this module only reads, never writes.
"""

from datetime import date
from typing import Optional

from core.supabase import get_supabase
from models.schemas import Gamification

MILESTONE_STREAK_DAYS = {3, 7, 14, 30, 60, 100, 200, 365}


def get_gamification(user_id: str) -> Gamification:
    # No existence check: the auth.users trigger guarantees a gamification
    # row for every signed-up user, same invariant as profiles.
    response = (
        get_supabase().table("gamification").select("*").eq("user_id", user_id).limit(1).execute()
    )
    return Gamification(**response.data[0])


def streak_state_for(streak_count: int) -> str:
    if streak_count <= 0:
        return "none"
    if streak_count in MILESTONE_STREAK_DAYS:
        return "milestone"
    return "building"


def _days_missed(last_checkin: Optional[date], today: date) -> int:
    """Full days with no check-in since last_checkin, not counting today."""
    if last_checkin is None:
        return 0
    return max((today - last_checkin).days - 1, 0)


def _is_phase_transition_day(cycle_day: int, period_length: int, ovulation_day: int) -> bool:
    """True if today is the first day of whichever phase cycle_day falls
    in — derived purely from prediction.py's own phase boundaries
    (_phase_for_day), so no extra "previous phase" state needs storing."""
    transition_days = {
        1,  # into menstrual
        period_length + 1,  # into follicular
        ovulation_day - 4,  # into ovulatory (start of the fertile window)
        ovulation_day + 2,  # into luteal
    }
    return cycle_day in transition_days


def pick_context(
    *,
    streak_count: int,
    last_checkin: Optional[date],
    cycle_day: int,
    period_length: int,
    cycle_length: int,
    today: date,
) -> str:
    """Picks exactly one Sakhi copy context for today. Priority: a missed
    check-in nudge takes precedence (gentle-guilt copy only ever applies
    here), then a streak milestone or phase change if today is genuinely
    that day, then a plain greeting/prompt depending on whether today's
    check-in is already done.
    """
    missed_days = _days_missed(last_checkin, today)
    if missed_days >= 3:
        return "missed_3plus"
    if missed_days >= 1:
        return "missed_1"

    checked_in_today = last_checkin == today

    if checked_in_today and streak_count in MILESTONE_STREAK_DAYS:
        return "streak_milestone"

    ovulation_day = cycle_length - 14
    if _is_phase_transition_day(cycle_day, period_length, ovulation_day):
        return "phase_transition"

    return "greeting" if checked_in_today else "log_prompt"
