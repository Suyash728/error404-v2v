from datetime import date, timedelta

import pytest

from models.schemas import Cycle, Profile
from services.prediction import predict

USER_ID = "00000000-0000-0000-0000-000000000001"


def make_cycle(start_date: date) -> Cycle:
    return Cycle(id=USER_ID, user_id=USER_ID, start_date=start_date)


def make_profile(avg_cycle_len=28, avg_period_len=5, last_period_start=None) -> Profile:
    return Profile(
        id=USER_ID,
        created_at="2024-01-01T00:00:00Z",
        avg_cycle_len=avg_cycle_len,
        avg_period_len=avg_period_len,
        last_period_start=last_period_start,
    )


def cycles_from_starts(starts: list[date]) -> list[Cycle]:
    return [make_cycle(start) for start in starts]


def test_regular_28_day_cycles_predict_high_confidence():
    # Six perfectly regular 28-day cycles, most recent starting 10 days ago.
    latest_start = date(2026, 6, 30)
    starts = [latest_start - timedelta(days=28 * n) for n in range(6, -1, -1)]
    # Day 7: past the 5-day period, before the fertile window (day 10-15).
    today = latest_start + timedelta(days=6)

    result = predict(cycles_from_starts(starts), make_profile(), today=today)

    assert result.cycle_length == 28
    assert result.confidence == "high"
    assert result.cycle_day == 7
    assert result.next_period_start == latest_start + timedelta(days=28)
    assert result.current_phase == "follicular"


def test_irregular_cycles_predict_low_confidence():
    # Lengths swing widely between starts: +21, +35, +24, +40 days.
    starts = [
        date(2026, 1, 1),
        date(2026, 1, 22),
        date(2026, 2, 26),
        date(2026, 3, 22),
        date(2026, 5, 1),
    ]
    today = starts[-1] + timedelta(days=5)

    result = predict(cycles_from_starts(starts), make_profile(), today=today)

    assert result.confidence == "low"


def test_brand_new_user_uses_profile_averages():
    # No cycles logged at all yet — only onboarding data on the profile.
    profile = make_profile(avg_cycle_len=30, avg_period_len=6, last_period_start=date(2026, 6, 20))
    today = date(2026, 6, 25)

    result = predict([], profile, today=today)

    assert result.cycle_length == 30
    assert result.confidence == "low"
    assert result.cycle_day == 6
    assert result.current_phase == "menstrual"
    assert result.next_period_start == date(2026, 6, 20) + timedelta(days=30)


def test_currently_on_period_is_menstrual_phase():
    start = date(2026, 6, 1)
    today = start + timedelta(days=2)  # cycle day 3, within avg_period_len=5

    result = predict(cycles_from_starts([start]), make_profile(avg_period_len=5), today=today)

    assert result.cycle_day == 3
    assert result.current_phase == "menstrual"


def test_single_cycle_falls_back_to_profile_average_length():
    # Exactly one logged cycle: not enough to compute a gap, so cycle_length
    # comes from the profile, but the anchor date is still the real cycle.
    start = date(2026, 5, 1)
    today = start + timedelta(days=20)
    profile = make_profile(avg_cycle_len=27, avg_period_len=4)

    result = predict(cycles_from_starts([start]), profile, today=today)

    assert result.cycle_length == 27
    assert result.confidence == "low"
    assert result.cycle_day == 21
    assert result.next_period_start == start + timedelta(days=27)


def test_raises_without_any_cycles_or_last_period_start():
    with pytest.raises(ValueError):
        predict([], make_profile(last_period_start=None))


def test_fertile_window_is_four_days_before_to_one_day_after_ovulation():
    start = date(2026, 6, 1)
    today = start + timedelta(days=1)
    # 28-day cycle_length -> ovulation on cycle day 14 -> date = start + 13 days.
    result = predict(cycles_from_starts([start]), make_profile(avg_cycle_len=28), today=today)

    ovulation_date = start + timedelta(days=13)
    assert result.fertile_window.start == ovulation_date - timedelta(days=4)
    assert result.fertile_window.end == ovulation_date + timedelta(days=1)
