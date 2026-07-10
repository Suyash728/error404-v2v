"""Sakhi's phase-aware copy engine: picks one warm, on-brand line per
(phase, context) from data/sakhi_copy.json, deterministically for a given
day so repeat calls on the same day return the identical message.

Rules baked in here, not left to content discipline alone:
  - gentle-guilt phrasing only ever applies to missed_1/missed_3plus —
    enforced structurally, since those are the only contexts whose JSON
    entries carry that tone at all (see data/sakhi_copy.json)
  - menstrual-phase nudges (missed_1/missed_3plus) are restricted to lines
    tagged "soft": true, never the punchier non-menstrual variants
  - "capped to one nudge/day" falls out of the caller invoking this once
    per day for a single context, combined with the date-seeded
    determinism below — a second call the same day returns the same line,
    not a fresh nudge
  - never reference weight/appearance: content discipline in the JSON,
    checked by tests/test_copy_engine.py
"""

import json
import random
from datetime import date
from pathlib import Path
from typing import Optional

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sakhi_copy.json"

CONTEXTS = {"greeting", "log_prompt", "missed_1", "missed_3plus", "streak_milestone", "phase_transition"}
GENTLE_GUILT_CONTEXTS = {"missed_1", "missed_3plus"}


def _load_matrix() -> dict:
    with DATA_PATH.open() as f:
        return json.load(f)


_MATRIX = _load_matrix()


def _matches(line: dict, key: str, value: str) -> bool:
    allowed = line.get(key)
    return not allowed or value in allowed


def get_message(
    context: str,
    phase: str,
    streak_state: str,
    intention_mode: str,
    *,
    today: Optional[date] = None,
) -> str:
    if context not in CONTEXTS:
        raise ValueError(f"unknown context: {context!r}")

    today = today or date.today()

    try:
        candidates = _MATRIX[phase][context]
    except KeyError as exc:
        raise ValueError(f"no copy for phase={phase!r} context={context!r}") from exc

    if context in GENTLE_GUILT_CONTEXTS and phase == "menstrual":
        soft_candidates = [line for line in candidates if line.get("soft")]
        if soft_candidates:
            candidates = soft_candidates

    filtered = [
        line
        for line in candidates
        if _matches(line, "intention_modes", intention_mode) and _matches(line, "streak_states", streak_state)
    ]
    if filtered:
        candidates = filtered

    seed = f"{today.isoformat()}:{phase}:{context}"
    chosen = random.Random(seed).choice(candidates)
    return chosen["text"]
