"""Business logic for the cycles table. Routers stay thin; this does the work."""

from datetime import date

from core.errors import ApiError
from core.supabase import get_supabase
from models.schemas import Cycle


def list_cycles(user_id: str) -> list[Cycle]:
    supabase = get_supabase()
    response = (
        supabase.table("cycles")
        .select("*")
        .eq("user_id", user_id)
        .order("start_date", desc=True)
        .execute()
    )
    return [Cycle(**row) for row in response.data]


def _get_open_cycle(supabase, user_id: str) -> dict | None:
    """The most recent cycle whose length hasn't been computed yet, if any."""
    response = (
        supabase.table("cycles")
        .select("*")
        .eq("user_id", user_id)
        .is_("length", "null")
        .order("start_date", desc=True)
        .limit(1)
        .execute()
    )
    rows = response.data
    return rows[0] if rows else None


def start_cycle(user_id: str, start_date: date) -> Cycle:
    supabase = get_supabase()
    open_cycle = _get_open_cycle(supabase, user_id)

    if open_cycle is not None:
        open_start = date.fromisoformat(open_cycle["start_date"])
        if start_date <= open_start:
            raise ApiError(
                status_code=400,
                code="period_start_before_open_cycle",
                message=(
                    f"New period start ({start_date.isoformat()}) must be after the "
                    f"currently open cycle's start ({open_start.isoformat()})."
                ),
            )

        length = (start_date - open_start).days
        supabase.table("cycles").update({"length": length}).eq("id", open_cycle["id"]).execute()

    response = (
        supabase.table("cycles")
        .insert({"user_id": user_id, "start_date": start_date.isoformat()})
        .execute()
    )
    return Cycle(**response.data[0])


def set_cycle_end_date(user_id: str, cycle_id: str, end_date: date) -> Cycle:
    supabase = get_supabase()
    response = (
        supabase.table("cycles")
        .select("*")
        .eq("id", cycle_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data
    if not rows:
        raise ApiError(status_code=404, code="cycle_not_found", message="No cycle with that id.")

    start_date = date.fromisoformat(rows[0]["start_date"])
    if end_date < start_date:
        raise ApiError(
            status_code=400,
            code="end_date_before_start_date",
            message=(
                f"end_date ({end_date.isoformat()}) cannot be before "
                f"start_date ({start_date.isoformat()})."
            ),
        )

    response = (
        supabase.table("cycles")
        .update({"end_date": end_date.isoformat()})
        .eq("id", cycle_id)
        .execute()
    )
    return Cycle(**response.data[0])
