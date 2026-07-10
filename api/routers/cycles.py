import uuid
from datetime import date

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from core.security import get_current_user
from models.schemas import Cycle, Prediction
from services import cycles as cycles_service
from services import prediction as prediction_service
from services import profiles as profiles_service

router = APIRouter(prefix="/cycles", tags=["cycles"])


class CycleStartRequest(BaseModel):
    start_date: date


class CycleEndDateRequest(BaseModel):
    end_date: date


@router.post("", response_model=Cycle, status_code=status.HTTP_201_CREATED)
def start_cycle(
    payload: CycleStartRequest,
    current_user: dict = Depends(get_current_user),
) -> Cycle:
    return cycles_service.start_cycle(current_user["sub"], payload.start_date)


@router.get("/prediction", response_model=Prediction)
def get_prediction(current_user: dict = Depends(get_current_user)) -> Prediction:
    user_id = current_user["sub"]
    cycles = cycles_service.list_cycles(user_id)
    profile = profiles_service.get_profile(user_id)
    return prediction_service.predict(cycles, profile)


@router.patch("/{cycle_id}", response_model=Cycle)
def update_cycle_end_date(
    cycle_id: uuid.UUID,
    payload: CycleEndDateRequest,
    current_user: dict = Depends(get_current_user),
) -> Cycle:
    return cycles_service.set_cycle_end_date(current_user["sub"], str(cycle_id), payload.end_date)


@router.get("", response_model=list[Cycle])
def list_cycles(current_user: dict = Depends(get_current_user)) -> list[Cycle]:
    return cycles_service.list_cycles(current_user["sub"])
