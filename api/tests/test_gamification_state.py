from datetime import date

from services.gamification_state import pick_context, streak_state_for

TODAY = date(2026, 7, 11)


def test_streak_state_none_when_zero():
    assert streak_state_for(0) == "none"


def test_streak_state_milestone_on_milestone_day():
    assert streak_state_for(7) == "milestone"


def test_streak_state_building_otherwise():
    assert streak_state_for(4) == "building"


def test_pick_context_missed_3plus_takes_priority():
    context = pick_context(
        streak_count=10,
        last_checkin=date(2026, 7, 5),  # 6 days ago -> well past 3 missed days
        cycle_day=15,
        period_length=5,
        cycle_length=28,
        today=TODAY,
    )
    assert context == "missed_3plus"


def test_pick_context_missed_1_for_a_single_skipped_day():
    context = pick_context(
        streak_count=10,
        last_checkin=date(2026, 7, 9),  # yesterday was skipped, day before was logged
        cycle_day=15,
        period_length=5,
        cycle_length=28,
        today=TODAY,
    )
    assert context == "missed_1"


def test_pick_context_no_miss_when_checked_in_yesterday():
    context = pick_context(
        streak_count=10,
        last_checkin=date(2026, 7, 10),  # yesterday
        cycle_day=15,  # not a transition day, not a milestone
        period_length=5,
        cycle_length=28,
        today=TODAY,
    )
    assert context == "log_prompt"


def test_pick_context_streak_milestone_when_checked_in_today_on_milestone():
    context = pick_context(
        streak_count=7,
        last_checkin=TODAY,
        cycle_day=15,  # not a transition day
        period_length=5,
        cycle_length=28,
        today=TODAY,
    )
    assert context == "streak_milestone"


def test_pick_context_phase_transition_into_follicular():
    # period_length=5 -> cycle_day 6 is the first follicular day.
    context = pick_context(
        streak_count=2,  # not a milestone, so it can't shadow the transition
        last_checkin=date(2026, 7, 10),  # checked in yesterday, no miss
        cycle_day=6,
        period_length=5,
        cycle_length=28,
        today=TODAY,
    )
    assert context == "phase_transition"


def test_pick_context_greeting_when_checked_in_today_and_nothing_special():
    context = pick_context(
        streak_count=2,
        last_checkin=TODAY,
        cycle_day=15,
        period_length=5,
        cycle_length=28,
        today=TODAY,
    )
    assert context == "greeting"


def test_pick_context_log_prompt_default():
    context = pick_context(
        streak_count=0,
        last_checkin=None,
        cycle_day=15,
        period_length=5,
        cycle_length=28,
        today=TODAY,
    )
    assert context == "log_prompt"
