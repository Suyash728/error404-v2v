"""Pure risk-flag evaluators: no DB access, no I/O. Given a user's completed
cycles, recent daily logs, and profile, each evaluator decides whether a
specific pattern (irregularity, PCOS, anemia, PMDD) is evident in the data.

Every evaluator returns one of three things:
  - a RiskFlagCreate, if the pattern fired
  - None, if it was evaluated but did not fire
  - NEEDS_MORE_DATA, if there isn't enough history to evaluate it at all

Router (routers/risk.py) wires evaluate_all() to GET /risk/evaluate,
persisting whichever flags fired. See tests/test_rule_engine.py for the
scenarios each evaluator is expected to handle.
"""

from datetime import date, timedelta
from statistics import mean, pstdev
from typing import Literal, Union

from constants import Symptom
from models.schemas import Cycle, DailyLog, Profile, RiskFlagCreate

NEEDS_MORE_DATA = "NEEDS_MORE_DATA"
EvaluatorResult = Union[RiskFlagCreate, None, Literal["NEEDS_MORE_DATA"]]

IRREGULARITY = "IRREGULARITY"
PCOS_PATTERN = "PCOS_PATTERN"
ANEMIA_PATTERN = "ANEMIA_PATTERN"
PMDD_PATTERN = "PMDD_PATTERN"

# Minimum logged days before a symptom *rate* (vs. a raw day count) is
# treated as meaningful rather than noise — an arbitrary but documented
# heuristic, not a clinical figure.
MIN_LOGGED_DAYS_FOR_SYMPTOM_RATE = 14

IRREGULARITY_STDDEV_THRESHOLD_DAYS = 8
IRREGULARITY_SHORT_CYCLE_DAYS = 21
IRREGULARITY_LONG_CYCLE_DAYS = 35
IRREGULARITY_MIN_CYCLES = 3

PCOS_MIN_MATCHING_CRITERIA = 2
PCOS_ACNE_RATE_THRESHOLD = 0.30
PCOS_SYMPTOM_DAY_THRESHOLD = 3
PCOS_LONG_CYCLE_MIN_COUNT = 2

ANEMIA_MIN_CYCLES = 2
ANEMIA_HEAVY_FLOW_MIN_VALUE = 3
ANEMIA_HEAVY_FLOW_MIN_DAYS = 4
ANEMIA_FATIGUE_RATE_THRESHOLD = 0.40
ANEMIA_DIZZINESS_MIN_DAYS = 3

PMDD_MIN_CYCLES = 2
PMDD_MOOD_DROP_THRESHOLD = 1.5


def _completed_cycles(cycles: list[Cycle]) -> list[Cycle]:
    return sorted((c for c in cycles if c.length is not None), key=lambda c: c.start_date)


def _symptom_day_count(daily_logs: list[DailyLog], symptom: Symptom) -> int:
    return sum(1 for log in daily_logs if symptom in log.symptoms)


def _symptom_rate(daily_logs: list[DailyLog], symptom: Symptom) -> float:
    if not daily_logs:
        return 0.0
    return _symptom_day_count(daily_logs, symptom) / len(daily_logs)


def evaluate_irregularity(cycles: list[Cycle]) -> EvaluatorResult:
    lengths = [c.length for c in _completed_cycles(cycles)]
    if len(lengths) < IRREGULARITY_MIN_CYCLES:
        return NEEDS_MORE_DATA

    spread = pstdev(lengths)
    stddev_high = spread > IRREGULARITY_STDDEV_THRESHOLD_DAYS
    outliers = [
        length
        for length in lengths
        if length < IRREGULARITY_SHORT_CYCLE_DAYS or length > IRREGULARITY_LONG_CYCLE_DAYS
    ]

    if not stddev_high and not outliers:
        return None

    fired_rules = []
    if stddev_high:
        fired_rules.append(
            f"cycle length stddev {spread:.1f}d exceeds {IRREGULARITY_STDDEV_THRESHOLD_DAYS}d "
            f"(n={len(lengths)} cycles)"
        )
    for length in outliers:
        fired_rules.append(
            f"cycle length {length}d outside normal "
            f"{IRREGULARITY_SHORT_CYCLE_DAYS}-{IRREGULARITY_LONG_CYCLE_DAYS}d range"
        )

    severity = "high" if stddev_high and outliers else "medium"
    return RiskFlagCreate(flag_type=IRREGULARITY, severity=severity, fired_rules=fired_rules)


def evaluate_pcos_pattern(cycles: list[Cycle], daily_logs: list[DailyLog]) -> EvaluatorResult:
    irregularity = evaluate_irregularity(cycles)
    if irregularity == NEEDS_MORE_DATA:
        return NEEDS_MORE_DATA
    if irregularity is None:
        return None

    if len(daily_logs) < MIN_LOGGED_DAYS_FOR_SYMPTOM_RATE:
        return NEEDS_MORE_DATA

    acne_rate = _symptom_rate(daily_logs, Symptom.ACNE)
    hair_growth_days = _symptom_day_count(daily_logs, Symptom.EXCESS_HAIR_GROWTH)
    weight_gain_days = _symptom_day_count(daily_logs, Symptom.WEIGHT_GAIN)
    long_cycle_count = sum(1 for c in _completed_cycles(cycles) if c.length > IRREGULARITY_LONG_CYCLE_DAYS)

    matched_criteria = []
    if acne_rate > PCOS_ACNE_RATE_THRESHOLD:
        matched_criteria.append(f"acne logged on {acne_rate:.0%} of days (> {PCOS_ACNE_RATE_THRESHOLD:.0%})")
    if hair_growth_days >= PCOS_SYMPTOM_DAY_THRESHOLD:
        matched_criteria.append(
            f"excess hair growth logged on {hair_growth_days} days (>= {PCOS_SYMPTOM_DAY_THRESHOLD})"
        )
    if weight_gain_days >= PCOS_SYMPTOM_DAY_THRESHOLD:
        matched_criteria.append(
            f"weight gain logged on {weight_gain_days} days (>= {PCOS_SYMPTOM_DAY_THRESHOLD})"
        )
    if long_cycle_count >= PCOS_LONG_CYCLE_MIN_COUNT:
        matched_criteria.append(
            f"{long_cycle_count} cycles longer than {IRREGULARITY_LONG_CYCLE_DAYS}d "
            f"(>= {PCOS_LONG_CYCLE_MIN_COUNT})"
        )

    if len(matched_criteria) < PCOS_MIN_MATCHING_CRITERIA:
        return None

    fired_rules = ["irregularity criteria met"] + matched_criteria
    return RiskFlagCreate(flag_type=PCOS_PATTERN, severity="medium", fired_rules=fired_rules)


def _is_heavy_flow_cycle(cycle: Cycle, daily_logs: list[DailyLog]) -> bool:
    cycle_end = cycle.start_date + timedelta(days=cycle.length)
    heavy_days = sum(
        1
        for log in daily_logs
        if cycle.start_date <= log.log_date < cycle_end
        and log.flow is not None
        and log.flow >= ANEMIA_HEAVY_FLOW_MIN_VALUE
    )
    return heavy_days >= ANEMIA_HEAVY_FLOW_MIN_DAYS


def evaluate_anemia_pattern(cycles: list[Cycle], daily_logs: list[DailyLog]) -> EvaluatorResult:
    completed = _completed_cycles(cycles)
    if len(completed) < ANEMIA_MIN_CYCLES or len(daily_logs) < MIN_LOGGED_DAYS_FOR_SYMPTOM_RATE:
        return NEEDS_MORE_DATA

    heavy_flags = [_is_heavy_flow_cycle(c, daily_logs) for c in completed]
    has_consecutive_heavy = any(
        heavy_flags[i] and heavy_flags[i + 1] for i in range(len(heavy_flags) - 1)
    )
    if not has_consecutive_heavy:
        return None

    fatigue_rate = _symptom_rate(daily_logs, Symptom.FATIGUE)
    dizziness_days = _symptom_day_count(daily_logs, Symptom.DIZZINESS)

    if fatigue_rate <= ANEMIA_FATIGUE_RATE_THRESHOLD and dizziness_days < ANEMIA_DIZZINESS_MIN_DAYS:
        return None

    fired_rules = [
        f"2+ consecutive cycles with flow >= {ANEMIA_HEAVY_FLOW_MIN_VALUE} on "
        f">= {ANEMIA_HEAVY_FLOW_MIN_DAYS} days"
    ]
    if fatigue_rate > ANEMIA_FATIGUE_RATE_THRESHOLD:
        fired_rules.append(
            f"fatigue logged on {fatigue_rate:.0%} of days (> {ANEMIA_FATIGUE_RATE_THRESHOLD:.0%})"
        )
    if dizziness_days >= ANEMIA_DIZZINESS_MIN_DAYS:
        fired_rules.append(f"dizziness logged on {dizziness_days} days (>= {ANEMIA_DIZZINESS_MIN_DAYS})")

    return RiskFlagCreate(flag_type=ANEMIA_PATTERN, severity="medium", fired_rules=fired_rules)


def _dates_in_range(start: date, end: date) -> list[date]:
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def evaluate_pmdd_pattern(cycles: list[Cycle], daily_logs: list[DailyLog]) -> EvaluatorResult:
    mood_by_date = {log.log_date: log.mood for log in daily_logs if log.mood is not None}

    pre_period_moods: list[int] = []
    baseline_moods: list[int] = []
    cycles_with_both_windows = 0

    for cycle in cycles:
        pre_window = _dates_in_range(cycle.start_date - timedelta(days=7), cycle.start_date - timedelta(days=1))
        baseline_window = _dates_in_range(
            cycle.start_date + timedelta(days=4), cycle.start_date + timedelta(days=13)
        )
        pre = [mood_by_date[d] for d in pre_window if d in mood_by_date]
        baseline = [mood_by_date[d] for d in baseline_window if d in mood_by_date]

        if pre and baseline:
            cycles_with_both_windows += 1
            pre_period_moods.extend(pre)
            baseline_moods.extend(baseline)

    if cycles_with_both_windows < PMDD_MIN_CYCLES:
        return NEEDS_MORE_DATA

    pre_mean = mean(pre_period_moods)
    baseline_mean = mean(baseline_moods)
    drop = baseline_mean - pre_mean

    if drop < PMDD_MOOD_DROP_THRESHOLD:
        return None

    fired_rules = [
        f"mean mood days -7..-1 ({pre_mean:.2f}) is {drop:.2f} points below mean mood days "
        f"5..14 ({baseline_mean:.2f}), across {cycles_with_both_windows} cycles"
    ]
    return RiskFlagCreate(flag_type=PMDD_PATTERN, severity="medium", fired_rules=fired_rules)


def evaluate_all(cycles: list[Cycle], daily_logs: list[DailyLog], profile: Profile) -> list[RiskFlagCreate]:
    """Runs every evaluator and returns only the ones that actually fired.
    `profile` isn't consulted by any of the four rules today (none of them
    key off profile fields) but is accepted here per the rule engine's
    input contract, for evaluators that may need it later.
    """
    del profile  # not used by any current evaluator; see docstring.
    results = [
        evaluate_irregularity(cycles),
        evaluate_pcos_pattern(cycles, daily_logs),
        evaluate_anemia_pattern(cycles, daily_logs),
        evaluate_pmdd_pattern(cycles, daily_logs),
    ]
    return [r for r in results if isinstance(r, RiskFlagCreate)]
