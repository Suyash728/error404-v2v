"""Business logic for the daily_logs table. Routers stay thin; this does the work."""

from datetime import date

from core.errors import ApiError
from core.supabase import get_supabase
from models.schemas import DailyLog, DailyLogCreate


def upsert_log(user_id: str, payload: DailyLogCreate) -> DailyLog:
    supabase = get_supabase()
    row = {
        "user_id": user_id,
        "log_date": payload.log_date.isoformat(),
        "flow": payload.flow,
        "symptoms": [symptom.value for symptom in payload.symptoms],
        "mood": payload.mood,
        "energy": payload.energy,
        "water_ml": payload.water_ml,
        "bbt": payload.bbt,
        "notes": payload.notes,
    }

    response = (
        supabase.table("daily_logs").upsert(row, on_conflict="user_id,log_date").execute()
    )
    return DailyLog(**response.data[0])


def list_logs(user_id: str, from_date: date | None, to_date: date | None) -> list[DailyLog]:
    if from_date is not None and to_date is not None and from_date > to_date:
        raise ApiError(
            status_code=400,
            code="invalid_date_range",
            message=f"`from` ({from_date.isoformat()}) must not be after `to` ({to_date.isoformat()}).",
        )

    query = get_supabase().table("daily_logs").select("*").eq("user_id", user_id)
    if from_date is not None:
        query = query.gte("log_date", from_date.isoformat())
    if to_date is not None:
        query = query.lte("log_date", to_date.isoformat())

    response = query.order("log_date").execute()
    return [DailyLog(**row) for row in response.data]
