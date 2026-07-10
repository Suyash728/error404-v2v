from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.security import get_current_user
from services import cycles as cycles_service
from services import prediction as prediction_service
from services import profiles as profiles_service
from services.copy_engine import get_message
from services.gamification_state import get_gamification, pick_context, streak_state_for

router = APIRouter(prefix="/gamification", tags=["gamification"])


class SakhiMessageResponse(BaseModel):
    message: str


@router.get("/state", response_model=SakhiMessageResponse)
def get_state(current_user: dict = Depends(get_current_user)) -> SakhiMessageResponse:
    user_id = current_user["sub"]
    today = date.today()

    cycles = cycles_service.list_cycles(user_id)
    profile = profiles_service.get_profile(user_id)
    prediction = prediction_service.predict(cycles, profile, today=today)
    gamification = get_gamification(user_id)

    context = pick_context(
        streak_count=gamification.streak_count,
        last_checkin=gamification.last_checkin,
        cycle_day=prediction.cycle_day,
        period_length=profile.avg_period_len,
        cycle_length=prediction.cycle_length,
        today=today,
    )
    streak_state = streak_state_for(gamification.streak_count)

    message = get_message(
        context, prediction.current_phase, streak_state, profile.intention_mode, today=today
    )
    return SakhiMessageResponse(message=message)
