from datetime import date, timedelta

from fastapi import APIRouter, Depends

from core.security import get_current_user
from models.schemas import RiskFlag
from services import cycles as cycles_service
from services import logs as logs_service
from services import profiles as profiles_service
from services import risk as risk_service

router = APIRouter(prefix="/risk", tags=["risk"])

DAILY_LOG_WINDOW_DAYS = 120


@router.get("/evaluate", response_model=list[RiskFlag])
def evaluate_risk(current_user: dict = Depends(get_current_user)) -> list[RiskFlag]:
    user_id = current_user["sub"]
    today = date.today()

    cycles = cycles_service.list_cycles(user_id)
    daily_logs = logs_service.list_logs(user_id, today - timedelta(days=DAILY_LOG_WINDOW_DAYS), today)
    profile = profiles_service.get_profile(user_id)

    return risk_service.evaluate_and_persist(user_id, cycles, daily_logs, profile)
