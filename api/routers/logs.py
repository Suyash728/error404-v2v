from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from core.security import get_current_user
from models.schemas import DailyLog, DailyLogCreate
from services import logs as logs_service

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("", response_model=DailyLog)
def upsert_log(
    payload: DailyLogCreate,
    current_user: dict = Depends(get_current_user),
) -> DailyLog:
    return logs_service.upsert_log(current_user["sub"], payload)


@router.get("", response_model=list[DailyLog])
def list_logs(
    from_: Optional[date] = Query(default=None, alias="from"),
    to: Optional[date] = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> list[DailyLog]:
    return logs_service.list_logs(current_user["sub"], from_, to)
