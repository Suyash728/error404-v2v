from fastapi import APIRouter, Depends

from core.security import get_current_user
from models.schemas import Profile
from services import profiles as profiles_service

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/profile", response_model=Profile)
def get_profile(current_user: dict = Depends(get_current_user)) -> Profile:
    return profiles_service.get_profile(current_user["sub"])
