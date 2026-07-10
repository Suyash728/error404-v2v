from datetime import date, timedelta

from constants import Symptom
from models.schemas import Cycle, DailyLog, Profile
from services.rule_engine import (
    NEEDS_MORE_DATA,
    evaluate_all,
    evaluate_anemia_pattern,
    evaluate_irregularity,
    evaluate_pcos_pattern,
    evaluate_pmdd_pattern,
)

USER_ID = "00000000-0000-0000-0000-000000000001"


def make_cycle(start_date: date, length: int | None = None) -> Cycle:
    return Cycle(id=USER_ID, user_id=USER_ID, start_date=start_date, length=length)


def make_log(log_date: date, **kwargs) -> DailyLog:
    return DailyLog(id=USER_ID, user_id=USER_ID, log_date=log_date, **kwargs)


def logs_over_range(
    start: date,
    days: int,
    *,
    flow_by_offset: dict[int, int] | None = None,
    symptom_offsets: dict[Symptom, set[int]] | None = None,
    mood_by_offset: dict[int, int] | None = None,
) -> list[DailyLog]:
    flow_by_offset = flow_by_offset or {}
    symptom_offsets = symptom_offsets or {}
    mood_by_offset = mood_by_offset or {}
    logs = []
    for offset in range(days):
        log_date = start + timedelta(days=offset)
        symptoms = [symptom for symptom, offsets in symptom_offsets.items() if offset in offsets]
        logs.append(
            make_log(
                log_date,
                flow=flow_by_offset.get(offset),
                symptoms=symptoms,
                mood=mood_by_offset.get(offset),
            )
        )
    return logs


# --- IRREGULARITY -----------------------------------------------------------


def test_irregularity_needs_more_data_with_fewer_than_3_cycles():
    cycles = [make_cycle(date(2026, 1, 1), length=28), make_cycle(date(2026, 1, 29), length=27)]
    assert evaluate_irregularity(cycles) == NEEDS_MORE_DATA


def test_irregularity_does_not_fire_for_regular_cycles():
    cycles = [
        make_cycle(date(2026, 1, 1), length=28),
        make_cycle(date(2026, 1, 29), length=27),
        make_cycle(date(2026, 2, 25), length=29),
    ]
    assert evaluate_irregularity(cycles) is None


def test_irregularity_fires_medium_for_isolated_outlier_without_high_stddev():
    # 40d cycle is an outlier (>35d), but the other two are identical enough
    # that population stddev stays under the 8d threshold.
    cycles = [
        make_cycle(date(2026, 1, 1), length=28),
        make_cycle(date(2026, 1, 29), length=28),
        make_cycle(date(2026, 2, 26), length=40),
    ]
    result = evaluate_irregularity(cycles)
    assert result is not None
    assert result.flag_type == "IRREGULARITY"
    assert result.severity == "medium"
    assert any("40d" in rule for rule in result.fired_rules)


def test_irregularity_fires_high_when_stddev_and_outlier_both_trip():
    cycles = [
        make_cycle(date(2026, 1, 1), length=20),
        make_cycle(date(2026, 1, 21), length=20),
        make_cycle(date(2026, 2, 10), length=50),
    ]
    result = evaluate_irregularity(cycles)
    assert result is not None
    assert result.severity == "high"
    assert len(result.fired_rules) >= 2


# --- PCOS_PATTERN -------------------------------------------------------------

IRREGULAR_CYCLES = [
    make_cycle(date(2026, 1, 1), length=28),
    make_cycle(date(2026, 1, 29), length=28),
    make_cycle(date(2026, 2, 26), length=40),
]
REGULAR_CYCLES = [
    make_cycle(date(2026, 1, 1), length=28),
    make_cycle(date(2026, 1, 29), length=27),
    make_cycle(date(2026, 2, 25), length=29),
]


def test_pcos_needs_more_data_when_irregularity_needs_more_data():
    cycles = [make_cycle(date(2026, 1, 1), length=28)]
    logs = logs_over_range(date(2026, 1, 1), 20)
    assert evaluate_pcos_pattern(cycles, logs) == NEEDS_MORE_DATA


def test_pcos_needs_more_data_when_too_few_logs():
    logs = logs_over_range(date(2026, 1, 1), 5, symptom_offsets={Symptom.ACNE: {0, 1, 2}})
    assert evaluate_pcos_pattern(IRREGULAR_CYCLES, logs) == NEEDS_MORE_DATA


def test_pcos_does_not_fire_when_cycles_are_not_irregular():
    # Even with every symptom criterion satisfied, no irregularity -> no PCOS flag.
    logs = logs_over_range(
        date(2026, 1, 1),
        20,
        symptom_offsets={
            Symptom.ACNE: set(range(10)),
            Symptom.EXCESS_HAIR_GROWTH: {0, 1, 2},
            Symptom.WEIGHT_GAIN: {0, 1, 2},
        },
    )
    assert evaluate_pcos_pattern(REGULAR_CYCLES, logs) is None


def test_pcos_does_not_fire_with_only_one_matching_criterion():
    # Irregular cycles + acne above threshold, but nothing else matches.
    logs = logs_over_range(date(2026, 1, 1), 20, symptom_offsets={Symptom.ACNE: set(range(7))})
    assert evaluate_pcos_pattern(IRREGULAR_CYCLES, logs) is None


def test_pcos_fires_with_two_matching_criteria():
    # Acne on 7/20 days (35% > 30%) + excess hair growth on 3 days (>= 3).
    logs = logs_over_range(
        date(2026, 1, 1),
        20,
        symptom_offsets={Symptom.ACNE: set(range(7)), Symptom.EXCESS_HAIR_GROWTH: {0, 1, 2}},
    )
    result = evaluate_pcos_pattern(IRREGULAR_CYCLES, logs)
    assert result is not None
    assert result.flag_type == "PCOS_PATTERN"
    assert len(result.fired_rules) >= 3  # irregularity note + 2 matched criteria


# --- ANEMIA_PATTERN -----------------------------------------------------------

ANEMIA_CYCLES = [make_cycle(date(2026, 1, 1), length=10), make_cycle(date(2026, 1, 11), length=10)]


def test_anemia_needs_more_data_with_fewer_than_2_cycles():
    cycles = [make_cycle(date(2026, 1, 1), length=10)]
    logs = logs_over_range(date(2026, 1, 1), 20, flow_by_offset={i: 3 for i in range(4)})
    assert evaluate_anemia_pattern(cycles, logs) == NEEDS_MORE_DATA


def test_anemia_needs_more_data_with_too_few_logs():
    # Only the 8 heavy-flow days logged, no padding to reach the 14-day floor.
    logs = logs_over_range(date(2026, 1, 1), 4, flow_by_offset={i: 3 for i in range(4)})
    logs += logs_over_range(date(2026, 1, 11), 4, flow_by_offset={i: 4 for i in range(4)})
    assert evaluate_anemia_pattern(ANEMIA_CYCLES, logs) == NEEDS_MORE_DATA


def test_anemia_does_not_fire_without_two_consecutive_heavy_cycles():
    # Cycle 1 is heavy (4 days flow>=3); cycle 2 only has 3 such days.
    logs = logs_over_range(
        date(2026, 1, 1),
        20,
        flow_by_offset={0: 3, 1: 3, 2: 3, 3: 3, 10: 4, 11: 4, 12: 4},
    )
    assert evaluate_anemia_pattern(ANEMIA_CYCLES, logs) is None


def test_anemia_does_not_fire_without_fatigue_or_dizziness():
    logs = logs_over_range(
        date(2026, 1, 1),
        20,
        flow_by_offset={0: 3, 1: 3, 2: 3, 3: 3, 10: 4, 11: 4, 12: 4, 13: 4},
    )
    assert evaluate_anemia_pattern(ANEMIA_CYCLES, logs) is None


def test_anemia_fires_with_consecutive_heavy_cycles_and_fatigue():
    logs = logs_over_range(
        date(2026, 1, 1),
        20,
        flow_by_offset={0: 3, 1: 3, 2: 3, 3: 3, 10: 4, 11: 4, 12: 4, 13: 4},
        symptom_offsets={Symptom.FATIGUE: set(range(4, 13))},  # 9/20 = 45% > 40%
    )
    result = evaluate_anemia_pattern(ANEMIA_CYCLES, logs)
    assert result is not None
    assert result.flag_type == "ANEMIA_PATTERN"
    assert any("fatigue" in rule for rule in result.fired_rules)


# --- PMDD_PATTERN -------------------------------------------------------------


def test_pmdd_needs_more_data_with_fewer_than_2_cycles_covered():
    cycle_a = make_cycle(date(2026, 1, 1))
    cycle_b = make_cycle(date(2026, 2, 1))
    # Only cycle_a has mood data in both the pre-period and baseline windows.
    logs = [make_log(date(2026, 1, 1) - timedelta(days=d), mood=2) for d in range(1, 8)]
    logs += [make_log(date(2026, 1, 1) + timedelta(days=d), mood=4) for d in range(4, 14)]
    assert evaluate_pmdd_pattern([cycle_a, cycle_b], logs) == NEEDS_MORE_DATA


def _pmdd_logs(cycle_starts: list[date], pre_mood: int, baseline_mood: int) -> list[DailyLog]:
    logs = []
    for start in cycle_starts:
        for d in range(1, 8):
            logs.append(make_log(start - timedelta(days=d), mood=pre_mood))
        for d in range(4, 14):
            logs.append(make_log(start + timedelta(days=d), mood=baseline_mood))
    return logs


def test_pmdd_does_not_fire_below_the_mood_drop_threshold():
    cycle_starts = [date(2026, 1, 1), date(2026, 2, 1)]
    cycles = [make_cycle(s) for s in cycle_starts]
    logs = _pmdd_logs(cycle_starts, pre_mood=3, baseline_mood=4)  # drop of 1 < 1.5
    assert evaluate_pmdd_pattern(cycles, logs) is None


def test_pmdd_fires_at_or_above_the_mood_drop_threshold():
    cycle_starts = [date(2026, 1, 1), date(2026, 2, 1)]
    cycles = [make_cycle(s) for s in cycle_starts]
    logs = _pmdd_logs(cycle_starts, pre_mood=1, baseline_mood=5)  # drop of 4 >= 1.5
    result = evaluate_pmdd_pattern(cycles, logs)
    assert result is not None
    assert result.flag_type == "PMDD_PATTERN"
    assert "2 cycles" in result.fired_rules[0]


# --- evaluate_all --------------------------------------------------------------


def test_evaluate_all_returns_only_fired_flags():
    # IRREGULARITY fires; PCOS/ANEMIA/PMDD all need more data or don't fire
    # given this minimal log set.
    logs = logs_over_range(date(2026, 1, 1), 5)
    profile = Profile(id=USER_ID, created_at="2024-01-01T00:00:00Z")

    flags = evaluate_all(IRREGULAR_CYCLES, logs, profile)

    assert [flag.flag_type for flag in flags] == ["IRREGULARITY"]
