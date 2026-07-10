"""Phase-based fitness/nutrition content, plus an optional Fit-derived
adaptive line on top of it. The content itself is curated, not computed —
it lives in data/phase_content.json; this module just resolves which
phase's content to serve and applies the (currently very small) Fit-aware
hook described in CC-12.
"""

import json
from pathlib import Path
from typing import Optional

from models.schemas import CyclePhaseName

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "phase_content.json"

DISCLAIMER = (
    "Cycle-phase fitness and nutrition guidance draws on emerging, still-developing research — "
    "it's a helpful starting point, not a strict prescription. Listen to your body first."
)

# Below-average sleep is the clearest, most directly actionable Fit signal
# for "should today's planned intensity change" — kept to a single simple
# threshold rather than a full recovery model, per CC-12's "hook" scope.
LOW_SLEEP_THRESHOLD_MIN = 360  # 6 hours
LOW_ACTIVITY_STEPS_THRESHOLD = 2000
LOW_ACTIVITY_ACTIVE_MIN_THRESHOLD = 15


def _load_content() -> dict:
    with DATA_PATH.open() as f:
        return json.load(f)


_CONTENT = _load_content()


def get_phase_content(phase: CyclePhaseName) -> dict:
    return _CONTENT[phase]


def adaptive_line(
    *,
    sleep_min: Optional[int] = None,
    steps: Optional[int] = None,
    active_min: Optional[int] = None,
) -> Optional[str]:
    """At most one Fit-derived line, in priority order — low sleep first,
    since that most directly affects whether today's planned workout
    intensity still makes sense. Returns None when there's no signal (no
    data provided, or nothing notable in what was)."""
    if sleep_min is not None and sleep_min < LOW_SLEEP_THRESHOLD_MIN:
        return (
            "You logged less sleep than usual last night — consider a lighter session today, "
            "even if it's normally a higher-intensity day."
        )
    if (
        steps is not None
        and steps < LOW_ACTIVITY_STEPS_THRESHOLD
        and active_min is not None
        and active_min < LOW_ACTIVITY_ACTIVE_MIN_THRESHOLD
    ):
        return "Today's been a low-movement day so far — even a short walk can help you feel more like yourself."
    return None
