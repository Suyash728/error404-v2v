from datetime import date, timedelta

import pytest

from services.copy_engine import _MATRIX, CONTEXTS, GENTLE_GUILT_CONTEXTS, get_message

PHASES = ("menstrual", "follicular", "ovulatory", "luteal")

WEIGHT_APPEARANCE_TERMS = [
    "weight",
    "pounds",
    " lbs",
    "skinny",
    "overweight",
    "underweight",
    "figure",
    "slim",
    "diet",
    "calorie",
    "appearance",
    "pretty",
    "gorgeous",
    "attractive",
    "body image",
]

GUILT_CODED_PHRASES = [
    "you forgot",
    "don't forget",
    "disappointed",
    "you failed",
    "shame",
    "should have",
    "let yourself down",
    "let down",
]


def all_lines():
    for phase in PHASES:
        for context in CONTEXTS:
            for line in _MATRIX[phase][context]:
                yield phase, context, line


# --- content-discipline checks over the whole seed matrix --------------------


def test_matrix_has_every_phase_and_context_covered():
    for phase in PHASES:
        for context in CONTEXTS:
            assert _MATRIX[phase][context], f"no lines for {phase}/{context}"


def test_no_line_references_weight_or_appearance():
    for phase, context, line in all_lines():
        lowered = line["text"].lower()
        for term in WEIGHT_APPEARANCE_TERMS:
            assert term not in lowered, f"{phase}/{context} references {term!r}: {line['text']!r}"


def test_menstrual_missed_lines_are_all_tagged_soft():
    for context in ("missed_1", "missed_3plus"):
        for line in _MATRIX["menstrual"][context]:
            assert line.get("soft") is True, f"menstrual {context} line not soft: {line['text']!r}"


def test_gentle_guilt_phrasing_confined_to_missed_contexts():
    non_missed_contexts = CONTEXTS - GENTLE_GUILT_CONTEXTS
    for phase in PHASES:
        for context in non_missed_contexts:
            for line in _MATRIX[phase][context]:
                lowered = line["text"].lower()
                for phrase in GUILT_CODED_PHRASES:
                    assert phrase not in lowered, f"{phase}/{context} has guilt phrasing: {line['text']!r}"


# --- get_message behavior -----------------------------------------------------


def test_unknown_context_raises():
    with pytest.raises(ValueError):
        get_message("not_a_context", "menstrual", "none", "track")


def test_unknown_phase_raises():
    with pytest.raises(ValueError):
        get_message("greeting", "not_a_phase", "none", "track")


def test_same_day_is_deterministic():
    today = date(2026, 7, 11)
    first = get_message("greeting", "follicular", "building", "track", today=today)
    second = get_message("greeting", "follicular", "building", "track", today=today)
    assert first == second


def test_selection_varies_across_days():
    messages = {
        get_message("greeting", "follicular", "building", "track", today=date(2026, 1, 1) + timedelta(days=i))
        for i in range(30)
    }
    assert len(messages) > 1


def test_menstrual_missed_only_returns_soft_lines():
    soft_texts = {line["text"] for line in _MATRIX["menstrual"]["missed_1"] if line.get("soft")}
    for i in range(30):
        today = date(2026, 1, 1) + timedelta(days=i)
        message = get_message("missed_1", "menstrual", "none", "track", today=today)
        assert message in soft_texts


def test_ttc_specific_line_only_surfaces_for_ttc_intention_mode():
    ttc_only_text = next(
        line["text"]
        for line in _MATRIX["ovulatory"]["phase_transition"]
        if line.get("intention_modes") == ["ttc"]
    )

    ttc_results = {
        get_message("phase_transition", "ovulatory", "none", "ttc", today=date(2026, 1, 1) + timedelta(days=i))
        for i in range(30)
    }
    assert ttc_only_text in ttc_results

    track_results = {
        get_message("phase_transition", "ovulatory", "none", "track", today=date(2026, 1, 1) + timedelta(days=i))
        for i in range(30)
    }
    assert ttc_only_text not in track_results


def test_milestone_specific_line_only_surfaces_for_milestone_streak_state():
    milestone_only_text = next(
        line["text"]
        for line in _MATRIX["follicular"]["streak_milestone"]
        if line.get("streak_states") == ["milestone"]
    )

    milestone_results = {
        get_message(
            "streak_milestone", "follicular", "milestone", "track", today=date(2026, 1, 1) + timedelta(days=i)
        )
        for i in range(30)
    }
    assert milestone_only_text in milestone_results

    building_results = {
        get_message(
            "streak_milestone", "follicular", "building", "track", today=date(2026, 1, 1) + timedelta(days=i)
        )
        for i in range(30)
    }
    assert milestone_only_text not in building_results
