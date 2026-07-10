"""Business logic for the risk_flags table. Routers stay thin; this does the work."""

from typing import Optional

from core.supabase import get_supabase
from models.schemas import Cycle, DailyLog, Profile, RiskFlag, RiskFlagCreate
from services.risk_explanation import generate_explanation
from services.rule_engine import evaluate_all


def create_risk_flags(user_id: str, flags: list[RiskFlagCreate]) -> list[RiskFlag]:
    # risk_flags is an append-only audit log (see 001_init.sql) — every
    # evaluation run inserts fresh rows rather than deduping against past
    # flags of the same flag_type.
    if not flags:
        return []

    rows = [
        {
            "user_id": user_id,
            "flag_type": flag.flag_type,
            "severity": flag.severity,
            "fired_rules": flag.fired_rules,
            "explanation": flag.explanation,
            "llm_provider": flag.llm_provider,
        }
        for flag in flags
    ]
    response = get_supabase().table("risk_flags").insert(rows).execute()
    return [RiskFlag(**row) for row in response.data]


def find_cached_explanation(
    user_id: str, flag_type: str, fired_rules: list[str]
) -> Optional[tuple[str, str]]:
    """A prior risk_flags row for this user with the same flag_type and the
    exact same fired_rules already has a generated explanation — reuse it
    instead of paying for a fresh LLM call for semantically identical
    content ("generate once, cache").
    """
    response = (
        get_supabase()
        .table("risk_flags")
        .select("fired_rules, explanation, llm_provider")
        .eq("user_id", user_id)
        .eq("flag_type", flag_type)
        .not_.is_("explanation", "null")
        .execute()
    )
    for row in response.data:
        if row["fired_rules"] == fired_rules:
            return row["explanation"], row["llm_provider"]
    return None


def evaluate_and_persist(
    user_id: str, cycles: list[Cycle], daily_logs: list[DailyLog], profile: Profile
) -> list[RiskFlag]:
    fired_flags = evaluate_all(cycles, daily_logs, profile)
    if not fired_flags:
        return []

    explained_flags = []
    for flag in fired_flags:
        cached = find_cached_explanation(user_id, flag.flag_type, flag.fired_rules)
        explanation, llm_provider = (
            cached if cached is not None else generate_explanation(flag.flag_type, flag.fired_rules)
        )
        explained_flags.append(
            flag.model_copy(update={"explanation": explanation, "llm_provider": llm_provider})
        )

    return create_risk_flags(user_id, explained_flags)
