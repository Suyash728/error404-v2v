"""Business logic for the risk_flags table. Routers stay thin; this does the work."""

from core.supabase import get_supabase
from models.schemas import RiskFlag, RiskFlagCreate


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
