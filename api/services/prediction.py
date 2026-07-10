"""Pure cycle-prediction math: no DB access, no I/O. Given cycle history and
a profile fallback, predicts the current phase, fertile window, and next
period start. Router wires this to GET /cycles/prediction; see
tests/test_prediction.py for the scenarios this is expected to handle.
"""

from datetime import date, timedelta
from statistics import pstdev
from typing import Optional

from models.schemas import ConfidenceLevel, Cycle, CyclePhaseName, FertileWindow, Prediction, Profile

# Ovulation happens ~14 days before the *next* period regardless of overall
# cycle length (the luteal phase is the fixed part of the cycle); the
# fertile window is the 4 days before ovulation through 1 day after it.
LUTEAL_PHASE_LENGTH_DAYS = 14
FERTILE_WINDOW_DAYS_BEFORE_OVULATION = 4
FERTILE_WINDOW_DAYS_AFTER_OVULATION = 1

# Heuristics, not clinical figures — good enough to rank confidence for a
# hackathon build without a real statistical model behind it.
MAX_LENGTHS_FOR_AVERAGE = 6
HIGH_CONFIDENCE_MAX_STDDEV_DAYS = 2
MEDIUM_CONFIDENCE_MAX_STDDEV_DAYS = 5


def _completed_cycle_lengths(cycles: list[Cycle]) -> list[int]:
    """Day gaps between consecutive logged period starts, oldest pair first."""
    starts = sorted(cycle.start_date for cycle in cycles)
    return [(later - earlier).days for earlier, later in zip(starts, starts[1:])]


def _weighted_average_length(lengths: list[int]) -> float:
    """Weighted moving average of the most recent lengths, weighting more
    recent cycles higher (weights 1..n, oldest to newest in the window)."""
    recent = lengths[-MAX_LENGTHS_FOR_AVERAGE:]
    weights = range(1, len(recent) + 1)
    return sum(length * weight for length, weight in zip(recent, weights)) / sum(weights)


def _confidence_for(lengths: list[int]) -> ConfidenceLevel:
    if len(lengths) < 2:
        return "low"
    spread = pstdev(lengths[-MAX_LENGTHS_FOR_AVERAGE:])
    if spread <= HIGH_CONFIDENCE_MAX_STDDEV_DAYS:
        return "high"
    if spread <= MEDIUM_CONFIDENCE_MAX_STDDEV_DAYS:
        return "medium"
    return "low"


def _phase_for_day(cycle_day: int, period_length: int, ovulation_day: int) -> CyclePhaseName:
    if cycle_day <= period_length:
        return "menstrual"
    if cycle_day < ovulation_day - FERTILE_WINDOW_DAYS_BEFORE_OVULATION:
        return "follicular"
    if cycle_day <= ovulation_day + FERTILE_WINDOW_DAYS_AFTER_OVULATION:
        return "ovulatory"
    # Also covers "period is late": once cycle_day runs past the predicted
    # cycle_length, we stay in luteal rather than guessing a new cycle
    # started without an actual logged period.
    return "luteal"


def predict(cycles: list[Cycle], profile: Profile, today: Optional[date] = None) -> Prediction:
    """Predict the current phase, fertile window, and next period start.

    Needs at least 2 logged cycles to compute a data-driven cycle length
    (one completed gap between period starts). Below that — 0 or 1 cycles —
    falls back to the profile's avg_cycle_len, with confidence="low".

    `today` is injectable for deterministic tests; defaults to date.today().
    Raises ValueError if there's no cycle history and no
    profile.last_period_start to anchor the prediction on.
    """
    today = today or date.today()
    period_length = profile.avg_period_len

    lengths = _completed_cycle_lengths(cycles) if len(cycles) >= 2 else []
    if lengths:
        cycle_length = round(_weighted_average_length(lengths))
        confidence: ConfidenceLevel = _confidence_for(lengths)
    else:
        cycle_length = profile.avg_cycle_len
        confidence = "low"

    if cycles:
        anchor = max(cycle.start_date for cycle in cycles)
    elif profile.last_period_start is not None:
        anchor = profile.last_period_start
    else:
        raise ValueError(
            "Cannot predict without logged cycles or a profile.last_period_start to anchor on."
        )

    cycle_day = (today - anchor).days + 1
    ovulation_day = cycle_length - LUTEAL_PHASE_LENGTH_DAYS

    def date_for_cycle_day(day: int) -> date:
        return anchor + timedelta(days=day - 1)

    return Prediction(
        next_period_start=anchor + timedelta(days=cycle_length),
        fertile_window=FertileWindow(
            start=date_for_cycle_day(ovulation_day - FERTILE_WINDOW_DAYS_BEFORE_OVULATION),
            end=date_for_cycle_day(ovulation_day + FERTILE_WINDOW_DAYS_AFTER_OVULATION),
        ),
        current_phase=_phase_for_day(cycle_day, period_length, ovulation_day),
        cycle_day=cycle_day,
        cycle_length=cycle_length,
        confidence=confidence,
    )
