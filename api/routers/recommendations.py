from typing import Optional

from fastapi import APIRouter, Depends, Query

from core.security import get_current_user
from models.schemas import PhaseContent, RecommendationsResponse
from services import cycles as cycles_service
from services import prediction as prediction_service
from services import profiles as profiles_service
from services import recommendations as recommendations_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/today", response_model=RecommendationsResponse)
def get_today_recommendations(
    sleep_min: Optional[int] = Query(default=None, ge=0),
    steps: Optional[int] = Query(default=None, ge=0),
    active_min: Optional[int] = Query(default=None, ge=0),
    current_user: dict = Depends(get_current_user),
) -> RecommendationsResponse:
    user_id = current_user["sub"]
    cycles = cycles_service.list_cycles(user_id)
    profile = profiles_service.get_profile(user_id)
    prediction = prediction_service.predict(cycles, profile)

    content = recommendations_service.get_phase_content(prediction.current_phase)
    line = recommendations_service.adaptive_line(sleep_min=sleep_min, steps=steps, active_min=active_min)

    return RecommendationsResponse(
        phase=prediction.current_phase,
        cycle_day=prediction.cycle_day,
        content=PhaseContent(**content),
        adaptive_line=line,
        disclaimer=recommendations_service.DISCLAIMER,
    )
